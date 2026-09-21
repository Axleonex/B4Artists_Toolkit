"""Train-only feasibility of sequence models; never validation or qualification."""
from pathlib import Path
import os,sys,json,time,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();BASE=ROOT/'training/b4artists_ml/results/sequence-feasibility-v2';PYTHON='X:/ComfyUI/ComfyUI_windows_portable/python_embeded/python.exe'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def worker():
 sys.path.insert(0,str(HERE.parent))
 import numpy as np,torch
 from bvh_data import parse_bvh
 import temporal_data as td
 import semantic_motion_data as semantic
 from sequence_packet_v2 import packet
 from sequence_conditioning_v1 import request,restore_observations
 from sequence_model_v1 import SequenceModel
 import sequence_numpy_v1 as portable
 plan=ROOT/'training/b4artists_ml/sequence_feasibility_plan_v2.json';protocol=json.loads(plan.read_text());assert sha(plan)=='534f1d06a5cc56c97497710e573880c2befa45b16003b8276b4a8311504be34c'
 torch.set_num_threads(4);torch.use_deterministic_algorithms(True);torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=True;torch.backends.cuda.matmul.allow_tf32=False;torch.cuda.set_per_process_memory_fraction(.25)
 started=time.perf_counter();manifest=json.loads((ROOT/'training/b4artists_ml/temporal_training_manifest_v19.json').read_text());row=next(r for r in manifest['files'] if r['clip']=='07_01' and r['split']=='train');path=ROOT/'training/b4artists_ml/cache/07_01.bvh';assert sha(path)==row['sha256']
 protected=json.loads((ROOT/'training/b4artists_ml/temporal_expansion_plan_v19.json').read_text())['planned_splits']['confirmation'];assert all(not (ROOT/f'training/b4artists_ml/cache/{n}.bvh').exists() for n in protected)
 motion=semantic.from_bvh(parse_bvh(path.read_text()),30);gap=min(32,len(motion.positions)-3);assert gap>=16;starts=np.unique(np.linspace(1,len(motion.positions)-gap-1,4).astype(int));requests=[];targets=[]
 for start in starts:
  start=int(start);end=start+gap;item=packet(motion,start,end,context=False,pattern=2);target=item['target'];req=item['request'];mask=item['mask'];hidden=target.copy();hidden[~req['mask']]=np.nan;assert np.array_equal(req['condition'],request(np.arange(gap+1)*motion.dt,hidden,mask,item['observations'].rest)['condition']);requests.append(req);targets.append(target)
 cond=np.stack([r['condition'] for r in requests]);base=np.stack([r['baseline'].reshape(gap+1,153) for r in requests]);mask=np.stack([r['mask'].reshape(gap+1,153) for r in requests]);truth=np.stack(targets).reshape(base.shape).astype(np.float32);residual=truth-base;residual[mask]=0
 ct=torch.tensor(cond,device='cuda');mt=torch.tensor(mask,device='cuda');yt=torch.tensor(residual,device='cuda');unknown=(~mt).float();schedule=torch.tensor(portable.alpha_schedule(),device='cuda');results=[]
 report=dict(complete=False,plan_sha256=sha(plan),train_clip='07_01',train_clip_sha256=sha(path),train_windows=len(starts),gap=gap,source_frames=[motion.frames[int(s):int(s)+gap+1].tolist() for s in starts],artificial_frame_zero_excluded=True,validation_read=False,confirmation_read=False,hidden_feature_invariance=True,python=sys.version,torch=torch.__version__,numpy=np.__version__,gpu=torch.cuda.get_device_name(0),gpu_memory_fraction=.25,models=results,full_goal_complete=False,quality_qualified=False,scope='Capacity/information-boundary/export checks on one training clip. Fitting is deliberately in-sample; no generalization, style, physics, or Cascadeur claim.')
 for kind in ('direct','diffusion'):
  torch.manual_seed(20260909);torch.cuda.manual_seed_all(20260909);model=SequenceModel().cuda();count=sum(p.numel() for p in model.parameters());assert count<=1200000;optimizer=torch.optim.AdamW(model.parameters(),lr=.0003,weight_decay=.0001);fixed_noise=torch.randn(yt.shape,device='cuda');fixed_levels=torch.full((len(ct),),128,device='cuda',dtype=torch.long);history=[]
  def objective(levels,noise):
   noisy=torch.zeros_like(yt) if kind=='direct' else (schedule[levels,None,None].sqrt()*yt+(1-schedule[levels,None,None]).sqrt()*noise).masked_fill(mt,0)
   level=torch.zeros(len(ct),device='cuda') if kind=='direct' else levels.float()/255
   prediction=model(ct,noisy,level).masked_fill(mt,0)
   return ((prediction-yt).square()*unknown).sum()/unknown.sum()
  with torch.no_grad():initial=float(objective(fixed_levels,fixed_noise))
  begin=time.perf_counter()
  for step in range(80):
   assert time.perf_counter()-started<300 and time.time()<1789053845.
   optimizer.zero_grad(set_to_none=True);levels=torch.randint(0,256,(len(ct),),device='cuda');loss=objective(levels,torch.randn(yt.shape,device='cuda'));assert torch.isfinite(loss);loss.backward();grad=torch.nn.utils.clip_grad_norm_(model.parameters(),1.);assert torch.isfinite(grad);optimizer.step()
   if step%20==0:history.append(dict(step=step,loss=float(loss.detach())));print(json.dumps(dict(model=kind,step=step,loss=history[-1]['loss'])),flush=True)
  torch.cuda.synchronize();elapsed=time.perf_counter()-begin
  model.eval()
  with torch.no_grad():final=float(objective(fixed_levels,fixed_noise))
  assert final<initial,'Training-only capacity check did not improve'
  weights={k:v.detach().cpu().numpy().copy() for k,v in model.state_dict().items()};weight_path=BASE/(kind+'-train-only.npz');np.savez(weight_path,**weights);assert weight_path.stat().st_size<5*1024**2
  model.cpu();noise=np.random.default_rng(123).normal(size=base.shape).astype(np.float32);levels=np.full(len(cond),.5,dtype=np.float32)
  with torch.no_grad():expected=model(torch.from_numpy(cond),torch.from_numpy(noise),torch.from_numpy(levels)).numpy()
  actual=portable.forward(weights,cond,noise,levels);error=float(np.max(abs(expected-actual)));assert error<5e-5
  def infer():return portable.forward(weights,cond,np.zeros_like(base),np.zeros(len(cond),np.float32)) if kind=='direct' else portable.sample(weights,cond,mask,seed=20260909)
  at=time.perf_counter();generated=infer();seconds=time.perf_counter()-at;again=infer();assert np.array_equal(generated,again)
  generated[mask]=0
  for i,req in enumerate(requests):
   out=restore_observations((base[i]+generated[i]).reshape(gap+1,17,9),req);assert np.array_equal(out[req['mask']],req['observed'][req['mask']])
  changed=cond.copy();changed[0,1,0]+=.25;remote=portable.forward(weights,changed,noise,levels);temporal_effect=float(np.max(abs(remote[0,gap//2]-actual[0,gap//2])));assert temporal_effect>1e-9
  record=dict(kind=kind,parameters=count,optimizer_steps=80,initial_train_probe_loss=initial,final_train_probe_loss=final,loss_reduced=True,training_seconds=elapsed,history=history,weight_sha256=sha(weight_path),weight_bytes=weight_path.stat().st_size,torch_numpy_max_abs_error=error,deterministic_sampling=True,authored_observations_exact=True,temporal_influence=temporal_effect,numpy_inference_seconds=seconds,inference_shape=list(cond.shape[:2]),trained_only_on_one_clip=True,deployable=False)
  results.append(record);write(BASE/'report.json',report);print(json.dumps(record),flush=True)
 report.update(complete=True,seconds=time.perf_counter()-started,peak_cuda_bytes=torch.cuda.max_memory_allocated(),source_sha256={p.name:sha(p) for p in (HERE,ROOT/'training/b4artists_ml/sequence_conditioning_v1.py',ROOT/'training/b4artists_ml/sequence_model_v1.py',ROOT/'training/b4artists_ml/sequence_numpy_v1.py',ROOT/'training/b4artists_ml/sequence_packet_v2.py')});assert all(not (ROOT/f'training/b4artists_ml/cache/{n}.bvh').exists() for n in protected);write(BASE/'report.json',report)
def main():
 BASE.mkdir(exist_ok=False);log=BASE/'worker.log';at=time.perf_counter()
 with log.open('w') as out:proc=subprocess.run([PYTHON,'-B',str(HERE),'--worker'],stdout=out,stderr=subprocess.STDOUT,timeout=330,env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1',CUBLAS_WORKSPACE_CONFIG=':4096:8'))
 write(BASE/'process.json',dict(exit_code=proc.returncode,seconds=time.perf_counter()-at,log_sha256=sha(log)));print(json.dumps(dict(exit_code=proc.returncode,seconds=time.perf_counter()-at)),flush=True)
 if proc.returncode:raise SystemExit(proc.returncode)
 assert json.loads((BASE/'report.json').read_text())['complete']
if __name__=='__main__':
 if '--worker' in sys.argv:worker()
 else:main()
