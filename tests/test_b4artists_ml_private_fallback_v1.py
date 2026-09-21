"""An unrelated external dependency must keep the existing supported workflow."""
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy
from b4artists_ml import temporal_generation as g,temporal_math,workflow as w
from test_b4artists_ml_temporal_private_v1 import PrivateTemporalTests

class PrivateFallbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        PrivateTemporalTests.setUpClass();cls.helper=PrivateTemporalTests.helper
    def tearDown(self):g.before_host_change()
    def test_unused_external_accessory_keeps_guarded_generation(self):
        original=self.helper.helper.builders['boneforge']
        def with_accessory():
            ob=original();bpy.context.view_layer.objects.active=ob
            bpy.ops.object.mode_set(mode='EDIT')
            bone=ob.data.edit_bones.new('unmapped_accessory');bone.head=(2,0,0);bone.tail=(2,0,1)
            bpy.ops.object.mode_set(mode='OBJECT')
            target=bpy.data.objects.new('External accessory target',None);bpy.context.scene.collection.objects.link(target)
            constraint=ob.pose.bones['unmapped_accessory'].constraints.new('COPY_LOCATION');constraint.target=target;constraint.influence=0
            return ob
        self.helper.helper.builders['boneforge']=with_accessory
        try:ob,_=self.helper.fixture()
        finally:self.helper.helper.builders['boneforge']=original
        before=self.helper.visible(ob);inventory=self.helper.inventory()
        expected,_=g.generate_samples(ob,lambda o,t:o.baseline(t),context=False,prepare_predictor=temporal_math.prepare)
        job=g.generate_private_steps(ob,lambda o,t:o.baseline(t),context=False,prepare_predictor=temporal_math.prepare)
        self.assertEqual(job.execution_path,'guarded_source')
        (actual,_),_,_=self.helper.consume(ob,job);self.helper.compare(actual,expected)
        w.preview(ob,bpy.context.scene,pose_samples=actual);w.finish_preview(ob,bpy.context.scene,False)
        self.assertEqual(self.helper.visible(ob),before);self.assertEqual(self.helper.inventory(),inventory)
        self.assertFalse(g._LIVE);self.assertFalse(g._OWNERS)
