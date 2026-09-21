"""Signed bend-plane fitting and calibration on actual humanoid rigs."""
from pathlib import Path
import sys,os,json,math,unittest,time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy,numpy as np
from mathutils import Quaternion
import b4artists_ml
from b4artists_ml import body_solver as solver,body_preview as body,joint_limits as limits,joint_frames as frames,workflow as w,posing as p
from test_b4artists_ml_joint_limits import LimitTests,bound
RECORDS=[]


def plane(axis=0.,minimum=.15,maximum=.6,sideways=.06):
    return dict(axis=axis,minimum=minimum,maximum=maximum,sideways=sideways)


def author_joint(s,name,q):
    pair=frames.bind(s.obj,s.binding)[name];ob=s.obj
    wanted=ob.pose.bones[pair[1]].matrix.to_quaternion()@frames.rest_relative(ob,pair)@q
    actual=ob.pose.bones[pair[0]].matrix.to_quaternion()
    target=wanted@actual.inverted()@ob.pose.bones[name].matrix.to_quaternion()
    matrix=target.to_matrix().to_4x4();matrix.translation=ob.pose.bones[name].head
    p._write_rotation(ob,name,matrix)


def feasible(s,calibrate_ui=False):
    rng=np.random.default_rng(622)
    x=rng.normal(0,.04,3+3*len(s.q0));x[:3]*=.1;s._apply(x)
    _,_,limbs=p.bindings(s.obj);request={}
    for row in limbs:
        axis=.45 if row['id'].endswith('L') else -.65
        name=row['fk'][1];q=Quaternion((math.cos(axis),0,math.sin(axis)),.35)
        author_joint(s,name,q)
        request[name]=dict(bound(1.4),space='JOINT',bend=plane(axis))
        if calibrate_ui:
            state=s.obj.b4ml;item=state.body_limits[name];item.enabled=True;item.space='JOINT';item.use_bend_plane=True
            item.swing=1.4;item.bend_min=.15;item.bend_max=.6;item.bend_sideways=.06
            state.body_limit_control=name
            assert bpy.ops.b4ml.body(operation='CALIBRATE_BEND')=={'FINISHED'}
            assert abs(item.bend_axis-axis)<1e-4
    points=s.world_points(s.points());rotation={0:list(s.world.to_quaternion()@s.obj.pose.bones[s.binding['names'][0]].matrix.to_quaternion())}
    for index,name in zip(solver.ORIENTATION_JOINTS[1:],s.binding['effectors']):rotation[index]=list(s.world.to_quaternion()@s.obj.pose.bones[name].matrix.to_quaternion())
    poles={index:points[index].copy() for index in solver.POLE_CHAINS}
    w.restore_pose(s.obj,s.normalized);p._update(s.obj)
    return points,rotation,poles,request


