"""Scene-aware provisional contact suggestions on evaluated humanoid rigs."""
from pathlib import Path
import json,os,sys,tempfile,time,traceback,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]
import bpy
from mathutils import Vector
import b4artists_ml
from b4artists_ml import contacts,posing,workflow
from test_b4artists_ml_contacts import fixture


class ContactSuggestionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):b4artists_ml.register()

    def prepared(self,label='boneforge'):
        ob,*_=fixture(label);scene=bpy.context.scene;ob.b4ml.contacts.clear();scene.frame_set(1);posing._update(ob)
        rows={r['id']:r for r in posing.bindings(ob)[2]};points=[]
        for limb in ('leg-L','leg-R'):
            matrix=workflow.display_world(ob)@ob.pose.bones[rows[limb]['joints'][2]].matrix;points.append(matrix@Vector(ob.b4ml.contact_offset))
        ob.b4ml.support_plane_point=(points[0]+points[1])*.5;ob.b4ml.support_plane_normal=(0,0,1)
        ob.b4ml.contact_suggest_distance=.2;ob.b4ml.contact_suggest_speed=.001;ob.b4ml.contact_suggest_min_frames=3;ob.b4ml.contact_suggest_gap_frames=1
        scene.frame_set(6);return ob,scene,points

    def test_proposals_require_acceptance_and_preserve_animation(self):
        for label in ('boneforge','rigify_basic','rigify_default'):
            with self.subTest(rig=label):
                ob,scene,_=self.prepared(label);candidate=ob.b4ml.candidate_action;signature=contacts._action_signature(ob);pose=workflow.raw_pose(ob)
                report=contacts.suggest(ob,scene)
                self.assertTrue(report['provisional']);self.assertEqual(report['backend'],'scene_contact_suggestions_v1');self.assertGreaterEqual(report['suggestions'],2)
                self.assertTrue(all(i.review_state=='PROPOSED' and i.provenance=='AUTHORED_PLANE' for i in ob.b4ml.contacts))
                self.assertTrue(all('matching grounded priority poses' in i.reason for i in ob.b4ml.contacts))
                self.assertEqual(contacts.rows(ob),[]);self.assertIs(ob.animation_data.action,candidate);self.assertEqual(contacts._action_signature(ob),signature);self.assertEqual(workflow.raw_pose(ob),pose);self.assertEqual(posing._frame(scene),6.)
                ob.b4ml.contact_index=0;self.assertEqual(bpy.ops.b4ml.contact(operation='ACCEPT'),{'FINISHED'})
                self.assertEqual(len(contacts.rows(ob)),1);self.assertEqual(ob.b4ml.contacts[0].review_state,'ACCEPTED')
                ob.b4ml.contact_index=1;self.assertEqual(bpy.ops.b4ml.contact(operation='REJECT'),{'FINISHED'});self.assertFalse(ob.b4ml.contacts[1].enabled)
                correction=contacts.solve(ob,scene);self.assertLess(correction['max_after'],2e-4);self.assertEqual(correction['contacts'],1)

    def test_static_planar_mesh_bounds_and_provenance(self):
        ob,scene,points=self.prepared();center=(points[0]+points[1])*.5
        bpy.ops.mesh.primitive_plane_add(size=20,location=(center.x,center.y,center.z));surface=bpy.context.object;surface.name='Reviewed Ground'
        ob.b4ml.contact_surface=surface;bpy.context.view_layer.objects.active=ob
        report=contacts.suggest(ob,scene)
        self.assertEqual(report['surface'],'STATIC_PLANAR_MESH:Reviewed Ground');self.assertGreaterEqual(report['suggestions'],2)
        self.assertTrue(all(i.provenance==report['surface'] for i in ob.b4ml.contacts))
        surface.location.x+=100
        report=contacts.suggest(ob,scene);self.assertEqual(report['suggestions'],0);self.assertEqual(len(ob.b4ml.contacts),0)

    def test_cancel_and_changed_inputs_publish_nothing(self):
        ob,scene,_=self.prepared();candidate=ob.b4ml.candidate_action;signature=contacts._action_signature(ob);pose=workflow.raw_pose(ob)
        contacts.suggest_start(ob,scene);self.assertFalse(contacts.suggest_step(ob));contacts.suggest_abort(ob)
        self.assertFalse(ob.b4ml.contact_suggest_running);self.assertEqual(len(ob.b4ml.contacts),0);self.assertIs(ob.animation_data.action,candidate);self.assertEqual(contacts._action_signature(ob),signature);self.assertEqual(workflow.raw_pose(ob),pose);self.assertEqual(posing._frame(scene),6.)
        contacts.suggest_start(ob,scene)
        while not ob.b4ml.contact_suggest_progress.startswith('Preparing rig mapping'):self.assertFalse(contacts.suggest_step(ob))
        ob.b4ml.contact_suggest_speed=.002
        with self.assertRaisesRegex(ValueError,'settings changed'):contacts.suggest_step(ob)
        self.assertFalse(ob.b4ml.contact_suggest_running);self.assertEqual(len(ob.b4ml.contacts),0);self.assertEqual(contacts._action_signature(ob),signature)

    def test_proposals_survive_reload_without_becoming_accepted(self):
        ob,scene,_=self.prepared();name=ob.name;contacts.suggest(ob,scene);expected=[(i.name,i.review_state,i.confidence,i.provenance,i.reason) for i in ob.b4ml.contacts]
        with tempfile.TemporaryDirectory() as td:
            path=str(Path(td)/'contact-suggestions.blend');bpy.ops.wm.save_as_mainfile(filepath=path);bpy.ops.wm.open_mainfile(filepath=path,use_scripts=False)
            ob=bpy.data.objects[name];bpy.context.view_layer.objects.active=ob
            self.assertEqual([(i.name,i.review_state,i.confidence,i.provenance,i.reason) for i in ob.b4ml.contacts],expected)
            self.assertEqual(contacts.rows(ob),[]);self.assertFalse(ob.b4ml.contact_suggest_running)


