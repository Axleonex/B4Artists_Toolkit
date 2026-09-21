"""Pre-fit calculus, variable-length loss and observation-only inference checks."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import sys,json,hashlib,copy,tempfile
from dataclasses import replace
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'tests'))
from test_b4artists_ml_semantic_predictor import windows
from test_b4artists_ml_semantic_motion_data import sequence
from semantic_motion_data import window
import joint_mixture_v24 as m
import kinematic_trajectory_v20 as parent
from temporal_data import rotation6,quat_matrix,rotation_matrix

def main():
 out=ROOT/'results/joint-mixture-checks-v24.json';assert not out.exists();checks=[]
 rows=windows();ps=dict(hidden=8,epochs=10,batch_size=4,learning_rate=.001,regularization=0.,velocity_weight=.01,acceleration_weight=.0001,baseline_kind='shape',continuity='C0')
 pm,_=parent.fit(rows,ps,7);frozen=copy.deepcopy(pm)
 spec=dict(hidden=8,epochs=10,batch_size=4,learning_rate=.001,regularization=0.,velocity_weight=.01,acceleration_weight=.0001,initial_position_probabilities=[.025,.025,.05,.9],initial_rotation_probabilities=[.025,.075,.9])
 for w in rows:w['gate_features']=m.curve_features(w['observations'],m.expert_predictions(pm,w['observations'],m.GRID))
 preds=[m.expert_predictions(pm,w['observations'],w['t']) for w in rows]
 # Include substantial rotations to exercise normalization and every quaternion derivative.
 altered=[];rng=np.random.default_rng(1)
 for w,pr in zip(rows,preds):
  v=np.asarray(pr).copy().reshape(4,-1,17,9)
  for k in (0,1,3):
   q=rng.normal(size=(len(w['t']),17,4));q/=np.linalg.norm(q,axis=-1,keepdims=True);v[k,...,3:]=rotation6(quat_matrix(q))
  altered.append(v.reshape(4,-1,153))
 terms=[m.training_terms(w,p,spec) for w,p in zip(rows,altered)];batch=m.assemble(terms,range(4));x=rng.normal(size=(4,596));params=m.initialize(596,8,119,3,dtype=np.float64);weights=np.array([.1,.2,.3,.4])
 loss,grad=m.loss_and_grad(params,x,batch,weights,.001)
 logits=(np.tanh(x@params['w0']+params['b0'])@params['w1']+params['b1']).reshape(4,17,7);pp=m.softmax(logits[...,:4]);rp=m.softmax(logits[...,4:]);expected=0.
 for w,pr,p,r,weight in zip(rows,altered,pp,rp,weights):
  values=pr.reshape(4,-1,17,9);points=np.einsum('jk,ktjc->tjc',p,values[...,:3]);rot=m.rotation_mix(r[None],m.rotation_experts(pr)[None])[0][0]
  prediction=np.concatenate((points,rot),axis=-1).reshape(-1,153);error=prediction-w['target'];expected+=.5*weight*np.sum((m.operators(w,spec)@error)**2)/153
 expected+=.5*.001*sum(np.sum(params[k]**2) for k in ('w0','w1'));np.testing.assert_allclose(loss,expected,rtol=1e-11,atol=1e-10);checks.append('compressed position and quaternion rotation objective matches explicit trajectory derivatives')
 for key in params:
  direction=rng.normal(0,.1,params[key].shape);before=params[key].copy();eps=1e-5
  params[key]=before+eps*direction;a=m.loss_and_grad(params,x,batch,weights,.001)[0]
  params[key]=before-eps*direction;b=m.loss_and_grad(params,x,batch,weights,.001)[0];params[key]=before
  np.testing.assert_allclose((a-b)/(2*eps),np.sum(grad[key]*direction),rtol=1e-6,atol=1e-7)
 checks.append('all parameter gradients including normalized quaternion mixture match finite differences')
 q=rng.normal(size=(100,4));q/=np.linalg.norm(q,axis=-1,keepdims=True);np.testing.assert_allclose(m.rotation6_and_jacobian(q)[0],rotation6(quat_matrix(q)),atol=1e-14);checks.append('rotation polynomial matches established quaternion convention')
 varied=[window(sequence(),1,end,context=True) for end in (5,9,12)]
 variable=[m.training_terms(w,m.expert_predictions(pm,w['observations'],w['t']),spec) for w in varied]
 bx=m.assemble(variable,range(3));joint,jgrad=m.loss_and_grad(params,x[:3],bx,weights[:3],0.)
 individual=[m.loss_and_grad(params,x[i:i+1],m.assemble(variable,[i]),np.ones(1),0.) for i in range(3)]
 np.testing.assert_allclose(joint,sum(weights[i]*individual[i][0] for i in range(3))/sum(weights[:3]),rtol=1e-10,atol=1e-10)
 for k in jgrad:np.testing.assert_allclose(jgrad[k],sum(weights[i]*individual[i][1][k] for i in range(3))/sum(weights[:3]),rtol=1e-9,atol=1e-10)
 checks.append('padding mixed sequence lengths leaves objective and every gradient unchanged')
 # Antipodal half-turn experts can cancel each other; reference mass still prevents a zero quaternion.
 eq=np.zeros((1,3,2,17,4));eq[:,0,...,0]=1;eq[:,1,...,1]=1;eq[:,2,...,1]=-1
 probs=np.tile([0.,.5,.5],(1,17,1));rr,_,_,norm=m.rotation_mix(probs,eq)
 assert norm.min()>=m.EPSILON*.99;mat,bad=rotation_matrix(rr);assert not bad.any();np.testing.assert_allclose(np.linalg.det(mat),1.,atol=1e-12);checks.append('opposing half-turn proposals cannot create zero-norm mixture')
 learning=copy.deepcopy(rows);learn_terms=[]
 for w,pr in zip(learning,preds):
  v=np.asarray(pr).copy().reshape(4,-1,17,9);v[3,...,0]+=.3*np.sin(np.pi*w['t'])[:,None];w['target']=v[3].reshape(-1,153).copy();learn_terms.append(m.training_terms(w,v.reshape(4,-1,153),spec))
 model,d=m.fit(learning,learn_terms,pm,spec,7);assert d['training_objective']<d['initial_objective'] and d['hidden_feature_change']>1e-5;checks.append('zero-regularization supervised fit learns hidden features and reduces trajectory loss')
 for k in pm:np.testing.assert_array_equal(pm[k],frozen[k])
 checks.append('fitting preserves frozen parent')
 w=rows[0];obs=w['observations'];pred=m.predict_packed(model,obs,w['t']);v=np.asarray(preds[0]).reshape(4,-1,17,9);pv=pred.reshape(-1,17,9)
 assert np.all(pv[...,:3]>=v[...,:3].min(axis=0)-1e-12) and np.all(pv[...,:3]<=v[...,:3].max(axis=0)+1e-12);checks.append('every joint position stays within coordinate-wise expert bounds')
 matrices,bad=rotation_matrix(pv[...,3:]);assert not bad.any();np.testing.assert_allclose(np.linalg.det(matrices),1.,atol=1e-12);checks.append('all predicted rotations are proper')
 np.testing.assert_array_equal(pred[[0,-1]],w['linear'][[0,-1]]);checks.append('authored priority poses remain exact')
 # Query subsets use the fixed feature grid and cannot change any shared-time prediction.
 np.testing.assert_allclose(m.predict_packed(model,obs,w['t'][::2]),pred[::2],atol=1e-13);checks.append('query density does not change shared-time inference')
 w['target'][:]=np.nan;np.testing.assert_array_equal(pred,m.predict_packed(model,obs,w['t']));checks.append('inference cannot read hidden training labels')
 static=replace(obs,positions=np.repeat(obs.positions[:1],4,axis=0),rotations=np.repeat(obs.rotations[:1],4,axis=0))
 np.testing.assert_allclose(m.predict_packed(model,static,w['t']),parent.reference(static,w['t'],'shape'),rtol=0,atol=1e-14);checks.append('stationary pose retained within double-precision conversion roundoff')
 nc=replace(obs,context=False);pos=nc.positions.copy();pos[2:]+=100;rot=nc.rotations.copy();rot[2:]=np.eye(3);ignored=replace(nc,positions=pos,rotations=rot)
 np.testing.assert_array_equal(m.predict_packed(model,nc,w['t']),m.predict_packed(model,ignored,w['t']));checks.append('masked context positions and rotations cannot influence inference')
 with tempfile.TemporaryDirectory() as folder:
  path=Path(folder)/'model.npz';m.save(path,model);np.testing.assert_array_equal(pred,m.predict_packed(m.load(path),obs,w['t']));checks.append('serialization reproduces predictions exactly')
  for key,value in [('std',np.zeros(596)),('w1',np.zeros((8,118))),('parent_w1',np.zeros((8,613))),('b0',np.full(8,np.nan)),('parent_kind','untrained')]:
   invalid=copy.deepcopy(model);invalid[key]=value;m.save(path,invalid)
   try:m.load(path)
   except ValueError:pass
   else:raise AssertionError('Malformed model accepted: '+key)
  checks.append('malformed learned and parent models rejected')
 for t in [np.array([-.1,.5]),np.array([0.,np.nan]),np.array([[.5]])]:
  try:m.predict_packed(model,obs,t)
  except ValueError:pass
  else:raise AssertionError('Invalid query accepted')
 checks.append('invalid query times rejected')
 for size in (3,4):
  logits=np.full((2,17,size),-1e300);logits[...,0]=1e300;p=m.softmax(logits);assert np.isfinite(p).all() and np.all(p.sum(axis=-1)==1)
 checks.append('extreme finite logits remain finite and normalized')
 result=dict(passed=True,checks=checks,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'joint_mixture_v24.py',ROOT/'curve_mixture_v23.py',ROOT/'curve_features_v23.py']},scope='Pre-fit math and data-boundary checks, not motion quality qualification')
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
