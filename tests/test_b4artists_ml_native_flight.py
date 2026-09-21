"""Native motion integration: complete editable results and workflow recovery."""
from pathlib import Path
import sys,json,unittest,tempfile,os
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]
import bpy,numpy as np
import b4artists_ml
from b4artists_ml import motion_layer as m,workflow as w,posing as p
from test_b4artists_ml_contacts import fixture


def animate(instance):
    instance['residual']=.1;instance.keyframe_insert('["residual"]',frame=1)
    instance['residual']=.5;instance.keyframe_insert('["residual"]',frame=11)
    fc=instance.driver_add('location',2);fc.keyframe_points.clear();driver=fc.driver
    driver.type='SCRIPTED';v=driver.variables.new();v.name='r';v.type='SINGLE_PROP';v.targets[0].id=instance;v.targets[0].data_path='["residual"]'
    driver.expression='r+0.02*(frame-1)*(11-frame)'


def values(owner):
    instance=m.validate(owner);scene=bpy.context.scene;rows=[]
    for f in (1.,2.137,6.,8.713,11.):
        scene.frame_set(int(f),subframe=f%1);p._update(owner)
        dep=bpy.context.evaluated_depsgraph_get()
        for e in dep.object_instances:
            if e.is_instance and e.parent and e.parent.original==instance and e.object.original==owner:
                rows.append([list(e.matrix_world@b.head) for b in e.object.pose.bones]);break
        else:raise AssertionError('Missing instanced rig')
    return np.array(rows)


class NativeResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):b4artists_ml.register()

    def test_keep_archive_reload_preview_discard_two_real_rigs(self):
        for label in ('boneforge','rigify_default'):
            with self.subTest(rig=label):
                ob,source,sig,modes=fixture(label,True);scene=bpy.context.scene;source_name=source.name;links=sorted(c.name for c in ob.users_collection)
                instance=m.begin(ob,scene);animate(instance);p._update(ob)
                bpy.context.view_layer.objects.active=instance;instance.select_set(True)
                self.assertIs(w.active_rig(bpy.context),ob)
                expected=values(ob);expression=instance.animation_data.drivers[0].driver.expression
                w.finish_preview(ob,scene,True);self.assertEqual(m._read(ob)['phase'],'kept')
                w.restore_kept_source(ob,scene);self.assertIs(ob.animation_data.action,source);self.assertIsNone(m.find(ob))
                result=m.results(ob)[-1];self.assertTrue(result.use_fake_user);self.assertEqual(result.animation_data.drivers[0].driver.expression,expression)
                self.assertIs(result.animation_data.drivers[0].driver.variables[0].targets[0].id,result)
                self.assertEqual(sorted(c.name for c in ob.users_collection),links)
                names=(ob.name,scene.name,result.name)
                with tempfile.TemporaryDirectory() as td:
                    saved=str(Path(td)/'native-result.blend');bpy.ops.wm.save_as_mainfile(filepath=saved);bpy.ops.wm.open_mainfile(filepath=saved,use_scripts=False)
                    ob=bpy.data.objects[names[0]];scene=bpy.data.scenes[names[1]];bpy.context.window.scene=scene;result=bpy.data.objects[names[2]]
                    self.assertEqual(ob.animation_data.action.name,source_name)
                    w.preview_motion_result(ob,scene,result);restored=m.validate(ob)
                    self.assertIsNot(restored.animation_data.action,result.animation_data.action)
                    self.assertIs(restored.animation_data.drivers[0].driver.variables[0].targets[0].id,restored)
                    np.testing.assert_allclose(values(ob),expected,atol=2e-5)
                    archived_action=result.animation_data.action
                    restored['residual']=9.;self.assertIs(result.animation_data.action,archived_action)
                    w.finish_preview(ob,scene,False);self.assertEqual(ob.animation_data.action.name,source_name)
                    self.assertIsNone(m.find(ob));self.assertIn(result,m.results(ob));self.assertEqual(sorted(c.name for c in ob.users_collection),links)

    def test_cached_mapping_segment_samples_match_public_adapter(self):
        from b4artists_ml import native_flight as native, support
        from test_b4artists_ml_flight import fixture as flight_fixture
        for label in ('boneforge','rigify_default','rigify_basic','metarig_basic','metarig_default'):
            with self.subTest(rig=label):
                ob,*_=flight_fixture(label,True);scene=bpy.context.scene
                for frame in (1.,2.137,6.25,10.713,11.):
                    scene.frame_set(int(frame),subframe=frame%1);p._update(ob)
                    binding,evaluated,a,b=support.sample(ob,bpy.context.evaluated_depsgraph_get())
                    actual=native._segment_points(evaluated,binding['names'])
                    np.testing.assert_array_equal(actual[0],a)
                    np.testing.assert_array_equal(actual[1],b)
                w.finish_preview(ob,scene,False)

    def test_native_flight_real_rigs_and_cancellation(self):
        from b4artists_ml import flight as f, support
        for label,frames in (('boneforge',10),('rigify_default',60)):
            with self.subTest(rig=label):
                ob,source,sig,modes=fixture(label,True);scene=bpy.context.scene
                if frames!=10:
                    w.finish_preview(ob,scene,False);max(ob.b4ml.anchors,key=lambda v:v.frame).frame=frames+1;w.preview(ob,scene)
                ob.b4ml.contacts.clear();support.initialize(ob);ob.b4ml.flights.clear();scene.frame_set(1);f.add(ob,scene);scene.frame_set(6)
                ob.b4ml.flight_backend='NATIVE';candidate=ob.b4ml.candidate_action;original=f._curve_token(ob)
                f.start(ob,scene);self.assertFalse(f.step(ob));f.abort(ob)
                self.assertIsNone(m.find(ob));self.assertIs(ob.animation_data.action,candidate);self.assertEqual(f._curve_token(ob),original)
                report=f.solve(ob,scene);self.assertEqual(report['backend'],'native_instance_com_v1');self.assertLess(report['max_after'],2e-4);self.assertLess(report['relative_basis_error'],2e-4)
                self.assertLess(max(r['acceleration_error_p95'] for r in report['intervals']),.1)
                self.assertIs(ob.animation_data.action,candidate);self.assertEqual(f._curve_token(ob),original)
                self.assertIsNotNone(m.validate(ob));f.restore(ob,scene);self.assertIsNone(m.find(ob));self.assertIs(ob.animation_data.action,candidate)
                w.finish_preview(ob,scene,False);self.assertIs(ob.animation_data.action,source)

    def test_displayed_helpers_contacts_and_support(self):
        from b4artists_ml import body_preview,contacts,support,body_solver
        from mathutils import Vector,Quaternion
        ob,*_=fixture('boneforge',True);scene=bpy.context.scene;instance=m.begin(ob,scene);instance.location=(4,-2,3);instance.rotation_mode='QUATERNION';instance.rotation_quaternion=Quaternion((0,0,1),.3);p._update(ob);transform=instance.matrix_world.copy()
        support.initialize(ob);before=support.sample(ob,bpy.context.evaluated_depsgraph_get());com=support.center_of_mass if hasattr(support,'center_of_mass') else None
        report=support.analyze(ob,scene,bpy.context.evaluated_depsgraph_get())
        from b4artists_ml.support_math import center_of_mass
        source_com=center_of_mass(before[2],before[3],[i.weight for i in ob.b4ml.mass_segments],[i.fraction for i in ob.b4ml.mass_segments])[0]
        np.testing.assert_allclose(report['com'],transform@Vector(source_com),atol=1e-6)
        ob.b4ml.contacts.clear();item=contacts.capture(ob,scene);row=next(r for r in p.bindings(ob)[2] if r['id']==item.limb)
        wanted=w.display_world(ob)@ob.pose.bones[row['joints'][2]].head
        np.testing.assert_allclose(item.point,wanted,atol=1e-6)
        w.finish_preview(ob,scene,True)
        body_preview.begin(ob,scene);session=body_preview._get(ob);source_points=session.world_points(session.baseline)
        for index,label in body_preview.TARGETS:
            helper=ob.b4ml.body_targets[label].target;bpy.context.view_layer.update()
            np.testing.assert_allclose(helper.matrix_world.translation,transform@Vector(source_points[index]),atol=1e-6)
        helper=ob.b4ml.body_targets['Hand L'].target;bpy.context.view_layer.objects.active=helper;helper.select_set(True)
        self.assertIs(w.active_rig(bpy.context),ob)
        targets,mask,signature,rotations,poles=body_preview._request(ob,session)
        np.testing.assert_allclose(targets,source_points,atol=1e-6)
        body_preview.solve(ob);body_preview.finish(ob,scene,False)
        self.assertIs(bpy.context.view_layer.objects.active,instance)
        p.begin(ob,scene)
        for target in ob.b4ml.pose_targets:
            row=next(r for r in p.bindings(ob)[2] if r['id']==target.name)
            expected=w.display_world(ob)@ob.pose.bones[row['joints'][2]].head
            bpy.context.view_layer.update();np.testing.assert_allclose(target.target.matrix_world.translation,expected,atol=1e-6)
        p.finish(ob,scene,False);w.restore_kept_source(ob,scene)

    def test_native_flight_playhead_change_aborts_without_overwriting_user_frame(self):
        from b4artists_ml import flight as f,support
        ob,*_=fixture();scene=bpy.context.scene;ob.b4ml.contacts.clear();support.initialize(ob);f.add(ob,scene);ob.b4ml.flight_backend='NATIVE'
        f.start(ob,scene);f.step(ob);scene.frame_set(9)
        with self.assertRaisesRegex(ValueError,'Playhead'):f.step(ob)
        self.assertEqual(scene.frame_current,9);self.assertFalse(ob.b4ml.flight_running);self.assertIsNone(m.find(ob))

    def test_cancel_after_native_data_created_recovers_selection_and_actions(self):
        from b4artists_ml import flight as f,support
        ob,*_=fixture();scene=bpy.context.scene;ob.b4ml.contacts.clear();support.initialize(ob);f.add(ob,scene);ob.b4ml.flight_backend='NATIVE'
        bpy.context.view_layer.objects.active=ob;ob.select_set(True);actions=set(bpy.data.actions.keys());objects=set(bpy.data.objects.keys());collections=set(bpy.data.collections.keys())
        f.start(ob,scene)
        while m.find(ob) is None:self.assertFalse(f.step(ob))
        f.abort(ob)
        self.assertEqual(set(bpy.data.actions.keys()),actions);self.assertEqual(set(bpy.data.objects.keys()),objects);self.assertEqual(set(bpy.data.collections.keys()),collections)
        self.assertIs(bpy.context.view_layer.objects.active,ob);self.assertTrue(ob.select_get())

    def test_external_pose_edit_rejected_and_preserved_before_and_after_layer(self):
        from b4artists_ml import flight as f,support
        for after_layer in (False,True):
            with self.subTest(after_layer=after_layer):
                ob,*_=fixture();scene=bpy.context.scene;ob.b4ml.contacts.clear();support.initialize(ob);f.add(ob,scene);ob.b4ml.flight_backend='NATIVE'
                f.start(ob,scene);self.assertFalse(f.step(ob))
                if after_layer:
                    while m.find(ob) is None:self.assertFalse(f.step(ob))
                bone=ob.pose.bones['hips'];bone.location.x+=.125;wanted=list(bone.location)
                with self.assertRaisesRegex(ValueError,'Pose controls'):f.step(ob)
                self.assertEqual(list(bone.location),wanted);self.assertFalse(ob.b4ml.flight_running);self.assertIsNone(m.find(ob))

    def test_direct_cancel_preserves_external_pose_and_playhead_edits(self):
        from b4artists_ml import flight as f,support
        for edit in ('pose','frame'):
            with self.subTest(edit=edit):
                ob,*_=fixture();scene=bpy.context.scene;ob.b4ml.contacts.clear();support.initialize(ob);f.add(ob,scene);ob.b4ml.flight_backend='NATIVE'
                f.start(ob,scene);self.assertFalse(f.step(ob))
                if edit=='pose':
                    ob.pose.bones['hips'].location.x+=.125;wanted=w.raw_pose(ob)
                else:scene.frame_set(9)
                f.abort(ob)
                if edit=='pose':self.assertEqual(w.raw_pose(ob),wanted)
                else:self.assertEqual(scene.frame_current,9)
                self.assertFalse(ob.b4ml.flight_running);self.assertIsNone(m.find(ob))

    def test_cubic_fit_failure_cleans_partially_created_native_action(self):
        from b4artists_ml import flight as f,support,flight_math as fm
        from unittest.mock import patch
        ob,*_=fixture();scene=bpy.context.scene;ob.b4ml.contacts.clear();support.initialize(ob);f.add(ob,scene);ob.b4ml.flight_backend='NATIVE'
        actions=set(bpy.data.actions.keys());objects=set(bpy.data.objects.keys());collections=set(bpy.data.collections.keys());candidate=ob.b4ml.candidate_action
        with patch.object(fm,'cubic_controls',side_effect=ValueError('Injected native handle failure')):
            with self.assertRaisesRegex(ValueError,'Injected native handle failure'):f.solve(ob,scene)
        self.assertEqual(set(bpy.data.actions.keys()),actions);self.assertEqual(set(bpy.data.objects.keys()),objects);self.assertEqual(set(bpy.data.collections.keys()),collections)
        self.assertIsNone(m.find(ob));self.assertIs(ob.animation_data.action,candidate);self.assertFalse(ob.b4ml.flight_running)

    def test_sixteen_flights_keep_archive_reload_and_reopen(self):
        from b4artists_ml import flight as f,support
        ob,source,*_=fixture();scene=bpy.context.scene;source_name=source.name
        w.finish_preview(ob,scene,False);payload=ob.b4ml.anchors[0].payload;ob.b4ml.anchors.clear()
        for index in range(17):
            anchor=ob.b4ml.anchors.add();anchor.frame=1+index*10/16;anchor.payload=payload
        w.preview(ob,scene);ob.b4ml.contacts.clear();support.initialize(ob);ob.b4ml.flights.clear()
        for index in range(16):
            row=ob.b4ml.flights.add();row.start=1+index*10/16;row.end=1+(index+1)*10/16
        ob.b4ml.flight_backend='NATIVE';f.solve(ob,scene)
        self.assertEqual(len(m.find(ob).animation_data.drivers),51);expected=values(ob)
        w.finish_preview(ob,scene,True);w.restore_kept_source(ob,scene);result=m.results(ob)[-1]
        self.assertEqual(len(result.animation_data.drivers),51)
        for fc in result.animation_data.drivers:
            for variable in fc.driver.variables:self.assertIs(variable.targets[0].id,result)
        names=(ob.name,result.name,scene.name)
        with tempfile.TemporaryDirectory() as td:
            path=str(Path(td)/'sixteen-flights.blend');bpy.ops.wm.save_as_mainfile(filepath=path);bpy.ops.wm.open_mainfile(filepath=path,use_scripts=False)
            ob=bpy.data.objects[names[0]];result=bpy.data.objects[names[1]];scene=bpy.data.scenes[names[2]];bpy.context.window.scene=scene
            w.preview_motion_result(ob,scene,result);np.testing.assert_allclose(values(ob),expected,atol=2e-5)
            w.finish_preview(ob,scene,False);self.assertEqual(ob.animation_data.action.name,source_name);self.assertIsNone(m.find(ob))

    def retry_fixture(self,native=True):
        from b4artists_ml import body_preview as body
        ob,*_=fixture('boneforge',True);scene=bpy.context.scene
        if native:
            instance=m.begin(ob,scene);instance.location=(4,-2,3);p._update(ob)
        w.finish_preview(ob,scene,True);body.begin(ob,scene)
        hand=ob.b4ml.body_targets['Hand L'].target;pelvis=ob.b4ml.body_targets['Pelvis'].target
        hand.location+=(pelvis.location-hand.location).normalized()*.03;ob.b4ml.body_influence=.3
        return ob,scene,body

    def test_near_converged_pose_retries_with_unchanged_pin_tolerance(self):
        for native in (False,True):
            with self.subTest(native=native):
                ob,scene,body=self.retry_fixture(native);body.solve(ob)
                report=json.loads(ob.b4ml.body_payload)['metrics']
                self.assertEqual(report['solve_attempts'],2);self.assertLess(report['pin_error'],2e-4)
                body.finish(ob,scene,False);w.restore_kept_source(ob,scene)

    def test_cancel_between_pose_attempts_restores_previous_preview(self):
        ob,scene,body=self.retry_fixture();before=w.raw_pose(ob);body.start(ob)
        for _ in range(2000):
            self.assertFalse(body.step(ob))
            if ob.b4ml.body_progress=='Solving pose: 0/100':break
        else:self.fail('Expected bounded retry boundary')
        body.abort(ob);self.assertEqual(w.raw_pose(ob),before);self.assertFalse(ob.b4ml.body_running)
        body.finish(ob,scene,False);w.restore_kept_source(ob,scene)

    def test_target_edit_between_pose_attempts_aborts(self):
        ob,scene,body=self.retry_fixture();before=w.raw_pose(ob);body.start(ob)
        for _ in range(2000):
            self.assertFalse(body.step(ob))
            if ob.b4ml.body_progress=='Solving pose: 0/100':break
        else:self.fail('Expected bounded retry boundary')
        ob.b4ml.body_targets['Hand L'].target.location.x+=.01
        with self.assertRaisesRegex(ValueError,'Targets changed'):body.step(ob)
        self.assertEqual(w.raw_pose(ob),before);self.assertFalse(ob.b4ml.body_running)
        body.finish(ob,scene,False);w.restore_kept_source(ob,scene)

    def test_result_rejects_changed_rest_and_wrong_owner_before_mutation(self):
        ob,*_=fixture();scene=bpy.context.scene;instance=m.begin(ob,scene);animate(instance);w.finish_preview(ob,scene,True);w.restore_kept_source(ob,scene);result=m.results(ob)[-1]
        before=ob.animation_data.action;result['b4ml_result_rest']='invalid'
        with self.assertRaisesRegex(ValueError,'rest pose'):w.preview_motion_result(ob,scene,result)
        self.assertIs(ob.animation_data.action,before);self.assertIsNone(m.find(ob));self.assertIsNone(ob.b4ml.candidate_action)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(NativeResultTests))
    report=dict(passed=result.wasSuccessful(),tests=result.testsRun,failures=[(t.id(),v) for t,v in result.failures],errors=[(t.id(),v) for t,v in result.errors])
    (ROOT/'training/b4artists_ml/results/native-result-workflow-v3.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
