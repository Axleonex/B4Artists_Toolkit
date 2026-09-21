"""Differential actual-rig verification of dependency-closed evaluation copies."""
from pathlib import Path
import os,sys,json,time,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy,numpy as np
from mathutils import Vector,Quaternion
import b4artists_ml
from b4artists_ml import body_proxy,body_solver,posing,workflow as w
from test_b4artists_ml_context_rig import ContextRigTests
RECORDS=[]

class ProxyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ContextRigTests.setUpClass();cls.fixtures=ContextRigTests()

    def test_differential_random_controls(self):
        rng=np.random.default_rng(20260906)
        for label in os.environ.get('B4ML_PROXY_RIGS',','.join(self.fixtures.builders)).split(','):
            with self.subTest(rig=label):
                ob,source,session,targets,mask=self.fixtures.fixture(label)
                counts=(len(bpy.data.objects),len(bpy.data.armatures),len(bpy.data.scenes))
                original_context=(bpy.context.scene,bpy.context.view_layer.objects.active,ob.mode)
                proxy=None
                try:
                    started=time.perf_counter()
                    proxy=body_proxy.EvaluationProxy(ob,set(session.binding['names']+session.binding['rotations']+session.binding['effectors']+[session.binding['root']])|set(session.lengths))
                    startup=(time.perf_counter()-started)*1000
                    self.assertEqual(original_context,(bpy.context.scene,bpy.context.view_layer.objects.active,ob.mode))
                    maximum=0.;timing={'full':0.,'proxy':0.}
                    for i in range(25):
                        x=rng.normal(0,.12,3+3*len(session.q0));x[:3]*=.1
                        points={}
                        for kind,obj in (('full',ob),('proxy',proxy.obj)):
                            started=time.perf_counter()
                            obj.pose.bones[session.binding['root']].location=session.root_location+Vector(x[:3])*session.scale
                            for j,(name,q) in enumerate(zip(session.binding['rotations'],session.q0)):
                                v=Vector(x[3+j*3:6+j*3]);angle=v.length
                                body_solver._set_quat(obj.pose.bones[name],q@Quaternion(v/angle,angle))
                            if kind=='proxy':proxy.update()
                            else:posing._update(obj)
                            points[kind]=np.array([obj.pose.bones[n].matrix for n in session.binding['names']])
                            timing[kind]+=time.perf_counter()-started
                        maximum=max(maximum,float(np.max(np.abs(points['full']-points['proxy']))))
                    row=dict(rig=label,samples=25,max_matrix_error=maximum,total_bones=len(ob.pose.bones),needed_bones=len(proxy.needed),proxy_bones=len(proxy.obj.pose.bones),muted_constraints=proxy.muted_constraints,startup_ms=startup,full_ms=timing['full']*1000,proxy_ms=timing['proxy']*1000)
                    RECORDS.append(row);print('PROXY_METRIC: '+json.dumps(row),flush=True)
                    self.assertLess(maximum,2e-5)
                finally:
                    if proxy:proxy.close()
                    session.cancel()
                self.assertEqual(counts,(len(bpy.data.objects),len(bpy.data.armatures),len(bpy.data.scenes)))

    def test_complete_solves_match_host_and_cleanup(self):
        for label in ('boneforge','rigify_basic','rigify_default','metarig_basic','metarig_default'):
            with self.subTest(rig=label):
                ob,source,session,targets,mask=self.fixtures.fixture(label,transformed=True)
                counts=(len(bpy.data.objects),len(bpy.data.armatures),len(bpy.data.scenes))
                try:
                    direct=session.solve(targets,mask,evaluation_backend='host')
                    proxied=session.solve(targets,mask,evaluation_backend='proxy')
                    delta=float(np.max(np.abs(direct['points']-proxied['points'])))
                    row=dict(fixture=label,full={k:v for k,v in direct.items() if k!='points'},proxy={k:v for k,v in proxied.items() if k!='points'},point_delta=delta)
                    RECORDS.append(row);print('PROXY_SOLVE: '+json.dumps(row),flush=True)
                    self.assertLess(delta,2e-5)
                    self.assertLess(proxied['pin_error'],2e-4)
                    self.assertLessEqual(proxied['proposal_error'],direct['proposal_error']*1.01)
                    self.assertEqual(counts,(len(bpy.data.objects),len(bpy.data.armatures),len(bpy.data.scenes)))
                finally:session.cancel()

    def test_cooperative_close_releases_private_scene(self):
        ob,source,session,targets,mask=self.fixtures.fixture('rigify_default')
        before=w.raw_pose(ob);counts=(len(bpy.data.objects),len(bpy.data.armatures),len(bpy.data.scenes))
        steps=None
        try:
            steps=session.solve_steps(targets,mask,evaluation_backend='proxy')
            for _ in range(2048):
                next(steps)
                if len(bpy.data.scenes)==counts[2]+1:break
            self.assertEqual(len(bpy.data.scenes),counts[2]+1)
            steps.close()
            steps=None
            self.assertEqual(w.raw_pose(ob),before)
            self.assertEqual(counts,(len(bpy.data.objects),len(bpy.data.armatures),len(bpy.data.scenes)))
        finally:
            if steps:steps.close()
            session.cancel()

    def test_private_edit_mode_preserves_source_pose_mode(self):
        ob,source,session,targets,mask=self.fixtures.fixture('rigify_basic')
        bpy.context.view_layer.objects.active=ob;ob.select_set(True)
        bpy.ops.object.mode_set(mode='POSE');proxy=None
        try:
            proxy=body_proxy.EvaluationProxy(ob,set(session.binding['names']+session.binding['rotations']+session.binding['effectors']+[session.binding['root']]))
            self.assertEqual(ob.mode,'POSE');self.assertEqual(bpy.context.mode,'POSE')
            self.assertIs(bpy.context.view_layer.objects.active,ob)
        finally:
            if proxy:proxy.close()
            bpy.ops.object.mode_set(mode='OBJECT');session.cancel()


    def test_auto_fallback_for_external_dependency(self):
        ob,source,session,targets,mask=self.fixtures.fixture('rigify_basic')
        external=bpy.data.objects.new('External proxy test target',None);bpy.context.scene.collection.objects.link(external)
        constraint=ob.pose.bones[session.binding['names'][4]].constraints.new('COPY_LOCATION')
        constraint.target=external;constraint.influence=0.
        try:
            result=session.solve(targets,mask)
            self.assertEqual(result['evaluation_backend'],'host')
            self.assertIn('External constraint',result['proxy_rejection'])
            before=w.raw_pose(ob)
            with self.assertRaisesRegex(ValueError,'External constraint'):
                session.solve(targets,mask,evaluation_backend='proxy')
            self.assertEqual(w.raw_pose(ob),before)
        finally:
            ob.pose.bones[session.binding['names'][4]].constraints.remove(constraint)
            bpy.data.objects.remove(external,do_unlink=True);session.cancel()

    def test_injected_proxy_failure_restores_pose_and_cleanup(self):
        from unittest.mock import patch
        ob,source,session,targets,mask=self.fixtures.fixture('rigify_basic')
        before=w.raw_pose(ob);counts=(len(bpy.data.objects),len(bpy.data.armatures),len(bpy.data.scenes))
        apply=session._apply;calls=0
        def fail(x,obj=None,update=None):
            nonlocal calls
            apply(x,obj=obj,update=update)
            if obj is not None and obj!=ob:
                calls+=1
                if calls==3:raise RuntimeError('injected proxy failure')
        try:
            with patch.object(session,'_apply',side_effect=fail):
                with self.assertRaisesRegex(RuntimeError,'injected proxy failure'):session.solve(targets,mask)
            self.assertEqual(w.raw_pose(ob),before);self.assertFalse(session.running)
            self.assertEqual(counts,(len(bpy.data.objects),len(bpy.data.armatures),len(bpy.data.scenes)))
        finally:session.cancel()

    def test_save_mid_proxy_preview_excludes_private_scene(self):
        from b4artists_ml import body_preview as body
        ob,source,session,targets,mask=self.fixtures.fixture('rigify_basic');session.cancel()
        bpy.context.view_layer.objects.active=ob;body.begin(ob,bpy.context.scene)
        before_scenes=sorted(s.name for s in bpy.data.scenes);name=ob.name
        body.start(ob)
        for _ in range(2048):
            body.step(ob)
            if any(s.name.startswith('B4ML private evaluation') for s in bpy.data.scenes):break
        self.assertTrue(any(s.name.startswith('B4ML private evaluation') for s in bpy.data.scenes))
        path=ROOT/'training/b4artists_ml/cache/proxy-save-test.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        self.assertFalse(body._JOBS);self.assertEqual(sorted(s.name for s in bpy.data.scenes),before_scenes)
        bpy.ops.wm.open_mainfile(filepath=str(path));ob=bpy.data.objects[name]
        self.assertEqual(sorted(s.name for s in bpy.data.scenes),before_scenes)
        body.finish(ob,bpy.context.scene,False)


    def test_frame_dependent_driver_matches_subframe(self):
        ob,source,session,targets,mask=self.fixtures.fixture('rigify_basic')
        scene=bpy.context.scene;scene.frame_set(8,subframe=.5)
        bone=ob.pose.bones[session.binding['names'][0]]
        constraint=bone.constraints.new('COPY_ROTATION');constraint.target=ob
        constraint.subtarget='root'  # Ancestor target avoids a cyclic dependency in this fixture.
        curve=constraint.driver_add('influence');curve.driver.expression='0.2 + 0.01 * frame'
        proxy=None
        try:
            posing._update(ob)
            seeds=set(session.binding['names']+session.binding['rotations']+session.binding['effectors']+[session.binding['root']])
            proxy=body_proxy.EvaluationProxy(ob,seeds)
            self.assertEqual(proxy.scene.frame_current,8);self.assertEqual(proxy.scene.frame_subframe,.5)
            self.assertEqual(scene.frame_current,8);self.assertEqual(scene.frame_subframe,.5)
            for n in session.binding['names']:
                np.testing.assert_allclose(np.array(ob.pose.bones[n].matrix),np.array(proxy.obj.pose.bones[n].matrix),atol=2e-5,rtol=0.)
            self.assertAlmostEqual(proxy.obj.pose.bones[bone.name].constraints[-1].influence,constraint.influence,places=6)
        finally:
            if proxy:proxy.close()
            constraint.driver_remove('influence');bone.constraints.remove(constraint)
            scene.frame_set(1);session.cancel()


    def test_baseline_mismatch_discards_proxy_before_fallback(self):
        from unittest.mock import patch
        ob,source,session,targets,mask=self.fixtures.fixture('metarig_default')
        counts=(len(bpy.data.objects),len(bpy.data.armatures),len(bpy.data.scenes))
        factory=body_proxy.EvaluationProxy
        class DivergentProxy(factory):
            def prepare_steps(proxy,*args,**kwargs):
                yield from super().prepare_steps(*args,**kwargs)
                proxy.obj.pose.bones[session.binding['root']].location.x+=.5
                proxy.update()
        try:
            with patch.object(body_proxy,'EvaluationProxy',DivergentProxy):
                result=session.solve(targets,mask)
            self.assertEqual(result['evaluation_backend'],'host')
            self.assertIn('differs from the original',result['proxy_rejection'])
            self.assertEqual(counts,(len(bpy.data.objects),len(bpy.data.armatures),len(bpy.data.scenes)))
        finally:session.cancel()

    def test_complete_rig_proxy_preserves_all_bones_and_source_data(self):
        ob,source,session,targets,mask=self.fixtures.fixture('rigify_default')
        counts=(len(bpy.data.objects),len(bpy.data.armatures),len(bpy.data.scenes));before=w.raw_pose(ob);data=ob.data;proxy=None
        try:
            proxy=body_proxy.EvaluationProxy(ob,set(ob.pose.bones),preserve_all=True)
            self.assertEqual(len(proxy.obj.pose.bones),len(ob.pose.bones))
            self.assertEqual(proxy.needed,set(ob.pose.bones.keys()))
            if data.animation_data and len(data.animation_data.drivers):
                self.assertIsNot(proxy.obj.data,data);self.assertIs(proxy.obj.data,proxy.data)
            else:
                self.assertIs(proxy.obj.data,data);self.assertIsNone(proxy.data)
            self.assertEqual(w.raw_pose(ob),before)
        finally:
            if proxy:proxy.close()
            session.cancel()
        self.assertEqual(counts,(len(bpy.data.objects),len(bpy.data.armatures),len(bpy.data.scenes)))


if __name__=='__main__':
    selection=os.environ.get('B4ML_PROXY_TEST')
    suite=unittest.defaultTestLoader.loadTestsFromName(selection,sys.modules[__name__]) if selection else unittest.defaultTestLoader.loadTestsFromTestCase(ProxyTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report=dict(package=b4artists_ml.__file__,tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),errors=len(result.errors),records=RECORDS)
    (ROOT/'training/b4artists_ml/results'/os.environ.get('B4ML_PROXY_RESULT','proxy-evaluation-current.json')).write_text(json.dumps(report,indent=2)+'\n')
    print('PROXY_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