class BendTests(LimitTests):
    def test_signed_swing_decomposition_and_asymmetric_bounds(self):
        for axis in (-2.,-.7,0.,.8,2.8):
            for angle in (.001,.4,1.5,3.):
                for twist in (-2.,0.,2.):
                    q=Quaternion((math.cos(axis),0,math.sin(axis)),angle)@Quaternion((0,1,0),twist)
                    np.testing.assert_allclose(limits.swing_vector(q),[angle*math.cos(axis),angle*math.sin(axis)],atol=1e-6)
                    np.testing.assert_allclose(limits.bend_coordinates(q,axis),[angle,0.],atol=1e-6)
                    limit=dict(bound(3.1),bend=plane(axis))
                    np.testing.assert_allclose(limits.residual(q,limit),limits.residual(-np.array(q),limit),atol=1e-7)
        limit=dict(bound(2.),bend=plane(0.,0.,1.,.05))
        self.assertLess(np.max(np.abs(limits.residual(Quaternion((1,0,0),.4),limit))),1e-6)
        self.assertAlmostEqual(limits.residual(Quaternion((1,0,0),-.4),limit)[2],-.4,places=6)
        self.assertAlmostEqual(limits.residual(Quaternion((0,0,1),.4),limit)[3],.35,places=6)

    def test_invalid_plane_requests_do_not_mutate(self):
        ob,source,s,targets,mask=self.fixtures.fixture('boneforge');before=w.raw_pose(ob);name=s.binding['effectors'][0]
        for value in (dict(bound(1.),bend=plane(float('nan'))),dict(bound(1.),bend=plane(minimum=1.,maximum=-1.)),dict(bound(1.),bend=plane(sideways=-.1)),dict(bound(math.pi),bend=plane()),dict(bound(1.),bend={})):
            with self.assertRaises(ValueError):s.solve(targets,mask,rotation_limits={name:value})
            self.assertEqual(before,w.raw_pose(ob))

    def test_active_directional_bounds_on_five_rigs(self):
        for label in self.fixtures.builders:
            with self.subTest(rig=label):
                ob,source,s,targets,mask=self.fixtures.fixture(label,transformed=True)
                targets=s.world_points(s.baseline);mask[:]=False;mask[0]=True
                _,_,rows=p.bindings(ob);mapping=frames.bind(ob,s.binding)
                request={row['fk'][1]:dict(bound(1.4),space='JOINT',bend=plane(.45 if row['id'].endswith('L') else -.65)) for row in rows}
                s.solve(targets,mask,iterations=80)
                original={n:limits.bend_coordinates(frames.rotation(ob,mapping[n],frames.rest_relative(ob,mapping[n])),v['bend']['axis']).tolist() for n,v in request.items()}
                self.assertTrue(any(f<.15 or f>.6 or abs(side)>.06 for f,side in original.values()))
                result=s.solve(targets,mask,iterations=100,rotation_limits=request)
                measured={n:limits.bend_coordinates(frames.rotation(ob,mapping[n],frames.rest_relative(ob,mapping[n])),v['bend']['axis']).tolist() for n,v in request.items()}
                for f,side in measured.values():self.assertGreaterEqual(f,.149);self.assertLessEqual(f,.601);self.assertLessEqual(abs(side),.061)
                self.assertEqual(result['requested_bend_planes'],4)
                RECORDS.append(dict(case='active_bend_planes',fixture=label,before=original,after=measured,**{k:v for k,v in result.items() if k!='points'}));s.cancel()

    def test_feasible_combined_pins_poles_rotations_and_planes(self):
        for label in self.fixtures.builders:
            with self.subTest(rig=label):
                ob,source,s,targets,mask=self.fixtures.fixture(label,transformed=True)
                targets,rotations,poles,request=feasible(s)
                result=s.solve(targets,mask,iterations=100,orientations_world=rotations,pole_targets=poles,rotation_limits=request)
                self.assertLess(result['pin_error'],2e-4);self.assertLess(result['joint_limit_error_radians'],.001)
                self.assertLess(result['pole_error_radians'],.01)
                RECORDS.append(dict(case='combined_bend_planes',fixture=label,**{k:v for k,v in result.items() if k!='points'}));s.cancel()

    def test_calibration_uses_actual_pose_and_preserves_controls(self):
        for label in ('boneforge','rigify_default','metarig_basic'):
            ob,source,s,targets,mask=self.fixtures.fixture(label);s.cancel()
            bpy.context.view_layer.objects.active=ob;body.begin(ob,bpy.context.scene);s=body._get(ob)
            _,_,rows=p.bindings(ob)
            for row in rows:
                name=row['fk'][1];axis=.6 if row['id'].endswith('L') else -.8
                item=ob.b4ml.body_limits[name];item.space='JOINT';ob.b4ml.body_limit_control=name
                author_joint(s,name,Quaternion((math.cos(axis),0,math.sin(axis)),.4));before=w.raw_pose(ob)
                self.assertAlmostEqual(body.calibrate_bend_axis(ob),axis,places=4)
                self.assertEqual(before,w.raw_pose(ob))
            name=rows[0]['fk'][1];ob.b4ml.body_limit_control=name
            author_joint(s,name,Quaternion());before=w.raw_pose(ob);previous=ob.b4ml.body_limits[name].bend_axis
            with self.assertRaisesRegex(ValueError,'at least 5 degrees'):body.calibrate_bend_axis(ob)
            self.assertEqual(before,w.raw_pose(ob));self.assertEqual(previous,ob.b4ml.body_limits[name].bend_axis)
            body.finish(ob,bpy.context.scene,False)

    def test_directional_settings_reload_cancel_and_stale(self):
        ob,source,s,targets,mask=self.fixtures.fixture('boneforge');s.cancel()
        bpy.context.view_layer.objects.active=ob;body.begin(ob,bpy.context.scene);s=body._get(ob)
        points,rotations,poles,request=feasible(s,calibrate_ui=True)
        for index,label in body.TARGETS:
            item=ob.b4ml.body_targets[label];item.target.location=points[index]
            if index in solver.ORIENTATION_JOINTS:item.target.rotation_quaternion=rotations[index];item.use_orientation=True
            if index in body.POLE_JOINTS:item.pole.location=poles[body.POLE_JOINTS[index]];item.use_pole=True
        p._update(ob);body.solve(ob);before=w.raw_pose(ob)
        body.start(ob);body.step(ob)
        with self.assertRaisesRegex(ValueError,'running solve'):body.calibrate_bend_axis(ob)
        body.abort(ob);self.assertEqual(before,w.raw_pose(ob))
        path=ROOT/'training/b4artists_ml/cache/bend-limits-reload.blend';name=ob.name
        bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path))
        ob=bpy.data.objects[name];bpy.context.view_layer.objects.active=ob
        item=next(i for i in ob.b4ml.body_limits if i.use_bend_plane);old=item.bend_sideways;item.bend_sideways=.3
        with self.assertRaisesRegex(ValueError,'Solve the current targets'):body.finish(ob,bpy.context.scene,True)
        item.bend_sideways=old;body.finish(ob,bpy.context.scene,True);self.assertEqual(len(ob.b4ml.anchors),1)
        for n,row in source.items():self.assertEqual(w.raw_pose(ob)[n],row)

    def test_mixed_residual_widths_report_correct_conflicting_control(self):
        ob,source,s,targets,mask=self.fixtures.fixture('boneforge');s.solve(targets,mask);before=w.raw_pose(ob)
        name=s.binding['effectors'][0]
        # A zero swing cone cannot reach the strictly positive forward interval.
        request={s.binding['rotations'][0]:bound(1.5),name:dict(bound(0.),space='JOINT',bend=plane(minimum=1.,maximum=1.1,sideways=0.))}
        with self.assertRaisesRegex(ValueError,'Joint limits conflict.*'+name):s.solve(targets,mask,rotation_limits=request,iterations=20)
        self.assertEqual(before,w.raw_pose(ob))

    def test_control_space_calibration_and_directional_preview(self):
        for label in ('boneforge','rigify_default'):
            ob,source,s,targets,mask=self.fixtures.fixture(label);s.cancel()
            bpy.context.view_layer.objects.active=ob;body.begin(ob,bpy.context.scene)
            _,_,rows=p.bindings(ob);name=next(row['fk'][1] for row in rows if row['id']=='arm-R')
            item=ob.b4ml.body_limits[name];self.assertEqual(item.space,'CONTROL')
            item.enabled=True;item.use_bend_plane=True;item.swing=1.4;item.bend_min=.2;item.bend_max=.5;item.bend_sideways=.04
            ob.b4ml.body_limit_control=name;axis=-.65
            solver._set_quat(ob.pose.bones[name],Quaternion((math.cos(axis),0,math.sin(axis)),.4));p._update(ob)
            self.assertAlmostEqual(body.calibrate_bend_axis(ob),axis,places=5)
            for target in ob.b4ml.body_targets:target.enabled=target.name=='Pelvis'
            body.solve(ob)
            f,side=limits.bend_coordinates(solver._quat(ob.pose.bones[name]),item.bend_axis)
            self.assertGreaterEqual(f,.199);self.assertLessEqual(f,.501);self.assertLessEqual(abs(side),.041)
            metrics=json.loads(ob.b4ml.body_payload)['metrics'];self.assertEqual(metrics['requested_skeletal_limits'],0)
            self.assertEqual(metrics['requested_bend_planes'],1)
            RECORDS.append(dict(case='control_space_plane',fixture=label,forward=f,sideways=side,**metrics))
            body.finish(ob,bpy.context.scene,True);self.assertEqual(len(ob.b4ml.anchors),1)
            for n,row in source.items():self.assertEqual(w.raw_pose(ob)[n],row)

    def test_actual_0_8_skeletal_preview_remains_keepable(self):
        path=ROOT/'training/b4artists_ml/cache/bend-limits-legacy-v0.8.0.blend'
        self.assertTrue(path.exists(),'Build this fixture using the actual retained 0.8.0 ZIP')
        bpy.ops.wm.open_mainfile(filepath=str(path))
        ob=next(o for o in bpy.data.objects if hasattr(o,'b4ml') and o.b4ml.body_payload)
        bpy.context.view_layer.objects.active=ob
        request=json.loads(ob.b4ml.body_payload)['signature']['joint_limits']
        self.assertTrue(any(v.get('space')=='JOINT' for v in request.values()))
        self.assertTrue(all('bend' not in v for v in request.values()))
        self.assertTrue(all(not i.use_bend_plane for i in ob.b4ml.body_limits))
        body.finish(ob,bpy.context.scene,True);self.assertEqual(len(ob.b4ml.anchors),1)

    def test_singular_swing_does_not_pass_narrow_twist_or_plane(self):
        q=Quaternion((1,0,0),math.pi)
        for value in (bound(math.pi-2e-5,-.1,.1),dict(bound(math.pi-2e-5),bend=plane())):
            self.assertGreater(np.max(np.abs(limits.residual(q,value))),.001)
        with self.assertRaisesRegex(ValueError,'reversed'):limits.swing_vector(q)


