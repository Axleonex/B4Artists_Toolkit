"""Actual-rig temporal contact correction and isolated candidate recovery."""
from pathlib import Path
import os,sys,json,unittest,math,time,traceback
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]
import bpy
from mathutils import Vector
import b4artists_ml
from b4artists_ml import contacts as c,contact_math as cm,workflow as w,posing as p,rig_state as rs
from test_b4artists_ml_posing import boneforge_rig,rigify_rig
RECORDS=[]
BUILDERS={'boneforge':boneforge_rig,'rigify_basic':rigify_rig,'rigify_default':lambda:rigify_rig(full=True),'metarig_basic':lambda:rigify_rig(generate=False),'metarig_default':lambda:rigify_rig(full=True,generate=False)}


def fixture(label='boneforge',transformed=False):
    bpy.context.window.scene=bpy.data.scenes.new('Contact '+label);scene=bpy.context.scene;ob=BUILDERS[label]()
    if transformed:ob.location=(2,-1,.4);ob.rotation_euler=(.1,.2,.3);ob.scale=(1.7,)*3
    bpy.context.view_layer.objects.active=ob;p._update(ob)
    root=p.bindings(ob)[1];scene.frame_set(1);ob.pose.bones[root].keyframe_insert('location',frame=1);ob.pose.bones[root].keyframe_insert('location',frame=11)
    source=ob.animation_data.action;source_signature=c._action_signature(ob);modes=rs.mode_values(ob)
    w.capture_anchor(ob,scene)
    scene.frame_set(11);p.begin(ob,scene)
    ob.b4ml.pose_offset=ob.matrix_world.to_3x3()@Vector((.025,0,-.15));ob.b4ml.pose_strength=1.
    for item in ob.b4ml.pose_targets:item.enabled=item.name.startswith('leg')
    p.solve(ob,scene);p.finish(ob,scene,True)
    w.preview(ob,scene);scene.frame_set(1)
    for limb in ('leg-L','leg-R'):
        ob.b4ml.contact_limb=limb;item=c.capture(ob,scene);item.start=1.;item.end=11.;item.blend=0.
    scene.frame_set(6)
    return ob,source,source_signature,modes


class ContactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):b4artists_ml.register()

    def test_timing_validation_and_fractional_sampling(self):
        row=dict(limb='leg-L',start=2.,end=4.,blend=2.,strength=.8,point=[0,0,0],offset=[0,0,0],rotation=[1,0,0,0],lock_rotation=True)
        validated=cm.validate([row],0.,6.)
        self.assertEqual(cm.weight(row,2.),.8);self.assertAlmostEqual(cm.weight(row,1.),.4);self.assertEqual(cm.weight(row,0.),0.)
        self.assertIn(2.25,cm.sample_frames(validated,[0.,6.],0.,6.))
        for bad in (dict(row,start=float('nan')),dict(row,end=9.),dict(row,strength=-.1),dict(row,offset=[0,float('inf'),0])):
            with self.assertRaises(ValueError):cm.validate([bad],0.,6.)
        with self.assertRaisesRegex(ValueError,'overlap'):cm.validate([row,row],0.,6.)
        self.assertEqual(len(cm.validate([dict(row,start=1.,end=2.,blend=1.),dict(row,start=4.,end=5.,blend=1.)],0.,6.)),2)

    def test_crouch_contacts_on_five_real_rigs(self):
        for label in BUILDERS:
            with self.subTest(rig=label):
                ob,source,sig,modes=fixture(label,transformed=True);scene=bpy.context.scene;original=ob.b4ml.candidate_action
                report=c.solve(ob,scene);self.assertLess(report['max_after'],2e-4);self.assertGreater(report['max_before'],1e-5)
                self.assertEqual(report['sample_interval_frames'],.25);self.assertLessEqual(report['validation_max_interval_frames'],.125)
                self.assertEqual(report['priority_poses'],2);self.assertEqual(p._frame(scene),6.)
                self.assertIsNot(ob.b4ml.candidate_action,original);self.assertTrue(original.use_fake_user)
                RECORDS.append(dict(fixture=label,**report))
                w.finish_preview(ob,scene,False);self.assertIs(ob.animation_data.action,source);self.assertEqual(c._action_signature(ob),sig);self.assertEqual(rs.mode_values(ob),modes)

    def test_abort_restores_input_candidate_pose_and_playhead(self):
        ob,source,sig,modes=fixture();scene=bpy.context.scene;original=ob.b4ml.candidate_action;before=w.raw_pose(ob);action=c._action_signature(ob)
        c.start(ob,scene);self.assertFalse(c.step(ob));c.abort(ob)
        self.assertIs(ob.b4ml.candidate_action,original);self.assertIs(ob.animation_data.action,original);self.assertEqual(c._action_signature(ob),action);self.assertEqual(w.raw_pose(ob),before);self.assertEqual(p._frame(scene),6.)
        self.assertFalse(ob.b4ml.contact_running)

    def test_conflicting_priority_pose_preserves_source(self):
        ob,source,sig,modes=fixture();scene=bpy.context.scene;original=ob.b4ml.candidate_action;before=w.raw_pose(ob);action=c._action_signature(ob)
        ob.b4ml.contacts[0].point.x+=.2
        with self.assertRaisesRegex(ValueError,'priority pose'):c.solve(ob,scene)
        self.assertIs(ob.b4ml.candidate_action,original);self.assertEqual(w.raw_pose(ob),before);self.assertEqual(c._action_signature(ob),action)

    def test_changed_request_rejected_during_job(self):
        ob,source,sig,modes=fixture();scene=bpy.context.scene;original=ob.b4ml.candidate_action
        c.start(ob,scene);c.step(ob);ob.b4ml.contacts[0].blend=1.
        with self.assertRaisesRegex(ValueError,'changed'):c.step(ob)
        self.assertIs(ob.animation_data.action,original);self.assertFalse(ob.b4ml.contact_running)

    def test_save_cancels_running_job_and_reload_keeps_result(self):
        ob,source,sig,modes=fixture();scene=bpy.context.scene;name=ob.name;original=ob.b4ml.candidate_action
        c.start(ob,scene);c.step(ob)
        path=ROOT/'training/b4artists_ml/cache/contacts-running.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path))
        self.assertFalse(ob.b4ml.contact_running);self.assertIs(ob.animation_data.action,original)
        c.solve(ob,scene);bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path))
        ob=bpy.data.objects[name];scene=bpy.context.scene;bpy.context.view_layer.objects.active=ob
        self.assertEqual(len(ob.b4ml.contacts),2);self.assertIn('b4ml_contact_metrics',ob.b4ml.candidate_action)
        w.finish_preview(ob,scene,True);w.restore_kept_source(ob,scene);self.assertEqual(c._action_signature(ob),sig);self.assertEqual(rs.mode_values(ob),modes)

    def test_offsets_partial_strength_and_unaffected_curves(self):
        ob,source,sig,modes=fixture('rigify_default',transformed=True);scene=bpy.context.scene
        ob.b4ml.contacts.clear();scene.frame_set(5);ob.b4ml.contact_limb='leg-L';ob.b4ml.contact_offset=(.01,.06,-.035)
        item=c.capture(ob,scene);item.start=4.;item.end=7.;item.blend=1.;item.strength=.5;item.lock_rotation=False
        original=ob.b4ml.candidate_action;input_signature=c._action_signature(ob)
        _,_,limbs=p.bindings(ob);left=next(r for r in limbs if r['id']=='leg-L');affected={ob.pose.bones[n].path_from_id(prop) for n in left['fk'] for prop in ('rotation_quaternion','rotation_euler','rotation_axis_angle')}
        outside={}
        for frame in (1.,1.5,2.,2.75,8.25,9.,9.5,10.,11.):
            c._frame(scene,frame);outside[frame]={n:ob.pose.bones[n].matrix.copy() for n in left['fk']}
        report=c.solve(ob,scene);self.assertLess(report['max_after'],2e-4)
        for frame,matrices in outside.items():
            c._frame(scene,frame)
            for n,matrix in matrices.items():
                self.assertLess(max(abs(a-b) for ra,rb in zip(matrix,ob.pose.bones[n].matrix) for a,b in zip(ra,rb)),2e-5)
        output=c._action_signature(ob)
        self.assertEqual([r for r in input_signature if r[0] not in affected],[r for r in output if r[0] not in affected])
        for before in input_signature:
            if before[0] not in affected:continue
            after=next(r for r in output if r[:2]==before[:2])
            # LINEAR keys do not use their automatically recalculated handle coordinates.
            self.assertEqual([(k[0],k[-1]) for k in before[-1] if not 3<=k[0][0]<=8],[(k[0],k[-1]) for k in after[-1] if not 3<=k[0][0]<=8])
        self.assertAlmostEqual(report['contact_drift_after']/report['contact_drift_before'],.5,delta=.001)
        RECORDS.append(dict(fixture='rigify_offset_partial',**report))

    def test_unreachable_mid_interval_rolls_back(self):
        ob,source,sig,modes=fixture();scene=bpy.context.scene;original=ob.b4ml.candidate_action;before=w.raw_pose(ob)
        for item in ob.b4ml.contacts:item.start=4.;item.end=8.;item.blend=0.;item.point.x+=20.
        with self.assertRaisesRegex(ValueError,'unreachable'):c.solve(ob,scene)
        self.assertIs(ob.animation_data.action,original);self.assertEqual(w.raw_pose(ob),before)

    def test_cancel_during_final_validation_removes_only_temporary_action(self):
        ob,source,sig,modes=fixture();scene=bpy.context.scene;original=ob.b4ml.candidate_action;actions=set(bpy.data.actions.keys());before=w.raw_pose(ob)
        c.start(ob,scene)
        while not ob.b4ml.contact_progress.startswith('Checking'):self.assertFalse(c.step(ob))
        self.assertIsNot(ob.animation_data.action,original)
        with self.assertRaisesRegex(ValueError,'contact correction'):w.finish_preview(ob,scene,True)
        c.abort(ob);self.assertIs(ob.animation_data.action,original);self.assertEqual(set(bpy.data.actions.keys()),actions);self.assertEqual(w.raw_pose(ob),before)

    def test_input_action_changes_reject_copy_commit(self):
        ob,source,sig,modes=fixture();scene=bpy.context.scene;original=ob.b4ml.candidate_action
        c.start(ob,scene);c.step(ob)
        fc=next(iter(w.action_curves(original,getattr(ob.animation_data,'action_slot',None))))
        fc.keyframe_points[0].co.y+=.01;fc.update();changed=c._action_signature(ob)
        with self.assertRaisesRegex(ValueError,'Input action changed'):
            while not c.step(ob):pass
        self.assertIs(ob.animation_data.action,original);self.assertEqual(c._action_signature(ob),changed)

    def test_hand_contact_offset_and_orientation(self):
        for label in ('boneforge','rigify_default'):
            ob,source,sig,modes=fixture(label,transformed=True);scene=bpy.context.scene;ob.b4ml.contacts.clear();scene.frame_set(6)
            ob.b4ml.contact_limb='arm-R';ob.b4ml.contact_offset=(.015,.02,-.01);item=c.capture(ob,scene)
            _,_,limbs=p.bindings(ob);row=next(r for r in limbs if r['id']=='arm-R')
            elbow=ob.matrix_world@ob.pose.bones[row['joints'][1]].head
            item.point=Vector(item.point).lerp(elbow,.15);item.start=4.;item.end=8.;item.blend=1.
            from mathutils import Quaternion
            item.rotation=Quaternion((0,0,1),.15)@Quaternion(item.rotation)
            report=c.solve(ob,scene);self.assertLess(report['max_after'],2e-4)
            RECORDS.append(dict(fixture=label+'_hand_orientation',**report))

    def test_contact_drift_between_sampled_keys(self):
        ob,source,sig,modes=fixture();scene=bpy.context.scene;c.solve(ob,scene)
        _,_,limbs=p.bindings(ob);mapping={r['id']:r for r in limbs};maximum=0.
        for step in range(8,88):
            frame=(step+.5)/8;c._frame(scene,frame)
            for item in ob.b4ml.contacts:
                row=mapping[item.limb];reference=sum((ob.pose.bones[row['joints'][i+1]].head-ob.pose.bones[row['joints'][i]].head).length for i in (0,1))
                maximum=max(maximum,(c._point(ob,row,item.offset)-Vector(item.point)).length/reference)
        RECORDS.append(dict(fixture='between_samples',maximum_drift=maximum))
        self.assertLess(maximum,2e-4)

    def test_repeated_partial_strength_regenerates_from_retained_input(self):
        ob,source,sig,modes=fixture();scene=bpy.context.scene
        for item in ob.b4ml.contacts:item.strength=.5
        base=ob.b4ml.candidate_action;c.solve(ob,scene);first=c._action_signature(ob)
        self.assertIs(ob.b4ml.contact_input,base)
        c.solve(ob,scene);self.assertEqual(c._action_signature(ob),first)
        before=ob.b4ml.candidate_action
        c.start(ob,scene);c.step(ob);c.abort(ob);self.assertIs(ob.animation_data.action,before)
        path=ROOT/'training/b4artists_ml/cache/contacts-repeat.blend';name=ob.name
        bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path));ob=bpy.data.objects[name];bpy.context.view_layer.objects.active=ob
        c.solve(ob,bpy.context.scene);self.assertEqual(c._action_signature(ob),first)


    def test_restore_before_contacts_and_missing_retained_input(self):
        ob,source,sig,modes=fixture();scene=bpy.context.scene;base=ob.b4ml.candidate_action;before=c._action_signature(ob)
        c.solve(ob,scene);self.assertEqual(bpy.ops.b4ml.contact(operation='RESET'),{'FINISHED'})
        self.assertIs(ob.b4ml.candidate_action,base);self.assertEqual(c._action_signature(ob),before);self.assertIsNone(ob.b4ml.contact_input)
        c.solve(ob,scene);previous=ob.b4ml.candidate_action;bpy.data.actions.remove(base)
        with self.assertRaisesRegex(ValueError,'Retained contact input is missing'):c.solve(ob,scene)
        self.assertIs(ob.animation_data.action,previous)


