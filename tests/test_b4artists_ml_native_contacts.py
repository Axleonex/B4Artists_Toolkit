"""Native flight to contact workflow, generated timing and saved recovery."""
from pathlib import Path
import sys,os,json,unittest,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]
import bpy,numpy as np,b4artists_ml
from b4artists_ml import flight as f,contacts as c,workflow as w,motion_layer as m
from test_b4artists_ml_momentum import MomentumHostTests
from test_b4artists_ml_native_flight import values

class NativeContactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):b4artists_ml.register()
    def fixture(self,label='boneforge'):
        ob,source,sig,modes=MomentumHostTests().fixture(label);scene=bpy.context.scene
        ob.b4ml.flights[0].takeoff_blend=ob.b4ml.flights[0].landing_blend=2
        scene.frame_set(1);item=c.capture(ob,scene);item.start=1;item.end=2;item.blend=0
        f.solve(ob,scene);return ob,source,sig,modes
    def test_composition_restore_and_saved_editable_result_two_rigs(self):
        records=[]
        for label in ('boneforge','rigify_default'):
            ob,source,sig,modes=self.fixture(label);scene=bpy.context.scene;input_action=ob.animation_data.action;token=f._curve_token(ob);layer=m.validate(ob);layer_token=f._curve_token(layer)
            report=c.solve(ob,scene);self.assertLess(report['max_after'],2e-4);self.assertIsNot(ob.animation_data.action,input_action)
            self.assertEqual(f._curve_token(ob,input_action),token);self.assertEqual(f._curve_token(layer),layer_token)
            expected=values(ob);name=ob.name;w.finish_preview(ob,scene,True);w.restore_kept_source(ob,scene);self.assertEqual(c._action_signature(ob),sig);result=m.results(ob)[-1];result_name=result.name
            with tempfile.TemporaryDirectory() as td:
                path=str(Path(td)/'native-contacts.blend');bpy.ops.wm.save_as_mainfile(filepath=path);bpy.ops.wm.open_mainfile(filepath=path,use_scripts=False)
                ob=bpy.data.objects[name];scene=bpy.context.scene;result=bpy.data.objects[result_name];w.preview_motion_result(ob,scene,result)
                np.testing.assert_allclose(values(ob),expected,atol=2e-5)
                self.assertEqual(len(c._flight_intervals(ob,w.read_anchors(ob),c.rows(ob))),1)
                w.finish_preview(ob,scene,False);self.assertEqual(c._action_signature(ob),sig)
            records.append(dict(profile=label,contact_report=report,source_preserved=True,saved_result_preserved=True))
        (ROOT/('training/b4artists_ml/results/'+os.environ.get('B4ML_RUN_LABEL','native-contact')+'-composition.json')).write_text(json.dumps(dict(passed=True,rows=records),indent=2)+'\n')
    def test_nontrivial_contact_correction_preserves_native_motion(self):
        from mathutils import Quaternion
        from b4artists_ml import posing as p
        for label in ('boneforge','rigify_default'):
            ob,*_=MomentumHostTests().fixture(label);scene=bpy.context.scene
            ob.b4ml.flights[0].takeoff_blend=ob.b4ml.flights[0].landing_blend=2
            scene.frame_set(1);item=c.capture(ob,scene);item.start=1;item.end=2;item.blend=0
            row=next(r for r in p.bindings(ob)[2] if r['id']==item.limb);bone=ob.pose.bones[row['fk'][0]]
            self.assertEqual(bone.rotation_mode,'QUATERNION');original=bone.rotation_quaternion.copy()
            scene.frame_set(1,subframe=.5);bone.rotation_quaternion=original@Quaternion((1,0,0),.01);bone.keyframe_insert('rotation_quaternion',frame=1.5)
            scene.frame_set(2);bone.rotation_quaternion=original;bone.keyframe_insert('rotation_quaternion',frame=2)
            f.solve(ob,scene);before=values(ob);input_action=ob.animation_data.action;token=f._curve_token(ob)
            report=c.solve(ob,scene);self.assertGreater(report['max_before'],1e-4);self.assertLess(report['max_after'],2e-4)
            actual=values(ob)
            diag=dict(profile=label,max_by_frame=np.max(np.abs(actual-before),axis=(1,2)).tolist(),changed_bones=[dict(frame=[1.,2.137,6.,8.713,11.][i],bone=list(ob.pose.bones)[j].name,error=float(np.max(np.abs(actual[i,j]-before[i,j])))) for i,j in np.argwhere(np.max(np.abs(actual-before),axis=2)>2e-5)])
            (ROOT/('training/b4artists_ml/results/native-contact-outside-diagnostic-'+label+'.json')).write_text(json.dumps(diag,indent=2))
            np.testing.assert_allclose(actual,before,atol=2e-5);self.assertEqual(f._curve_token(ob,input_action),token)
    def test_generated_spans_survive_panel_edits_and_reject_overlap(self):
        ob,*_=self.fixture();scene=bpy.context.scene;token=f._curve_token(ob);ob.b4ml.flights.clear();ob.b4ml.contacts[0].end=3
        with self.assertRaisesRegex(ValueError,'transition'):c.solve(ob,scene)
        self.assertEqual(f._curve_token(ob),token);self.assertFalse(ob.b4ml.contact_running);self.assertIsNotNone(m.find(ob))
        ob.b4ml.contacts[0].end=2;c.solve(ob,scene);c.restore_before_contacts(ob,scene);self.assertEqual(f._curve_token(ob),token)
        f.restore(ob,scene);self.assertIsNone(m.find(ob))
    def test_legacy_native_metadata_migration_is_read_only(self):
        ob,*_=self.fixture();scene=bpy.context.scene;layer=m.validate(ob);del layer['b4ml_flight'];metrics=layer['b4ml_flight_metrics'];ob.b4ml.flights.clear()
        ob.b4ml.contacts[0].end=3
        with self.assertRaisesRegex(ValueError,'transition'):c.solve(ob,scene)
        ob.b4ml.contacts[0].end=2;c.solve(ob,scene);self.assertNotIn('b4ml_flight',layer);self.assertEqual(layer['b4ml_flight_metrics'],metrics)
    def test_corrupt_metadata_readable_error_and_rollback(self):
        for payload in ('{broken',json.dumps(dict(flights=None)),json.dumps({})):
            ob,*_=self.fixture();layer=m.validate(ob);layer['b4ml_flight']=payload;token=f._curve_token(ob)
            with self.assertRaises(ValueError):c.solve(ob,bpy.context.scene)
            self.assertEqual(f._curve_token(ob),token);self.assertFalse(ob.b4ml.contact_running);self.assertIsNotNone(m.find(ob))
    def test_metadata_edit_during_contact_fit_cancels(self):
        ob,*_=self.fixture();scene=bpy.context.scene;layer=m.validate(ob);token=f._curve_token(ob);c.start(ob,scene);self.assertFalse(c.step(ob))
        metadata=json.loads(layer['b4ml_flight']);metadata['flights'][0]['strength']=.5;layer['b4ml_flight']=json.dumps(metadata)
        with self.assertRaisesRegex(ValueError,'Generated flight changed'):c.step(ob)
        self.assertEqual(f._curve_token(ob),token);self.assertFalse(ob.b4ml.contact_running);self.assertEqual(json.loads(layer['b4ml_flight']),metadata)

if __name__=='__main__':unittest.main()
