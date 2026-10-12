# bonecraft/tests/test_tab_sides.py
"""Pure test: tab sides — regions, defaults, parent-first order, preference read. Run: python tests/test_tab_sides.py"""
import os
import sys
from types import SimpleNamespace as NS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from boneforge import tab_sides as ts

# regions
assert ts.region_for("LEFT") == "TOOLS" and ts.region_for("RIGHT") == "UI"
assert ts.region_for("UP") == "UI" and ts.region_for(None) == "UI", "an unknown side is the sidebar"

# tabs and defaults (owner: BoneCraft and Rig Builder left, CATS right)
assert [t[0] for t in ts.TABS] == ["boneforge", "cats", "rig_builder"], "the Preferences row order"
assert [t[1] for t in ts.TABS] == ["BoneCraft", "CATS", "Rig Builder"]
for key, category, side_pref, show_pref in ts.TABS:
    assert side_pref == "side_" + key and show_pref.startswith("show_tab_"), (key, side_pref, show_pref)
assert ts.DEFAULT_SIDE == {"boneforge": "LEFT", "rig_builder": "LEFT", "cats": "RIGHT"}
assert [i[0] for i in ts.SIDE_ITEMS] == ["LEFT", "RIGHT"]
assert ts.tab("cats")[1] == "CATS"


# parent-first order: a three-level tree given children first, siblings keep their order
def P(idname, parent=""):
    return NS(bl_idname=idname, bl_parent_id=parent, __name__=idname)


root, a, b, a1, outside = P("root"), P("a", "root"), P("b", "root"), P("a1", "a"), P("x", "not_in_list")
order = [c.bl_idname for c in ts.parents_first([a1, b, a, outside, root])]
assert order.index("root") < order.index("a") < order.index("a1"), order
assert order.index("root") < order.index("b"), order
assert order.index("b") < order.index("a"), ("siblings keep their input order", order)
assert "x" in order, "a panel whose parent is not in the list is ready at once"
loop1, loop2 = P("l1", "l2"), P("l2", "l1")
assert {c.bl_idname for c in ts.parents_first([loop1, loop2, root])} == {"l1", "l2", "root"}, "a loop never hangs"


# preference read: a stand-in context; an unreadable or unknown value gives the default
def ctx(**prefs):
    addon = NS(preferences=NS(**prefs))
    return NS(preferences=NS(addons={"boneforge": addon}))


assert ts.side_of("cats", ctx(side_cats="LEFT")) == "LEFT"
assert ts.side_of("boneforge", ctx(side_boneforge="RIGHT")) == "RIGHT"
assert ts.side_of("boneforge", ctx()) == "LEFT", "no such preference: default"
assert ts.side_of("cats", ctx(side_cats="SIDEWAYS")) == "RIGHT", "unknown value: default"
assert ts.side_of("rig_builder", NS(preferences=NS(addons={}))) == "LEFT", "add-on not installed: default"
print("PASS test_tab_sides")
