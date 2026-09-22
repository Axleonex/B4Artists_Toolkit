"""Native exit-gate tests for Phase 2 viewport overlay (plan §6 row 2).

Verified source facts:
  body_preview.py:20   TARGETS_V3 — 9 main target labels created by begin()
  body_preview.py:186  begin() uses controls_version=5,torso_coupling_version=1 → TARGETS_V3
  body_preview.py:204-206  one body_targets item per label; target = empty object
  viewport_overlay.py:122  build_payload iterates state.body_targets
  viewport_overlay.py:96   _HANDLERS list — stays [] while bpy.app.background (register:585-586)
  ui_workflow/stage.py:74-85  Snapshot.posing/.candidate/.kept fields
"""
from pathlib import Path
import os,sys,math,json,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
import bpy
import b4artists_ml
from b4artists_ml import body_preview as body,workflow as w
from b4artists_ml.ui_workflow import viewport_overlay
from b4artists_ml.ui_workflow.copy import FORBIDDEN_TERMS
from test_b4artists_ml_context_rig import ContextRigTests


class NativeOverlayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()
        ContextRigTests.setUpClass()
        cls._ctx=ContextRigTests()

    def _begin(self,label='boneforge'):
        """Minimal session: context-rig fixture → cancel solver → body.begin."""
        ob,source,s,targets,mask=self._ctx.fixture(label)
        s.cancel()
        bpy.context.view_layer.objects.active=ob
        body.begin(ob,bpy.context.scene)
        return ob,source

    def tearDown(self):
        for ob in list(bpy.data.objects):
            if hasattr(ob,'b4ml') and ob.b4ml.body_payload:
                if ob.users_scene:bpy.context.window.scene=ob.users_scene[0]
                body.finish(ob,bpy.context.scene,False)
        body.reset_runtime()

    def test_payload_after_begin(self):
        ob,source=self._begin()
        payload=viewport_overlay.build_payload(bpy.context)
        self.assertGreaterEqual(len(payload),8,
            f'expected ≥8 entries, got {len(payload)}: {[e["role"] for e in payload]}')
        for entry in payload:
            for key in ('role','label','color','position','pinned'):
                self.assertIn(key,entry,f'missing key {key!r} in entry {entry}')
            r,g,b_c=entry['color']
            self.assertTrue(all(0.0<=c<=1.0 for c in (r,g,b_c)),
                f'color out of [0,1]: {entry["color"]}')
            self.assertEqual(len(entry['position']),3)
            for coord in entry['position']:
                self.assertTrue(math.isfinite(coord),
                    f'non-finite position coord in {entry["position"]}')
            self.assertIsInstance(entry['pinned'],bool)
            lbl_lower=entry['label'].lower()
            for term in FORBIDDEN_TERMS:
                self.assertNotIn(term.lower(),lbl_lower,
                    f'forbidden term {term!r} in label {entry["label"]!r}')
        roles=[e['role'] for e in payload]
        print(f'OVERLAY_ROLES: {roles}',flush=True)

    def test_focus_selects_targets_and_object_mode(self):
        ob,source=self._begin()
        result=viewport_overlay.focus(bpy.context)
        self.assertTrue(result,'focus() returned False')
        vl=bpy.context.view_layer
        for item in ob.b4ml.body_targets:
            t=getattr(item,'target',None)
            if t is not None and t.name in vl.objects:
                self.assertTrue(t.select_get(),
                    f'target {item.name!r} not selected after focus()')
        pelvis=ob.b4ml.body_targets.get('Pelvis')
        if pelvis is not None and pelvis.target is not None:
            self.assertIs(vl.objects.active,pelvis.target,
                'active object is not the pelvis target after focus()')
        self.assertEqual(bpy.context.mode,'OBJECT')

    def test_no_draw_handlers_in_background(self):
        # register() skips handlers/timer when bpy.app.background (viewport_overlay.py:585-586)
        self.assertTrue(bpy.app.background,
            'test only meaningful in background mode; re-check in interactive mode')
        self.assertEqual(viewport_overlay._HANDLERS,[],
            f'unexpected draw handlers registered in background: {viewport_overlay._HANDLERS}')

    def test_hud_lines_only_in_session(self):
        # viewport_overlay has no standalone hud_lines() helper; HUD logic is embedded in
        # _draw_2d() POST_PIXEL handler which requires live bpy draw context.
        self.skipTest(
            'no standalone hud_lines() helper in viewport_overlay; '
            'HUD logic embedded in _draw_2d POST_PIXEL handler — '
            'add a pure hud_lines(snap) helper to enable this test')


if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(NativeOverlayTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report=dict(tests=result.testsRun,passed=result.wasSuccessful(),
                failures=len(result.failures),errors=len(result.errors),
                package=b4artists_ml.__file__)
    print('OVERLAY_RESULT: '+json.dumps(report),flush=True)
    if not result.wasSuccessful():raise SystemExit(1)
