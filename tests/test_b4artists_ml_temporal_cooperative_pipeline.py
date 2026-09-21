"""Existing native motion workflow guards through cooperative temporal generation."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy
from unittest.mock import patch
from b4artists_ml import body_solver as bs
import temporal_projection as reference
import temporal_cooperative_v1 as cooperative
from test_b4artists_ml_temporal_projection import TemporalProjectionTests
_ORIGINAL=None

class CooperativePipelineTests(TemporalProjectionTests):
    @classmethod
    def setUpClass(cls):
        global _ORIGINAL
        super().setUpClass();_ORIGINAL=reference.generate_samples;reference.generate_samples=cooperative.generate_samples
    @classmethod
    def tearDownClass(cls):
        global _ORIGINAL
        try:super().tearDownClass()
        finally:
            reference.generate_samples=_ORIGINAL;cooperative.unregister()
    def test_later_projection_failure_never_publishes_partial_action(self):
        # Same failure and expected completed frame as the original case. Observe
        # the cooperative solver entry point, not the synchronous wrapper.
        ob,binding=self.fixture('unity_humanoid');ob.b4ml.anchors[1].frame=7
        before=self.helper.state(ob);successful=[];original=bs.Session.solve_steps
        def record(session,*args,**kwargs):
            result=yield from original(session,*args,**kwargs)
            successful.append(bpy.context.scene.frame_current);return result
        with patch.object(bs.Session,'solve_steps',record):
            with self.assertRaises(bs.ProjectionError):
                reference.preview(ob,reference.procedural,context=False,constraints={5:{'position_pins':{13:[30,30,30]}}})
        self.assertEqual(successful,[4]);self.assertEqual(self.helper.state(ob),before);self.assertFalse(ob.b4ml.candidate_action)
