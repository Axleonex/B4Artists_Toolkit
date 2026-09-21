"""Evaluated skeletal frame integration across control-follow spaces."""
from pathlib import Path
import sys,os,json,math,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy,numpy as np
from mathutils import Quaternion,Vector
import b4artists_ml
from b4artists_ml import body_solver as solver,body_preview as body,joint_frames as frames,joint_limits as limits,workflow as w,posing as p
from test_b4artists_ml_joint_limits import LimitTests,bound
RECORDS=[]

class JointFrameTests(LimitTests):
    # Only the new tests are loaded below; inherited setup and cleanup are reused.
    def test_joint_frames_at_rest_on_five_rigs(self):
        for label in self.fixtures.builders:
            with self.subTest(rig=label):
                ob,source,s,targets,mask=self.fixtures.fixture(label,transformed=True)
                mapping=frames.bind(ob,s.binding)
                self.assertTrue(set(s.binding['effectors'])<=set(mapping))
                for name,pair in mapping.items():
                    self.assertFalse(name.startswith(('ORG-','MCH-','DEF-')))
                    rest=frames.rest_relative(ob,pair)
                    a,b=pair
                    reference=rest.inverted()@ob.data.bones[b].matrix_local.to_quaternion().inverted()@ob.data.bones[a].matrix_local.to_quaternion()
                    self.assertLess(solver._angle(reference,Quaternion()),1e-5)
                s.cancel()

    def test_identical_evaluated_head_has_same_limits_across_follow_spaces(self):
        ob,source,s,targets,mask=self.fixtures.fixture('rigify_basic',transformed=True)
        goal=ob.pose.bones['head'].matrix.to_quaternion()@Quaternion((0,1,0),.4)
        s.cancel();rows=[]
        for follow in (0.,1.):
            ob.pose.bones['torso']['head_follow']=follow;p._update(ob);s=solver.Session(ob)
            pair=frames.bind(ob,s.binding)['head'];rest=frames.rest_relative(ob,pair)
            neck=ob.pose.bones['neck'];solver._set_quat(neck,solver._quat(neck)@Quaternion((0,1,0),.2));p._update(ob)
            matrix=goal.to_matrix().to_4x4();matrix.translation=ob.pose.bones['head'].head;p._write_rotation(ob,'head',matrix)
            if rows:
                # Rigify distributes head LOCAL rotation through neck segments.
                # Match the actual neck parent too; matching the head alone does
                # not create an identical skeletal pose across follow settings.
                wanted=Quaternion(rows[0]['parent']);base=solver._quat(neck);x=np.zeros(3)
                def evaluate(v):
                    delta=Quaternion(tuple(v)) if np.linalg.norm(v)>1e-12 else Quaternion()
                    solver._set_quat(neck,base@delta);p._update(ob)
                    m=goal.to_matrix().to_4x4();m.translation=ob.pose.bones['head'].head;p._write_rotation(ob,'head',m)
                    q=wanted.rotation_difference(ob.pose.bones[pair[1]].matrix.to_quaternion())
                    if q.w<0:q.negate()
                    return 2*np.array((q.x,q.y,q.z))
                for step in range(20):
                    error=evaluate(x)
                    if np.linalg.norm(error)<1e-6:break
                    jac=np.column_stack([(evaluate(x+np.eye(3)[i]*1e-3)-error)/1e-3 for i in range(3)])
                    delta=np.linalg.lstsq(jac,-error,rcond=None)[0]
                    x+=delta/max(1.,np.linalg.norm(delta)/.25)
                self.assertLess(np.linalg.norm(evaluate(x)),1e-5)
            rows.append(dict(joint=list(frames.rotation(ob,pair,rest)),control=list(solver._quat(ob.pose.bones['head'])),child=list(ob.pose.bones[pair[0]].matrix.to_quaternion()),parent=list(ob.pose.bones[pair[1]].matrix.to_quaternion())))
            s.cancel()
        print('FRAME_INVARIANCE: '+json.dumps(rows),flush=True)
        for key in ('joint','child','parent'):self.assertLess(solver._angle(Quaternion(rows[0][key]),Quaternion(rows[1][key])),1e-5)
        self.assertGreater(solver._angle(Quaternion(rows[0]['control']),Quaternion(rows[1]['control'])),.1)
        RECORDS.append(dict(case='follow_space_invariance',measurements=rows))

    def test_root_follow_head_joint_limit_can_fit_without_changing_follow(self):
        for label in ('boneforge','rigify_basic','rigify_default','metarig_basic','metarig_default'):
            with self.subTest(rig=label):
                ob,source,s,targets,mask=self.fixtures.fixture(label,transformed=True)
                name=s.binding['effectors'][0];pb=ob.pose.bones[name]
                target=s.world.to_quaternion()@pb.matrix.to_quaternion()@Quaternion((0,1,0),.3)
                limit=dict(bound(.8,-.02,.02),space='JOINT')
                result=s.solve(targets,mask,iterations=100,jacobian_mode=os.environ.get('B4ML_FRAME_JACOBIAN','reuse'),orientations_world={4:list(target)},rotation_limits={name:limit})
                pair=frames.bind(ob,s.binding)[name];q=frames.rotation(ob,pair,frames.rest_relative(ob,pair))
                self.assertLess(max(abs(limits.residual(q,limit))),.001)
                self.assertLess(solver._angle(target,s.world.to_quaternion()@pb.matrix.to_quaternion()),.001)
                if label.startswith('rigify'):
                    self.assertEqual(ob.pose.bones['torso']['head_follow'],0.)
                    self.assertGreater(abs(limits.angles(solver._quat(pb))[1]),.2)
                RECORDS.append(dict(case='head_joint_fit',fixture=label,joint_quaternion=list(q),**{k:v for k,v in result.items() if k!='points'}));s.cancel()

    def test_active_limb_joint_limits_on_all_rig_families(self):
        for label in ('boneforge','rigify_default','metarig_basic'):
            with self.subTest(rig=label):
                ob,source,s,targets,mask=self.fixtures.fixture(label,transformed=True)
                targets=s.world_points(s.baseline);mask[:]=False;mask[0]=True
                _,_,limbs=p.bindings(ob);names=[r['fk'][1] for r in limbs]
                mapping=frames.bind(ob,s.binding);reference={n:frames.rest_relative(ob,mapping[n]) for n in names}
                s.solve(targets,mask,iterations=80)
                before={n:limits.angles(frames.rotation(ob,mapping[n],reference[n]))[0] for n in names}
                request={n:dict(bound(.025),space='JOINT') for n in names}
                result=s.solve(targets,mask,rotation_limits=request,iterations=80)
                after={n:limits.angles(frames.rotation(ob,mapping[n],reference[n]))[0] for n in names}
                self.assertGreater(max(before.values()),.026);self.assertLess(max(after.values()),.026)
                RECORDS.append(dict(case='active_limb_joint',fixture=label,before=before,after=after,**{k:v for k,v in result.items() if k!='points'}));s.cancel()

    def test_joint_limited_head_drives_bound_mesh(self):
        ob,source,s,targets,mask=self.fixtures.fixture('rigify_default',transformed=True)
        deform='DEF-spine.006';self.assertIn(deform,ob.pose.bones)
        point=ob.data.bones[deform].head_local+Vector((.035,.02,.025))
        data=bpy.data.meshes.new('Joint-frame weighted mesh');data.from_pydata([point],[],[])
        mesh=bpy.data.objects.new('Joint-frame weighted mesh',data);bpy.context.scene.collection.objects.link(mesh)
        mesh.matrix_world=ob.matrix_world
        mesh.vertex_groups.new(name=deform).add([0],1.,'REPLACE');mesh.modifiers.new('Armature','ARMATURE').object=ob
        p._update(ob);start=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices[0].co.copy()
        target=s.world.to_quaternion()@ob.pose.bones['head'].matrix.to_quaternion()@Quaternion((0,1,0),.3)
        result=s.solve(targets,mask,iterations=100,orientations_world={4:list(target)},rotation_limits={'head':dict(bound(.8,-.02,.02),space='JOINT')})
        actual=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices[0].co.copy()
        expected=ob.pose.bones[deform].matrix@ob.data.bones[deform].matrix_local.inverted()@point
        self.assertLess((actual-expected).length,1e-5);self.assertGreater((actual-start).length,.003)
        RECORDS.append(dict(case='weighted_head_mesh',error=(actual-expected).length,displacement=(actual-start).length))
        s.cancel();bpy.data.objects.remove(mesh,do_unlink=True);bpy.data.meshes.remove(data)

    def test_actual_0_7_control_limit_preview_still_keeps(self):
        path=ROOT/'training/b4artists_ml/cache/joint-frame-legacy-v0.7.0.blend'
        self.assertTrue(path.exists(),'Generate this fixture with the actual retained 0.7.0 ZIP')
        bpy.ops.wm.open_mainfile(filepath=str(path))
        ob=next(o for o in bpy.data.objects if hasattr(o,'b4ml') and o.b4ml.body_payload)
        bpy.context.view_layer.objects.active=ob
        record=json.loads(ob.b4ml.body_payload)
        self.assertTrue(record['signature']['joint_limits'])
        self.assertTrue(all('space' not in value for value in record['signature']['joint_limits'].values()))
        self.assertTrue(all(i.space=='CONTROL' for i in ob.b4ml.body_limits))
        body.finish(ob,bpy.context.scene,True);self.assertEqual(len(ob.b4ml.anchors),1)

    def test_invalid_or_unsupported_joint_space_does_not_mutate(self):
        ob,source,s,targets,mask=self.fixtures.fixture('rigify_basic');before=w.raw_pose(ob)
        for request in ({'head':dict(bound(.8),space='WORLD')},{'hips':dict(bound(.8),space='JOINT')}):
            with self.assertRaisesRegex(ValueError,'Unknown limit measurement|No verified skeletal'):
                s.solve(targets,mask,rotation_limits=request)
            self.assertEqual(before,w.raw_pose(ob))

    def test_joint_space_reload_stale_and_cancel(self):
        ob,source=self.preview()
        for item in ob.b4ml.body_limits:
            item.enabled=item.joint_available
            if item.enabled:item.space='JOINT'
        body.solve(ob);name=ob.name;before=w.raw_pose(ob)
        record=json.loads(ob.b4ml.body_payload);self.assertGreater(record['metrics']['requested_skeletal_limits'],12)
        body.start(ob);body.step(ob);body.abort(ob);self.assertEqual(before,w.raw_pose(ob))
        path=ROOT/'training/b4artists_ml/cache/joint-frames-reload.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path))
        ob=bpy.data.objects[name];bpy.context.view_layer.objects.active=ob
        item=next(i for i in ob.b4ml.body_limits if i.enabled)
        self.assertEqual(item.space,'JOINT');item.space='CONTROL'
        with self.assertRaisesRegex(ValueError,'Solve the current targets'):body.finish(ob,bpy.context.scene,True)
        item.space='JOINT';body.finish(ob,bpy.context.scene,True)
        self.assertEqual(len(ob.b4ml.anchors),1)
        for n,row in source.items():self.assertEqual(w.raw_pose(ob)[n],row)


