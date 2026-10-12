"""Pure test: Rig Builder's single placement (Properties > Scene tab) and compact rule."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from boneforge.autorig import rb_placement as rp

assert rp.SCENE_PLACEMENT == {"bl_space_type": "PROPERTIES", "bl_region_type": "WINDOW",
                              "bl_context": "scene", "bl_category": ""}, rp.SCENE_PLACEMENT
for gone in ("TOOL_SHELF", "PROPERTIES", "LOCATION_ITEMS", "location_from_prefs", "placement"):
    assert not hasattr(rp, gone), ("Tool Shelf / location option must be gone", gone)

# compact threshold: < 220 * ui_scale
assert rp.is_compact(100, 1.0) and rp.is_compact(219.9, 1.0)
assert not rp.is_compact(220, 1.0) and not rp.is_compact(300, 1.0)
assert rp.is_compact(400, 2.0) and not rp.is_compact(440, 2.0)
print("test_rb_placement PASS")
