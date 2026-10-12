import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from boneforge.weights import widgets
from boneforge.autorig.rig_build import RigSpec, compute_build_plan

for wid, gen in widgets.WIDGET_LIBRARY.items():
    verts, edges = gen()
    assert verts, "empty verts: " + wid
    for a, b in edges:
        assert 0 <= a < len(verts) and 0 <= b < len(verts), ("bad edge", wid)

# every widget the engine references must exist
plan = compute_build_plan(RigSpec(preset="quadruped", spline_chains=(("spineX", 6),)))
missing = widgets.coverage_report([w.widget for w in plan.widgets])
assert missing == [], missing
assert "face" in widgets.COLOR_GROUPS
print("test_widgets PASS  (%d shapes, coverage clean)" % len(widgets.WIDGET_LIBRARY))