def run_ui_smoke():
    import test_b4artists_ml_context_preview as preview_tests
    from test_b4artists_ml_body_controls import BodyControlTests
    os.environ['B4ML_UI_RIG']='rigify_default';os.environ['B4ML_UI_CONTROLS']='1'
    original_step=body.step;step_ms=[]
    def desired(test,s):
        points,rotations,poles,request=feasible(s,calibrate_ui=True)
        s.obj.b4ml.show_body_limits=True;s.obj.b4ml.show_body_targets=False
        s.obj.b4ml.body_limit_control=next(iter(request))
        return points,rotations,poles
    def checked_step(ob):
        started=time.perf_counter()
        try:done=original_step(ob)
        finally:step_ms.append((time.perf_counter()-started)*1000)
        if done:
            record=json.loads(ob.b4ml.body_payload)
            assert record['metrics']['requested_bend_planes']==4
            assert record['metrics']['requested_skeletal_limits']==4
            assert record['metrics']['joint_limit_error_radians']<.001
            version='.'.join(map(str,b4artists_ml.bl_info['version']))
            timing=dict(package=b4artists_ml.__file__,step_count=len(step_ms),p50_ms=float(np.percentile(step_ms,50)),p95_ms=float(np.percentile(step_ms,95)),max_ms=max(step_ms),step_ms=step_ms)
            (ROOT/f'training/b4artists_ml/results/bend-ui-timing-v{version}.json').write_text(json.dumps(timing,indent=2)+'\n')
        return done
    BodyControlTests.desired=desired;body.step=checked_step
    preview_tests.run_ui_smoke()


if __name__=='__main__' and '--ui-smoke' in sys.argv:run_ui_smoke()
elif __name__=='__main__':
    selection=os.environ.get('B4ML_BEND_TEST');names=[n for n in BendTests.__dict__ if n.startswith('test_')]
    suite=unittest.defaultTestLoader.loadTestsFromName(selection,sys.modules[__name__]) if selection else unittest.TestSuite(BendTests(n) for n in names)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report=dict(tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),errors=len(result.errors),records=RECORDS,package=b4artists_ml.__file__)
    (ROOT/'training/b4artists_ml/results'/os.environ.get('B4ML_BEND_RESULT','bend-limits-v1.json')).write_text(json.dumps(report,indent=2)+'\n')
    print('BEND_LIMIT_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
