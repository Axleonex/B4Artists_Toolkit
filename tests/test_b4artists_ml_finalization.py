"""Final-stage cancellation, borrowing and recovery on actual host rigs."""
from pathlib import Path
import sys,os,json,copy,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]
import bpy
from b4artists_ml import body_preview as body,body_live as live,workflow as w,rig_state as rs
from test_b4artists_ml_body_live import LivePoseTests

class FinalizationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):LivePoseTests.setUpClass();cls.helper=LivePoseTests()
 def tearDown(self):self.helper.tearDown()
 def fixture(self,label='boneforge'):
  ob,*_=self.helper.fixture(label);body.solve(ob);before=w.raw_pose(ob)
  ob.b4ml.body_targets['Head'].target.location.y+=.002;bpy.context.view_layer.update()
  return ob,before
 def advance(self,ob,boundary=2):
  body.start(ob);job=body._JOBS[ob.as_pointer()];original=job['iterator'];progress={}
  def watch():
   try:
    while True:
     try:value=next(original)
     except StopIteration as done:return done.value
     progress.clear();progress.update(value);yield value
   finally:original.close()
  job['iterator']=watch();count=0
  for _ in range(3000):
   self.assertFalse(body.step(ob))
   if progress.get('phase')=='finishing':
    count+=1
    if count==boundary:return
  self.fail('Finishing checkpoint not reached')
 def test_cancel_at_each_final_orientation_checkpoint(self):
  for boundary in [1,2]:
   ob,before=self.fixture('rigify_default');counts=(len(bpy.data.objects),len(bpy.data.armatures),len(bpy.data.scenes));self.advance(ob,boundary)
   body.abort(ob);self.assertEqual(w.raw_pose(ob),before);self.assertFalse(body._JOBS);self.assertFalse(body._get(ob).running)
   self.assertEqual(counts,(len(bpy.data.objects),len(bpy.data.armatures),len(bpy.data.scenes)));body.finish(ob,bpy.context.scene,False)
 def test_frame_change_at_final_boundary_restores_preview(self):
  ob,before=self.fixture();self.advance(ob);frame=bpy.context.scene.frame_current;bpy.context.scene.frame_set(frame+1)
  try:
   with self.assertRaisesRegex(ValueError,'Return to the session frame'):body.step(ob)
   self.assertEqual(w.raw_pose(ob),before);self.assertFalse(body._JOBS)
  finally:bpy.context.scene.frame_set(frame)
 def test_malformed_payload_during_completion_restores_preview(self):
  ob,before=self.fixture();self.advance(ob);payload=ob.b4ml.body_payload;request=body._request
  def malformed(*args,**kwargs):
   ob.b4ml.body_payload='{';return request(*args,**kwargs)
  try:
   with patch.object(body,'_request',malformed):
    with self.assertRaises(json.JSONDecodeError):body.step(ob)
   self.assertFalse(body._JOBS);self.assertFalse(ob.b4ml.body_running);self.assertEqual(w.raw_pose(ob),before)
  finally:ob.b4ml.body_payload=payload
 def test_final_live_tick_borrows_only_immutable_record(self):
  ob,before=self.fixture('rigify_default');live.start(ob,now=0.);clock=0.;decode=body._decode
  for _ in range(3000):
   clock+=.02;decoded=[];snapshots=[]
   def spy(payload):
    record=decode(payload);decoded.append(record);snapshots.append(copy.deepcopy(record));return record
   with patch.object(body,'_decode',spy):status=live.tick(ob,now=clock)
   if status=='ready':break
  else:self.fail('Live solve did not finish')
  self.assertEqual(len(decoded),2);self.assertEqual(decoded[0],snapshots[0]);self.assertIsNot(decoded[0],decoded[1]);self.assertNotEqual(decoded[1]['preview'],decoded[0]['preview']);self.assertNotEqual(w.raw_pose(ob),before)
 def test_changed_target_after_final_checkpoint_is_rejected(self):
  ob,before=self.fixture();self.advance(ob);target=ob.b4ml.body_targets['Head'].target;target.location.y+=.003;bpy.context.view_layer.update();wanted=tuple(target.location)
  with self.assertRaisesRegex(ValueError,'Targets changed during solving'):body.step(ob)
  self.assertEqual(w.raw_pose(ob),before);self.assertEqual(tuple(target.location),wanted);self.assertFalse(body._JOBS)
 def test_save_hook_at_final_boundary_cancels_private_copy(self):
  ob,before=self.fixture('rigify_default');counts=(len(bpy.data.objects),len(bpy.data.armatures),len(bpy.data.scenes));self.advance(ob)
  body.before_save();self.assertEqual(w.raw_pose(ob),before);self.assertFalse(body._JOBS);self.assertEqual(counts,(len(bpy.data.objects),len(bpy.data.armatures),len(bpy.data.scenes)))
if __name__=='__main__':unittest.main()
