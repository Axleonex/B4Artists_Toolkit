"""Rebuild boneforge/assets/quick_rigs.blend from Quick Rig's own humanoid.

Usage (from bonecraft/):
    bforartists --background --factory-startup --python scripts/build_quick_rigs_asset.py
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from boneforge.autorig import quick_human as qh   # noqa: E402
from boneforge.autorig import rig_assets as ra    # noqa: E402

for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob)

arm = qh._build_fallback_skeleton(bpy.context)
arm.name = ra.ASSET_NAME
arm.data.name = ra.ASSET_NAME
arm[qh.DROPPED_RIG_PROP] = "fallback"

arm.asset_mark()
meta = arm.asset_data
meta.description = ("BoneCraft's 19-bone humanoid. Drop it on a character, "
                    "then use Rig Builder > Quick Rig > Fit Dropped Rig.")
meta.catalog_id = ra.CATALOG_ID
meta.tags.new(ra.ASSET_TAG)

img = bpy.data.images.load(os.path.join(HERE, "assets_src", "basic_humanoid_preview.png"))
preview = arm.preview_ensure()
preview.image_size = tuple(img.size)
preview.image_pixels_float = list(img.pixels)
bpy.data.images.remove(img)

bpy.ops.wm.save_as_mainfile(filepath=ra.asset_file(), compress=True)
print("WROTE", ra.asset_file())
