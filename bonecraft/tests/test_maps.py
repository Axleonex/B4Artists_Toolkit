import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from boneforge.autorig import maps
from boneforge.autorig.rig_build import RigSpec, compute_build_plan

# engine target bones (FK controls + spine) must cover every map target
plan = compute_build_plan(RigSpec())
engine_bones = {b.name for b in plan.bones}
assert maps.TARGET_BONES <= engine_bones, maps.TARGET_BONES - engine_bones

names = maps.available_maps()
assert len(names) >= 4, names
for nm in names:
    data = maps.load_map(nm)
    assert maps.validate_map(data) == [], (nm, maps.validate_map(data))
    assert json.loads(json.dumps(data)) == data            # round-trip
    assert len(data["bones"]) >= 14, (nm, len(data["bones"]))
print("test_maps PASS  (%d maps, all targets valid)" % len(names))
