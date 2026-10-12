# bonecraft/tests/test_mech_guide_steps.py
"""Pure test: guided build steps. Run: python tests/test_mech_guide_steps.py"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from boneforge.mechanisms.guide_steps import STEPS, Guide

assert set(STEPS) == {"HINGE", "SLIDE", "TELESCOPE", "PISTON", "GEAR", "FOLLOW"}
g = Guide("PISTON")
assert g.prompt(True) == "Step 1 of 2: click the cylinder part. Esc cancels."
assert g.prompt(False) == "Cylinder part"
assert g.pick("a", None) == "" and g.prompt(True) == "Step 2 of 2: click the rod part. Esc cancels."
assert g.pick("a", None) == "That part is already picked."
assert g.pick("b", None) == "" and g.done
assert g.prompt(True) == "Enter keeps it; Esc removes it." and g.prompt(False) == "Enter / Esc"
assert g.op_args() == ("BC_OT_mech_add_link", {"type": "PISTON", "parts": "a,b"})

h = Guide("HINGE")
assert h.choose_axis("X") == "Click the part first."
assert h.pick("p", None) == "" and h.pick("q", None) == "Press X, Y or Z for the axis, or A to align to the selection."
assert h.choose_axis("Z") == "" and h.done
assert h.op_args() == ("BC_OT_mech_add_joint", {"type": "HINGE", "parts": "p", "axis": "Z"})

t = Guide("TELESCOPE")
t.pick("base", None)
assert t.finish_list() == "Click at least one segment."
t.pick("s1", None)
t.pick("s2", None)
assert t.finish_list() == "" and t.choose_axis("SELECTION") == ""
assert t.op_args() == ("BC_OT_mech_add_joint", {"type": "TELESCOPE", "parts": "base,s1,s2", "axis": "SELECTION"})

f = Guide("GEAR")
assert f.pick("p", None) == "That part needs a Hinge first."
assert f.pick("p", "SLIDE") == "That part needs a Hinge first."
assert f.pick("p", "HINGE") == "" and f.pick("q", None) == "That part needs a Hinge or Slide first."
assert f.pick("q", "SLIDE") == "" and f.op_args() == ("BC_OT_mech_add_link", {"type": "GEAR", "source": "p", "target": "q"})
f.back()
assert not f.done and f.picked == ["p"], "back() undoes the last answer"

# The viewport header line: hover and picked names and the message ride behind the prompt
from boneforge.mechanisms.guide_steps import header_text
assert header_text("P") == "P"
assert header_text("P", hover="Blade1") == "P   (over: Blade1)"
assert header_text("P", picked="Blade1") == "P   (picked: Blade1)"
assert header_text("P", picked="Blade1", message="That part is already picked.") == "P   (picked: Blade1 · That part is already picked.)"

print("PASS mechanisms guide steps: prompts long/short, needs, telescope list, axis, operator arguments")
