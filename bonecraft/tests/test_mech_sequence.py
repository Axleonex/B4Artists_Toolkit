"""Pure test: Sequence steps, deltas and easing. Run: python tests/test_mech_sequence.py"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from boneforge.mechanisms import model as M, planner as P
from boneforge.mechanisms.recipes import sequence as S


def raises(fn, text):
    try:
        fn()
    except P.PlanError as exc:
        assert text in str(exc), (text, str(exc))
        return
    raise AssertionError("no PlanError: " + text)


assert S.eased(0.5, "LINEAR") == 0.5 and S.eased(-1, "LINEAR") == 0.0 and S.eased(2, "LINEAR") == 1.0
assert abs(S.eased(0.5, "EASE_IN_OUT") - 0.5) < 1e-12
assert abs(S.eased(0.5, "EASE_IN") - (1 - math.cos(math.pi / 4))) < 1e-12
assert abs(S.eased(0.5, "EASE_OUT") - math.sin(math.pi / 4)) < 1e-12
assert S.eased(0.99, "SNAP") == 0.0 and S.eased(1.0, "SNAP") == 1.0
assert S.ease_keys(2.0, "EASE_IN")[0] == (0.0, 0.0, "SINE", "EASE_IN")
for _e in ("EASE_IN", "EASE_OUT", "EASE_IN_OUT"):
    assert S.ease_keys(2.0, _e) == [(0.0, 0.0, "SINE", _e), (10.0, 2.0, "LINEAR", "")], _e
assert S.ease_keys(2.0, "SNAP") == [(0.0, 0.0, "CONSTANT", ""), (10.0, 2.0, "CONSTANT", "")]
assert S.ease_keys(2.0, "LINEAR") == [(0.0, 0.0, "LINEAR", ""), (10.0, 2.0, "LINEAR", "")]


def rig(steps):
    parts = [M.Part("blade", "Blade"), M.Part("mast", "Mast Base"), M.Part("seg", "Seg", parent="mast")]
    ms = [M.Mechanism("h1", "HINGE", "Blade Hinge", parts=["blade"], min=-180, max=180),
          M.Mechanism("t1", "TELESCOPE", "Mast", parts=["mast", "seg"], axis=(0, 0, 1), length=1.0)]
    return M.MechRig(parts=parts, mechanisms=ms, sequences=[M.Sequence("q1", "Unfold", steps=steps)])


steps = [M.Step("h1", 90.0, 0.0, 0.5, "EASE_IN_OUT"), M.Step("h1", 30.0, 0.5, 1.0, "LINEAR"), M.Step("t1", 0.8, 0.2, 0.6, "SNAP")]
r = rig(steps)
assert [(i, round(d, 9)) for i, _, d in S.deltas(r.sequences[0])] == [(0, 90.0), (1, -60.0), (2, 0.8)]
plan = P.plan_rig(r)
assert plan.names["q1:CTRL"] == "CTRL-SEQ-Unfold" and plan.bone("q1:CTRL").parent == "root"
assert plan.pose["q1:CTRL"].lock_location == (True, False, True) and not plan.pose["q1:CTRL"].hide
hl = plan.constraints_on("q1:CTRL")[0]
assert hl.type == "LIMIT_LOCATION" and (hl.params["min_y"], hl.params["max_y"]) == (0.0, 1.0)
on_blade = [c for c in plan.constraints_on("blade:MCH") if c.tag == "q1"]
assert [c.name for c in on_blade] == ["BC·q1·s0", "BC·q1·s1"]
s0 = on_blade[0]
assert (s0.type, s0.subtarget, s0.params["transform_channel"], s0.params["mix_mode"]) == ("ACTION", "q1:CTRL", "LOCATION_Y", "AFTER_SPLIT")
assert (s0.params["min"], s0.params["max"], s0.params["action"].key) == (0.0, 0.5, "q1:s0")
assert [c.name for c in plan.constraints_on("blade:MCH")][-1] == "BC·h1·limit", "the joint limit stays last"
on_handle = [c for c in plan.constraints_on("t1:CTRL") if c.tag == "q1"]
assert [c.name for c in on_handle] == ["BC·q1·s2"], "a Telescope step drives its handle"
acts = {a.key: a for a in plan.actions}
assert (acts["q1:s0"].channel, acts["q1:s0"].index) == ("rotation_euler", 0)
assert abs(acts["q1:s1"].keys[1][1] - math.radians(-60)) < 1e-12
assert (acts["q1:s2"].channel, acts["q1:s2"].index, acts["q1:s2"].keys[1][1]) == ("location", 1, 0.8)

want = 90 * (1 - math.cos(math.pi * 0.8)) / 2                      # slider 0.4 -> 0.8 through step 0
assert abs(S.value(r, r.sequences[0], "h1", 0.4) - want) < 1e-9
assert abs(S.value(r, r.sequences[0], "h1", 1.0) - 30.0) < 1e-9
assert S.value(r, r.sequences[0], "t1", 0.59) == 0.0 and S.value(r, r.sequences[0], "t1", 0.6) == 0.8

raises(lambda: P.plan_rig(rig([M.Step("h1", 10.0, 0.6, 0.4)])), "must start before it ends")
raises(lambda: P.plan_rig(rig([M.Step("nope", 10.0)])), "has no joint")
r = rig([M.Step("h1", 10.0)])
r.missing = {"blade"}
mp = P.plan_rig(r)
assert ("q1:s0", "Part 'Blade' is missing") in mp.skipped and mp.bone("q1:CTRL") is not None
print("PASS mechanisms sequence: deltas, easing, slices, telescope steps, skips")
