"""Pure test: Mechanisms records, ids and names (no bpy). Run: python tests/test_mech_model.py"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from boneforge.mechanisms import model as M

tokens = iter(["root", "aaaa0001", "aaaa0002"])
assert M.new_id({"aaaa0001"}, token=lambda: next(tokens)) == "aaaa0002"   # never "root", never taken
assert M.clean_name('  Big   "Gun" \\ ') == "Big _Gun_ _"
assert M.clean_name("   ") == "Part"
assert M.unique_name("CTRL-Blade", {"CTRL-Blade", "CTRL-Blade.001"}) == "CTRL-Blade.002"
assert M.unique_name("CTRL-Blade", set()) == "CTRL-Blade"
assert M.default_name("Blade", "HINGE") == "Blade Hinge"
assert M.default_name("Barrel", "SLIDE") == "Barrel Slide"

rig = M.MechRig(
    parts=[M.Part("p1", "Blade")],
    mechanisms=[M.Mechanism("m1", "HINGE", "Blade Hinge", parts=["p1"]),
                M.Mechanism("m2", "FOLLOW", "Cover Follow", source="m1", target="m1")],
    sequences=[M.Sequence("s1", "Fold")],
)
assert M.controls(rig) == [("m1", "Blade Hinge"), ("s1", "Fold")]
assert rig.part("p1").name == "Blade" and rig.mech("nope") is None and rig.seq("s1").name == "Fold"
assert rig.ids() == {"p1", "m1", "m2", "s1"}
assert rig.missing == set()

assert M.gear_ratio(M.Mechanism("g", "GEAR", "G", teeth_source=20, teeth_target=40)) == 0.5
assert M.gear_ratio(M.Mechanism("g", "GEAR", "G", ratio=3.0)) == 3.0
assert set(M.FIELDS) == set(M.TYPES)
assert "pinion_radius" not in M.FIELDS["HINGE"] and "pinion_radius" in M.FIELDS["GEAR"]
assert M.DEFAULT_WIDGET["HINGE"] == "eyelid"


# Capture Step windows: the next quarter after the last step's end; past 1.0 it reuses 0.75-1.0 (and overlaps)
assert M.step_window([]) == (0.0, 0.25)
assert M.step_window([(0.0, 0.25)]) == (0.25, 0.5)
assert M.step_window([(0.5, 1.0)]) == (0.75, 1.0)
assert M.overlapping_steps([(0.0, 0.25), (0.5, 1.0)], 0.75, 1.0) == [1]
assert M.overlapping_steps([(0.0, 0.25)], 0.25, 0.5) == []
assert M.overlapping_steps([(0.2, 0.6)], 0.5, 0.75) == [0]

import boneforge.mechanisms as pkg
assert pkg._SUBMODULES == () or isinstance(pkg._SUBMODULES, tuple)
assert "bpy" not in sys.modules, "pure modules imported bpy"
print("PASS mechanisms model: ids, names, controls, ratios, fields")
