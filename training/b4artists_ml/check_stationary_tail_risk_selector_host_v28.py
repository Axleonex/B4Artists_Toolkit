"""Actual-rig stationary learned-motion preservation, editable action and recovery."""

from pathlib import Path

import os,sys,json,time,hashlib,subprocess,traceback

ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();TAG='stationary-tail-risk-selector-host-v28';OUT=ROOT/f'training/b4artists_ml/results/{TAG}.json'



def host():

 import bpy,numpy as np

 sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]

 from test_b4artists_ml_anchor_observations import AnchorObservationTests

 from b4artists_ml import workflow as w

 import tail_risk_selector_v28 as predictor

 from kinematic_trajectory_v20 import observation_scale

 import temporal_projection as projection

 import rig_observations

 folder=ROOT/'training/b4artists_ml/results/tail_risk_selector_v28';trained=json.loads((folder/'report.json').read_text());path=folder/'best_learned.npz';digest=hashlib.sha256(path.read_bytes()).hexdigest();assert digest==trained['selection']['best_learned_sha256'];model=predictor.load(path)

 complete=json.loads((folder/'complete.json').read_text());assert complete['complete'] and complete['report_sha256']==hashlib.sha256((folder/'report.json').read_bytes()).hexdigest()
 AnchorObservationTests.setUpClass();helper=AnchorObservationTests();rows=[]

 for context in [False,True]:

  for label in helper.builders:

   ob,binding,expected,_=helper.fixture(label);scene=bpy.context.scene

   payload=next(a.payload for a in ob.b4ml.anchors if a.frame==3)

   next(a for a in ob.b4ml.anchors if a.frame==11).payload=payload

   if context:

    for frame in [2,12]:item=ob.b4ml.anchors.add();item.frame=frame;item.payload=payload

   before=helper.state(ob);start=time.perf_counter();row=dict(profile=label,context=context,passed=False)

   try:

    observation=rig_observations.sample_anchors(ob,3,11,context=context);row['observed_scale_max']=float(np.max(observation_scale(observation)))

    samples,metrics=projection.generate_samples(ob,predictor.provider(model),context=context,iterations=100);assert helper.state(ob)==before

    w.preview(ob,scene,pose_samples=samples);position_error=0.;rotation_error=0.

    for frame in samples:

     scene.frame_set(int(frame),subframe=frame-int(frame));points,rotations=helper.pose(ob,binding)

     position_error=max(position_error,float(np.max(abs(points-expected[3][0]))));rotation_error=max(rotation_error,float(np.max(abs(rotations-expected[3][1]))))

    row.update(frames=len(samples),position_component_max=position_error,rotation_matrix_component_max=rotation_error)

    assert position_error<2e-5 and rotation_error<2e-5,'Stationary rig drift exceeds existing host numerical tolerance'

    scene.frame_set(7,subframe=.25);w.finish_preview(ob,scene,False);assert helper.state(ob)==before;row.update(passed=True,editable_action=True)

   except Exception as exc:

    row.update(error=str(exc),traceback=traceback.format_exc())

    if ob.b4ml.candidate_action:scene.frame_set(7,subframe=.25);w.finish_preview(ob,scene,False)

   row['source_restored']=helper.state(ob)==before;row['total_ms']=(time.perf_counter()-start)*1000;rows.append(row)

   report=dict(scope='Controlled stationary authored poses through trained proposal, actual-rig projection, editable candidate and Discard. No motion-quality promotion.',complete=len(rows)==16,passed=len(rows)==16 and all(r['passed'] and r['source_restored'] for r in rows),model_sha256=digest,quality_qualified=trained['gates']['best_learned']['passed'],rows=rows,runtime_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'b4artists_ml').glob('*.py')},research_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE,ROOT/'training/b4artists_ml/tail_risk_selector_v28.py',ROOT/'training/b4artists_ml/soft_selector_v27.py',ROOT/'training/b4artists_ml/projected_selector_v26.py',ROOT/'training/b4artists_ml/temporal_projection.py',ROOT/'training/b4artists_ml/rig_observations.py']},full_goal_complete=False)

   OUT.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(json.dumps(row),flush=True)



if __name__=='__main__':

 if '--host' in sys.argv:host()

 else:

  if OUT.exists():raise RuntimeError('Evidence exists')

  start=time.perf_counter();log=ROOT/f'training/b4artists_ml/cache/{TAG}.log'

  with log.open('w') as stream:

   done=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','--host'],stdout=stream,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4',B4ML_RUN_LABEL=TAG),timeout=900)

  report=dict(exit_code=done.returncode,seconds=time.perf_counter()-start,log=log.relative_to(ROOT).as_posix());(OUT.parent/(TAG+'-process.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

