"""Pre-fit calculus and data-boundary checks for the fixed mixture experiment."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '4')
from pathlib import Path
import sys, json, hashlib, tempfile, copy
from dataclasses import replace
import numpy as np
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / 'tests'))
from test_b4artists_ml_semantic_predictor import windows
import curve_mixture_v23 as m
import kinematic_trajectory_v20 as parent


def main():
    out = ROOT / 'results/curve-mixture-checks-v23.json'
    assert not out.exists()
    checks = []
    feature_checks=[]
    rows = windows()
    ps = dict(hidden=8, epochs=10, batch_size=4, learning_rate=.001, regularization=0., velocity_weight=.01, acceleration_weight=.0001, baseline_kind='shape', continuity='C0')
    pm, _ = parent.fit(rows, ps, 7)
    frozen = copy.deepcopy(pm)
    for w in rows: w['gate_features']=m.curve_features(w['observations'],m.expert_predictions(pm,w['observations'],m.GRID))
    spec = dict(hidden=8, epochs=10, batch_size=4, learning_rate=.001, regularization=0., velocity_weight=.01, acceleration_weight=.0001, initial_probabilities=[.025,.025,.05,.9])
    predictions = [m.expert_predictions(pm, w['observations'], w['t']) for w in rows]
    terms = tuple(np.asarray(a) for a in zip(*(m.training_terms(w,p,spec) for w,p in zip(rows,predictions))))
    rng = np.random.default_rng(1); x = rng.normal(size=(4,596)); params = m.initialize(596,8,4,3,dtype=np.float64); weights=np.array([.1,.2,.3,.4])
    loss, grad = m.loss_and_grad(params,x,terms,weights,.001)
    probabilities = m.softmax(np.tanh(x@params['w0']+params['b0'])@params['w1']+params['b1']); expected=0.
    for w, preds, prob, weight in zip(rows,predictions,probabilities,weights):
        positions = np.asarray(preds).reshape(4,-1,17,9)[...,:3].reshape(4,-1,51)
        error = np.einsum('k,ktf->tf',prob,positions)-w['target'].reshape(-1,17,9)[...,:3].reshape(-1,51)
        expected += .5*weight*np.sum((m.operators(w,spec)@error)**2)/51
    expected += .5*.001*sum(np.sum(params[k]**2) for k in ('w0','w1'))
    assert abs(loss-expected)<1e-10; checks.append('Gram objective matches explicit trajectory and derivative loss')
    for k in params:
        direction=rng.normal(0,.1,params[k].shape); before=params[k].copy(); eps=1e-5
        params[k]=before+eps*direction; a=m.loss_and_grad(params,x,terms,weights,.001)[0]
        params[k]=before-eps*direction; b=m.loss_and_grad(params,x,terms,weights,.001)[0];params[k]=before
        assert abs((a-b)/(2*eps)-np.sum(grad[k]*direction))<1e-8
    checks.append('all four parameter gradients match finite differences')
    # A controlled, nontrivial positional signal verifies feature learning independently
    # of the almost identical procedural experts in the tiny existing fixture.
    learning_rows=copy.deepcopy(rows); learning_terms=[]
    for w, original in zip(learning_rows,predictions):
        signal=np.asarray(original).copy().reshape(4,-1,17,9)
        signal[3,...,0] += .3*np.sin(np.pi*w['t'])[:,None]
        w['target']=signal[3].reshape(-1,153).copy()
        learning_terms.append(m.training_terms(w,signal.reshape(4,-1,153),spec))
    learning_terms=tuple(np.asarray(a) for a in zip(*learning_terms))
    model,d=m.fit(learning_rows,learning_terms,pm,spec,7)
    assert d['training_objective']<d['initial_objective'] and d['hidden_feature_change']>1e-5
    checks.append('zero-regularization fit learns hidden features and lowers loss')
    for k in pm: np.testing.assert_array_equal(pm[k],frozen[k])
    checks.append('gate fitting preserves frozen parent parameters')
    w=rows[0]; obs=w['observations']; fixed=m.expert_predictions(pm,obs,m.GRID); f=m.curve_features(obs,fixed)
    from kinematic_features_v20 import features as original_features
    np.testing.assert_array_equal(f[:548],original_features(obs.features(),'motion'));assert f.shape==(596,) and np.isfinite(f).all() and np.all(f[548:]>=0);checks.append('curve descriptors retain all original observed features')
    for scale,offset in [(3.,np.zeros(3)),(1.,np.array([2.,-1.,.5]))]:
        changed=replace(obs,positions=obs.positions*scale+offset,rest=obs.rest*scale+offset)
        proposals=np.asarray(fixed).copy().reshape(4,9,17,9);proposals[...,:3]=proposals[...,:3]*scale+offset
        np.testing.assert_allclose(f[548:],m.curve_features(changed,proposals.reshape(4,9,153))[548:],rtol=1e-10,atol=1e-10)
    checks.append('curve descriptors are invariant to matched positional scale and translation')
    changed=np.asarray(fixed).copy().reshape(4,9,17,9);changed[1,4,:,0]+=.2
    assert not np.array_equal(f[548:],m.curve_features(obs,changed.reshape(4,9,153))[548:]);checks.append('observed proposal excursions affect confidence descriptors')
    for bad in [np.asarray(fixed)[:,:8],np.full((4,9,153),np.nan)]:
        try:m.curve_features(obs,bad)
        except ValueError:pass
        else:raise AssertionError('Invalid proposal descriptors accepted')
    checks.append('malformed or nonfinite fixed-grid proposals rejected')
    pred=m.predict_packed(model,w['observations'],w['t']); values=np.asarray(predictions[0]).reshape(4,-1,17,9)
    pp=pred.reshape(-1,17,9)
    assert np.all(pp[...,:3]>=values[...,:3].min(axis=0)-1e-12) and np.all(pp[...,:3]<=values[...,:3].max(axis=0)+1e-12)
    np.testing.assert_array_equal(pp[...,3:],values[3,...,3:]);checks.append('position convex bounds and unchanged parent rotations')
    np.testing.assert_array_equal(pred[[0,-1]],w['linear'][[0,-1]]);checks.append('authored priorities remain exact')
    w['target'][:]=np.nan;np.testing.assert_array_equal(pred,m.predict_packed(model,w['observations'],w['t']));checks.append('inference cannot read hidden labels')
    o=w['observations'];static=replace(o,positions=np.repeat(o.positions[:1],4,axis=0),rotations=np.repeat(o.rotations[:1],4,axis=0))
    np.testing.assert_array_equal(m.predict_packed(model,static,w['t']),parent.reference(static,w['t'],'shape'));checks.append('stationary poses receive no invented motion')
    no_context=replace(o,context=False);positions=no_context.positions.copy();positions[2:]+=100
    ignored=replace(no_context,positions=positions)
    np.testing.assert_array_equal(m.predict_packed(model,no_context,w['t']),m.predict_packed(model,ignored,w['t']));checks.append('masked context cannot influence gate or experts')
    with tempfile.TemporaryDirectory() as folder:
        path=Path(folder)/'model.npz';m.save(path,model)
        np.testing.assert_array_equal(pred,m.predict_packed(m.load(path),o,w['t']));checks.append('serialized gate and parent reproduce exact predictions')
        for key, value in [('std',np.zeros(596)),('w1',np.zeros((8,5))),('parent_w1',np.zeros((8,613))),('b0',np.full(8,np.nan)),('parent_kind','untrained')]:
            bad=copy.deepcopy(model);bad[key]=value;m.save(path,bad)
            try:m.load(path)
            except ValueError:pass
            else:raise AssertionError('Malformed model accepted: '+key)
        checks.append('malformed gate and parent models rejected')
    for queries in [np.array([-.1,.5]),np.array([0.,np.nan]),np.array([[.5]])]:
        try:m.predict_packed(model,o,queries)
        except ValueError:pass
        else:raise AssertionError('Invalid query accepted')
    checks.append('invalid query times rejected')
    for invalid in [np.array([-1.,1.,1.,0.]),np.full(4,np.nan),np.zeros(4)]:
        try:m.blend(predictions[0],invalid,w['t'])
        except ValueError:pass
        else:raise AssertionError('Invalid weights accepted')
    checks.append('invalid simplex strengths rejected')
    check = m.softmax(np.array([[1e300,-1e300,0,1.]]));assert np.isfinite(check).all() and check.sum()==1
    checks.append('stable softmax remains finite for extreme finite logits')
    result=dict(passed=True,checks=checks,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'curve_mixture_v23.py',ROOT/'curve_features_v23.py']},scope='Pre-fit math and data-boundary checks; not motion quality qualification')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
