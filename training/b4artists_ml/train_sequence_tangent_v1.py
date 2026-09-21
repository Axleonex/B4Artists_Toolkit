"""Fixed prospective corpus fits. Train partition only; no model selection."""
from pathlib import Path
import os,sys,json,time,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();TR=HERE.parent;BASE=TR/'results/sequence-tangent-training-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def rss():
 import ctypes
 from ctypes import wintypes
 class Counters(ctypes.Structure):
  _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(name,ctypes.c_size_t) for name in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage')]
 c=Counters();c.cb=ctypes.sizeof(c);ctypes.windll.kernel32.GetCurrentProcess.restype=ctypes.c_void_p
 if not ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.c_void_p(ctypes.windll.kernel32.GetCurrentProcess()),ctypes.byref(c),c.cb):raise RuntimeError('Process memory measurement unavailable')
 return c.WorkingSetSize

def worker(kind,seed):
 sys.path.insert(0,str(TR));import numpy as np,torch
 from sequence_tangent_model_v1 import SequenceModel
 from sequence_numpy_v1 import alpha_schedule
 from sequence_tangent_numpy_v1 import forward
 from sequence_tangent_training_data_v1 import augment
 plan_path=TR/'sequence_tangent_fit_plan_v1.json';plan=json.loads(plan_path.read_text());assert sha(plan_path)==json.loads((BASE/'frozen-plan.json').read_text())['plan_sha256'];assert all(sha(TR/n)==h for n,h in plan['sources'].items());manifest_path=TR/'results/sequence-corpus-v2/manifest.json';manifest=json.loads(manifest_path.read_text());assert manifest['complete'] and manifest['plan_sha256']==plan['base_corpus_plan_sha256'] and not manifest['validation_read'] and not manifest['confirmation_read']
 portable=json.loads((TR/'results/sequence-tangent-portability-v2/host.json').read_text());assert portable['complete'] and len(portable['cases'])==3 and all(r['known_values_exact'] and r['torch_numpy_max_abs_error']<5e-5 for r in portable['cases']);assert all(sha(TR/n)==h for n,h in portable['sources'].items())
 original=json.loads((TR/'results/sequence-feasibility-v2/report.json').read_text());assert original['complete'] and all(sha(TR/n)==h for n,h in original['source_sha256'].items())
 assert kind in ('direct','diffusion') and seed in plan['training']['seeds'];out=BASE/(kind+'-'+str(seed));out.mkdir(exist_ok=False);data=[];t=time.perf_counter();read_bytes=0
 for row in manifest['files']:
  path=ROOT/row['path'];assert sha(path)==row['sha256']
  with np.load(path,allow_pickle=False) as z:arrays={k:z[k].copy() for k in z.files}
  assert all(np.isfinite(a).all() for a in arrays.values());assert arrays['condition'].shape[0]==row['windows'];assert np.array_equal(arrays['target'][arrays['mask']],arrays['baseline'][arrays['mask']]);read_bytes+=sum(a.nbytes for a in arrays.values());data.append(arrays)
 assert read_bytes==manifest['array_bytes'] and read_bytes<3221225472 and rss()<4*1024**3
 augmentation=augment(data,manifest);assert augmentation['array_bytes']<3221225472 and rss()<4*1024**3
 protected=json.loads((TR/'temporal_expansion_plan_v19.json').read_text())['planned_splits']['confirmation'];assert all(not (TR/'cache'/(n+'.bvh')).exists() for n in protected)
 torch.set_num_threads(4);torch.manual_seed(seed);torch.cuda.manual_seed_all(seed);torch.use_deterministic_algorithms(True);torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True;torch.backends.cuda.matmul.allow_tf32=False;torch.cuda.set_per_process_memory_fraction(.25)
 model=SequenceModel().cuda();optimizer=torch.optim.AdamW(model.parameters(),lr=.0003,weight_decay=.0001);schedule=torch.tensor(alpha_schedule(),device='cuda');rng=np.random.default_rng(seed);history=[];maximum_rss=rss();begin=time.perf_counter();status='running'
 report=dict(kind=kind,seed=seed,complete=False,quality_qualified=False,manifest_sha256=sha(manifest_path),plan_sha256=sha(plan_path),script_sha256=sha(HERE),windows=manifest['window_count'],clip_count=manifest['clip_count'],loaded_array_bytes=read_bytes,augmentation=augmentation,load_seconds=begin-t,history=history,python=sys.version,torch=torch.__version__,numpy=np.__version__,source_sha256={n:sha(TR/n) for n in ('sequence_model_v1.py','sequence_tangent_model_v1.py','sequence_tangent_numpy_v1.py','sequence_tangent_context_v1.py','sequence_tangent_training_data_v1.py','sequence_conditioning_v1.py','sequence_packet_v2.py','semantic_motion_data.py','rig_observations.py')},validation_read=False,confirmation_read=False,full_goal_complete=False)
 def objective(prediction,base,target,mask,dt):
  error=(base+prediction.masked_fill(mask,0)-target).reshape(*prediction.shape[:2],17,9);unknown=(~mask).reshape(error.shape)
  p=(error[...,:3].square()*unknown[...,:3]).sum()/unknown[...,:3].sum().clamp_min(1);r=(error[...,3:].square()*unknown[...,3:]).sum()/unknown[...,3:].sum().clamp_min(1)
  velocity=(error[:,1:]-error[:,:-1])/dt[:,None,None,None];vm=unknown[:,1:]|unknown[:,:-1];v=(velocity.square()*vm).sum()/vm.sum().clamp_min(1)
  acc=(error[:,2:]-2*error[:,1:-1]+error[:,:-2])/dt[:,None,None,None].square();am=unknown[:,2:]|unknown[:,1:-1]|unknown[:,:-2];a=(acc.square()*am).sum()/am.sum().clamp_min(1)
  return p+.1*r+.01*v+.0001*a
 try:
  for epoch in range(60):
   batches=[]
   for bi,bucket in enumerate(data):
    indices=rng.permutation(len(bucket['condition']));batches.extend((bi,indices[i:i+16]) for i in range(0,len(indices),16))
   rng.shuffle(batches);total=0.;examples=0
   for bi,ids in batches:
    if time.perf_counter()-begin>=1800 or time.time()>=1789053845.:raise TimeoutError('Fixed training budget reached')
    bucket=data[bi];ct=torch.tensor(bucket['condition'][ids],device='cuda');base=torch.tensor(bucket['baseline'][ids],device='cuda');target=torch.tensor(bucket['target'][ids],device='cuda');mask=torch.tensor(bucket['mask'][ids],device='cuda');dt=torch.tensor(bucket['dt'][ids],device='cuda');residual=(target-base).masked_fill(mask,0)
    if kind=='direct':noisy=torch.zeros_like(residual);level=torch.zeros(len(ids),device='cuda')
    else:
     steps=torch.randint(0,256,(len(ids),),device='cuda');a=schedule[steps,None,None];noisy=(a.sqrt()*residual+(1-a).sqrt()*torch.randn_like(residual)).masked_fill(mask,0);level=steps.float()/255
    optimizer.zero_grad(set_to_none=True);prediction=model(ct,noisy,level);loss=objective(prediction,base,target,mask,dt);assert torch.isfinite(loss);loss.backward();norm=torch.nn.utils.clip_grad_norm_(model.parameters(),1.);assert torch.isfinite(norm);optimizer.step();total+=float(loss.detach())*len(ids);examples+=len(ids)
   maximum_rss=max(maximum_rss,rss());assert maximum_rss<4*1024**3 and examples==manifest['window_count'];row=dict(epoch=epoch+1,mean_training_loss=total/examples,seconds=time.perf_counter()-begin,examples=examples);history.append(row);write(out/'progress.json',report);print(json.dumps(dict(kind=kind,seed=seed,**row)),flush=True)
  status='complete';report['complete']=True
 except BaseException as exc:
  status='failed';report['error']=repr(exc);raise
 finally:
  weights={k:v.detach().cpu().numpy().copy() for k,v in model.state_dict().items()};path=out/('weights.npz' if status=='complete' else 'partial-weights.npz');np.savez(path,**weights);report.update(status=status,completed_epochs=len(history),weights=path.relative_to(ROOT).as_posix(),weights_sha256=sha(path),weight_bytes=path.stat().st_size,training_seconds=time.perf_counter()-begin,peak_cuda_bytes=torch.cuda.max_memory_allocated(),peak_observed_rss=maximum_rss)
  assert all(not (TR/'cache'/(n+'.bvh')).exists() for n in protected)
  if status=='complete':
   model.eval().cpu();bucket=data[-1];cond=bucket['condition'][:1];noise=np.random.default_rng(seed).normal(size=(1,cond.shape[1],153)).astype(np.float32);level=np.array([.5],np.float32)
   with torch.no_grad():expected=model(torch.from_numpy(cond),torch.from_numpy(noise),torch.from_numpy(level)).numpy()
   actual=forward(weights,cond,noise,level);report['cpu_export_max_abs_error']=float(np.max(abs(expected-actual)));assert report['cpu_export_max_abs_error']<5e-5
  write(out/'report.json',report)

