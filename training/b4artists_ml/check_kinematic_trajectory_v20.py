"""Pre-fit calculus, genuine learning, readout and inference invariants."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import sys,json,hashlib,tempfile,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tests'))
import numpy as np
from dataclasses import replace
from test_b4artists_ml_semantic_predictor import windows
import kinematic_trajectory_v20 as m
from kinematic_readout_v20 import fit_readout
ROOT=Path(__file__).resolve().parent
SPEC=dict(hidden=8,epochs=10,batch_size=4,learning_rate=.001,regularization=0.,velocity_weight=.01,acceleration_weight=.0001,baseline_kind='shape',continuity='C0')
def main():
    checks=[];rows=windows();x=np.random.default_rng(1).normal(size=(4,548));params=m.initialize(548,8,612,3,dtype=np.float64);terms=m.trajectory_terms(rows,SPEC);weights=np.array([.1,.2,.3,.4])
    loss,grad=m.loss_and_grad(params,x,terms,weights,.001);expected=0.;coeff=m.forward(params,x).reshape(4,4,153)
    for w,c,weight in zip(rows,coeff,weights):
        error=m.reference(w['observations'],w['t'],'shape')+m.residual_basis(w['t'],'C0')@(c*m.observation_scale(w['observations'])[None,:])-w['target'];expected+=.5*weight*np.sum((m.operators(w,SPEC)@error)**2)/153
    expected+=.5*.001*sum(np.sum(params[k]**2) for k in ['w0','w1']);assert abs(expected-loss)<1e-10;checks.append('trajectory Gram loss equals explicit per-frame objective')
    rng=np.random.default_rng(8);eps=1e-5
    for k in params:
        direction=rng.normal(0,.01,params[k].shape);before=params[k].copy();params[k]=before+eps*direction;a=m.loss_and_grad(params,x,terms,weights,.001)[0];params[k]=before-eps*direction;b=m.loss_and_grad(params,x,terms,weights,.001)[0];params[k]=before;assert abs((a-b)/(2*eps)-np.sum(grad[k]*direction))<1e-8
    checks.append('all parameter gradients match independent finite differences')
    model,d=m.fit(rows,SPEC,7);assert d['training_objective']<d['initial_objective'] and d['hidden_feature_change']>1e-4;checks.append('supervised hidden features change and training loss falls')
    before=copy.deepcopy(model);model,readout=fit_readout(rows,model,SPEC,.01);assert readout['after_objective']<=readout['before_objective'];assert readout['readout_gradient_max']<1e-9
    np.testing.assert_array_equal(before['w0'],model['w0']);checks.append('exact readout preserves hidden features and lowers objective')
    w=rows[0];pred=m.predict_packed(model,w['observations'],w['t']);np.testing.assert_array_equal(pred[[0,-1]],w['linear'][[0,-1]]);w['target'][:]=np.nan;np.testing.assert_array_equal(pred,m.predict_packed(model,w['observations'],w['t']));checks.append('priorities exact and inference independent of hidden labels')
    with tempfile.TemporaryDirectory() as folder:
        p=Path(folder)/'model.npz';m.save(p,model);np.testing.assert_array_equal(pred,m.predict_packed(m.load(p),w['observations'],w['t']))
    checks.append('serialized model reproduces predictions')
    o=w['observations'];o=replace(o,positions=np.repeat(o.positions[:1],4,axis=0),rotations=np.repeat(o.rotations[:1],4,axis=0));np.testing.assert_array_equal(m.predict_packed(model,o,w['t']),m.reference(o,w['t'],'shape'));checks.append('stationary observations have exactly zero learned correction')
    result=dict(passed=True,checks=checks,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'kinematic_trajectory_v20.py',ROOT/'kinematic_readout_v20.py',ROOT/'shape_reference.py']},scope='Pre-fit math/learning tests, not corpus or product quality')
    out=ROOT/'results/kinematic-trajectory-checks-v20.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
