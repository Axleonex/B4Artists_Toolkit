"""Native source-visible scheduling, reference parity and cancellation guards."""
from pathlib import Path
import sys,os,json,time,unittest,copy
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy,numpy as np
from b4artists_ml import workflow as w,posing as p,body_solver as solver,rig_state as rs
import temporal_projection as reference
import temporal_cooperative_v1 as cooperative
from test_b4artists_ml_anchor_observations import AnchorObservationTests
RECORDS=[]

class CooperativeTemporalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):AnchorObservationTests.setUpClass();cls.helper=AnchorObservationTests()
    @classmethod
    def tearDownClass(cls):
        cooperative.unregister()
        tag=os.environ.get('B4ML_RUN_LABEL','temporal-cooperative')
        (ROOT/f'training/b4artists_ml/results/{tag}-detail.json').write_text(json.dumps(RECORDS,indent=2)+'\n')
    def fixture(self,label='boneforge'):
        ob,binding,*_=self.helper.fixture(label);ob.b4ml.anchors[1].frame=5;return ob,binding
    def inventory(self):
        return {n:sorted(v.as_pointer() for v in getattr(bpy.data,n)) for n in ('objects','armatures','scenes','actions')}
    def visible(self,ob):
        value=self.helper.state(ob)
        # Global inventory includes the solver's private evaluation copy while
        # suspended. Compare the actual visible scene here; require exact global
        # inventories separately after completion, close and rejection.
        scene=bpy.context.scene
        visible_objects=tuple((o.as_pointer(),o.name,o.type) for o in scene.objects)
        active=bpy.context.view_layer.objects.active
        return value[:6]+value[7:]+(visible_objects,active.as_pointer() if active else None,ob.mode)
    def compare(self,actual,expected):
        self.assertEqual(actual.keys(),expected.keys())
        for frame in actual:
            self.assertEqual(actual[frame].keys(),expected[frame].keys())
            for name,a in actual[frame].items():
                b=expected[frame][name]
                for prop in ('location','scale','raw_rotation'):
                    np.testing.assert_allclose(a[prop],b[prop],rtol=0,atol=2e-6,err_msg=f'{frame}/{name}/{prop}')
                self.assertEqual(a['mode'],b['mode']);self.assertEqual(a['channels'],b['channels'])
                np.testing.assert_allclose(a['rotation'],b['rotation'],rtol=0,atol=2e-6,err_msg=f'{frame}/{name}/rotation')
    def consume(self,ob,steps):
        before=self.visible(ob);ticks=[];phases=[]
        try:
            while True:
                start=time.perf_counter()
                try:progress=next(steps)
                except StopIteration as done:return done.value,ticks,phases
                ticks.append((time.perf_counter()-start)*1000);phases.append(progress['phase'])
                self.assertEqual(self.visible(ob),before,'Working frame or pose leaked at a pause')
                self.assertIsNone(ob.b4ml.candidate_action)
        finally:steps.close()
    def parity(self,label,context=False):
        ob,binding=self.fixture(label);before=self.visible(ob);inventory=self.inventory()
        expected,expected_metrics=reference.generate_samples(ob,reference.procedural,context=context)
        self.assertEqual(self.visible(ob),before)
        (actual,metrics),ticks,phases=self.consume(ob,cooperative.generate_steps(ob,reference.procedural,context=context))
        self.compare(actual,expected);self.assertEqual(len(metrics),len(expected_metrics))
        for frame,_ in w.read_anchors(ob):self.assertEqual(actual[frame],expected[frame])
        self.assertEqual(self.visible(ob),before);self.assertEqual(self.inventory(),inventory)
        self.assertNotIn(ob.as_pointer(),solver._SESSIONS);self.assertNotIn(ob.as_pointer(),cooperative._OWNERS)
        self.assertIn('derivatives',phases);self.assertIn('ready',phases)
        w.preview(ob,bpy.context.scene,pose_samples=actual)
        bpy.context.scene.frame_set(7,subframe=.25);w.finish_preview(ob,bpy.context.scene,False)
        self.assertEqual(self.visible(ob),before)
        RECORDS.append(dict(profile=label,context=context,reference_parity=True,visible_yields=len(ticks),max_tick_ms=max(ticks),p95_tick_ms=float(np.percentile(ticks,95)),phases=sorted(set(phases)),editable_action=True,source_restored=True))
    def test_boneforge_smoke_reference_and_visible_source(self):self.parity('boneforge')
    def test_remaining_profiles_reference_and_visible_source(self):
        for label in self.helper.builders:
            if label=='boneforge':continue
            with self.subTest(profile=label):self.parity(label)
    def test_observed_context_reference_parity(self):
        for label in ('boneforge','rigify_default','unity_humanoid'):
            with self.subTest(profile=label):self.parity(label,True)
    def advance(self,steps,phase):
        for _ in range(2000):
            item=next(steps)
            if item['phase']==phase:return
        self.fail('Expected cooperative phase never reached: '+phase)
    def test_close_every_owned_phase_restores_source_and_resources(self):
        for label in ('boneforge','rigify_default'):
            for phase in ('observing','proposal_ready','derivatives','finishing','frame_ready','ready'):
                with self.subTest(profile=label,phase=phase):
                    ob,_=self.fixture(label);before=self.visible(ob);inventory=self.inventory()
                    steps=cooperative.generate_steps(ob,reference.procedural,context=False)
                    try:self.advance(steps,phase);self.assertEqual(self.visible(ob),before)
                    finally:steps.close()
                    self.assertEqual(self.visible(ob),before);self.assertEqual(self.inventory(),inventory)
                    self.assertNotIn(ob.as_pointer(),solver._SESSIONS);self.assertNotIn(ob.as_pointer(),cooperative._OWNERS)
    def test_intervening_edits_reject_and_preserve_new_state(self):
        for edit in ('pose','frame','curve','anchor','fps','object','rotation_mode'):
            with self.subTest(edit=edit):
                ob,binding=self.fixture();scene=bpy.context.scene;inventory=self.inventory();steps=cooperative.generate_steps(ob,reference.procedural,context=False)
                self.advance(steps,'derivatives');root=ob.pose.bones[binding['root']]
                if edit=='pose':root.location.y+=.125;p._update(ob)
                elif edit=='frame':scene.frame_set(9,subframe=.125)
                elif edit=='curve':root.keyframe_insert('location',frame=4)
                elif edit=='anchor':ob.b4ml.anchors[0].frame+=.125
                elif edit=='fps':scene.render.fps=24
                elif edit=='object':ob.location.y+=.125;p._update(ob)
                else:root.rotation_mode='XYZ';root.rotation_euler.x=.125;p._update(ob)
                changed=self.visible(ob);anchors=[(a.frame,a.payload) for a in ob.b4ml.anchors];fps=scene.render.fps
                try:
                    with self.assertRaisesRegex(ValueError,'changed'):next(steps)
                finally:steps.close()
                self.assertEqual(self.visible(ob),changed);self.assertEqual(anchors,[(a.frame,a.payload) for a in ob.b4ml.anchors]);self.assertEqual(scene.render.fps,fps);self.assertEqual(self.inventory(),inventory)
                self.assertNotIn(ob.as_pointer(),solver._SESSIONS);self.assertNotIn(ob.as_pointer(),cooperative._OWNERS)
    def test_foreign_workflow_started_while_paused_rejects_and_preserves_state(self):
        for attribute in ('body_running','body_live','contact_suggest_running','secondary_running','cleanup_running'):
            with self.subTest(workflow=attribute):
                ob,_=self.fixture();before=self.visible(ob);inventory=self.inventory()
                steps=cooperative.generate_steps(ob,reference.procedural,context=False)
                self.advance(steps,'derivatives');setattr(ob.b4ml,attribute,True)
                try:
                    with self.assertRaisesRegex(ValueError,'Another animation workflow'):next(steps)
                    steps.close()
                    self.assertEqual(self.visible(ob),before);self.assertEqual(self.inventory(),inventory)
                    self.assertNotIn(ob.as_pointer(),solver._SESSIONS);self.assertNotIn(ob.as_pointer(),cooperative._OWNERS)
                finally:setattr(ob.b4ml,attribute,False)
    def test_direct_close_keeps_newer_pose_and_playhead(self):
        for label in ('boneforge','rigify_default'):
            with self.subTest(profile=label):
                ob,binding=self.fixture(label);inventory=self.inventory();steps=cooperative.generate_steps(ob,reference.procedural,context=False)
                self.advance(steps,'derivatives');bpy.context.scene.frame_set(9,subframe=.125);ob.pose.bones[binding['root']].location.y+=.125;p._update(ob)
                changed=self.visible(ob);steps.close()
                self.assertEqual(self.visible(ob),changed);self.assertEqual(self.inventory(),inventory)
                self.assertNotIn(ob.as_pointer(),solver._SESSIONS);self.assertNotIn(ob.as_pointer(),cooperative._OWNERS)
    def test_cancel_callback_and_invalid_provider_never_publish(self):
        for invalid in (False,True):
            with self.subTest(invalid=invalid):
                ob,_=self.fixture();before=self.visible(ob);inventory=self.inventory();cancel=[False]
                def provider(obs,t):
                    points,rot=reference.procedural(obs,t)
                    if invalid:points[0,0,0]=np.nan
                    return points,rot
                steps=cooperative.generate_steps(ob,provider,context=False,cancel_requested=lambda:cancel[0])
                try:
                    if invalid:
                        with self.assertRaises(ValueError):
                            while True:next(steps)
                    else:
                        self.advance(steps,'derivatives');cancel[0]=True
                        with self.assertRaises(InterruptedError):next(steps)
                finally:steps.close()
                self.assertEqual(self.visible(ob),before);self.assertEqual(self.inventory(),inventory)
                self.assertNotIn(ob.as_pointer(),solver._SESSIONS);self.assertNotIn(ob.as_pointer(),cooperative._OWNERS)
    def test_second_job_cannot_take_ownership(self):
        ob,_=self.fixture();before=self.visible(ob);a=cooperative.generate_steps(ob,reference.procedural,context=False);b=cooperative.generate_steps(ob,reference.procedural,context=False)
        try:
            next(a)
            with self.assertRaisesRegex(ValueError,'already owns'):next(b)
        finally:b.close();a.close()
        self.assertEqual(self.visible(ob),before);self.assertNotIn(ob.as_pointer(),cooperative._OWNERS)

    def test_save_and_load_cancel_private_work_before_serialization(self):
        ob,_=self.fixture('rigify_default');before=self.visible(ob);inventory=self.inventory();steps=cooperative.generate_steps(ob,reference.procedural,context=False)
        self.advance(steps,'derivatives');self.assertTrue(cooperative._LIVE)
        object_name=ob.name;action_name=ob.animation_data.action.name
        tag=os.environ.get('B4ML_RUN_LABEL','temporal-cooperative');path=ROOT/f'training/b4artists_ml/cache/{tag}-paused.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        self.assertEqual(self.visible(ob),before);self.assertEqual(self.inventory(),inventory)
        self.assertFalse(cooperative._OWNERS);self.assertFalse(cooperative._LIVE);self.assertNotIn(ob.as_pointer(),solver._SESSIONS)
        with self.assertRaises(InterruptedError):next(steps)
        steps.close()
        # Reopen through the actual host. Its library API intentionally refuses
        # to link from the current file; reopening also verifies saved recovery.
        bpy.ops.wm.open_mainfile(filepath=str(path));ob=bpy.data.objects[object_name]
        self.assertFalse(any(o.name.startswith('B4ML temporary evaluator') for o in bpy.data.objects))
        self.assertFalse(any(s.name.startswith('B4ML private evaluation') for s in bpy.data.scenes))
        self.assertEqual(ob.animation_data.action.name,action_name)
        loaded=self.helper.state(ob);self.assertEqual(loaded[:5],before[:5]);self.assertEqual(loaded[8],before[7])
        loading=cooperative.generate_steps(ob,reference.procedural,context=False);self.advance(loading,'derivatives')
        bpy.ops.wm.open_mainfile(filepath=str(path));ob=bpy.data.objects[object_name]
        self.assertFalse(cooperative._OWNERS);self.assertFalse(cooperative._LIVE);self.assertFalse(solver._SESSIONS)
        self.assertFalse(any(o.name.startswith('B4ML temporary evaluator') for o in bpy.data.objects))
        self.assertEqual(ob.animation_data.action.name,action_name)
        loaded=self.helper.state(ob);self.assertEqual(loaded[:5],before[:5]);self.assertEqual(loaded[8],before[7])
        with self.assertRaises(InterruptedError):next(loading)
        loading.close()
    def test_unregister_cancels_and_removes_lifecycle_handlers(self):
        ob,_=self.fixture('rigify_default');before=self.visible(ob);inventory=self.inventory();steps=cooperative.generate_steps(ob,reference.procedural,context=False)
        self.advance(steps,'derivatives');cooperative.unregister()
        self.assertEqual(self.visible(ob),before);self.assertEqual(self.inventory(),inventory)
        self.assertFalse(cooperative._LIVE);self.assertFalse(cooperative._OWNERS)
        for name in cooperative._HANDLER_NAMES:self.assertNotIn(cooperative.before_host_change,getattr(bpy.app.handlers,name))
        with self.assertRaises(InterruptedError):next(steps)
        steps.close()
