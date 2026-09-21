"""Bforartists behavioral tests for contact interval inspection and trimming."""
from pathlib import Path
import hashlib
import json
import math
import os
import sys
import time
import traceback
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]

import addon_utils
import bpy
import b4artists_ml
from b4artists_ml import contacts,posing,rig_state,ui,workflow
from test_b4artists_ml_contacts import fixture
from test_b4artists_ml_quadruped_contacts import _candidate,_signature as _quadruped_signature

RECORDS=[]


def _sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _contact_state(obj):
    return [(item.name,item.enabled,item.review_state,item.limb,item.start,item.end,item.blend,
             item.strength,tuple(item.point),tuple(item.rotation),tuple(item.offset),
             item.lock_rotation) for item in obj.b4ml.contacts]


def _protected(obj):
    return dict(action=obj.animation_data.action,action_signature=contacts._action_signature(obj),
                pose=workflow.raw_pose(obj),modes=rig_state.mode_values(obj),
                matrix=tuple(v for row in obj.matrix_world for v in row),contacts=_contact_state(obj))


def _assert_protected(case,obj,before,contacts_too=True):
    case.assertIs(obj.animation_data.action,before['action'])
    case.assertEqual(contacts._action_signature(obj),before['action_signature'])
    case.assertEqual(workflow.raw_pose(obj),before['pose'])
    case.assertEqual(rig_state.mode_values(obj),before['modes'])
    case.assertEqual(tuple(v for row in obj.matrix_world for v in row),before['matrix'])
    if contacts_too:case.assertEqual(_contact_state(obj),before['contacts'])


class ContactIntervalEditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():raise unittest.SkipTest('Bforartists required')
        addon_utils.enable('rigify',default_set=True,persistent=False)
        b4artists_ml.register()

    def test_humanoid_jump_and_fractional_trim_preserve_animation(self):
        obj,_,_,_=fixture('rigify_default');scene=bpy.context.scene;item=obj.b4ml.contacts[0]
        item.start=2.25;item.end=9.75;obj.b4ml.contact_index=0
        before=_protected(obj);contacts.edit_interval(obj,scene,'GO_START')
        self.assertAlmostEqual(posing._frame(scene),2.25);self.assertEqual(_contact_state(obj),before['contacts'])
        contacts.edit_interval(obj,scene,'GO_END');self.assertAlmostEqual(posing._frame(scene),9.75)
        scene.frame_set(5,subframe=.5);self.assertEqual(bpy.ops.b4ml.contact(operation='SET_START'),{'FINISHED'})
        self.assertAlmostEqual(item.start,5.5);self.assertEqual(item.end,9.75)
        self.assertIs(obj.animation_data.action,before['action'])
        self.assertEqual(contacts._action_signature(obj),before['action_signature'])
        self.assertEqual(rig_state.mode_values(obj),before['modes'])
        RECORDS.append(dict(workflow='humanoid_fractional_trim',start=item.start,end=item.end))

    def test_operator_metadata_and_interval_roundtrip(self):
        obj,_,_,_=fixture('boneforge');scene=bpy.context.scene;item=obj.b4ml.contacts[0]
        item.start=2.;item.end=10.;obj.b4ml.contact_index=0;scene.frame_set(8,subframe=.25)
        self.assertIn('UNDO',ui.B4ML_OT_contact.bl_options)
        self.assertEqual(bpy.ops.b4ml.contact(operation='SET_END'),{'FINISHED'})
        self.assertAlmostEqual(item.end,8.25)
        RECORDS.append(dict(workflow='undoable_operator',end=item.end))

    def test_invalid_bounds_overlap_and_busy_state_are_atomic(self):
        obj,_,_,_=fixture('boneforge');scene=bpy.context.scene;first=obj.b4ml.contacts[0]
        first.start=4.;first.end=8.;first.blend=0.;obj.b4ml.contact_index=0
        other=obj.b4ml.contacts.add();other.name='Earlier left hold';other.limb=first.limb
        other.start=1.;other.end=3.;other.blend=0.;other.strength=1.;other.point=first.point
        other.rotation=first.rotation;other.offset=first.offset;other.lock_rotation=first.lock_rotation
        scene.frame_set(2,subframe=.5);before=_protected(obj)
        with self.assertRaisesRegex(ValueError,'overlap'):
            contacts.edit_interval(obj,scene,'SET_START')
        _assert_protected(self,obj,before)
        scene.frame_set(9);before=_protected(obj)
        with self.assertRaisesRegex(ValueError,'start must not be after'):
            contacts.edit_interval(obj,scene,'SET_START')
        _assert_protected(self,obj,before)
        scene.frame_set(6);before=_protected(obj);obj.b4ml.contact_running=True
        with self.assertRaisesRegex(ValueError,'active solve'):
            contacts.edit_interval(obj,scene,'SET_END')
        obj.b4ml.contact_running=False;_assert_protected(self,obj,before)
        frame=posing._frame(scene);obj.b4ml.temporal_running=True
        with self.assertRaisesRegex(ValueError,'active solve'):
            contacts.edit_interval(obj,scene,'GO_START')
        obj.b4ml.temporal_running=False;self.assertAlmostEqual(posing._frame(scene),frame)
        _assert_protected(self,obj,before)

    def test_rejected_or_missing_candidate_cannot_be_trimmed(self):
        obj,_,_,_=fixture();scene=bpy.context.scene;item=obj.b4ml.contacts[0]
        obj.b4ml.contact_index=0;scene.frame_set(5);item.review_state='REJECTED';item.enabled=False
        before=_protected(obj)
        with self.assertRaisesRegex(ValueError,'Enable and accept or propose'):
            contacts.edit_interval(obj,scene,'SET_START')
        _assert_protected(self,obj,before)
        item.review_state='ACCEPTED';item.enabled=True;obj.animation_data.action=None;before=_contact_state(obj)
        with self.assertRaisesRegex(ValueError,'Generate and select'):
            contacts.edit_interval(obj,scene,'SET_START')
        self.assertEqual(_contact_state(obj),before)

    def test_generated_quadruped_uses_same_validated_controls(self):
        scene,obj,source,source_signature,candidate,candidate_signature,_=_candidate('cat')
        item=obj.b4ml.contacts[0];obj.b4ml.contact_index=0;scene.frame_set(3,subframe=.5)
        self.assertEqual(bpy.ops.b4ml.contact(operation='SET_START'),{'FINISHED'})
        scene.frame_set(9,subframe=.25);self.assertEqual(bpy.ops.b4ml.contact(operation='SET_END'),{'FINISHED'})
        self.assertAlmostEqual(item.start,3.5);self.assertAlmostEqual(item.end,9.25)
        self.assertEqual(_quadruped_signature(obj,candidate),candidate_signature)
        self.assertEqual(_quadruped_signature(obj,source),source_signature)
        RECORDS.append(dict(workflow='generated_quadruped_trim',start=item.start,end=item.end))

    def test_save_reload_preserves_fractional_boundaries(self):
        obj,_,_,_=fixture('boneforge');scene=bpy.context.scene;obj.b4ml.contact_index=0
        scene.frame_set(3,subframe=.125);contacts.edit_interval(obj,scene,'SET_START')
        scene.frame_set(8,subframe=.875);contacts.edit_interval(obj,scene,'SET_END')
        name=obj.name;path=ROOT/'training/b4artists_ml/cache/contact-interval-edit-v1.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path),use_scripts=False)
        obj=bpy.data.objects[name];self.assertAlmostEqual(obj.b4ml.contacts[0].start,3.125)
        self.assertAlmostEqual(obj.b4ml.contacts[0].end,8.875)


