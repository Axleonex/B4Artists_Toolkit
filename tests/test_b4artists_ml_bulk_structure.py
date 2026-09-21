"""Exact serialized compatibility and fresh invalidation of bulk rest reads."""
from pathlib import Path
import os,sys,json,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]
import bpy
from b4artists_ml import workflow as w
from test_b4artists_ml_context_rig import ContextRigTests

def reference(ob):
 return {b.name:{'parent':b.parent.name if b.parent else None,'rest':[v for row in b.matrix_local for v in row]} for b in ob.data.bones}

class BulkStructureTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):ContextRigTests.setUpClass();cls.helper=ContextRigTests()
 def exact(self,ob):self.assertEqual(json.dumps(w._rest_signature(ob)),json.dumps(reference(ob)))
 def test_five_profiles_exact_saved_format(self):
  for label in self.helper.builders:
   ob,source,session,targets,mask=self.helper.fixture(label,transformed=True)
   try:self.exact(ob)
   finally:session.cancel()
 def test_edited_rest_is_fresh_and_invalidates_session(self):
  ob,source,session,targets,mask=self.helper.fixture('metarig_basic');before=w._rest_signature(ob);name=session.binding['names'][4]
  bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bone=ob.data.edit_bones[name];saved=(bone.head.copy(),bone.tail.copy(),bone.roll);bone.roll+=.37;bpy.ops.object.mode_set(mode='OBJECT')
  try:
   self.exact(ob);self.assertNotEqual(w._rest_signature(ob),before)
   with self.assertRaisesRegex(ValueError,'Rig structure'):session._validate()
  finally:
   bpy.ops.object.mode_set(mode='EDIT');bone=ob.data.edit_bones[name];bone.head=saved[0];bone.tail=saved[1];bone.roll=saved[2];bpy.ops.object.mode_set(mode='OBJECT');self.assertEqual(w._rest_signature(ob),before);session.cancel()
 def test_empty_rename_and_reparent_are_not_cached(self):
  data=bpy.data.armatures.new('Bulk structural test');ob=bpy.data.objects.new('Bulk structural test',data);bpy.context.scene.collection.objects.link(ob);bpy.context.view_layer.objects.active=ob;ob.select_set(True)
  self.assertEqual(w._rest_signature(ob),{});self.exact(ob)
  bpy.ops.object.mode_set(mode='EDIT');a=data.edit_bones.new('a');a.head=(0,0,0);a.tail=(.1,.2,1);b=data.edit_bones.new('b');b.head=(0,0,1);b.tail=(.3,.2,2);b.parent=a;bpy.ops.object.mode_set(mode='OBJECT');first=w._rest_signature(ob);self.exact(ob)
  bpy.ops.object.mode_set(mode='EDIT');b=data.edit_bones['b'];b.name='renamed';b.parent=None;bpy.ops.object.mode_set(mode='OBJECT');second=w._rest_signature(ob);self.exact(ob);self.assertNotEqual(first,second);self.assertIsNone(second['renamed']['parent']);self.assertNotIn('b',second)
  bpy.data.objects.remove(ob,do_unlink=True);bpy.data.armatures.remove(data)
if __name__=='__main__':unittest.main()
