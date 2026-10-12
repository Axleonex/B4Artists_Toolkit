"""Pure test: Mechanisms validator checks from the records. Run: python tests/test_mech_checks.py"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from boneforge.mechanisms import checks, model as M, planner


def rig(src_max=720, seq=True):
    ms = [M.Mechanism("ha", "HINGE", "Crank", parts=["a"], min=-src_max, max=src_max),
          M.Mechanism("hb", "HINGE", "Wheel", parts=["b"], min=-720, max=720),
          M.Mechanism("g1", "GEAR", "Crank Gear", source="ha", target="hb")]
    seqs = [M.Sequence("q1", "Spin Up", steps=[M.Step("ha", 90.0)])] if seq else []
    return M.MechRig(parts=[M.Part("a", "A"), M.Part("b", "B")], mechanisms=ms, sequences=seqs)


assert checks.record_checks(rig(seq=False)) == []
warn = checks.record_checks(rig())
assert [w[0] for w in warn] == ["warn"] and "Crank" in warn[0][1] and "not passed on" in warn[0][1], warn
assert checks.record_checks(rig(src_max=90)) == [], "a limited gear reads the whole source: no warning"
missing = rig(seq=False)
missing.missing = {"b"}
assert ("fail", "Part 'B' is missing: Reassign it or delete it.", "B") in checks.record_checks(missing)
loop = rig(seq=False)
loop.mechanisms.append(M.Mechanism("g2", "GEAR", "Back Gear", source="hb", target="ha"))
out = checks.record_checks(loop)
assert out[0][0] == "fail" and out[0][1].endswith("would loop."), out
assert planner.find_loop(loop) == out[0][1]
print("PASS mechanisms checks: loops, missing parts, free-gear warnings")
