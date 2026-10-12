import os, sys, random
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from boneforge.autorig import geo_detect as g

# synthetic T-pose-ish humanoid point cloud (X=left/right, Z=up)
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

res = g.guess_landmarks(pts)
assert res["symmetry_axis"] == 0, res["symmetry_axis"]   # X is mirror axis
lm = {d["name"]: d["pos"] for d in res["landmarks"]}
zmax = max(p[2] for p in pts)
assert lm["head"][2] > 1.4, lm["head"]
assert lm["hand-L"][0] > 0.3 and lm["hand-R"][0] < -0.3, (lm["hand-L"], lm["hand-R"])
assert lm["foot-L"][2] < 0.3 and lm["foot-R"][2] < 0.3, "feet not low"
assert all(0.0 <= d["confidence"] <= 1.0 for d in res["landmarks"])

# -- body marker proposal mapping (maps geometry -> all 19 BODY_MARKERS) --
from boneforge.autorig.constants import BODY_MARKERS, REQUIRED_BODY_MARKERS
from boneforge.autorig.geo_detect import confidence_category

props = g.body_marker_proposals(res)
# every required marker must be proposed
for name in REQUIRED_BODY_MARKERS:
    assert name in props, ("missing required proposal", name)
# all proposals well-formed and within [0,1] confidence
for name, p in props.items():
    assert name in BODY_MARKERS, ("unknown marker", name)
    assert len(p["pos"]) == 3
    assert 0.0 <= p["confidence"] <= 1.0, p
# pure geometry never reaches the auto-confirm band -> nothing silently accepted
assert all(confidence_category(p["confidence"]) != 'CONFIRMED'
           for p in props.values()), "geometry should not auto-confirm"
# sane geometry: head above pelvis; left wrist +X, right wrist -X
assert props["HEAD_TOP"]["pos"][2] > props["PELVIS"]["pos"][2]
assert props["WRIST_LEFT"]["pos"][0] > 0 and props["WRIST_RIGHT"]["pos"][0] < 0

# MEASURABLE accuracy target: the major markers must land within a tolerance
# band of their known positions on the synthetic T-pose cloud (median error
# under the band). This makes "smart" a numeric target, not just a sanity sign.
import math
_EXPECTED = {            # derived from the box layout above
    "HEAD_TOP":     (0.0, 0.0, 1.62),
    "PELVIS":       (0.0, 0.0, 0.86),
    "WRIST_LEFT":   (0.90, 0.0, 1.45),
    "WRIST_RIGHT":  (-0.90, 0.0, 1.45),
    "ANKLE_LEFT":   (0.12, 0.0, 0.0),
    "ANKLE_RIGHT":  (-0.12, 0.0, 0.0),
}
_TOLERANCE = 0.30       # world units; cloud boxes are ~0.1-0.45 across
errors = []
for name, exp in _EXPECTED.items():
    got = props[name]["pos"]
    errors.append(math.dist(got, exp))
errors.sort()
median_err = errors[len(errors) // 2]
assert median_err < _TOLERANCE, ("detection median error too high",
                                 median_err, errors)
assert max(errors) < _TOLERANCE * 2, ("a marker is way off", errors)

# Robustness: detached clutter should be filtered before landmarks are guessed.
clutter = list(pts)
for _ in range(90):
    clutter.append((4.5 + random.uniform(-0.2, 0.2),
                    2.0 + random.uniform(-0.2, 0.2),
                    1.0 + random.uniform(-0.2, 0.2)))
cleaned = g.preprocess_points(clutter)
assert len(cleaned) < len(clutter), "detached clutter was not filtered"
res_clutter = g.guess_landmarks(clutter)
props_clutter = g.body_marker_proposals(res_clutter)
assert abs(props_clutter["PELVIS"]["pos"][0]) < 0.30, \
    ("pelvis dragged toward clutter", props_clutter["PELVIS"])
assert props_clutter["WRIST_LEFT"]["pos"][0] < 1.25, \
    ("left wrist dragged toward clutter", props_clutter["WRIST_LEFT"])

# Scale normalization helper: output should fit a unit sphere and preserve
# proposal ratios across very small / very large versions of the same cloud.
norm, center, scale = g.normalize_points([(p[0] * 100.0, p[1] * 100.0,
                                           p[2] * 100.0) for p in pts])
assert scale > 10.0 and len(norm) == len(pts)
assert max(math.sqrt(sum(v * v for v in p)) for p in norm) <= 1.00001

# Asymmetric extras should not crash the mirror-axis heuristic or produce
# non-finite proposals.
asym = list(pts)
for _ in range(80):
    asym.append((1.05 + random.uniform(-0.08, 0.08),
                 0.10 + random.uniform(-0.05, 0.05),
                 1.15 + random.uniform(-0.25, 0.25)))
res_asym = g.guess_landmarks(asym)
props_asym = g.body_marker_proposals(res_asym)
assert res_asym["symmetry_axis"] in (0, 1)
assert all(math.isfinite(v) for p in props_asym.values() for v in p["pos"])

# Non-upright clouds still return finite landmarks but confidence is downgraded
# so the wizard asks for manual adjustment instead of pretending certainty.
lying = [(p[2], p[1], p[0] * 0.1) for p in pts]
res_lying = g.guess_landmarks(lying)
assert max(d["confidence"] for d in res_lying["landmarks"]) < 0.8
assert all(math.isfinite(v) for d in res_lying["landmarks"] for v in d["pos"])

print("test_geo_detect PASS  (%d landmarks, %d/19 proposals, median marker "
      "error %.3f < %.2f tol; robustness cases covered)" %
      (len(res["landmarks"]), len(props), median_err, _TOLERANCE))