def run_ui_smoke():
    ContactSuggestionTests.setUpClass();case=ContactSuggestionTests();ob,scene,_=case.prepared('rigify_default')
    source=ob.b4ml.source_action;source_signature=contacts._action_signature(ob) if ob.animation_data.action==source else None
    if source_signature is None:
        candidate=ob.animation_data.action;workflow.assign_action(ob,source,workflow._slot(ob.animation_data));source_signature=contacts._action_signature(ob);workflow.assign_action(ob,candidate,workflow._slot(ob.animation_data))
    result_path=ROOT/'training/b4artists_ml/results'/os.environ.get('B4ML_CONTACT_SUGGEST_UI_RESULT','contact-suggestions-ui-v1.json')
    screenshot_path=ROOT/'training/b4artists_ml/cache'/os.environ.get('B4ML_CONTACT_SUGGEST_UI_SCREENSHOT','contact-suggestions-ui-v1.png')
    state=dict(name=ob.name,source=source.name,source_signature=source_signature,phase='dismiss',started=time.monotonic());steps=[];suggestion_details=[];correction_steps=[];correction_details=[];original_step=contacts.suggest_step;original_correction_step=contacts.step
    def timed_step(obj):
        started=time.perf_counter()
        try:return original_step(obj)
        finally:
            elapsed=(time.perf_counter()-started)*1000;steps.append(elapsed);suggestion_details.append(dict(elapsed_ms=elapsed,progress=obj.b4ml.contact_suggest_progress))
    contacts.suggest_step=timed_step
    def timed_correction_step(obj):
        started=time.perf_counter()
        try:return original_correction_step(obj)
        finally:
            elapsed=(time.perf_counter()-started)*1000;correction_steps.append(elapsed);correction_details.append(dict(elapsed_ms=elapsed,progress=obj.b4ml.contact_progress))
    contacts.step=timed_correction_step
    def tick():
        try:
            if time.monotonic()-state['started']>120:raise AssertionError('Contact suggestion UI workflow timed out')
            win=bpy.context.window_manager.windows[0];area=next(a for a in win.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW')
            area.spaces.active.show_region_ui=True
            for r in area.regions:
                if r.type=='UI' and hasattr(r,'active_panel_category'):r.active_panel_category='B4Artists ML'
            ob=bpy.data.objects[state['name']];win.view_layer.objects.active=ob;ob.select_set(True)
            with bpy.context.temp_override(window=win,area=area,region=region):
                if state['phase']=='dismiss':
                    win.event_simulate(type='ESC',value='PRESS');state['phase']='begin'
                elif state['phase']=='begin':
                    assert bpy.ops.b4ml.contact_suggest('INVOKE_DEFAULT')=={'RUNNING_MODAL'};state['phase']='suggested'
                elif state['phase']=='suggested':
                    if ob.b4ml.contact_suggest_running:return .03
                    report=json.loads(ob.b4ml.contact_suggestion_report);assert report['suggestions']>=2 and all(i.review_state=='PROPOSED' for i in ob.b4ml.contacts)
                    state['suggestion']=report;ob.b4ml.contact_index=0;assert bpy.ops.b4ml.contact(operation='ACCEPT')=={'FINISHED'}
                    ob.b4ml.contact_index=1;assert bpy.ops.b4ml.contact(operation='REJECT')=={'FINISHED'}
                    assert bpy.ops.b4ml.contact_solve('INVOKE_DEFAULT')=={'RUNNING_MODAL'};state['phase']='corrected'
                elif state['phase']=='corrected':
                    if ob.b4ml.contact_running:return .03
                    correction=json.loads(ob.b4ml.contact_metrics);assert correction['contacts']==1 and correction['max_after']<2e-4
                    state['correction']=correction;ob.b4ml.show_contacts=True;ob.b4ml.contact_index=0;state['phase']='capture';area.tag_redraw();return .2
                elif state['phase']=='capture':
                    path=screenshot_path;bpy.ops.screen.screenshot(filepath=str(path))
                    assert bpy.ops.b4ml.action(operation='KEEP')=={'FINISHED'};assert bpy.ops.b4ml.action(operation='RESTORE_SOURCE')=={'FINISHED'}
                    assert ob.animation_data.action.name==state['source'];assert contacts._action_signature(ob)==state['source_signature']
                    ordered=sorted(steps);p95=ordered[min(len(ordered)-1,int(.95*len(ordered)))]
                    correction_ordered=sorted(correction_steps);correction_p95=correction_ordered[min(len(correction_ordered)-1,int(.95*len(correction_ordered)))]
                    report=dict(passed=True,package=b4artists_ml.__file__,suggestion=state['suggestion'],suggestion_step_count=len(steps),suggestion_steps_ms=steps,suggestion_step_details=suggestion_details,suggestion_step_p95_ms=p95,suggestion_step_max_ms=max(steps),correction=state['correction'],correction_step_count=len(correction_steps),correction_steps_ms=correction_steps,correction_step_details=correction_details,correction_step_p95_ms=correction_p95,correction_step_max_ms=max(correction_steps),screenshot=str(path.relative_to(ROOT)),elapsed_seconds=time.monotonic()-state['started'])
                    result_path.write_text(json.dumps(report,indent=2)+'\n');print('CONTACT_SUGGEST_UI_RESULT: '+json.dumps(report),flush=True);bpy.ops.wm.quit_blender();return None
        except Exception as exc:
            report=dict(passed=False,phase=state['phase'],error=str(exc),traceback=traceback.format_exc())
            result_path.write_text(json.dumps(report,indent=2)+'\n');print('CONTACT_SUGGEST_UI_RESULT: '+json.dumps(report),flush=True);bpy.ops.wm.quit_blender();return None
        return .03
    bpy.app.timers.register(tick,first_interval=.5)


if __name__=='__main__' and '--ui-smoke' in sys.argv:run_ui_smoke()
elif __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ContactSuggestionTests))
    report=dict(tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),errors=len(result.errors),package=b4artists_ml.__file__)
    path=ROOT/'training/b4artists_ml/results'/os.environ.get('B4ML_CONTACT_SUGGEST_RESULT','contact-suggestions-v1.json');path.write_text(json.dumps(report,indent=2)+'\n')
    print('CONTACT_SUGGEST_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
