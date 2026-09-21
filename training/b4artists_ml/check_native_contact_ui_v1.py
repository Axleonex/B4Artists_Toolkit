"""Real-window native operator lifecycle; no independent usability score implied."""
from pathlib import Path
import sys,os,json,time,traceback,subprocess
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve();TAG=os.environ.get('B4ML_NATIVE_UI_TAG','native-contact-v1')

def run():
 import bpy,numpy as np
 from mathutils import Vector
 sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]
 import b4artists_ml
 from b4artists_ml import workflow as w,flight as f,motion_layer as m,posing as p,support,contacts
 from test_b4artists_ml_flight import fixture,FlightTests
 from test_b4artists_ml_momentum import MomentumHostTests
 FlightTests.setUpClass();ob,source,sig,modes=MomentumHostTests().fixture('rigify_default');scene=bpy.context.scene
 ob.b4ml.flights[0].takeoff_blend=ob.b4ml.flights[0].landing_blend=2
 scene.frame_set(1);item=contacts.capture(ob,scene);item.start=1;item.end=2;item.blend=0
 scene.frame_set(6)

 # Disposable bone-bound surface so the displayed instance has visible geometry.
 verts=[];faces=[];groups=[]
 for bone in ob.data.bones:
  if not bone.use_deform:continue
  first=len(verts);width=max(bone.length*.12,.003)
  for z in (0,bone.length):
   for x,y in ((-width,-width),(width,-width),(width,width),(-width,width)):verts.append(bone.matrix_local@Vector((x,z,y)))
  faces.extend(tuple(first+i for i in face) for face in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)));groups.append((bone.name,list(range(first,first+8))))
 data=bpy.data.meshes.new('Native UI bound surface');data.from_pydata(verts,[],faces);mesh=bpy.data.objects.new('Native UI character',data);scene.collection.objects.link(mesh)
 for name,indices in groups:mesh.vertex_groups.new(name=name).add(indices,1.,'REPLACE')
 mesh.modifiers.new('Armature','ARMATURE').object=ob
 state=dict(name=ob.name,source=source.name,phase='dismiss',started=time.monotonic(),events=[]);steps=[];original=f.step
 def timed(obj):
  start=time.perf_counter()
  try:return original(obj)
  finally:steps.append((time.perf_counter()-start)*1000)
 f.step=timed
 def tick():
  try:
   if time.monotonic()-state['started']>300:raise AssertionError('UI workflow timeout')
   win=bpy.context.window_manager.windows[0];area=next(a for a in win.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW');area.spaces.active.show_region_ui=True
   for r in area.regions:
    if r.type=='UI' and hasattr(r,'active_panel_category'):r.active_panel_category='B4Artists ML'
   ob=bpy.data.objects[state['name']];visible=m.find(ob) or ob;win.view_layer.objects.active=visible;visible.select_set(True)
   with bpy.context.temp_override(window=win,area=area,region=region):
    phase=state['phase']
    if phase=='dismiss':
     win.event_simulate(type='ESC',value='PRESS');bpy.ops.view3d.view_axis(type='FRONT');bpy.ops.view3d.view_selected(use_all_regions=False);state['phase']='start_cancel'
    elif phase=='start_cancel':
     ob.b4ml.show_flights=True;bpy.ops.ed.undo_push(message='Native flight inputs ready');assert bpy.ops.b4ml.flight_solve('INVOKE_DEFAULT')=={'RUNNING_MODAL'};state['phase']='escape'
    elif phase=='escape':
     if not ob.b4ml.flight_progress.startswith('Fitting'):return .02
     win.event_simulate(type='ESC',value='PRESS');state['phase']='cancelled'
    elif phase=='cancelled':
     if ob.b4ml.flight_running:return .02
     assert m.find(ob) is None and ob.b4ml.candidate_action==ob.animation_data.action
     state['events'].append('Escape cancelled native generation and restored its input')
     assert bpy.ops.b4ml.flight_solve('INVOKE_DEFAULT')=={'RUNNING_MODAL'};state['phase']='completed'
    elif phase=='completed':
     if ob.b4ml.flight_running:return .03
     instance=m.validate(ob);assert w.active_rig(bpy.context)==ob
     state['metrics']=json.loads(ob.b4ml.flight_metrics);assert len(state['metrics']['transitions'])==2;assert all(r['normalized_jump']<=.02 for r in state['metrics']['transitions']);state['events'].append('Native modal flight and both velocity transitions completed with visible character selection')
     state['instance']=instance.name
     screenshot=ROOT/f'training/b4artists_ml/cache/native-ui-{TAG}.png';bpy.ops.screen.screenshot(filepath=str(screenshot));state['screenshot']=str(screenshot.relative_to(ROOT))
     assert bpy.ops.ed.undo()=={'FINISHED'};state['phase']='undo'
    elif phase=='undo':
     assert m.find(ob) is None;assert ob.b4ml.candidate_action==ob.animation_data.action
     assert bpy.ops.ed.redo()=={'FINISHED'};state['phase']='redo'
    elif phase=='redo':
     m.validate(ob);state['events'].append('Undo and Redo restored collection ownership and native drivers')
     assert bpy.ops.b4ml.contact_solve('INVOKE_DEFAULT')=={'RUNNING_MODAL'};state['phase']='contacts_completed'
    elif phase=='contacts_completed':
     if ob.b4ml.contact_running:return .03
     assert ob.b4ml.contact_output==ob.b4ml.candidate_action;state['contact_metrics']=json.loads(ob.b4ml.contact_metrics);assert state['contact_metrics']['max_after']<2e-4
     assert bpy.ops.ed.undo()=={'FINISHED'};state['phase']='contacts_undo'
    elif phase=='contacts_undo':
     m.validate(ob);assert ob.b4ml.contact_output is None
     assert bpy.ops.ed.redo()=={'FINISHED'};state['phase']='contacts_redo'
    elif phase=='contacts_redo':
     m.validate(ob);assert ob.b4ml.contact_output==ob.b4ml.candidate_action
     state['events'].append('Contacts applied after native transitions; Undo/Redo preserved the native layer and contact candidate')
     assert bpy.ops.b4ml.action(operation='KEEP')=={'FINISHED'};assert bpy.ops.b4ml.action(operation='RESTORE_SOURCE')=={'FINISHED'}
     assert ob.animation_data.action.name==state['source'];state['result']=m.results(ob)[-1].name
     state['events'].append('Keep and Restore Source archived the complete editable result')
     state['active_after_source_restore']=win.view_layer.objects.active.name if win.view_layer.objects.active else None
     state['phase']='reopen'
    elif phase=='reopen':
     assert bpy.ops.b4ml.motion_result(result_name=state['result'])=={'FINISHED'};state['phase']='restored'
    elif phase=='restored':
     instance=m.validate(ob);assert instance.animation_data.drivers[0].driver.variables[0].targets[0].id==instance
     assert bpy.ops.b4ml.action(operation='DISCARD')=={'FINISHED'};assert ob.animation_data.action.name==state['source'];assert m.find(ob) is None
     state['events'].append('Saved result operator reopened an independent preview; Discard restored the source')
     import hashlib
     runtime_sha256={'b4artists_ml/'+p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(b4artists_ml.__file__).parent.glob('*.py')}
     report=dict(contact_metrics=state['contact_metrics'],runtime_sha256=runtime_sha256,passed=True,events=state['events'],metrics=state['metrics'],screenshot=state['screenshot'],step_count=len(steps),step_p95_ms=float(np.percentile(steps,95)),step_max_ms=max(steps),elapsed_seconds=time.monotonic()-state['started'],active_after_source_restore=state.get('active_after_source_restore'),scope='Automated real-window operators and events; independent animator usability and visual motion assessment remain unverified.')
     (ROOT/f'docs/b4artists_ml/native-ui-{TAG}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True);bpy.ops.wm.quit_blender();return None
  except Exception:
   report=dict(passed=False,phase=state['phase'],events=state['events'],error=traceback.format_exc());(ROOT/f'docs/b4artists_ml/native-ui-{TAG}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True);bpy.ops.wm.quit_blender();return None
  return .03
 bpy.app.timers.register(tick,first_interval=.5)

if __name__=='__main__':
 if '--host' in sys.argv:run()
 else:
  startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
  start=time.perf_counter()
  with (ROOT/f'training/b4artists_ml/cache/native-ui-{TAG}.log').open('w') as log:
   p=subprocess.run(['X:/5.1.0/bforartists.exe','--factory-startup','--no-window-focus','--enable-event-simulate','--python',str(HERE),'--','--host'],stdout=log,stderr=subprocess.STDOUT,startupinfo=startup,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4'),timeout=360)
  report=dict(exit_code=p.returncode,seconds=time.perf_counter()-start);(ROOT/f'training/b4artists_ml/results/native-ui-process-{TAG}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
