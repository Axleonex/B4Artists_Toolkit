"""Read-only rig mapping diagnostics for the 0.33 usability slice."""
from pathlib import Path
import json,os,sys,unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import addon_utils,bpy
import b4artists_ml
from b4artists_ml import motion_layer,rig_diagnostics,rig_state as rs,ui,workflow as w
from test_b4artists_ml_context_rig import ContextRigTests
from test_b4artists_ml_imported_humanoids import authored
from test_b4artists_ml_quadruped_pose import _generate as generated_quadruped

RECORDS=[]


def _workflow(report,identifier):
    return next(row for row in report['workflows'] if row['id']==identifier)


class RigDiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        addon_utils.enable('rigify',default_set=True,persistent=False)
        b4artists_ml.register();ContextRigTests.setUpClass();cls.fixtures=ContextRigTests()

    def _rig(self,label):
        if label=='unity_humanoid_fbx':
            ob,mesh,roles=authored('unity_humanoid',1);return ob
        ob,source,session,targets,mask=self.fixtures.fixture(label,transformed=True)
        session.cancel();return ob

    def test_supported_humanoid_reports_are_complete_and_read_only(self):
        for label in ('boneforge','rigify_default','unity_humanoid_fbx'):
            with self.subTest(rig=label):
                ob=self._rig(label);bpy.context.view_layer.objects.active=ob;ob.select_set(True)
                pose=w.raw_pose(ob);modes=rs.mode_values(ob);world=ob.matrix_world.copy()
                action=ob.animation_data.action if ob.animation_data else None
                selected={item.name:item.select_get() for item in bpy.context.view_layer.objects}
                active=bpy.context.view_layer.objects.active
                report=rig_diagnostics.analyze(ob)
                self.assertEqual(report['mapped_required_role_count'],report['required_role_count'])
                self.assertFalse(report['missing_roles']);self.assertFalse(report['unsafe_mapped_controls'])
                self.assertTrue(_workflow(report,'automatic_capture')['ready'])
                self.assertFalse(_workflow(report,'pose_blending')['ready'])
                self.assertIn('at least two poses',_workflow(report,'pose_blending')['detail'])
                self.assertTrue(_workflow(report,'humanoid_whole_body')['ready'],report)
                self.assertGreater(report['writable_control_count'],0)
                self.assertLessEqual(report['writable_control_count'],report['mapped_control_count'])
                self.assertEqual(w.raw_pose(ob),pose);self.assertEqual(rs.mode_values(ob),modes)
                self.assertTrue(all(abs(a-b)<1e-8 for row_a,row_b in zip(ob.matrix_world,world) for a,b in zip(row_a,row_b)))
                self.assertIs(bpy.context.view_layer.objects.active,active)
                self.assertEqual({item.name:item.select_get() for item in bpy.context.view_layer.objects},selected)
                self.assertIs(ob.animation_data.action if ob.animation_data else None,action)
                if label=='rigify_default':
                    self.assertGreater(report['excluded_bone_counts']['deform'],0)
                    self.assertGreater(report['excluded_bone_counts']['mechanism'],0)
                    self.assertGreater(report['excluded_bone_counts']['organization'],0)
                RECORDS.append({'fixture':label,'profile':report['profile'],
                                'roles':report['mapped_required_role_count'],
                                'mapped_controls':report['mapped_control_count'],
                                'writable_controls':report['writable_control_count'],
                                'whole_body_ready':True,'read_only':True})

    def test_current_transform_blocker_is_actionable_without_mutation(self):
        ob=self._rig('boneforge');ob.scale=(1.,1.5,1.);bpy.context.view_layer.update()
        pose=w.raw_pose(ob);world=ob.matrix_world.copy();report=rig_diagnostics.analyze(ob)
        row=_workflow(report,'humanoid_whole_body')
        self.assertTrue(row['applicable']);self.assertFalse(row['ready'])
        self.assertIn('uniform object scale without shear',row['detail'])
        self.assertEqual(w.raw_pose(ob),pose)
        self.assertTrue(all(abs(a-b)<1e-8 for row_a,row_b in zip(ob.matrix_world,world) for a,b in zip(row_a,row_b)))

    def test_generated_quadruped_reports_its_existing_pose_workflow(self):
        scene,ob=generated_quadruped('cat');pose=w.raw_pose(ob);world=ob.matrix_world.copy()
        report=rig_diagnostics.analyze(ob);row=_workflow(report,'quadruped_whole_body')
        self.assertEqual(report['profile'],'Rigify Generated Quadruped (Cat)')
        self.assertEqual(report['mapped_required_role_count'],report['required_role_count'])
        self.assertTrue(row['applicable']);self.assertTrue(row['ready'],row)
        self.assertFalse(_workflow(report,'humanoid_whole_body')['applicable'])
        self.assertFalse(report['unsafe_mapped_controls']);self.assertEqual(w.raw_pose(ob),pose)
        self.assertTrue(all(abs(a-b)<1e-8 for row_a,row_b in zip(ob.matrix_world,world) for a,b in zip(row_a,row_b)))
        RECORDS.append({'fixture':'rigify_cat','profile':report['profile'],
                        'roles':report['mapped_required_role_count'],
                        'mapped_controls':report['mapped_control_count'],
                        'writable_controls':report['writable_control_count'],
                        'quadruped_pose_ready':True,'read_only':True})

    def test_operational_blockers_are_current_and_read_only(self):
        ob=self._rig('boneforge');pose=w.raw_pose(ob);modes=rs.mode_values(ob);scene=bpy.context.scene
        ob.b4ml.anchors.clear();report=rig_diagnostics.analyze(ob)
        self.assertFalse(_workflow(report,'pose_blending')['ready'])
        self.assertIn('at least two poses',_workflow(report,'pose_blending')['detail'])
        scene.frame_set(1);w.capture_anchor(ob,scene);scene.frame_set(9);w.capture_anchor(ob,scene)
        self.assertTrue(_workflow(rig_diagnostics.analyze(ob),'pose_blending')['ready'])
        with patch.object(motion_layer,'find',return_value=object()):
            kept=_workflow(rig_diagnostics.analyze(ob),'pose_blending')
        self.assertFalse(kept['ready']);self.assertIn('Restore the kept motion source',kept['detail'])
        ob.b4ml.anchors[0].payload='{'
        self.assertFalse(_workflow(rig_diagnostics.analyze(ob),'pose_blending')['ready'])
        ob.b4ml.anchors.clear();ob.b4ml.body_payload='{}'
        active=rig_diagnostics.analyze(ob);ob.b4ml.body_payload=''
        self.assertFalse(_workflow(active,'humanoid_whole_body')['ready'])
        self.assertIn('active preview',_workflow(active,'humanoid_whole_body')['detail'])
        for name in rig_diagnostics.detect_rig(ob.data.bones.keys()).controls:
            bone=ob.pose.bones[name];bone.lock_location=(True,True,True)
            bone.lock_rotation=(True,True,True);bone.lock_scale=(True,True,True)
            if bone.rotation_mode=='QUATERNION':bone.lock_rotations_4d=True;bone.lock_rotation_w=True
        locked=rig_diagnostics.analyze(ob)
        self.assertFalse(_workflow(locked,'automatic_capture')['ready'])
        self.assertEqual(locked['writable_control_count'],0)
        self.assertEqual(len(locked['blocked_mapped_controls']),locked['mapped_control_count'])
        self.assertEqual(rs.mode_values(ob),modes)
        for name,row in pose.items():
            self.assertEqual(tuple(ob.pose.bones[name].location),row['location'])
            self.assertEqual(tuple(ob.pose.bones[name].scale),row['scale'])

    def test_degenerate_recognized_body_frame_is_blocked(self):
        ob=self._rig('boneforge');bpy.context.view_layer.objects.active=ob;ob.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        point=ob.data.edit_bones['thigh.def-L'].head.copy()
        ob.data.edit_bones['thigh.def-R'].head=point
        bpy.ops.object.mode_set(mode='OBJECT');pose=w.raw_pose(ob)
        report=rig_diagnostics.analyze(ob);row=_workflow(report,'humanoid_whole_body')
        self.assertFalse(row['ready']);self.assertIn('Degenerate body frame',row['detail'])
        self.assertEqual(w.raw_pose(ob),pose)

    def test_unrecognized_rig_lists_missing_roles_without_claiming_support(self):
        data=bpy.data.armatures.new('Incomplete diagnostic rig')
        ob=bpy.data.objects.new('Incomplete diagnostic rig',data);bpy.context.scene.collection.objects.link(ob)
        bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
        for index,name in enumerate(('Head','Left','Right','MyShoulder')):
            bone=data.edit_bones.new(name);bone.head=(0,0,index);bone.tail=(0,0,index+0.5)
        bpy.ops.object.mode_set(mode='OBJECT')
        report=rig_diagnostics.analyze(ob)
        self.assertEqual((report['profile'],report['family'],report['mapping_schema']),
                         ('Unrecognized','unknown','unmapped'))
        self.assertEqual(len(report['missing_roles']),report['required_role_count'])
        self.assertFalse(_workflow(report,'automatic_capture')['ready'])
        self.assertFalse(_workflow(report,'humanoid_whole_body')['applicable'])
        self.assertFalse(_workflow(report,'quadruped_whole_body')['applicable'])
        bpy.ops.object.mode_set(mode='POSE')
        for bone in ob.pose.bones:bone.select=False
        ob.pose.bones['Head'].select=True
        scene=bpy.context.scene;scene.frame_set(2);w.capture_anchor(ob,scene,True)
        scene.frame_set(6);w.capture_anchor(ob,scene,True)
        manual=rig_diagnostics.analyze(ob)
        self.assertFalse(_workflow(manual,'automatic_capture')['ready'])
        self.assertTrue(_workflow(manual,'pose_blending')['ready'],manual)

    def test_inspect_operator_opens_live_panel_and_role_rows_render(self):
        ob=self._rig('boneforge');bpy.context.view_layer.objects.active=ob;ob.select_set(True)
        pose=w.raw_pose(ob);self.assertEqual(bpy.ops.b4ml.action(operation='INSPECT'),{'FINISHED'})
        self.assertTrue(ob.b4ml.show_rig_diagnostics);self.assertIn('14/14 roles',ob.b4ml.status)
        report=rig_diagnostics.decode(ob.b4ml.rig_diagnostics_report)
        self.assertIsNotNone(report);ob.b4ml.show_rig_role_mappings=True
        class Layout:
            def __init__(self):self.labels=[];self.props=[];self.alert=False
            def box(self):return self
            def row(self):return self
            def prop(self,state,name,**kwargs):self.props.append(name)
            def label(self,text='',**kwargs):self.labels.append(text)
        layout=Layout();ui._draw_rig_diagnostics(layout,ob.b4ml,report)
        self.assertIn('show_rig_diagnostics',layout.props)
        self.assertIn('show_rig_role_mappings',layout.props)
        self.assertIn('hips -> hips',layout.labels)
        self.assertIn('Whole-Body Pose',layout.labels)
        self.assertIn('Mapped controls: 29',layout.labels)
        self.assertEqual(w.raw_pose(ob),pose)

    def test_corrupt_saved_report_fails_closed_without_panel_exception(self):
        ob=self._rig('boneforge');ob.b4ml.show_rig_diagnostics=True
        base=rig_diagnostics.analyze(ob)
        corrupt=[]
        def changed(operation):
            value=json.loads(json.dumps(base));operation(value);return json.dumps(value)
        corrupt.append(changed(lambda value:value.update(bone_count='many')))
        corrupt.append(changed(lambda value:value.update(mapped_required_role_count=0)))
        corrupt.append(changed(lambda value:value['workflows'].__setitem__(1,dict(value['workflows'][0]))))
        corrupt.append(changed(lambda value:value['workflows'][-1].update(ready=True)))
        corrupt.append(changed(lambda value:value['mapped_roles'].__setitem__(1,dict(value['mapped_roles'][0]))))
        corrupt.append(changed(lambda value:value['warnings'].append('x'*513)))
        corrupt.append(changed(lambda value:value.update(unexpected=True)))
        oversized=' '*rig_diagnostics._MAX_REPORT_CHARS+'{}'
        nested='['*2000+'0'+']'*2000
        for value in (None,'', '{', '{"schema":1}', '{"schema":2}',oversized,nested,*corrupt):
            with self.subTest(value=value):
                self.assertIsNone(rig_diagnostics.decode(value))
                class Layout:
                    def __init__(self):self.labels=[];self.alert=False
                    def box(self):return self
                    def prop(self,*args,**kwargs):pass
                    def label(self,text='',**kwargs):self.labels.append(text)
                layout=Layout();ui._draw_rig_diagnostics(layout,ob.b4ml,None)
                self.assertIn('Click Inspect / Refresh above.',layout.labels)


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(RigDiagnosticTests))
    report={'tests':result.testsRun,'passed':result.wasSuccessful(),
            'failures':len(result.failures),'errors':len(result.errors),
            'records':RECORDS,'package':b4artists_ml.__file__}
    path=ROOT/'training/b4artists_ml/results'/os.environ.get(
        'B4ML_RIG_DIAGNOSTICS_RESULT','rig-diagnostics-v1.json')
    path.write_text(json.dumps(report,indent=2)+'\n')
    print('RIG_DIAGNOSTICS_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
