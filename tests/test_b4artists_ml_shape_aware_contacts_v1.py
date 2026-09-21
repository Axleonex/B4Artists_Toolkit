"""Research cubic-contact publication, cancellation, and failure recovery."""
from pathlib import Path
import sys,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy
from b4artists_ml import workflow as w,contacts as c,posing as p,rig_state as rs
from test_b4artists_ml_contacts import fixture
from shape_curve_v4 import smooth_copy
import shape_aware_contacts_v1 as shaped
class ShapeAwareContactsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import b4artists_ml;b4artists_ml.register()
    def setup(self):
        ob,source,signature,modes=fixture();scene=bpy.context.scene;candidate,_=smooth_copy(ob,ob.b4ml.candidate_action,1.,11.)
        w.assign_action(ob,candidate,w._slot(ob.animation_data));ob.b4ml.candidate_action=candidate
        return ob,scene,source,signature,modes,candidate,c._action_signature(ob)
    def test_shape_failure_removes_unpublished_copy(self):
        ob,scene,source,sig,modes,candidate,before=self.setup();actions={a.as_pointer() for a in bpy.data.actions}
        with patch.object(shaped,'smooth_copy',side_effect=ValueError('injected shape rejection')):
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
        self.assertEqual(report['backend'],'research_shape_aware_contact_projection_v1');self.assertLessEqual(report['max_after'],2e-4);self.assertLessEqual(report['orientation_error_radians'],.001);self.assertLessEqual(len(report['adaptive_refinements']),4);self.assertLessEqual(report['validation_max_interval_frames'],.03125)
        self.assertIs(ob.b4ml.contact_input,candidate);self.assertIs(ob.b4ml.contact_output,ob.animation_data.action)
        slot=w._slot(ob.animation_data);corrected=ob.animation_data.action;w.assign_action(ob,candidate,slot);self.assertEqual(c._action_signature(ob),before);w.assign_action(ob,corrected,slot)
        w.finish_preview(ob,scene,True);w.restore_kept_source(ob,scene);self.assertIs(ob.animation_data.action,source);self.assertEqual(c._action_signature(ob),sig);self.assertEqual(rs.mode_values(ob),modes)
