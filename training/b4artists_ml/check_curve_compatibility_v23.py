"""Coordinate invariance and zero-extension compatibility of added descriptors."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import sys,json,hashlib,copy
from dataclasses import replace
import numpy as np
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT.parents[1]/'tests'))
from test_b4artists_ml_semantic_predictor import windows
import mixture_trajectory_v21 as old
import curve_mixture_v23 as new

def main():
 out=ROOT/'results/curve-compatibility-v23.json';assert not out.exists();path=ROOT/'results/mixture_trajectory_v21/best_learned.npz';model=old.load(path);expanded=copy.deepcopy(model);expanded['kind']='curve_mixture_v23';expanded['mean']=np.r_[model['mean'],np.zeros(48)];expanded['std']=np.r_[model['std'],np.ones(48)];expanded['w0']=np.r_[model['w0'],np.zeros((48,model['w0'].shape[1]))];errors=[]
 for w in windows():
  obs=w['observations'];a=old.predict_packed(model,obs,w['t']);b=new.predict_packed(expanded,obs,w['t']);errors.append(float(np.max(abs(a-b))));np.testing.assert_allclose(a,b,rtol=0,atol=1e-12)
  parent=new.parent_model(expanded);fixed=new.expert_predictions(parent,obs,new.GRID);f=new.curve_features(obs,fixed);q=np.array([[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]])
  changed=replace(obs,positions=obs.positions@q.T,rest=obs.rest@q.T,rotations=q@obs.rotations);pred=np.asarray(fixed).copy().reshape(4,9,17,9);pred[...,:3]=pred[...,:3]@q.T;pred[...,3:]=np.asarray(fixed).reshape(4,9,17,9)[...,3:]
  np.testing.assert_allclose(f[548:],new.curve_features(changed,pred.reshape(4,9,153))[548:],rtol=1e-12,atol=1e-12)
 result=dict(passed=True,synthetic_windows=4,zero_extension_max_error=max(errors),rotation_descriptor_invariance=True,scope='Added gate rows at zero preserve established predictions within floating precision; this is not equality of separately trained candidates or motion-quality evidence.',model_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'curve_features_v23.py',ROOT/'curve_mixture_v23.py']});out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