def run_ui_smoke():
    import test_b4artists_ml_context_preview as preview_tests
    os.environ['B4ML_UI_RIG']='rigify_default';os.environ['B4ML_UI_CONTROLS']='1'
    original_begin=preview_tests.PreviewTests.begin;original_step=body.step
    def begin(test,ob,targets):
        original_begin(test,ob,targets)
        for item in ob.b4ml.body_limits:
            item.enabled=item.joint_available;item.swing=1.5
            if item.enabled:item.space='JOINT'
        ob.b4ml.show_body_limits=True
    def checked_step(ob):
        done=original_step(ob)
        if done:
            record=json.loads(ob.b4ml.body_payload)
            assert record['metrics']['requested_skeletal_limits']==13
            assert record['metrics']['joint_limit_error_radians']<1e-3
        return done
    preview_tests.PreviewTests.begin=begin;body.step=checked_step;preview_tests.run_ui_smoke()

if __name__=='__main__' and '--ui-smoke' in sys.argv:run_ui_smoke()
elif __name__=='__main__':
    selection=os.environ.get('B4ML_FRAME_TEST')
    names=[name for name in JointFrameTests.__dict__ if name.startswith('test_')]
    suite=unittest.defaultTestLoader.loadTestsFromName(selection,sys.modules[__name__]) if selection else unittest.TestSuite(JointFrameTests(n) for n in names)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report=dict(tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),errors=len(result.errors),records=RECORDS,package=b4artists_ml.__file__)
    (ROOT/'training/b4artists_ml/results'/os.environ.get('B4ML_FRAME_RESULT','joint-frames-v1.json')).write_text(json.dumps(report,indent=2)+'\n')
    print('JOINT_FRAMES_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
