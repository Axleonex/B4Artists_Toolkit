"""Headless unit test of fitting the control-rig engine onto a wizard skeleton.

Pure Python — no bpy. Proves the fit is exact under a similarity transform,
follows a real (non-template) pose such as an A-pose, keeps poles on the
correct side, maps every limb deform segment 1:1, and splits spine weight
between the two bracketing bones. Run: python tests/test_rig_integrate.py
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from boneforge.autorig.rig_build import RigSpec, compute_build_plan
from boneforge.autorig import rig_integrate as ri


def close(a, b, tol=1e-6):
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def similarity(p, s=0.62, d=(0.3, -0.1, 0.05)):
    return (p[0] * s + d[0], p[1] * s + d[1], p[2] * s + d[2])


# 1) identity targets reproduce the template exactly
tmpl = ri.template_segments()
plan = compute_build_plan(RigSpec(fingers=False))
orig = {bd.name: (bd.head, bd.tail) for bd in plan.bones}
ri.fit_plan(plan, dict(tmpl))
for bd in plan.bones:
    assert close(bd.head, orig[bd.name][0]) and close(bd.tail, orig[bd.name][1]), bd.name

# 2) a scaled + moved character: every bone lands on the transformed template
plan = compute_build_plan(RigSpec(fingers=False))
targets = {k: (similarity(h), similarity(t)) for k, (h, t) in tmpl.items()}
ri.fit_plan(plan, targets)
for bd in plan.bones:
    want_h, want_t = similarity(orig[bd.name][0]), similarity(orig[bd.name][1])
    assert close(bd.head, want_h, 1e-6) and close(bd.tail, want_t, 1e-6), \
        (bd.name, bd.head, want_h)

# 3) A-pose arms (45 deg down): hand deform bone follows the wrist, pole
# stays behind the elbow (+Y), controls stay on the limb.
def a_pose(p):
    x, y, z = p
    if abs(x) <= 0.16 or z < 1.3:
        return p
    sx = 1.0 if x > 0 else -1.0
    r = abs(x) - 0.16
    return (sx * (0.16 + r * math.cos(math.radians(45))), y,
            1.45 - r * math.sin(math.radians(45)))


targets = {k: (a_pose(h), a_pose(t)) for k, (h, t) in tmpl.items()}
plan = compute_build_plan(RigSpec(fingers=False))
ri.fit_plan(plan, targets)
bones = {bd.name: bd for bd in plan.bones}
assert close(bones["hand.def-L"].head, targets["hand-L"][0]), bones["hand.def-L"].head
assert close(bones["forearm.fk-R"].tail, targets["forearm-R"][1])
assert bones["arm.pole-L"].head[1] > 0.2, ("arm pole must stay behind", bones["arm.pole-L"].head)
assert bones["leg.pole-L"].head[1] < -0.2, ("leg pole must stay in front", bones["leg.pole-L"].head)

# 4) wizard skeleton -> targets: limbs 1:1, spine split, clavicle derived
wiz = {
    "spine": ((0, 0, 0.9), (0, 0, 1.1)), "spine.001": ((0, 0, 1.1), (0, 0, 1.25)),
    "spine.002": ((0, 0, 1.25), (0, 0, 1.4)), "neck": ((0, 0, 1.4), (0, 0, 1.5)),
    "head": ((0, 0, 1.5), (0, 0, 1.7)),
}
for s, sx in (("L", 1), ("R", -1)):
    wiz.update({
        "upper_arm.%s" % s: ((sx * 0.18, 0, 1.38), (sx * 0.42, 0, 1.38)),
        "forearm.%s" % s: ((sx * 0.42, 0, 1.38), (sx * 0.64, 0, 1.38)),
        "hand.%s" % s: ((sx * 0.64, 0, 1.38), (sx * 0.74, 0, 1.38)),
        "thigh.%s" % s: ((sx * 0.1, 0, 0.9), (sx * 0.1, 0, 0.5)),
        "shin.%s" % s: ((sx * 0.1, 0, 0.5), (sx * 0.1, 0, 0.1)),
        "foot.%s" % s: ((sx * 0.1, 0, 0.1), (sx * 0.1, -0.12, 0.02)),
        "toe.%s" % s: ((sx * 0.1, -0.12, 0.02), (sx * 0.1, -0.2, 0.02)),
    })
assert ri.is_wizard_skeleton(wiz)
assert not ri.is_wizard_skeleton(list(wiz) + ["upperarm.def-L"])
t = ri.wizard_joint_targets(wiz)
assert t["forearm-L"] == wiz["forearm.L"] and t["thigh-R"] == wiz["thigh.R"]
assert close(t["hips"][0], (0, 0, 0.9)) and close(t["chest"][1], (0, 0, 1.4))
assert t["clavicle-L"][1] == wiz["upper_arm.L"][0]
m = ri.weight_transfer_map(wiz)
for s in ("L", "R"):
    for wz, en in (("upper_arm", "upperarm.def"), ("forearm", "forearm.def"),
                   ("hand", "hand.def"), ("thigh", "thigh.def"),
                   ("shin", "shin.def"), ("foot", "foot.def")):
        assert m["%s.%s" % (wz, s)] == "%s-%s" % (en, s), (wz, s)
assert "toe.L" not in m, "toe has no engine deform bone; it is kept, not merged"
assert m["neck"] == "neck" and m["head"] == "head"

# 5) spine weight split conserves weight and brackets correctly
centers = [0.05, 0.2, 0.35, 0.5]
for param in (-1.0, 0.05, 0.12, 0.35, 0.44, 0.9):
    split = ri.spine_split(param, centers)
    assert abs(sum(split.values()) - 1.0) < 1e-9, split
    assert len(split) <= 2, split

# 6) fitted foot follows the wizard's toe direction (-Y), heel lands behind
plan = compute_build_plan(RigSpec(fingers=False))
ri.fit_plan(plan, t)
bones = {bd.name: bd for bd in plan.bones}
assert bones["foot.def-L"].tail[1] < bones["foot.def-L"].head[1], "foot must point to -Y toes"
assert bones["roll_heel-L"].head[1] > bones["foot.def-L"].head[1] - 1e-6, \
    ("heel behind the ankle", bones["roll_heel-L"].head)

print("test_rig_integrate PASS  (similarity-exact fit, A-pose, poles, "
      "1:1 weight map, spine split, foot direction)")
