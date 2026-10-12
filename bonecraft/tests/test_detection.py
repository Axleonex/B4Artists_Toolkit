"""In-Bforartists behavioural test for R1 smart detection.

Verifies the detection pipeline on a real mesh (vertex sampling with
modifiers, two-tier detect with geometry fallback) and the wizard
operator/session path (proposals written confidence-tagged and never
auto-confirmed; accept-high / reset-low / mirror).
"""
import random

import bpy

import boneforge
from boneforge.autorig import inference
from boneforge.autorig.geo_detect import confidence_category
from boneforge.autorig.constants import REQUIRED_BODY_MARKERS, BODY_MARKERS


def _humanoid_mesh(name="BF_DET_MESH", loc=(0.0, 0.0, 0.0)):
    """A T-pose-ish point cloud baked as mesh vertices (X=left/right, Z=up)."""
    random.seed(7)
    pts = []

    def box(cx, cy, cz, sx, sy, sz, n=120):
        for _ in range(n):
            pts.append((cx + random.uniform(-sx, sx),
                        cy + random.uniform(-sy, sy),
                        cz + random.uniform(-sz, sz)))
    box(0, 0, 1.5, 0.12, 0.10, 0.12)       # head
    box(0, 0, 1.1, 0.18, 0.10, 0.30)       # torso
    box(0.55, 0, 1.45, 0.35, 0.06, 0.06)   # left arm (+X)
    box(-0.55, 0, 1.45, 0.35, 0.06, 0.06)  # right arm (-X)
    box(0.12, 0, 0.45, 0.07, 0.07, 0.45)   # left leg
    box(-0.12, 0, 0.45, 0.07, 0.07, 0.45)  # right leg

    mesh = bpy.data.meshes.new(name)
    # a single degenerate face keeps Blender happy as a MESH object
    mesh.from_pydata(pts, [], [list(range(min(3, len(pts))))])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    bpy.context.scene.collection.objects.link(obj)
    return obj


def test_pipeline():
    obj = _humanoid_mesh(loc=(5.0, 0.0, 0.0))   # offset to check world-space
    pts = inference.sample_point_cloud(obj)
    assert pts, "no points sampled"
    # world space: the offset must show up in the samples
    assert max(p[0] for p in pts) > 4.0, "sampling not in world space"

    # missing/garbage model path must fall back to geometry, not error
    result = inference.detect_landmarks(pts, model_path="/no/such/model.onnx")
    assert result.success and result.message == "geometry", result.message
    for name in REQUIRED_BODY_MARKERS:
        assert name in result.proposals, ("missing required proposal", name)
    for name, (pos, conf) in result.proposals.items():
        assert name in BODY_MARKERS and 0.0 <= conf <= 1.0
    # nothing reaches the auto-confirm band
    assert all(confidence_category(c) != 'CONFIRMED'
               for _, (_, c) in result.proposals.items())
    print("detection pipeline verified (%d proposals, world-space, geometry "
          "fallback, none auto-confirm)" % len(result.proposals))
    bpy.data.objects.remove(obj, do_unlink=True)


def test_operator_and_session():
    # register the add-on so the wizard session PropertyGroup exists
    try:
        boneforge.register()
    except Exception as exc:
        raise AssertionError("add-on failed to register in Bforartists: %s" % exc)

    try:
        obj = _humanoid_mesh()
        bpy.context.view_layer.objects.active = obj
        scene = bpy.context.scene
        bpy.ops.boneforge.autorig_wizard_start()
        session = scene.boneforge_autorig_session
        session.mesh_object_name = obj.name

        assert inference.BF_OT_RunDetection.poll(bpy.context), "detection poll False"
        bpy.ops.boneforge.autorig_run_detection()

        placed = [session.body_markers[i] for i in range(len(BODY_MARKERS))
                  if session.body_markers[i].confidence > 0.0]
        assert placed, "no markers written"
        assert all(not m.confirmed for m in placed), \
            "detection auto-confirmed markers (must not)"
        high = [m for m in placed if m.confidence >= inference.ACCEPT_THRESHOLD]
        assert high, "no high-confidence markers to accept"

        bpy.ops.boneforge.autorig_accept_high()
        accepted = [session.body_markers[i] for i in range(len(BODY_MARKERS))
                    if session.body_markers[i].confirmed]
        assert len(accepted) == len(high), ("accept-high mismatch",
                                            len(accepted), len(high))

        bpy.ops.boneforge.autorig_reset_low()
        lows = [session.body_markers[i] for i in range(len(BODY_MARKERS))
                if 0.0 < session.body_markers[i].confidence
                < inference.ACCEPT_THRESHOLD]
        assert not lows, "reset-low left low-confidence markers"

        bpy.ops.boneforge.autorig_mirror_confirmed(from_side='LEFT')
        print("detection operator/session verified (run -> %d markers, "
              "accept-high -> %d confirmed, reset-low, mirror)"
              % (len(placed), len(accepted)))
        bpy.ops.boneforge.autorig_wizard_cancel()
        bpy.data.objects.remove(obj, do_unlink=True)
    finally:
        try:
            boneforge.unregister()
        except Exception:
            pass


def run():
    test_pipeline()
    test_operator_and_session()
    print("ALL DETECTION TESTS PASS")
