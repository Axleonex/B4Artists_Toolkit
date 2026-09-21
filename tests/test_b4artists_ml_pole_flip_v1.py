"""Opposite-bend pole ergonomics for the 0.33 humanoid posing workflow."""
from pathlib import Path
import json,os,sys,unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy,numpy as np
from mathutils import Matrix
from b4artists_ml import body_preview as body,body_solver as solver,workflow as w
from test_b4artists_ml_pole_align_v1 import PoleAlignTests
from test_b4artists_ml_imported_humanoids import keys

RECORDS=[]


class PoleFlipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        PoleAlignTests.setUpClass();cls.support=PoleAlignTests()
        cls.support.fixtures=PoleAlignTests.fixtures

    def tearDown(self):
        for obj in list(bpy.data.objects):
            if hasattr(obj,'b4ml') and obj.b4ml.body_payload:
                if obj.users_scene:bpy.context.window.scene=obj.users_scene[0]
                body.finish(obj,bpy.context.scene,False)
        body.reset_runtime()

    def _fixture(self,label):return self.support._fixture(label)

    def _flip_geometry(self,obj,label):
        session,record,index,middle,chain,points,motion,pole,error=self.support._geometry(obj,label)
        bend,wanted=solver._pole_vectors(points,chain,pole);intended=-bend
        error=float(np.arctan2(np.linalg.norm(np.cross(intended,wanted)),np.dot(intended,wanted)))
        centre=points[chain[1]]
        return session,record,middle,points,motion,pole,float(np.linalg.norm(pole-centre)),error

    def test_flips_evaluated_bend_on_six_humanoid_adapters(self):
        labels=(*self.support.fixtures.builders,'unity_humanoid_fbx')
        for label in labels:
            with self.subTest(rig=label):
                obj,source,action,action_keys=self._fixture(label)
                bpy.context.view_layer.objects.active=obj;obj.select_set(True);body.begin(obj,bpy.context.scene)
                item=obj.b4ml.body_targets['Hand L'];item.use_pole=False
                before_pose=w.raw_pose(obj);before_distance=self._flip_geometry(obj,'Hand L')[-2]
                result=body.flip_pole_to_opposite_bend(obj,'Hand L')
                session,record,middle,points,motion,pole,distance,error=self._flip_geometry(obj,'Hand L')
                self.assertLess(error,1e-6);self.assertAlmostEqual(distance,max(before_distance,session.scale*.4),places=6)
                self.assertFalse(result['enabled']);self.assertEqual(result['operation'],'Flip')
                self.assertEqual(w.raw_pose(obj),before_pose)
                RECORDS.append(dict(fixture=label,target='Hand L',opposite_error_radians=error,
                    distance_preserved_or_stabilized=True,pose_unchanged=True))
                body.finish(obj,bpy.context.scene,False);self.assertEqual(w.raw_pose(obj),source)
                if action is not None:
                    self.assertEqual(obj.animation_data.action,action);self.assertEqual(keys(obj),action_keys)

    def test_all_four_helpers_preserve_toggles_and_operator_wiring(self):
        obj,source,action,action_keys=self._fixture('boneforge')
        bpy.context.view_layer.objects.active=obj;obj.select_set(True);body.begin(obj,bpy.context.scene)
        before_pose=w.raw_pose(obj)
        for enabled,label in zip((False,True,False,True),('Hand L','Hand R','Foot L','Foot R')):
            item=obj.b4ml.body_targets[label];item.use_pole=enabled
            if label=='Hand L':
                self.assertEqual(bpy.ops.b4ml.body(operation='FLIP_POLE',target_name=label),{'FINISHED'})
            else:body.flip_pole_to_opposite_bend(obj,label)
            self.assertLess(self._flip_geometry(obj,label)[-1],2e-6);self.assertEqual(item.use_pole,enabled)
        self.assertEqual(w.raw_pose(obj),before_pose)
        class FakeRow:
            def __init__(self):self.calls=[];self.enabled=True
            def row(self,**kwargs):return self
            def operator(self,*args,**kwargs):
                from types import SimpleNamespace
                value=SimpleNamespace();self.calls.append((args,kwargs,value));return value
        ui=__import__('b4artists_ml.ui',fromlist=['ui'])
        row=FakeRow();op=ui._draw_body_pole_flip(row,'Foot R',False)
        self.assertFalse(row.enabled);self.assertEqual((op.operation,op.target_name),('FLIP_POLE','Foot R'))
        self.assertEqual(row.calls[0][1]['text'],'Flip Side')
        align_row=FakeRow();ui._draw_body_pole_align(align_row,'Hand L',True)
        self.assertEqual(align_row.calls[0][1]['text'],'Align Bend')
        props=__import__('types').SimpleNamespace
        self.assertIn('opposite',ui.B4ML_OT_body.description(None,props(operation='FLIP_POLE')))
        self.assertIn('current evaluated',ui.B4ML_OT_body.description(None,props(operation='ALIGN_POLE')))

    def test_invalid_and_straight_flip_is_atomic(self):
        obj,source,action,action_keys=self._fixture('boneforge')
        bpy.context.view_layer.objects.active=obj;body.begin(obj,bpy.context.scene)
        item=obj.b4ml.body_targets['Hand L'];pole=item.pole;matrix=pole.matrix_world.copy();before=w.raw_pose(obj)
        pole.delta_location.x=.1
        with self.assertRaisesRegex(ValueError,'clear them before Flip'):
            body.flip_pole_to_opposite_bend(obj,'Hand L')
        pole.delta_location=(0.,0.,0.);pole.matrix_world=matrix;bpy.context.view_layer.update()
        session=body._get(obj);original=session.points;straight=original();root,middle,end=solver.POLE_CHAINS[6]
        straight[middle]=(straight[root]+straight[end])*.5;session.points=lambda *args,**kwargs:straight.copy()
        try:
            with self.assertRaisesRegex(ValueError,'too straight'):body.flip_pole_to_opposite_bend(obj,'Hand L')
        finally:session.points=original
        self.assertTrue(np.allclose(np.asarray(pole.matrix_world),np.asarray(matrix)));self.assertEqual(w.raw_pose(obj),before)
        obj.b4ml.body_live=True
        with self.assertRaisesRegex(ValueError,'Stop Live Solve'):body.flip_pole_to_opposite_bend(obj,'Hand L')
        obj.b4ml.body_live=False

    def test_enabled_flipped_pole_survives_solve_reload_and_keep(self):
        obj,source,action,action_keys=self._fixture('rigify_basic')
        bpy.context.view_layer.objects.active=obj;obj.select_set(True);body.begin(obj,bpy.context.scene)
        item=obj.b4ml.body_targets['Foot R'];item.use_pole=True
        body.flip_pole_to_opposite_bend(obj,'Foot R');body.solve(obj)
        metrics=json.loads(obj.b4ml.body_payload)['metrics']
        self.assertEqual(metrics['requested_poles'],1);self.assertLess(metrics['pole_error_radians'],.01)
        name=obj.name;path=ROOT/'training/b4artists_ml/cache/pole-flip-v1-reload.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path))
        obj=bpy.data.objects[name];bpy.context.view_layer.objects.active=obj
        self.assertTrue(obj.b4ml.body_targets['Foot R'].use_pole)
        body.finish(obj,bpy.context.scene,True)
        self.assertEqual(len(obj.b4ml.anchors),1);self.assertEqual(w.raw_pose(obj),source)


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PoleFlipTests))
    report=dict(tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),
                errors=len(result.errors),records=RECORDS,package=__import__('b4artists_ml').__file__)
    path=ROOT/'training/b4artists_ml/results'/os.environ.get('B4ML_POLE_FLIP_RESULT','pole-flip-v1.json')
    path.write_text(json.dumps(report,indent=2)+'\n')
    print('POLE_FLIP_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
