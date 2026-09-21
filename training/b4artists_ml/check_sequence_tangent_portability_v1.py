"""Nontrivial synthetic export check in training Python and actual Bforartists."""
from pathlib import Path
import sys,os,json,time,hashlib,subprocess
HERE=Path(__file__).resolve();TR=HERE.parent;ROOT=TR.parents[1];OUT=TR/'results/sequence-tangent-portability-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def prepare():
 import numpy as np,torch
 from sequence_tangent_model_v1 import SequenceModel
 from sequence_model_v1 import SequenceModel as Original
 from sequence_tangent_context_v1 import build
 from sequence_tangent_numpy_v1 import forward
 torch.set_num_threads(4);torch.manual_seed(20260909);old=Original();torch.manual_seed(20260909);new=SequenceModel();a=old.state_dict();b=new.state_dict()
 for k in a:
  if k=='input.weight':assert torch.equal(a[k][:,:394],b[k][:,:394]) and torch.equal(a[k][:,394:],b[k][:,666:]) and torch.count_nonzero(b[k][:,394:666])==0
  else:assert torch.equal(a[k],b[k]),k
 # Nonzero output head and added columns are mandatory: zero initialization would make parity vacuous.
 with torch.no_grad():
  torch.manual_seed(1701);new.output.weight.normal_(0,.03);new.output.bias.normal_(0,.01);new.input.weight[:,394:666].normal_(0,.01)
 weights={k:v.detach().numpy().copy() for k,v in new.state_dict().items()};wp=OUT/'synthetic-weights.npz';np.savez(wp,**weights);records=[]
 for n in (2,33,120):
  t=np.linspace(0,4,n);y=np.zeros((n,17,9));y[:,:,0]=t[:,None]**2*.1;y[:,:,3]=1;y[:,:,7]=1;m=np.zeros((n,17,2),bool);m[[0,-1]]=True
  if n>2:m[[1,-2]]=True;m[n//2,7,0]=True
  enriched=build(t,y,m,np.zeros((17,3)));req=enriched['request'];c=enriched['condition'][None].copy();noise=np.random.default_rng(1701).normal(size=(1,n,153)).astype(np.float32);level=np.array([.5],np.float32)
  with torch.no_grad():expected=new(torch.from_numpy(c),torch.from_numpy(noise),torch.from_numpy(level)).numpy()
  actual=forward(weights,c,noise,level);error=float(np.max(abs(expected-actual)));assert error<5e-5 and np.max(abs(expected))>.01
  path=OUT/f'frames-{n}.npz';np.savez(path,condition=c,noisy=noise,level=level,expected=expected,mask=req['mask'],baseline=req['baseline'],observed=req['observed']);records.append(dict(frames=n,path=path.relative_to(ROOT).as_posix(),sha256=sha(path),cpu_error=error))
 # Added features demonstrably affect nontrivial synthetic network output.
 removed=c.copy();removed[:,:,394:]=0;delta=float(np.max(abs(forward(weights,c,noise,level)-forward(weights,removed,noise,level))));assert delta>1e-4
 write(OUT/'fixtures.json',dict(complete=True,records=records,weights=wp.relative_to(ROOT).as_posix(),weights_sha256=sha(wp),shared_initialization_exact=True,synthetic_tangent_response=delta,parameters=sum(p.numel() for p in new.parameters()),torch=torch.__version__,python=sys.version,trained=False))
def host():
 import numpy as np,bpy
 from sequence_tangent_numpy_v1 import forward
 from sequence_tangent_provider_v1 import load_weights
 fixtures=read(OUT/'fixtures.json');weights=load_weights(ROOT/fixtures['weights'],fixtures['weights_sha256']);rows=[]
 for f in fixtures['records']:
  p=ROOT/f['path'];assert sha(p)==f['sha256']
  with np.load(p,allow_pickle=False) as z:d={k:z[k] for k in z.files}
  at=time.perf_counter();value=forward(weights,d['condition'],d['noisy'],d['level']);elapsed=time.perf_counter()-at;error=float(np.max(abs(value-d['expected'])));assert error<5e-5;out=(d['baseline']+value[0].reshape(f['frames'],17,9)).astype(float);out[d['mask']]=d['observed'][d['mask']];assert np.array_equal(out[d['mask']],d['observed'][d['mask']]);assert np.array_equal(value,forward(weights,d['condition'],d['noisy'],d['level']));rows.append(dict(frames=f['frames'],torch_numpy_max_abs_error=error,seconds=elapsed,known_values_exact=True,repeat_exact=True))
 write(OUT/'host.json',dict(complete=True,cases=rows,host=bpy.app.version_string,python=sys.version,numpy=np.__version__,fixtures_sha256=sha(OUT/'fixtures.json'),sources={n:sha(TR/n) for n in ('sequence_tangent_model_v1.py','sequence_tangent_numpy_v1.py','sequence_tangent_provider_v1.py','sequence_tangent_context_v1.py')},ui_tested=False,trained_quality_qualified=False));print(json.dumps(rows),flush=True)
def main():
 OUT.mkdir(exist_ok=False);env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1');rows=[]
 for name,command in [('prepare',['X:/ComfyUI/ComfyUI_windows_portable/python_embeded/python.exe','-B',str(HERE),'--prepare']),('host',['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','host'])]:
  log=OUT/(name+'.log');at=time.perf_counter()
  with log.open('w') as out:p=subprocess.run(command,stdout=out,stderr=subprocess.STDOUT,env=env,timeout=180)
  rows.append(dict(stage=name,exit_code=p.returncode,seconds=time.perf_counter()-at,log_sha256=sha(log)));write(OUT/'processes.json',rows)
  if name=='prepare':assert p.returncode==0
  else:assert read(OUT/'host.json')['complete']
 print(json.dumps(dict(processes=rows,assertions_passed=True,native_exit_qualified=rows[-1]['exit_code']==0)),flush=True)
if __name__=='__main__':
 if '--prepare' in sys.argv:prepare()
 elif 'host' in sys.argv:host()
 else:main()
