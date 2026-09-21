"""Actual-window live preview lifecycle; automated evidence, not animator assessment."""
from pathlib import Path
import sys,os,json,time,traceback,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();TAG=os.environ.get('B4ML_LIVE_UI_TAG','v1')
REPORT=ROOT/f'training/b4artists_ml/results/live-pose-ui-{TAG}.json'

def run():
 import bpy,numpy as np
 sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]
 import b4artists_ml
 from b4artists_ml import body_live as live,body_preview as body,workflow as w,rig_state as rs
 package_root=Path(b4artists_ml.__file__).resolve().parent
 expected_root=Path(os.environ.get('B4ML_PACKAGE',str(ROOT))).resolve()/'b4artists_ml'
 assert package_root==expected_root
 loaded_runtime_sha256={p.relative_to(package_root.parent).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in package_root.glob('*.py')}
 from test_b4artists_ml_body_live import LivePoseTests
 LivePoseTests.setUpClass();helper=LivePoseTests();imported=os.environ.get('B4ML_IMPORTED_UI')
 if imported:
  from test_b4artists_ml_imported_humanoids import authored
  ob,mesh,roles=authored(imported,1);source=w.raw_pose(ob);modes=rs.mode_values(ob);action=ob.animation_data.action;keys=helper.keys(ob)
  body.begin(ob,bpy.context.scene);ob.b4ml.body_influence=0.;ob.b4ml.body_targets['Head'].target.location.y+=.002
 else:ob,source,modes,action,keys=helper.fixture('rigify_default')
 state=dict(name=ob.name,source=source,modes=modes,action=action.name,keys=keys,phase='dismiss',started=time.monotonic(),events=[])
 samples=[];original=live.tick
 def timed(obj,**kwargs):
  start=time.perf_counter();before=obj.b4ml.body_running
  try:
   result=original(obj,**kwargs);samples.append(dict(ms=(time.perf_counter()-start)*1000,result=result,already_solving=before));return result
  except Exception:
   samples.append(dict(ms=(time.perf_counter()-start)*1000,result='error',already_solving=before));raise
 live.tick=timed
 def source_ok(obj):
  assert obj.animation_data.action.name==state['action']
  assert helper.keys(obj)==state['keys']
  assert w.raw_pose(obj)==state['source']
  assert rs.mode_values(obj)==state['modes']
 def idle(obj):
  return not obj.b4ml.body_running and body._read(obj)['signature']==body._request(obj,body._get(obj))[2]
 def select(obj,win):
  for selected in list(bpy.context.selected_objects):selected.select_set(False)
  obj.select_set(True);win.view_layer.objects.active=obj
 def change(obj):
  obj.b4ml.body_targets['Head'].target.location.y+=.002;bpy.context.view_layer.update()
 def start(obj):
  assert bpy.ops.b4ml.body_live('INVOKE_DEFAULT')=={'RUNNING_MODAL'}
 def finish(passed,error=None):
  groups={name:[r['ms'] for r in samples if (r['result'] in ('idle','queued'))==schedule] for name,schedule in (('scheduling',True),('fit_and_completion',False))}
  report=dict(fixture=imported or 'rigify_default',passed=passed,phase=state['phase'],events=state['events'],error=error,elapsed_seconds=time.monotonic()-state['started'],timings={k:dict(count=len(v),p95_ms=float(np.percentile(v,95)) if v else None,max_ms=max(v) if v else None) for k,v in groups.items()},scope='Automated actual-window operators, keyboard transform and Escape, undo/redo, file save/reload and add-on unregister. Independent animator usability remains unverified.',runtime_sha256=loaded_runtime_sha256,package_root=str(package_root),screenshot=state.get('screenshot'))
  REPORT.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True);bpy.ops.wm.quit_blender()
 def tick():
  try:
   if time.monotonic()-state['started']>300:raise AssertionError('Live UI workflow timeout')
   win=bpy.context.window_manager.windows[0];area=next(a for a in win.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW');area.spaces.active.show_region_ui=True
   obj=bpy.data.objects[state['name']]
   with bpy.context.temp_override(window=win,area=area,region=region):
    phase=state['phase']
    if phase!=state.get('logged_phase'):
     print('Live UI phase: '+phase,flush=True);state['logged_phase']=phase;state['phase_started']=time.monotonic()
    if phase=='keyboard_edit' and time.monotonic()-state['phase_started']>10:
     raise AssertionError('Keyboard edit did not reach expected target: '+str(tuple(obj.b4ml.body_targets['Head'].target.location))+' before '+str(state['target_before']))
    if phase=='dismiss':
     win.event_simulate(type='ESC',value='PRESS')
     # Category location verified in live-pose-ui-package-v1.png from this disposable window.
     assert win.width==1920 and win.height in (1008,1009)
     win.event_simulate(type='MOUSEMOVE',value='NOTHING',x=1574,y=win.height-357)
     win.event_simulate(type='LEFTMOUSE',value='PRESS',x=1574,y=win.height-357)
     win.event_simulate(type='LEFTMOUSE',value='RELEASE',x=1574,y=win.height-357)
     select(obj,win);bpy.ops.view3d.view_axis(type='FRONT');bpy.ops.view3d.view_selected(use_all_regions=False);state['phase']='start'
    elif phase=='start':
     bpy.ops.ed.undo_push(message='Live preview ready');start(obj);state['phase']='initial_fit'
    elif phase=='initial_fit':
     if not idle(obj):return .03
     state['events'].append('Live modal solved initial targets')
     old=live._WATCHERS[obj.as_pointer()]
     assert bpy.ops.b4ml.body_live('INVOKE_DEFAULT')=={'FINISHED'}
     start(obj);assert live._WATCHERS[obj.as_pointer()] is not old
     state['events'].append('Immediate stop/start created a separately owned live session')
     target=obj.b4ml.body_targets['Head'].target;select(target,win);state['target_before']=tuple(target.location)
     assert bpy.ops.transform.translate('INVOKE_DEFAULT',constraint_axis=(False,True,False))=={'RUNNING_MODAL'}
     assert 'unicode' in win.bl_rna.functions['event_simulate'].parameters
     for event,char in (('ZERO','0'),('PERIOD','.'),('ZERO','0'),('ZERO','0'),('TWO','2'),('RET','')):
      win.event_simulate(type=event,value='PRESS',unicode=char);win.event_simulate(type=event,value='RELEASE')
     state['phase']='keyboard_edit'
    elif phase=='keyboard_edit':
     target=obj.b4ml.body_targets['Head'].target
     if abs(target.location.y-state['target_before'][1]-.002)>1e-6:return .03
     state['events'].append('Native keyboard target transform passed through live modal')
     state['phase']='stale_edit'
    elif phase=='stale_edit':
     if not obj.b4ml.body_running:return .03
     state['cancelled_before']=live._WATCHERS[obj.as_pointer()]['cancelled'];change(obj);state['phase']='newest_fit'
    elif phase=='newest_fit':
     if not idle(obj):return .03
     assert live._WATCHERS[obj.as_pointer()]['cancelled']>state['cancelled_before']
     state['events'].append('New edit cancelled stale fitting and only newest request completed')
     screenshot=ROOT/f'training/b4artists_ml/cache/live-pose-ui-{TAG}.png'
     bpy.ops.screen.screenshot(filepath=str(screenshot));state['screenshot']=str(screenshot.relative_to(ROOT))
     state['solved']=w.raw_pose(obj)
     bpy.ops.ed.undo_push(message='Live solved preview before edit')
     select(obj.b4ml.body_targets['Head'].target,win)
     assert bpy.ops.transform.translate('EXEC_DEFAULT',True,value=(0.,.002,0.))=={'FINISHED'}
     state['phase']='undo_active_fit'
    elif phase=='undo_active_fit':
     if not obj.b4ml.body_running:return .03
     assert bpy.ops.ed.undo()=={'FINISHED'};state['phase']='undone_active'
    elif phase=='undone_active':
     assert not obj.b4ml.body_live and not obj.b4ml.body_running and not live._WATCHERS and not body._JOBS
     assert bpy.ops.ed.redo()=={'FINISHED'};state['phase']='redone_active'
    elif phase=='redone_active':
     assert not obj.b4ml.body_live and not obj.b4ml.body_running and not live._WATCHERS and not body._JOBS
     state['events'].append('Undo and Redo of an edit made while live restored both snapshots with scheduling off')
     select(obj,win);start(obj);state['phase']='restarted_after_undo'
    elif phase=='restarted_after_undo':
     if not idle(obj):return .03
     state['solved']=w.raw_pose(obj);change(obj);state['phase']='escape_fit'
    elif phase=='escape_fit':
     if not obj.b4ml.body_running:return .03
     win.event_simulate(type='ESC',value='PRESS');state['phase']='escaped'
    elif phase=='escaped':
     if obj.b4ml.body_live:return .03
     assert not obj.b4ml.body_running and not live._WATCHERS and not body._JOBS
     assert w.raw_pose(obj)==state['solved']
     state['events'].append('Escape stopped live fitting and restored last solved preview')
     try:result=bpy.ops.b4ml.body('INVOKE_DEFAULT',True,operation='KEEP')
     except RuntimeError:result={'CANCELLED'}
     assert result=={'CANCELLED'} and len(obj.b4ml.anchors)==0
     state['events'].append('Keep rejected an unsolved target request')
     start(obj);state['phase']='ready_keep'
    elif phase=='ready_keep':
     if not idle(obj):return .03
     assert bpy.ops.b4ml.body_live('INVOKE_DEFAULT')=={'FINISHED'}
     assert not obj.b4ml.body_live
     state['phase']='keep_stopped'
    elif phase=='keep_stopped':
     assert bpy.ops.b4ml.body('INVOKE_DEFAULT',True,operation='KEEP')=={'FINISHED'};source_ok(obj)
     assert len(obj.b4ml.anchors)==1
     state['events'].append('Stop and Keep stored one pose anchor and restored source action and keys')
     state['phase']='undo_ready'
    elif phase=='undo_ready':
     assert bpy.ops.ed.undo()=={'FINISHED'};state['phase']='undo_keep'
    elif phase=='undo_keep':
     assert len(obj.b4ml.anchors)==0 and obj.b4ml.body_payload and not obj.b4ml.body_live
     assert not live._WATCHERS and not body._JOBS
     assert bpy.ops.ed.redo()=={'FINISHED'};state['phase']='redo_keep'
    elif phase=='redo_keep':
     assert len(obj.b4ml.anchors)==1 and not obj.b4ml.body_payload, str(dict(anchors=len(obj.b4ml.anchors),preview=bool(obj.b4ml.body_payload),live=obj.b4ml.body_live,status=obj.b4ml.status));source_ok(obj)
     state['events'].append('Actual Undo and Redo restored preview and kept anchor without resuming live')
     select(obj,win);assert bpy.ops.b4ml.body(operation='BEGIN')=={'FINISHED'}
     change(obj);start(obj);state['phase']='save_fit'
    elif phase=='save_fit':
     if not obj.b4ml.body_running:return .03
     state['path']=str(ROOT/f'training/b4artists_ml/cache/live-pose-ui-{TAG}.blend')
     assert bpy.ops.wm.save_as_mainfile(filepath=state['path'])=={'FINISHED'}
     assert not obj.b4ml.body_live and not obj.b4ml.body_running and not live._WATCHERS and not body._JOBS
     state['saved_pose']=w.raw_pose(obj);state['phase']='reload'
    elif phase=='reload':
     state['phase']='reloaded';assert bpy.ops.wm.open_mainfile(filepath=state['path'])=={'FINISHED'}
    elif phase=='reloaded':
     assert not obj.b4ml.body_live and not obj.b4ml.body_running and not live._WATCHERS and not body._JOBS
     assert w.raw_pose(obj)==state['saved_pose'];select(obj,win)
     state['events'].append('Save during fitting cancelled work; reload retained recoverable preview with live off')
     assert bpy.ops.b4ml.body(operation='CANCEL')=={'FINISHED'};source_ok(obj)
     state['events'].append('Cancel after actual file reload restored original source')
     assert bpy.ops.b4ml.body(operation='BEGIN')=={'FINISHED'};change(obj);start(obj);state['phase']='disable_fit'
    elif phase=='disable_fit':
     if not obj.b4ml.body_running:return .03
     b4artists_ml.unregister();assert not live._WATCHERS and not body._JOBS and not body._LIVE
     assert obj.animation_data.action.name==state['action'];assert helper.keys(obj)==state['keys'];assert w.raw_pose(obj)==state['source'];assert rs.mode_values(obj)==state['modes']
     state['phase']='disabled';state['events'].append('Unregister during fitting restored source and removed live jobs and preview helpers')
    elif phase=='disabled':
     finish(True);return None
  except Exception:
   finish(False,traceback.format_exc());return None
  return .04
 bpy.app.timers.register(tick,first_interval=.5,persistent=True)

if __name__=='__main__':
 if '--host' in sys.argv:run()
 else:
  if REPORT.exists():raise RuntimeError('Evidence already exists')
  startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0;start=time.perf_counter()
  with (ROOT/f'training/b4artists_ml/cache/live-pose-ui-{TAG}.log').open('w') as log:
   p=subprocess.run(['X:/5.1.0/bforartists.exe','--factory-startup','--no-window-focus','--enable-event-simulate','--python',str(HERE),'--','--host'],stdout=log,stderr=subprocess.STDOUT,startupinfo=startup,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4'),timeout=360)
  report=dict(exit_code=p.returncode,seconds=time.perf_counter()-start);(ROOT/f'training/b4artists_ml/results/live-pose-ui-process-{TAG}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
