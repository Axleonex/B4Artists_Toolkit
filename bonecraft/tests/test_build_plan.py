"""Headless unit test of the control-rig construction engine's plan.

Pure Python — no bpy. Proves the engine produces a full IK/FK + pole +
driver + foot-roll network (vs the pre-engine generator: 1 constraint,
0 drivers), and that every widget the plan references exists in the
library. Run: python3 tests/test_build_plan.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from boneforge.autorig.rig_build import RigSpec, compute_build_plan
from boneforge.weights.widgets import coverage_report, WIDGET_LIBRARY

plan = compute_build_plan(RigSpec())
c = plan.counts()
print("plan counts:", c)

ik_constraints = [x for x in plan.constraints if x.type == "IK"]
copyrot = [x for x in plan.constraints if x.type == "COPY_ROTATION"]
limitrot = [x for x in plan.constraints if x.type == "LIMIT_ROTATION"]

# 1) gap actually closed
assert c["constraints"] >= 24, c
assert c["drivers"] >= 12, c
assert len(ik_constraints) == 4, ("expect 1 IK per limb x4", len(ik_constraints))

# 2) symmetry (both sides built)
assert plan.bones_named("-L"), "no left-side bones"
assert plan.bones_named("-R"), "no right-side bones"

# 3) blend drivers reference the IK_FK properties
blend_drivers = [d for d in plan.drivers if "influence" in d.data_path_suffix]
assert len(blend_drivers) >= 12, len(blend_drivers)
ikfk_props = [p for p in plan.props if p.name.startswith("IK_FK-")]
assert len(ikfk_props) == 4, [p.name for p in plan.props]

# 4) foot roll present with drivers
foot_props = [p for p in plan.props if p.name.startswith("foot_roll-")]
assert len(foot_props) == 2, foot_props
assert len(limitrot) == 4, len(limitrot)

# 5) deform skeleton present and tagged
deform = plan.deform_bones()
assert any("spine" in d for d in deform) and any("hand.def" in d for d in deform), deform
assert len(deform) >= 12, deform

# 6) every referenced widget exists in the library
missing = coverage_report([w.widget for w in plan.widgets])
assert missing == [], ("widgets missing from library: %s" % missing)
assert all(w.color_group in ("fk", "ik", "root", "special", "deform", "face")
           for w in plan.widgets), "bad colour group"

# 7) collections organised
coll_names = {cc.name for cc in plan.collections}
assert {"FK", "IK", "Deform"} <= coll_names, coll_names

print("IK constraints:", len(ik_constraints),
      "| COPY_ROTATION:", len(copyrot),
      "| LIMIT_ROTATION:", len(limitrot),
      "| blend drivers:", len(blend_drivers))
print("widget library size:", len(WIDGET_LIBRARY),
      "| collections:", sorted(coll_names))
# -- face option (R2): plan validates and carries the face network ----
from boneforge.autorig.components import validate_plan

face_plan = compute_build_plan(RigSpec(face=True))
assert validate_plan(face_plan) == [], validate_plan(face_plan)
face_bones = {b.name for b in face_plan.bones}
for needed in ("jaw", "lip.upper", "lip.lower", "eye-L", "eye-R",
               "eye.ik-L", "eye_master", "lid.upper-L", "brow-L", "face_props"):
    assert needed in face_bones, ("missing face bone", needed)
# jaw limit + eye aim + lip-follow constraints exist
ftypes = [(cc.bone, cc.type, cc.name) for cc in face_plan.constraints]
assert any(t == ("jaw", "LIMIT_ROTATION", "BF_JAW_LIMIT") for t in ftypes)
assert any(b == "eye-L" and ty == "DAMPED_TRACK" for b, ty, _ in ftypes)
assert any(n == "BF_LIP_FOLLOW" for _, _, n in ftypes)
# soft/sticky-lips driver references both props
lip_drv = [d for d in face_plan.drivers if "BF_LIP_FOLLOW" in d.data_path_suffix]
assert lip_drv and "s * (1.0 - k)" == lip_drv[0].expression, lip_drv
face_props = {p.name for p in face_plan.props if p.bone == "face_props"}
assert {"soft_lips", "sticky_lips"} <= face_props, face_props
# face widgets all exist in the library
face_missing = coverage_report([w.widget for w in face_plan.widgets])
assert face_missing == [], ("face widgets missing: %s" % face_missing)
assert "Face" in {cc.name for cc in face_plan.collections}
print("face plan PASS  (jaw limit + eye aim + soft/sticky-lips drivers, "
      "%d bones)" % len(face_bones))

print("\nALL ENGINE PLAN TESTS PASS  (gap closed: %d constraints, %d drivers vs old 1/0)"
      % (c["constraints"], c["drivers"]))
