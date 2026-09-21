"""Bforartists behavioral tests for explicit humanoid hand-to-prop holds."""
from pathlib import Path
import hashlib,json,math,os,sys,time,traceback,unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]

import addon_utils
import bpy
from mathutils import Vector
import b4artists_ml
from b4artists_ml import contacts,posing,rig_state,ui,workflow
from test_b4artists_ml_posing import boneforge_rig,rigify_rig

RECORDS=[]


def _sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _make_prop_hold(label='boneforge',rotation=True):
    bpy.context.window.scene=bpy.data.scenes.new('Prop Hold '+label);scene=bpy.context.scene
    obj=rigify_rig(full=True) if label=='rigify_default' else boneforge_rig()
    bpy.context.view_layer.objects.active=obj;posing._update(obj);root=posing.bindings(obj)[1]
    scene.frame_set(1);obj.pose.bones[root].keyframe_insert('location',frame=1)
    source=obj.animation_data.action;workflow.capture_anchor(obj,scene)
    scene.frame_set(11);obj.pose.bones[root].keyframe_insert('location',frame=11);workflow.capture_anchor(obj,scene)
    source_signature=contacts._action_signature(obj);modes=rig_state.mode_values(obj);workflow.preview(obj,scene)
    obj.b4ml.contacts.clear();scene.frame_set(3);obj.b4ml.contact_limb='arm-R'
    item=contacts.capture(obj,scene);item.start=3.;item.end=9.;item.blend=1.;item.lock_rotation=rotation
    row=next(row for row in posing.bindings(obj)[2] if row['id']=='arm-R')
    hand=workflow.display_world(obj)@obj.pose.bones[row['joints'][2]].matrix
    prop=bpy.data.objects.new('Animator Prop',None);scene.collection.objects.link(prop);prop.matrix_world=hand
    base=prop.location.copy();shoulder=workflow.display_world(obj)@obj.pose.bones[row['joints'][0]].head
    inward=(shoulder-hand.translation).normalized()*.015
    for frame,delta,angle in ((3.,0.,0.),(9.,1.,.03)):
        scene.frame_set(int(frame));prop.location=base+inward*delta;prop.rotation_euler[2]=angle
        prop.keyframe_insert('location',frame=frame);prop.keyframe_insert('rotation_euler',frame=frame)
    for curve in workflow.action_curves(prop.animation_data.action,getattr(prop.animation_data,'action_slot',None)):
        for key in curve.keyframe_points:key.interpolation='LINEAR'
    scene.frame_set(3);item.prop_object=prop;obj.b4ml.contact_index=0
    contacts.edit_prop_binding(obj,scene,'BIND_PROP')
    scene.frame_set(6)
    return obj,scene,item,prop,source,source_signature,modes


def _state(obj,item,prop):
    return dict(candidate=obj.b4ml.candidate_action,candidate_signature=contacts._action_signature(obj),
        pose=workflow.raw_pose(obj),modes=rig_state.mode_values(obj),matrix=tuple(v for row in obj.matrix_world for v in row),
        item=(item.prop_bound,item.prop_name,item.prop_object,tuple(item.prop_point),tuple(item.prop_rotation),
              tuple(item.point),tuple(item.rotation)),prop_action=prop.animation_data.action,
        prop_signature=contacts._action_signature(prop))


class PropHoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():raise unittest.SkipTest('Bforartists required')
        addon_utils.enable('rigify',default_set=True,persistent=False);b4artists_ml.register()

    def test_moving_prop_position_and_rotation_follow_on_copied_candidate(self):
        obj,scene,item,prop,source,source_signature,modes=_make_prop_hold()
        original=obj.b4ml.candidate_action;original_signature=contacts._action_signature(obj)
        prop_action=prop.animation_data.action;prop_signature=contacts._action_signature(prop)
        report=contacts.solve(obj,scene)
        self.assertEqual(report['prop_relative_contacts'],1);self.assertEqual(report['prop_objects'],[prop.name])
        self.assertEqual(report['prop_target_space'],'evaluated object-local')
        self.assertIsNot(obj.b4ml.candidate_action,original);self.assertTrue(original.use_fake_user)
        stored=json.loads(obj.b4ml.candidate_action['b4ml_contacts'])[0]
        self.assertEqual(stored['prop_object'],prop.name)
        self.assertNotIn('prop_identity',stored);self.assertNotIn('prop_pointer',stored)
        self.assertEqual(contacts._action_signature(obj,original),original_signature)
        self.assertEqual(contacts._action_signature(obj,source),source_signature)
        self.assertIs(prop.animation_data.action,prop_action);self.assertEqual(contacts._action_signature(prop),prop_signature)
        self.assertEqual(rig_state.mode_values(obj),modes)
        row=next(row for row in posing.bindings(obj)[2] if row['id']=='arm-R')
        reference=sum((obj.pose.bones[row['joints'][i+1]].head-obj.pose.bones[row['joints'][i]].head).length for i in (0,1))*workflow.display_world(obj).to_scale().x
        maximum=rotation_error=0.
        for frame in (3.,4.5,6.,7.5,9.):
            scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame));posing._update(obj)
            expected=prop.matrix_world@Vector(item.prop_point);actual=contacts._point(obj,row,item.offset)
            maximum=max(maximum,(actual-expected).length/reference)
            desired=(prop.matrix_world.to_quaternion()@item.prop_rotation).normalized()
            actual_rotation=(workflow.display_world(obj)@obj.pose.bones[row['joints'][2]].matrix).to_quaternion()
            rotation_error=max(rotation_error,contacts._angle(actual_rotation,desired))
        self.assertLess(maximum,2e-4);self.assertLess(rotation_error,.001)
        RECORDS.append(dict(workflow='animated_rigid_prop',position_error=maximum,rotation_error=rotation_error,
            source_preserved=True,prop_animation_preserved=True))

    def test_bind_clear_and_operator_metadata_preserve_animation(self):
        obj,scene,item,prop,_,_,_=_make_prop_hold(rotation=False);before=_state(obj,item,prop)
        self.assertIn('UNDO',ui.B4ML_OT_contact.bl_options)
        enum_items=ui.B4ML_OT_contact.__annotations__['operation'].keywords['items']
        self.assertIn('BIND_PROP',{value[0] for value in enum_items})
        self.assertEqual(bpy.ops.b4ml.contact(operation='CLEAR_PROP'),{'FINISHED'})
        self.assertFalse(item.prop_bound);self.assertIsNone(item.prop_object);self.assertEqual(item.prop_name,'')
        self.assertIs(obj.b4ml.candidate_action,before['candidate'])
        self.assertEqual(contacts._action_signature(obj),before['candidate_signature'])
        self.assertEqual(workflow.raw_pose(obj),before['pose']);self.assertEqual(rig_state.mode_values(obj),before['modes'])
        self.assertEqual(contacts._action_signature(prop),before['prop_signature'])
        item.prop_object=prop;self.assertEqual(bpy.ops.b4ml.contact(operation='BIND_PROP'),{'FINISHED'})
        self.assertTrue(item.prop_bound);self.assertEqual(item.prop_name,prop.name)
        RECORDS.append(dict(workflow='undoable_bind_clear',animation_preserved=True))

    def test_invalid_targets_and_support_patch_refuse_atomically(self):
        obj,scene,item,prop,_,_,_=_make_prop_hold(rotation=False);contacts.edit_prop_binding(obj,scene,'CLEAR_PROP')
        baseline=_state(obj,item,prop)
        item.prop_object=obj
        with self.assertRaisesRegex(ValueError,'own prop'):contacts.edit_prop_binding(obj,scene,'BIND_PROP')
        self.assertEqual(contacts._action_signature(obj),baseline['candidate_signature'])
        child=bpy.data.objects.new('Parented Prop',None);scene.collection.objects.link(child);child.parent=prop;item.prop_object=child
        with self.assertRaisesRegex(ValueError,'unparented'):contacts.edit_prop_binding(obj,scene,'BIND_PROP')
        outside_scene=bpy.data.scenes.new('Outside Prop Scene');outside=bpy.data.objects.new('Outside Prop',None)
        outside_scene.collection.objects.link(outside);item.prop_object=outside
        with self.assertRaisesRegex(ValueError,'character scene'):contacts.edit_prop_binding(obj,scene,'BIND_PROP')
        excluded_collection=bpy.data.collections.new('Excluded Prop Collection')
        scene.collection.children.link(excluded_collection);excluded=bpy.data.objects.new('Excluded Prop',None)
        excluded_collection.objects.link(excluded);working_layer=scene.view_layers.new('Working Prop Layer')
        working_layer.layer_collection.children[excluded_collection.name].exclude=True
        item.prop_object=excluded
        with bpy.context.temp_override(scene=scene,view_layer=working_layer):
            with self.assertRaisesRegex(ValueError,'visible'):
                contacts.edit_prop_binding(obj,scene,'BIND_PROP',working_layer)
        bpy.context.view_layer.objects.active=obj
        item.prop_object=prop;item.use_support=True
        with self.assertRaisesRegex(ValueError,'support-patch'):contacts.edit_prop_binding(obj,scene,'BIND_PROP')
        item.use_support=False;prop.hide_set(True,view_layer=scene.view_layers[0])
        with self.assertRaisesRegex(ValueError,'visible'):contacts.edit_prop_binding(obj,scene,'BIND_PROP')
        prop.hide_set(False,view_layer=scene.view_layers[0]);prop.delta_scale=(1.,1.,1.)
        prop.keyframe_insert('delta_scale',frame=3)
        with self.assertRaisesRegex(ValueError,'animated prop scale'):contacts.edit_prop_binding(obj,scene,'BIND_PROP')
        bpy.ops.mesh.primitive_cube_add();rigid=bpy.context.object;bpy.ops.rigidbody.object_add();item.prop_object=rigid
        with self.assertRaisesRegex(ValueError,'rigid-body'):contacts.edit_prop_binding(obj,scene,'BIND_PROP')
        bpy.context.view_layer.objects.active=obj
        self.assertFalse(item.prop_bound);self.assertEqual(item.prop_name,'')
        self.assertEqual(contacts._action_signature(obj),baseline['candidate_signature'])
        self.assertEqual(workflow.raw_pose(obj),baseline['pose']);self.assertEqual(rig_state.mode_values(obj),baseline['modes'])

    def test_retarget_or_prop_animation_edit_aborts_and_restores(self):
        obj,scene,item,prop,_,_,_=_make_prop_hold(rotation=False);before=_state(obj,item,prop)
        replacement=bpy.data.objects.new('Replacement Prop',None);scene.collection.objects.link(replacement)
        item.prop_object=replacement
        self.assertIs(item.prop_target,prop);self.assertEqual(contacts.rows(obj)[0]['prop_object'],prop.name)
        name=prop.name;bpy.data.objects.remove(prop,do_unlink=True);replacement.name=name;item.prop_object=replacement
        with self.assertRaisesRegex(ValueError,'committed prop'):contacts.solve(obj,scene)
        self.assertIs(obj.b4ml.candidate_action,before['candidate'])
        obj,scene,item,prop,_,_,_=_make_prop_hold(rotation=False);before=_state(obj,item,prop)
        iterator=contacts.correction_steps(obj,scene);next(iterator)
        curve=workflow.action_curves(prop.animation_data.action,getattr(prop.animation_data,'action_slot',None))[0]
        curve.modifiers.new('LIMITS')
        with self.assertRaisesRegex(ValueError,'curve modifiers'):next(iterator)
        iterator.close()
        self.assertIs(obj.b4ml.candidate_action,before['candidate'])
        self.assertEqual(contacts._action_signature(obj),before['candidate_signature'])
        self.assertEqual(workflow.raw_pose(obj),before['pose']);self.assertEqual(rig_state.mode_values(obj),before['modes'])
        obj,scene,item,prop,_,_,_=_make_prop_hold(rotation=False);before=_state(obj,item,prop)
        iterator=contacts.correction_steps(obj,scene);next(iterator)
        prop.animation_data.action_influence=.5
        with self.assertRaisesRegex(ValueError,'Bound prop changed'):next(iterator)
        iterator.close();self.assertIs(obj.b4ml.candidate_action,before['candidate'])
        self.assertEqual(contacts._action_signature(obj),before['candidate_signature'])
        obj,scene,item,prop,_,_,_=_make_prop_hold(rotation=False);before=_state(obj,item,prop)
        iterator=contacts.correction_steps(obj,scene);next(iterator)
        prop.animation_data.action.layers[0].name='Changed During Hold'
        with self.assertRaisesRegex(ValueError,'Bound prop changed'):next(iterator)
        iterator.close();self.assertIs(obj.b4ml.candidate_action,before['candidate'])
        self.assertEqual(contacts._action_signature(obj),before['candidate_signature'])
        RECORDS.append(dict(workflow='changed_target_fail_closed',candidate_restored=True))

    def test_generated_rigify_default_and_save_reload_binding(self):
        obj,scene,item,prop,_,_,_=_make_prop_hold('rigify_default',rotation=False)
        self.assertGreaterEqual(len(obj.pose.bones),128)
        item.end=4.;item.blend=0.;report=contacts.solve(obj,scene)
        row=next(row for row in posing.bindings(obj)[2] if row['id']=='arm-R')
        scene.frame_set(4);posing._update(obj)
        error=(contacts._point(obj,row,item.offset)-prop.matrix_world@item.prop_point).length
        self.assertLess(error,1e-4);self.assertEqual(report['prop_relative_contacts'],1)
        name=obj.name;prop_name=prop.name;path=ROOT/'training/b4artists_ml/cache/prop-hold-v1.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path),use_scripts=False)
        obj=bpy.data.objects[name];prop=bpy.data.objects[prop_name];item=obj.b4ml.contacts[0]
        self.assertTrue(item.prop_bound);self.assertIs(item.prop_object,prop);self.assertIs(item.prop_target,prop)
        self.assertEqual(item.prop_name,prop.name)
        row=contacts.rows(obj)[0];self.assertTrue(row['prop_bound']);self.assertEqual(row['prop_object'],prop.name)
        resolved=contacts._resolved_contact(obj,row,bpy.context.scene)
        self.assertLess((Vector(resolved['point'])-prop.matrix_world@Vector(item.prop_point)).length,1e-8)
        RECORDS.append(dict(workflow='rigify_default_solve_save_reload',bones=len(obj.pose.bones),
            position_error=error,solver_ms=report['elapsed_ms'],binding_preserved=True))


