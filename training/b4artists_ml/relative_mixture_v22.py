"""Fixed v21 predictor with training-only relative cohort loss balancing.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import numpy as np
from mixture_trajectory_v21 import (features, initialize, Adam, statistics,
    fit_feature_normalization, loss_and_grad, predict_packed, provider, save, load,
    expert_predictions, training_terms, strengths, EXPERTS)


def cohort_weights(windows, position_errors, relative_fraction, floor_fraction):
    errors = np.asarray(position_errors, dtype=float)
    alpha, fraction = float(relative_fraction), float(floor_fraction)
    if not windows or errors.shape != (len(windows), 3) or not np.isfinite(errors).all() or np.any(errors < 0):
        raise ValueError('Finite nonnegative three-control training errors required')
    if not np.isfinite(alpha) or not 0 <= alpha <= 1 or not np.isfinite(fraction) or not 0 < fraction <= 1:
        raise ValueError('Invalid relative loss fractions')
    groups = {}
    for i, w in enumerate(windows): groups.setdefault((w['clip'], w['gap'], w['context']), []).append(i)
    keys = sorted(groups)
    scale = np.array([np.min(np.mean(errors[groups[k]], axis=0)) for k in keys])
    positive = scale[scale > 0]
    floor = max(float(np.median(positive)) * fraction, np.finfo(float).tiny) if len(positive) else 1.
    denominator = np.maximum(scale, floor)
    # A bounded ratio avoids overflow for near-zero finite errors.
    relative = denominator.min() / denominator
    relative /= relative.sum()
    mass = (1 - alpha) / len(keys) + alpha * relative
    weight = np.zeros(len(windows))
    for k, value in zip(keys, mass):
        weight[groups[k]] = 1 / (len(keys) * len(groups[k])) if alpha == 0 else value / len(groups[k])
    if not np.isfinite(weight).all() or abs(weight.sum() - 1) > 1e-12:
        raise ValueError('Invalid normalized cohort weights')
    return weight, dict(relative_fraction=alpha, floor_fraction=fraction,
        positive_median=float(np.median(positive)) if len(positive) else 0., error_floor=floor,
        cohorts=[dict(clip=k[0], gap=k[1], context=k[2], baseline_position_mse=float(scale[i]),
                      mass=float(mass[i]), windows=len(groups[k])) for i,k in enumerate(keys)],
        feature_normalization='Original equal-cohort weights, unchanged from v21',
        label_scope='Only raw procedural position errors on training labels set loss weights; never consulted at inference')


def fit(windows, terms, parent, spec, seed, position_errors):
    hidden, epochs, batch = (spec[k] for k in ('hidden', 'epochs', 'batch_size'))
    rate, reg = float(spec['learning_rate']), float(spec['regularization'])
    initial_probabilities = np.asarray(spec['initial_probabilities'], dtype=float)
    if any(type(v) is not int or v <= 0 for v in (hidden, epochs, batch)) or hidden > 128 or not np.isfinite(rate) or rate <= 0 or not np.isfinite(reg) or reg < 0:
        raise ValueError('Invalid mixture fit specification')
    if initial_probabilities.shape != (4,) or not np.isfinite(initial_probabilities).all() or np.any(initial_probabilities <= 0) or abs(initial_probabilities.sum() - 1) > 1e-12:
        raise ValueError('Positive normalized initial expert weights required')
    x = np.stack([features(w['x'], 'motion') for w in windows])
    _, base_weights, _, _ = statistics(windows)
    weights, weighting = cohort_weights(windows, position_errors, spec['relative_fraction'], spec['relative_floor_fraction'])
    mean, std = fit_feature_normalization(x, base_weights)
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
    return model, dict(initial_objective=initial, training_objective=history[-1]['objective'], epochs=history, hidden_feature_change=float(np.linalg.norm(params['w0'] - original_hidden)), backtracked_steps=backtracked, rejected_steps=rejected, scope='Gate training diagnostic on group-excluded parent predictions; not independent gate validation', relative_weighting=weighting)
