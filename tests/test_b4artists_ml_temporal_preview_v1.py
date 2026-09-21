"""Native operator/controller integration, authored-only reads, and recovery."""
from pathlib import Path
import sys,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy
from b4artists_ml import workflow as w,temporal_preview as preview,temporal_generation as generation,temporal_observations as observations
from test_b4artists_ml_temporal_cooperative import CooperativeTemporalTests
from test_b4artists_ml_anchor_observations import AnchorObservationTests

class TemporalPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        AnchorObservationTests.setUpClass();cls.helper=CooperativeTemporalTests();cls.helper.helper=AnchorObservationTests()
    def tearDown(self):preview.before_host_change()
    def fixture(self):
        ob,_=self.helper.fixture();a=ob.b4ml.anchors.add();a.frame=7.;a.payload=ob.b4ml.anchors[0].payload
        return ob,self.helper.visible(ob),self.helper.inventory()
    def clean(self,ob):
        self.assertFalse(ob.b4ml.temporal_running);self.assertFalse(ob.b4ml.temporal_progress);self.assertFalse(preview._JOBS);self.assertFalse(generation._LIVE);self.assertFalse(generation._OWNERS)
    def test_observes_only_authored_frames_and_publishes_once(self):
        ob,before,inventory=self.fixture();calls=[];original=observations._frame_set
        def record(scene,frame,**kwargs):calls.append(float(frame)+kwargs.get('subframe',0));return original(scene,frame,**kwargs)
        with patch.object(observations,'_frame_set',record):
            preview.start(ob,bpy.context.scene)
            while not preview.step(ob):
                self.assertEqual(self.helper.visible(ob),before);self.assertIsNone(ob.b4ml.candidate_action)
        self.assertEqual(calls,[3.,5.,5.,7.]);self.clean(ob);self.assertTrue(ob.b4ml.candidate_action)
        w.finish_preview(ob,bpy.context.scene,False);self.assertEqual(self.helper.visible(ob),before);self.assertEqual(self.helper.inventory(),inventory)
    def test_registered_operator_generates_and_discard_operator_recovers(self):
        ob,before,_=self.fixture();self.assertEqual(bpy.ops.b4ml.temporal_preview('EXEC_DEFAULT'),{'FINISHED'});self.clean(ob)
        self.assertTrue(ob.b4ml.candidate_action);self.assertEqual(bpy.ops.b4ml.action(operation='DISCARD'),{'FINISHED'});self.assertEqual(self.helper.visible(ob),before)
    def test_cancel_operator_preserves_source(self):
        ob,before,inventory=self.fixture();preview.start(ob,bpy.context.scene);self.assertFalse(preview.step(ob));self.assertEqual(bpy.ops.b4ml.temporal_cancel(),{'FINISHED'});self.clean(ob);self.assertEqual(self.helper.visible(ob),before);self.assertEqual(self.helper.inventory(),inventory)
    def test_save_cancels_before_serialization(self):
        ob,before,_=self.fixture();preview.start(ob,bpy.context.scene);preview.step(ob)
        path=ROOT/'training/b4artists_ml/cache/temporal-preview-live-save-v1.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path));self.clean(ob);self.assertEqual(self.helper.visible(ob),before)
        bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);loaded=bpy.context.view_layer.objects.active;self.assertFalse(loaded.b4ml.temporal_running);self.assertFalse(loaded.b4ml.candidate_action);self.assertTrue(loaded.animation_data.action)
    def test_unregister_cancels_and_reregister_does_not_duplicate_hooks(self):
        ob,before,inventory=self.fixture();preview.start(ob,bpy.context.scene);preview.step(ob);preview.unregister();self.clean(ob);self.assertEqual(self.helper.visible(ob),before);self.assertEqual(self.helper.inventory(),inventory)
        preview.register();preview.register()
        for name in ('save_pre','load_pre','undo_pre','redo_pre'):
            self.assertEqual(list(getattr(bpy.app.handlers,name)).count(preview.before_host_change),1);self.assertEqual(list(getattr(bpy.app.handlers,name)).count(generation.before_host_change),1)
    def test_generation_failure_clears_flags_and_preserves_source(self):
        ob,before,inventory=self.fixture()
        with patch.object(preview.temporal_math,'prepare',side_effect=ValueError('injected preparation failure')):
            preview.start(ob,bpy.context.scene)
            with self.assertRaisesRegex(ValueError,'injected'):
                while not preview.step(ob):pass
        self.clean(ob);self.assertEqual(self.helper.visible(ob),before);self.assertEqual(self.helper.inventory(),inventory)
    def test_publish_failure_preserves_source_and_clears_flags(self):
        ob,before,inventory=self.fixture()
        with patch.object(w,'preview',side_effect=ValueError('injected publication failure')):
            preview.start(ob,bpy.context.scene)
            with self.assertRaisesRegex(ValueError,'publication'):
                while not preview.step(ob):pass
        self.clean(ob);self.assertEqual(self.helper.visible(ob),before);self.assertEqual(self.helper.inventory(),inventory)
    def test_two_jobs_on_same_rig_reject_without_cancelling_owner(self):
        ob,before,_=self.fixture();preview.start(ob,bpy.context.scene);job=preview._JOBS[ob.as_pointer()]
        with self.assertRaises(ValueError):preview.start(ob,bpy.context.scene)
        self.assertIs(preview._JOBS[ob.as_pointer()],job);self.assertFalse(preview.step(ob));preview.abort(ob);self.clean(ob);self.assertEqual(self.helper.visible(ob),before)

    def test_active_contact_scan_and_secondary_jobs_reject_before_ownership(self):
        ob,before,inventory=self.fixture()
        for attribute in ('contact_suggest_running','secondary_running'):
            with self.subTest(workflow=attribute):
                setattr(ob.b4ml,attribute,True)
                try:
                    with self.assertRaisesRegex(ValueError,'active animation'):
                        preview.start(ob,bpy.context.scene)
                    self.clean(ob)
                    self.assertEqual(self.helper.visible(ob),before)
                    self.assertEqual(self.helper.inventory(),inventory)
                finally:setattr(ob.b4ml,attribute,False)

    def test_procedural_strength_is_captured_and_marked_nonlearned(self):
        ob,before,_=self.fixture();ob.b4ml.temporal_strength=.25
        candidate=preview.run(ob,bpy.context.scene)
        self.clean(ob)
        self.assertIs(candidate,ob.b4ml.candidate_action)
        self.assertAlmostEqual(float(candidate['b4ml_temporal_strength']),.25,places=12)
        self.assertFalse(bool(candidate['b4ml_temporal_learned']))
        self.assertIn('25% strength',ob.b4ml.status)
        w.finish_preview(ob,bpy.context.scene,False)
        self.assertEqual(self.helper.visible(ob),before)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(TemporalPreviewTests))
    print('TEMPORAL_PREVIEW_RESULT: '+('PASS' if result.wasSuccessful() else 'FAIL'),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
