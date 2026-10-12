"""In-Bforartists test: the bundled quick_rigs.blend holds the Basic Humanoid asset."""
import bpy


def run():
    from boneforge.autorig import rig_assets as ra
    from boneforge.autorig import quick_human as qh
    path = ra.asset_file()
    with bpy.data.libraries.load(path, link=True, assets_only=True) as (src, dst):
        assert ra.ASSET_NAME in src.objects, src.objects
        manifest = ra.starter_manifest()
        assert set(src.objects) == {r['asset_name'] for r in manifest}, src.objects
        dst.objects = list(src.objects)
    for asset in dst.objects:
        starter = next(r for r in manifest if r['asset_name'] == asset.name)
        assert asset.type == 'ARMATURE'
        assert asset.get(qh.DROPPED_RIG_PROP) == starter['rig_name']
        assert asset.asset_data.catalog_id == ra.CATALOGS[starter['group']][0]
        assert ra.ASSET_TAG in [t.name for t in asset.asset_data.tags]
        assert tuple(asset.preview.image_size) == (256, 256)
        if starter['requires_rigify']:
            assert 'Requires Rigify' in asset.asset_data.description
    ob = next(ob for ob in dst.objects if ob.name == ra.ASSET_NAME)
    assert ob.type == 'ARMATURE', ob.type
    assert len(ob.data.bones) == len(qh._FALLBACK_BONES), len(ob.data.bones)
    assert ob.get(qh.DROPPED_RIG_PROP) == "fallback"
    assert ob.asset_data is not None
    assert ob.asset_data.catalog_id == ra.CATALOG_ID
    assert ra.ASSET_TAG in [t.name for t in ob.asset_data.tags]
    assert ob.preview is not None and tuple(ob.preview.image_size) == (256, 256)
    assert qh.enable_rigify_if_available()
    assert {r['op_id'] for r in manifest if r['requires_rigify']} == {r['op_id'] for r in qh.discover_rigify_metarigs()}
    print("PASS quick_rigs.blend: complete installed starter collection, tags, catalogs, previews")
