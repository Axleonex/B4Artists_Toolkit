"""Frozen direct-model training diagnostic; no new fits or holdout reads."""
from pathlib import Path
import os,time,json,hashlib,collections
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
import numpy as np
from sequence_numpy_v1 import forward
ROOT=Path(__file__).resolve().parents[2];TR=Path(__file__).resolve().parent;BASE=TR/'results/sequence-training-diagnosis-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def components(error,mask,dt):
 e=error.reshape(*error.shape[:2],17,9).astype(float);u=(~mask).reshape(e.shape)
 def average(v,m):return (v*v*m).sum(axis=(1,2,3))/np.maximum(m.sum(axis=(1,2,3)),1)
 p=average(e[...,:3],u[...,:3]);r=average(e[...,3:],u[...,3:])
 v=average((e[:,1:]-e[:,:-1])/dt[:,None,None,None],u[:,1:]|u[:,:-1])
 a=average((e[:,2:]-2*e[:,1:-1]+e[:,:-2])/dt[:,None,None,None]**2,u[:,2:]|u[:,1:-1]|u[:,:-2])
 return np.stack((p,r,v,a,p+.1*r+.01*v+.0001*a),axis=1)
def main():
 manifest_path=TR/'results/sequence-corpus-v2/manifest.json';manifest=read(manifest_path);selection=[w for w in manifest['windows'] if w['mask_pattern']=='boundary'];assert len(selection)==1926
 BASE.mkdir(exist_ok=False);plan=dict(training_only=True,selection='All1926boundary-mask training windows; both direct seeds, zero-residual request baseline. Selection uses no outcomes.',manifest_sha256=sha(manifest_path),script_sha256=sha(Path(__file__)),weights={},metric='Mean of per-window unknown-channel MSE and derivative MSE in the raw training representation; training loss weights retained. Diagnostic is not projected development acceptance.',retraining=False,validation_read=False,confirmation_read=False,max_seconds=600);models={}
 for seed in (20260909,20260910):
  r=read(TR/'results/sequence-corpus-training-v2'/('direct-'+str(seed))/'report.json');p=ROOT/r['weights'];assert sha(p)==r['weights_sha256'];plan['weights'][str(seed)]=r['weights_sha256']
  with np.load(p,allow_pickle=False) as z:models[str(seed)]={n:z[n] for n in z.files}
 write(BASE/'plan.json',plan);out={k:[] for k in ('baseline',*models)};groups=collections.defaultdict(list)
 for w in selection:groups[w['bucket']].append(w['index'])
 start=time.perf_counter()
 for file in manifest['files']:
  p=ROOT/file['path'];assert sha(p)==file['sha256']
  with np.load(p,allow_pickle=False) as z:c=z['condition'];base=z['baseline'];target=z['target'];mask=z['mask'];dt=z['dt']
  ids=groups[file['frames']]
  for offset in range(0,len(ids),16):
   assert time.perf_counter()-start<600 and time.time()<1789053845.
   take=ids[offset:offset+16];e=base[take]-target[take];out['baseline'].extend(components(e,mask[take],dt[take]).tolist())
   for name,weights in models.items():
    prediction=forward(weights,c[take],np.zeros_like(base[take]),np.zeros(len(take),np.float32));prediction[mask[take]]=0;out[name].extend(components(e+prediction,mask[take],dt[take]).tolist())
  write(BASE/'progress.json',dict(windows=len(out['baseline']),seconds=time.perf_counter()-start))
 assert all(len(v)==1926 for v in out.values());metrics={k:dict(zip(('position_mse','rotation6_mse','velocity_mse','acceleration_mse','weighted_loss'),np.mean(v,axis=0).tolist())) for k,v in out.items()};ratios={k:{n:v/metrics['baseline'][n] for n,v in values.items()} for k,values in metrics.items() if k!='baseline'}
 report=dict(complete=True,windows=1926,training_only=True,projected_quality_qualification=False,metrics=metrics,ratios_to_linear_slerp_request_baseline=ratios,plan_sha256=sha(BASE/'plan.json'),seconds=time.perf_counter()-start,validation_read=False,confirmation_read=False,retraining=False)
 write(BASE/'report.json',report);print(json.dumps(report),flush=True)
if __name__=='__main__':main()
