"""Research cubic-contact publication, cancellation, and failure recovery."""
from pathlib import Path
import sys,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy
from mathutils import Quaternion,Vector
from b4artists_ml import workflow as w,contacts as c,posing as p,rig_state as rs
from test_b4artists_ml_contacts import fixture
from b4artists_ml.curve_smoothing import smooth_copy,BACKEND
from b4artists_ml import contacts as shaped,curve_smoothing
class ShapeAwareContactsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import b4artists_ml;b4artists_ml.register()
    def setup(self):
        ob,source,signature,modes=fixture();scene=bpy.context.scene;candidate,_=smooth_copy(ob,ob.b4ml.candidate_action,1.,11.)
        candidate['b4ml_backend']=BACKEND
        w.assign_action(ob,candidate,w._slot(ob.animation_data));ob.b4ml.candidate_action=candidate
        return ob,scene,source,signature,modes,candidate,c._action_signature(ob)
    def test_shape_failure_removes_unpublished_copy(self):
        ob,scene,source,sig,modes,candidate,before=self.setup();actions={a.as_pointer() for a in bpy.data.actions}
        with patch.object(curve_smoothing,'smooth_copy',side_effect=ValueError('injected shape rejection')):
            with self.assertRaisesRegex(ValueError,'injected'):shaped.solve(ob,scene)
        self.assertIs(ob.animation_data.action,candidate);self.assertIs(ob.b4ml.candidate_action,candidate);self.assertEqual(c._action_signature(ob),before);self.assertEqual({a.as_pointer() for a in bpy.data.actions},actions)
        w.finish_preview(ob,scene,False);self.assertIs(ob.animation_data.action,source);self.assertEqual(c._action_signature(ob),sig);self.assertEqual(rs.mode_values(ob),modes)
    def test_close_during_cubic_validation_restores_input(self):
        ob,scene,source,sig,modes,candidate,before=self.setup();actions={a.as_pointer() for a in bpy.data.actions};frame=p._frame(scene);steps=shaped.correction_steps(ob,scene)
        try:
            for progress in steps:
                if progress['phase']=='Checking contacts':break
            else:self.fail('No cubic validation yield')
            self.assertIsNot(ob.animation_data.action,candidate)
        finally:steps.close()
        self.assertIs(ob.animation_data.action,candidate);self.assertIs(ob.b4ml.candidate_action,candidate);self.assertEqual(c._action_signature(ob),before);self.assertEqual(p._frame(scene),frame);self.assertEqual({a.as_pointer() for a in bpy.data.actions},actions)
    def test_changed_contact_rejects_and_preserves_user_edit(self):
        ob,scene,source,sig,modes,candidate,before=self.setup();actions={a.as_pointer() for a in bpy.data.actions};steps=shaped.correction_steps(ob,scene);next(steps);ob.b4ml.contacts[0].end=10.
        try:
            with self.assertRaisesRegex(ValueError,'Contacts or rig changed'):next(steps)
        finally:steps.close()
        self.assertEqual(ob.b4ml.contacts[0].end,10.);self.assertIs(ob.animation_data.action,candidate);self.assertEqual(c._action_signature(ob),before);self.assertEqual({a.as_pointer() for a in bpy.data.actions},actions)
    def test_success_keeps_input_editable_and_restores_source(self):
        ob,scene,source,sig,modes,candidate,before=self.setup();report=shaped.solve(ob,scene)
        self.assertEqual(report['backend'],'geometric_contact_projection_shape_v1');self.assertLessEqual(report['max_after'],2e-4);self.assertLessEqual(report['orientation_error_radians'],.001);self.assertLessEqual(len(report['adaptive_refinements']),4);self.assertLessEqual(report['validation_max_interval_frames'],.0625)
        # The adaptive validator may accept 1/16-frame intervals. Verify the
        # published cubic result independently at the former 1/32 density so
        # this test protects motion quality instead of one sampling strategy.
        _,_,limbs=p.bindings(ob);mapping={row['id']:row for row in limbs};max_position=max_orientation=0.
        for step in range(32,353):
            frame=step/32.;c._frame(scene,frame)
            for item in ob.b4ml.contacts:
                row=mapping[item.limb]
                reference=max(sum((ob.pose.bones[row['joints'][i+1]].head-ob.pose.bones[row['joints'][i]].head).length for i in (0,1))*w.display_world(ob).to_scale().x,1e-8)
                max_position=max(max_position,(c._point(ob,row,item.offset)-Vector(item.point)).length/reference)
                actual=(w.display_world(ob)@ob.pose.bones[row['joints'][2]].matrix).to_quaternion()
                max_orientation=max(max_orientation,c._angle(actual,Quaternion(item.rotation)))
        self.assertLessEqual(max_position,2e-4);self.assertLessEqual(max_orientation,.001)
        self.assertIs(ob.b4ml.contact_input,candidate);self.assertIs(ob.b4ml.contact_output,ob.animation_data.action)
        slot=w._slot(ob.animation_data);corrected=ob.animation_data.action;w.assign_action(ob,candidate,slot);self.assertEqual(c._action_signature(ob),before);w.assign_action(ob,corrected,slot)
        w.finish_preview(ob,scene,True);w.restore_kept_source(ob,scene);self.assertIs(ob.animation_data.action,source);self.assertEqual(c._action_signature(ob),sig);self.assertEqual(rs.mode_values(ob),modes)

    def test_noncontact_arm_curve_handles_are_preserved(self):
        ob,scene,*_=self.setup();limb=next(r for r in p.bindings(ob)[2] if r['id']=='arm-L');path=ob.pose.bones[limb['fk'][2]].path_from_id('rotation_quaternion');slot=ob.animation_data.action_slot
        curve=w.action_curves(ob.animation_data.action,slot).find(path,index=0);key=curve.keyframe_points[3];key.handle_left_type='FREE';key.handle_left.y+=.12
        def values(fc):return [(tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.interpolation,k.handle_left_type,k.handle_right_type) for k in fc.keyframe_points]
        before=values(curve);shaped.solve(ob,scene);actual=w.action_curves(ob.animation_data.action,ob.animation_data.action_slot).find(path,index=0);self.assertEqual(values(actual),before)
    def test_backend_change_during_fit_rejects_without_reverting_edit(self):
        ob,scene,source,sig,modes,candidate,before=self.setup();steps=shaped.correction_steps(ob,scene);next(steps);candidate['b4ml_backend']='animator_edit'
        try:
            with self.assertRaisesRegex(ValueError,'smoothing mode changed'):next(steps)
        finally:steps.close()
        self.assertIs(ob.animation_data.action,candidate);self.assertEqual(candidate['b4ml_backend'],'animator_edit');self.assertEqual(c._action_signature(ob),before)

    def test_prevalidated_anchor_snapshot_is_reused_for_shape_publication(self):
        ob,scene,*_=self.setup();anchors=w.read_anchors(ob);flight=c._flight_intervals(ob,anchors,c.rows(ob))
        steps=c._host_correction_steps(ob,scene,_anchors=anchors,_flight=flight)
        with patch.object(w,'read_anchors',side_effect=AssertionError('validated anchors were read again')):
            while True:
                try:next(steps)
                except StopIteration as stop:
                    report=stop.value;break
        self.assertEqual(report['backend'],'geometric_contact_projection_shape_v1')
        self.assertLessEqual(report['max_after'],2e-4)
