"""Run the frozen v0.37.2-dev static-capsule binding contract in Bforartists.

The current worktree tests intentionally cover newer moving/continuous capsule
APIs.  This runner is pinned to the static contract shipped in the exact
v0.37.2-dev archive so a mixed-version test cannot be reported as archive
evidence.
"""

from pathlib import Path
import hashlib
import inspect
import json
import os
import sys
import time
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(os.environ.get("B4ML_PACKAGE", ""))
ARCHIVE_LABEL = "b4artists_ml_v0.37.2-dev.zip"
REPORT = ROOT / "docs" / "b4artists_ml" / "capsule-exact-archive-binding-v1.json"


def endpoint(name, location):
    import bpy

    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "SPHERE"
    obj.empty_display_size = 0.1
    obj.location = location
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.update()
    return obj


class FrozenCapsuleBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import b4artists_ml

        b4artists_ml.register()

    def test_request_and_static_endpoint_binding(self):
        import bpy
        from b4artists_ml import secondary_motion as secondary
        from test_b4artists_ml_secondary_motion import fixture

        obj, _, _, _, _, _ = fixture("boneforge")
        state = obj.b4ml
        start = endpoint("B4ML Frozen Capsule Start", (-1.0, 0.0, 0.0))
        end = endpoint("B4ML Frozen Capsule End", (1.0, 0.0, 0.0))
        state.secondary_collision = True
        state.secondary_collision_shape = "CAPSULE"
        state.secondary_capsule_start = start
        state.secondary_capsule_end = end
        state.secondary_capsule_radius = 0.25

        raw = secondary.request(obj, bpy.context.scene)
        self.assertEqual(raw["collision_shape"], "CAPSULE")
        self.assertEqual(raw["collision_capsule_start"], start.name_full)
        self.assertEqual(raw["collision_capsule_end"], end.name_full)
        self.assertAlmostEqual(raw["collision_capsule_radius"], 0.25)
        self.assertFalse(raw.get("collision_capsule_continuous", False))

        signature = inspect.signature(secondary._capsule_collider_values)
        self.assertEqual(
            list(signature.parameters),
            ["state", "scene", "rig", "start", "end", "radius"],
        )
        values = secondary._capsule_collider_values(
            state, bpy.context.scene, obj, start, end, 0.25)
        self.assertEqual(values[3], "STATIC_CAPSULE:" + start.name + ":" + end.name)
        self.assertEqual(values[4][0:2], (start.as_pointer(), end.as_pointer()))

    def test_endpoint_constraints_and_animation_are_rejected(self):
        import bpy
        from b4artists_ml import secondary_motion as secondary
        from test_b4artists_ml_secondary_motion import fixture

        obj, _, _, _, _, _ = fixture("rigify_default")
        state = obj.b4ml
        start = endpoint("B4ML Frozen Invalid Start", (-1.0, 0.0, 0.0))
        end = endpoint("B4ML Frozen Invalid End", (1.0, 0.0, 0.0))
        state.secondary_capsule_start = start
        state.secondary_capsule_end = end
        parent = endpoint("B4ML Frozen Capsule Parent", (0.0, 0.0, 0.0))
        start.parent = parent
        with self.assertRaisesRegex(ValueError, "unparented"):
            secondary._capsule_collider_values(
                state, bpy.context.scene, obj, start, end, 0.25)
        start.parent = None
        start.keyframe_insert(data_path="location", frame=1.0)
        with self.assertRaisesRegex(ValueError, "static"):
            secondary._capsule_collider_values(
                state, bpy.context.scene, obj, start, end, 0.25)


def _report(result, began, package, import_file, signature, host):
    archive_sha256 = hashlib.sha256(package.read_bytes()).hexdigest()
    with zipfile.ZipFile(package) as archive:
        members = archive.namelist()
        integrity = archive.testzip() is None
    if len(members) != 54 or not integrity:
        raise AssertionError(
            f"Unexpected archive integrity: members={len(members)} integrity={integrity}")
    report = {
        "schema": "b4ml-capsule-exact-archive-binding-v1",
        "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "archive": {
            "label": ARCHIVE_LABEL,
            "path": str(package),
            "sha256": archive_sha256,
            "members": len(members),
            "integrity": "PASS" if integrity else "FAIL",
        },
        "runtime": host,
        "import_provenance": {
            "package_selector": str(package),
            "secondary_motion_file": str(import_file),
            "capsule_signature": signature,
        },
        "result": {
            "tests": result.testsRun,
            "passed": result.testsRun - len(result.failures) - len(result.errors),
            "failed": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped),
            "was_successful": result.wasSuccessful(),
        },
        "elapsed_seconds": time.monotonic() - began,
        "claim_boundary": "Frozen static capsule binding only; current-worktree APIs, learned temporal quality, independent animator usability, and Cascadeur comparison are not covered.",
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("B4ML_EXACT_CAPSULE_BINDING:", json.dumps(report, sort_keys=True), flush=True)


def main():
    sys.path[:0] = [str(PACKAGE), str(ROOT / "tests"), str(ROOT / "training" / "b4artists_ml")]
    import b4artists_ml
    from b4artists_ml import secondary_motion as secondary
    import bpy

    if not PACKAGE.is_file() or PACKAGE.name != ARCHIVE_LABEL:
        raise RuntimeError(
            f"B4ML_PACKAGE must point to {ARCHIVE_LABEL}, got {PACKAGE!s}")
    signature = list(inspect.signature(
        secondary._capsule_collider_values).parameters)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        FrozenCapsuleBindingTests)
    began = time.monotonic()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    build_hash = getattr(bpy.app, "build_hash", None)
    if isinstance(build_hash, bytes):
        build_hash = build_hash.decode("ascii", errors="replace")
    host = {
        "application": "Bforartists",
        "version": getattr(bpy.app, "version_string", None),
        "blender_core": getattr(bpy.app, "version_string", None),
        "build_hash": build_hash,
    }
    _report(result, began, PACKAGE, Path(secondary.__file__), signature, host)
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
