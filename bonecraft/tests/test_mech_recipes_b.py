"""Pure test: Gear Link auto-pick and Follow. Run: python tests/test_mech_recipes_b.py"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from boneforge.mechanisms import model as M, planner as P
from boneforge.mechanisms.recipes import gear


def raises(fn, text):
    try:
        fn()
    except P.PlanError as exc:
        assert text in str(exc), (text, str(exc))
        return
    raise AssertionError("no PlanError: " + text)


def gears(src_min=-90, src_max=90, kind="GEAR", tgt_type="HINGE", **link):
    parts = [M.Part("a", "Gear A"), M.Part("b", "Gear B", pivot=(1, 0, 0)), M.Part("c", "Gear C", pivot=(2, 0, 0))]
    ms = [M.Mechanism("ha", "HINGE", "A Hinge", parts=["a"], min=src_min, max=src_max),
          M.Mechanism("hb", tgt_type, "B Joint", parts=["b"], axis=(1, 0, 0) if tgt_type == "HINGE" else (0, 1, 0),
                      min=-720 if tgt_type == "HINGE" else 0, max=720 if tgt_type == "HINGE" else 1),
          M.Mechanism("g1", "GEAR", "AB Gear", source="ha", target="hb", gear_kind=kind, **link)]
    return M.MechRig(parts=parts, mechanisms=ms)


g = M.Mechanism("g", "GEAR", "G", teeth_source=20, teeth_target=40)
assert gear.factor(g) == -0.5
g.gear_kind = "BELT"
assert gear.factor(g) == 0.5
g.reverse = True
assert gear.factor(g) == -0.5
assert gear.factor(M.Mechanism("r", "GEAR", "R", gear_kind="RACK", ratio=1.0, pinion_radius=0.05)) == 0.05

# within ±180° -> Transform reading the source MCH, ADD, extrapolated
plan = P.plan_rig(gears())
assert plan.recipe["g1"] == "TRANSFORM"
tr = [c for c in plan.constraints_on("b:MCH") if c.tag == "g1"][0]
assert (tr.type, tr.subtarget, tr.params["mix_mode_rot"]) == ("TRANSFORM", "a:MCH", "ADD")
assert tr.params["to_max_x_rot"] == -1.0 and tr.params["use_motion_extrapolate"]
assert [c.name for c in plan.constraints_on("b:MCH")] == ["BC·hb·copy", "BC·g1·gear", "BC·hb·limit"], "fixed stack order"
assert not plan.build.drivers
assert P.plan_rig(gears(src_min=-179, src_max=179)).recipe["g1"] == "TRANSFORM"

# a full turn or more (spec §6: max − min ≥ 360°, so exactly −180…180 too) -> simple-expression driver
for lo, hi in ((-180, 180), (-720, 720)):
    dp = P.plan_rig(gears(src_min=lo, src_max=hi))
    assert dp.recipe["g1"] == "DRIVER", (lo, hi)
    assert not [c for c in dp.build.constraints if c.tag == "g1"], "no Transform for a driver-kind gear"
    (d,) = dp.build.drivers
    assert (d.bone, d.data_path_suffix, d.index, d.tag) == ("b:MCH", "rotation_euler", 0, "b")
    assert d.expression == "bc0 * -1", d.expression
    assert d.variables == [dict(name="bc0", bone="ha:CTRL", transform_type="ROT_X", space="TRANSFORM_SPACE")]

# chains of driver-kind gears compose ratios onto the handles
rig = gears(src_min=-720, src_max=720, ratio=2.0)
rig.mechanisms.append(M.Mechanism("hc", "HINGE", "C Hinge", parts=["c"], min=-720, max=720))
rig.mechanisms.append(M.Mechanism("g2", "GEAR", "BC Gear", source="hb", target="hc", ratio=0.5))
cp = P.plan_rig(rig)
assert gear.handle_terms(rig, cp, "hb") == {("hb:CTRL", "TRANSFORM_SPACE"): 1.0, ("ha:CTRL", "TRANSFORM_SPACE"): -2.0}
dc = [d for d in cp.build.drivers if d.bone == "c:MCH"][0]
assert dc.expression == "bc0 * 1 + bc1 * -0.5", dc.expression            # (-0.5)(-2) on A, -0.5 on B
assert [v["bone"] for v in dc.variables] == ["ha:CTRL", "hb:CTRL"]

# rack: rotation -> slide; wide source uses location[1]
rp = P.plan_rig(gears(kind="RACK", tgt_type="SLIDE", pinion_radius=0.1))
rk = [c for c in rp.constraints_on("b:MCH") if c.tag == "g1"][0]
assert (rk.params["map_to"], rk.params["map_to_y_from"], rk.params["mix_mode"]) == ("LOCATION", "X", "ADD")
assert abs(rk.params["to_max_y"] - 0.1) < 1e-12
rd = P.plan_rig(gears(src_min=-720, src_max=720, kind="RACK", tgt_type="SLIDE")).build.drivers[0]
assert (rd.data_path_suffix, rd.index) == ("location", 1)
raises(lambda: P.plan_rig(gears(kind="RACK")), "target must be a Slide")
raises(lambda: P.plan_rig(gears(ratio=0.0)), "ratio must be above zero")
raises(lambda: P.plan_rig(gears(kind="RACK", tgt_type="SLIDE", pinion_radius=0.0)), "pinion radius must be above zero")

# mixed chain: limited A -> free B is Transform-kind; B -> free C is driver-kind and still carries A's motion
mixed = gears(ratio=2.0)                                                   # A within ±180°, B free
mixed.mechanisms.append(M.Mechanism("hc", "HINGE", "C Hinge", parts=["c"], min=-720, max=720))
mixed.mechanisms.append(M.Mechanism("g2", "GEAR", "BC Gear", source="hb", target="hc", ratio=0.5))
xp = P.plan_rig(mixed)
assert (xp.recipe["g1"], xp.recipe["g2"]) == ("TRANSFORM", "DRIVER")
assert gear.handle_terms(mixed, xp, "hb") == {("hb:CTRL", "TRANSFORM_SPACE"): 1.0, ("a:MCH", "LOCAL_SPACE"): -2.0}
(dx,) = xp.build.drivers
assert dx.bone == "c:MCH" and dx.expression == "bc0 * 1 + bc1 * -0.5", dx.expression
assert [(v["bone"], v["space"]) for v in dx.variables] == [("a:MCH", "LOCAL_SPACE"), ("hb:CTRL", "TRANSFORM_SPACE")]

# Follow
def follow(**kw):
    rig = gears()
    args = dict(source_range=(0, 90), target_range=(0, 40))
    args.update(kw)
    rig.mechanisms[2] = M.Mechanism("f1", "FOLLOW", "B Follow", source="ha", target="hb", **args)
    return rig


fp = P.plan_rig(follow())
ft = [c for c in fp.constraints_on("b:MCH") if c.tag == "f1"][0]
assert fp.recipe["f1"] == "STRAIGHT" and ft.type == "TRANSFORM" and not ft.params["use_motion_extrapolate"]
assert abs(ft.params["from_max_x_rot"] - math.radians(90)) < 1e-12 and abs(ft.params["to_max_x_rot"] - math.radians(40)) < 1e-12
assert (ft.params["map_to_x_from"], ft.params["mix_mode_rot"]) == ("X", "ADD")
cv = P.plan_rig(follow(curve=True))
fa = [c for c in cv.constraints_on("b:MCH") if c.tag == "f1"][0]
assert (fa.type, fa.params["transform_channel"], fa.params["mix_mode"]) == ("ACTION", "ROTATION_X", "AFTER_SPLIT")
assert isinstance(fa.params["action"], P.ActionRef) and fa.params["action"].key == "f1:curve"
(act,) = cv.actions
assert (act.bone, act.channel, act.index, act.tag) == ("b:MCH", "rotation_euler", 0, "f1")
assert [k[0] for k in act.keys] == [0.0, 10.0] and abs(act.keys[1][1] - math.radians(40)) < 1e-12
raises(lambda: P.plan_rig(follow(source_range=(0, 200))), "−180°…180°")
raises(lambda: P.plan_rig(follow(source_range=(30, 30))), "source range is empty")
free = follow()
free.mechanisms[0] = M.Mechanism("ha", "HINGE", "A Hinge", parts=["a"], min=-720, max=720)    # a free-spinning source
raises(lambda: P.plan_rig(free), "the source Hinge must have limits under a full turn")
print("PASS mechanisms recipes: gear sign/ratio/rack, D11 auto-pick, chains, follow straight/curve")
