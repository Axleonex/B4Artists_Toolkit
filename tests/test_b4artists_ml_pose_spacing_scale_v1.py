"""Bforartists tests for proportional scaling of later priority-pose frames."""
from pathlib import Path
import json, math, os, struct, sys, tempfile, unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]
import bpy
from mathutils import Quaternion
import b4artists_ml
from b4artists_ml import quadruped_gait, workflow


class PoseSpacingScaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():raise unittest.SkipTest('Bforartists required')
        b4artists_ml.register()

    def setUp(self):
        if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
        data=bpy.data.armatures.new('Pose Scale Rig');self.obj=bpy.data.objects.new('Pose Scale Rig',data)
        bpy.context.scene.collection.objects.link(self.obj);bpy.context.view_layer.objects.active=self.obj
        self.obj.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
        for i,name in enumerate(('hips','upperarm.fk-L','thigh.fk-R')):
            bone=data.edit_bones.new(name);bone.head=(i,0,0);bone.tail=(i,0,1)
        bpy.ops.object.mode_set(mode='POSE');self.hips=self.obj.pose.bones['hips']
        self.hips.rotation_mode='QUATERNION';self.scene=bpy.context.scene
        self.scene.tool_settings.use_keyframe_insert_auto=False;self.scene.frame_set(1)

    def tearDown(self):
        self.scene=bpy.context.scene;self.scene.tool_settings.use_keyframe_insert_auto=False
        if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
        obj=bpy.data.objects.get('Pose Scale Rig')
        if obj:
            data=obj.data;bpy.data.objects.remove(obj,do_unlink=True)
            if not data.users:bpy.data.armatures.remove(data)

    def _frame(self,value):
        base=math.floor(value);self.scene.frame_set(base,subframe=value-base)

    def _capture(self,frame,value):
        self._frame(frame);self.hips.location.x=value
        self.hips.rotation_quaternion=Quaternion((0,0,1),math.radians(value*9))
        self.hips.keyframe_insert('location',frame=frame)
        self.hips.keyframe_insert('rotation_quaternion',frame=frame)
        workflow.capture_anchor(self.obj,self.scene)

    def _four(self,order=(1,6,11,16)):
        for frame in order:self._capture(frame,{1:0,6:5,11:10,16:15}[frame])

    def _anchor(self,frame):
        return next(a for a in self.obj.b4ml.anchors if abs(a.frame-frame)<1e-5)

    def _rows(self):return [(float(a.frame),a.name,a.payload) for a in self.obj.b4ml.anchors]
    def _sorted_frames(self):return [r[0] for r in workflow.read_anchors(self.obj)]
    def _digest(self):return quadruped_gait._action_digest(self.obj,self.obj.animation_data.action)
    @staticmethod
    def _stored(value):return float(struct.unpack('<f',struct.pack('<f',float(value)))[0])

    def _untouched(self):
        ad=self.obj.animation_data
        return (ad.action,getattr(ad,'action_slot',None),self._digest(),
                self.scene.frame_current,self.scene.frame_subframe,
                self.scene.tool_settings.use_keyframe_insert_auto,
                [(b.name,tuple(b.location),tuple(b.rotation_quaternion),b.rotation_mode,bool(b.select))
                 for b in self.obj.pose.bones])

    def test_expand_preserves_pivot_payload_timing_suffix_and_state(self):
        self._four();workflow.set_transition_timing(self.obj,11,True,'EASE_OUT',-.2,.1,.3)
        for f,label in ((11,'anticipation'),(16,'landing')):self._anchor(f).name+=' ('+label+')'
        before=self._rows();payloads=[self._anchor(f).payload for f in (1,6,11,16)]
        suffixes=[self._anchor(f).name.split(' - ',1)[1] for f in (1,6,11,16)]
        self.scene.tool_settings.use_keyframe_insert_auto=True;self._frame(77.5);untouched=self._untouched()
        result=workflow.scale_pose_spacing(self.obj,6,2)
        self.assertEqual(result,{'pivot_frame':6.0,'factor':2.0,'moved_count':2})
        self.assertEqual(self._sorted_frames(),[1,6,16,26]);self.assertEqual(self._anchor(6).name,before[1][1])
        for old,new,index in ((11,16,2),(16,26,3)):
            self.assertEqual(self._anchor(new).payload,payloads[index])
            self.assertEqual(self._anchor(new).name,f'Frame {new:.9g} - '+suffixes[index])
        self.assertEqual(workflow.transition_timing(self.obj,16),{'easing':'EASE_OUT','bias':-.2,'departure_hold':.1,'arrival_hold':.3})
        self.assertEqual(self._untouched(),untouched)

    def test_compress_first_pivot_unsorted_storage_and_endpoint_factors(self):
        self._four(order=(11,1,16,6));workflow.scale_pose_spacing(self.obj,1,.25)
        self.assertEqual(self._sorted_frames(),[1,2.25,3.5,4.75])
        self.assertEqual([r[0] for r in self._rows()],[3.5,1,4.75,2.25])
        self.obj.b4ml.anchors.clear();self._four();workflow.scale_pose_spacing(self.obj,11,4)
        self.assertEqual(self._sorted_frames(),[1,6,11,31])
        with self.assertRaisesRegex(ValueError,'at least one later'):
            workflow.scale_pose_spacing(self.obj,31,2)

    def test_factor_validation_noop_and_float32_storage(self):
        self._four();baseline=self._rows()
        for factor in (True,'2',None,float('nan'),float('inf'),.249,4.001,1):
            with self.subTest(factor=factor),self.assertRaises(ValueError):
                workflow.scale_pose_spacing(self.obj,6,factor)
            self.assertEqual(self._rows(),baseline)
        factor=1.23456789;workflow.scale_pose_spacing(self.obj,6,factor)
        expected=self._stored(6+(11-6)*factor)
        self.assertIn(expected,self._sorted_frames());self.assertTrue(self._anchor(expected).name.startswith(f'Frame {expected:.9g} - '))
        self.obj.b4ml.anchors.clear()
        for frame,value in ((1,0),(6,5),(200,10)):self._capture(frame,value)
        context=workflow.pose_spacing_scale_context(self.obj,6)
        self.assertEqual(context['moved_count'],1)
        with self.assertRaisesRegex(ValueError,'240 frames'):
            workflow.scale_pose_spacing(self.obj,6,1.25,context['binding'])
        result=workflow.scale_pose_spacing(self.obj,6,.5,context['binding'])
        self.assertEqual(result['factor'],.5);self.assertEqual(self._sorted_frames(),[1,6,103])

    def test_span_absolute_bounds_collision_and_rounding_distortion(self):
        for f,v in ((1,0),(11,10),(62,20)):self._capture(f,v)
        before=self._rows()
        with self.assertRaisesRegex(ValueError,'240 frames'):workflow.scale_pose_spacing(self.obj,1,4)
        self.assertEqual(self._rows(),before)
        self.obj.b4ml.anchors.clear();self._four();original=workflow._stored_anchor_frame
        def collapse(value):
            stored=original(value)
            return 6.000001 if abs(value-6.000001)<1e-4 else stored
        self.obj.b4ml.anchors.clear();self._capture(1,0);self._capture(1.00002,1)
        with self.assertRaises(ValueError):workflow.scale_pose_spacing(self.obj,1,.25)
        self.obj.b4ml.anchors.clear();self._four()
        def distort(value):
            stored=original(value);return original(stored+.2) if abs(value-26)<1e-4 else stored
        with mock.patch.object(workflow,'_stored_anchor_frame',side_effect=distort),self.assertRaisesRegex(ValueError,'spacing'):
            workflow.scale_pose_spacing(self.obj,6,2)
        frame_max=float(bpy.types.Scene.bl_rna.properties['frame_current'].hard_max)
        self.obj.b4ml.anchors.clear();self._capture(frame_max-20,0);self._capture(frame_max-10,1)
        with self.assertRaisesRegex(ValueError,'timeline frame range'):workflow.scale_pose_spacing(self.obj,frame_max-20,4)

    def test_stale_binding_malformed_ambiguous_busy_motion_and_nla(self):
        self._four();context=workflow.pose_spacing_scale_context(self.obj,6)
        self._anchor(16).name+=' changed';changed=self._rows()
        with self.assertRaisesRegex(ValueError,'Saved poses changed'):
            workflow.scale_pose_spacing(self.obj,6,2,context['binding'])
        self.assertEqual(self._rows(),changed);self.obj.b4ml.anchors.clear();self._four();baseline=self._rows()
        old=self._anchor(11).name;self._anchor(11).name='bad'
        with self.assertRaisesRegex(ValueError,'display name'):workflow.scale_pose_spacing(self.obj,6,2)
        self._anchor(11).name=old
        for field in ('temporal_running','body_running','body_live','contact_running','contact_suggest_running','flight_running','secondary_running','cleanup_running'):
            setattr(self.obj.b4ml,field,True)
            with self.assertRaisesRegex(ValueError,'active animation workflow'):workflow.scale_pose_spacing(self.obj,6,2)
            setattr(self.obj.b4ml,field,False)
        with mock.patch.object(workflow.motion_layer,'find',return_value=object()),self.assertRaisesRegex(ValueError,'kept motion source'):
            workflow.scale_pose_spacing(self.obj,6,2)
        track=self.obj.animation_data.nla_tracks.new();track.strips.new('Scale',1,self.obj.animation_data.action);track.mute=False
        with self.assertRaisesRegex(ValueError,'Mute NLA'):workflow.scale_pose_spacing(self.obj,6,2)
        self.obj.animation_data.nla_tracks.remove(track);self.assertEqual(self._rows(),baseline)

    def test_partial_and_topology_failures_restore_exact_semantic_state(self):
        self._four();self.obj.b4ml.status='prior';baseline=self._rows();untouched=self._untouched();original=workflow._write_retimed_anchor
        for mutation in ('raise','clear','remove','add','move'):
            calls=[]
            def fail(anchor,destination,name,kind=mutation):
                original(anchor,destination,name);calls.append(1)
                if len(calls)>1:return
                anchors=self.obj.b4ml.anchors
                if kind=='raise':raise RuntimeError('forced write')
                if kind=='clear':anchors.clear()
                elif kind=='remove':anchors.remove(0)
                elif kind=='add':
                    a=anchors.add();a.frame=99;a.name='Frame 99 - injected';a.payload=baseline[0][2]
                else:anchors.move(0,1)
            with self.subTest(mutation=mutation),mock.patch.object(workflow,'_write_retimed_anchor',side_effect=fail),self.assertRaises(Exception):
                workflow.scale_pose_spacing(self.obj,6,2)
            self.assertEqual(self._rows(),baseline);self.assertEqual(self.obj.b4ml.status,'prior');self.assertEqual(self._untouched(),untouched)

    def test_operator_save_reload_and_preview_use_scaled_frames(self):
        self._four();payloads=[self._anchor(f).payload for f in (1,6,11,16)];digest=self._digest()
        context=workflow.pose_spacing_scale_context(self.obj,6)
        self.assertEqual(bpy.ops.b4ml.pose_spacing_scale('EXEC_DEFAULT',pivot_frame=6,factor=2,moved_count=2,source_binding=context['binding']),{'FINISHED'})
        self.assertEqual(self._sorted_frames(),[1,6,16,26]);self.assertEqual([self._anchor(f).payload for f in (1,6,16,26)],payloads)
        self.assertEqual(bpy.ops.b4ml.action(operation='PREVIEW'),{'FINISHED'});self.scene.frame_set(16);self.assertAlmostEqual(self.hips.location.x,10)
        self.assertEqual(bpy.ops.b4ml.action(operation='DISCARD'),{'FINISHED'});self.assertEqual(self._digest(),digest)
        with tempfile.TemporaryDirectory() as directory:
            path=str(Path(directory)/'pose-spacing-scale-v1.blend');bpy.ops.wm.save_as_mainfile(filepath=path);bpy.ops.wm.open_mainfile(filepath=path,load_ui=False,use_scripts=False)
            self.scene=bpy.context.scene;self.obj=bpy.data.objects['Pose Scale Rig'];self.hips=self.obj.pose.bones['hips']
            self.assertEqual(self._sorted_frames(),[1,6,16,26]);self.assertEqual(self._digest(),digest)

    def test_context_binding_covers_order_frame_name_and_payload(self):
        for mutation in ('order','frame','name','payload'):
            self.obj.b4ml.anchors.clear();self._four();context=workflow.pose_spacing_scale_context(self.obj,6)
            if mutation=='order':self.obj.b4ml.anchors.move(3,0)
            elif mutation=='frame':self._anchor(16).frame=16.25
            elif mutation=='name':self._anchor(16).name+=' changed'
            else:
                value=json.loads(self._anchor(16).payload);value['changed']=True;self._anchor(16).payload=json.dumps(value)
            changed=self._rows()
            with self.subTest(mutation=mutation),self.assertRaisesRegex(ValueError,'Saved poses changed'):
                workflow.scale_pose_spacing(self.obj,6,2,context['binding'])
            self.assertEqual(self._rows(),changed)


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PoseSpacingScaleTests))
    if not result.wasSuccessful():raise SystemExit(1)
