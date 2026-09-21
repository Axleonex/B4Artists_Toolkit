"""Real-rig gravity correction, original pose preservation and recovery."""
from pathlib import Path
import os,sys,json,time,unittest,traceback
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]
import numpy as np
import bpy
import b4artists_ml
from b4artists_ml import flight as f,workflow as w,posing as p,contacts as c,support,rig_state as rs
from test_b4artists_ml_contacts import fixture as contact_fixture,BUILDERS
RECORDS=[]

def fixture(label='boneforge',transformed=False):
    ob,source,sig,modes=contact_fixture(label,transformed)
    ob.b4ml.contacts.clear();support.initialize(ob);f.add(ob,bpy.context.scene)
    return ob,source,sig,modes

def com(ob,frame):
    c._frame(bpy.context.scene,frame);p._update(ob)
    _,_,a,b=support.sample(ob,bpy.context.evaluated_depsgraph_get())
    return f.center_of_mass(a,b,[i.weight for i in ob.b4ml.mass_segments],[i.fraction for i in ob.b4ml.mass_segments])[0]

class FlightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):b4artists_ml.register()
    def test_fractional_lookup_and_legacy_curve_equivalence(self):
        import zipfile
        ob,source,sig,modes=fixture();scene=bpy.context.scene
        w.finish_preview(ob,scene,False)
        for item in ob.b4ml.anchors:item.frame+=.2
        w.preview(ob,scene);ob.b4ml.flights.clear();scene.frame_set(1);f.add(ob,scene)
        original=ob.b4ml.candidate_action
        curve=next(iter(w.action_curves(original,getattr(ob.animation_data,'action_slot',None))))
        keys={float(k.co.x):k for k in curve.keyframe_points};times=sorted(keys)
        for frame in times+[v+1e-7 for v in times]:
            expected=min(keys.values(),key=lambda k:abs(float(k.co.x)-frame))
            self.assertEqual(f._key_at(keys,times,frame),expected)
        with self.assertRaisesRegex(ValueError,'frame precision'):f._key_at(keys,times,10000.)
        # Execute the archived released implementation on exactly the same fixture.
        # Only its relative dependencies use current (unchanged) workflow/rig modules.
        legacy={'__name__':'b4artists_ml._legacy_flight','__package__':'b4artists_ml'}
        with zipfile.ZipFile(ROOT/'releases/b4artists_ml_v0.13.0.zip') as archive:
            code=archive.read('b4artists_ml/flight.py').decode('utf-8')
        exec(compile(code,'archived-v0.13.0/flight.py','exec'),legacy)
        legacy['solve'](ob,scene);expected=f._curve_signature(ob);legacy['restore'](ob,scene)
        f.solve(ob,scene);self.assertEqual(f._curve_signature(ob),expected)
        w.finish_preview(ob,scene,False);self.assertEqual(c._action_signature(ob),sig)

    def test_replaced_results_cleanup_and_retention(self):
        for retention in ('none','fake_user','shared','edited','renamed','legacy'):
            with self.subTest(retention=retention):
                ob,source,sig,modes=fixture();scene=bpy.context.scene;original=ob.b4ml.candidate_action
                f.solve(ob,scene);previous=ob.b4ml.candidate_action
                if retention=='fake_user':previous.use_fake_user=True
                elif retention=='shared':
                    other=bpy.data.objects.new('Shared flight consumer',ob.data);scene.collection.objects.link(other)
                    w.assign_action(other,previous,w._slot(ob.animation_data))
                elif retention=='edited':
                    fc=next(iter(w.action_curves(previous,getattr(ob.animation_data,'action_slot',None))))
                    fc.keyframe_points[0].co.y+=.001;fc.update()
                elif retention=='renamed':previous.name='Authored flight alternative'
                elif retention=='legacy':del previous['b4ml_flight_token']
                name=previous.name;token=f._curve_token(ob,previous)
                f.solve(ob,scene);self.assertIs(ob.b4ml.flight_input,original)
                if retention=='none':self.assertNotIn(name,bpy.data.actions)
                else:
                    self.assertIn(name,bpy.data.actions);self.assertEqual(f._curve_token(ob,previous),token)
                    self.assertGreater(previous.users,0)
                current=ob.b4ml.candidate_action;name=current.name
                f.solve(ob,scene);self.assertNotIn(name,bpy.data.actions)
                w.finish_preview(ob,scene,False);self.assertIs(ob.animation_data.action,source);self.assertEqual(c._action_signature(ob),sig)

    def test_bulk_fingerprint_detects_curve_semantics(self):
        ob,*_=fixture();action=ob.b4ml.candidate_action
        fc=next(iter(w.action_curves(action,getattr(ob.animation_data,'action_slot',None))));key=fc.keyframe_points[0]
        for prop,value in (('interpolation','ELASTIC'),('easing','EASE_OUT'),('amplitude',1.7),('back',2.3),('period',.7),('handle_left_type','FREE'),('type','BREAKDOWN')):
            old=f._curve_token(ob);setattr(key,prop,value);self.assertNotEqual(f._curve_token(ob),old,prop)
        for prop in ('co','handle_left','handle_right'):
            old=f._curve_token(ob);getattr(key,prop).y+=.001;self.assertNotEqual(f._curve_token(ob),old,prop)
        old=f._curve_token(ob);modifier=fc.modifiers.new('NOISE');self.assertNotEqual(f._curve_token(ob),old)
        old=f._curve_token(ob);modifier.phase+=.4;self.assertNotEqual(f._curve_token(ob),old)

    def test_refinement_boundary_rejects_frame_and_world_changes(self):
        from unittest.mock import patch
        for edit in ('frame','world'):
            ob,*_=fixture();scene=bpy.context.scene;original=ob.b4ml.candidate_action
            def refine(*args):
                if False:yield None
                raise f._RefineFlight('Injected pass failure')
            with patch.object(f,'_correction_steps',refine):
                f.start(ob,scene);self.assertFalse(f.step(ob))
                if edit=='frame':scene.frame_set(7)
                else:ob.location.x+=.1;p._update(ob)
                with self.assertRaisesRegex(ValueError,'during refinement'):f.step(ob)
            self.assertFalse(ob.b4ml.flight_running);self.assertIs(ob.animation_data.action,original)
            if edit=='frame':self.assertEqual(p._frame(scene),7.)
            else:self.assertAlmostEqual(ob.location.x,.1)

    def test_long_rigify_rejection_recovers_source(self):
        ob,source,sig,modes=fixture('rigify_default');scene=bpy.context.scene
        w.finish_preview(ob,scene,False);max(ob.b4ml.anchors,key=lambda a:a.frame).frame=61
        w.preview(ob,scene);ob.b4ml.flights.clear();scene.frame_set(1);f.add(ob,scene);scene.frame_set(31)
        original=ob.b4ml.candidate_action;pose=w.raw_pose(ob);signature=f._curve_token(ob);actions=set(bpy.data.actions.keys())
        with self.assertRaisesRegex(ValueError,'Master-root translation failed'):f.solve(ob,scene)
        self.assertFalse(ob.b4ml.flight_running);self.assertIs(ob.animation_data.action,original)
        self.assertEqual(w.raw_pose(ob),pose);self.assertEqual(f._curve_token(ob),signature);self.assertEqual(set(bpy.data.actions.keys()),actions)
        w.finish_preview(ob,scene,False);self.assertIs(ob.animation_data.action,source);self.assertEqual(c._action_signature(ob),sig);self.assertEqual(rs.mode_values(ob),modes)

    def test_five_real_rigs(self):
        for label in os.environ.get('B4ML_FLIGHT_RIGS',','.join(BUILDERS)).split(','):
            with self.subTest(rig=label):
                ob,source,sig,modes=fixture(label,True);scene=bpy.context.scene;original=ob.b4ml.candidate_action
                steps=[];f.start(ob,scene)
                while True:
                    before=time.perf_counter();done=f.step(ob);steps.append((time.perf_counter()-before)*1000)
                    if done:break
                report=json.loads(ob.b4ml.flight_metrics);self.assertLess(report['max_after'],2e-4);self.assertGreater(report['max_before'],.01)
                self.assertEqual(p._frame(scene),6.);self.assertIs(ob.b4ml.flight_input,original)
                # Independent dense COM acceleration check, away from interval boundaries.
                frames=np.arange(2.,10.,.25);positions=np.array([com(ob,float(t)) for t in frames]);dt=.25*scene.render.fps_base/scene.render.fps
                acceleration=np.diff(positions,n=2,axis=0)/dt**2
                error=np.linalg.norm(acceleration-np.array(scene.gravity),axis=1)
                self.assertIn('takeoff_velocity',report['intervals'][0])
                report.update(fixture=label,acceleration_sample_frames=.25,acceleration_error_p95=float(np.percentile(error,95)),acceleration_error_max=float(max(error)),step_p95_ms=float(np.percentile(steps,95)),step_max_ms=max(steps))
                RECORDS.append(report)
                self.assertLess(np.percentile(error,95),.1)
                w.finish_preview(ob,scene,False);self.assertIs(ob.animation_data.action,source);self.assertEqual(c._action_signature(ob),sig);self.assertEqual(rs.mode_values(ob),modes)
                self.assertIsNone(ob.b4ml.flight_input);self.assertIsNone(ob.b4ml.flight_output)
    def test_adaptive_refinement_on_fast_torso_motion(self):
        from mathutils import Quaternion
        ob,*_=fixture();scene=bpy.context.scene;chest=ob.pose.bones['chest']
        for frame,angle in ((3.,0.),(4.,2.6),(5.,-1.8),(6.,2.4),(7.,0.)):
            chest.rotation_quaternion=Quaternion((1,0,0),angle);chest.keyframe_insert('rotation_quaternion',frame=frame)
        for fc in w.action_curves(ob.animation_data.action,getattr(ob.animation_data,'action_slot',None)):
            if fc.data_path==chest.path_from_id('rotation_quaternion'):
                for k in fc.keyframe_points:k.interpolation='LINEAR'
        scene.frame_set(6);p._update(ob);report=f.solve(ob,scene)
        self.assertGreater(report['sample_divisions'],2);self.assertLess(report['max_after'],2e-4)
        RECORDS.append(dict(fixture='fast_torso_adaptive',**report))

    def test_bound_mesh_and_unaffected_curves(self):
        from mathutils import Vector
        ob,source,sig,modes=fixture('rigify_default',True);scene=bpy.context.scene;original=ob.b4ml.candidate_action;slot=w._slot(ob.animation_data)
        names=['DEF-hand.L','DEF-foot.R','DEF-lid.B.L','DEF-spine.003'];verts=[]
        for name in names:
            point=ob.data.bones[name].head_local
            verts.extend([point,point+Vector((.01,0,0)),point+Vector((0,.01,0))])
        data=bpy.data.meshes.new('Flight mesh');data.from_pydata(verts,[],[tuple(range(i,i+3)) for i in range(0,len(verts),3)])
        mesh=bpy.data.objects.new('Flight mesh',data);scene.collection.objects.link(mesh);mesh.matrix_world=ob.matrix_world
        for i,name in enumerate(names):mesh.vertex_groups.new(name=name).add(list(range(i*3,i*3+3)),1.,'REPLACE')
        mesh.modifiers.new('Armature','ARMATURE').object=ob
        before=f._curve_signature(ob);report=f.solve(ob,scene);candidate=ob.b4ml.candidate_action
        root_path=ob.pose.bones[report['root']].path_from_id('location')
        self.assertEqual([r for r in before if r[0]!=root_path],[r for r in f._curve_signature(ob) if r[0]!=root_path])
        for frame in (1.,2.217,5.713,8.427,11.):
            w.assign_action(ob,original,slot);a=com(ob,frame);evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());points=np.array([evaluated.matrix_world@v.co for v in evaluated.data.vertices])
            w.assign_action(ob,candidate,slot);b=com(ob,frame);evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());actual=np.array([evaluated.matrix_world@v.co for v in evaluated.data.vertices])
            np.testing.assert_allclose(actual,points+(b-a),atol=1e-5)
    def test_changed_curve_modifier_rejects_candidate(self):
        ob,*_=fixture();scene=bpy.context.scene;original=ob.b4ml.candidate_action
        path=ob.pose.bones['chest'].path_from_id('rotation_quaternion')
        fc=w.action_curves(original,getattr(ob.animation_data,'action_slot',None)).find(path,index=0)
        modifier=fc.modifiers.new('NOISE');modifier.strength=0.
        f.start(ob,scene);f.step(ob);modifier.phase+=1.;changed=f._curve_signature(ob)
        with self.assertRaisesRegex(ValueError,'Input animation changed'):
            while not f.step(ob):pass
        self.assertIs(ob.animation_data.action,original);self.assertEqual(f._curve_signature(ob),changed)

    def test_gravity_frame_rate_and_display_units(self):
        ob,*_=fixture();scene=bpy.context.scene;scene.render.fps=30;scene.render.fps_base=1.001;scene.unit_settings.scale_length=.01;scene.gravity=(2.,-3.,-4.)
        start=com(ob,1.);end=com(ob,11.);report=f.solve(ob,scene);duration=10*scene.render.fps_base/scene.render.fps
        expected=(start+end)/2-np.array(scene.gravity)*duration**2/8
        np.testing.assert_allclose(com(ob,6.),expected,atol=2e-6);self.assertAlmostEqual(report['intervals'][0]['duration_seconds'],duration)
        scene.use_gravity=False;f.solve(ob,scene);np.testing.assert_allclose(com(ob,6.),(start+end)/2,atol=2e-6)
    def test_priority_conflict_and_contact_composition(self):
        ob,*_=fixture();scene=bpy.context.scene
        w.finish_preview(ob,scene,False);scene.frame_set(3);w.capture_anchor(ob,scene);scene.frame_set(8);w.capture_anchor(ob,scene);w.preview(ob,scene)
        ob.b4ml.flights[0].start=1.;ob.b4ml.flights[0].end=11.;original=ob.b4ml.candidate_action
        with self.assertRaisesRegex(ValueError,'priority pose'):f.solve(ob,scene)
        self.assertIs(ob.animation_data.action,original)
        ob.b4ml.flights[0].start=3.;ob.b4ml.flights[0].end=8.;f.solve(ob,scene);flight_output=ob.b4ml.candidate_action
        baseline={frame:com(ob,frame) for frame in (3.,4.37,6.21,8.)}
        scene.frame_set(1);item=c.capture(ob,scene);item.start=1.;item.end=1.;item.blend=1.;c.solve(ob,scene)
        for frame,point in baseline.items():np.testing.assert_allclose(com(ob,frame),point,atol=2e-6)
        with self.assertRaisesRegex(ValueError,'Restore Before Contacts'):f.solve(ob,scene)
        c.restore_before_contacts(ob,scene);self.assertIs(ob.animation_data.action,flight_output)
        item.end=5.
        with self.assertRaisesRegex(ValueError,'overlap'):c.solve(ob,scene)
        f.restore(ob,scene);self.assertIs(ob.animation_data.action,original)
    def test_cancel_after_copy_and_stale_input(self):
        ob,*_=fixture();scene=bpy.context.scene;original=ob.b4ml.candidate_action;actions=set(bpy.data.actions.keys());pose=w.raw_pose(ob)
        f.start(ob,scene)
        while not ob.b4ml.flight_progress.startswith('Checking'):self.assertFalse(f.step(ob))
        f.abort(ob);self.assertEqual(set(bpy.data.actions.keys()),actions);self.assertEqual(w.raw_pose(ob),pose)
        f.start(ob,scene);f.step(ob)
        fc=next(iter(w.action_curves(original,getattr(ob.animation_data,'action_slot',None))));fc.keyframe_points[0].co.y+=.01;fc.update();changed=f._curve_signature(ob)
        with self.assertRaisesRegex(ValueError,'Input animation changed'):
            while not f.step(ob):pass
        self.assertIs(ob.animation_data.action,original);self.assertEqual(f._curve_signature(ob),changed)
    def test_outside_curves_and_adjacent_intervals(self):
        ob,*_=fixture();scene=bpy.context.scene
        w.finish_preview(ob,scene,False)
        for frame in (3,6,8):scene.frame_set(frame);w.capture_anchor(ob,scene)
        w.preview(ob,scene);original=ob.b4ml.candidate_action
        ob.b4ml.flights[0].start=3.;ob.b4ml.flights[0].end=6.;row=ob.b4ml.flights.add();row.start=6.;row.end=8.
        curves=w.action_curves(original,getattr(ob.animation_data,'action_slot',None));root_path=ob.pose.bones['root'].path_from_id('location')
        # Exercise automatic handles at boundaries and neighboring original keys.
        for fc in curves:
            if fc.data_path==root_path:
                for k in fc.keyframe_points:
                    if fc.array_index==0:k.co.y=.03*np.sin(float(k.co.x)*.7)
                    k.interpolation='BEZIER';k.handle_left_type=k.handle_right_type='AUTO_CLAMPED'
                fc.update()
        frames=(.75,1.,1.3,2.37,2.99,3.,6.,8.,8.01,8.23,9.63,11.,11.25);baseline={t:com(ob,t) for t in frames}
        f.solve(ob,scene)
        for frame,point in baseline.items():np.testing.assert_allclose(com(ob,frame),point,atol=2e-6)
        self.assertEqual(len(json.loads(ob.b4ml.flight_metrics)['intervals']),2)

    def test_cancel_and_mutated_settings(self):
        ob,source,sig,modes=fixture();scene=bpy.context.scene;original=ob.b4ml.candidate_action;pose=w.raw_pose(ob);actions=set(bpy.data.actions.keys())
        f.start(ob,scene);self.assertFalse(f.step(ob))
        with self.assertRaisesRegex(ValueError,'flight correction'):w.finish_preview(ob,scene,True)
        with self.assertRaisesRegex(ValueError,'flight correction'):c.start(ob,scene)
        f.abort(ob);self.assertEqual(w.raw_pose(ob),pose);self.assertEqual(set(bpy.data.actions.keys()),actions)
        f.start(ob,scene);f.step(ob);ob.b4ml.flights[0].strength=.5
        with self.assertRaisesRegex(ValueError,'changed'):f.step(ob)
        self.assertIs(ob.animation_data.action,original);self.assertFalse(ob.b4ml.flight_running)
    def test_partial_nonstacking_and_restore(self):
        ob,source,sig,modes=fixture();scene=bpy.context.scene;original=ob.b4ml.candidate_action;before=c._action_signature(ob)
        ob.b4ml.flights[0].strength=.5;f.solve(ob,scene);first=com(ob,6.)
        f.solve(ob,scene);np.testing.assert_allclose(com(ob,6.),first,atol=2e-6);self.assertIs(ob.b4ml.flight_input,original)
        f.restore(ob,scene);self.assertIs(ob.animation_data.action,original);self.assertEqual(c._action_signature(ob),before)
    def test_contacts_rejected_and_zero_strength(self):
        ob,source,sig,modes=fixture();scene=bpy.context.scene;original=ob.b4ml.candidate_action
        item=c.capture(ob,scene);item.start=4.;item.end=8.
        with self.assertRaisesRegex(ValueError,'overlap'):f.solve(ob,scene)
        self.assertIs(ob.animation_data.action,original);ob.b4ml.contacts.clear()
        ob.b4ml.flights[0].strength=0.;before=com(ob,6.);f.solve(ob,scene);np.testing.assert_allclose(com(ob,6.),before,atol=2e-6)
    def test_save_cancel_reload_keep_recovery(self):
        ob,source,sig,modes=fixture();scene=bpy.context.scene;name=ob.name;original=ob.b4ml.candidate_action
        f.start(ob,scene);f.step(ob);path=ROOT/'training/b4artists_ml/cache/flight-preview.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path));self.assertFalse(ob.b4ml.flight_running);self.assertIs(ob.animation_data.action,original)
        f.solve(ob,scene);bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path))
        ob=bpy.data.objects[name];scene=bpy.context.scene;bpy.context.view_layer.objects.active=ob
        self.assertEqual(len(ob.b4ml.flights),1);self.assertIs(ob.b4ml.flight_output,ob.animation_data.action)
        w.finish_preview(ob,scene,True);w.restore_kept_source(ob,scene);self.assertEqual(c._action_signature(ob),sig);self.assertEqual(rs.mode_values(ob),modes)

