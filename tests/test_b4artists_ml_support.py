"""Evaluated COM/support workflow on actual BoneForge/Rigify rigs and meshes."""
from pathlib import Path
import os,sys,json,time,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]
import bpy,numpy as np
from mathutils import Vector,Quaternion
import b4artists_ml
from b4artists_ml import support as s,contacts as c,workflow as w,rig_state as rs,posing as p
from test_b4artists_ml_posing import boneforge_rig,rigify_rig
BUILDERS={'boneforge':boneforge_rig,'rigify_basic':rigify_rig,'rigify_default':lambda:rigify_rig(full=True),
          'metarig_basic':lambda:rigify_rig(generate=False),'metarig_default':lambda:rigify_rig(full=True,generate=False)}
RECORDS=[]


def fixture(label):
    bpy.context.window.scene=bpy.data.scenes.new('Support '+label);scene=bpy.context.scene
    ob=BUILDERS[label]();p._update(ob)
    s.initialize(ob)
    return ob,scene


def snapshot_rig(ob):
    return dict(pose=w.raw_pose(ob),modes=rs.mode_values(ob),world=[list(v) for v in ob.matrix_world],
        action=ob.animation_data.action.as_pointer() if ob.animation_data and ob.animation_data.action else None,
        slot=w._slot(ob.animation_data),
        curves=c._action_signature(ob) if ob.animation_data and ob.animation_data.action else [],
        constraints={b.name:[(x.name,x.type,x.influence,x.mute) for x in b.constraints] for b in ob.pose.bones},
        rest={b.name:[list(v) for v in b.matrix_local] for b in ob.data.bones})


def point_contact(ob,scene,limb='leg-L',point=None):
    row=next(r for r in p.bindings(ob)[2] if r['id']==limb)
    matrix=ob.matrix_world@ob.pose.bones[row['joints'][2]].matrix
    if point is None:
        point=matrix.translation.copy();point.z=0.
    ob.b4ml.contact_limb=limb;ob.b4ml.contact_offset=matrix.inverted()@Vector(point)
    item=c.capture(ob,scene);item.use_support=True;item.start=1.;item.end=11.
    item.support_width=.4;item.support_length=.6
    return item


class SupportRigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):b4artists_ml.register()

    def test_five_native_rigs_meshes_and_animation_unchanged(self):
        for label in BUILDERS:
            with self.subTest(rig=label):
                ob,scene=fixture(label);root=p.bindings(ob)[1]
                ob.pose.bones[root].keyframe_insert('location',frame=1)
                ob.pose.bones[root].keyframe_insert('location',frame=11);scene.frame_set(1)
                point_contact(ob,scene,'leg-L');point_contact(ob,scene,'leg-R')
                joint='hand.def-L' if label=='boneforge' else 'DEF-hand.L' if label.startswith('rigify') else 'hand.L'
                data=bpy.data.meshes.new('Support bound mesh');point=ob.data.bones[joint].head_local.copy()
                data.from_pydata([point,point+Vector((.01,0,0)),point+Vector((0,.01,0))],[],[(0,1,2)])
                mesh=bpy.data.objects.new('Support bound mesh',data);scene.collection.objects.link(mesh)
                mesh.vertex_groups.new(name=joint).add([0,1,2],1.,'REPLACE');mesh.modifiers.new('Armature','ARMATURE').object=ob
                deps=bpy.context.evaluated_depsgraph_get();before_mesh=[list(v.co) for v in mesh.evaluated_get(deps).data.vertices]
                before=snapshot_rig(ob);frame=(scene.frame_current,scene.frame_subframe)
                first=s.snapshot(ob,scene,deps);timings=[]
                for _ in range(10):
                    start=time.perf_counter();result=s.analyze(ob,scene,deps);timings.append((time.perf_counter()-start)*1000)
                self.assertEqual(result['profile'],s.sample(ob,deps)[0]['profile']);self.assertEqual(len(result['segments']),17)
                self.assertEqual(len(result['contacts']),2);self.assertEqual(result['excluded_contacts'],[])
                self.assertGreater(result['plane_height'],0);self.assertIsNotNone(result['margin'])
                self.assertEqual(before,snapshot_rig(ob));self.assertEqual(frame,(scene.frame_current,scene.frame_subframe))
                np.testing.assert_array_equal(before_mesh,[list(v.co) for v in mesh.evaluated_get(deps).data.vertices])
                expected=sum(np.array(row['center'])*row['weight'] for row in result['segments'])
                np.testing.assert_allclose(expected,result['com'],atol=1e-12)
                RECORDS.append(dict(rig=label,profile=result['profile'],native_modes=before['modes'],
                    status=result['status'],com=result['com'],margin=result['margin'],first_ms=first['seconds']*1000,
                    warm_p50_ms=float(np.percentile(timings,50)),warm_p95_ms=float(np.percentile(timings,95)),
                    original_animation_rig_mesh_preserved=True))

    def test_editable_mass_positions_and_transformed_rig(self):
        ob,scene=fixture('rigify_basic');deps=bpy.context.evaluated_depsgraph_get();original=s.analyze(ob,scene,deps)
        for item in ob.b4ml.mass_segments:item.weight=0.
        head=ob.b4ml.mass_segments[4];head.weight=7.;head.fraction=.8
        result=s.analyze(ob,scene,bpy.context.evaluated_depsgraph_get())
        np.testing.assert_allclose(result['com'],result['segments'][4]['center'])
        self.assertGreater(np.linalg.norm(np.array(original['com'])-result['com']),.1)
        before=np.array(result['com']);ob.location=(3,-2,1);ob.rotation_euler=(.2,-.3,.4);ob.scale=(1.7,)*3;p._update(ob)
        transformed=s.analyze(ob,scene,bpy.context.evaluated_depsgraph_get())
        np.testing.assert_allclose(transformed['com'],ob.matrix_world@Vector(before),atol=5e-6)
        saved=ob.b4ml.support_report;head.weight=0.
        with self.assertRaises(ValueError):s.snapshot(ob,scene,bpy.context.evaluated_depsgraph_get())
        self.assertEqual(saved,ob.b4ml.support_report)

    def test_support_exclusions_and_gravity(self):
        ob,scene=fixture('boneforge');item=point_contact(ob,scene)
        def run():return s.analyze(ob,scene,bpy.context.evaluated_depsgraph_get())
        result=run();self.assertEqual(len(result['contacts']),1)
        item.strength=.5;self.assertEqual(run()['excluded_contacts'][0]['reason'],'contact strength below one')
        item.strength=1.;original_q=list(item.rotation);item.rotation=Quaternion(original_q)@Quaternion((1,0,0),.3)
        self.assertEqual(run()['excluded_contacts'][0]['reason'],'evaluated contact rotation exceeds tolerance')
        item.rotation=original_q;scene.frame_set(12);self.assertEqual(run()['excluded_contacts'][0]['reason'],'outside hold interval')
        scene.frame_set(1);item.point.x+=.1;self.assertEqual(run()['excluded_contacts'][0]['reason'],'evaluated contact drift exceeds tolerance')
        item.point.x-=.1;ob.b4ml.support_plane_point.z=1.
        self.assertEqual(run()['excluded_contacts'][0]['reason'],'contact off support plane')
        ob.b4ml.support_plane_point.z=0.;scene.use_gravity=False;self.assertEqual(run()['status'],'ZERO_GRAVITY')
        scene.use_gravity=True;scene.gravity=(1,0,-9.81);self.assertEqual(run()['status'],'INCLINED_GEOMETRY_ONLY')
        item.use_support=False;self.assertEqual(run()['status'],'NO_SUPPORT')

    def test_support_ui_operators_persist_without_rewriting_source(self):
        ob,scene=fixture('metarig_default');root=p.bindings(ob)[1]
        ob.pose.bones[root].keyframe_insert('location',frame=1);point_contact(ob,scene)
        ob.b4ml.mass_segments[0].weight=22.;ob.b4ml.mass_segments[0].inertia_radius=.41;ob.b4ml.show_support=True
        self.assertEqual(bpy.ops.b4ml.support(operation='ANALYZE'),{'FINISHED'})
        report=ob.b4ml.support_report;before=snapshot_rig(ob);objname=ob.name
        self.assertEqual(bpy.ops.b4ml.support(operation='INITIALIZE'),{'FINISHED'})
        self.assertEqual(ob.b4ml.mass_segments[0].weight,22.);self.assertAlmostEqual(ob.b4ml.mass_segments[0].inertia_radius,.41);self.assertEqual(before,snapshot_rig(ob))
        path=ROOT/'training/b4artists_ml/cache/support-roundtrip-v1.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path),check_existing=False)
        bpy.ops.wm.open_mainfile(filepath=str(path));ob=bpy.data.objects[objname];scene=bpy.context.scene
        self.assertEqual(ob.b4ml.support_report,report);self.assertTrue(ob.b4ml.contacts[0].use_support)
        self.assertEqual(ob.b4ml.mass_segments[0].weight,22.);self.assertAlmostEqual(ob.b4ml.mass_segments[0].inertia_radius,.41)
        self.assertAlmostEqual(json.loads(report)['segments'][0]['inertia_radius'],.41)
        result=s.analyze(ob,scene,bpy.context.evaluated_depsgraph_get())
        np.testing.assert_allclose(result['com'],json.loads(report)['com'],atol=1e-6)
        # RNA pointers change across reload; compare actual values instead.
        after=snapshot_rig(ob)
        for key in ('pose','modes','world','curves','constraints','rest'):self.assertEqual(before[key],after[key])

    def test_actual_ik_motion_changes_com_without_normalizing(self):
        ob,scene=fixture('rigify_basic');first=s.analyze(ob,scene,bpy.context.evaluated_depsgraph_get())
        row=next(r for r in p.bindings(ob)[2] if r['id']=='arm-L')
        self.assertEqual(row['mode'],'IK')
        ob.pose.bones[row['ik']].location.z+=.15;p._update(ob)
        before=snapshot_rig(ob);result=s.analyze(ob,scene,bpy.context.evaluated_depsgraph_get())
        self.assertGreater(np.linalg.norm(np.array(result['com'])-first['com']),.001)
        self.assertEqual(before,snapshot_rig(ob));self.assertEqual(p.bindings(ob)[2][0]['mode'],'IK')

    def test_read_only_analysis_with_locked_controls(self):
        ob,scene=fixture('rigify_basic');ob.pose.bones['head'].lock_rotation=(True,True,True)
        before=snapshot_rig(ob);s.analyze(ob,scene,bpy.context.evaluated_depsgraph_get());self.assertEqual(before,snapshot_rig(ob))
        with self.assertRaises(ValueError):s.body_solver.mapping(ob)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(SupportRigTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    destination=Path(os.environ.get('B4ML_SUPPORT_REPORT',str(ROOT/'training/b4artists_ml/results/support-host-v1.json')))
    destination.write_text(json.dumps(dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),
        skipped=len(result.skipped),host=bpy.app.version_string,records=RECORDS),indent=2),encoding='utf-8')
    if not result.wasSuccessful() or result.skipped:raise SystemExit(1)