def run_ui_smoke():
    ContactIntervalEditTests.setUpClass();obj,_,_,_=fixture('rigify_default');scene=bpy.context.scene
    item=obj.b4ml.contacts[0];item.start=2.;item.end=10.;obj.b4ml.contact_index=0
    state=dict(name=obj.name,phase='open',started=time.monotonic(),events=[])
    def tick():
        try:
            if time.monotonic()-state['started']>45:raise AssertionError('Contact interval UI timed out')
            win=bpy.context.window_manager.windows[0];area=next(a for a in win.screen.areas if a.type=='VIEW_3D')
            scene=win.scene
            region=next(r for r in area.regions if r.type=='WINDOW');area.spaces.active.show_region_ui=True
            ui_region=next(r for r in area.regions if r.type=='UI')
            for r in area.regions:
                if r.type=='UI' and hasattr(r,'active_panel_category'):r.active_panel_category='B4Artists ML'
            obj=bpy.data.objects[state['name']];win.view_layer.objects.active=obj;obj.select_set(True)
            with bpy.context.temp_override(window=win,area=area,region=region):
                if state['phase']=='open':
                    win.event_simulate(type='ESC',value='PRESS');obj.b4ml.show_contacts=True
                    scene.frame_set(4,subframe=.5);bpy.ops.ed.undo_push(message='Interval edit baseline')
                    assert bpy.ops.b4ml.contact(operation='SET_START')=={'FINISHED'}
                    assert math.isclose(obj.b4ml.contacts[0].start,4.5);state['events'].append('Set Start used fractional playhead')
                    bpy.ops.ed.undo_push(message='Contact interval start changed')
                    assert bpy.ops.ed.undo()=={'FINISHED'};state['phase']='redo'
                elif state['phase']=='redo':
                    obj=bpy.context.view_layer.objects.active;assert math.isclose(obj.b4ml.contacts[0].start,2.)
                    assert bpy.ops.ed.redo()=={'FINISHED'};state['phase']='inspect'
                elif state['phase']=='inspect':
                    obj=bpy.context.view_layer.objects.active;assert math.isclose(obj.b4ml.contacts[0].start,4.5)
                    assert bpy.ops.b4ml.contact(operation='GO_END')=={'FINISHED'}
                    assert math.isclose(posing._frame(scene),10.);state['events'].append('Undo Redo and Go End passed')
                    with bpy.context.temp_override(window=win,area=area,region=ui_region):
                        for _ in range(8):bpy.ops.view2d.scroll_down(deltay=6)
                    state['phase']='screenshot';return .35
                elif state['phase']=='screenshot':
                    obj=bpy.context.view_layer.objects.active
                    path=ROOT/'training/b4artists_ml/cache/contact-interval-edit-ui-v1.png'
                    bpy.ops.screen.screenshot(filepath=str(path));report=dict(passed=True,fixture='rigify_default',
                        events=state['events'],start=obj.b4ml.contacts[0].start,end=obj.b4ml.contacts[0].end,
                        screenshot=str(path.relative_to(ROOT)),elapsed_seconds=time.monotonic()-state['started'])
                    (ROOT/'docs/b4artists_ml/contact-interval-edit-ui-v1.json').write_text(json.dumps(report,indent=2)+'\n')
                    print('CONTACT_INTERVAL_UI_RESULT: '+json.dumps(report),flush=True);bpy.ops.wm.quit_blender();return None
        except Exception as exc:
            report=dict(passed=False,phase=state['phase'],error=str(exc),traceback=traceback.format_exc(),events=state['events'])
            (ROOT/'docs/b4artists_ml/contact-interval-edit-ui-v1.json').write_text(json.dumps(report,indent=2)+'\n')
            print('CONTACT_INTERVAL_UI_RESULT: '+json.dumps(report),flush=True);bpy.ops.wm.quit_blender();return None
        return .05
    bpy.app.timers.register(tick,first_interval=.5)


def run():
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ContactIntervalEditTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report=dict(tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),errors=len(result.errors),
                skips=len(result.skipped),records=RECORDS,package=b4artists_ml.__file__,runtime_sha256={
                    'contacts':_sha(contacts.__file__),'ui':_sha(ROOT/'b4artists_ml/ui.py')})
    (ROOT/'training/b4artists_ml/results/contact-interval-edit-v1.json').write_text(json.dumps(report,indent=2)+'\n')
    print('CONTACT_INTERVAL_EDIT_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)


if __name__=='__main__' and '--ui-smoke' in sys.argv:run_ui_smoke()
elif __name__=='__main__':run()