def run_ui_smoke():
    ContactTests.setUpClass();ob,source,sig,modes=fixture('rigify_default')
    state=dict(name=ob.name,source_name=source.name,source_signature=sig,modes=modes,phase='dismiss',started=time.monotonic(),events=[])
    version='.'.join(map(str,b4artists_ml.bl_info['version']));steps=[];old_step=c.step
    def timed_step(obj):
        started=time.perf_counter()
        try:return old_step(obj)
        finally:steps.append((time.perf_counter()-started)*1000)
    c.step=timed_step
    def tick():
        try:
            if time.monotonic()-state['started']>90:raise AssertionError('Contact UI workflow timed out')
            win=bpy.context.window_manager.windows[0];area=next(a for a in win.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW')
            area.spaces.active.show_region_ui=True
            for r in area.regions:
                if r.type=='UI' and hasattr(r,'active_panel_category'):r.active_panel_category='B4Artists ML'
            ob=bpy.data.objects[state['name']];win.view_layer.objects.active=ob;ob.select_set(True)
            with bpy.context.temp_override(window=win,area=area,region=region):
                if state['phase']=='dismiss':
                    win.event_simulate(type='ESC',value='PRESS');bpy.ops.view3d.view_axis(type='FRONT');bpy.ops.view3d.view_selected(use_all_regions=False);state['phase']='begin'
                elif state['phase']=='begin':
                    ob.b4ml.contacts.clear();bpy.context.scene.frame_set(1)
                    for limb in ('leg-L','leg-R'):
                        ob.b4ml.contact_limb=limb;assert bpy.ops.b4ml.contact(operation='CAPTURE')=={'FINISHED'}
                        item=ob.b4ml.contacts[-1];item.start=1.;item.end=11.;item.blend=0.
                    ob.b4ml.show_contacts=True;ob.b4ml.contact_index=0;bpy.context.scene.frame_set(6)
                    state['input_name']=ob.b4ml.candidate_action.name;state['input_signature']=c._action_signature(ob)
                    bpy.ops.ed.undo_push(message='Contact inputs ready')
                    assert bpy.ops.b4ml.contact_solve('INVOKE_DEFAULT')=={'RUNNING_MODAL'};state['phase']='completed';state['events'].append('Contact capture and modal correction invoked')
                elif state['phase']=='completed':
                    if ob.b4ml.contact_running:return .03
                    assert ob.b4ml.contact_output==ob.b4ml.candidate_action
                    metrics=json.loads(ob.b4ml.contact_metrics);assert metrics['max_after']<2e-4
                    state['metrics']=metrics;state['step_ms']=list(steps);state['result_name']=ob.b4ml.candidate_action.name
                    state['result_signature']=c._action_signature(ob);state['events'].append('Evaluated correction completed')
                    path=ROOT/f'training/b4artists_ml/cache/contacts-ui-v{version}.png';bpy.ops.screen.screenshot(filepath=str(path));state['screenshot']=str(path.relative_to(ROOT))
                    assert bpy.ops.b4ml.contact_solve('INVOKE_DEFAULT')=={'RUNNING_MODAL'};state['phase']='escape'
                elif state['phase']=='escape':
                    if not ob.b4ml.contact_progress.startswith('Fitting'):return .02
                    win.event_simulate(type='ESC',value='PRESS');state['phase']='cancelled'
                elif state['phase']=='cancelled':
                    if ob.b4ml.contact_running:return .02
                    assert ob.b4ml.candidate_action.name==state['result_name'];assert c._action_signature(ob)==state['result_signature']
                    state['events'].append('Escape restored previous candidate');assert bpy.ops.ed.undo()=={'FINISHED'};state['phase']='redo'
                elif state['phase']=='redo':
                    assert ob.b4ml.candidate_action.name==state['input_name'];assert c._action_signature(ob)==state['input_signature']
                    assert bpy.ops.ed.redo()=={'FINISHED'};state['phase']='keep'
                elif state['phase']=='keep':
                    assert ob.b4ml.candidate_action.name==state['result_name'];assert c._action_signature(ob)==state['result_signature']
                    assert bpy.ops.b4ml.action(operation='KEEP')=={'FINISHED'};assert bpy.ops.b4ml.action(operation='RESTORE_SOURCE')=={'FINISHED'}
                    assert ob.animation_data.action.name==state['source_name'];assert c._action_signature(ob)==state['source_signature'];assert rs.mode_values(ob)==state['modes']
                    state['events'].append('Undo, redo, Keep and Restore Source passed')
                    import numpy as np
                    report=dict(passed=True,fixture='rigify_default',package=b4artists_ml.__file__,events=state['events'],metrics=state['metrics'],elapsed_seconds=time.monotonic()-state['started'],screenshot=state['screenshot'],step_count=len(state['step_ms']),step_p95_ms=float(np.percentile(state['step_ms'],95)),step_max_ms=max(state['step_ms']))
                    (ROOT/f'docs/b4artists_ml/contacts-ui-v{version}.json').write_text(json.dumps(report,indent=2)+'\n');print('CONTACT_UI_RESULT: '+json.dumps(report),flush=True);bpy.ops.wm.quit_blender();return None
        except Exception as exc:
            report=dict(passed=False,phase=state['phase'],error=str(exc),traceback=traceback.format_exc(),events=state['events'])
            (ROOT/f'docs/b4artists_ml/contacts-ui-v{version}.json').write_text(json.dumps(report,indent=2)+'\n');print('CONTACT_UI_RESULT: '+json.dumps(report),flush=True);bpy.ops.wm.quit_blender();return None
        return .03
    bpy.app.timers.register(tick,first_interval=.5)


if __name__=='__main__' and '--ui-smoke' in sys.argv:run_ui_smoke()
elif __name__=='__main__':
    selection=os.environ.get('B4ML_CONTACT_TEST')
    suite=unittest.defaultTestLoader.loadTestsFromName(selection,sys.modules[__name__]) if selection else unittest.defaultTestLoader.loadTestsFromTestCase(ContactTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report=dict(tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),errors=len(result.errors),skips=len(result.skipped),records=RECORDS,package=b4artists_ml.__file__)
    (ROOT/'training/b4artists_ml/results'/os.environ.get('B4ML_CONTACT_RESULT','contacts-v1.json')).write_text(json.dumps(report,indent=2)+'\n')
    print('CONTACT_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
