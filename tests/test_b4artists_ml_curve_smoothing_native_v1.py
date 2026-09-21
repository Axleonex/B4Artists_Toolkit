"""Actual FCurve behavior for bounded shape interpolation and rollback."""
from pathlib import Path
import sys,unittest,copy
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy,numpy as np
from b4artists_ml import workflow as w,posing as p,contacts as c
from test_b4artists_ml_contacts import fixture
from b4artists_ml.curve_smoothing import smooth_copy

class ShapeCurveNativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import b4artists_ml;b4artists_ml.register()
    def setup(self):
        ob,*_=fixture();return ob,ob.b4ml.candidate_action,c._action_signature(ob)
    def curves(self,ob,action):return w.action_curves(action,next(s for s in action.slots if s.identifier==w._slot(ob.animation_data)))
    def test_exact_key_samples_and_original_action_preserved(self):
        ob,action,before=self.setup();candidate,report=smooth_copy(ob,action,1.,11.);self.assertIs(ob.animation_data.action,action);self.assertEqual(c._action_signature(ob),before);self.assertTrue(report['authored_coordinates_unchanged'])
        old=self.curves(ob,action);new=self.curves(ob,candidate)
        for a in old:
            b=new.find(a.data_path,index=a.array_index);self.assertEqual([tuple(k.co) for k in a.keyframe_points],[tuple(k.co) for k in b.keyframe_points])
    def test_unowned_channel_is_unchanged(self):
        ob,action,_=self.setup();fc=self.curves(ob,action).new('location',index=1)
        for frame,value in [(0.,2.),(5.,3.),(17.,-2.)]:fc.keyframe_points.insert(frame,value)
        fc.update();values=[fc.evaluate(float(t)) for t in np.linspace(-2,20,113)];candidate,_=smooth_copy(ob,action,1.,11.);other=self.curves(ob,candidate).find('location',index=1);self.assertEqual(values,[other.evaluate(float(t)) for t in np.linspace(-2,20,113)])
    def outside(self,handle_type):
        ob,action,_=self.setup();root=p.bindings(ob)[1];fc=self.curves(ob,action).find(ob.pose.bones[root].path_from_id('location'),index=0)
        for frame,value in [(-4.,-.3),(17.,.4)]:fc.keyframe_points.insert(frame,value)
        for k in fc.keyframe_points:k.interpolation='BEZIER';k.handle_left_type=handle_type;k.handle_right_type=handle_type
        fc.update();times=np.r_[np.linspace(-5,1,121),np.linspace(11,19,161)];values=np.array([fc.evaluate(float(t)) for t in times]);before=c._action_signature(ob)
        candidate,_=smooth_copy(ob,action,1.,11.);other=self.curves(ob,candidate).find(fc.data_path,index=0);np.testing.assert_array_equal(values,np.array([other.evaluate(float(t)) for t in times]));self.assertEqual(c._action_signature(ob),before)
    def test_free_handles_outside_span_preserved(self):self.outside('FREE')
    def test_auto_handles_outside_span_preserved(self):self.outside('AUTO_CLAMPED')
    def test_locked_curve_rejects_without_copy_or_mutation(self):
        ob,action,_=self.setup();fc=next(f for f in self.curves(ob,action) if f.data_path.endswith('.location'));fc.lock=True;before=c._action_signature(ob);count=len(bpy.data.actions)
        with self.assertRaises(ValueError):smooth_copy(ob,action,1.,11.)
        self.assertEqual(len(bpy.data.actions),count);self.assertEqual(c._action_signature(ob),before)
    def test_opposite_quaternion_signs_reject_without_mutation(self):
        ob,action,_=self.setup();curves=self.curves(ob,action);path=next(f.data_path for f in curves if f.data_path.endswith('.rotation_quaternion'))
        for i in range(4):
            fc=curves.find(path,index=i);fc.keyframe_points[1].co.y*=-1;fc.update()
        before=c._action_signature(ob);count=len(bpy.data.actions)
        with self.assertRaisesRegex(ValueError,'signs or turns'):smooth_copy(ob,action,1.,11.)
        self.assertEqual(len(bpy.data.actions),count);self.assertEqual(c._action_signature(ob),before)

    def test_exact_constant_owned_curve_is_copied_without_rewrite(self):
        ob,action,_=self.setup();root=p.bindings(ob)[1];fc=self.curves(ob,action).find(ob.pose.bones[root].path_from_id('location'),index=0)
        for key in fc.keyframe_points:
            if 1.<=key.co.x<=11.:key.co.y=.25
        fc.update();times=np.linspace(-2.,14.,129);expected=np.array([fc.evaluate(float(t)) for t in times])
        def state(curve):return [(tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.handle_left_type,k.handle_right_type,k.interpolation) for k in curve.keyframe_points]
        source_state=state(fc);before=c._action_signature(ob);candidate,report=smooth_copy(ob,action,1.,11.);other=self.curves(ob,candidate).find(fc.data_path,index=0)
        self.assertGreaterEqual(report['skipped_constant_curves'],1);self.assertGreaterEqual(report['skipped_constant_keys'],2);self.assertEqual(state(other),source_state)
        np.testing.assert_array_equal(np.array([other.evaluate(float(t)) for t in times]),expected);self.assertEqual(c._action_signature(ob),before);bpy.data.actions.remove(candidate)

    def test_auto_boundary_survives_save_and_reload(self):
        ob,action,_=self.setup();root=p.bindings(ob)[1];fc=self.curves(ob,action).find(ob.pose.bones[root].path_from_id('location'),index=0)
        for frame,value in [(-4.,-.3),(17.,.4)]:fc.keyframe_points.insert(frame,value)
        for k in fc.keyframe_points:k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
        fc.update();times=np.r_[np.linspace(-5,1,121),np.linspace(11,19,161)];expected=np.array([fc.evaluate(float(t)) for t in times]);path=fc.data_path;name=ob.name
        candidate,_=smooth_copy(ob,action,1.,11.);w.assign_action(ob,candidate,w._slot(ob.animation_data));ob.b4ml.candidate_action=candidate
        scene=bpy.context.scene;scene.frame_set(6);filename=ROOT/'training/b4artists_ml/cache/runtime-shape-auto-reload-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(filename));bpy.ops.wm.open_mainfile(filepath=str(filename),load_ui=False,use_scripts=False)
        ob=bpy.data.objects[name];actual=self.curves(ob,ob.animation_data.action).find(path,index=0);np.testing.assert_array_equal(expected,np.array([actual.evaluate(float(t)) for t in times]))
