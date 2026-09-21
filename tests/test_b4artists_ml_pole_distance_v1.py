"""Body-scale pole-distance ergonomics for the 0.33 humanoid posing workflow."""
from pathlib import Path
import json,os,sys,unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy,numpy as np
from mathutils import Vector
from b4artists_ml import body_preview as body,motion_layer,workflow as w
from test_b4artists_ml_pole_align_v1 import PoleAlignTests
from test_b4artists_ml_imported_humanoids import keys

RECORDS=[]


class PoleDistanceTests(unittest.TestCase):
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

    def _geometry(self,obj,label):
        session,record,index,middle,chain,points,motion,pole,error=self.support._geometry(obj,label)
        vector=pole-points[middle];distance=float(np.linalg.norm(vector))
        return session,record,middle,points,motion,pole,distance,vector/distance

    def test_body_scale_distance_on_six_humanoid_adapters(self):
        labels=(*self.support.fixtures.builders,'unity_humanoid_fbx')
        for label in labels:
            with self.subTest(rig=label):
                obj,source,action,action_keys=self._fixture(label)
                bpy.context.view_layer.objects.active=obj;obj.select_set(True);body.begin(obj,bpy.context.scene)
                item=obj.b4ml.body_targets['Hand L'];item.use_pole=False
                before_pose=w.raw_pose(obj);before_direction=self._geometry(obj,'Hand L')[-1]
                result=body.set_pole_distance(obj,'Hand L',.85)
                session,record,middle,points,motion,pole,distance,direction=self._geometry(obj,'Hand L')
                self.assertTrue(np.allclose(direction,before_direction,atol=1e-7))
                self.assertAlmostEqual(distance/session.scale,.85,places=6)
                self.assertEqual(result['distance_body_scales'],.85);self.assertFalse(result['enabled'])
                self.assertEqual(item.pole.empty_display_type,'CIRCLE');self.assertTrue(item.pole.show_in_front)
                self.assertEqual(w.raw_pose(obj),before_pose)
                RECORDS.append(dict(fixture=label,target='Hand L',distance_body_scales=distance/session.scale,
                    direction_error=float(np.linalg.norm(direction-before_direction)),pose_unchanged=True))
                body.finish(obj,bpy.context.scene,False);self.assertEqual(w.raw_pose(obj),source)
                if action is not None:
                    self.assertEqual(obj.animation_data.action,action);self.assertEqual(keys(obj),action_keys)

    def test_all_four_helpers_and_operator_ui_wiring(self):
        obj,source,action,action_keys=self._fixture('boneforge')
        bpy.context.view_layer.objects.active=obj;obj.select_set(True);body.begin(obj,bpy.context.scene)
        before_pose=w.raw_pose(obj)
        manual=obj.b4ml.body_targets['Hand L'];manual.pole.location.x+=.03;bpy.context.view_layer.update()
        self.assertAlmostEqual(manual.pole_distance,.4,places=6)
        aligned=body.align_pole_to_current_bend(obj,'Hand R')
        self.assertAlmostEqual(obj.b4ml.body_targets['Hand R'].pole_distance,
                               aligned['distance']/body._get(obj).scale,places=6)
        flipped=body.flip_pole_to_opposite_bend(obj,'Foot L')
        self.assertAlmostEqual(obj.b4ml.body_targets['Foot L'].pole_distance,
                               flipped['distance']/body._get(obj).scale,places=6)
        session,record,middle,points,motion,pole,*_=self._geometry(obj,'Hand R')
        radial=np.asarray(pole-points[middle],dtype=float)
        radial/=np.linalg.norm(radial)
        obj.b4ml.body_targets['Hand R'].pole.matrix_world.translation=(
            motion@Vector(points[middle]+radial*session.scale*5.5))
        bpy.context.view_layer.update()
        capped=body.align_pole_to_current_bend(obj,'Hand R')
        self.assertAlmostEqual(capped['distance']/session.scale,4.,places=6)
        self.assertAlmostEqual(obj.b4ml.body_targets['Hand R'].pole_distance,4.,places=6)
        for enabled,label,distance in zip((False,True,False,True),('Hand L','Hand R','Foot L','Foot R'),(.25,.5,.75,1.)):
            item=obj.b4ml.body_targets[label];item.use_pole=enabled;item.pole_distance=distance
            before_direction=self._geometry(obj,label)[-1]
            if label=='Hand L':
                self.assertEqual(bpy.ops.b4ml.body(operation='SET_POLE_DISTANCE',target_name=label),{'FINISHED'})
            else:body.set_pole_distance(obj,label,distance)
            session,*_,actual,after_direction=self._geometry(obj,label)
            self.assertAlmostEqual(actual/session.scale,distance,places=6)
            self.assertTrue(np.allclose(after_direction,before_direction,atol=1e-7));self.assertEqual(item.use_pole,enabled)
        self.assertEqual(w.raw_pose(obj),before_pose)
        class FakeRow:
            def __init__(self):self.calls=[];self.enabled=True
            def row(self,**kwargs):return self
            def prop(self,*args,**kwargs):self.calls.append(('prop',args,kwargs))
            def operator(self,*args,**kwargs):
                value=__import__('types').SimpleNamespace();self.calls.append(('operator',args,kwargs,value));return value
        ui=__import__('b4artists_ml.ui',fromlist=['ui']);row=FakeRow()
        op=ui._draw_body_pole_distance(row,obj.b4ml.body_targets['Foot R'],False)
        self.assertFalse(row.enabled);self.assertEqual((op.operation,op.target_name),('SET_POLE_DISTANCE','Foot R'))
        self.assertEqual(row.calls[0][0],'prop');self.assertEqual(row.calls[0][2]['text'],'')
        self.assertEqual(row.calls[1][2]['text'],'Set Distance')
        props=__import__('types').SimpleNamespace(operation='SET_POLE_DISTANCE')
        self.assertIn('body-scale distance',ui.B4ML_OT_body.description(None,props))

    def test_invalid_distance_and_state_reject_atomically(self):
        obj,source,action,action_keys=self._fixture('boneforge')
        bpy.context.view_layer.objects.active=obj;body.begin(obj,bpy.context.scene)
        item=obj.b4ml.body_targets['Hand L'];pole=item.pole
        for value in (None,float('nan'),.09,4.01,True):
            before=pole.matrix_world.copy();setting=item.pole_distance;pose=w.raw_pose(obj);status=obj.b4ml.status
            with self.assertRaisesRegex(ValueError,'finite number'):body.set_pole_distance(obj,'Hand L',value)
            self.assertTrue(np.allclose(np.asarray(pole.matrix_world),np.asarray(before)))
            self.assertEqual(item.pole_distance,setting);self.assertEqual(w.raw_pose(obj),pose);self.assertEqual(obj.b4ml.status,status)
        with self.assertRaisesRegex(ValueError,'does not support pole distance'):
            body.set_pole_distance(obj,'Chest',.5)
        original=pole.matrix_world.copy();pole.delta_location.x=.1
        with self.assertRaisesRegex(ValueError,'clear them before Set Distance'):
            body.set_pole_distance(obj,'Hand L',.5)
        pole.delta_location=(0.,0.,0.);pole.matrix_world=original;bpy.context.view_layer.update()
        session,record,middle,points,motion,*_=self._geometry(obj,'Hand L')
        pole.matrix_world.translation=motion@Vector(points[middle]);bpy.context.view_layer.update()
        centred=pole.matrix_world.copy();pose=w.raw_pose(obj);status=obj.b4ml.status
        with self.assertRaisesRegex(ValueError,'too close'):body.set_pole_distance(obj,'Hand L',.5)
        self.assertTrue(np.allclose(np.asarray(pole.matrix_world),np.asarray(centred)))
        self.assertEqual(w.raw_pose(obj),pose);self.assertEqual(obj.b4ml.status,status)
        obj.b4ml.body_live=True
        with self.assertRaisesRegex(ValueError,'Stop Live Solve'):body.set_pole_distance(obj,'Hand L',.5)
        obj.b4ml.body_live=False

    def test_native_motion_change_rejects_all_pole_placement_atomically(self):
        obj,source,action,action_keys=self._fixture('boneforge');scene=bpy.context.scene
        instance=motion_layer.begin(obj,scene);instance.location.x=100000.;bpy.context.view_layer.update()
        saved=instance.matrix_world.copy()
        try:
            body.begin(obj,scene)
            item=obj.b4ml.body_targets['Hand L'];pole=item.pole
            instance.location.x+=.25;bpy.context.view_layer.update()
            before=pole.matrix_world.copy();pose=w.raw_pose(obj);status=obj.b4ml.status;setting=item.pole_distance
            for operation in (lambda:body.align_pole_to_current_bend(obj,'Hand L'),
                              lambda:body.flip_pole_to_opposite_bend(obj,'Hand L'),
                              lambda:body.set_pole_distance(obj,'Hand L',.8)):
                with self.assertRaisesRegex(ValueError,'preview-start transform'):operation()
                self.assertTrue(np.allclose(np.asarray(pole.matrix_world),np.asarray(before)))
                self.assertEqual(w.raw_pose(obj),pose);self.assertEqual(obj.b4ml.status,status)
                self.assertEqual(item.pole_distance,setting)
            body.reset_runtime()
            with self.assertRaisesRegex(ValueError,'saved transform'):
                body.set_pole_distance(obj,'Hand L',.8)
            self.assertTrue(np.allclose(np.asarray(pole.matrix_world),np.asarray(before)))
            self.assertEqual(w.raw_pose(obj),pose);self.assertEqual(obj.b4ml.status,status)
            self.assertEqual(item.pole_distance,setting)
            instance.matrix_world=saved;bpy.context.view_layer.update();body.finish(obj,scene,False)
        finally:
            if obj.b4ml.body_payload:
                instance.matrix_world=saved;bpy.context.view_layer.update();body.finish(obj,scene,False)
            if motion_layer.find(obj):motion_layer.restore(obj)
        self.assertEqual(w.raw_pose(obj),source)

    def test_enabled_distance_survives_solve_reload_and_keep(self):
        obj,source,action,action_keys=self._fixture('rigify_basic')
        bpy.context.view_layer.objects.active=obj;obj.select_set(True);body.begin(obj,bpy.context.scene)
        item=obj.b4ml.body_targets['Foot R'];item.use_pole=True
        body.set_pole_distance(obj,'Foot R',.9);body.solve(obj)
        metrics=json.loads(obj.b4ml.body_payload)['metrics']
        self.assertEqual(metrics['requested_poles'],1);self.assertLess(metrics['pole_error_radians'],.01)
        name=obj.name;path=ROOT/'training/b4artists_ml/cache/pole-distance-v1-reload.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path))
        obj=bpy.data.objects[name];bpy.context.view_layer.objects.active=obj
        self.assertTrue(obj.b4ml.body_targets['Foot R'].use_pole)
        self.assertAlmostEqual(obj.b4ml.body_targets['Foot R'].pole_distance,.9,places=6)
        body.finish(obj,bpy.context.scene,True)
        self.assertEqual(len(obj.b4ml.anchors),1);self.assertEqual(w.raw_pose(obj),source)


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PoleDistanceTests))
    report=dict(tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),
                errors=len(result.errors),records=RECORDS,package=__import__('b4artists_ml').__file__)
    path=ROOT/'training/b4artists_ml/results'/os.environ.get('B4ML_POLE_DISTANCE_RESULT','pole-distance-v1.json')
    path.write_text(json.dumps(report,indent=2)+'\n')
    print('POLE_DISTANCE_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
