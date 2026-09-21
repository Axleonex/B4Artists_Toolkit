"""Native safety checks for the authored trajectory preparation boundary."""
from pathlib import Path
import sys,unittest,copy
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy
from functools import partial
from b4artists_ml import workflow as w,body_solver as solver
from b4artists_ml import temporal_generation as cooperative
import temporal_projection as reference
from b4artists_ml.temporal_math import prepare
from test_b4artists_ml_temporal_cooperative import CooperativeTemporalTests
from test_b4artists_ml_anchor_observations import AnchorObservationTests

class RuntimeTemporalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        AnchorObservationTests.setUpClass();cls.helper=CooperativeTemporalTests();cls.helper.helper=AnchorObservationTests()
    @classmethod
    def tearDownClass(cls):cooperative.unregister()
    def fixture(self):
        ob,binding=self.helper.fixture();a=ob.b4ml.anchors.add();a.frame=7.;a.payload=ob.b4ml.anchors[0].payload
        return ob,self.helper.visible(ob),self.helper.inventory()
    def job(self,ob,factory=None):
        return cooperative.generate_steps(ob,reference.procedural,context=True,prepare_predictor=partial(prepare,rotation='slerp') if factory is None else factory)
    def at_phase(self,ob,job,phase):
        before=self.helper.visible(ob)
        for step in job:
            self.assertEqual(self.helper.visible(ob),before)
            if step['phase']==phase:return
        self.fail('Missing phase '+phase)
    def clean(self,ob,expected,inventory):
        self.assertEqual(self.helper.visible(ob),expected);self.assertEqual(self.helper.inventory(),inventory)
        self.assertNotIn(ob.as_pointer(),cooperative._OWNERS);self.assertNotIn(ob.as_pointer(),solver._SESSIONS);self.assertFalse(cooperative._LIVE);self.assertFalse(ob.b4ml.candidate_action)
    def test_three_priorities_source_visible_and_editable(self):
        ob,before,inventory=self.fixture();(samples,metrics),ticks,phases=self.helper.consume(ob,self.job(ob))
        self.assertIn('trajectory_ready',phases)
        for frame,payload in w.read_anchors(ob):self.assertEqual(samples[frame],payload['pose'])
        self.clean(ob,before,inventory);w.preview(ob,bpy.context.scene,pose_samples=samples);w.finish_preview(ob,bpy.context.scene,False);self.assertEqual(self.helper.visible(ob),before)
    def test_close_during_sampling(self):
        ob,before,inventory=self.fixture();job=self.job(ob);self.at_phase(ob,job,'observed_pose');job.close();self.clean(ob,before,inventory)
    def test_close_after_trajectory_prepared(self):
        ob,before,inventory=self.fixture();job=self.job(ob);self.at_phase(ob,job,'trajectory_ready');job.close();self.clean(ob,before,inventory)
    def test_anchor_edit_after_prepare_preserved_and_rejected(self):
        ob,before,inventory=self.fixture();job=self.job(ob);self.at_phase(ob,job,'trajectory_ready');ob.b4ml.anchors[1].frame=4.5;edited=self.helper.visible(ob)
        with self.assertRaisesRegex(ValueError,'Authored poses changed'):next(job)
        job.close();self.clean(ob,edited,inventory);self.assertEqual(ob.b4ml.anchors[1].frame,4.5)
    def test_source_curve_edit_after_prepare_preserved_and_rejected(self):
        ob,before,inventory=self.fixture();job=self.job(ob);self.at_phase(ob,job,'trajectory_ready')
        # Use existing animation ownership API, including layered action slots.
        curve=next(iter(w.action_curves(ob.animation_data.action,ob.animation_data.action_slot)));curve.keyframe_points[0].co.y+=.03;curve.update();scene=bpy.context.scene;scene.frame_set(scene.frame_current,subframe=scene.frame_subframe);edited=self.helper.visible(ob)
        with self.assertRaisesRegex(ValueError,'changed'):next(job)
        job.close();self.clean(ob,edited,inventory)
    def test_lifecycle_cancels_prepared_work(self):
        ob,before,inventory=self.fixture();job=self.job(ob);self.at_phase(ob,job,'trajectory_ready');cooperative.before_host_change()
        with self.assertRaises(InterruptedError):next(job)
        self.clean(ob,before,inventory)
    def test_bad_preparation_result_has_no_side_effect(self):
        ob,before,inventory=self.fixture();job=self.job(ob,lambda obs,frames:None)
        with self.assertRaisesRegex(ValueError,'return an interval provider'):
            for _ in job:pass
        job.close();self.clean(ob,before,inventory)
    def test_failed_preparation_has_no_side_effect(self):
        ob,before,inventory=self.fixture()
        def fail(obs,frames):raise RuntimeError('injected preparation failure')
        job=self.job(ob,fail)
        with self.assertRaisesRegex(RuntimeError,'injected preparation failure'):
            for _ in job:pass
        job.close();self.clean(ob,before,inventory)
