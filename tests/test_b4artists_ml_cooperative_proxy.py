"""Actual-rig cancellation boundaries introduced by staged proxy preparation."""

from pathlib import Path

import sys,os,json,unittest,hashlib

ROOT=Path(__file__).resolve().parents[1]

sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]

import bpy,numpy as np

from unittest.mock import patch

from b4artists_ml import body_proxy,body_preview as body,workflow as w,posing

from test_b4artists_ml_proxy import ProxyTests



class CooperativeProxyTests(ProxyTests):

    def counts(self):return (len(bpy.data.objects),len(bpy.data.armatures),len(bpy.data.scenes))

    def test_cooperative_close_releases_private_scene(self):

        ob,source,session,targets,mask=self.fixtures.fixture('rigify_default')

        before=w.raw_pose(ob);counts=self.counts();context=(bpy.context.scene,bpy.context.view_layer.objects.active,bpy.context.mode)

        stages=0

        try:

            # Every externally observable preparation boundary must be cancellable.

            for boundary in range(100):

                steps=session.solve_steps(targets,mask,evaluation_backend='proxy')

                try:

                    for _ in range(boundary+1):progress=next(steps)

                    self.assertEqual(context,(bpy.context.scene,bpy.context.view_layer.objects.active,bpy.context.mode))

                    if progress['phase']!='preparing':break

                    stages+=1

                finally:steps.close()

                self.assertEqual(w.raw_pose(ob),before);self.assertEqual(self.counts(),counts);self.assertFalse(session.running)

            self.assertGreater(stages,5)

            self.assertEqual(w.raw_pose(ob),before);self.assertEqual(self.counts(),counts)

        finally:session.cancel()



    def test_save_mid_proxy_preview_excludes_private_scene(self):

        ob,source,session,targets,mask=self.fixtures.fixture('rigify_basic');session.cancel()

        bpy.context.view_layer.objects.active=ob;body.begin(ob,bpy.context.scene)

        before_scenes=sorted(s.name for s in bpy.data.scenes);name=ob.name

        body.start(ob)

        for _ in range(100):

            self.assertFalse(body.step(ob))

            if any(s.name.startswith('B4ML private evaluation') for s in bpy.data.scenes):break

        else:self.fail('Private scene preparation was never reached')

        path=ROOT/'training/b4artists_ml/cache/cooperative-proxy-save-v1.blend'

        bpy.ops.wm.save_as_mainfile(filepath=str(path))

        self.assertFalse(body._JOBS);self.assertEqual(sorted(s.name for s in bpy.data.scenes),before_scenes)

        bpy.ops.wm.open_mainfile(filepath=str(path));ob=bpy.data.objects[name]

        self.assertEqual(sorted(s.name for s in bpy.data.scenes),before_scenes)

        body.finish(ob,bpy.context.scene,False)



    def test_baseline_mismatch_discards_proxy_before_fallback(self):

        ob,source,session,targets,mask=self.fixtures.fixture('metarig_default');counts=self.counts()

        prepare=body_proxy.EvaluationProxy.prepare_steps

        def divergent(proxy,*args,**kwargs):

            yield from prepare(proxy,*args,**kwargs)

            proxy.obj.pose.bones[session.binding['root']].location.x+=.5;proxy.update()

        try:

            with patch.object(body_proxy.EvaluationProxy,'prepare_steps',divergent):result=session.solve(targets,mask)

            self.assertEqual(result['evaluation_backend'],'host');self.assertIn('differs from the original',result['proxy_rejection']);self.assertEqual(counts,self.counts())

        finally:session.cancel()



    def test_preparation_failure_releases_partial_copy(self):

        ob,source,session,targets,mask=self.fixtures.fixture('rigify_default');counts=self.counts();before=w.raw_pose(ob)

        try:

            with patch.object(body_proxy.EvaluationProxy,'update',side_effect=RuntimeError('injected preparation failure')):

                steps=session.solve_steps(targets,mask,evaluation_backend='proxy')

                with self.assertRaisesRegex(RuntimeError,'injected preparation failure'):

                    for _ in steps:pass

            self.assertEqual(counts,self.counts());self.assertEqual(before,w.raw_pose(ob));self.assertFalse(session.running)

        finally:session.cancel()



    def test_frame_change_at_preparation_boundary_rejected(self):

        ob,source,session,targets,mask=self.fixtures.fixture('rigify_default');counts=self.counts();before=w.raw_pose(ob);frame=bpy.context.scene.frame_current

        try:

            steps=session.solve_steps(targets,mask,evaluation_backend='proxy')

            for _ in range(100):

                progress=next(steps)

                if self.counts()[2]>counts[2]:break

            else:self.fail('Missing scene boundary')

            bpy.context.scene.frame_set(frame+1)

            with self.assertRaisesRegex(ValueError,'Return to the session frame'):next(steps)

            self.assertEqual(counts,self.counts());self.assertEqual(before,w.raw_pose(ob));self.assertFalse(session.running)

        finally:

            bpy.context.scene.frame_set(frame);session.cancel()



    def test_auto_backend_does_not_fit_after_source_invalidation(self):
        ob,source,session,targets,mask=self.fixtures.fixture('rigify_default');counts=self.counts();before=w.raw_pose(ob);frame=bpy.context.scene.frame_current
        try:
            steps=session.solve_steps(targets,mask,evaluation_backend='auto');next(steps)
            bpy.context.scene.frame_set(frame+1)
            with patch.object(session,'_apply',wraps=session._apply) as apply:
                with self.assertRaisesRegex(ValueError,'Return to the session frame'):next(steps)
                self.assertEqual(apply.call_count,0)
            self.assertEqual(counts,self.counts());self.assertEqual(before,w.raw_pose(ob));self.assertFalse(session.running)
        finally:
            bpy.context.scene.frame_set(frame);session.cancel()

    def test_cancel_probe_interrupts_preparation(self):

        ob,source,session,targets,mask=self.fixtures.fixture('rigify_default');counts=self.counts();before=w.raw_pose(ob);cancel=[False]

        try:

            steps=session.solve_steps(targets,mask,evaluation_backend='proxy',cancel_requested=lambda:cancel[0]);next(steps);cancel[0]=True

            with self.assertRaises(InterruptedError):next(steps)

            self.assertEqual(counts,self.counts());self.assertEqual(before,w.raw_pose(ob));self.assertFalse(session.running)

        finally:session.cancel()



if __name__=='__main__':unittest.main()

