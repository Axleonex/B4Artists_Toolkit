"""Actual-rig rest-local limits: fitting, incompatibility and persistence."""
from pathlib import Path
import os,sys,json,math,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy,numpy as np
from mathutils import Quaternion
import b4artists_ml
from b4artists_ml import joint_limits as limits,body_solver as solver,body_preview as body,workflow as w,posing as p
from test_b4artists_ml_context_rig import ContextRigTests
RECORDS=[]


def bound(swing,low=-math.pi,high=math.pi):
    return dict(swing=swing,twist_min=low,twist_max=high)


class LimitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ContextRigTests.setUpClass();cls.fixtures=ContextRigTests()

    def tearDown(self):
        for ob in list(bpy.data.objects):
            if hasattr(ob,'b4ml') and ob.b4ml.body_payload:
                bpy.context.window.scene=ob.users_scene[0];body.finish(ob,bpy.context.scene,False)
        for s in list(solver._SESSIONS.values()):
            if not s.closed:
                bpy.context.window.scene=s.obj.users_scene[0];s.cancel()
        body.reset_runtime()

    def test_decomposition_and_sign_equivalence(self):
        for swing in (0.,.4,1.5,math.pi-.01):
            for twist in (-math.pi,-2.,-.5,0.,.5,2.,math.pi):
                q=Quaternion((1,0,0),swing)@Quaternion((0,1,0),twist)
                a,b=limits.angles(q)
                self.assertAlmostEqual(a,swing,places=6)
                self.assertLess(abs((b-twist+math.pi)%(2*math.pi)-math.pi),2e-6)
                np.testing.assert_allclose(limits.residual(q,bound(.8,-1,1)),limits.residual(-np.array(q),bound(.8,-1,1)),atol=1e-7)
        # The allowed +180-degree edge is also the -180-degree rotation.
        self.assertLess(abs(limits.residual(Quaternion((0,1,0),-math.pi),bound(1.,0.,math.pi))[1]),1e-6)
        q=Quaternion((0,1,0),math.radians(-179))
        self.assertAlmostEqual(abs(limits.residual(q,bound(1.,0.,math.pi))[1]),math.radians(1),places=6)

    def test_invalid_limit_requests_are_rejected_before_mutation(self):
        ob,source,s,targets,mask=self.fixtures.fixture('boneforge');before=w.raw_pose(ob)
        name=s.binding['rotations'][0]
        for request in ({'ORG-spine':bound(1.)},{name:bound(-1.)},{name:bound(1.,1.,-1.)},{name:bound(float('nan'))},{name:bound(math.pi,-1,1)},{name:{'swing':1.}},[]):
            with self.assertRaises(ValueError):s.solve(targets,mask,rotation_limits=request)
            self.assertEqual(before,w.raw_pose(ob))

    def test_feasible_pins_and_limits_on_five_transformed_rigs(self):
        for label in self.fixtures.builders:
            with self.subTest(rig=label):
                ob,source,s,targets,mask=self.fixtures.fixture(label,transformed=True)
                request={n:bound(1.5) for n in s.binding['rotations']+s.binding['effectors']}
                result=s.solve(targets,mask,rotation_limits=request,iterations=80)
                self.assertLess(result['pin_error'],2e-4);self.assertLess(result['joint_limit_error_radians'],1e-3)
                for n,limit in request.items():self.assertLess(max(abs(limits.residual(solver._quat(ob.pose.bones[n]),limit))),1e-3)
                RECORDS.append(dict(case='feasible',fixture=label,**{k:v for k,v in result.items() if k!='points'}))
                s.cancel();self.assertEqual(w.raw_pose(ob,s.binding['controls']),{n:source[n] for n in s.binding['controls']})

    def test_active_swing_limits_change_learned_pose(self):
        for label in ('boneforge','rigify_default','metarig_basic'):
            with self.subTest(rig=label):
                ob,source,s,targets,mask=self.fixtures.fixture(label,transformed=True)
                targets=s.world_points(s.baseline);mask[:]=False;mask[0]=True
                _,_,limbs=p.bindings(ob);names=[r['fk'][1] for r in limbs]
                unconstrained=s.solve(targets,mask,iterations=80)
                original={n:limits.angles(solver._quat(ob.pose.bones[n]))[0] for n in names}
                request={n:bound(.025) for n in names}
                result=s.solve(targets,mask,rotation_limits=request,iterations=80)
                constrained={n:limits.angles(solver._quat(ob.pose.bones[n]))[0] for n in names}
                self.assertGreater(max(original.values()),.026)
                self.assertLess(max(constrained.values()),.026)
                RECORDS.append(dict(case='active',fixture=label,unconstrained_swing=original,constrained_swing=constrained,**{k:v for k,v in result.items() if k!='points'}))
                s.cancel()

    def test_head_twist_limit_changes_parent_solution(self):
        for label in ('boneforge','rigify_basic','metarig_default'):
            with self.subTest(rig=label):
                ob,source,s,targets,mask=self.fixtures.fixture(label,transformed=True)
                if label.startswith('rigify'):
                    # In root-follow space this target necessarily consumes head
                    # control twist. Author neck-follow before starting the session.
                    s.cancel();ob.pose.bones['torso']['head_follow']=1.;p._update(ob);s=solver.Session(ob)
                name=s.binding['effectors'][0];pb=ob.pose.bones[name]
                target=s.world.to_quaternion()@pb.matrix.to_quaternion()@Quaternion((0,1,0),.3)
                request={name:bound(.8,-.02,.02)}
                result=s.solve(targets,mask,iterations=100,orientations_world={4:list(target)},rotation_limits=request)
                self.assertLess(abs(limits.angles(solver._quat(pb))[1]),.021)
                self.assertLess(solver._angle(target,s.world.to_quaternion()@pb.matrix.to_quaternion()),.001)
                RECORDS.append(dict(case='head_twist',fixture=label,**{k:v for k,v in result.items() if k!='points'}))
                s.cancel()

    def test_rigify_root_follow_conflict_is_not_silently_changed(self):
        ob,source,s,targets,mask=self.fixtures.fixture('rigify_basic')
        self.assertEqual(ob.pose.bones['torso']['head_follow'],0.)
        name=s.binding['effectors'][0];pb=ob.pose.bones[name]
        target=s.world.to_quaternion()@pb.matrix.to_quaternion()@Quaternion((0,1,0),.3)
        before=w.raw_pose(ob)
        with self.assertRaisesRegex(ValueError,'Joint limits conflict'):
            s.solve(targets,mask,iterations=20,orientations_world={4:list(target)},rotation_limits={name:bound(.8,-.02,.02)})
        self.assertEqual(before,w.raw_pose(ob));self.assertEqual(ob.pose.bones['torso']['head_follow'],0.)

    def test_conflicting_limits_restore_previous_preview(self):
        ob,source,s,targets,mask=self.fixtures.fixture('boneforge')
        s.solve(targets,mask);before=w.raw_pose(ob)
        request={n:bound(0.,0.,0.) for n in s.binding['rotations']+s.binding['effectors']}
        with self.assertRaisesRegex(ValueError,'Joint limits conflict|Actual rig projection failed'):
            s.solve(targets,mask,rotation_limits=request,iterations=12)
        self.assertEqual(before,w.raw_pose(ob));self.assertFalse(s.running)
        self.assertFalse(any(scene.name.startswith('B4ML private evaluation') for scene in bpy.data.scenes))

    def preview(self):
        ob,source,s,targets,mask=self.fixtures.fixture('boneforge');s.cancel()
        bpy.context.view_layer.objects.active=ob;body.begin(ob,bpy.context.scene)
        for index,label in body.TARGETS:ob.b4ml.body_targets[label].target.location=targets[index]
        for item in ob.b4ml.body_limits:item.enabled=True;item.swing=1.5
        p._update(ob);return ob,source

    def test_limits_reload_keep_and_stale_edits(self):
        ob,source=self.preview();body.solve(ob);name=ob.name
        path=ROOT/'training/b4artists_ml/cache/joint-limits-reload.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path))
        ob=bpy.data.objects[name];bpy.context.view_layer.objects.active=ob
        self.assertTrue(all(i.enabled for i in ob.b4ml.body_limits))
        item=ob.b4ml.body_limits[0];original=item.swing;item.swing=.4
        with self.assertRaisesRegex(ValueError,'Solve the current targets'):body.finish(ob,bpy.context.scene,True)
        item.swing=original;body.finish(ob,bpy.context.scene,True)
        self.assertEqual(len(ob.b4ml.anchors),1)
        for n,row in source.items():self.assertEqual(w.raw_pose(ob)[n],row)
        body.begin(ob,bpy.context.scene);self.assertTrue(all(i.enabled for i in ob.b4ml.body_limits))

    def test_limit_edit_and_cancel_during_solve(self):
        ob,source=self.preview();body.solve(ob);before=w.raw_pose(ob)
        body.start(ob);body.step(ob);body.abort(ob)
        self.assertEqual(w.raw_pose(ob),before)
        body.start(ob);body.step(ob);ob.b4ml.body_limits[0].swing=1.4
        with self.assertRaisesRegex(ValueError,'Targets changed during solving'):
            while not body.step(ob):pass
        self.assertEqual(w.raw_pose(ob),before)


