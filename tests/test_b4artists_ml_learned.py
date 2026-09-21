"""Independent decoder and learned model validation; host tests use actual BVH import."""
import json
import os
from pathlib import Path
import sys
import unittest
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,os.environ.get('B4ML_PACKAGE',str(ROOT)))
sys.path.insert(0,str(ROOT/'tests'))
sys.path.insert(0,str(ROOT/'training'/'b4artists_ml'))
from bvh_data import parse_bvh, limb_samples
try:
    import bpy
except ImportError:
    bpy=None

SIMPLE="""HIERARCHY
ROOT Root { OFFSET 1 2 3 CHANNELS 6 Xposition Yposition Zposition Zrotation Yrotation Xrotation
 JOINT Child { OFFSET 2 0 0 CHANNELS 3 Zrotation Yrotation Xrotation
  End Site { OFFSET 0 1 0 }
 }
}
MOTION
Frames: 2
Frame Time: 0.0083333
0 0 0 90 0 0 0 0 0
2 3 4 0 90 90 0 0 0
"""
class DecoderTests(unittest.TestCase):
    def test_known_noncommuting_rotations(self):
        pos=parse_bvh(SIMPLE).positions()
        np.testing.assert_allclose(pos[0],[[1,2,3],[1,4,3],[0,4,3]],atol=1e-12)
        np.testing.assert_allclose(pos[1],[[3,5,7],[3,5,5],[4,5,5]],atol=1e-12)

    def test_reject_invalid_data(self):
        for bad in (SIMPLE.replace('OFFSET 2','OFFSET nan'),
                    SIMPLE.replace('CHANNELS 3','CHANNELS -3'),
                    SIMPLE.replace('Frames: 2','Frames: 3'),
                    SIMPLE.replace('0.0083333','nan'),
                    SIMPLE.replace('Xposition Yposition','Xposition Xposition'),
                    SIMPLE.replace('0 0 0 90','nan 0 0 90')):
            with self.subTest(bad=bad[:50]),self.assertRaises(ValueError):
                parse_bvh(bad)

    def test_reject_truncation(self):
        with self.assertRaises(ValueError):
            parse_bvh('HIERARCHY ROOT A { OFFSET 0 MOTION')

    def test_manifest_and_features(self):
        import hashlib
        directory=ROOT/'training'/'b4artists_ml'
        manifests=[json.loads((directory/name).read_text()) for name in
                   ('data_manifest.json','confirmation_manifest.json','proportion_confirmation_manifest.json','expansion_manifest.json','context_confirmation_manifest.json')]
        manifest={'files':[row for m in manifests for row in m['files']]}
        ids=set()
        for row in manifest['files']:
            self.assertNotIn(row['clip'],ids);ids.add(row['clip'])
            data=(directory/'cache'/(row['clip']+'.bvh')).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(),row['sha256'])
            motion=parse_bvh(data.decode())
            self.assertAlmostEqual(motion.frame_time,1/120,places=6)
            for x,y,g in limb_samples(motion).values():
                self.assertEqual(x.shape[1],7)
                self.assertTrue(np.isfinite(x).all())
                np.testing.assert_allclose(np.linalg.norm(y,axis=1),1,atol=1e-10)
                np.testing.assert_allclose(np.sum(y*g[:,:3],axis=1),0,atol=1e-10)

@unittest.skipIf(bpy is None,'Bforartists runtime required')
class HostDecoderTests(unittest.TestCase):
    def test_actual_host_import(self):
        from io_anim_bvh import import_bvh
        from mathutils import Matrix
        records=[]
        for clip in ('07_01','13_10'):
            path=ROOT/'training'/'b4artists_ml'/'cache'/(clip+'.bvh')
            motion=parse_bvh(path.read_text());positions=motion.positions()
            result=import_bvh.load(bpy.context,filepath=str(path),
                global_matrix=Matrix.Identity(4),global_scale=1.0,frame_start=1,
                use_fps_scale=False,update_scene_fps=False,update_scene_duration=False,
                rotate_mode='NATIVE')
            self.assertEqual(result,{'FINISHED'})
            obj=bpy.context.object
            indices=np.linspace(0,len(positions)-1,9,dtype=int)
            errors=[]
            for frame in indices:
                bpy.context.scene.frame_set(int(frame)+1)
                evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
                for j,name in enumerate(motion.names):
                    if name.endswith('__end'):
                        continue
                    actual=np.asarray(evaluated.pose.bones[name].head)
                    errors.append(float(np.linalg.norm(actual-positions[frame,j])))
            max_error=max(errors)
            # Float32 host matrix accumulation over a multi-joint skeleton.
            self.assertLess(max_error,0.0002)
            records.append(dict(clip=clip,frames=len(indices),joint_samples=len(errors),max_position_error=max_error))
        print('BVH_DECODER_EVIDENCE: '+json.dumps(records),flush=True)



