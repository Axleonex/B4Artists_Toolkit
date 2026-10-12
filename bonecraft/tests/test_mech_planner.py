"""Pure test: the Mechanisms planner core, Hinge and Slide. Run: python tests/test_mech_planner.py"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from boneforge.mechanisms import geometry as G, model as M, planner as P


def raises(fn, text):
    try:
        fn()
    except P.PlanError as exc:
        assert text in str(exc), (text, str(exc))
        return
    raise AssertionError("no PlanError: " + text)


def rig_hinge(**kw):
    h = M.Mechanism("h1", "HINGE", "Blade Hinge", parts=["blade"], axis=(1, 0, 0), min=-10, max=90)
    for k, v in kw.items():
        setattr(h, k, v)
    return M.MechRig(parts=[M.Part("base", "Base"), M.Part("blade", "Blade", parent="base", pivot=(0, 0, 1))],
                     mechanisms=[h])


plan = P.plan_rig(rig_hinge())
b = {x.name: x for x in plan.build.bones}
assert set(b) == {"root", "base:MCH", "base:DEF", "blade:MCH", "blade:DEF", "h1:CTRL"}, set(b)
assert b["base:MCH"].parent == "root" and b["blade:DEF"].parent == "base:DEF" and b["h1:CTRL"].parent == "base:DEF"
assert plan.names["h1:CTRL"] == "CTRL-Blade" and plan.names["blade:DEF"] == "DEF-Blade"
assert [x.name for x in plan.build.bones if x.deform] == ["base:DEF", "blade:DEF"]
assert b["h1:CTRL"].tag == "h1" and b["blade:MCH"].tag == "blade" and b["root"].tag == ""
assert b["blade:MCH"].collection == "Mechanism MCH" and b["h1:CTRL"].collection == "Mechanism Controls"
y = G.normalize(G.sub(b["h1:CTRL"].tail, b["h1:CTRL"].head))
assert all(abs(c - a) < 1e-9 for c, a in zip(G.cross(y, plan.align_z["h1:CTRL"]), (1, 0, 0))), "bone X must be the hinge axis"

assert [c.name for c in plan.constraints_on("blade:MCH")] == ["BC·h1·copy", "BC·h1·limit"]
copy, limit = plan.constraints_on("blade:MCH")
assert copy.subtarget == "h1:CTRL" and copy.params["mix_mode"] == "AFTER_SPLIT" and copy.tag == "h1"
assert limit.params["use_limit_x"] and abs(limit.params["min_x"] - math.radians(-10)) < 1e-12
assert "use_transform_limit" not in limit.params
handle = plan.constraints_on("h1:CTRL")[0]
assert handle.type == "LIMIT_ROTATION" and handle.params["use_transform_limit"]
dfm = plan.constraints_on("blade:DEF")[0]
assert (dfm.subtarget, dfm.params["target_space"], dfm.tag) == ("blade:MCH", "WORLD", "blade")
assert plan.pose["h1:CTRL"].lock_rotation == (False, True, True) and not plan.pose["h1:CTRL"].hide
assert plan.pose["blade:MCH"].hide and plan.pose["blade:MCH"].rotation_mode == "XYZ"
assert (plan.build.widgets[0].bone, plan.build.widgets[0].widget) == ("h1:CTRL", "eyelid")

free = P.plan_rig(rig_hinge(min=-720, max=720))
assert not free.constraints_on("blade:MCH")[1].params["use_limit_x"], "360°+ range spins freely"
raises(lambda: P.plan_rig(rig_hinge(min=0, max=270)), "−180°…180°")
raises(lambda: P.plan_rig(rig_hinge(min=10, max=5)), "Min is above Max")

# Slide
s = M.MechRig(parts=[M.Part("barrel", "Barrel", pivot=(0, 0, 0))],
              mechanisms=[M.Mechanism("s1", "SLIDE", "Barrel Slide", parts=["barrel"], axis=(0, 2, 0), min=0, max=0.3)])
sp = P.plan_rig(s)
sb = sp.bone("barrel:MCH")
assert all(abs(c - a) < 1e-9 for c, a in zip(G.normalize(G.sub(sb.tail, sb.head)), (0, 1, 0))), "bone Y must be the slide axis"
lim = sp.constraints_on("barrel:MCH")[1]
assert lim.type == "LIMIT_LOCATION" and (lim.params["min_y"], lim.params["max_y"]) == (0, 0.3)
assert sp.pose["s1:CTRL"].lock_location == (True, False, True)
assert sp.build.widgets[0].widget == "arrow"

# Rigger-facing errors
r = rig_hinge()
r.parts[0].parent = "blade"
raises(lambda: P.plan_rig(r), "rides on itself")
r = rig_hinge()
r.mechanisms.append(M.Mechanism("h2", "SLIDE", "Blade Slide", parts=["blade"], axis=(0, 1, 0)))
raises(lambda: P.plan_rig(r), "already moves with 'Blade Hinge'")
raises(lambda: P.plan_rig(rig_hinge(axis=(0, 0, 0))), "degenerate")
raises(lambda: P.plan_rig(rig_hinge(parts=[])), "a Hinge moves exactly one part")
r = rig_hinge()
r.mechanisms.append(M.Mechanism("t9", "TELESCOPE", "Mast", parts=["base"], length=1.0))
raises(lambda: P.plan_rig(r), "a base part and at least one segment")
r = rig_hinge()
r.mechanisms.append(M.Mechanism("p9", "PISTON", "Lift", parts=["base"]))
raises(lambda: P.plan_rig(r), "a cylinder part and a rod part")
r = rig_hinge()
r.mechanisms.append(M.Mechanism("f9", "FOLLOW", "Cover Follow", source="h1"))
raises(lambda: P.plan_rig(r), "pick both the source joint and the target joint")

# Loops are refused and named
loop = M.MechRig(
    parts=[M.Part("p1", "Blade"), M.Part("p2", "Cover")],
    mechanisms=[M.Mechanism("h1", "HINGE", "Blade Hinge", parts=["p1"]),
                M.Mechanism("h2", "HINGE", "Cover Hinge", parts=["p2"]),
                M.Mechanism("f1", "FOLLOW", "Cover Follow", source="h1", target="h2"),
                M.Mechanism("g1", "GEAR", "Blade Gear", source="h2", target="h1")])
assert P.find_loop(loop) == "Blade Hinge → Cover Follow → Cover Hinge → Blade Gear → Blade Hinge would loop."
raises(lambda: P.plan_rig(loop), "would loop")
assert P.find_loop(rig_hinge()) is None

# Missing parts are skipped; everything else builds
r = rig_hinge()
r.parts.append(M.Part("lid", "Lid"))
r.mechanisms.append(M.Mechanism("h3", "HINGE", "Lid Hinge", parts=["lid"]))
r.missing = {"base"}
mp = P.plan_rig(r)
assert mp.bone("blade:MCH") is None and mp.bone("h1:CTRL") is None, "children of a missing part are skipped"
assert dict(mp.skipped)["h1"] == "Part 'Base' is missing" and dict(mp.skipped)["blade"] == "Part 'Base' is missing"
assert mp.bone("h3:CTRL") is not None, "other mechanisms keep working"
print("PASS mechanisms planner: parts, hinge, slide, errors, loops, missing parts")
