"""Validated humanoid semantic-role correction workflows."""
from pathlib import Path
import json
import os
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import addon_utils
import bpy

import b4artists_ml
from b4artists_ml import body_solver,posing,rig_diagnostics,rig_mapping,rig_state,ui,workflow
from b4artists_ml.rigs import source_maps
from test_b4artists_ml_context_rig import ContextRigTests
from test_b4artists_ml_imported_humanoids import authored
from test_b4artists_ml_quadruped_pose import _generate as generated_quadruped


RECORDS=[]


class MappingCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        addon_utils.enable('rigify',default_set=True,persistent=False)
        b4artists_ml.register();ContextRigTests.setUpClass();cls.fixtures=ContextRigTests()

    def _boneforge(self):
        obj,source,session,targets,mask=self.fixtures.fixture('boneforge',transformed=True)
        session.cancel();self._custom_head(obj)
        return obj

    def _custom_head(self,obj):
        bpy.context.view_layer.objects.active=obj;obj.select_set(True)
        head_name=rig_mapping.profile_for_object(obj).roles['head']
        bpy.ops.object.mode_set(mode='EDIT')
        original=obj.data.edit_bones[head_name];custom=obj.data.edit_bones.new('animator_head.custom')
        custom.head=original.head;custom.tail=original.tail;custom.matrix=original.matrix
        custom.parent=original.parent;custom.use_deform=False
        bpy.ops.object.mode_set(mode='OBJECT');bpy.context.view_layer.update()

    def _unchanged(self,obj):
        return dict(pose=workflow.raw_pose(obj),modes=rig_state.mode_values(obj),
                    action=obj.animation_data.action if obj.animation_data else None,
                    world=tuple(tuple(row) for row in obj.matrix_world))

    def _assert_unchanged(self,obj,before):
        self.assertEqual(workflow.raw_pose(obj),before['pose'])
        self.assertEqual(rig_state.mode_values(obj),before['modes'])
        self.assertIs(obj.animation_data.action if obj.animation_data else None,before['action'])
        self.assertEqual(tuple(tuple(row) for row in obj.matrix_world),before['world'])

    def test_correction_reaches_capture_posing_body_and_diagnostics_without_rig_mutation(self):
        obj=self._boneforge();before=self._unchanged(obj)
        rows=rig_mapping.set_correction(obj,'head','animator_head.custom')
        self.assertEqual(rows,{'head':'animator_head.custom'})
        profile=rig_mapping.profile_for_object(obj)
        self.assertEqual(profile.roles['head'],'animator_head.custom')
        self.assertIn('animator_head.custom',profile.controls)
        pose_profile,root,limbs=posing.bindings(obj)
        self.assertEqual(pose_profile.roles['head'],'animator_head.custom')
        binding=body_solver.mapping(obj)
        self.assertEqual(binding['effectors'][0],'animator_head.custom')
        scene=bpy.context.scene;scene.frame_set(3);workflow.capture_anchor(obj,scene)
        captured=json.loads(obj.b4ml.anchors[-1].payload)['pose']
        self.assertIn('animator_head.custom',captured)
        report=rig_diagnostics.analyze(obj)
        self.assertEqual(report['correction_state'],'active')
        self.assertEqual(report['manual_corrections'],[{'role':'head','bone':'animator_head.custom'}])
        self.assertEqual(next(row['bone'] for row in report['mapped_roles'] if row['role']=='head'),
                         'animator_head.custom')
        self.assertTrue(next(row for row in report['workflows']
                             if row['id']=='humanoid_whole_body')['ready'])
        before['pose'].update({name:value for name,value in workflow.raw_pose(obj).items()
                               if name not in before['pose']})
        self._assert_unchanged(obj,before)
        RECORDS.append({'workflow':'integration','role':'head','bone':'animator_head.custom',
                        'capture':True,'posing':True,'whole_body':True,'diagnostics':True})

    def test_boneforge_rigify_basic_default_and_imported_humanoid_accept_bound_role(self):
        rows=[]
        for label in ('boneforge','rigify_basic','rigify_default',
                      'mocap_humanoid_fbx','unity_humanoid_fbx','unreal_mannequin_fbx'):
            with self.subTest(rig=label):
                if label.endswith('_humanoid_fbx') or label=='unreal_mannequin_fbx':
                    obj,mesh,roles=authored(label[:-4],2);self._custom_head(obj)
                else:
                    obj,source,session,targets,mask=self.fixtures.fixture(label)
                    session.cancel();self._custom_head(obj)
                before=self._unchanged(obj)
                rig_mapping.set_correction(obj,'head','animator_head.custom')
                profile=rig_mapping.profile_for_object(obj);binding=body_solver.mapping(obj)
                self.assertEqual(profile.roles['head'],'animator_head.custom')
                self.assertEqual(binding['effectors'][0],'animator_head.custom')
                self.assertEqual(rig_diagnostics.analyze(obj)['correction_state'],'active')
                self._assert_unchanged(obj,before);rows.append(profile.name)
        self.assertEqual(len(rows),6)
        RECORDS.append({'workflow':'adapter_matrix','profiles':rows,'passed':True})

    def test_invalid_duplicate_structural_and_corrupt_data_fail_atomically(self):
        obj=self._boneforge();rig_mapping.set_correction(obj,'head','animator_head.custom')
        saved=obj[rig_mapping.PROPERTY_KEY];before=self._unchanged(obj)
        for role,bone,fragment in (
                ('unknown','hips','supported humanoid'),
                ('head','missing.control','does not exist'),
                ('head','hand.def-L','deform bone'),
                ('head','hips','distinct bone')):
            with self.subTest(role=role,bone=bone):
                with self.assertRaisesRegex(ValueError,fragment):
                    rig_mapping.set_correction(obj,role,bone)
                self.assertEqual(obj[rig_mapping.PROPERTY_KEY],saved)
                self._assert_unchanged(obj,before)
        obj[rig_mapping.PROPERTY_KEY]='{'
        with self.assertRaisesRegex(ValueError,'not valid JSON'):
            rig_mapping.profile_for_object(obj)
        with self.assertRaisesRegex(ValueError,'not valid JSON'):
            workflow.capture_anchor(obj,bpy.context.scene)
        report=rig_diagnostics.analyze(obj)
        self.assertEqual(report['correction_state'],'invalid')
        self.assertIn('not valid JSON',report['correction_error'])
        self.assertFalse(next(row for row in report['workflows']
                              if row['id']=='automatic_capture')['ready'])
        rig_mapping.clear_all(obj);self.assertNotIn(rig_mapping.PROPERTY_KEY,obj)
        self._assert_unchanged(obj,before)

    def test_case_variant_structural_prefixes_are_rejected(self):
        obj=self._boneforge();bpy.context.view_layer.objects.active=obj
        bpy.ops.object.mode_set(mode='EDIT')
        for index,name in enumerate(('dEf-Bad','mCh-Bad','oRg-Bad','wGt-Bad','WgTs_Bad')):
            bone=obj.data.edit_bones.new(name);bone.head=(index,0,0);bone.tail=(index,0,1)
        bpy.ops.object.mode_set(mode='OBJECT');before=self._unchanged(obj)
        for bone,category in (('dEf-Bad','deform'),('mCh-Bad','mechanism'),
                              ('oRg-Bad','organization'),('wGt-Bad','widget'),('WgTs_Bad','widget')):
            with self.subTest(bone=bone):
                with self.assertRaisesRegex(ValueError,category):
                    rig_mapping.set_correction(obj,'head',bone)
                self.assertNotIn(rig_mapping.PROPERTY_KEY,obj);self._assert_unchanged(obj,before)

    def test_optional_neck_role_is_editable_and_used_by_whole_body_mapping(self):
        obj=self._boneforge();bpy.context.view_layer.objects.active=obj
        bpy.ops.object.mode_set(mode='EDIT')
        obj.data.edit_bones['neck'].name='animator_neck.custom'
        bpy.ops.object.mode_set(mode='OBJECT');before=self._unchanged(obj)
        self.assertNotIn('neck',rig_mapping.profile_for_object(obj).roles)
        rig_mapping.set_correction(obj,'neck','animator_neck.custom')
        profile=rig_mapping.profile_for_object(obj);binding=body_solver.mapping(obj)
        self.assertEqual(profile.roles['neck'],'animator_neck.custom')
        self.assertIn('animator_neck.custom',binding['names'])
        self.assertIn('animator_neck.custom',binding['rotations'])
        report=rig_diagnostics.analyze(obj)
        self.assertEqual(report['mapped_required_role_count'],len(rig_mapping.REQUIRED))
        self.assertEqual(next(row['bone'] for row in report['mapped_roles'] if row['role']=='neck'),
                         'animator_neck.custom')
        enum=ui.B4ML_PG_settings.bl_rna.properties['mapping_role'].enum_items
        self.assertEqual({item.identifier for item in enum},set(rig_mapping.HUMANOID_ROLES))
        self._assert_unchanged(obj,before)

    def test_generated_rigify_reserved_root_controls_are_rejected_atomically(self):
        obj,source,session,targets,mask=self.fixtures.fixture('rigify_basic')
        session.cancel();before=self._unchanged(obj)
        for bone in ('torso','root'):
            with self.subTest(bone=bone):
                self.assertIn(bone,obj.pose.bones)
                with self.assertRaisesRegex(ValueError,'reserved master/root'):
                    rig_mapping.set_correction(obj,'head',bone)
                self.assertNotIn(rig_mapping.PROPERTY_KEY,obj)
                self._assert_unchanged(obj,before)

    def test_bone_change_marks_payload_stale_and_clear_all_recovers(self):
        obj=self._boneforge();rig_mapping.set_correction(obj,'head','animator_head.custom')
        bpy.context.view_layer.objects.active=obj;bpy.ops.object.mode_set(mode='EDIT')
        obj.data.edit_bones['animator_head.custom'].name='animator_head.renamed'
        bpy.ops.object.mode_set(mode='OBJECT')
        with self.assertRaisesRegex(ValueError,'stale after a rig bone change'):
            rig_mapping.profile_for_object(obj)
        profile,rows,error=rig_mapping.status(obj)
        self.assertEqual(profile.name,'BoneForge Control Rig');self.assertFalse(rows)
        self.assertIn('stale after a rig bone change',error)
        rig_mapping.clear_all(obj);self.assertEqual(rig_mapping.profile_for_object(obj).name,
                                                     'BoneForge Control Rig')

    def test_clear_role_rejects_a_new_duplicate_without_partial_write(self):
        obj=self._boneforge()
        rig_mapping.set_correction(obj,'head','animator_head.custom')
        rig_mapping.set_correction(obj,'hips','head')
        saved=obj[rig_mapping.PROPERTY_KEY];before=self._unchanged(obj)
        with self.assertRaisesRegex(ValueError,'distinct bone'):
            rig_mapping.clear_correction(obj,'head')
        self.assertEqual(obj[rig_mapping.PROPERTY_KEY],saved)
        self._assert_unchanged(obj,before)

    def test_operator_and_save_reload_preserve_exact_mapping(self):
        obj=self._boneforge();state=obj.b4ml;state.mapping_role='head'
        state.mapping_bone='animator_head.custom'
        self.assertEqual(bpy.ops.b4ml.mapping_correction(operation='APPLY'),{'FINISHED'})
        saved=obj[rig_mapping.PROPERTY_KEY]
        report=rig_diagnostics.decode(state.rig_diagnostics_report)
        self.assertEqual(report['correction_state'],'active')
        name=obj.name;path=ROOT/'training/b4artists_ml/cache/mapping-corrections-v1-reload.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
        obj=bpy.data.objects[name];bpy.context.view_layer.objects.active=obj
        self.assertEqual(obj[rig_mapping.PROPERTY_KEY],saved)
        self.assertEqual(rig_mapping.profile_for_object(obj).roles['head'],'animator_head.custom')
        self.assertEqual(bpy.ops.b4ml.mapping_correction(operation='CLEAR_ALL'),{'FINISHED'})
        self.assertNotIn(rig_mapping.PROPERTY_KEY,obj)
        RECORDS.append({'workflow':'operator_reload','save_reload':True,'clear':True})

    def test_quadruped_cannot_acquire_humanoid_corrections(self):
        scene,obj=generated_quadruped('cat');bpy.context.view_layer.objects.active=obj
        before=self._unchanged(obj)
        with self.assertRaisesRegex(ValueError,'recognized humanoid'):
            rig_mapping.set_correction(obj,'head','head')
        self.assertNotIn(rig_mapping.PROPERTY_KEY,obj);self._assert_unchanged(obj,before)

    def test_deform_only_rigify_profile_cannot_be_reactivated(self):
        source=next(data for data in source_maps().values()
                    if data['name']=='Rigify Deform')
        data=bpy.data.armatures.new('Deform-only correction fixture')
        obj=bpy.data.objects.new('Deform-only correction fixture',data)
        bpy.context.scene.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj
        obj.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
        for index,name in enumerate(source['bones']):
            bone=data.edit_bones.new(name);bone.head=(0,0,index);bone.tail=(0,0,index+.5)
        bpy.ops.object.mode_set(mode='OBJECT')
        self.assertEqual(rig_mapping.detect_rig(data.bones.keys()).name,'Rigify Deform')
        before=self._unchanged(obj)
        with self.assertRaisesRegex(ValueError,'deform-only skeleton'):
            rig_mapping.set_correction(obj,'head','DEF-head')
        self.assertNotIn(rig_mapping.PROPERTY_KEY,obj);self._assert_unchanged(obj,before)


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(MappingCorrectionTests))
    report={'tests':result.testsRun,'passed':result.wasSuccessful(),
            'failures':len(result.failures),'errors':len(result.errors),
            'records':RECORDS,'package':b4artists_ml.__file__}
    path=ROOT/'training/b4artists_ml/results'/os.environ.get(
        'B4ML_MAPPING_CORRECTIONS_RESULT','mapping-corrections-v1.json')
    path.write_text(json.dumps(report,indent=2)+'\n')
    print('MAPPING_CORRECTIONS_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
