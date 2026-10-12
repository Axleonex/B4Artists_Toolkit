import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from boneforge.autorig.rig_build import RigSpec, compute_build_plan
from boneforge.autorig.components import validate_plan

def check(spec, label):
    plan = compute_build_plan(spec)
    probs = validate_plan(plan)
    assert probs == [], (label, probs[:5])
    return plan

# human (regression)
h = check(RigSpec(), "human")
assert len([c for c in h.constraints if c.type == "IK"]) == 4

# quadruped: 4 legs => 4 IK, auto-tail
q = check(RigSpec(preset="quadruped"), "quadruped")
assert len([c for c in q.constraints if c.type == "IK"]) == 4, "quad IK"
assert q.bones_named("front_thigh") and q.bones_named("back_thigh"), "quad legs"
assert q.bones_named("tail."), "quad tail"

# human + tail
t = check(RigSpec(tail_segments=6), "human+tail")
assert len([b for b in t.bones if b.name.startswith("tail.")]) == 6

# human + spline chain
s = check(RigSpec(spline_chains=(("wing", 6, "chest"),)), "human+spline")
assert s.bones_named("wing."), "spline chain"
assert any(c.type == "SPLINE_IK" for c in s.constraints), "spline ik"

print("test_presets PASS  (human/quadruped/tail/spline all valid)")
