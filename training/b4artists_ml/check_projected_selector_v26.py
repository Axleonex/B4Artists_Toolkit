"""Pre-fit selector gradients, observed-only inference and model integrity."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import sys,json,hashlib,tempfile,copy
from dataclasses import replace
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'tests'))
from test_b4artists_ml_semantic_predictor import windows
import projected_selector_v26 as m
import kinematic_trajectory_v20 as parent

def main():
    out=ROOT/'results/projected-selector-checks-v26.json';assert not out.exists();checks=[]
    rows=windows();spec=dict(hidden=8,epochs=20,batch_size=4,learning_rate=.001,regularization=0.)
    pm,_=parent.fit(rows,dict(spec,velocity_weight=.01,acceleration_weight=.0001,baseline_kind='shape',continuity='C0'),7);frozen=copy.deepcopy(pm)
    rng=np.random.default_rng(9);x=rng.normal(size=(4,596));cost=rng.uniform(.2,3.,(4,12));weight=np.array([.1,.2,.3,.4])
    params=m.initialize(596,8,12,3,dtype=np.float64);loss,grad=m.loss_and_grad(params,x,cost,weight,.001)
    probability=m.softmax(np.tanh(x@params['w0']+params['b0'])@params['w1']+params['b1'])
    expected=float(np.sum(weight[:,None]*probability*cost))+.5*.001*sum(np.sum(params[k]**2) for k in ('w0','w1'))
    assert abs(loss-expected)<1e-12;checks.append('Expected fitted-risk objective matches explicit weighted sum')
    for k in params:
        direction=rng.normal(0,.1,params[k].shape);old=params[k].copy();epsilon=1e-5
        params[k]=old+epsilon*direction;a=m.loss_and_grad(params,x,cost,weight,.001)[0]
        params[k]=old-epsilon*direction;b=m.loss_and_grad(params,x,cost,weight,.001)[0];params[k]=old
        assert abs((a-b)/(2*epsilon)-np.sum(grad[k]*direction))<1e-8
    checks.append('All parameter gradients match finite differences')
    identities=[dict(clip='a',gap=8,context=True)]*3+[dict(clip='b',gap=16,context=False)]
    metrics=[[dict(position=float(v),rotation=float(v*.5)) for v in row] for row in cost]
    normalized,mass,den=m.training_costs(identities,metrics)
    assert abs(mass[:3].sum()-.5)<1e-12 and mass[3]==.5
    for indices,entry in [(range(3),den[0]),([3],den[1])]:
        raw=cost[list(indices)]*1.05;normalizer=raw[:,m.BASELINE_INDEX].mean(axis=0).min()
        np.testing.assert_allclose(normalized[list(indices)],raw/normalizer,rtol=1e-14,atol=1e-14)
    checks.append('Equal cohort mass and original position-plus-rotation normalization are exact')
    features=np.stack([m.curve_features(w['observations'],m.expert_predictions(pm,w['observations'],m.GRID)) for w in rows])
    model,diagnostic=m.fit(features,normalized,mass,pm,spec,7)
    assert diagnostic['training_objective']<diagnostic['initial_objective'] and diagnostic['hidden_feature_change']>0
    for k in pm:np.testing.assert_array_equal(pm[k],frozen[k])
    checks.append('Unregularized supervised fit learns hidden features and preserves frozen parent')
    w=rows[0];o=w['observations'];prediction=m.predict_packed(model,o,w['t']);choice,prob=m.selection(model,o)
    assert 0<=choice<12 and np.isfinite(prob).all() and abs(prob.sum()-1)<1e-12
    from projected_pool_v26 import combine
    np.testing.assert_array_equal(prediction,combine(m.expert_predictions(pm,o,w['t']),choice))
    np.testing.assert_array_equal(prediction[[0,-1]],w['linear'][[0,-1]])
    for i,t in enumerate(w['t']):np.testing.assert_array_equal(m.predict_packed(model,o,np.array([t]))[0],prediction[i])
    checks.append('One declared proposal is selected per interval, with exact priorities and query-independent choice')
    w['target'][:]=np.nan;np.testing.assert_array_equal(prediction,m.predict_packed(model,o,w['t']))
    checks.append('Inference cannot read hidden training labels')
    static=replace(o,positions=np.repeat(o.positions[:1],4,axis=0),rotations=np.repeat(o.rotations[:1],4,axis=0))
    np.testing.assert_array_equal(m.predict_packed(model,static,w['t']),parent.reference(static,w['t'],'shape'))
    checks.append('Stationary observations invent no motion')
    masked=replace(o,context=False);pos=masked.positions.copy();pos[2:]+=100
    np.testing.assert_array_equal(m.predict_packed(model,masked,w['t']),m.predict_packed(model,replace(masked,positions=pos),w['t']))
    checks.append('Masked context is ignored by the selector and proposals')
    with tempfile.TemporaryDirectory(dir=ROOT/'cache',prefix='selector-v26-check-') as folder:
        path=Path(folder)/'model.npz';assert path.resolve().is_relative_to((ROOT/'cache').resolve())
        m.save(path,model);loaded=m.load(path)
        np.testing.assert_array_equal(prediction,m.predict_packed(loaded,o,w['t']))
        checks.append('Safe NPZ roundtrip preserves exact predictions')
        for key,value in [('std',np.zeros(596)),('w1',np.zeros((8,11))),('parent_w1',np.zeros((8,613))),('b0',np.full(8,np.nan)),('parent_kind','untrained')]:
            bad=copy.deepcopy(model);bad[key]=value;m.save(path,bad)
            try:m.load(path)
            except ValueError:pass
            else:raise AssertionError('Malformed model accepted:'+key)
        checks.append('Malformed parameters and unrecognized parent representations are rejected')
    for queries in (np.array([-.1,.5]),np.array([0.,np.nan]),np.array([[.5]])):
        try:m.predict_packed(model,o,queries)
        except ValueError:pass
        else:raise AssertionError('Invalid query accepted')
    checks.append('Invalid queries fail closed')
    for bad in (np.full_like(cost,np.nan),-cost,cost[:,:11]):
        try:m.loss_and_grad(params,x,bad,weight,.001)
        except ValueError:pass
        else:raise AssertionError('Invalid training cost accepted')
    checks.append('Malformed, negative and nonfinite fitted risks are rejected')
    names=['projected_selector_v26.py','projected_pool_v26.py','check_projected_selector_v26.py','curve_mixture_v23.py','curve_features_v23.py','kinematic_trajectory_v20.py','temporal_model.py','context_network.py']
    result=dict(passed=True,checks=checks,source_sha256={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names},scope='Tiny pre-fit mathematical/data-boundary fixtures; no corpus model fit or validation read')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=len(checks))),flush=True)
if __name__=='__main__':main()