def run_ui_smoke():
    # Reuse the established real event-loop / Escape / undo / redo scenario.
    # Only fixture setup and additional assertions are supplied here.
    import test_b4artists_ml_context_preview as preview_tests
    os.environ['B4ML_UI_RIG']='rigify_default';os.environ['B4ML_UI_CONTROLS']='1'
    original_begin=preview_tests.PreviewTests.begin
    original_step=body.step
    def begin(test,ob,targets):
        original_begin(test,ob,targets)
        for item in ob.b4ml.body_limits:item.enabled=True;item.swing=1.5
        ob.b4ml.show_body_limits=True
    def checked_step(ob):
        done=original_step(ob)
        if done:
            record=json.loads(ob.b4ml.body_payload)
            assert record['metrics']['requested_joint_limits']==len(ob.b4ml.body_limits)
            assert record['metrics']['joint_limit_error_radians']<1e-3
            assert record['signature']['joint_limits']
        return done
    preview_tests.PreviewTests.begin=begin;body.step=checked_step
    preview_tests.run_ui_smoke()


if __name__=='__main__' and '--ui-smoke' in sys.argv:
    run_ui_smoke()
elif __name__=='__main__':
    selection=os.environ.get('B4ML_LIMIT_TEST')
    suite=unittest.defaultTestLoader.loadTestsFromName(selection,sys.modules[__name__]) if selection else unittest.defaultTestLoader.loadTestsFromTestCase(LimitTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report=dict(tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),errors=len(result.errors),records=RECORDS,package=b4artists_ml.__file__)
    (ROOT/'training/b4artists_ml/results'/os.environ.get('B4ML_LIMIT_RESULT','joint-limits-v1.json')).write_text(json.dumps(report,indent=2)+'\n')
    print('JOINT_LIMIT_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
