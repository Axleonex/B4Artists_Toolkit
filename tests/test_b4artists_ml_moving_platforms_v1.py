"""Behavioral evidence for explicit moving rigid planar foot contacts."""
import hashlib,json,math,os,sys,time,traceback,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]
import addon_utils,bpy
from mathutils import Vector
import b4artists_ml
from b4artists_ml import contacts,posing,rig_state,ui,workflow
from test_b4artists_ml_contacts import fixture

RECORDS=[]


def _sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _platform(scene,point,name='Animator Platform',nonplanar=False):
    mesh=bpy.data.meshes.new(name+' Mesh')
    mesh.from_pydata([(-.7,-.7,0),(.7,-.7,0),(.7,.7,.08 if nonplanar else 0),(-.7,.7,0)],[],[(0,1,2,3)])
    mesh.update();target=bpy.data.objects.new(name,mesh);scene.collection.objects.link(target);target.location=point
    return target


def _setup(label='boneforge'):
    obj,source,source_signature,modes=fixture(label);scene=bpy.context.scene
    scene.frame_set(6);posing._update(obj);item=obj.b4ml.contacts[0];item.start=3.;item.end=9.;item.blend=0.
    row=next(row for row in posing.bindings(obj)[2] if row['id']==item.limb)
    samples={}
    for frame in (3,6,9):
        scene.frame_set(frame);posing._update(obj);point=contacts._point(obj,row,item.offset)
        hip=workflow.display_world(obj)@obj.pose.bones[row['joints'][0]].head
        samples[frame]=point+(hip-point).normalized()*.002
    platform=_platform(scene,samples[6])
    for frame,angle in ((3,-.02),(6,0.),(9,.02)):
        platform.location=samples[frame];platform.rotation_euler.z=angle
        platform.keyframe_insert('location',frame=frame);platform.keyframe_insert('rotation_euler',frame=frame)
    scene.frame_set(6);posing._update(obj);obj.b4ml.contact_index=0;item.prop_object=platform
    contacts.edit_prop_binding(obj,scene,'BIND_SURFACE',bpy.context.view_layer)
    return obj,scene,item,platform,source,source_signature,modes


class MovingPlatformTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not b4artists_ml.is_bforartists():raise unittest.SkipTest('Bforartists required')
        addon_utils.enable('rigify',default_set=True,persistent=False);b4artists_ml.register()

    def test_animated_platform_position_rotation_and_clear(self):
        obj,scene,item,platform,source,source_signature,modes=_setup()
        original=obj.b4ml.candidate_action;original_signature=contacts._action_signature(obj)
        platform_action=platform.animation_data.action;platform_signature=contacts._action_signature(platform)
        report=contacts.solve(obj,scene)
        self.assertEqual(report['moving_surface_contacts'],1);self.assertEqual(report['moving_surface_objects'],[platform.name])
        self.assertEqual(report['prop_relative_contacts'],0)
        self.assertEqual(report['moving_surface_target_space'],'evaluated planar-mesh object-local')
        stored=json.loads(obj.b4ml.candidate_action['b4ml_contacts'])[0]
        self.assertNotIn('prop_identity',stored);self.assertNotIn('prop_pointer',stored)
        self.assertEqual(contacts._action_signature(obj,original),original_signature)
        self.assertEqual(contacts._action_signature(obj,source),source_signature)
        self.assertIs(platform.animation_data.action,platform_action)
        self.assertEqual(contacts._action_signature(platform),platform_signature);self.assertEqual(rig_state.mode_values(obj),modes)
        row=next(row for row in posing.bindings(obj)[2] if row['id']==item.limb)
        reference=sum((obj.pose.bones[row['joints'][i+1]].head-obj.pose.bones[row['joints'][i]].head).length for i in (0,1))*workflow.display_world(obj).to_scale().x
        maximum=rotation_error=0.
        for frame in (3.,4.5,6.,7.5,9.):
            scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame));posing._update(obj)
            expected=platform.matrix_world@Vector(item.prop_point);actual=contacts._point(obj,row,item.offset)
            maximum=max(maximum,(actual-expected).length/reference)
            desired=(platform.matrix_world.to_quaternion()@item.prop_rotation).normalized()
            actual_rotation=(workflow.display_world(obj)@obj.pose.bones[row['joints'][2]].matrix).to_quaternion()
            rotation_error=max(rotation_error,contacts._angle(actual_rotation,desired))
        self.assertLess(maximum,2e-4);self.assertLess(rotation_error,.001)
        scene.frame_set(9);expected=platform.matrix_world@Vector(item.prop_point)
        contacts.edit_prop_binding(obj,scene,'CLEAR_SURFACE',bpy.context.view_layer)
        self.assertFalse(item.prop_bound);self.assertLess((Vector(item.point)-expected).length,1e-8)
        RECORDS.append(dict(workflow='animated_rigid_planar_platform',position_error=maximum,
            rotation_error=rotation_error,source_preserved=True,platform_animation_preserved=True))

    def test_invalid_platforms_and_changed_geometry_fail_closed(self):
        obj,scene,item,_,_,_,_=_setup();contacts.edit_prop_binding(obj,scene,'CLEAR_SURFACE',bpy.context.view_layer)
        original=obj.b4ml.candidate_action;signature=contacts._action_signature(obj);pose=workflow.raw_pose(obj)
        modes=rig_state.mode_values(obj);contact_state=(item.prop_bound,item.prop_target,item.prop_name,
            tuple(item.point),tuple(item.rotation),tuple(item.prop_point),tuple(item.prop_rotation))
        empty=bpy.data.objects.new('Not A Surface',None);scene.collection.objects.link(empty);item.prop_object=empty
        with self.assertRaisesRegex(ValueError,'planar mesh'):contacts.edit_prop_binding(obj,scene,'BIND_SURFACE',bpy.context.view_layer)
        bad=_platform(scene,Vector(item.point),'Bent Platform',nonplanar=True);item.prop_object=bad
        with self.assertRaisesRegex(ValueError,'must be planar'):contacts.edit_prop_binding(obj,scene,'BIND_SURFACE',bpy.context.view_layer)
        modified=_platform(scene,Vector(item.point),'Modified Platform');modified.modifiers.new('Visual Deform','DISPLACE');item.prop_object=modified
        with self.assertRaisesRegex(ValueError,'modifiers'):contacts.edit_prop_binding(obj,scene,'BIND_SURFACE',bpy.context.view_layer)
        shaped=_platform(scene,Vector(item.point),'Shape Key Platform');shaped.shape_key_add(name='Basis');item.prop_object=shaped
        with self.assertRaisesRegex(ValueError,'shape keys'):contacts.edit_prop_binding(obj,scene,'BIND_SURFACE',bpy.context.view_layer)
        far=_platform(scene,Vector(item.point)+Vector((0,0,1)),'Far Platform');item.prop_object=far
        with self.assertRaisesRegex(ValueError,'Place the captured foot'):contacts.edit_prop_binding(obj,scene,'BIND_SURFACE',bpy.context.view_layer)
        item.use_support=True;item.prop_object=far
        with self.assertRaisesRegex(ValueError,'support-patch'):contacts.edit_prop_binding(obj,scene,'BIND_SURFACE',bpy.context.view_layer)
        item.use_support=False
        self.assertIs(obj.b4ml.candidate_action,original);self.assertEqual(contacts._action_signature(obj),signature)
        self.assertEqual(workflow.raw_pose(obj),pose);self.assertEqual(rig_state.mode_values(obj),modes)
        self.assertEqual((item.prop_bound,item.prop_target,item.prop_name,tuple(item.point),tuple(item.rotation),
            tuple(item.prop_point),tuple(item.prop_rotation)),contact_state)
        obj,scene,item,platform,_,_,_=_setup();before=obj.b4ml.candidate_action;before_signature=contacts._action_signature(obj)
        scene.frame_set(6);obj.b4ml.contact_limb='arm-R';hand=contacts.capture(obj,scene)
        hand.start=3.;hand.end=9.;hand.blend=0.;hand.prop_object=platform
        contacts.edit_prop_binding(obj,scene,'BIND_PROP',bpy.context.view_layer);obj.b4ml.contact_index=0
        iterator=contacts.correction_steps(obj,scene);next(iterator);platform.data.vertices[2].co.z=.2;platform.data.update()
        with self.assertRaisesRegex(ValueError,'platform|surface|changed'):next(iterator)
        iterator.close();self.assertIs(obj.b4ml.candidate_action,before)
        self.assertEqual(contacts._action_signature(obj),before_signature)
        RECORDS.append(dict(workflow='invalid_or_changed_platform_fail_closed',candidate_restored=True))

    def test_generated_rigify_default_solve_and_save_reload(self):
        obj,scene,item,platform,_,_,_=_setup('rigify_default');self.assertGreaterEqual(len(obj.pose.bones),128)
        item.start=5.;item.end=7.;item.blend=0.;report=contacts.solve(obj,scene)
        self.assertEqual(report['moving_surface_contacts'],1)
        name=obj.name;platform_name=platform.name;path=ROOT/'training/b4artists_ml/cache/moving-platform-v1.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path),use_scripts=False)
        obj=bpy.data.objects[name];platform=bpy.data.objects[platform_name];item=obj.b4ml.contacts[0]
        self.assertTrue(item.prop_bound);self.assertIs(item.prop_target,platform);self.assertIs(item.prop_object,platform)
        row=contacts.rows(obj)[0];resolved=contacts._resolved_contact(obj,row,bpy.context.scene)
        self.assertLess((Vector(resolved['point'])-platform.matrix_world@Vector(item.prop_point)).length,1e-8)
        RECORDS.append(dict(workflow='rigify_default_moving_platform_save_reload',bones=len(obj.pose.bones),
            solver_ms=report['elapsed_ms'],binding_preserved=True))

    def test_operator_metadata(self):
        self.assertIn('UNDO',ui.B4ML_OT_contact.bl_options)
        operations={row[0] for row in ui.B4ML_OT_contact.__annotations__['operation'].keywords['items']}
        self.assertTrue({'BIND_SURFACE','CLEAR_SURFACE'}<=operations)

    def test_concave_platform_uses_blender_tessellation(self):
        scene=bpy.context.scene;mesh=bpy.data.meshes.new('Concave Platform Mesh')
        mesh.from_pydata([(0,0,0),(2,0,0),(2,2,0),(1,1,0),(0,2,0)],[],[(0,1,2,3,4)])
        mesh.update();platform=bpy.data.objects.new('Concave Platform',mesh);scene.collection.objects.link(platform)
        _,_,triangles,_,_=contacts._platform_geometry(platform)
        self.assertTrue(contacts._inside_surface(Vector((.5,.5,0)),triangles))
        self.assertFalse(contacts._inside_surface(Vector((1,1.5,0)),triangles))


