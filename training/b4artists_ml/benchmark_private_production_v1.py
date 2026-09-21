"""Serial ABBA preview timing and exact output comparison on default Rigify."""
from pathlib import Path
import sys,os,json,time,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();BASE=ROOT/'training/b4artists_ml/results/private-production-benchmark-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def host():
 import bpy,numpy as np
 from unittest.mock import patch
 sys.path.insert(0,str(ROOT));import b4artists_ml
 from b4artists_ml import workflow as w,contacts as c,rig_state as rs,temporal_preview as tp,temporal_generation as g
 b4artists_ml.register()
 reference=ROOT/'training/b4artists_ml/results/broader-shape-runtime-v1/rigify_default/reach_hold-smooth_both.blend'
 bpy.ops.wm.open_mainfile(filepath=str(reference),load_ui=False,use_scripts=False)
 scene=bpy.context.scene;ob=next(o for o in scene.objects if o.type=='ARMATURE' and o.b4ml.candidate_action);w.finish_preview(ob,scene,False)
 source=ob.animation_data.action;sig=c._action_signature(ob);modes=rs.mode_values(ob);anchors=[(a.frame,a.payload) for a in ob.b4ml.anchors];inventory={n:len(getattr(bpy.data,n)) for n in ('objects','armatures','scenes','actions')}
 def curves():
  return sorted((fc.data_path,fc.array_index,tuple((tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.interpolation,k.handle_left_type,k.handle_right_type) for k in fc.keyframe_points)) for fc in w.action_curves(ob.animation_data.action,ob.animation_data.action_slot))
 report=dict(complete=False,method='One native process; guarded/private/private/guarded ABBA. All smoothing enabled. No concurrent task-owned training, evaluation or native suites. Timings exclude test assertion overhead. First invocation is not verified OS-cold; no UI events.',runs=[],runtime_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')},reference_sha256=sha(reference),script_sha256=sha(HERE),ui_responsiveness_qualified=False,host_version=bpy.app.version_string)
 private_factory=g.generate_private_steps;expected=None
 for index,path in enumerate(('guarded','private','private','guarded')):
  scene.frame_set(1);ob.b4ml.temporal_smoothing=True;ticks=[];factory=g.generate_steps if path=='guarded' else private_factory
  with patch.object(g,'generate_private_steps',factory):
   at=time.perf_counter();tp.start(ob,scene);start_seconds=time.perf_counter()-at
   while ob.b4ml.temporal_running:
    at=time.perf_counter();done=tp.step(ob);ticks.append(time.perf_counter()-at)
    if not done:assert ob.animation_data.action==source and c._action_signature(ob)==sig
  output=curves()
  if expected is None:expected=output
  assert output==expected,'Candidate curve output changed'
  w.finish_preview(ob,scene,False)
  assert ob.animation_data.action==source and c._action_signature(ob)==sig and rs.mode_values(ob)==modes and [(a.frame,a.payload) for a in ob.b4ml.anchors]==anchors
  assert inventory=={n:len(getattr(bpy.data,n)) for n in inventory} and not g._LIVE and not g._OWNERS
  row=dict(index=index,path=path,start_seconds=start_seconds,measured_work_seconds=start_seconds+sum(ticks),max_tick_seconds=max(ticks),p95_tick_seconds=float(np.percentile(ticks,95)),ticks=len(ticks),exact_candidate_curves=True,source_preserved=True,inventory_preserved=True)
  report['runs'].append(row);write(BASE/'report.json',report);print(json.dumps(row),flush=True)
 report['complete']=True;report['median_seconds']={path:float(np.median([v['measured_work_seconds'] for v in report['runs'] if v['path']==path])) for path in ('guarded','private')};report['ratio']=report['median_seconds']['private']/report['median_seconds']['guarded'];write(BASE/'report.json',report)
def main():
 rows=json.loads((ROOT/'training/b4artists_ml/results/private-production-full-v1-regression.json').read_text());assert len(rows)==41 and all(r['assertions_passed'] for r in rows)
 assert json.loads((ROOT/'training/b4artists_ml/results/sequence-development-v1/report.json').read_text())['complete']
 BASE.mkdir(exist_ok=False);log=BASE/'host.log';at=time.perf_counter()
 with log.open('w') as out:p=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','host'],stdout=out,stderr=subprocess.STDOUT,env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1'),timeout=600)
 write(BASE/'process.json',dict(exit_code=p.returncode,seconds=time.perf_counter()-at,log_sha256=sha(log)));assert json.loads((BASE/'report.json').read_text())['complete'];print(json.dumps(dict(complete=True,exit_code=p.returncode)),flush=True)
if __name__=='__main__':
 if '--' in sys.argv:host()
 else:main()
