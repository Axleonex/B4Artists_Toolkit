"""In-Bforartists test: the bundled quick_rigs.blend holds the Basic Humanoid asset."""
import bpy


def run():
    from boneforge.autorig import rig_assets as ra
    from boneforge.autorig import quick_human as qh
    path = ra.asset_file()
    with bpy.data.libraries.load(path, link=True, assets_only=True) as (src, dst):
        assert ra.ASSET_NAME in src.objects, src.objects
        dst.objects = [ra.ASSET_NAME]
    ob = dst.objects[0]
    assert ob.type == 'ARMATURE', ob.type
    assert len(ob.data.bones) == len(qh._FALLBACK_BONES), len(ob.data.bones)
    assert ob.get(qh.DROPPED_RIG_PROP) == "fallback"
    assert ob.asset_data is not None
    assert ob.asset_data.catalog_id == ra.CATALOG_ID
    assert ra.ASSET_TAG in [t.name for t in ob.asset_data.tags]
    assert ob.preview is not None and tuple(ob.preview.image_size) == (256, 256)
    print("PASS quick_rigs.blend: Basic Humanoid asset, tag, catalog, preview")
