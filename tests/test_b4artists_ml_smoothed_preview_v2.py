"""Opt-in smooth motion publication and source-preserving failure boundaries."""
from pathlib import Path
import sys,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
import bpy
from b4artists_ml import temporal_preview as preview,curve_smoothing as curves,workflow as w
from test_b4artists_ml_temporal_preview_v1 import TemporalPreviewTests
class SmoothPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):TemporalPreviewTests.setUpClass();cls.helper=TemporalPreviewTests();cls.helper.helper=TemporalPreviewTests.helper
    def tearDown(self):preview.before_host_change()
    def fixture(self):
        ob,before,inventory=self.helper.fixture();ob.b4ml.temporal_smoothing=True;return ob,before,inventory
    def verify_rollback(self,ob,before,inventory):
        self.helper.clean(ob);self.assertEqual(self.helper.helper.visible(ob),before);self.assertEqual(self.helper.helper.inventory(),inventory)
    def test_enabled_operator_generates_editable_curves_and_discard_recovers(self):
        ob,before,inventory=self.fixture();self.assertEqual(bpy.ops.b4ml.temporal_preview('EXEC_DEFAULT'),{'FINISHED'});self.assertEqual(ob.animation_data.action['b4ml_backend'],curves.BACKEND)
        self.assertTrue(any(k.interpolation=='BEZIER' for fc in w.action_curves(ob.animation_data.action,ob.animation_data.action_slot) for k in fc.keyframe_points));w.finish_preview(ob,bpy.context.scene,False);self.verify_rollback(ob,before,inventory)
    def test_publication_reuses_one_validated_anchor_snapshot(self):
        ob,before,inventory=self.fixture();original=preview._publish
        def observed(job,samples):
            self.assertIsInstance(samples,w._ValidatedPoseSamples);self.assertFalse(samples.consumed)
            with patch.object(w,'read_anchors',wraps=w.read_anchors) as reads:
                result=original(job,samples)
                self.assertEqual(reads.call_count,1)
                self.assertTrue(samples.consumed)
                with self.assertRaisesRegex(ValueError,'already consumed'):samples.consume()
                return result
        with patch.object(preview,'_publish',observed):preview.run(ob,bpy.context.scene)
        w.finish_preview(ob,bpy.context.scene,False);self.verify_rollback(ob,before,inventory)
    def test_transferred_samples_are_revalidated_before_action_mutation(self):
        ob,before,inventory=self.fixture();original=preview._publish
        def corrupt(job,samples):
            self.assertIsInstance(samples,w._ValidatedPoseSamples)
            frame=next(iter(samples._samples));name=next(iter(samples._samples[frame]))
            location=list(samples._samples[frame][name]['location']);location[0]=float('nan')
            samples._samples[frame][name]['location']=tuple(location)
            return original(job,samples)
        with patch.object(preview,'_publish',corrupt):
            with self.assertRaises(ValueError):preview.run(ob,bpy.context.scene)
        self.verify_rollback(ob,before,inventory)
    def test_smoothing_rejection_restores_source_without_leaking_actions(self):
        ob,before,inventory=self.fixture()
        with patch.object(curves,'smooth_copy',side_effect=ValueError('injected smoothing failure')):
            with self.assertRaisesRegex(ValueError,'injected'):preview.run(ob,bpy.context.scene)
        self.verify_rollback(ob,before,inventory)
    def test_smoothed_assignment_failure_restores_source(self):
        ob,before,inventory=self.fixture();original=w.assign_action
        def fail(obj,action,slot):
            if action and action.get('b4ml_backend')==curves.BACKEND:raise ValueError('injected assignment failure')
            return original(obj,action,slot)
        with patch.object(w,'assign_action',fail):
            with self.assertRaisesRegex(ValueError,'assignment'):preview.run(ob,bpy.context.scene)
        self.verify_rollback(ob,before,inventory)
    def test_setting_change_during_generation_preserves_new_setting_and_source(self):
        ob,before,inventory=self.fixture();preview.start(ob,bpy.context.scene);preview.step(ob);ob.b4ml.temporal_smoothing=False
        with self.assertRaisesRegex(ValueError,'setting changed'):preview.step(ob)
        self.assertFalse(ob.b4ml.temporal_smoothing);self.verify_rollback(ob,before,inventory)
    def test_default_generation_does_not_inherit_smoothed_backend(self):
        ob,before,_=self.fixture();ob.b4ml.temporal_smoothing=False;ob.animation_data.action['b4ml_backend']=curves.BACKEND
        with patch.object(curves,'smooth_copy',side_effect=AssertionError('Default path must not smooth')):preview.run(ob,bpy.context.scene)
        self.assertNotEqual(ob.animation_data.action['b4ml_backend'],curves.BACKEND);w.finish_preview(ob,bpy.context.scene,False);self.assertEqual(ob.animation_data.action['b4ml_backend'],curves.BACKEND)
    def test_cancel_smoothed_generation_restores_inventory(self):
        ob,before,inventory=self.fixture();preview.start(ob,bpy.context.scene);preview.step(ob);preview.abort(ob);self.verify_rollback(ob,before,inventory)
    def test_keep_restore_keeps_editable_smoothed_action(self):
        ob,before,_=self.fixture();source=ob.animation_data.action;preview.run(ob,bpy.context.scene);candidate=ob.animation_data.action;w.finish_preview(ob,bpy.context.scene,True);w.restore_kept_source(ob,bpy.context.scene)
        self.assertIs(ob.animation_data.action,source);self.assertEqual(candidate['b4ml_backend'],curves.BACKEND);self.assertTrue(candidate.use_fake_user);expected=list(before);expected[6]+=1;self.assertEqual(self.helper.helper.visible(ob),tuple(expected))
    def test_smoothing_setting_and_candidate_survive_reload(self):
        ob,before,_=self.fixture();preview.run(ob,bpy.context.scene);name=ob.name;path=ROOT/'training/b4artists_ml/cache/smoothed-preview-reload-v1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
        loaded=bpy.data.objects[name];self.assertTrue(loaded.b4ml.temporal_smoothing);self.assertFalse(loaded.b4ml.temporal_running);self.assertEqual(loaded.animation_data.action['b4ml_backend'],curves.BACKEND);w.finish_preview(loaded,bpy.context.scene,False);self.assertIsNone(loaded.b4ml.candidate_action);self.assertTrue(loaded.animation_data.action)