def run():
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(PropHoldTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report=dict(tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),errors=len(result.errors),
        skips=len(result.skipped),records=RECORDS,package=b4artists_ml.__file__,runtime_sha256={
            'contacts':_sha(contacts.__file__),'ui':_sha(ROOT/'b4artists_ml/ui.py'),'test':_sha(__file__)})
    (ROOT/'training/b4artists_ml/results/prop-holds-v1.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PROP_HOLDS_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)


def run_ui_smoke():
    PropHoldTests.setUpClass();obj,_,item,prop,_,_,_=_make_prop_hold(rotation=False)
    obj.b4ml.show_contacts=True;state=dict(rig=obj.name,prop=prop.name,phase='operate',started=time.monotonic(),events=[])
    def tick():
        try:
            if time.monotonic()-state['started']>45:raise AssertionError('Prop Hold UI timed out')
            window=bpy.context.window_manager.windows[0];area=next(value for value in window.screen.areas if value.type=='VIEW_3D')
            region=next(value for value in area.regions if value.type=='WINDOW');sidebar=next(value for value in area.regions if value.type=='UI')
            area.spaces.active.show_region_ui=True
            for value in area.regions:
                if value.type=='UI' and hasattr(value,'active_panel_category'):value.active_panel_category='B4Artists ML'
            obj=bpy.data.objects[state['rig']];prop=bpy.data.objects[state['prop']]
            window.view_layer.objects.active=obj;obj.select_set(True);item=obj.b4ml.contacts[0]
            with bpy.context.temp_override(window=window,area=area,region=region,object=obj,active_object=obj,
                selected_objects=[obj],selected_editable_objects=[obj]):
                if state['phase']=='operate':
                    window.event_simulate(type='ESC',value='PRESS')
                    assert bpy.ops.b4ml.contact(operation='CLEAR_PROP')=={'FINISHED'};assert not item.prop_bound
                    item.prop_object=prop;assert bpy.ops.b4ml.contact(operation='BIND_PROP')=={'FINISHED'}
                    assert item.prop_bound and item.prop_target==prop
                    state['events'].append('Clear and Bind operators preserved explicit target ownership')
                    state['phase']='scroll';state['scrolls']=0;return .2
                if state['phase']=='scroll':
                    window.cursor_warp(sidebar.x+sidebar.width//2,sidebar.y+sidebar.height//2)
                    window.event_simulate(type='WHEELDOWNMOUSE',value='PRESS',
                        x=sidebar.x+sidebar.width//2,y=sidebar.y+sidebar.height//2)
                    state['scrolls']+=1
                    if state['scrolls']<16:return .04
                    state['phase']='capture';return .5
                path=ROOT/'training/b4artists_ml/cache/prop-hold-ui-v1.png';bpy.ops.screen.screenshot(filepath=str(path))
                report=dict(passed=True,fixture='boneforge',events=state['events'],bound=item.prop_bound,
                    target=item.prop_target.name if item.prop_target else None,screenshot=str(path.relative_to(ROOT)),
                    elapsed_seconds=time.monotonic()-state['started'])
                (ROOT/'docs/b4artists_ml/prop-hold-ui-v1.json').write_text(json.dumps(report,indent=2)+'\n')
                print('PROP_HOLD_UI_RESULT: '+json.dumps(report),flush=True);bpy.ops.wm.quit_blender();return None
        except Exception as exc:
            report=dict(passed=False,phase=state['phase'],error=str(exc),traceback=traceback.format_exc(),events=state['events'])
            (ROOT/'docs/b4artists_ml/prop-hold-ui-v1.json').write_text(json.dumps(report,indent=2)+'\n')
            print('PROP_HOLD_UI_RESULT: '+json.dumps(report),flush=True);bpy.ops.wm.quit_blender();return None
        return .05
    bpy.app.timers.register(tick,first_interval=.5)


if __name__=='__main__' and '--ui-smoke' in sys.argv:run_ui_smoke()
elif __name__=='__main__':run()