class AugmentationTests(unittest.TestCase):
    def test_preserves_segment_directions_and_joint_angles(self):
        from augment_limb import retarget,segments,TRAIN_RATIOS
        # Known right-angle bend, unequal source segments; independent geometric fixture.
        ratio=.6
        upper=np.array([1.,0,0]);lower=np.array([0,0,-1.])
        joint=upper*ratio;delta=joint+lower*(1-ratio)
        axis=delta/np.linalg.norm(delta)
        plane=joint-axis*np.dot(joint,axis);height=np.linalg.norm(plane)
        x=np.array([[0,0,0,*delta,ratio]])
        y=(plane/height)[None,:];g=np.array([[*axis,height]])
        for target_ratio in (*TRAIN_RATIOS,.5232833,.537037):
            xx,yy,gg=retarget(x,y,g,target_ratio)
            u,l=segments(xx,yy,gg)
            np.testing.assert_allclose(u,[upper],atol=1e-10)
            np.testing.assert_allclose(l,[lower],atol=1e-10)
            np.testing.assert_allclose(xx[0,3:6],upper*target_ratio+lower*(1-target_ratio),atol=1e-10)
            self.assertAlmostEqual(float(np.dot(u[0],l[0])),0)
            self.assertAlmostEqual(xx[0,6],target_ratio)

    def test_reject_invalid_geometry_and_ratios(self):
        from augment_limb import retarget,segments
        for ratio in (0,1,float('nan'),-1):
            with self.assertRaises(ValueError):
                retarget(np.zeros((1,7)),np.zeros((1,3)),np.zeros((1,4)),ratio)
        with self.assertRaises(ValueError):
            segments(np.zeros((1,7)),np.zeros((1,3)),np.zeros((1,4)))

