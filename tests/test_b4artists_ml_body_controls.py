"""Explicit whole-body orientation and pole intent on actual humanoid controls."""
from pathlib import Path
import os,sys,json,time,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy,numpy as np
from mathutils import Quaternion
import b4artists_ml
from b4artists_ml import body_solver as solver,body_preview as body,workflow as w,posing,rig_state as rs
from test_b4artists_ml_context_rig import ContextRigTests
RECORDS=[]

class BodyControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ContextRigTests.setUpClass();cls.fixtures=ContextRigTests()

    def desired(self,s):
        rng=np.random.default_rng(324)
        x=rng.normal(0,.08,3+3*len(s.q0));x[:3]*=.1;s._apply(x)
        for n in s.binding['effectors']:
            pb=s.obj.pose.bones[n];solver._set_quat(pb,solver._quat(pb)@Quaternion((1,0,0),.15))
        posing._update(s.obj)
        points=s.world_points(s.points())
        orientation={0:list(s.world.to_quaternion()@s.obj.pose.bones[s.binding['names'][0]].matrix.to_quaternion())}
        for i,n in zip(solver.ORIENTATION_JOINTS[1:],s.binding['effectors']):orientation[i]=list(s.world.to_quaternion()@s.obj.pose.bones[n].matrix.to_quaternion())
        self.evaluated_goal={s.binding['names'][i]:s.obj.pose.bones[s.binding['names'][i]].matrix.to_quaternion().copy() for i in solver.ORIENTATION_JOINTS}
        poles={i:points[i].copy() for i in solver.POLE_CHAINS}
        w.restore_pose(s.obj,s.normalized);posing._update(s.obj)
        return points,orientation,poles

    def test_feasible_full_control_requests_on_five_rigs(self):
        for label in os.environ.get('B4ML_CONTROL_RIGS',','.join(self.fixtures.builders)).split(','):
            with self.subTest(rig=label):
                ob,source,s,targets,mask=self.fixtures.fixture(label,transformed=True)
                try:
                    points,orientation,poles=self.desired(s)
                    result=s.solve(points,mask,iterations=80,jacobian_mode=os.environ.get('B4ML_CONTROL_JACOBIAN','reuse'),orientations_world=orientation,pole_targets=poles)
                    RECORDS.append(dict(fixture=label,**{k:v for k,v in result.items() if k!='points'}))
                    print('BODY_CONTROL_METRIC: '+json.dumps(RECORDS[-1]),flush=True)
                    self.assertLess(result['pin_error'],2e-4)
                    self.assertLess(result['orientation_error_radians'],.001)
                    self.assertLess(result['pole_error_radians'],.01)
                    self.assertEqual(result['requested_orientations'],6)
                    self.assertEqual(result['requested_poles'],4)
                    for name,q in self.evaluated_goal.items():self.assertLess(solver._angle(q,ob.pose.bones[name].matrix.to_quaternion()),.001)
                finally:s.cancel()

    def test_coupled_torso_math_is_bounded_and_fail_closed(self):
        jacobian=np.array(((0.,1.,0.,0.),(-1.,0.,0.,.5),(0.,0.,0.,0.)),dtype=float)
        update,metrics=solver.bounded_coupled_torso_update(jacobian,np.array((.02,.01,0.)))
        self.assertLessEqual(metrics['applied_norm'],solver.MAX_COUPLED_TORSO_PARAMETER_NORM)
        self.assertGreaterEqual(metrics['rank'],2)
        self.assertTrue(np.isfinite(update).all())
        solver.verify_coupled_torso_request(np.array((.02,.01,0.)),metrics)
        with self.assertRaisesRegex(ValueError,'insufficient torso control rank'):
            solver.bounded_coupled_torso_update(np.array(((1.,0.),(0.,0.),(0.,0.))),np.zeros(3))
        with self.assertRaisesRegex(ValueError,'outside the verified torso control space'):
            solver.verify_coupled_torso_request(np.array((1.,0.,0.)),dict(residual_norm=.3))

    def test_coupled_spine_target_on_six_humanoid_adapters(self):
        """A reachable coupled Pelvis/Spine target must solve on every adapter."""
        from test_b4artists_ml_imported_humanoids import authored

        def feasible_spine(ob,s):
            controls=solver.coupled_torso_controls(s.binding)
            slot=s.binding['rotations'].index(controls[0])
            x=np.zeros(3+3*len(s.q0));x[3+slot*3:6+slot*3]=(.04,-.02,.01)
            s._apply(x);posing._update(ob);points=s.world_points(s.points());s.cancel()
            return points

        for label in self.fixtures.builders:
            with self.subTest(adapter=label):
                ob,source,s,_,_=self.fixtures.fixture(label,transformed=True)
                points=feasible_spine(ob,s)
                bpy.context.view_layer.objects.active=ob;body.begin(ob,bpy.context.scene)
                for item in ob.b4ml.body_targets:item.enabled=item.name in {'Pelvis','Spine'}
                ob.b4ml.body_targets['Pelvis'].target.location=points[0]
                ob.b4ml.body_targets['Spine'].target.location=points[1]
                try:body.solve(ob)
                except solver.CoupledTorsoError as error:
                    self.assertIn(label, {'rigify_basic','rigify_default'})
                    RECORDS.append(dict(adapter=label,status='fail_closed',reason=str(error)))
                    body.finish(ob,bpy.context.scene,False)
                    self.assertEqual(w.raw_pose(ob),source)
                    continue
                session=body._get(ob);actual=session.world_points(session.points())
                record=body._read(ob);coupling=record['metrics']['torso_coupling']
                self.assertLess(float(np.linalg.norm(actual[1]-points[1]))/session.scale,2e-4)
                self.assertLess(float(np.linalg.norm(actual[0]-points[0]))/session.scale,2e-4)
                self.assertGreaterEqual(coupling['rank'],2)
                self.assertTrue(np.isfinite(coupling['residual_norm']))
                RECORDS.append(dict(adapter=label,spine_error_body_scales=float(np.linalg.norm(actual[1]-points[1])/session.scale),
                                    pelvis_error_body_scales=float(np.linalg.norm(actual[0]-points[0])/session.scale),
                                    torso_coupling=coupling))
                body.finish(ob,bpy.context.scene,False)
                self.assertEqual(w.raw_pose(ob),source)

        ob,mesh,roles=authored('unity_humanoid',2)
        source=w.raw_pose(ob)
        mesh_data=mesh.data;armature_data=ob.data
        try:
            s=solver.Session(ob);points=feasible_spine(ob,s)
            bpy.context.view_layer.objects.active=ob;body.begin(ob,bpy.context.scene)
            for item in ob.b4ml.body_targets:item.enabled=item.name in {'Pelvis','Spine'}
            ob.b4ml.body_targets['Pelvis'].target.location=points[0]
            ob.b4ml.body_targets['Spine'].target.location=points[1]
            body.solve(ob);session=body._get(ob);actual=session.world_points(session.points())
            self.assertLess(float(np.linalg.norm(actual[1]-points[1]))/session.scale,2e-4)
            self.assertGreaterEqual(body._read(ob)['metrics']['torso_coupling']['rank'],2)
            RECORDS.append(dict(adapter='unity_humanoid_fbx',spine_error_body_scales=float(np.linalg.norm(actual[1]-points[1])/session.scale),
                                pelvis_error_body_scales=float(np.linalg.norm(actual[0]-points[0])/session.scale),
                                torso_coupling=body._read(ob)['metrics']['torso_coupling']))
            body.finish(ob,bpy.context.scene,False)
            self.assertEqual(w.raw_pose(ob),source)
        finally:
            if ob.as_pointer() in solver._SESSIONS:solver._SESSIONS.pop(ob.as_pointer(),None)
            if mesh.name in bpy.data.objects:bpy.data.objects.remove(mesh,do_unlink=True)

    def test_coupled_pelvis_spine_chest_target_on_six_humanoid_adapters(self):
        """Three explicit torso position pins use one bounded coupled chart."""
        from test_b4artists_ml_imported_humanoids import authored

        def feasible_torso(ob,s):
            controls=solver.coupled_torso_controls(s.binding)
            slot=s.binding['rotations'].index(controls[0])
            x=np.zeros(3+3*len(s.q0));x[3+slot*3:6+slot*3]=(.025,-.015,.01)
            s._apply(x);posing._update(ob);points=s.world_points(s.points());s.cancel()
            return points

        for label in self.fixtures.builders:
            with self.subTest(adapter=label):
                ob,source,s,_,_=self.fixtures.fixture(label,transformed=True)
                points=feasible_torso(ob,s)
                bpy.context.view_layer.objects.active=ob;body.begin(ob,bpy.context.scene)
                for item in ob.b4ml.body_targets:item.enabled=item.name in {'Pelvis','Spine','Chest'}
                for index,target_label in ((0,'Pelvis'),(1,'Spine'),(2,'Chest')):
                    ob.b4ml.body_targets[target_label].target.location=points[index]
                try:body.solve(ob)
                except solver.CoupledTorsoError as error:
                    self.fail(f'{label} rejected reachable three-point torso target: {error}')
                session=body._get(ob);actual=session.world_points(session.points())
                record=body._read(ob);coupling=record['metrics']['torso_coupling']
                self.assertLess(float(np.max(np.linalg.norm(actual[:3]-points[:3],axis=1)))/session.scale,2e-4)
                self.assertEqual(coupling['target_count'],3)
                self.assertGreaterEqual(coupling['rank'],3)
                self.assertTrue(np.isfinite(coupling['residual_norm']))
                RECORDS.append(dict(adapter=label,torso_error_body_scales=float(np.max(np.linalg.norm(actual[:3]-points[:3],axis=1))/session.scale),torso_coupling=coupling))
                body.finish(ob,bpy.context.scene,False)
                self.assertEqual(w.raw_pose(ob),source)

        ob,mesh,roles=authored('unity_humanoid',2)
        source=w.raw_pose(ob)
        try:
            s=solver.Session(ob);points=feasible_torso(ob,s)
            bpy.context.view_layer.objects.active=ob;body.begin(ob,bpy.context.scene)
            for item in ob.b4ml.body_targets:item.enabled=item.name in {'Pelvis','Spine','Chest'}
            for index,target_label in ((0,'Pelvis'),(1,'Spine'),(2,'Chest')):
                ob.b4ml.body_targets[target_label].target.location=points[index]
            body.solve(ob);session=body._get(ob);actual=session.world_points(session.points())
            coupling=body._read(ob)['metrics']['torso_coupling']
            self.assertLess(float(np.max(np.linalg.norm(actual[:3]-points[:3],axis=1)))/session.scale,2e-4)
            self.assertEqual(coupling['target_count'],3)
            self.assertGreaterEqual(coupling['rank'],3)
            RECORDS.append(dict(adapter='unity_humanoid_fbx',torso_error_body_scales=float(np.max(np.linalg.norm(actual[:3]-points[:3],axis=1))/session.scale),torso_coupling=coupling))
            body.finish(ob,bpy.context.scene,False)
            self.assertEqual(w.raw_pose(ob),source)
        finally:
            if ob.as_pointer() in solver._SESSIONS:solver._SESSIONS.pop(ob.as_pointer(),None)
            if mesh.name in bpy.data.objects:bpy.data.objects.remove(mesh,do_unlink=True)

    def preview(self,label='boneforge'):
        ob,source,s,targets,mask=self.fixtures.fixture(label,transformed=True)
        points,rotations,poles=self.desired(s);s.cancel()
        bpy.context.view_layer.objects.active=ob;body.begin(ob,bpy.context.scene)
        for index,label in body.TARGETS:
            item=ob.b4ml.body_targets[label];item.target.location=points[index]
            if index in solver.ORIENTATION_JOINTS:
                item.target.rotation_quaternion=rotations[index];item.use_orientation=True
            if index in body.POLE_JOINTS:
                item.pole.location=poles[body.POLE_JOINTS[index]];item.use_pole=True
        bpy.context.view_layer.update()
        return ob,source

    def tearDown(self):
        for ob in list(bpy.data.objects):
            if hasattr(ob,'b4ml') and ob.b4ml.body_payload:
                if ob.users_scene:bpy.context.window.scene=ob.users_scene[0]
                body.finish(ob,bpy.context.scene,False)
        body.reset_runtime()

    def test_preview_reload_keep_and_source_restoration(self):
        ob,source=self.preview('rigify_basic');body.solve(ob);name=ob.name
        record=json.loads(ob.b4ml.body_payload)
        self.assertEqual(record['metrics']['requested_poles'],4)
        self.assertEqual(record['metrics']['requested_orientations'],6)
        path=ROOT/'training/b4artists_ml/cache/body-controls-reload.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path))
        ob=bpy.data.objects[name];bpy.context.view_layer.objects.active=ob
        self.assertTrue(all(i.use_orientation for i in ob.b4ml.body_targets
                            if i.name not in {'Chest','Neck'} and body.target_supports_orientation(i.name)))
        self.assertFalse(ob.b4ml.body_targets['Chest'].use_orientation)
        self.assertFalse(ob.b4ml.body_targets['Neck'].use_orientation)
        body.finish(ob,bpy.context.scene,True)
        self.assertEqual(len(ob.b4ml.anchors),1)
        for n,row in source.items():self.assertEqual(w.raw_pose(ob)[n],row)

    def test_coupled_spine_orientation_with_chest_pin_on_six_humanoid_adapters(self):
        """Spine rotation and three torso pins share one bounded control solve."""
        from test_b4artists_ml_imported_humanoids import authored

        def feasible_goal(ob,s):
            name=solver.orientation_bone(s.binding,1)
            baseline=ob.pose.bones[name].matrix.to_quaternion().copy()
            best=None
            for control in solver.coupled_torso_controls(s.binding):
                slot=s.binding['rotations'].index(control)
                for axis in range(3):
                    x=np.zeros(3+3*len(s.q0));x[3+slot*3+axis]=.08
                    s._apply(x);posing._update(ob)
                    orientation=ob.pose.bones[name].matrix.to_quaternion().copy()
                    angle=solver._angle(baseline,orientation)
                    if best is None or angle>best[0]:
                        best=(angle,x.copy(),s.world_points(s.points()).copy(),orientation)
                    w.restore_pose(ob,s.normalized);posing._update(ob)
            if best is None or best[0]<.02:
                raise AssertionError('No mapped control reaches semantic Spine orientation')
            goal=s.world.to_quaternion()@best[3]
            s.cancel()
            return best[2],goal,best[1]

        labels=os.environ.get('B4ML_SPINE_ORIENTATION_RIGS',
            ','.join((*self.fixtures.builders,'unity_humanoid_fbx'))).split(',')
        for label in labels:
            with self.subTest(adapter=label):
                mesh=None
                if label=='unity_humanoid_fbx':
                    ob,mesh,_=authored('unity_humanoid',2)
                    source=w.raw_pose(ob);s=solver.Session(ob)
                else:
                    ob,source,s,_,_=self.fixtures.fixture(label,transformed=True)
                try:
                    points,goal,source_parameters=feasible_goal(ob,s)
                    bpy.context.view_layer.objects.active=ob
                    body.begin(ob,bpy.context.scene)
                    for item in ob.b4ml.body_targets:
                        item.enabled=item.name in {'Pelvis','Spine','Chest'}
                    for index,label_name in ((0,'Pelvis'),(1,'Spine'),(2,'Chest')):
                        ob.b4ml.body_targets[label_name].target.location=points[index]
                    spine=ob.b4ml.body_targets['Spine']
                    spine.use_orientation=True
                    spine.target.rotation_quaternion=goal
                    bpy.context.view_layer.update()
                    request=body._request(ob,body._get(ob))
                    request_orientation_error=solver._angle(Quaternion(request[3][1]),goal)
                    self.assertLess(request_orientation_error,.001)
                    request_position_error=float(np.max(np.linalg.norm(request[0][:3]-points[:3],axis=1)))
                    self.assertLess(request_position_error,1e-6)
                    session=body._get(ob)
                    session._apply(source_parameters);posing._update(ob)
                    replay_points=session.world_points(session.points())
                    replay_orientation=(session.world.to_quaternion()
                        @ob.pose.bones[solver.orientation_bone(session.binding,1)].matrix.to_quaternion())
                    self.assertLess(float(np.max(np.linalg.norm(replay_points[:3]-points[:3],axis=1)))/session.scale,2e-4)
                    self.assertLess(solver._angle(goal,replay_orientation),.001)
                    w.restore_pose(ob,session.normalized);posing._update(ob)
                    body.solve(ob)
                    actual=session.world_points(session.points())
                    actual_orientation=(session.world.to_quaternion()
                        @ob.pose.bones[solver.orientation_bone(session.binding,1)].matrix.to_quaternion())
                    record=body._read(ob)['metrics'];coupling=record['torso_coupling']
                    self.assertLess(float(np.max(np.linalg.norm(actual[:3]-points[:3],axis=1)))/session.scale,2e-4)
                    self.assertLess(solver._angle(goal,actual_orientation),.001)
                    self.assertLess(record['orientation_error_radians'],.001)
                    self.assertEqual(coupling['target_count'],3)
                    self.assertEqual(coupling['orientation_joint'],1)
                    self.assertTrue(np.isfinite(coupling['residual_norm']))
                    RECORDS.append(dict(adapter=label,spine_orientation_error_radians=solver._angle(goal,actual_orientation),
                                        request_orientation_error_radians=request_orientation_error,
                                        request_position_error=request_position_error,
                                        torso_error_body_scales=float(np.max(np.linalg.norm(actual[:3]-points[:3],axis=1))/session.scale),
                                        torso_coupling=coupling))
                    body.finish(ob,bpy.context.scene,False)
                    self.assertEqual(w.raw_pose(ob),source)
                finally:
                    if hasattr(ob,'b4ml') and ob.b4ml.body_payload:
                        body.finish(ob,bpy.context.scene,False)
                    if ob.as_pointer() in solver._SESSIONS:
                        active=solver._SESSIONS.get(ob.as_pointer())
                        if active is not None and not active.closed:active.cancel()
                    if mesh is not None and mesh.name in bpy.data.objects:
                        bpy.data.objects.remove(mesh,do_unlink=True)

    def test_spine_orientation_rejects_missing_spine_position_pin(self):
        ob,source,s,targets,_=self.fixtures.fixture('boneforge',transformed=True)
        try:
            points=s.world_points(s.points())
            orientation=(s.world.to_quaternion()
                @ob.pose.bones[solver.orientation_bone(s.binding,1)].matrix.to_quaternion())
            mask=np.zeros(17,dtype=bool);mask[0]=True
            with self.assertRaisesRegex(solver.CoupledTorsoError,'requires pinned Pelvis and Spine positions'):
                s.solve(points,mask,orientations_world={1:list(orientation)})
            self.assertEqual(w.raw_pose(ob),source)
        finally:s.cancel()

    def test_rotated_or_moved_poles_require_resolve(self):
        ob,source=self.preview();body.solve(ob)
        item=ob.b4ml.body_targets['Hand L'];q=item.target.rotation_quaternion.copy()
        item.target.rotation_quaternion=q@Quaternion((0,1,0),.1);bpy.context.view_layer.update()
        with self.assertRaisesRegex(ValueError,'Solve the current targets'):body.finish(ob,bpy.context.scene,True)
        item.target.rotation_quaternion=q;point=item.pole.location.copy();item.pole.location.x+=.05
        bpy.context.view_layer.update()
        with self.assertRaisesRegex(ValueError,'Solve the current targets'):body.finish(ob,bpy.context.scene,True)
        item.pole.location=point;bpy.context.view_layer.update()
        body.finish(ob,bpy.context.scene,True)

    def test_partial_solve_cancel_restores_previous_controls(self):
        ob,source=self.preview('rigify_basic');body.solve(ob);before=w.raw_pose(ob)
        body.start(ob);body.step(ob);body.abort(ob)
        self.assertEqual(w.raw_pose(ob),before)
        self.assertFalse(any(s.name.startswith('B4ML private evaluation') for s in bpy.data.scenes))

    def test_invalid_requests_do_not_change_controls(self):
        ob,source,s,targets,mask=self.fixtures.fixture('boneforge');before=w.raw_pose(ob)
        try:
            for rotations,poles in (({0:[0,0,0,0]},{}),({1:[1,0,0,0]},{}),({7:[float('nan'),0,0,0]},{}),({},{6:[float('inf'),0,0]}),({},{7:[0,0,0]})):
                with self.assertRaises(ValueError):s.solve(targets,mask,orientations_world=rotations,pole_targets=poles)
                self.assertEqual(w.raw_pose(ob),before)
        finally:s.cancel()

    def test_actual_0_5_1_preview_remains_keepable(self):
        path=ROOT/'training/b4artists_ml/cache/body-controls-legacy-0.5.1.blend'
        self.assertTrue(path.exists(),'Build the legacy fixture with the retained 0.5.1 ZIP first')
        bpy.ops.wm.open_mainfile(filepath=str(path))
        ob=next(o for o in bpy.data.objects if hasattr(o,'b4ml') and o.b4ml.body_payload)
        bpy.context.view_layer.objects.active=ob
        self.assertNotIn('controls_version',json.loads(ob.b4ml.body_payload))
        self.assertTrue(all(not i.use_orientation and not i.use_pole for i in ob.b4ml.body_targets))
        body.finish(ob,bpy.context.scene,True)
        self.assertEqual(len(ob.b4ml.anchors),1)


    def test_rotation_can_be_selected_without_position_pin(self):
        ob,source,s,targets,mask=self.fixtures.fixture('boneforge');s.cancel()
        bpy.context.view_layer.objects.active=ob;body.begin(ob,bpy.context.scene)
        for index,label in body.TARGETS:ob.b4ml.body_targets[label].target.location=targets[index]
        item=ob.b4ml.body_targets['Head'];item.enabled=False;item.use_orientation=True
        goal=item.target.rotation_quaternion.copy()@Quaternion((0,0,1),.35)
        item.target.rotation_quaternion=goal;item.target.location.x+=100
        bpy.context.view_layer.update()
        ob.b4ml.body_strength=0.
        request=body._request(ob,body._get(ob))
        self.assertLess(solver._angle(Quaternion(request[3][4]),body._world_orientation(body._get(ob),4)),1e-5)
        self.assertFalse(request[1][4]);self.assertFalse(request[4])
        ob.b4ml.body_strength=1.;body.solve(ob)
        session=body._get(ob);name=session.binding['effectors'][0]
        self.assertLess(solver._angle(goal,ob.matrix_world.to_quaternion()@ob.pose.bones[name].matrix.to_quaternion()),.001)
        metrics=json.loads(ob.b4ml.body_payload)['metrics']
        self.assertEqual(metrics['requested_orientations'],1);self.assertEqual(metrics['requested_poles'],0)

    def test_edit_during_solve_restores_last_verified_preview(self):
        ob,source=self.preview('metarig_basic');body.solve(ob);before=w.raw_pose(ob)
        body.start(ob);body.step(ob)
        ob.b4ml.body_targets['Head'].target.rotation_quaternion.rotate(Quaternion((0,0,1),.2))
        bpy.context.view_layer.update()
        with self.assertRaisesRegex(ValueError,'Targets changed during solving'):
            while not body.step(ob):pass
        self.assertEqual(w.raw_pose(ob),before);self.assertFalse(ob.b4ml.body_running)


if __name__=='__main__':
    selection=os.environ.get('B4ML_CONTROL_TEST')
    suite=unittest.defaultTestLoader.loadTestsFromName(selection,sys.modules[__name__]) if selection else unittest.defaultTestLoader.loadTestsFromTestCase(BodyControlTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report=dict(tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),errors=len(result.errors),records=RECORDS,package=b4artists_ml.__file__)
    (ROOT/'training/b4artists_ml/results'/os.environ.get('B4ML_CONTROL_RESULT','body-controls-v1.json')).write_text(json.dumps(report,indent=2)+'\n')
    print('BODY_CONTROLS_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
