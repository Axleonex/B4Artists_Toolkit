"""Evaluated pole alignment ergonomics for the 0.33 humanoid posing workflow."""
from pathlib import Path
import json,os,sys,unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy,numpy as np
from mathutils import Matrix,Quaternion,Vector
import b4artists_ml
from b4artists_ml import body_preview as body,body_solver as solver,posing as p,workflow as w
from test_b4artists_ml_context_rig import ContextRigTests
from test_b4artists_ml_imported_humanoids import authored,keys

RECORDS=[]


class PoleAlignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register();ContextRigTests.setUpClass();cls.fixtures=ContextRigTests()

    def tearDown(self):
        for obj in list(bpy.data.objects):
            if hasattr(obj,'b4ml') and obj.b4ml.body_payload:
                if obj.users_scene:bpy.context.window.scene=obj.users_scene[0]
                body.finish(obj,bpy.context.scene,False)
        body.reset_runtime()

    def _fixture(self,label):
        if label=='unity_humanoid_fbx':
            obj,mesh,roles=authored('unity_humanoid',1)
            return obj,w.raw_pose(obj),obj.animation_data.action,keys(obj)
        obj,source,session,targets,mask=self.fixtures.fixture(label,transformed=True)
        session.cancel()
        if label=='boneforge':
            profile,root,limbs=p.bindings(obj);rows={row['id']:row for row in limbs}
            for key in ('arm-L','arm-R','leg-L','leg-R'):
                bone=obj.pose.bones[rows[key]['fk'][1]]
                value=Quaternion(w._rotation(bone));bone.rotation_mode='QUATERNION'
                bone.rotation_quaternion=value@Quaternion((1.,0.,0.),.3)
            p._update(obj);source=w.raw_pose(obj)
        return obj,source,None,None

    def _geometry(self,obj,label):
        session=body._get(obj);record=json.loads(obj.b4ml.body_payload)
        index=dict((name,index) for index,name in body._target_rows(record))[label]
        middle=body.POLE_JOINTS[index];chain=solver.POLE_CHAINS[middle]
        points=session.world_points(session.points())
        motion=Matrix(record['motion_transform']);inverse=motion.inverted()
        pole=np.asarray(inverse@obj.b4ml.body_targets[label].pole.matrix_world.translation,float)
        bend,wanted=solver._pole_vectors(points,chain,pole)
        error=float(np.arctan2(np.linalg.norm(np.cross(bend,wanted)),np.dot(bend,wanted)))
        return session,record,index,middle,chain,points,motion,pole,error

    def _misalign(self,obj,label):
        session,record,index,middle,chain,points,motion,pole,error=self._geometry(obj,label)
        root,centre,end=(points[i] for i in chain)
        axis=end-root;axis/=np.linalg.norm(axis)
        bend=centre-root;bend-=axis*np.dot(bend,axis);bend/=np.linalg.norm(bend)
        side=np.cross(axis,bend);side/=np.linalg.norm(side)
        distance=max(float(np.linalg.norm(pole-centre)),session.scale*.4)
        helper=obj.b4ml.body_targets[label].pole
        helper.matrix_world.translation=motion@Vector(centre+side*distance)
        bpy.context.view_layer.update()
        return distance

    def _assert_aligned(self,obj,label):
        *_,error=self._geometry(obj,label)
        self.assertLess(error,1e-6)
        return error

    def test_aligns_evaluated_bend_on_six_humanoid_adapters(self):
        labels=(*self.fixtures.builders,'unity_humanoid_fbx')
        for label in labels:
            with self.subTest(rig=label):
                obj,source,action,action_keys=self._fixture(label)
                bpy.context.view_layer.objects.active=obj;obj.select_set(True)
                body.begin(obj,bpy.context.scene)
                item=obj.b4ml.body_targets['Hand L'];item.use_pole=False
                before_pose=w.raw_pose(obj);distance=self._misalign(obj,'Hand L')
                before_error=self._geometry(obj,'Hand L')[-1];self.assertGreater(before_error,.5)
                result=body.align_pole_to_current_bend(obj,'Hand L')
                error=self._assert_aligned(obj,'Hand L')
                self.assertAlmostEqual(result['distance'],distance,places=6)
                self.assertFalse(result['enabled']);self.assertEqual(result['middle_joint'],6)
                self.assertEqual(w.raw_pose(obj),before_pose)
                RECORDS.append(dict(fixture=label,target='Hand L',
                    before_error_radians=before_error,after_error_radians=error,
                    distance_preserved=True,pose_unchanged=True))
                body.finish(obj,bpy.context.scene,False)
                self.assertEqual(w.raw_pose(obj),source)
                if action is not None:
                    self.assertEqual(obj.animation_data.action,action)
                    self.assertEqual(keys(obj),action_keys)

    def test_all_four_helpers_preserve_toggles_and_operator_wiring(self):
        obj,source,action,action_keys=self._fixture('boneforge')
        bpy.context.view_layer.objects.active=obj;obj.select_set(True);body.begin(obj,bpy.context.scene)
        before_pose=w.raw_pose(obj)
        for enabled,label in zip((False,True,False,True),('Hand L','Hand R','Foot L','Foot R')):
            item=obj.b4ml.body_targets[label];item.use_pole=enabled
            self._misalign(obj,label)
            if label=='Hand L':
                self.assertEqual(bpy.ops.b4ml.body(operation='ALIGN_POLE',target_name=label),{'FINISHED'})
            else:body.align_pole_to_current_bend(obj,label)
            self._assert_aligned(obj,label);self.assertEqual(item.use_pole,enabled)
        self.assertEqual(w.raw_pose(obj),before_pose)
        class FakeRow:
            def __init__(self):self.calls=[];self.enabled=True
            def row(self,**kwargs):return self
            def operator(self,*args,**kwargs):
                from types import SimpleNamespace
                value=SimpleNamespace();self.calls.append((args,kwargs,value));return value
        row=FakeRow();op=__import__('b4artists_ml.ui',fromlist=['ui'])._draw_body_pole_align(row,'Foot R',False)
        self.assertFalse(row.enabled);self.assertEqual((op.operation,op.target_name),('ALIGN_POLE','Foot R'))

    def test_read_only_status_reports_aligned_opposite_and_off_plane(self):
        obj,source,action,action_keys=self._fixture('boneforge')
        bpy.context.view_layer.objects.active=obj;obj.select_set(True);body.begin(obj,bpy.context.scene)
        status=body.pole_bend_status(obj,'Hand L')
        self.assertEqual(status['relation'],'aligned');self.assertFalse(status['enabled'])
        self.assertLess(status['error_radians'],1e-6)
        self._misalign(obj,'Hand L')
        status=body.pole_bend_status(obj,'Hand L')
        self.assertEqual(status['relation'],'off-plane');self.assertGreater(status['error_radians'],1.)
        body.flip_pole_to_opposite_bend(obj,'Hand L')
        status=body.pole_bend_status(obj,'Hand L')
        self.assertEqual(status['relation'],'opposite');self.assertLess(status['opposite_error_radians'],1e-6)
        self.assertEqual(w.raw_pose(obj),source)
        body.finish(obj,bpy.context.scene,False)

    def test_read_only_status_ui_is_non_mutating_and_actionable(self):
        obj,source,action,action_keys=self._fixture('boneforge')
        bpy.context.view_layer.objects.active=obj;body.begin(obj,bpy.context.scene)
        class FakeRow:
            def __init__(self):self.calls=[]
            def label(self,**kwargs):self.calls.append(kwargs)
        row=FakeRow();status=__import__('b4artists_ml.ui',fromlist=['ui'])._draw_body_pole_status(row,obj,'Hand L')
        self.assertEqual(status['relation'],'aligned')
        self.assertIn('Current: aligned',row.calls[0]['text'])
        self.assertEqual(w.raw_pose(obj),source)
        body.finish(obj,bpy.context.scene,False)

    def test_invalid_and_ambiguous_alignment_is_atomic(self):
        obj,source,action,action_keys=self._fixture('boneforge')
        bpy.context.view_layer.objects.active=obj;body.begin(obj,bpy.context.scene)
        before_pose=w.raw_pose(obj)
        with self.assertRaisesRegex(ValueError,'Unknown whole-body target'):
            body.align_pole_to_current_bend(obj,'Missing')
        with self.assertRaisesRegex(ValueError,'does not support pole alignment'):
            body.align_pole_to_current_bend(obj,'Chest')
        item=obj.b4ml.body_targets['Hand L'];pole=item.pole
        matrix=pole.matrix_world.copy();pole.parent=item.target;pole.matrix_world=matrix
        with self.assertRaisesRegex(ValueError,'parented'):
            body.align_pole_to_current_bend(obj,'Hand L')
        self.assertTrue(np.allclose(np.asarray(pole.matrix_world),np.asarray(matrix)))
        pole.parent=None;pole.matrix_world=matrix;bpy.context.view_layer.update()
        pole.delta_location.x=.1
        with self.assertRaisesRegex(ValueError,'clear them before Align'):
            body.align_pole_to_current_bend(obj,'Hand L')
        pole.delta_location=(0.,0.,0.);pole.matrix_world=matrix;bpy.context.view_layer.update()
        session=body._get(obj);original_points=session.points
        straight=original_points();root,middle,end=solver.POLE_CHAINS[6]
        straight[middle]=(straight[root]+straight[end])*.5
        session.points=lambda *args,**kwargs:straight.copy()
        try:
            before=pole.matrix_world.copy();status=obj.b4ml.status
            with self.assertRaisesRegex(ValueError,'too straight'):
                body.align_pole_to_current_bend(obj,'Hand L')
            self.assertTrue(np.allclose(np.asarray(pole.matrix_world),np.asarray(before)))
            self.assertEqual(obj.b4ml.status,status);self.assertEqual(w.raw_pose(obj),before_pose)
        finally:session.points=original_points
        obj.b4ml.body_live=True
        with self.assertRaisesRegex(ValueError,'Stop Live Solve'):
            body.align_pole_to_current_bend(obj,'Hand L')
        obj.b4ml.body_live=False

    def test_aligned_enabled_pole_survives_solve_reload_and_keep(self):
        obj,source,action,action_keys=self._fixture('rigify_basic')
        bpy.context.view_layer.objects.active=obj;obj.select_set(True);body.begin(obj,bpy.context.scene)
        item=obj.b4ml.body_targets['Foot R'];item.use_pole=True
        self._misalign(obj,'Foot R');body.align_pole_to_current_bend(obj,'Foot R')
        expected=item.pole.matrix_world.copy();body.solve(obj)
        metrics=json.loads(obj.b4ml.body_payload)['metrics']
        self.assertEqual(metrics['requested_poles'],1);self.assertLess(metrics['pole_error_radians'],.01)
        name=obj.name;path=ROOT/'training/b4artists_ml/cache/pole-align-v1-reload.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path))
        obj=bpy.data.objects[name];bpy.context.view_layer.objects.active=obj
        self.assertTrue(np.allclose(np.asarray(obj.b4ml.body_targets['Foot R'].pole.matrix_world),
                                    np.asarray(expected),atol=1e-7))
        body.finish(obj,bpy.context.scene,True)
        self.assertEqual(len(obj.b4ml.anchors),1);self.assertEqual(w.raw_pose(obj),source)


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(PoleAlignTests))
    report=dict(tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),
                errors=len(result.errors),records=RECORDS,package=b4artists_ml.__file__)
    path=ROOT/'training/b4artists_ml/results'/os.environ.get(
        'B4ML_POLE_ALIGN_RESULT','pole-align-v1.json')
    path.write_text(json.dumps(report,indent=2)+'\n')
    print('POLE_ALIGN_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
