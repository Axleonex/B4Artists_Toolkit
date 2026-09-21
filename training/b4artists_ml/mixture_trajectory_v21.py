"""Supervised position mixture; frozen v20 rotations and learned trajectory expert.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import numpy as np
import kinematic_trajectory_v20 as parent_predictor
from kinematic_features_v20 import features
from context_network import initialize, Adam
from trajectory_predictor import operators
from sequence_model import statistics
from motion_coverage import fit_feature_normalization
from temporal_data import rotation_matrix

EXPERTS = ('linear', 'hermite', 'shape', 'v20')


def softmax(logits):
    logits = np.asarray(logits, dtype=float)
    if logits.ndim != 2 or logits.shape[1] != 4 or not np.isfinite(logits).all():
        raise ValueError('Finite four-expert logits required')
    values = np.exp(logits - logits.max(axis=1, keepdims=True))
    return values / values.sum(axis=1, keepdims=True)


def expert_predictions(parent, observations, t):
    queries = np.asarray(t, dtype=float)
    if queries.ndim != 1 or not np.isfinite(queries).all() or np.any((queries < 0) | (queries > 1)):
        raise ValueError('Finite normalized query times required')
    return [parent_predictor.predict_packed(dict(kind='baseline', baseline=k), observations, queries)
            for k in EXPERTS[:-1]] + [parent_predictor.predict_packed(parent, observations, queries)]


def training_terms(window, predictions, spec):
    values = np.asarray(predictions, dtype=float)
    target = np.asarray(window['target'], dtype=float)
    if values.shape != (4, len(window['t']), 153) or target.shape != values.shape[1:] or not np.isfinite(values).all() or not np.isfinite(target).all():
        raise ValueError('Finite matched four-expert training trajectories required')
    positions = values.reshape(4, -1, 17, 9)[..., :3].reshape(4, -1, 51)
    truth = target.reshape(-1, 17, 9)[..., :3].reshape(-1, 51)
    op = operators(window, spec)
    # Subtract the same reference from all experts and truth for stable Gram terms.
    reference = positions[2]
    delta = np.einsum('at,ktf->kaf', op, positions - reference)
    residual = op @ (truth - reference)
    return np.einsum('kaf,jaf->kj', delta, delta), np.einsum('kaf,af->k', delta, residual), float(np.sum(residual ** 2))


def loss_and_grad(params, x, terms, weights, regularization):
    gram, rhs, constant = terms
    x = np.asarray(x, dtype=float); weights = np.asarray(weights, dtype=float)
    n = len(x)
    if x.ndim != 2 or x.shape[1] != 548 or weights.shape != (n,) or not n or not np.isfinite(x).all() or not np.isfinite(weights).all() or np.any(weights < 0) or weights.sum() <= 0 or not np.isfinite(regularization) or regularization < 0:
        raise ValueError('Invalid mixture training inputs or weights')
    if gram.shape != (n, 4, 4) or rhs.shape != (n, 4) or constant.shape != (n,) or any(not np.isfinite(a).all() for a in terms):
        raise ValueError('Invalid mixture trajectory terms')
    hidden = np.tanh(x @ params['w0'] + params['b0'])
    probabilities = softmax(hidden @ params['w1'] + params['b1'])
    normalizer = weights / weights.sum() / 51
    gp = np.einsum('nkj,nj->nk', gram, probabilities)
    per = np.sum(probabilities * gp - 2 * probabilities * rhs, axis=1) + constant
    loss = .5 * float(normalizer @ per) + .5 * regularization * sum(float(np.sum(params[k] ** 2)) for k in ('w0', 'w1'))
    dp = (gp - rhs) * normalizer[:, None]
    delta = probabilities * (dp - np.sum(dp * probabilities, axis=1, keepdims=True))
    dh = (delta @ params['w1'].T) * (1 - hidden ** 2)
    grad = dict(w0=x.T @ dh + regularization * params['w0'], b0=dh.sum(axis=0), w1=hidden.T @ delta + regularization * params['w1'], b1=delta.sum(axis=0))
    return loss, grad


def fit(windows, terms, parent, spec, seed):
    hidden, epochs, batch = (spec[k] for k in ('hidden', 'epochs', 'batch_size'))
    rate, reg = float(spec['learning_rate']), float(spec['regularization'])
    initial_probabilities = np.asarray(spec['initial_probabilities'], dtype=float)
    if any(type(v) is not int or v <= 0 for v in (hidden, epochs, batch)) or hidden > 128 or not np.isfinite(rate) or rate <= 0 or not np.isfinite(reg) or reg < 0:
        raise ValueError('Invalid mixture fit specification')
    if initial_probabilities.shape != (4,) or not np.isfinite(initial_probabilities).all() or np.any(initial_probabilities <= 0) or abs(initial_probabilities.sum() - 1) > 1e-12:
        raise ValueError('Positive normalized initial expert weights required')
    x = np.stack([features(w['x'], 'motion') for w in windows])
    _, weights, _, _ = statistics(windows)
    mean, std = fit_feature_normalization(x, weights)
    z = np.clip((x - mean) / std, -8, 8)
    params = initialize(548, hidden, 4, seed, dtype=np.float64)
    params['w1'][:] = 0; params['b1'][:] = np.log(initial_probabilities)
    original_hidden = params['w0'].copy()
    initial = loss_and_grad(params, z, terms, weights, reg)[0]
    optimizer = Adam(params, rate=rate); rng = np.random.default_rng(seed)
    history = []; backtracked = rejected = 0
    for epoch in range(epochs):
        ids = rng.permutation(len(z))
        for start in range(0, len(ids), batch):
            ix = ids[start:start + batch]; local_terms = tuple(a[ix] for a in terms)
            before_loss, grad = loss_and_grad(params, z[ix], local_terms, weights[ix], reg)
            norm = np.sqrt(sum(float(np.sum(v ** 2)) for v in grad.values()))
            if not np.isfinite(norm): raise ValueError('Nonfinite mixture gradient')
            if norm > 1: grad = {k:v / norm for k,v in grad.items()}
            before = {k:v.copy() for k,v in params.items()}
            optimizer.step(params, grad)
            direction = {k:params[k] - before[k] for k in params}; accepted = False
            for attempt in range(8):
                if attempt:
                    for k in params: params[k][:] = before[k] + direction[k] * .5 ** attempt
                candidate = loss_and_grad(params, z[ix], local_terms, weights[ix], reg)[0]
                if np.isfinite(candidate) and candidate <= before_loss:
                    accepted = True; backtracked += int(attempt > 0); break
            if not accepted:
                for k in params: params[k][:] = before[k]
                rejected += 1
        if (epoch + 1) % 10 == 0 or epoch + 1 == epochs:
            objective = loss_and_grad(params, z, terms, weights, reg)[0]
            if not np.isfinite(objective): raise ValueError('Nonfinite mixture objective')
            history.append(dict(epoch=epoch + 1, objective=objective))
    model = dict(kind='position_mixture_v21', mean=mean, std=std, **params)
    model.update({'parent_' + k:v.copy() if isinstance(v, np.ndarray) else v for k,v in parent.items()})
    return model, dict(initial_objective=initial, training_objective=history[-1]['objective'], epochs=history, hidden_feature_change=float(np.linalg.norm(params['w0'] - original_hidden)), backtracked_steps=backtracked, rejected_steps=rejected, scope='Gate training diagnostic on group-excluded parent predictions; not independent gate validation')


def parent_model(model):
    return {k.removeprefix('parent_'):v for k,v in model.items() if k.startswith('parent_')}


def strengths(model, observations):
    z = np.clip((features(observations.features(), 'motion') - model['mean']) / model['std'], -8, 8)
    return softmax((np.tanh(z @ model['w0'] + model['b0']) @ model['w1'] + model['b1'])[None])[0]


def blend(predictions, probabilities, t):
    probabilities = np.asarray(probabilities, dtype=float)
    values = np.asarray(predictions, dtype=float).reshape(4, -1, 17, 9)
    if probabilities.shape != (4,) or not np.isfinite(probabilities).all() or np.any(probabilities < 0) or abs(probabilities.sum() - 1) > 1e-12 or not np.isfinite(values).all():
        raise ValueError('Finite simplex strengths and predictions required')
    out = values[3].copy()
    positions = values[..., :3]; reference = positions[2]
    out[..., :3] = reference + np.einsum('k,ktjf->tjf', probabilities, positions - reference)
    priorities = (np.asarray(t) == 0) | (np.asarray(t) == 1)
    out[priorities] = values[3, priorities]
    return out.reshape(-1, 153)


def predict_packed(model, observations, t):
    if model['kind'] == 'baseline': return parent_predictor.predict_packed(model, observations, t)
    if model['kind'] != 'position_mixture_v21': raise ValueError('Invalid mixture model kind')
    return blend(expert_predictions(parent_model(model), observations, t), strengths(model, observations), t)


def provider(model):
    def call(observations, t):
        values = predict_packed(model, observations, t).reshape(-1, 17, 9)
        rotation, bad = rotation_matrix(values[..., 3:])
        if bad.any(): raise ValueError('Degenerate mixture parent rotation')
        return values[..., :3], rotation
    return call


def save(path, model):
    np.savez_compressed(path, **{k:np.asarray(v) for k,v in model.items()})


def load(path):
    with np.load(path, allow_pickle=False) as archive: model = {k:archive[k] for k in archive.files}
    text_keys = ('kind', 'parent_kind', 'parent_baseline_kind', 'parent_continuity')
    for k in text_keys:
        if k not in model or model[k].shape != (): raise ValueError('Missing scalar model representation')
        model[k] = str(model[k])
    expected = {'kind', 'mean', 'std', 'w0', 'b0', 'w1', 'b1'} | {'parent_' + k for k in ('kind', 'baseline_kind', 'continuity', 'mean', 'std', 'w0', 'b0', 'w1', 'b1')}
    if set(model) != expected or model['kind'] != 'position_mixture_v21' or model['parent_kind'] != 'kinematic_mlp_v20' or model['parent_baseline_kind'] not in ('linear', 'shape') or model['parent_continuity'] not in ('C0', 'C1'):
        raise ValueError('Invalid mixture parameter keys or representation')
    for prefix, outputs in (('', 4), ('parent_', 612)):
        if model[prefix + 'mean'].shape != (548,) or model[prefix + 'std'].shape != (548,) or np.any(model[prefix + 'std'] <= 0): raise ValueError('Invalid model normalization')
        w0 = model[prefix + 'w0']
        if w0.ndim != 2 or w0.shape[0] != 548 or not 1 <= w0.shape[1] <= 128: raise ValueError('Invalid hidden shape')
        h = w0.shape[1]
        if model[prefix + 'b0'].shape != (h,) or model[prefix + 'w1'].shape != (h, outputs) or model[prefix + 'b1'].shape != (outputs,): raise ValueError('Invalid model readout')
    if any(not np.isfinite(v).all() for k,v in model.items() if k not in text_keys): raise ValueError('Nonfinite model parameters')
    return model
