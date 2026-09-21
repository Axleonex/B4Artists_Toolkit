"""Host lifecycle validation of packaged whole-body previews."""
import os,sys,json,time,traceback,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,os.environ.get('B4ML_PACKAGE',str(ROOT)))
sys.path.insert(1,str(ROOT/'tests'));sys.path.insert(2,str(ROOT/'training/b4artists_ml'))
import bpy
from mathutils import Matrix,Vector,Quaternion
import b4artists_ml
from b4artists_ml import body_preview as body,body_solver as solver,workflow as w,rig_state as rs,posing,rig_diagnostics,rig_mapping
from test_b4artists_ml_context_rig import ContextRigTests
VERSION='.'.join(map(str,b4artists_ml.bl_info['version']))
UI_RESULT_TAG=os.environ.get('B4ML_UI_RESULT_TAG',VERSION)

class PreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register();ContextRigTests.setUpClass();cls.fixtures=ContextRigTests()

    def make(self,label='boneforge'):
        ob,source,session,targets,mask=self.fixtures.fixture(label)
        session.cancel();modes=rs.mode_values(ob)
        bpy.context.view_layer.objects.active=ob;ob.select_set(True)
        return ob,source,modes,targets

    def begin(self,ob,targets):
        self.assertEqual(bpy.ops.b4ml.body(operation='BEGIN'),{'FINISHED'})
        for index,label in body.TARGETS:ob.b4ml.body_targets[label].target.location=targets[index]
        bpy.context.view_layer.update()

    def tearDown(self):
        for ob in list(bpy.data.objects):
            if hasattr(ob,'b4ml') and ob.b4ml.body_payload:
                if ob.users_scene:bpy.context.window.scene=ob.users_scene[0]
                try:body.finish(ob,bpy.context.scene,False)
                except Exception:pass
        body.reset_runtime()

    def test_operator_keep_and_interpolation_candidate(self):
        ob,source,modes,targets=self.make()
        self.begin(ob,targets)
        self.assertEqual(bpy.ops.b4ml.body_solve(),{'FINISHED'})
        solved=w.raw_pose(ob)
        self.assertEqual(bpy.ops.b4ml.body(operation='KEEP'),{'FINISHED'})
        self.assertFalse(ob.b4ml.body_payload);self.assertEqual(rs.mode_values(ob),modes)
        first=json.loads(ob.b4ml.anchors[0].payload)
        self.assertEqual(first['pose']['head']['raw_rotation'],list(solved['head']['raw_rotation']))
        for name,row in first['pose'].items():self.assertEqual(w.raw_pose(ob)[name],source[name])
        bpy.context.scene.frame_set(12);w.capture_anchor(ob,bpy.context.scene)
        w.preview(ob,bpy.context.scene)
        bpy.context.scene.frame_set(1)
        self.assertEqual(ob.animation_data.action,ob.b4ml.candidate_action)
        w.finish_preview(ob,bpy.context.scene,False)
        self.assertIsNone(ob.animation_data.action)

    def test_rigify_anchor_captures_complete_spine(self):
        ob,source,modes,targets=self.make('rigify_basic')
        self.begin(ob,targets);body.solve(ob);body.finish(ob,bpy.context.scene,True)
        names=set(json.loads(ob.b4ml.anchors[0].payload)['pose'])
        self.assertTrue({'spine_fk.002','spine_fk.003'}<=names)
        self.assertEqual(rs.mode_values(ob),modes)

    def test_cancel_mid_solve_restores_previous_preview(self):
        ob,source,modes,targets=self.make();self.begin(ob,targets);body.solve(ob)
        before=w.raw_pose(ob);ob.b4ml.body_targets['Head'].target.location.y+=.02
        body.start(ob);self.assertFalse(body.step(ob));self.assertTrue(ob.b4ml.body_running)
        body.abort(ob);self.assertEqual(w.raw_pose(ob),before);self.assertFalse(ob.b4ml.body_running)
        body.finish(ob,bpy.context.scene,False);self.assertEqual(rs.mode_values(ob),modes)

    def test_save_reload_keeps_solved_anchor(self):
        ob,source,modes,targets=self.make();self.begin(ob,targets);body.solve(ob)
        name=ob.name;source=body._plain(source);modes=body._plain(modes)
        path=ROOT/'training/b4artists_ml/cache/body-preview-reload-test.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        bpy.ops.wm.open_mainfile(filepath=str(path))
        ob=bpy.data.objects[name];bpy.context.view_layer.objects.active=ob
        self.assertFalse(body._LIVE)
        self.assertTrue(ob.b4ml.body_payload)
        body.finish(ob,bpy.context.scene,True)
        self.assertEqual(len(ob.b4ml.anchors),1);self.assertEqual(rs.mode_values(ob),modes)
        for name in json.loads(ob.b4ml.anchors[0].payload)['pose']:
            self.assertEqual(body._plain(w.raw_pose(ob)[name]),source[name])

    def test_animated_source_keys_and_slot_survive_reload(self):
        ob,source,modes,targets=self.make();scene=bpy.context.scene
        for row in rs.mode_bindings(ob):
            pb=ob.pose.bones[row['property_bone']]
            for frame,value in ((1,1.-row['fk_value']),(12,row['fk_value'])):
                pb[row['key']]=value;pb.keyframe_insert('['+json.dumps(row['key'])+']',frame=frame)
        scene.frame_set(1);posing._update(ob)
        source=w.raw_pose(ob);modes=rs.mode_values(ob)
        action_name=ob.animation_data.action.name;slot=w._slot(ob.animation_data)
        def keys(obj):
            return [(c.data_path,c.array_index,[(tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.interpolation) for k in c.keyframe_points]) for c in w.action_curves(obj.animation_data.action,obj.animation_data.action_slot)]
        original=keys(ob);self.begin(ob,targets);body.solve(ob);name=ob.name
        path=ROOT/'training/b4artists_ml/cache/body-preview-action-test.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path))
        ob=bpy.data.objects[name];bpy.context.view_layer.objects.active=ob
        body.finish(ob,bpy.context.scene,True)
        self.assertEqual(ob.animation_data.action.name,action_name)
        self.assertEqual(w._slot(ob.animation_data),slot);self.assertEqual(keys(ob),original)
        self.assertEqual(rs.mode_values(ob),modes)
        for name,row in source.items():self.assertEqual(w.raw_pose(ob)[name],row)

    def test_save_during_solve_recovers_previous_pose(self):
        ob,source,modes,targets=self.make();self.begin(ob,targets);body.solve(ob)
        previous=w.raw_pose(ob);body.start(ob);body.step(ob)
        path=ROOT/'training/b4artists_ml/cache/body-preview-interrupted-test.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        self.assertFalse(ob.b4ml.body_running);self.assertEqual(w.raw_pose(ob),previous)
        self.assertFalse(body._JOBS)
        body.finish(ob,bpy.context.scene,False)

    def test_corrupt_saved_preview_rejected_before_mutation(self):
        ob,source,modes,targets=self.make();self.begin(ob,targets)
        original=ob.b4ml.body_payload;record=json.loads(original)
        name=next(iter(record['preview']));record['preview'][name]['location'][0]=float('nan')
        ob.b4ml.body_payload=json.dumps(record);body.reset_runtime();before=w.raw_pose(ob)
        with self.assertRaisesRegex(ValueError,'Invalid saved control'):body.start(ob)
        self.assertEqual(w.raw_pose(ob),before)
        ob.b4ml.body_payload=original;body.finish(ob,bpy.context.scene,False)

    def test_corrupt_solver_metadata_is_rejected(self):
        ob,source,modes,targets=self.make();self.begin(ob,targets)
        original=ob.b4ml.body_payload;record=json.loads(original)
        record['session']['q0'][0][0]=float('nan')
        body.reset_runtime();before=w.raw_pose(ob);ob.b4ml.body_payload=json.dumps(record)
        with self.assertRaisesRegex(ValueError,'Invalid saved solver'):body.start(ob)
        self.assertEqual(w.raw_pose(ob),before)
        ob.b4ml.body_payload=original;body.finish(ob,bpy.context.scene,False)

    def test_unregister_restores_previews_in_their_own_scenes(self):
        first,source_a,modes_a,targets_a=self.make();scene_a=bpy.context.scene
        self.begin(first,targets_a)
        second,source_b,modes_b,targets_b=self.make();scene_b=bpy.context.scene
        scene_b.frame_set(7);self.begin(second,targets_b)
        scene_a.frame_set(4)
        try:
            b4artists_ml.unregister()
            self.assertEqual(scene_a.frame_current,1)
            self.assertEqual(scene_b.frame_current,7)
            self.assertEqual(rs.mode_values(first),modes_a)
            self.assertEqual(rs.mode_values(second),modes_b)
            for ob,source in ((first,source_a),(second,source_b)):
                for name,row in source.items():self.assertEqual(w.raw_pose(ob)[name],row)
            self.assertFalse(body._LIVE);self.assertFalse(body._JOBS)
        finally:b4artists_ml.register()

    def test_conflicting_preview_workflows_rejected(self):
        ob,source,modes,targets=self.make();self.begin(ob,targets)
        with self.assertRaises(ValueError):posing.begin(ob,bpy.context.scene)
        with self.assertRaises(ValueError):w.capture_anchor(ob,bpy.context.scene)
        with self.assertRaises(ValueError):w.preview(ob,bpy.context.scene)
        body.finish(ob,bpy.context.scene,False)

