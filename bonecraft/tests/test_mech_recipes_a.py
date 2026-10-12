"""Pure test: Telescope and Piston recipes. Run: python tests/test_mech_recipes_a.py"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from boneforge.mechanisms import geometry as G, model as M, planner as P
from boneforge.mechanisms.recipes import telescope


def raises(fn, text):
    try:
        fn()
    except P.PlanError as exc:
        assert text in str(exc), (text, str(exc))
        return
    raise AssertionError("no PlanError: " + text)


def scope(shares=(), parents=("base", "s1"), length=0.9):
    parts = [M.Part("base", "Base"), M.Part("s1", "Seg 1", parent=parents[0]), M.Part("s2", "Seg 2", parent=parents[1])]
    t = M.Mechanism("t1", "TELESCOPE", "Mast", parts=["base", "s1", "s2"], axis=(0, 0, 1), length=length, shares=list(shares))
    return M.MechRig(parts=parts, mechanisms=[t])


plan = P.plan_rig(scope())
assert telescope.shares(scope().mechanisms[0]) == [0.45, 0.45]
assert plan.names["t1:CTRL"] == "CTRL-Mast" and plan.bone("t1:CTRL").parent == "base:DEF"
assert plan.pose["t1:CTRL"].lock_location == (True, False, True)
hl = plan.constraints_on("t1:CTRL")[0]
assert hl.type == "LIMIT_LOCATION" and hl.params["max_y"] == 0.9 and hl.params["use_transform_limit"]
total = 0.0
for i, seg in enumerate(("s1", "s2"), 1):
    tr, lim = plan.constraints_on(f"{seg}:MCH")
    assert (tr.name, tr.type, tr.subtarget) == (f"BC·t1·seg{i}", "TRANSFORM", "t1:CTRL")
    assert (tr.params["from_max_y"], tr.params["mix_mode"], tr.params["use_motion_extrapolate"]) == (0.9, "ADD", False)
    assert lim.params["max_y"] == tr.params["to_max_y"]
    total += tr.params["to_max_y"]
    y = G.normalize(G.sub(plan.bone(f"{seg}:MCH").tail, plan.bone(f"{seg}:MCH").head))
    assert all(abs(c - a) < 1e-9 for c, a in zip(y, (0, 0, 1))), "segment slides on its local Y"
assert abs(total - 0.9) < 1e-9, "the tip travels the full length"
assert [c.params["to_max_y"] for c in plan.build.constraints if c.type == "TRANSFORM"] == [0.45, 0.45]
custom = P.plan_rig(scope(shares=(0.6, 0.3)))
assert [c.params["to_max_y"] for c in custom.build.constraints if c.type == "TRANSFORM"] == [0.6, 0.3]
raises(lambda: P.plan_rig(scope(shares=(0.6, 0.6))), "must add up to the total length 0.9")
raises(lambda: P.plan_rig(scope(parents=("base", "base"))), "must ride on 'Seg 1'")
raises(lambda: P.plan_rig(scope(shares=(float("nan"), 0.9))), "must add up to the total length")
raises(lambda: P.plan_rig(scope(shares=(float("inf"), 0.0))), "must add up to the total length")
raises(lambda: P.plan_rig(scope(length=float("nan"))), "total length must be above zero")
raises(lambda: P.plan_rig(scope(length=float("inf"))), "total length must be above zero")

# Piston: cylinder on the frame, rod on the arm; each end aims at a fixed point on the other side
def piston(stretch=False, rod_pivot=(0, 1, 0)):
    parts = [M.Part("frame", "Frame"), M.Part("arm", "Arm"),
             M.Part("cyl", "Cylinder", parent="frame", pivot=(0, 0, 0)),
             M.Part("rod", "Rod", parent="arm", pivot=rod_pivot)]
    return M.MechRig(parts=parts, mechanisms=[M.Mechanism("p1", "PISTON", "Lift Piston", parts=["cyl", "rod"], stretch=stretch)])


pp = P.plan_rig(piston())
assert pp.bone("p1:AIM_A").parent == "frame:DEF" and pp.bone("p1:TGT_A").parent == "arm:DEF"
assert pp.bone("p1:AIM_B").parent == "arm:DEF" and pp.bone("p1:TGT_B").parent == "frame:DEF"
assert pp.bone("p1:TGT_A").head == (0, 1, 0) and pp.bone("p1:TGT_B").head == (0, 0, 0)
assert not pp.constraints_on("p1:TGT_A") and not pp.constraints_on("p1:TGT_B"), "target points stay constraint-free"
aim_a = pp.constraints_on("p1:AIM_A")[0]
assert (aim_a.type, aim_a.subtarget, aim_a.params["track_axis"]) == ("DAMPED_TRACK", "p1:TGT_A", "TRACK_Y")
follow = [c for c in pp.constraints_on("cyl:MCH") if c.tag == "p1"][0]
assert (follow.type, follow.subtarget, follow.params["owner_space"]) == ("COPY_TRANSFORMS", "p1:AIM_A", "WORLD")
assert [c.name for c in pp.constraints_on("cyl:MCH")] == ["BC·p1·follow_a"]
y = G.normalize(G.sub(pp.bone("cyl:MCH").tail, pp.bone("cyl:MCH").head))
assert all(abs(c - a) < 1e-9 for c, a in zip(y, (0, 1, 0))), "cylinder points at the rod"
assert not any(b.name.endswith(":CTRL") for b in pp.build.bones), "a Piston has no handle"
st = P.plan_rig(piston(stretch=True)).constraints_on("p1:AIM_B")[0]
assert st.type == "STRETCH_TO" and abs(st.params["rest_length"] - 1.0) < 1e-9
raises(lambda: P.plan_rig(piston(rod_pivot=(0, 0, 0))), "at the same spot")
print("PASS mechanisms recipes: telescope shares and travel, piston aims and stretch")
