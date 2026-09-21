"""Evaluation copies must preserve source visibility, dependencies and context."""
from pathlib import Path
import os,sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]
import bpy,numpy as np
from b4artists_ml import body_proxy,workflow as w
from test_b4artists_ml_context_rig import ContextRigTests
class ProxyIsolationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):ContextRigTests.setUpClass();cls.helper=ContextRigTests()
 def flags(self,ob):
  return dict(mirror=ob.data.use_mirror_x,bones={b.name:{n:getattr(b,n,None) for n in ('hide','hide_select','select','select_head','select_tail')} for b in ob.data.bones},collections={c.name:c.is_visible for c in ob.data.collections_all})
 def test_evaluation_copy_preserves_original_flags_and_exact_dependencies(self):
  for label in ['rigify_default','rigify_basic','metarig_default']:
   with self.subTest(rig=label):
    ob,source,session,targets,mask=self.helper.fixture(label);before=self.flags(ob);context=(bpy.context.scene,bpy.context.view_layer.objects.active,ob.mode);counts=(len(bpy.data.objects),len(bpy.data.armatures),len(bpy.data.scenes));proxy=None
    try:
     seeds=set(session.binding['names']+session.binding['rotations']+session.binding['effectors']+[session.binding['root']])|set(session.lengths);proxy=body_proxy.EvaluationProxy(ob,seeds)
     self.assertEqual(set(proxy.obj.pose.bones.keys()),proxy.needed);self.assertEqual(before,self.flags(ob));self.assertEqual(context,(bpy.context.scene,bpy.context.view_layer.objects.active,ob.mode))
     error=max(float(np.max(abs(np.array(ob.pose.bones[n].matrix)-np.array(proxy.obj.pose.bones[n].matrix)))) for n in seeds);self.assertLess(error,2e-5)
    finally:
     if proxy:proxy.close()
     session.cancel()
    self.assertEqual(before,self.flags(ob));self.assertEqual(counts,(len(bpy.data.objects),len(bpy.data.armatures),len(bpy.data.scenes)));self.assertEqual(w.raw_pose(ob),source)
if __name__=='__main__':unittest.main()