def run_ui_smoke():
    """Exercise the real window event loop, simulated Escape, and undo/redo."""
    PreviewTests.setUpClass();test=PreviewTests();fixture=os.environ.get('B4ML_UI_RIG','boneforge');ob,source,modes,targets=test.make(fixture)
    state=dict(fixture=fixture,phase='dismiss_splash',started=time.monotonic(),name=ob.name,source=body._plain(source),modes=modes,events=[])
    report_path=ROOT/f'docs/b4artists_ml/body-preview-ui-v{UI_RESULT_TAG}.json'
    def context_for():
        win=bpy.context.window_manager.windows[0]
        area=next(a for a in win.screen.areas if a.type=='VIEW_3D')
        region=next(r for r in area.regions if r.type=='WINDOW')
        area.spaces.active.show_region_ui=True
        for sidebar in area.regions:
            if sidebar.type=='UI' and hasattr(sidebar,'active_panel_category'):
                try:sidebar.active_panel_category='B4Artists ML'
                except (AttributeError,TypeError):pass
        ob=bpy.data.objects[state['name']];win.view_layer.objects.active=ob;ob.select_set(True)
        return win,area,region,ob
    def tick():
        try:
            if time.monotonic()-state['started']>50:raise AssertionError('Modal test timed out')
            win,area,region,ob=context_for()
            with bpy.context.temp_override(window=win,area=area,region=region):
                if state['phase']=='dismiss_splash':
                    win.event_simulate(type='ESC',value='PRESS')
                    bpy.ops.view3d.view_axis(type='FRONT')
                    bpy.ops.view3d.view_selected(use_all_regions=False)
                    state['phase']='begin'
                elif state['phase']=='pose_reuse_undo':
                    assert bpy.ops.ed.undo()=={'FINISHED'}
                    ob=bpy.data.objects[state['name']]
                    assert len(ob.b4ml.anchors)==2
                    state['events'].append('native undo removed reused pose anchor')
                    state['phase']='pose_reuse_redo'
                elif state['phase']=='pose_reuse_redo':
                    assert bpy.ops.ed.redo()=={'FINISHED'}
                    ob=bpy.data.objects[state['name']]
                    assert len(ob.b4ml.anchors)==3
                    target=next(a for a in ob.b4ml.anchors if abs(a.frame-5.)<1e-5)
                    assert json.loads(target.payload)==state['pose_reuse_source']
                    assert body._plain(w.raw_pose(ob))==state['pose_reuse_pose']
                    state['events'].append('native redo restored exact reused pose anchor')
                    state['pose_reuse_ready']=True;state['phase']='begin'
                elif state['phase']=='mapping_undo':
                    assert bpy.ops.ed.undo()=={'FINISHED'}
                    ob=bpy.data.objects[state['name']]
                    assert rig_mapping.PROPERTY_KEY not in ob
                    assert body._plain(w.raw_pose(ob))==state['mapping_pose']
                    state['events'].append('native undo removed humanoid mapping correction')
                    state['phase']='mapping_redo'
                elif state['phase']=='mapping_redo':
                    assert bpy.ops.ed.redo()=={'FINISHED'}
                    ob=bpy.data.objects[state['name']]
                    assert rig_mapping.profile_for_object(ob).roles['head']=='animator_head.custom'
                    assert body._plain(w.raw_pose(ob))==state['mapping_pose']
                    assert bpy.ops.b4ml.mapping_correction(operation='CLEAR_ALL')=={'FINISHED'}
                    assert rig_mapping.PROPERTY_KEY not in ob
                    ob.b4ml.show_rig_diagnostics=False;ob.b4ml.show_mapping_corrections=True
                    state['events'].append('native redo restored and Clear All removed the correction')
                    state['mapping_ready']=True;state['phase']='begin'
                elif state['phase']=='begin':
                    if os.environ.get('B4ML_UI_POSE_REUSE') and not state.get('pose_reuse_ready'):
                        bpy.context.scene.frame_set(1)
                        assert bpy.ops.b4ml.action(operation='CAPTURE')=={'FINISHED'}
                        first=json.loads(ob.b4ml.anchors[0].payload)
                        changed=False
                        for name,value in first['pose'].items():
                            for index,enabled in enumerate(value['channels']['location']):
                                if enabled:
                                    ob.pose.bones[name].location[index]+=.071;changed=True;break
                            if changed:break
                        assert changed
                        bpy.context.scene.frame_set(9)
                        assert bpy.ops.b4ml.action(operation='CAPTURE')=={'FINISHED'}
                        bpy.context.scene.frame_set(5);bpy.context.view_layer.update()
                        state['pose_reuse_pose']=body._plain(w.raw_pose(ob))
                        state['pose_reuse_source']=first
                        bpy.ops.ed.undo_push(message='Before reusable pose anchor')
                        assert bpy.ops.b4ml.action(operation='REUSE',anchor_frame=1.)=={'FINISHED'}
                        assert len(ob.b4ml.anchors)==3
                        assert body._plain(w.raw_pose(ob))==state['pose_reuse_pose']
                        bpy.ops.ed.undo_push(message='Reusable pose anchor created')
                        state['events'].append('reused stored pose at current frame without applying it')
                        state['phase']='pose_reuse_undo';return .05
                    if os.environ.get('B4ML_UI_MAPPING_CORRECTION') and not state.get('mapping_ready'):
                        bpy.ops.object.mode_set(mode='EDIT')
                        original=ob.data.edit_bones['head'];custom=ob.data.edit_bones.new('animator_head.custom')
                        custom.head=original.head;custom.tail=original.tail;custom.matrix=original.matrix
                        custom.parent=original.parent;custom.use_deform=False
                        bpy.ops.object.mode_set(mode='OBJECT');bpy.context.view_layer.update()
                        state['mapping_pose']=body._plain(w.raw_pose(ob))
                        ob.b4ml.mapping_role='head';ob.b4ml.mapping_bone='animator_head.custom'
                        ob.b4ml.show_mapping_corrections=True
                        bpy.ops.ed.undo_push(message='Before humanoid mapping correction')
                        assert bpy.ops.b4ml.mapping_correction(operation='APPLY')=={'FINISHED'}
                        report=rig_diagnostics.decode(ob.b4ml.rig_diagnostics_report)
                        assert report['correction_state']=='active'
                        assert report['manual_corrections']==[{'role':'head','bone':'animator_head.custom'}]
                        state['mapping_correction']=dict(role='head',bone='animator_head.custom',
                                                         schema=report['schema'])
                        assert body._plain(w.raw_pose(ob))==state['mapping_pose']
                        bpy.ops.ed.undo_push(message='Humanoid mapping correction applied')
                        state['events'].append('applied validated humanoid role correction without changing pose')
                        state['phase']='mapping_undo';return .05
                    bpy.ops.ed.undo_push(message='Whole-body test fixture ready')
                    if os.environ.get('B4ML_UI_DIAGNOSTICS'):
                        assert bpy.ops.b4ml.action(operation='INSPECT')=={'FINISHED'}
                        report=rig_diagnostics.analyze(ob)
                        assert ob.b4ml.show_rig_diagnostics
                        assert report['mapped_required_role_count']==report['required_role_count']
                        assert next(row for row in report['workflows'] if row['id']=='humanoid_whole_body')['ready']
                        state['events'].append('rig mapping diagnostics opened with whole-body preflight')
                    test.begin(ob,targets)
                    if os.environ.get('B4ML_UI_CHEST_ORIENTATION'):
                        chest=ob.b4ml.body_targets['Chest'];chest.enabled=False
                        chest.use_orientation=True
                        chest.target.rotation_quaternion=(
                            chest.target.rotation_quaternion@Quaternion((0.,0.,1.),.02))
                        bpy.context.view_layer.update()
                        state['chest_goal']=list(chest.target.matrix_world.to_quaternion())
                        state['events'].append('authored semantic Chest rotation target')
                    if os.environ.get('B4ML_UI_NECK_TARGET'):
                        assert json.loads(ob.b4ml.body_payload)['controls_version']>=5
                        neck=ob.b4ml.body_targets['Neck'];neck.enabled=False
                        neck.use_orientation=True
                        neck.target.rotation_quaternion=(
                            neck.target.rotation_quaternion@Quaternion((0.,0.,1.),.015))
                        bpy.context.view_layer.update()
                        state['neck_goal']=list(neck.target.matrix_world.to_quaternion())
                        state['events'].append('authored semantic Neck rotation target')
                    if os.environ.get('B4ML_UI_POSE_ASSET'):
                        hand=ob.b4ml.body_targets['Hand L'];session=body._get(ob)
                        hand.target.location+=Vector(session.basis[:,0]*session.scale*.008)
                        bpy.context.view_layer.update();body.solve(ob)
                        solved_target=hand.target.matrix_world.copy()
                        assert bpy.ops.b4ml.body(operation='SAVE_POSE_ASSET')=={'FINISHED'}
                        assert isinstance(bpy.context.scene.get(body.POSE_ASSET_KEY),str)
                        body.reset_target(ob,'Hand L')
                        assert bpy.ops.b4ml.body(operation='APPLY_POSE_ASSET')=={'FINISHED'}
                        assert body.np.allclose(body.np.asarray(hand.target.matrix_world,float),
                                                body.np.asarray(solved_target,float),atol=1e-7)
                        state['pose_asset_metrics']=dict(
                            source_profile=body._read_pose_asset(bpy.context.scene)['source_profile'],
                            bytes=len(bpy.context.scene[body.POSE_ASSET_KEY]))
                        state['events'].append('saved and reapplied semantic pose asset through UI operators')
                    if os.environ.get('B4ML_UI_RESET'):
                        item=ob.b4ml.body_targets['Hand L']
                        origin=json.loads(ob.b4ml.body_payload)['target_origins']['Hand L']
                        item.target.location.x+=.2
                        assert bpy.ops.b4ml.body(operation='RESET_TARGET',target_name='Hand L')=={'FINISHED'}
                        assert max(abs(item.target.location[i]-origin[i]) for i in range(3))<1e-8
                        state['events'].append('target reset operator restored helper')
                    if os.environ.get('B4ML_UI_MIRROR'):
                        record=json.loads(ob.b4ml.body_payload);left=ob.b4ml.body_targets['Hand L'];right=ob.b4ml.body_targets['Hand R']
                        left_start=Matrix(record['target_matrices']['Hand L']);right_start=Matrix(record['target_matrices']['Hand R'])
                        left.target.location+=Vector((.12,-.04,.03));bpy.context.view_layer.update();source_matrix=left.target.matrix_world.copy()
                        assert bpy.ops.b4ml.body(operation='MIRROR_TARGETS',mirror_direction='LEFT_TO_RIGHT')=={'FINISHED'}
                        basis=body.np.asarray(record['session']['basis'],float)
                        frame=body.np.asarray(Matrix(record['motion_transform']).to_quaternion().to_matrix(),float)@basis
                        source_delta=frame.T@body.np.asarray(left.target.matrix_world.translation-left_start.translation,float)
                        mirrored_delta=frame.T@body.np.asarray(right.target.matrix_world.translation-right_start.translation,float)
                        assert body.np.allclose(mirrored_delta,source_delta*(-1.,1.,1.),atol=1e-7)
                        assert body.np.allclose(left.target.matrix_world,source_matrix)
                        # Transform correctness is covered across three rig families in the
                        # focused suite. Keep the UI lifecycle on its established feasible pins.
                        left.enabled=False;right.enabled=False
                        state['events'].append('semantic target mirror operator copied left helpers to right')
                    if os.environ.get('B4ML_UI_POLE_ALIGN'):
                        label='Hand L';item=ob.b4ml.body_targets[label];item.use_pole=True
                        session=body._get(ob);record=json.loads(ob.b4ml.body_payload)
                        index=dict((name,index) for index,name in body._target_rows(record))[label]
                        middle=body.POLE_JOINTS[index];chain=solver.POLE_CHAINS[middle]
                        points=session.world_points(session.points());root,centre,end=(points[i] for i in chain)
                        axis=end-root;axis/=body.np.linalg.norm(axis)
                        bend=centre-root;bend-=axis*body.np.dot(bend,axis)
                        assert body.np.linalg.norm(bend)>session.scale*1e-5
                        bend/=body.np.linalg.norm(bend)
                        side=body.np.cross(axis,bend);side/=body.np.linalg.norm(side)
                        motion=Matrix(record['motion_transform']);inverse=motion.inverted()
                        current=body.np.asarray(inverse@item.pole.matrix_world.translation,float)
                        distance=max(float(body.np.linalg.norm(current-centre)),session.scale*.4)
                        item.pole.matrix_world.translation=motion@Vector(centre+side*distance)
                        bpy.context.view_layer.update()
                        before=body.np.asarray(inverse@item.pole.matrix_world.translation,float)
                        before_bend,before_wanted=solver._pole_vectors(points,chain,before)
                        before_error=float(body.np.arctan2(body.np.linalg.norm(body.np.cross(before_bend,before_wanted)),
                                                        body.np.dot(before_bend,before_wanted)))
                        assert before_error>.5
                        assert bpy.ops.b4ml.body(operation='ALIGN_POLE',target_name=label)=={'FINISHED'}
                        aligned=body.np.asarray(inverse@item.pole.matrix_world.translation,float)
                        aligned_bend,aligned_wanted=solver._pole_vectors(points,chain,aligned)
                        error=float(body.np.arctan2(body.np.linalg.norm(body.np.cross(aligned_bend,aligned_wanted)),
                                                  body.np.dot(aligned_bend,aligned_wanted)))
                        assert error<1e-6 and item.use_pole
                        assert abs(float(body.np.linalg.norm(aligned-centre))-distance)<1e-6
                        state['pole_align_metrics']=dict(target=label,before_error_radians=before_error,
                            alignment_error_radians=error,distance=distance,toggle_preserved=True)
                        state['events'].append('aligned Hand L pole to evaluated bend')
                    if os.environ.get('B4ML_UI_POLE_FLIP'):
                        label='Hand L';item=ob.b4ml.body_targets[label];item.use_pole=True
                        session=body._get(ob);record=json.loads(ob.b4ml.body_payload)
                        index=dict((name,index) for index,name in body._target_rows(record))[label]
                        middle=body.POLE_JOINTS[index];chain=solver.POLE_CHAINS[middle]
                        points=session.world_points(session.points());root,centre,end=(points[i] for i in chain)
                        motion=Matrix(record['motion_transform']);inverse=motion.inverted()
                        before=body.np.asarray(inverse@item.pole.matrix_world.translation,float)
                        distance=max(float(body.np.linalg.norm(before-centre)),session.scale*.4)
                        assert bpy.ops.b4ml.body(operation='FLIP_POLE',target_name=label)=={'FINISHED'}
                        flipped=body.np.asarray(inverse@item.pole.matrix_world.translation,float)
                        bend,wanted=solver._pole_vectors(points,chain,flipped);intended=-bend
                        error=float(body.np.arctan2(body.np.linalg.norm(body.np.cross(intended,wanted)),
                                                  body.np.dot(intended,wanted)))
                        assert error<2e-6 and item.use_pole
                        assert abs(float(body.np.linalg.norm(flipped-centre))-distance)<1e-6
                        state['pole_flip_metrics']=dict(target=label,opposite_error_radians=error,
                            distance=distance,toggle_preserved=True)
                        state['events'].append('flipped Hand L pole opposite evaluated bend')
                    if os.environ.get('B4ML_UI_POLE_DISTANCE'):
                        label='Hand L';item=ob.b4ml.body_targets[label];item.use_pole=True
                        session=body._get(ob);record=json.loads(ob.b4ml.body_payload)
                        index=dict((name,index) for index,name in body._target_rows(record))[label]
                        middle=body.POLE_JOINTS[index];points=session.world_points(session.points())
                        motion=Matrix(record['motion_transform']);inverse=motion.inverted()
                        before=body.np.asarray(inverse@item.pole.matrix_world.translation,float)-points[middle]
                        before/=body.np.linalg.norm(before);item.pole_distance=.85
                        assert bpy.ops.b4ml.body(operation='SET_POLE_DISTANCE',target_name=label)=={'FINISHED'}
                        after=body.np.asarray(inverse@item.pole.matrix_world.translation,float)-points[middle]
                        distance=float(body.np.linalg.norm(after));after/=distance
                        assert abs(distance/session.scale-.85)<1e-6
                        direction_error=float(body.np.linalg.norm(after-before));assert direction_error<2e-6
                        assert item.use_pole and item.pole.empty_display_type=='CIRCLE' and item.pole.show_in_front
                        state['pole_distance_metrics']=dict(target=label,distance_body_scales=distance/session.scale,
                            direction_error=direction_error,toggle_preserved=True,display='CIRCLE_IN_FRONT')
                        state['events'].append('applied body-scale Hand L pole distance')
                    if os.environ.get('B4ML_UI_CONTROLS'):
                        from test_b4artists_ml_body_controls import BodyControlTests
                        points,rotations,poles=BodyControlTests().desired(body._get(ob))
                        for index,label in body.TARGETS:
                            item=ob.b4ml.body_targets[label];item.target.location=points[index]
                            if index in solver.ORIENTATION_JOINTS:
                                item.target.rotation_quaternion=rotations[index];item.use_orientation=True
                            if index in body.POLE_JOINTS:
                                item.pole.location=poles[body.POLE_JOINTS[index]];item.use_pole=True
                        bpy.context.view_layer.update()
                    state['unsolved']=body._plain(w.raw_pose(ob))
                    bpy.ops.ed.undo_push(message='Whole-body targets authored')
                    outcome=bpy.ops.b4ml.body_solve('INVOKE_DEFAULT')
                    assert outcome=={'RUNNING_MODAL'},outcome
                    state['phase']='completed';state['events'].append('modal invoked')
                elif state['phase']=='completed':
                    if ob.b4ml.body_running:return .05
                    assert json.loads(ob.b4ml.body_payload)['signature'] is not None,(ob.b4ml.status,len(body._JOBS),ob.b4ml.body_progress)
                    assert not any(s.name.startswith('B4ML private evaluation') for s in bpy.data.scenes)
                    if fixture=='rigify_default':assert json.loads(ob.b4ml.body_payload)['metrics']['evaluation_backend']=='proxy'
                    if os.environ.get('B4ML_UI_CONTROLS'):
                        metrics=json.loads(ob.b4ml.body_payload)['metrics']
                        assert metrics['requested_orientations']==6 and metrics['requested_poles']==4
                        state['control_metrics']=metrics
                    if os.environ.get('B4ML_UI_CHEST_ORIENTATION'):
                        metrics=json.loads(ob.b4ml.body_payload)['metrics'];session=body._get(ob)
                        actual=(session.world.to_quaternion()
                                @ob.pose.bones[solver.orientation_bone(session.binding,2)].matrix.to_quaternion())
                        error=solver._angle(Quaternion(state['chest_goal']),actual)
                        assert metrics['requested_orientations']==1 and error<.001,(metrics,error)
                        state['chest_metrics']=dict(error_radians=error,
                            evaluations=metrics['evaluations'],elapsed_ms=metrics['elapsed_ms'])
                        state['events'].append('evaluated Chest rotation met the orientation gate')
                    if os.environ.get('B4ML_UI_NECK_TARGET'):
                        metrics=json.loads(ob.b4ml.body_payload)['metrics'];session=body._get(ob)
                        actual=(session.world.to_quaternion()
                                @ob.pose.bones[solver.orientation_bone(session.binding,3)].matrix.to_quaternion())
                        error=solver._angle(Quaternion(state['neck_goal']),actual)
                        assert metrics['requested_orientations']==1 and error<.001,(metrics,error)
                        state['neck_metrics']=dict(error_radians=error,
                            evaluations=metrics['evaluations'],elapsed_ms=metrics['elapsed_ms'])
                        state['events'].append('evaluated Neck rotation met the orientation gate')
                    if os.environ.get('B4ML_UI_POLE_ALIGN'):
                        metrics=json.loads(ob.b4ml.body_payload)['metrics']
                        assert metrics['requested_poles']==1 and metrics['pole_error_radians']<.01,metrics
                        state['pole_align_metrics']['solve_error_radians']=metrics['pole_error_radians']
                        state['pole_align_metrics']['evaluations']=metrics['evaluations']
                        state['pole_align_metrics']['elapsed_ms']=metrics['elapsed_ms']
                        state['events'].append('aligned pole survived modal solve gate')
                    if os.environ.get('B4ML_UI_POLE_FLIP'):
                        metrics=json.loads(ob.b4ml.body_payload)['metrics']
                        assert metrics['requested_poles']==1 and metrics['pole_error_radians']<.01,metrics
                        state['pole_flip_metrics']['solve_error_radians']=metrics['pole_error_radians']
                        state['pole_flip_metrics']['evaluations']=metrics['evaluations']
                        state['pole_flip_metrics']['elapsed_ms']=metrics['elapsed_ms']
                        state['events'].append('flipped pole survived modal solve gate')
                    if os.environ.get('B4ML_UI_POLE_DISTANCE'):
                        metrics=json.loads(ob.b4ml.body_payload)['metrics']
                        assert metrics['requested_poles']==1 and metrics['pole_error_radians']<.01,metrics
                        state['pole_distance_metrics']['solve_error_radians']=metrics['pole_error_radians']
                        state['pole_distance_metrics']['evaluations']=metrics['evaluations']
                        state['pole_distance_metrics']['elapsed_ms']=metrics['elapsed_ms']
                        state['events'].append('distance-adjusted pole survived modal solve gate')
                    state['preview']=body._plain(w.raw_pose(ob));state['events'].append('timer-driven solve completed')
                    try:
                        bpy.ops.screen.screenshot(filepath=str(ROOT/f'training/b4artists_ml/cache/body-preview-ui-v{UI_RESULT_TAG}.png'))
                        state['screenshot']=f'training/b4artists_ml/cache/body-preview-ui-v{UI_RESULT_TAG}.png'
                    except Exception as exc:state['screenshot_error']=str(exc)
                    assert bpy.ops.b4ml.body_solve('INVOKE_DEFAULT')=={'RUNNING_MODAL'}
                    state['phase']='send_escape'
                elif state['phase']=='send_escape':
                    if not ob.b4ml.body_progress.startswith('Solving'):return .02
                    state['second_solve_private_scene']=any(s.name.startswith('B4ML private evaluation') for s in bpy.data.scenes)
                    win.event_simulate(type='ESC',value='PRESS')
                    state['phase']='cancelled'
                elif state['phase']=='cancelled':
                    if ob.b4ml.body_running:return .02
                    assert body._plain(w.raw_pose(ob))==state['preview']
                    assert not any(s.name.startswith('B4ML private evaluation') for s in bpy.data.scenes)
                    state['events'].append('Escape restored previous preview')
                    assert bpy.ops.ed.undo()=={'FINISHED'}
                    state['phase']='redo'
                elif state['phase']=='redo':
                    assert not any(s.name.startswith('B4ML private evaluation') for s in bpy.data.scenes)
                    assert ob.b4ml.body_payload,'Undo removed preview setup'
                    assert json.loads(ob.b4ml.body_payload)['signature'] is None,'Undo did not remove solved result'
                    assert body._plain(w.raw_pose(ob))==state['unsolved'],'Undo did not restore pre-solve controls'
                    assert bpy.ops.ed.redo()=={'FINISHED'}
                    state['phase']='keep'
                elif state['phase']=='keep':
                    assert ob.b4ml.body_payload
                    assert body._plain(w.raw_pose(ob))==state['preview'],'Redo did not restore solved controls'
                    assert bpy.ops.b4ml.body(operation='KEEP')=={'FINISHED'}
                    assert len(ob.b4ml.anchors)==(3 if os.environ.get('B4ML_UI_POSE_REUSE') else 1)
                    assert rs.mode_values(ob)==state['modes']
                    state['events'].append('undo/redo and keep restored source modes')
                    report=dict(passed=True,fixture=fixture,control_metrics=state.get('control_metrics'),
                        chest_metrics=state.get('chest_metrics'),neck_metrics=state.get('neck_metrics'),
                        mapping_correction=state.get('mapping_correction'),
                        pose_asset_metrics=state.get('pose_asset_metrics'),
                        pole_align_metrics=state.get('pole_align_metrics'),
                        pole_flip_metrics=state.get('pole_flip_metrics'),pole_distance_metrics=state.get('pole_distance_metrics'),
                        package=b4artists_ml.__file__,
                        events=state['events'],elapsed_seconds=time.monotonic()-state['started'],
                        screenshot=state.get('screenshot'),screenshot_error=state.get('screenshot_error'))
                    report_path.write_text(json.dumps(report,indent=2)+'\n')
                    print('BODY_UI_RESULT: '+json.dumps(report),flush=True)
                    bpy.ops.wm.quit_blender();return None
        except Exception as exc:
            report=dict(passed=False,phase=state['phase'],error=str(exc),traceback=traceback.format_exc(),events=state['events'])
            report_path.write_text(json.dumps(report,indent=2)+'\n');print('BODY_UI_RESULT: '+json.dumps(report),flush=True)
            bpy.ops.wm.quit_blender();return None
        return .05
    bpy.app.timers.register(tick,first_interval=.5)


if __name__=='__main__' and '--ui-smoke' in sys.argv:
    run_ui_smoke()
elif __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PreviewTests))
    report=dict(tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),errors=len(result.errors),skips=len(result.skipped),package=b4artists_ml.__file__)
    (ROOT/f'docs/b4artists_ml/body-preview-test-v{VERSION}.json').write_text(json.dumps(report,indent=2)+'\n')
    print('BODY_PREVIEW_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