def run():
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(MovingPlatformTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report=dict(tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),errors=len(result.errors),
        skips=len(result.skipped),records=RECORDS,package=b4artists_ml.__file__,runtime_sha256={
            'contacts':_sha(contacts.__file__),'ui':_sha(ROOT/'b4artists_ml/ui.py'),'test':_sha(__file__)})
    (ROOT/'training/b4artists_ml/results/moving-platforms-v1.json').write_text(json.dumps(report,indent=2)+'\n')
    print('MOVING_PLATFORMS_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)


def run_ui_smoke():
    MovingPlatformTests.setUpClass();obj,_,item,platform,_,_,_=_setup()
    obj.b4ml.show_contacts=True;state=dict(rig=obj.name,platform=platform.name,phase='operate',
        started=time.monotonic(),events=[])
    def tick():
        try:
            if time.monotonic()-state['started']>45:raise AssertionError('Moving Platform UI timed out')
            window=bpy.context.window_manager.windows[0];area=next(value for value in window.screen.areas if value.type=='VIEW_3D')
            region=next(value for value in area.regions if value.type=='WINDOW');sidebar=next(value for value in area.regions if value.type=='UI')
            area.spaces.active.show_region_ui=True
            for value in area.regions:
                if value.type=='UI' and hasattr(value,'active_panel_category'):value.active_panel_category='B4Artists ML'
            obj=bpy.data.objects[state['rig']];platform=bpy.data.objects[state['platform']]
            window.view_layer.objects.active=obj;obj.select_set(True);item=obj.b4ml.contacts[0]
            with bpy.context.temp_override(window=window,area=area,region=region,object=obj,active_object=obj,
                selected_objects=[obj],selected_editable_objects=[obj]):
                if state['phase']=='operate':
                    window.event_simulate(type='ESC',value='PRESS')
                    assert bpy.ops.b4ml.contact(operation='CLEAR_SURFACE')=={'FINISHED'};assert not item.prop_bound
                    item.prop_object=platform;assert bpy.ops.b4ml.contact(operation='BIND_SURFACE')=={'FINISHED'}
                    assert item.prop_bound and item.prop_target==platform
                    state['events'].append('Clear and Bind operators preserved the explicit platform target')
                    state['phase']='scroll';state['scrolls']=0;return .2
                if state['phase']=='scroll':
                    window.cursor_warp(sidebar.x+sidebar.width//2,sidebar.y+sidebar.height//2)
                    window.event_simulate(type='WHEELDOWNMOUSE',value='PRESS',
                        x=sidebar.x+sidebar.width//2,y=sidebar.y+sidebar.height//2)
                    state['scrolls']+=1
                    if state['scrolls']<16:return .04
                    state['phase']='capture';return .5
                path=ROOT/'training/b4artists_ml/cache/moving-platform-ui-v1.png';bpy.ops.screen.screenshot(filepath=str(path))
                report=dict(passed=True,fixture='boneforge',events=state['events'],bound=item.prop_bound,
                    target=item.prop_target.name if item.prop_target else None,screenshot=str(path.relative_to(ROOT)),
                    elapsed_seconds=time.monotonic()-state['started'])
                (ROOT/'docs/b4artists_ml/moving-platform-ui-v1.json').write_text(json.dumps(report,indent=2)+'\n')
                print('MOVING_PLATFORM_UI_RESULT: '+json.dumps(report),flush=True);bpy.ops.wm.quit_blender();return None
        except Exception as exc:
            report=dict(passed=False,phase=state['phase'],error=str(exc),traceback=traceback.format_exc(),events=state['events'])
            (ROOT/'docs/b4artists_ml/moving-platform-ui-v1.json').write_text(json.dumps(report,indent=2)+'\n')
            print('MOVING_PLATFORM_UI_RESULT: '+json.dumps(report),flush=True);bpy.ops.wm.quit_blender();return None
        return .05
    bpy.app.timers.register(tick,first_interval=.5)


if __name__=='__main__' and '--ui-smoke' in sys.argv:run_ui_smoke()
elif __name__=='__main__':run()
