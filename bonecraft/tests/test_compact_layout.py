"""Pure test: CompactLayout stacks rows in a narrow shelf and keeps every word (owner, 2026-10-10).

Show, don't hide: labels are no longer shortened and info lines are no longer dropped; text too wide
for the shelf wraps (core.wrap_layout) instead.
"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from boneforge.autorig.compact_layout import CompactLayout


class Rec:
    """Records every layout call; any call returns another Rec."""
    def __init__(self, log):
        self.__dict__["log"] = log
    def __getattr__(self, name):
        def call(*a, **k):
            self.log.append((name, a, k))
            return Rec(self.log)
        return call
    def __setattr__(self, name, value):
        self.log.append(("set", name, value))


log = []
root = CompactLayout(Rec(log))

row = root.row(align=True)
assert isinstance(row, CompactLayout)
assert log[-1][0] == "column" and log[-1][2] == {"align": True}, "row must become a column"
root.split(factor=0.4)
assert log[-1][0] == "column"
box = root.box()
assert isinstance(box, CompactLayout)

# every label, button and setting draws with its full text: nothing shortened, nothing hidden
box.label(text="Fit Rig to Active Mesh", icon="CHECKMARK")
assert log[-1] == ("label", (), {"text": "Fit Rig to Active Mesh", "icon": "CHECKMARK"})
box.label(text="Preview only - replace with your own mesh before final use.", icon="INFO")
assert log[-1] == ("label", (), {"text": "Preview only - replace with your own mesh before final use.",
                                  "icon": "INFO"}), "info lines are shown"
box.label("Positional label", icon="INFO")
assert log[-1] == ("label", ("Positional label",), {"icon": "INFO"}), log[-1]

op = box.operator("boneforge.quick_mannequin", text="Quick Mannequin", icon="OUTLINER_OB_MESH")
assert log[-1] == ("operator", ("boneforge.quick_mannequin",), {"text": "Quick Mannequin", "icon": "OUTLINER_OB_MESH"})
op.rig_label = "Human"                                   # operator props still settable
box.prop("DATA", "fit", text="Fit Rig to Active Mesh")
assert log[-1] == ("prop", ("DATA", "fit"), {"text": "Fit Rig to Active Mesh"})

root.scale_y = 1.3                                       # attribute writes reach the layout
assert ("set", "scale_y", 1.3) in log
root.separator()
assert log[-1][0] == "separator"
print("test_compact_layout PASS")
