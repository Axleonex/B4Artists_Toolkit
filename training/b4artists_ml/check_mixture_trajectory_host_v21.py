"""Research learned-provider -> actual-rig/action diagnostic, not quality promotion."""
from pathlib import Path
import sys,os,json,time,hashlib,subprocess,traceback
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();TAG=os.environ.get('B4ML_SEMANTIC_HOST_TAG','mixture-trajectory-host-v21')
OUT=ROOT/f'training/b4artists_ml/results/{TAG}.json'

def host():
 import bpy,numpy as np
 sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
 from test_b4artists_ml_anchor_observations import AnchorObservationTests
 from b4artists_ml import workflow as w,posing as p
 import mixture_trajectory_v21 as predictor
 import temporal_projection as projection
 import rig_observations
 model_dir=ROOT/'training/b4artists_ml/results/mixture_trajectory_v21'
 trained=json.loads((model_dir/'report.json').read_text());model_path=model_dir/'best_learned.npz'
 digest=hashlib.sha256(model_path.read_bytes()).hexdigest();assert digest==trained['selection']['best_learned_sha256']
 model=predictor.load(model_path);assert model['kind']=='position_mixture_v21'
 AnchorObservationTests.setUpClass();helper=AnchorObservationTests();rows=[]
 for context,label in [(context,label) for context in [False,True] for label in helper.builders]:
  ob,binding,expected,_=helper.fixture(label);scene=bpy.context.scene;before=helper.state(ob);start=time.perf_counter()
  row=dict(profile=label,context=context,passed=False,learned_model=digest,quality_qualified=trained['gates']['best_learned']['passed'])
  try:
   observation=rig_observations.sample_anchors(ob,3,11,context=context);queries=np.arange(1,8)/8;call=predictor.provider(model)
   begin=time.perf_counter();pred=call(observation,queries);row['inference_ms']=(time.perf_counter()-begin)*1000
   assert pred[0].shape==(7,17,3) and pred[1].shape==(7,17,3,3)
   samples,metrics=projection.generate_samples(ob,call,context=context,iterations=100)
   assert helper.state(ob)==before
   row['frames']=len(samples);row['projection_metrics']=metrics
   w.preview(ob,scene,pose_samples=samples)
   for frame in (3,11):
    scene.frame_set(frame);p._update(ob)
    actual=np.array([ob.matrix_world@ob.pose.bones[n].head for n in binding['names']])
    assert np.max(abs(actual-expected[frame][0]))<2e-5
   scene.frame_set(7,subframe=.25);w.finish_preview(ob,scene,False)
   assert helper.state(ob)==before;row['passed']=True;row['editable_action']=True
  except Exception as exc:
   row.update(error=str(exc),traceback=traceback.format_exc())
   if ob.b4ml.candidate_action:
    scene.frame_set(7,subframe=.25);w.finish_preview(ob,scene,False)
  row['source_restored']=helper.state(ob)==before;row['total_ms']=(time.perf_counter()-start)*1000;rows.append(row)
  result=dict(scope='Best learned candidate diagnostic, including failures. Corpus quality gates are separate and no artifact is promoted.',complete=len(rows)==2*len(helper.builders),passed=len(rows)==2*len(helper.builders) and all(x['passed'] and x['source_restored'] for x in rows),model_path=model_path.relative_to(ROOT).as_posix(),model_sha256=digest,selected_overall=trained['selection']['id'],best_learned_id=trained['frozen_selection']['id'],quality_gates=trained['gates']['best_learned'],rows=rows,runtime_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'b4artists_ml').glob('*.py')},research_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE,ROOT/'training/b4artists_ml/mixture_trajectory_v21.py',ROOT/'training/b4artists_ml/temporal_projection.py',ROOT/'training/b4artists_ml/rig_observations.py']},full_goal_complete=False)
  OUT.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:row[k] for k in ('profile','context','passed','source_restored','total_ms')}),flush=True)

if __name__=='__main__':
 if '--host' in sys.argv:host()
 else:
  if OUT.exists():raise RuntimeError('Evidence exists')
  start=time.perf_counter();log=ROOT/f'training/b4artists_ml/cache/{TAG}.log'
  with log.open('w') as stream:
   done=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','--host'],stdout=stream,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4',B4ML_RUN_LABEL=TAG),timeout=900)
  report=dict(exit_code=done.returncode,seconds=time.perf_counter()-start,log=log.relative_to(ROOT).as_posix())
  (OUT.parent/(TAG+'-process.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