class LearnedMathTests(unittest.TestCase):
    def test_checksum_and_reference_inference(self):
        from b4artists_ml import learned
        from train_limb_prior import features
        with self.assertRaises(ValueError):
            learned.decode_model(b'broken model')
        for kind in ('arm','leg'):
            row=learned.model()[kind]
            x=(row['input_min']+row['input_max'])*.5
            actual,reason=learned.infer_features(kind,x)
            expected=features(x[None,:],row['mean'],row['scale'],row['omega'],row['phase'])@row['coefficients']
            self.assertEqual(reason,'learned')
            np.testing.assert_allclose(actual,expected[0],atol=1e-12)

    def test_rotation_scale_mirror_equivariance(self):
        from b4artists_ml import learned
        rot=np.array([[0,-1,0],[1,0,0],[0,0,1.]])
        for kind,ratio in (('arm',.61),('leg',.49)):
            base,_=learned.direction(kind,[0,0,0],[.2,-.3,-.7],[ratio,1-ratio],np.eye(3),'L')
            self.assertIsNotNone(base)
            np.testing.assert_allclose(np.dot(base,[.2,-.3,-.7]),0,atol=1e-10)
            self.assertAlmostEqual(np.linalg.norm(base),1)
            mirrored,_=learned.direction(kind,[0,0,0],[-.2,-.3,-.7],[ratio,1-ratio],np.eye(3),'R')
            np.testing.assert_allclose(mirrored,np.asarray(base)*[-1,1,1],atol=1e-10)
            for scale in (1e-4,1,1e4):
                root=np.array([2,3,4])*scale
                actual,_=learned.direction(kind,root,root+rot@np.array([.2,-.3,-.7])*scale,
                    np.array([ratio,1-ratio])*scale,rot,'L')
                np.testing.assert_allclose(actual,rot@base,atol=1e-10)

    def test_domains_and_degenerate_input(self):
        from b4artists_ml import learned
        for target in ([0,0,0],[9,0,0]):
            self.assertIsNone(learned.direction('leg',[0,0,0],target,[.5,.5],np.eye(3),'L')[0])
        self.assertIsNone(learned.direction('arm',[0,0,0],[.2,-.3,-.7],[.1,.9],np.eye(3),'L')[0])
        with self.assertRaises(ValueError):
            learned.direction('leg',[float('nan'),0,0],[0,0,1],[.5,.5],np.eye(3),'L')
        with self.assertRaises(ValueError):
            learned.anatomical_basis([0,0,0],[0,0,0],[1,0,1],[-1,0,1])
        with self.assertRaises(ValueError):
            learned.direction('leg',[0,0,0],[0,0,1],[.5,.5],np.eye(3)*2,'L')

    def test_confirmation_runtime_matches_frozen_model(self):
        from b4artists_ml import learned
        from train_limb_prior import load_rows,features,project
        manifest=json.loads((ROOT/'training/b4artists_ml/confirmation_manifest.json').read_text())
        coverage={}
        for kind in ('arm','leg'):
            row=learned.model()[kind]
            used=0;fallback=0
            for clip,x,y,g in load_rows(manifest,'confirmation',kind):
                x=x[::17];g=g[::17]
                raw=features(x[:,3:],row['mean'],row['scale'],row['omega'],row['phase'])@row['coefficients']
                expected=project(raw,g[:,:3])
                for sample,plane in zip(x,expected):
                    ratio=sample[-1]
                    actual,reason=learned.direction(kind,[0,0,0],sample[3:6],[ratio,1-ratio],np.eye(3),'L')
                    if actual is None:
                        fallback+=1
                    else:
                        used+=1
                        np.testing.assert_allclose(actual,plane,atol=1e-10)
            self.assertGreater(used,0)
            coverage[kind]=dict(learned=used,fallback=fallback)
        print('LEARNED_RUNTIME_COVERAGE: '+json.dumps(coverage),flush=True)

    def test_anatomical_frame_matches_training(self):
        from b4artists_ml import learned
        points=([1,0,0],[-1,0,0],[2,0,3],[-2,0,3])
        np.testing.assert_allclose(learned.anatomical_basis(*points),np.eye(3))


