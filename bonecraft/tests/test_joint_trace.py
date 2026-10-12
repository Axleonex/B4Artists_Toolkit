"""Headless test of limb-traced joint detection (P2) on surface-sampled figures.

Pure Python — no bpy. Builds hollow (surface-only, like real mesh vertices)
humanoids from capsules around known joints, in a T-pose and an A-pose, one
of them carrying a one-sided accessory, and checks the traced joints stay
within a regression margin (median <=4%, every marker <=7% of height; the
parity-plan 3%/6% gates are enforced on real models by bench_real_model.py —
synthetic "truth" here is one arbitrary joint convention),
arm joints are ordered along the arm, toes point to the face-forward side,
and the accessory is not taken for an arm. Run: python tests/test_joint_trace.py
"""
import math
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from boneforge.autorig import geo_detect as g


def capsule(pts, a, b, r, n, rng):
    ax = [b[i] - a[i] for i in range(3)]
    length = math.sqrt(sum(v * v for v in ax)) or 1e-9
    u = [v / length for v in ax]
    helper = (0, 0, 1) if abs(u[2]) < 0.9 else (1, 0, 0)
    v1 = [u[1] * helper[2] - u[2] * helper[1], u[2] * helper[0] - u[0] * helper[2],
          u[0] * helper[1] - u[1] * helper[0]]
    n1 = math.sqrt(sum(x * x for x in v1))
    v1 = [x / n1 for x in v1]
    v2 = [u[1] * v1[2] - u[2] * v1[1], u[2] * v1[0] - u[0] * v1[2], u[0] * v1[1] - u[1] * v1[0]]
    for _ in range(n):
        t = rng.random()
        ang = rng.random() * 2 * math.pi
        pts.append(tuple(a[i] + ax[i] * t + r * (math.cos(ang) * v1[i] + math.sin(ang) * v2[i])
                         for i in range(3)))


def figure(arm_drop_deg, accessory=False, seed=3):
    """Surface humanoid, 1.8 m, facing -Y. Returns (points, truth)."""
    rng = random.Random(seed)
    d = math.radians(arm_drop_deg)
    t = {"PELVIS": (0, 0, 0.98), "NECK_BASE": (0, 0, 1.47), "HEAD_TOP": (0, 0, 1.80)}
    for s, sx in (("LEFT", 1), ("RIGHT", -1)):
        sh = (sx * 0.17, 0, 1.43)
        el = (sh[0] + sx * 0.28 * math.cos(d), 0, sh[2] - 0.28 * math.sin(d))
        wr = (el[0] + sx * 0.25 * math.cos(d), 0, el[2] - 0.25 * math.sin(d))
        t.update({"SHOULDER_" + s: sh, "ELBOW_" + s: el, "WRIST_" + s: wr,
                  "HIP_" + s: (sx * 0.10, 0, 0.94), "KNEE_" + s: (sx * 0.10, 0, 0.52),
                  "ANKLE_" + s: (sx * 0.10, 0, 0.12), "TOE_" + s: (sx * 0.10, -0.12, 0.04)})
    pts = []
    capsule(pts, (0, 0, 0.90), (0, 0, 1.45), 0.15, 2600, rng)            # torso
    capsule(pts, (0, 0, 1.45), (0, 0, 1.55), 0.05, 200, rng)             # neck
    capsule(pts, (0, 0, 1.58), (0, 0, 1.78), 0.10, 700, rng)             # head
    for _ in range(80):                                                  # skull cap
        a, b = rng.random() * 2 * math.pi, rng.random() * 0.5 * math.pi
        pts.append((0.10 * math.cos(a) * math.cos(b), 0.10 * math.sin(a) * math.cos(b),
                    1.72 + 0.08 * math.sin(b)))
    for s, sx in (("LEFT", 1), ("RIGHT", -1)):
        sh, el, wr = t["SHOULDER_" + s], t["ELBOW_" + s], t["WRIST_" + s]
        tip = (wr[0] + sx * 0.17 * math.cos(d), 0, wr[2] - 0.17 * math.sin(d))
        capsule(pts, (sx * 0.08, 0, 1.43), el, 0.05, 450, rng)
        capsule(pts, el, wr, 0.04, 380, rng)
        capsule(pts, wr, tip, 0.045, 260, rng)
        capsule(pts, (sx * 0.10, 0, 0.95), t["KNEE_" + s], 0.07, 650, rng)
        capsule(pts, t["KNEE_" + s], t["ANKLE_" + s], 0.05, 520, rng)
        capsule(pts, (sx * 0.10, 0.04, 0.05), (sx * 0.10, -0.16, 0.03), 0.045, 260, rng)
    if accessory:          # a one-sided "robot arm" sticking far out at shoulder height
        capsule(pts, (0.15, 0.20, 1.45), (1.30, 0.30, 1.50), 0.06, 900, rng)
    return pts, t


def check(label, pts, truth):
    geo = g.guess_landmarks(g.preprocess_points(pts))
    props = g.body_marker_proposals(geo)
    h = 1.80
    errs = {k: math.dist(props[k]["pos"], v) / h * 100 for k, v in truth.items()}
    vals = sorted(errs.values())
    med, worst = vals[len(vals) // 2], vals[-1]
    assert len(geo.get("joints") or {}) == 19, (label, "joint trace did not run")
    assert med <= 4.0, (label, "median", med, errs)
    assert worst <= 7.0, (label, "max", worst, sorted(errs.items(), key=lambda kv: -kv[1])[:4])
    for s, sx in (("LEFT", 1), ("RIGHT", -1)):
        order = [props[k]["pos"][0] * sx for k in ("SHOULDER_" + s, "ELBOW_" + s, "WRIST_" + s)]
        assert order[0] < order[1] < order[2], (label, "arm joints out of order", s, order)
        assert props["TOE_" + s]["pos"][1] < props["ANKLE_" + s]["pos"][1], \
            (label, "toe must be in front (-Y) of the ankle", s)
    assert all(p["confidence"] < 0.85 for p in props.values()), "never auto-confirm"
    return med, worst


results = []
for label, drop, acc in (("T-pose", 0, False), ("A-pose", 40, False),
                         ("T-pose + one-sided accessory", 0, True)):
    pts, truth = figure(drop, acc)
    results.append((label,) + check(label, pts, truth))

# arms hanging down (walk / I-pose) are outside what the trace reads: it must
# say so (low confidence -> the wizard's ADJUST band), not guess confidently
pts, _truth = figure(88)
props = g.body_marker_proposals(g.guess_landmarks(g.preprocess_points(pts)))
for k in ("WRIST_LEFT", "WRIST_RIGHT", "ELBOW_LEFT", "SHOULDER_RIGHT"):
    assert g.confidence_category(props[k]["confidence"]) == "ADJUST",         ("arms-down pose not flagged", k, props[k]["confidence"])

print("test_joint_trace PASS  (" + ", ".join(
    "%s median %.1f%% max %.1f%%" % r for r in results) + "; arms-down pose flagged ADJUST)")
