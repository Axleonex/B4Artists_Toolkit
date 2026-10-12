"""Headless unit test for the pure retargeting core (no bpy)."""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from boneforge.autorig import retarget_core as rc
from boneforge.autorig import maps


def test_namespace():
    assert rc.strip_namespace("mixamorig:Hips") == "Hips"
    assert rc.strip_namespace("Armature|LeftArm") == "LeftArm"
    assert rc.strip_namespace("Hips") == "Hips"


def test_build_mappings():
    # use a real preset; source armature uses a namespace prefix
    preset = maps.load_map(maps.available_maps()[0])
    target_names = maps.TARGET_BONES
    # source names = the preset's source bones, prefixed with a namespace,
    # but drop one so we can see a missing-source diagnostic
    src_bones = list(preset["bones"])
    source_names = ["mocap:" + s for s in src_bones[1:]]   # omit the first
    res = rc.build_mappings(preset, source_names, target_names)
    matched = [m for m in res["mappings"] if m["matched"]]
    assert matched, "no bones matched through the namespace"
    # the omitted source bone is reported missing, not silently dropped
    assert src_bones[0] in res["missing_source"], res["missing_source"]
    # matched name map points namespace-resolved source -> engine target
    name_map = rc.matched_name_map(res)
    assert all(t in maps.TARGET_BONES for t in name_map.values())


def test_tweak():
    tw = rc.BoneTweak(loc_offset=(0.1, 0, 0), rot_offset=(0, 0, 0.2),
                      rot_multiplier=0.5)
    loc, rot = rc.apply_tweak((1, 2, 3), (0.4, 0, 0), tw)
    assert abs(loc[0] - 1.1) < 1e-9
    assert abs(rot[0] - 0.2) < 1e-9          # 0.4 * 0.5
    assert abs(rot[2] - 0.2) < 1e-9          # 0 * 0.5 + 0.2
    assert rc.reset_tweak().is_identity()


def test_retarget_quat():
    def axis_angle(axis, ang):
        s = math.sin(ang / 2)
        return rc.q_norm((math.cos(ang / 2), axis[0] * s, axis[1] * s,
                          axis[2] * s))
    src = axis_angle((1, 0, 0), math.radians(40))
    # identity delta -> unchanged
    out = rc.retarget_quat((1, 0, 0, 0), src)
    assert all(abs(out[i] - src[i]) < 1e-6 for i in range(4)), out
    # conjugation preserves the rotation angle (motion magnitude)
    delta = axis_angle((0, 0, 1), math.radians(90))
    out2 = rc.retarget_quat(delta, src)
    assert abs(out2[0] - src[0]) < 1e-6, ("angle changed", out2[0], src[0])


if __name__ == "__main__":
    test_namespace()
    test_build_mappings()
    test_tweak()
    test_retarget_quat()
    print("test_retarget_core PASS  (namespace, map diagnostics, tweaks, "
          "rotation conjugation)")