@unittest.skipIf(bpy is None,'Bforartists runtime required')
class HostLearnedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import b4artists_ml
        from test_b4artists_ml_posing import boneforge_rig,rigify_rig
        b4artists_ml.register()
        cls.names=[boneforge_rig().name,rigify_rig().name,rigify_rig(full=True).name,
                   rigify_rig(generate=False).name,rigify_rig(full=True,generate=False).name]

    def tearDown(self):
        from b4artists_ml import posing
        for name in self.names:
            obj=bpy.data.objects.get(name)
            if obj and obj.b4ml.posing_payload:
                posing.finish(obj,bpy.context.scene,False)

    def activate(self,obj):
        from b4artists_ml import posing,workflow,learned
        if bpy.context.object and bpy.context.object.mode!='OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        for selected in bpy.context.selected_objects:
            selected.select_set(False)
        obj.select_set(True);bpy.context.view_layer.objects.active=obj
        bpy.context.scene.frame_set(1)
        before=workflow.raw_pose(obj)
        posing.begin(obj,bpy.context.scene)
        data=json.loads(obj.b4ml.posing_payload)
        limbs={r['id']:r for r in data['limbs']}
        basis=learned.anatomical_basis(*(tuple(obj.pose.bones[limbs[k]['joints'][0]].head)
            for k in ('leg-L','leg-R','arm-L','arm-R')))
        from mathutils import Vector
        for row in data['limbs']:
            root=obj.pose.bones[row['fk'][0]].head
            delta=np.array([.2,-.3,-.7]);delta[0]*=1 if row['id'].endswith('L') else -1
            item=obj.b4ml.pose_targets[row['id']]
            item.target.location=obj.matrix_world@(root+Vector(basis@delta)*sum(row['lengths']))
            item.learn_bend=True
        bpy.context.view_layer.update()
        return before,data

    def test_actual_rigs_pin_lengths_poles_and_cancel(self):
        from b4artists_ml import posing,workflow
        evidence=[]
        for name in self.names:
            obj=bpy.data.objects[name]
            before,data=self.activate(obj)
            helpers={i.name:(tuple(i.target.location),tuple(i.pole.location)) for i in obj.b4ml.pose_targets}
            result=posing.solve(obj,bpy.context.scene)
            self.assertGreaterEqual(sum(r['bend_source']=='learned' for r in result),2)
            for r in result:
                self.assertLess(r['normalized_error'],1e-5)
                self.assertLess(r['stretch'],1e-4)
            self.assertEqual(helpers,{i.name:(tuple(i.target.location),tuple(i.pole.location)) for i in obj.b4ml.pose_targets})
            evidence.append(dict(rig=name,limbs=result,ratios={r['id']:r['lengths'][0]/sum(r['lengths']) for r in data['limbs']}))
            posing.finish(obj,bpy.context.scene,False)
            after=workflow.raw_pose(obj)
            for key in before:
                np.testing.assert_allclose(after[key]['location'],before[key]['location'],atol=2e-6)
                np.testing.assert_allclose(after[key]['rotation'],before[key]['rotation'],atol=2e-6)
        print('LEARNED_RIG_EVIDENCE: '+json.dumps(evidence),flush=True)

    def test_authored_pole_and_zero_influence(self):
        from b4artists_ml import posing,workflow
        obj=bpy.data.objects[self.names[0]]
        self.activate(obj)
        obj.b4ml.learned_bend_strength=0
        posing.solve(obj,bpy.context.scene);baseline=workflow.raw_pose(obj)
        obj.b4ml.learned_bend_strength=1
        for item in obj.b4ml.pose_targets:
            item.learn_bend=False
        result=posing.solve(obj,bpy.context.scene)
        self.assertTrue(all(r['bend_source']=='authored pole' for r in result))
        current=workflow.raw_pose(obj)
        for key in baseline:
            np.testing.assert_allclose(current[key]['rotation'],baseline[key]['rotation'],atol=2e-6)
        posing.finish(obj,bpy.context.scene,False)

    def test_inference_failure_rolls_back(self):
        from b4artists_ml import posing,workflow,learned
        from unittest.mock import patch
        obj=bpy.data.objects[self.names[0]]
        self.activate(obj)
        posing.solve(obj,bpy.context.scene)
        before=workflow.raw_pose(obj)
        original=learned.direction;calls=[0]
        def fail(*args):
            calls[0]+=1
            if calls[0]==2:
                raise ValueError('Injected inference failure')
            return original(*args)
        with patch.object(learned,'direction',side_effect=fail),self.assertRaisesRegex(ValueError,'Injected'):
            posing.solve(obj,bpy.context.scene)
        after=workflow.raw_pose(obj)
        for key in before:
            np.testing.assert_allclose(after[key]['rotation'],before[key]['rotation'],atol=2e-6)
        posing.finish(obj,bpy.context.scene,False)

    def test_zz_save_reload_keep(self):
        import tempfile
        from b4artists_ml import posing,workflow,rig_state
        obj=bpy.data.objects[self.names[0]]
        modes=rig_state.mode_values(obj)
        self.activate(obj)
        obj.b4ml.learned_bend_strength=.65
        posing.solve(obj,bpy.context.scene)
        before=workflow.raw_pose(obj)
        with tempfile.TemporaryDirectory() as temp:
            path=str(Path(temp)/'learned-preview.blend')
            bpy.ops.wm.save_as_mainfile(filepath=path,check_existing=False)
            bpy.ops.wm.open_mainfile(filepath=path,load_ui=False,use_scripts=False)
            obj=bpy.data.objects[self.names[0]]
            bpy.context.view_layer.objects.active=obj
            self.assertTrue(all(i.learn_bend for i in obj.b4ml.pose_targets))
            self.assertAlmostEqual(obj.b4ml.learned_bend_strength,.65,places=6)
            posing.solve(obj,bpy.context.scene)
            after=workflow.raw_pose(obj)
            for key in before:
                np.testing.assert_allclose(after[key]['rotation'],before[key]['rotation'],atol=2e-6)
            posing.finish(obj,bpy.context.scene,True)
            self.assertEqual(len(obj.b4ml.anchors),1)
            self.assertEqual(rig_state.mode_values(obj),modes)
        obj.b4ml.learned_bend_strength=1.


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    print('B4ML_LEARNED_RESULT: '+('PASS' if result.wasSuccessful() else 'FAIL'),flush=True)
    if not result.wasSuccessful():
        raise SystemExit(1)
