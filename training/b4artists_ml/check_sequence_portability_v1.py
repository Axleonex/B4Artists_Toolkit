"""Verify trained research weight portability inside the actual native host."""
from pathlib import Path
import os,sys,json,hashlib,time,subprocess
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();TR=HERE.parent;BASE=TR/'results/sequence-portability-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def prepare():
 sys.path.insert(0,str(TR));import numpy as np,torch
 from sequence_model_v1 import SequenceModel
 from sequence_conditioning_v1 import request
 torch.set_num_threads(4);records=[]
 for kind in ('direct','diffusion'):
  weight_path=TR/f'results/sequence-feasibility-v1/{kind}-train-only.npz';model=SequenceModel()
  with np.load(weight_path,allow_pickle=False) as z:model.load_state_dict({k:torch.from_numpy(z[k].copy()) for k in z.files})
  model.eval()
  for n in (2,33,120):
   times=np.linspace(0,4,n);y=np.zeros((n,17,9));y[...,3]=1.;y[...,7]=1.;y[...,0]=np.linspace(0,1,n)[:,None];mask=np.zeros((n,17,2),bool);mask[[0,-1]]=True;mask[n//2,7,0]=True;req=request(times,y,mask,np.zeros((17,3)))
   condition=req['condition'][None].copy();noise=np.random.default_rng(20260909).normal(size=(1,n,153)).astype(np.float32);level=np.array([.5],np.float32)
   with torch.no_grad():expected=model(torch.from_numpy(condition),torch.from_numpy(noise),torch.from_numpy(level)).numpy()
   target=BASE/f'{kind}-{n}.npz';np.savez(target,condition=condition,noisy=noise,level=level,expected=expected,mask=req['mask'][None].reshape(1,n,153),baseline=req['baseline'],observed=req['observed']);records.append(dict(kind=kind,frames=n,path=target.relative_to(ROOT).as_posix(),sha256=sha(target),weights=weight_path.relative_to(ROOT).as_posix(),weights_sha256=sha(weight_path)))
 write(BASE/'fixtures.json',dict(records=records,python=sys.version,torch=torch.__version__,numpy=np.__version__,script_sha256=sha(HERE),scope='Synthetic inference fixtures; not training or motion quality'))
def host():
 sys.path.insert(0,str(TR));import numpy as np,bpy
 from sequence_numpy_v1 import forward,sample
 rows=[];fixtures=json.loads((BASE/'fixtures.json').read_text())
 for r in fixtures['records']:
  assert sha(ROOT/r['path'])==r['sha256'] and sha(ROOT/r['weights'])==r['weights_sha256']
  with np.load(ROOT/r['path'],allow_pickle=False) as z:d={k:z[k] for k in z.files}
  with np.load(ROOT/r['weights'],allow_pickle=False) as z:w={k:z[k] for k in z.files}
  result=forward(w,d['condition'],d['noisy'],d['level']);error=float(np.max(abs(result-d['expected'])));assert error<5e-5
  def run():return forward(w,d['condition'],np.zeros_like(d['noisy']),np.zeros(1,np.float32)) if r['kind']=='direct' else sample(w,d['condition'],d['mask'])
  times=[];first=None
  for _ in range(3):
   at=time.perf_counter();prediction=run();times.append(time.perf_counter()-at)
   if first is None:first=prediction.copy()
   else:assert np.array_equal(first,prediction)
  output=(d['baseline']+prediction[0].reshape(r['frames'],17,9)).astype(np.float64);mask=d['mask'][0].reshape(r['frames'],17,9);output[mask]=d['observed'][mask];assert np.array_equal(output[mask],d['observed'][mask]);assert np.isfinite(output).all()
  rows.append(dict(kind=r['kind'],frames=r['frames'],torch_numpy_max_abs_error=error,numpy_seconds=times,known_values_exact=True,repeated_output_exact=True,finite=True));print(json.dumps(rows[-1]),flush=True)
 write(BASE/'host.json',dict(complete=True,cases=rows,host=bpy.app.version_string,python=sys.version,numpy=np.__version__,openblas=os.getenv('OPENBLAS_NUM_THREADS'),fixtures_sha256=sha(BASE/'fixtures.json'),numpy_module_sha256=sha(TR/'sequence_numpy_v1.py'),ui_tested=False,trained_quality_qualified=False))
def main():
 BASE.mkdir(exist_ok=False);env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1');logs=[]
 for name,exe,extra in [('prepare','X:/ComfyUI/ComfyUI_windows_portable/python_embeded/python.exe',['-B',str(HERE),'--prepare']),('host','X:/5.1.0/bforartists.exe',['--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','host'])]:
  path=BASE/(name+'.log');at=time.perf_counter()
  with path.open('w') as out:p=subprocess.run([exe]+extra,stdout=out,stderr=subprocess.STDOUT,env=env,timeout=180)
  row=dict(stage=name,exit_code=p.returncode,seconds=time.perf_counter()-at,log_sha256=sha(path));logs.append(row);write(BASE/'processes.json',logs);print(json.dumps(row),flush=True)
  if name=='prepare':assert p.returncode==0
 assert json.loads((BASE/'host.json').read_text())['complete']
if __name__=='__main__':
 if '--prepare' in sys.argv:prepare()
 elif '--' in sys.argv:host()
 else:main()
