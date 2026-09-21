"""Static balance correction, pins, limits, preview recovery and real rig fixtures."""
from pathlib import Path
import os,sys,json,unittest,math,time,copy
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]
import bpy,numpy as np
from mathutils import Quaternion,Vector
import b4artists_ml
from b4artists_ml import balance,support,body_solver as solver,body_preview as body,posing as p,workflow as w,rig_state as rs
from test_b4artists_ml_support import fixture,point_contact,snapshot_rig,BUILDERS
RECORDS=[]


def unbalanced(label='boneforge',transformed=False):
    ob,scene=fixture(label);ob.b4ml.mass_segments[4].weight=60.
    name='chest' if label=='boneforge' or label.startswith('rigify') else 'spine.003'
    pb=ob.pose.bones[name];solver._set_quat(pb,solver._quat(pb)@Quaternion((1,0,0),.35));p._update(ob)
    for limb in ('leg-L','leg-R'):
        item=point_contact(ob,scene,limb);item.support_width=.08;item.support_length=.06
    ob.b4ml.body_balance=True;ob.b4ml.body_balance_free_pelvis=True;ob.b4ml.body_balance_inset=.005
    if transformed:
        # Rotate the full scene coordinate description, not the rig relative to fixed gravity.
        q=Quaternion((1,1,1),.6);shift=Vector((2,-1,.3));scale=1.7
        for item in ob.b4ml.contacts:
            item.point=shift+q@Vector(item.point)*scale;item.rotation=q@Quaternion(item.rotation)
            item.support_width*=scale;item.support_length*=scale
            normal,u,v=support.sm.plane_basis(q@Vector((0,0,1)));axis=np.array(q@Vector((1,0,0)))
            item.support_heading=math.atan2(float(axis@v),float(axis@u))
        ob.location=shift;ob.rotation_mode='QUATERNION';ob.rotation_quaternion=q;ob.scale=(scale,)*3
        ob.b4ml.support_plane_point=shift;ob.b4ml.support_plane_normal=q@Vector((0,0,1))
        scene.gravity=q@scene.gravity;ob.b4ml.body_balance_inset*=scale;ob.b4ml.support_tolerance*=scale;p._update(ob)
    return ob,scene


def begin(ob,scene):
    body.begin(ob,scene);ob.b4ml.body_influence=0.
    for item in ob.b4ml.body_targets:item.enabled=item.name in ('Pelvis','Foot L','Foot R')


class BalanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):b4artists_ml.register()
    def tearDown(self):
        for obj in list(bpy.data.objects):
            if hasattr(obj,'b4ml') and obj.b4ml.body_payload:
                bpy.context.window.scene=obj.users_scene[0];body.finish(obj,bpy.context.scene,False)
        for session in list(solver._SESSIONS.values()):
            if not session.closed:bpy.context.window.scene=session.obj.users_scene[0];session.cancel()
        body.reset_runtime()

    def test_five_rigs_correct_com_preserve_support_and_bound_mesh(self):
        for label in BUILDERS:
            with self.subTest(rig=label):
                ob,scene=unbalanced(label);root=p.bindings(ob)[1]
                ob.pose.bones[root].keyframe_insert('location',frame=1);source=snapshot_rig(ob)
                begin(ob,scene);s=body._get(ob);before=support.analyze(ob,scene,bpy.context.evaluated_depsgraph_get())
                self.assertLess(before['margin'],-.01)
                joint='hand.def-L' if label=='boneforge' else 'DEF-hand.L' if label.startswith('rigify') else 'hand.L'
                data=bpy.data.meshes.new('Balance mesh');point=ob.data.bones[joint].head_local.copy()
                data.from_pydata([point,point+Vector((.01,0,0)),point+Vector((0,.01,0))],[],[(0,1,2)])
                mesh=bpy.data.objects.new('Balance mesh',data);scene.collection.objects.link(mesh)
                mesh.vertex_groups.new(name=joint).add([0,1,2],1.,'REPLACE');mesh.modifiers.new('Armature','ARMATURE').object=ob
                steps=[];body.start(ob)
                while ob.b4ml.body_running:
                    t=time.perf_counter();body.step(ob);steps.append((time.perf_counter()-t)*1000)
                result=json.loads(ob.b4ml.body_payload)['metrics'];m=result['balance']
                self.assertLess(m['com_error'],2e-4);self.assertLess(m['contact_error'],2e-4);self.assertLess(m['contact_rotation_error'],.001)
                self.assertGreater(m['after_margin'],.0048);self.assertGreater(m['after_margin']-m['before_margin'],.01)
                self.assertLess(result['pin_error'],2e-4);self.assertLess(result['length_error'],.002)
                actual=support.analyze(ob,scene,bpy.context.evaluated_depsgraph_get())
                np.testing.assert_allclose(actual['com'],m['after_com'],atol=1e-7)
                evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
                expected=ob.pose.bones[joint].matrix@ob.data.bones[joint].matrix_local.inverted()@point
                self.assertLess((evaluated.data.vertices[0].co-expected).length,1e-5)
                RECORDS.append(dict(rig=label,metrics=result,step_p95_ms=float(np.percentile(steps,95)),step_max_ms=max(steps),steps=len(steps)))
                body.finish(ob,scene,True);self.assertEqual(len(ob.b4ml.anchors),1)
                restored=snapshot_rig(ob)
                for key in ('pose','modes','world','curves','constraints','rest','action','slot'):self.assertEqual(source[key],restored[key])

    def test_strength_repeats_and_zero_restore_original_geometric_request(self):
        ob,scene=unbalanced();begin(ob,scene);ob.b4ml.body_balance_strength=.5
        body.solve(ob);first=json.loads(ob.b4ml.body_payload)['metrics']['balance'];pose=w.raw_pose(ob)
        self.assertLess(first['after_margin'],0);self.assertGreater(first['after_margin'],first['before_margin'])
        body.solve(ob);second=json.loads(ob.b4ml.body_payload)['metrics']['balance']
        np.testing.assert_allclose(first['target_projection'],second['target_projection'],atol=1e-12)
        self.assertEqual(pose,w.raw_pose(ob))
        ob.b4ml.body_balance_strength=0;body.solve(ob);result=json.loads(ob.b4ml.body_payload)['metrics']
        self.assertIsNone(result['balance']);s=body._get(ob)
        np.testing.assert_allclose(s.points(),s.baseline,atol=2e-4)

    def test_capture_point_balance_keeps_predicted_point_inside_support(self):
        ob,scene=unbalanced();begin(ob,scene)
        ob.b4ml.body_balance_dynamic=True
        ob.b4ml.body_balance_velocity=(.12,.0,.0)
        body.solve(ob)
        metrics=json.loads(ob.b4ml.body_payload)['metrics']['balance']
        self.assertEqual(metrics['schema'],2)
        self.assertTrue(metrics['dynamic'])
        self.assertFalse(metrics['static_only'])
        self.assertLess(metrics['capture_error'],2e-4)
        self.assertGreater(metrics['after_margin'],.0048)
        self.assertGreater(metrics['time_constant'],0.)
        body.finish(ob,scene,False)

    def test_immutable_requests_cancellation_and_incompatible_pins(self):
        ob,scene=unbalanced();begin(ob,scene);before=w.raw_pose(ob)
        body.start(ob);self.assertFalse(body.step(ob));body.abort(ob);self.assertEqual(before,w.raw_pose(ob))
        body.solve(ob);before=w.raw_pose(ob);report=ob.b4ml.body_payload
        original_location=ob.b4ml.body_targets.get('Foot L').target.location.copy()
        ob.b4ml.body_targets.get('Foot L').target.location.x+=.05
        with self.assertRaisesRegex(ValueError,'Pinned target conflicts'):body.solve(ob)
        self.assertEqual(before,w.raw_pose(ob));self.assertEqual(report,ob.b4ml.body_payload)
        ob.b4ml.body_targets.get('Foot L').target.location=original_location
        original_mass=ob.b4ml.mass_segments[4].weight;ob.b4ml.mass_segments[4].weight+=1.
        with self.assertRaisesRegex(ValueError,'Solve the current targets'):body.finish(ob,scene,True)
        ob.b4ml.mass_segments[4].weight=original_mass
        body.solve(ob);before=w.raw_pose(ob);body.start(ob)
        ob.b4ml.mass_segments[4].weight+=1.
        with self.assertRaisesRegex(ValueError,'Targets changed'):
            while not body.step(ob):pass
        self.assertEqual(before,w.raw_pose(ob))

    def test_conflicting_fixed_body_rolls_back(self):
        ob,scene=unbalanced();begin(ob,scene);ob.b4ml.body_balance_free_pelvis=False
        # Lock all writable rotation DOFs to the current pose; root position stays pinned.
        # Head/hand/foot rotations remain their original orientations.
        s=body._get(ob);targets=s.world_points(s.baseline);mask=np.ones(17,bool);before=w.raw_pose(ob)
        with self.assertRaises(ValueError):s.solve(targets,mask,learned_influence=0.,iterations=40,balance=balance.request(ob,scene))
        self.assertEqual(before,w.raw_pose(ob))

    def test_enabled_joint_limits_and_orientation_pins(self):
        ob,scene=unbalanced('rigify_basic');begin(ob,scene)
        head=ob.b4ml.body_targets.get('Head');head.use_orientation=True
        item=ob.b4ml.body_limits.get('head');item.enabled=True;item.swing=2.;item.twist_min=-2.;item.twist_max=2.;item.space='JOINT'
        body.solve(ob);metrics=json.loads(ob.b4ml.body_payload)['metrics']
        self.assertLess(metrics['joint_limit_error_radians'],.001);self.assertLess(metrics['orientation_error_radians'],.001)
        self.assertLess(metrics['balance']['com_error'],2e-4)

    def test_balance_with_learned_proposal(self):
        for label in ('boneforge','rigify_basic'):
            ob,scene=unbalanced(label);begin(ob,scene);ob.b4ml.body_influence=1.
            body.solve(ob);metrics=json.loads(ob.b4ml.body_payload)['metrics']
            self.assertGreater(metrics['neural_residual_norm'],.01)
            self.assertLess(metrics['balance']['com_error'],2e-4)
            self.assertLess(metrics['pin_error'],2e-4)
            self.assertGreater(metrics['balance']['after_margin'],.0048)
            body.finish(ob,scene,False)

    def test_pelvis_pin_retained_when_spine_can_correct_balance(self):
        ob,scene=unbalanced();begin(ob,scene);ob.b4ml.body_balance_free_pelvis=False
        session=body._get(ob);start=session.world_points(session.baseline)[0]
        body.solve(ob);metrics=json.loads(ob.b4ml.body_payload)['metrics']
        actual=session.world_points(session.points())[0]
        self.assertLess(np.linalg.norm(actual-start)/session.scale,2e-4)
        self.assertFalse(metrics['balance']['free_pelvis']);self.assertGreater(metrics['balance']['after_margin'],.0048)

    def test_legacy_v11_preview_recovers_without_balance(self):
        path=ROOT/'training/b4artists_ml/cache/body-preview-v0.11.0-for-balance.blend'
        self.assertTrue(path.is_file(),'Create the authentic released 0.11.0 fixture first')
        bpy.ops.wm.open_mainfile(filepath=str(path));ob=next(o for o in bpy.data.objects if o.type=='ARMATURE' and o.b4ml.body_payload)
        record=json.loads(ob.b4ml.body_payload);self.assertNotIn('balance_reference',record['session'])
        self.assertFalse(ob.b4ml.body_balance);body.solve(ob);before=w.raw_pose(ob)
        ob.b4ml.body_balance=True
        with self.assertRaisesRegex(ValueError,'Start a new whole-body preview'):body.solve(ob)
        self.assertEqual(before,w.raw_pose(ob));ob.b4ml.body_balance=False
        body.finish(ob,bpy.context.scene,True);self.assertEqual(len(ob.b4ml.anchors),1)

    def test_frame_gravity_mass_and_contact_validation_precede_writes(self):
        ob,scene=unbalanced();s=solver.Session(ob);targets=s.world_points(s.baseline);mask=np.zeros(17,bool);mask[[0,13,16]]=True
        good=balance.request(ob,scene);before=w.raw_pose(ob)
        cases=[]
        for key,value in (('gravity',[0,0,0]),('gravity',[1,0,-9]),('frame',4),('inset',100),('contacts',[]),('strength',float('nan'))):
            bad=copy.deepcopy(good);bad[key]=value;cases.append(bad)
        bad=copy.deepcopy(good);bad['masses'][0]['weight']=-1;cases.append(bad)
        bad=copy.deepcopy(good);bad['contacts'][0]['strength']=.4;cases.append(bad)
        for bad in cases:
            with self.assertRaises(ValueError):s.solve(targets,mask,learned_influence=0.,balance=bad)
            self.assertEqual(before,w.raw_pose(ob))
        self.assertTrue(mask[0]);np.testing.assert_array_equal(targets,s.world_points(s.baseline))

    def test_transformed_reference_and_save_reload_recovery(self):
        ob,scene=unbalanced('rigify_basic',transformed=True);begin(ob,scene);body.solve(ob)
        name=ob.name;before=json.loads(ob.b4ml.body_payload)['metrics']['balance'];record=json.loads(ob.b4ml.body_payload)
        path=ROOT/'training/b4artists_ml/cache/balance-roundtrip-v1.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(path))
        ob=bpy.data.objects[name];scene=bpy.context.scene;body.solve(ob)
        after=json.loads(ob.b4ml.body_payload)['metrics']['balance'];np.testing.assert_allclose(before['target_projection'],after['target_projection'],atol=1e-9)
        self.assertGreater(after['after_margin'],.004*1.7);body.finish(ob,scene,False)
        self.assertEqual(body._plain(w.raw_pose(ob,record['session']['binding']['controls'])),record['session']['source'])

if __name__=='__main__':
    names=os.environ.get('B4ML_BALANCE_TEST','')
    suite=unittest.TestSuite(BalanceTests(name) for name in names.split(',') if name) if names else unittest.defaultTestLoader.loadTestsFromTestCase(BalanceTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    destination=Path(os.environ.get('B4ML_BALANCE_REPORT',str(ROOT/'training/b4artists_ml/results/balance-host-v1.json')))
    destination.write_text(json.dumps(dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),host=bpy.app.version_string,records=RECORDS),indent=2),encoding='utf-8')
    if not result.wasSuccessful() or result.skipped:raise SystemExit(1)