def main():
 BASE.mkdir(exist_ok=False);write(BASE/'frozen-plan.json',dict(plan_sha256=sha(TR/'sequence_tangent_fit_plan_v1.json'),script_sha256=sha(HERE),recorded_at=time.time(),validation_read=False));rows=[];env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1',CUBLAS_WORKSPACE_CONFIG=':4096:8')
 for kind in ('direct',):
  for seed in (20260909,20260910):
   log=BASE/(kind+'-'+str(seed)+'.log');at=time.perf_counter()
   with log.open('w') as out:
    proc=subprocess.Popen(['X:/ComfyUI/ComfyUI_windows_portable/python_embeded/python.exe','-B',str(HERE),'--worker',kind,str(seed)],stdout=out,stderr=subprocess.STDOUT,env=env)
    write(BASE/'active-process.json',dict(pid=proc.pid,kind=kind,seed=seed,started_at=time.time(),log=log.relative_to(ROOT).as_posix()))
    try:code=proc.wait(timeout=2460)
    except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=30);raise
   row=dict(kind=kind,seed=seed,exit_code=code,seconds=time.perf_counter()-at,log_sha256=sha(log));rows.append(row);write(BASE/'processes.json',rows);print(json.dumps(row),flush=True)
   if code:raise SystemExit(code)
 write(BASE/'active-process.json',dict(terminal=True,all_complete=True));assert len(rows)==2
if __name__=='__main__':
 if '--worker' in sys.argv:worker(sys.argv[-2],int(sys.argv[-1]))
 else:main()