def run_ui_smoke():
    FlightTests.setUpClass();ob,source,sig,modes=fixture('rigify_default')
    state=dict(name=ob.name,source_name=source.name,source_signature=sig,modes=modes,phase='dismiss',started=time.monotonic(),events=[])
    version=os.environ.get('B4ML_FLIGHT_UI_TAG','development');steps=[];old_step=f.step
    def timed_step(obj):
        started=time.perf_counter()
        try:return old_step(obj)
        finally:steps.append((time.perf_counter()-started)*1000)
    f.step=timed_step
    def tick():
        try:
            if time.monotonic()-state['started']>240:raise AssertionError('Flight UI workflow timed out')
            win=bpy.context.window_manager.windows[0];area=next(a for a in win.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW')
            area.spaces.active.show_region_ui=True
            for r in area.regions:
                if r.type=='UI' and hasattr(r,'active_panel_category'):r.active_panel_category='B4Artists ML'
            ob=bpy.data.objects[state['name']];win.view_layer.objects.active=ob;ob.select_set(True)
            with bpy.context.temp_override(window=win,area=area,region=region):
                if state['phase']=='dismiss':
                    win.event_simulate(type='ESC',value='PRESS');bpy.ops.view3d.view_axis(type='FRONT');bpy.ops.view3d.view_selected(use_all_regions=False);state['phase']='begin'
                elif state['phase']=='begin':
                    ob.b4ml.flights.clear();bpy.context.scene.frame_set(1)
                    assert bpy.ops.b4ml.flight(operation='ADD')=={'FINISHED'}
                    ob.b4ml.show_flights=True;ob.b4ml.flight_index=0;bpy.context.scene.frame_set(6)
                    state['input_name']=ob.b4ml.candidate_action.name;state['input_signature']=c._action_signature(ob)
                    bpy.ops.ed.undo_push(message='Flight inputs ready')
                    assert bpy.ops.b4ml.flight_solve('INVOKE_DEFAULT')=={'RUNNING_MODAL'};state['phase']='completed';state['events'].append('Flight interval and modal correction invoked')
                elif state['phase']=='completed':
                    if ob.b4ml.flight_running:return .03
                    assert ob.b4ml.flight_output==ob.b4ml.candidate_action
                    metrics=json.loads(ob.b4ml.flight_metrics);assert metrics['max_after']<2e-4
                    state['metrics']=metrics;state['step_ms']=list(steps);state['result_name']=ob.b4ml.candidate_action.name
                    state['result_signature']=c._action_signature(ob);state['events'].append('Evaluated correction completed')
                    path=ROOT/f'training/b4artists_ml/cache/flight-ui-{version}.png';bpy.ops.screen.screenshot(filepath=str(path));state['screenshot']=str(path.relative_to(ROOT))
                    assert bpy.ops.b4ml.flight_solve('INVOKE_DEFAULT')=={'RUNNING_MODAL'};state['phase']='escape'
                elif state['phase']=='escape':
                    if not ob.b4ml.flight_progress.startswith('Fitting'):return .02
                    win.event_simulate(type='ESC',value='PRESS');state['phase']='cancelled'
                elif state['phase']=='cancelled':
                    if ob.b4ml.flight_running:return .02
                    assert ob.b4ml.candidate_action.name==state['result_name'];assert c._action_signature(ob)==state['result_signature']
                    state['events'].append('Escape restored previous candidate')
                    assert bpy.ops.b4ml.flight_solve('INVOKE_DEFAULT')=={'RUNNING_MODAL'};state['phase']='regenerate'
                elif state['phase']=='regenerate':
                    if ob.b4ml.flight_running:return .03
                    assert state['result_name'] not in bpy.data.actions
                    state['second_name']=ob.b4ml.candidate_action.name
                    assert bpy.ops.ed.undo()=={'FINISHED'};state['phase']='undo_replacement'
                elif state['phase']=='undo_replacement':
                    assert ob.b4ml.candidate_action.name==state['result_name'];assert c._action_signature(ob)==state['result_signature']
                    assert bpy.ops.ed.redo()=={'FINISHED'};state['phase']='redo_replacement'
                elif state['phase']=='redo_replacement':
                    assert ob.b4ml.candidate_action.name==state['second_name'];assert state['result_name'] not in bpy.data.actions
                    state['events'].append('Regeneration removes unused output; Undo/Redo restores replacement correctly')
                    assert bpy.ops.ed.undo()=={'FINISHED'};state['phase']='undo_first'
                elif state['phase']=='undo_first':
                    assert ob.b4ml.candidate_action.name==state['result_name']
                    assert bpy.ops.ed.undo()=={'FINISHED'};state['phase']='redo'
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
                    (ROOT/f'docs/b4artists_ml/flight-ui-{version}.json').write_text(json.dumps(report,indent=2)+'\n');print('FLIGHT_UI_RESULT: '+json.dumps(report),flush=True);bpy.ops.wm.quit_blender();return None
        except Exception as exc:
            report=dict(passed=False,phase=state['phase'],error=str(exc),traceback=traceback.format_exc(),events=state['events'])
            (ROOT/f'docs/b4artists_ml/flight-ui-{version}.json').write_text(json.dumps(report,indent=2)+'\n');print('FLIGHT_UI_RESULT: '+json.dumps(report),flush=True);bpy.ops.wm.quit_blender();return None
        return .03
    bpy.app.timers.register(tick,first_interval=.5)


if __name__=='__main__' and '--ui-smoke' in sys.argv:run_ui_smoke()
elif __name__=='__main__':
    selection=os.environ.get('B4ML_FLIGHT_TEST');suite=unittest.defaultTestLoader.loadTestsFromName(selection,sys.modules[__name__]) if selection else unittest.defaultTestLoader.loadTestsFromTestCase(FlightTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report=dict(tests=result.testsRun,passed=result.wasSuccessful(),errors=len(result.errors),failures=len(result.failures),records=RECORDS,package=b4artists_ml.__file__)
    (ROOT/'training/b4artists_ml/results'/os.environ.get('B4ML_FLIGHT_RESULT','flight-host-v1.json')).write_text(json.dumps(report,indent=2)+'\n')
    print('FLIGHT_RESULT: '+json.dumps({k:v for k,v in report.items() if k!='records'}),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
