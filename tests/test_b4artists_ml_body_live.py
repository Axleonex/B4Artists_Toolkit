"""Actual-rig live pose scheduling and source recovery, with a deterministic clock."""
from pathlib import Path
import sys,json,unittest,time,os
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy,numpy as np
from b4artists_ml import body_live as live,body_preview as body,workflow as w,rig_state as rs,posing as p
import test_b4artists_ml_context_preview as preview
RECORDS=[]

class LivePoseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        preview.PreviewTests.setUpClass();cls.helper=preview.PreviewTests()
    @classmethod
    def tearDownClass(cls):
        label=os.environ.get('B4ML_RUN_LABEL','live-pose-development')
        (ROOT/f'training/b4artists_ml/results/{label}-timings.json').write_text(json.dumps(RECORDS,indent=2)+'\n')
    def tearDown(self):self.helper.tearDown();self.assertFalse(live._WATCHERS)
    def fixture(self,label='boneforge'):
        ob,source,modes,targets=self.helper.make(label)
        root=ob.pose.bones[p.bindings(ob)[1]];root.keyframe_insert('location',frame=bpy.context.scene.frame_current)
        source=w.raw_pose(ob);action=ob.animation_data.action
        signature=[(c.data_path,c.array_index,[(tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.interpolation) for k in c.keyframe_points]) for c in w.action_curves(action,ob.animation_data.action_slot)]
        self.helper.begin(ob,targets)
        return ob,source,modes,action,signature
    def keys(self,ob):
        return [(c.data_path,c.array_index,[(tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.interpolation) for k in c.keyframe_points]) for c in w.action_curves(ob.animation_data.action,ob.animation_data.action_slot)]
    def settle(self,ob,clock):
        times=[]
        for _ in range(3000):
            clock+=.02;start=time.perf_counter();result=live.tick(ob,now=clock);times.append((time.perf_counter()-start)*1000)
            if result in ('ready','idle'):return clock,times
        self.fail('Live solver did not settle')
    def test_debounce_and_unchanged_request_no_repeated_solve(self):
        ob,*_=self.fixture();live.start(ob,now=0.)
        self.assertEqual(live.tick(ob,now=.1),'queued');self.assertFalse(body._JOBS)
        clock,times=self.settle(ob,.14);count=live._WATCHERS[ob.as_pointer()]['completed'];self.assertEqual(count,1)
        for i in range(10):self.assertEqual(live.tick(ob,now=clock+i*.02),'idle')
        self.assertEqual(live._WATCHERS[ob.as_pointer()]['completed'],1);self.assertFalse(body._JOBS)
    def test_five_profiles_two_edits_keep_restores_source(self):
        for label in ('boneforge','rigify_basic','rigify_default','metarig_basic','metarig_default'):
            with self.subTest(rig=label):
                ob,source,modes,action,keys=self.fixture(label);live.start(ob,now=0.)
                clock,first=self.settle(ob,.14)
                target=ob.b4ml.body_targets['Head'].target;target.location.y+=.002;bpy.context.view_layer.update()
                clock+=.02;self.assertEqual(live.tick(ob,now=clock),'queued');clock,second=self.settle(ob,clock)
                metrics=json.loads(ob.b4ml.body_payload)['metrics']
                self.assertLess(metrics['pin_error'],2e-4);self.assertLess(metrics['length_error'],.002);self.assertLess(metrics['orientation_error_radians'],.001)
                RECORDS.append(dict(rig=label,first_tick_p95_ms=float(np.percentile(first,95)),first_tick_max_ms=max(first),second_tick_p95_ms=float(np.percentile(second,95)),second_tick_max_ms=max(second),first_ticks=len(first),second_ticks=len(second),metrics=metrics))
                self.assertEqual(live._WATCHERS[ob.as_pointer()]['completed'],2)
                body.finish(ob,bpy.context.scene,True)
                self.assertFalse(ob.b4ml.body_live);self.assertFalse(live._WATCHERS)
                self.assertEqual(ob.animation_data.action,action);self.assertEqual(self.keys(ob),keys)
                self.assertEqual(rs.mode_values(ob),modes);self.assertEqual(w.raw_pose(ob),source)
                self.assertEqual(len(ob.b4ml.anchors),1)
    def test_stale_fit_aborts_and_only_newest_request_is_kept(self):
        ob,*_=self.fixture();body.solve(ob);before=w.raw_pose(ob)
        live.start(ob,now=0.);target=ob.b4ml.body_targets['Head'].target
        target.location.y+=.002;bpy.context.view_layer.update();self.assertEqual(live.tick(ob,now=.02),'queued')
        self.assertEqual(live.tick(ob,now=.2),'solving')
        target.location.y+=.003;bpy.context.view_layer.update();wanted=tuple(target.location)
        self.assertEqual(live.tick(ob,now=.22),'queued');self.assertFalse(ob.b4ml.body_running)
        self.assertEqual(w.raw_pose(ob),before);self.assertEqual(tuple(target.location),wanted)
        self.assertEqual(live._WATCHERS[ob.as_pointer()]['cancelled'],1)
        self.settle(ob,.22)
        self.assertEqual(body._read(ob)['signature'],body._request(ob,body._get(ob))[2])
    def test_direct_control_edit_is_preserved_and_live_stops(self):
        ob,*_=self.fixture();live.start(ob,now=0.);self.assertEqual(live.tick(ob,now=.2),'solving')
        root=ob.pose.bones[p.bindings(ob)[1]];root.location.x+=.007;bpy.context.view_layer.update();edited=w.raw_pose(ob)
        self.assertEqual(live.tick(ob,now=.22),'stopped');self.assertEqual(w.raw_pose(ob),edited)
        self.assertFalse(ob.b4ml.body_running);self.assertFalse(live._WATCHERS)
        with self.assertRaises(ValueError):body.finish(ob,bpy.context.scene,True)
    def test_save_and_runtime_reset_stop_pending_solve(self):
        for cleanup in (body.before_save,body.reset_runtime):
            ob,*_=self.fixture();body.solve(ob);before=w.raw_pose(ob)
            live.start(ob,now=0.);ob.b4ml.body_targets['Head'].target.location.y+=.002;bpy.context.view_layer.update()
            live.tick(ob,now=.02);live.tick(ob,now=.2);cleanup()
            self.assertFalse(ob.b4ml.body_live);self.assertFalse(ob.b4ml.body_running);self.assertFalse(live._WATCHERS)
            self.assertEqual(w.raw_pose(ob),before)
            body.finish(ob,bpy.context.scene,False)
    def test_manual_solve_cannot_take_live_ownership(self):
        ob,*_=self.fixture();live.start(ob,now=0.)
        with self.assertRaisesRegex(ValueError,'Stop Live Solve'):body.start(ob)
        self.assertFalse(bpy.ops.b4ml.body_solve.poll())
        self.assertEqual(bpy.ops.b4ml.body_live(),{'FINISHED'});self.assertFalse(ob.b4ml.body_live)
    def test_changed_frame_and_invalid_clock_stop_cleanly(self):
        ob,*_=self.fixture();live.start(ob,now=0.);live.tick(ob,now=.2)
        frame=bpy.context.scene.frame_current+1;bpy.context.scene.frame_set(frame)
        with self.assertRaisesRegex(ValueError,'frame changed'):live.tick(ob,now=.22)
        self.assertEqual(bpy.context.scene.frame_current,frame);self.assertFalse(ob.b4ml.body_running);self.assertFalse(live._WATCHERS)
        body.finish(ob,bpy.context.scene,False)
        ob,*_=self.fixture();live.start(ob,now=1.)
        with self.assertRaises(ValueError):live.tick(ob,now=.5)
        self.assertFalse(live._WATCHERS)
    def test_cancel_preview_while_live_restores_all_source(self):
        ob,source,modes,action,keys=self.fixture();live.start(ob,now=0.);live.tick(ob,now=.2)
        body.finish(ob,bpy.context.scene,False)
        self.assertEqual(w.raw_pose(ob),source);self.assertEqual(rs.mode_values(ob),modes)
        self.assertEqual(ob.animation_data.action,action);self.assertEqual(self.keys(ob),keys)
        self.assertFalse(body._JOBS);self.assertFalse(live._WATCHERS);self.assertFalse(ob.b4ml.body_live)
if __name__=='__main__':unittest.main()
