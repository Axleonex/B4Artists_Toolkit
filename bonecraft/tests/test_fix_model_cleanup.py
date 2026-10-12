from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE_ARMATURE = ROOT / "boneforge" / "core" / "armature.py"
FIX_MODEL = ROOT / "boneforge" / "vrchat" / "cats" / "fix_model.py"
CLEANUP = ROOT / "boneforge" / "vrchat" / "cats" / "cleanup.py"
CATS_PANEL = ROOT / "boneforge" / "vrchat" / "cats" / "cats_panel.py"


def test_fix_model_exposes_zero_weight_bone_toggle():
    source = FIX_MODEL.read_text(encoding="utf-8")

    assert "from boneforge.vrchat.cats.cleanup import _remove_zero_weight_bones" in source
    assert "_find_zero_weight_bones" not in source
    assert "remove_zero_weight_bones: BoolProperty" in source
    assert 'name="Remove Zero-Weight Bones"' in source
    assert "default=False" in source
    assert 'layout.prop(settings, "remove_zero_weight_bones", toggle=True)' in source
    assert "if settings.remove_zero_weight_bones:" in source
    assert "removed_count = _remove_zero_weight_bones(context, arm)" in source
    assert 'operations_done.append(f"Removed {removed_count} zero-weight bones")' in source


def test_cleanup_operator_reuses_zero_weight_helper():
    source = CLEANUP.read_text(encoding="utf-8")

    assert "def _find_zero_weight_bones(" in source
    assert "def _remove_zero_weight_bones(context, arm, zero_weight_bones=None) -> int:" in source
    assert "class BF_OT_VRC_RemoveZeroWeightBones(Operator):" in source
    assert "removed_count = _remove_zero_weight_bones(context, arm, zero_weight_bones)" in source


def test_compact_fix_model_panel_shows_zero_weight_toggle():
    source = CATS_PANEL.read_text(encoding="utf-8")

    assert 'if hasattr(settings, "remove_zero_weight_bones"):' in source
    assert 'col.prop(settings, "remove_zero_weight_bones", toggle=True)' in source
    assert "class CATS_PT_cleanup" not in source
    assert "CATS_PT_cleanup" not in source
    assert "BONEFORGE_PT_vrc_cleanup.draw" not in source
    assert source.index('col.prop(settings, "remove_empty_groups", toggle=True)') < source.index(
        'col.prop(settings, "remove_zero_weight_bones", toggle=True)'
    )
    assert source.index('col.prop(settings, "remove_zero_weight_bones", toggle=True)') < source.index(
        'col.prop(settings, "remove_constraints", toggle=True)'
    )


def test_cats_panel_has_scene_armature_target_dropdown():
    source = CATS_PANEL.read_text(encoding="utf-8")

    assert "def _cats_armature_items(scene, context):" in source
    assert "_CATS_ARMATURE_ENUM_ITEMS" in source
    assert "for index, obj in enumerate(armatures)" in source
    assert "def _cats_armature_by_name(scene, name):" in source
    assert "def _cats_target_armature_update(scene, context):" in source
    assert "for obj in context.selected_objects:" in source
    assert "if obj != arm and obj.type == 'ARMATURE':" in source
    assert "obj.select_set(False)" in source
    assert "context.view_layer.objects.active = arm" in source
    assert "arm.select_set(True)" in source
    assert "class CATS_PT_target_armature(Panel):" in source
    assert 'bl_idname = "CATS_PT_target_armature"' in source
    assert "bl_options = {'HIDE_HEADER'}" in source
    assert 'layout.prop(context.scene, "boneforge_cats_target_armature_name", text=T("Armature"))' in source
    assert "bpy.types.Scene.boneforge_cats_target_armature_name = bpy.props.EnumProperty" in source
    assert 'description="Armature used by CATS tools"' in source
    assert "items=_cats_armature_items" in source
    assert "update=_cats_target_armature_update" in source
    assert "del bpy.types.Scene.boneforge_cats_target_armature_name" in source
    assert source.index("class CATS_PT_target_armature(Panel):") < source.index("class CATS_PT_pipeline_status(Panel):")
    assert source.index("CATS_PT_target_armature,") < source.index("CATS_PT_pipeline_status,")


def test_active_armature_prefers_cats_target_before_context_active():
    source = CORE_ARMATURE.read_text(encoding="utf-8")

    assert "def _scene_target_armature(context:" in source
    assert 'getattr(scene, "boneforge_cats_target_armature_name", "")' in source
    assert 'getattr(scene, "boneforge_cats_target_armature", None)' in source
    assert "target = _scene_target_armature(context)" in source
    assert source.index("target = _scene_target_armature(context)") < source.index("obj = context.active_object")
