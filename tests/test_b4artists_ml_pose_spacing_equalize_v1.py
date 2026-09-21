"""Bforartists tests for constant spacing of later priority-pose frames."""
from pathlib import Path
import json, math, os, sys, unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]
import bpy
from mathutils import Quaternion
import b4artists_ml
from b4artists_ml import quadruped_gait, workflow


class PoseSpacingEqualizeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():raise unittest.SkipTest('Bforartists required')
        b4artists_ml.register()

    def setUp(self):
        if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
        data=bpy.data.armatures.new('Pose Equalize Rig')
        self.obj=bpy.data.objects.new('Pose Equalize Rig',data)
        bpy.context.scene.collection.objects.link(self.obj)
        bpy.context.view_layer.objects.active=self.obj;self.obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        for i,name in enumerate(('hips','upperarm.fk-L','thigh.fk-R')):
            bone=data.edit_bones.new(name);bone.head=(i,0,0);bone.tail=(i,0,1)
        bpy.ops.object.mode_set(mode='POSE');self.hips=self.obj.pose.bones['hips']
        self.hips.rotation_mode='QUATERNION';self.scene=bpy.context.scene
        self.scene.tool_settings.use_keyframe_insert_auto=False;self.scene.frame_set(1)

    def tearDown(self):
        self.scene=bpy.context.scene;self.scene.tool_settings.use_keyframe_insert_auto=False
        if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
        obj=bpy.data.objects.get('Pose Equalize Rig')
        if obj:
            data=obj.data;bpy.data.objects.remove(obj,do_unlink=True)
            if not data.users:bpy.data.armatures.remove(data)

    def _frame(self,value):
        base=math.floor(value);self.scene.frame_set(base,subframe=value-base)

    def _capture(self,frame,value):
        self._frame(frame);self.hips.location.x=value
        self.hips.rotation_quaternion=Quaternion((0,0,1),math.radians(value*7))
        self.hips.keyframe_insert('location',frame=frame)
        self.hips.keyframe_insert('rotation_quaternion',frame=frame)
        workflow.capture_anchor(self.obj,self.scene)

    def _capture_many(self,frames):
        for index,frame in enumerate(frames):self._capture(frame,float(index+1))

    def _sorted(self):
        return sorted((float(a.frame),a.name,a.payload) for a in self.obj.b4ml.anchors)

    def _digest(self):
        return quadruped_gait._action_digest(self.obj,self.obj.animation_data.action)

    def _state(self):
        ad=self.obj.animation_data
        return (ad.action,getattr(ad,'action_slot',None),self._digest(),
                self.scene.frame_current,self.scene.frame_subframe,
                self.scene.tool_settings.use_keyframe_insert_auto,
                [(b.name,tuple(b.location),tuple(b.rotation_quaternion),b.rotation_mode,bool(b.select))
                 for b in self.obj.pose.bones])

    def test_equalizes_irregular_later_poses_and_preserves_owned_data(self):
        self._capture_many((1,6,14,25))
        workflow.set_transition_timing(self.obj,14,True,'EASE_OUT',-.2,.1,.3)
        for frame,label in ((14,'anticipation'),(25,'landing')):
            anchor=next(a for a in self.obj.b4ml.anchors if abs(a.frame-frame)<1e-5)
            anchor.name+=' ('+label+')'
        before=self._sorted();payloads=[row[2] for row in before]
        suffixes=[row[1].split(' - ',1)[1] for row in before];runtime=self._state()
        result=workflow.equalize_pose_spacing(self.obj,6,4)
        rows=self._sorted()
        self.assertEqual([row[0] for row in rows],[1,6,10,14])
        self.assertEqual([row[2] for row in rows],payloads)
        self.assertEqual([row[1].split(' - ',1)[1] for row in rows],suffixes)
        self.assertEqual(result,{'pivot_frame':6.0,'interval':4.0,'moved_count':2})
        self.assertEqual(self.obj.b4ml.status,
                         'Equalized 2 later priority poses to 4-frame spacing')
        self.assertEqual(self._state(),runtime)

    def test_fractional_expansion_uses_exact_constant_intervals(self):
        self._capture_many((1,3,7,12))
        workflow.equalize_pose_spacing(self.obj,1,2)
        self.assertEqual([row[0] for row in self._sorted()],[1,3,5,7])
        self.assertEqual(self.obj.b4ml.status,
                         'Equalized 2 later priority poses to 2-frame spacing')
        workflow.equalize_pose_spacing(self.obj,1,7.5)
        frames=[row[0] for row in self._sorted()]
        self.assertEqual(frames,[1,8.5,16,23.5])
        self.assertEqual([frames[i+1]-frames[i] for i in range(3)],[7.5,7.5,7.5])

    def test_context_defaults_to_first_interval_and_binds_complete_collection(self):
        self._capture_many((1,6,14,25))
        context=workflow.pose_spacing_equalize_context(self.obj,6)
        self.assertEqual({key:context[key] for key in ('pivot_frame','interval','affected_count')},
                         {'pivot_frame':6.0,'interval':8.0,'affected_count':2})
        self.assertEqual(len(context['binding']),64)
        next(a for a in self.obj.b4ml.anchors if abs(a.frame-25)<1e-5).name+=' changed'
        before=self._sorted()
        with self.assertRaisesRegex(ValueError,'Saved poses changed'):
            workflow.equalize_pose_spacing(self.obj,6,4,context['binding'])
        self.assertEqual(self._sorted(),before)

    def test_rejects_invalid_or_noop_interval_before_mutation(self):
        self._capture_many((1,6,11,16));before=self._sorted()
        for value in (True,float('nan'),float('inf'),.1,241):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError,'Equal pose interval'):
                    workflow.equalize_pose_spacing(self.obj,1,value)
                self.assertEqual(self._sorted(),before)
        with self.assertRaisesRegex(ValueError,'already use this interval'):
            workflow.equalize_pose_spacing(self.obj,1,5)
        self.assertEqual(self._sorted(),before)

    def test_rejects_missing_last_and_ambiguous_pivots(self):
        self._capture_many((1,6,14));before=self._sorted()
        for pivot,reason in ((30,'missing or ambiguous'),(14,'at least one later')):
            with self.subTest(pivot=pivot):
                with self.assertRaisesRegex(ValueError,reason):
                    workflow.equalize_pose_spacing(self.obj,pivot,4)
                self.assertEqual(self._sorted(),before)
        duplicate=self.obj.b4ml.anchors.add();duplicate.frame=6
        duplicate.name='Frame 6 - duplicate';duplicate.payload=json.dumps({'pose':{}})
        with self.assertRaisesRegex(ValueError,'finite and distinct'):
            workflow.equalize_pose_spacing(self.obj,6,4)

    def test_rejects_busy_motion_layer_nla_and_bounded_span(self):
        self._capture_many((1,6,14,25));before=self._sorted()
        self.obj.b4ml.temporal_running=True
        with self.assertRaisesRegex(ValueError,'active animation workflow'):
            workflow.equalize_pose_spacing(self.obj,6,4)
        self.obj.b4ml.temporal_running=False
        with mock.patch.object(workflow.motion_layer,'find',return_value=object()):
            with self.assertRaisesRegex(ValueError,'kept motion source'):
                workflow.equalize_pose_spacing(self.obj,6,4)
        track=self.obj.animation_data.nla_tracks.new()
        track.strips.new('Equalize',1,self.obj.animation_data.action);track.mute=False
        with self.assertRaisesRegex(ValueError,'Mute NLA'):
            workflow.equalize_pose_spacing(self.obj,6,4)
        self.obj.animation_data.nla_tracks.remove(track)
        with self.assertRaisesRegex(ValueError,'240 frames'):
            workflow.equalize_pose_spacing(self.obj,1,100)
        self.assertEqual(self._sorted(),before)

    def test_topology_changing_write_failure_restores_exact_rows_and_status(self):
        self._capture_many((1,6,14,25));self.obj.b4ml.status='baseline status'
        before=self._sorted();original=workflow._write_retimed_anchor
        def hostile(anchor,frame,name):
            original(anchor,frame,name);self.obj.b4ml.anchors.clear()
            raise RuntimeError('hostile callback')
        with mock.patch.object(workflow,'_write_retimed_anchor',side_effect=hostile):
            with self.assertRaisesRegex(RuntimeError,'hostile callback'):
                workflow.equalize_pose_spacing(self.obj,6,4)
        self.assertEqual(self._sorted(),before)
        self.assertEqual(self.obj.b4ml.status,'baseline status')

    def test_operator_executes_with_stable_binding(self):
        self._capture_many((1,6,14,25));self.obj.b4ml.interpolation_method='POSES'
        context=workflow.pose_spacing_equalize_context(self.obj,6)
        result=bpy.ops.b4ml.pose_spacing_equalize(
            'EXEC_DEFAULT',pivot_frame=6,interval=4,affected_count=2,
            source_binding=context['binding'])
        self.assertEqual(result,{'FINISHED'})
        self.assertEqual([row[0] for row in self._sorted()],[1,6,10,14])


if __name__=='__main__':unittest.main()
