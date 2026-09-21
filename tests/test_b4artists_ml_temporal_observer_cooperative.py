"""Native exact-observation and interrupted sampling checks."""
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy,numpy as np
from b4artists_ml import posing as p,body_solver as solver
import temporal_cooperative_v1 as c
import temporal_projection as ref
from test_b4artists_ml_temporal_cooperative import CooperativeTemporalTests

class ObservationsDone(Exception):pass

class CooperativeObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):CooperativeTemporalTests.setUpClass();cls.helper=CooperativeTemporalTests()
    @classmethod
    def tearDownClass(cls):c.unregister()
    def test_exact_observations_across_all_profiles_and_contexts(self):
        for label in self.helper.helper.builders:
            for context in (False,True):
                with self.subTest(profile=label,context=context):
                    obj,_=self.helper.fixture(label);before=self.helper.visible(obj);inventory=self.helper.inventory()
                    expected=ref.sample_anchors(obj,3,5,context=context);called=[]
                    def provider(observed,t):
                        for name in vars(expected):
                            a,b=getattr(observed,name),getattr(expected,name)
                            if isinstance(b,np.ndarray):np.testing.assert_array_equal(a,b,err_msg=name)
                            else:self.assertEqual(a,b,name)
                        np.testing.assert_array_equal(observed.features(),expected.features())
                        called.append(True);raise ObservationsDone()
                    job=c.generate_steps(obj,provider,context=context);indices=[]
                    try:
                        with self.assertRaises(ObservationsDone):
                            while True:
                                row=next(job);self.assertEqual(self.helper.visible(obj),before)
                                if row['phase']=='observed_pose':indices.append(row['observed_index'])
                    finally:job.close()
                    self.assertEqual(indices,list(range(4 if context else 2)));self.assertEqual(called,[True])
                    self.assertEqual(self.helper.visible(obj),before);self.assertEqual(self.helper.inventory(),inventory)
                    self.assertFalse(c._OWNERS);self.assertFalse(c._LIVE)
    def test_interrupted_observations_preserve_newer_visible_edits(self):
        for label in ('boneforge','rigify_default'):
            for index in range(4):
                for action in ('close','resume'):
                    with self.subTest(profile=label,index=index,action=action):
                        obj,binding=self.helper.fixture(label);inventory=self.helper.inventory();job=c.generate_steps(obj,ref.procedural,context=True)
                        try:
                            while True:
                                row=next(job)
                                if row['phase']=='observed_pose' and row['observed_index']==index:break
                            bpy.context.scene.frame_set(9,subframe=.125);obj.pose.bones[binding['root']].location.y+=.125;p._update(obj)
                            changed=self.helper.visible(obj)
                            if action=='close':job.close()
                            else:
                                with self.assertRaisesRegex(ValueError,'changed'):next(job)
                            self.assertEqual(self.helper.visible(obj),changed)
                        finally:job.close()
                        self.assertEqual(self.helper.inventory(),inventory);self.assertFalse(c._OWNERS);self.assertFalse(c._LIVE)
                        self.assertNotIn(obj.as_pointer(),solver._SESSIONS)
    def test_callback_cancels_each_observation_without_candidate_or_leaks(self):
        for index in range(4):
            with self.subTest(index=index):
                obj,_=self.helper.fixture('rigify_default');before=self.helper.visible(obj);inventory=self.helper.inventory();cancel=[False]
                job=c.generate_steps(obj,ref.procedural,context=True,cancel_requested=lambda:cancel[0])
                try:
                    while True:
                        row=next(job)
                        if row['phase']=='observed_pose' and row['observed_index']==index:break
                    cancel[0]=True
                    with self.assertRaises(InterruptedError):next(job)
                finally:job.close()
                self.assertEqual(self.helper.visible(obj),before);self.assertEqual(self.helper.inventory(),inventory)
                self.assertFalse(c._OWNERS);self.assertFalse(c._LIVE);self.assertIsNone(obj.b4ml.candidate_action)
