"""Headless test of geometric finger-marker placement (pure Python, no bpy).

A surface-sampled left hand (palm, four fingers, thumb sticking out toward the
front) with known knuckles and tips, a detached prop floating beside it, and
the forearm leading in. Checks: markers land within 15% of the hand length
(median) and 30% (worst), index is on the thumb side, the prop is ignored,
and a right hand mirrors correctly. Run: python tests/test_finger_markers.py
"""
import math
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from boneforge.autorig import geo_detect as g
from test_joint_trace import capsule


def hand(side=1.0, seed=5):
    rng = random.Random(seed)
    wrist, elbow = (side * 0.70, 0.0, 1.40), (side * 0.45, 0.0, 1.40)
    pts = []
    capsule(pts, elbow, wrist, 0.035, 500, rng)                                   # forearm
    capsule(pts, wrist, (side * 0.78, 0.0, 1.40), 0.04, 700, rng)                 # palm
    truth = {"PALM": (side * 0.73, 0.0, 1.40)}
    for i, (f, dy, length) in enumerate((("INDEX", -0.024, 0.085), ("MIDDLE", -0.008, 0.092),
                                         ("RING", 0.008, 0.088), ("PINKY", 0.024, 0.072))):
        base = (side * 0.779, dy, 1.40)
        tip = (base[0] + side * length, dy, 1.40)
        capsule(pts, base, tip, 0.008, 260, rng)
        truth[f + "_BASE"], truth[f + "_TIP"] = base, tip
    t_base, t_tip = (side * 0.71, -0.03, 1.40), (side * 0.76, -0.075, 1.40)
    capsule(pts, t_base, t_tip, 0.010, 250, rng)                                  # thumb -> front
    truth["THUMB_BASE"], truth["THUMB_TIP"] = t_base, t_tip
    prop = []
    capsule(prop, (side * 0.80, 0.14, 1.38), (side * 0.95, 0.14, 1.38), 0.03, 400, rng)
    return pts + prop, wrist, elbow, truth


for side, tag in ((1.0, "L"), (-1.0, "R")):
    pts, wrist, elbow, truth = hand(side)
    got = g.finger_markers(pts, wrist, elbow, tag)
    assert got, "no hand found"
    hand_len = 0.17
    errs = {k: math.dist(got["FINGER_%s_%s" % (k, tag)], v) / hand_len * 100 for k, v in truth.items()}
    vals = sorted(errs.values())
    assert vals[len(vals) // 2] <= 15.0, ("median", tag, errs)
    assert vals[-1] <= 30.0, ("worst", tag, sorted(errs.items(), key=lambda kv: -kv[1])[:3])
    # index on the thumb (front, -Y) side, pinky on the back
    assert got["FINGER_INDEX_TIP_" + tag][1] < got["FINGER_PINKY_TIP_" + tag][1], tag
    # the floating prop beside the hand (y = 0.14) was not taken as a finger
    assert all(p[1] < 0.1 for p in got.values()), ("prop picked up", tag)
    print("  %s hand: median %.1f%%, worst %.1f%% of hand length"
          % (tag, vals[len(vals) // 2], vals[-1]))

assert g.finger_markers([(0, 0, 0)] * 5, (0, 0, 0), None, "L") == {}, "empty hand must yield {}"
print("test_finger_markers PASS")
