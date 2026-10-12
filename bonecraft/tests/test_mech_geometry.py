"""Pure test: tagged plan checks and mechanism bone frames. Run: python tests/test_mech_geometry.py"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from boneforge.autorig.components import BuildPlan, validate_plan
from boneforge.mechanisms import geometry as G


def close(a, b, eps=1e-9):
    return all(abs(x - y) < eps for x, y in zip(a, b))


# -- tags
p = BuildPlan()
p.add_bone("a:MCH", (0, 0, 0), (0, 1, 0), tag="a")
p.add_constraint("a:MCH", "COPY_TRANSFORMS", "BC·m1·copy", tag="m1")
assert validate_plan(p) == [], validate_plan(p)
p.add_constraint("a:MCH", "LIMIT_ROTATION", "limit", tag="m1")                  # tag missing from the name
p.add_constraint("a:MCH", "LIMIT_ROTATION", "BC·m1·" + "x" * 60, tag="m1")      # too long
p.add_constraint("a:MCH", "COPY_TRANSFORMS", "BC·m1·copy", tag="m1")           # duplicate
probs = validate_plan(p)
assert any("tag missing" in x for x in probs), probs
assert any("too long" in x for x in probs), probs
assert any("duplicate constraint" in x for x in probs), probs
q = BuildPlan()
q.add_bone("b", (0, 0, 0), (0, 1, 0))
q.add_constraint("b", "IK", "same")
q.add_constraint("b", "IK", "same")                                               # untagged plans are unchanged
assert validate_plan(q) == [], validate_plan(q)

# -- frames
for axis in ((1, 0, 0), (0, 1, 0), (0, 0, 1), (0.3, 0.4, 0.866), (-1, 0, 0)):
    a = G.normalize(axis)
    y, z = G.frame_for_hinge(axis)
    assert abs(G.length(y) - 1) < 1e-9 and abs(G.length(z) - 1) < 1e-9
    assert abs(G.dot(y, z)) < 1e-9
    assert close(G.cross(y, z), a), ("hinge: bone X must be the axis", axis)
    y, z = G.frame_for_slide(axis)
    assert close(y, a) and abs(G.dot(y, z)) < 1e-9 and abs(G.length(z) - 1) < 1e-9, ("slide: bone Y must be the axis", axis)
y, z = G.frame_toward((0, 0, 0), (0, 0, 2))
assert close(y, (0, 0, 1))
assert close(G.tail((1, 1, 1), (0, 0, 1), 0.5), (1, 1, 1.5))
for bad in ((0, 0, 0), (1e-12, 0, 0)):
    try:
        G.frame_for_hinge(bad)
        raise AssertionError(bad)
    except G.GeometryError:
        pass
print("PASS mechanisms geometry: tag checks, hinge/slide/aim frames")
