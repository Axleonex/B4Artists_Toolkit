from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "boneforge" / "vrchat" / "cats" / "material_atlas.py"
UV_PACKING = ROOT / "boneforge" / "vrchat" / "cats" / "uv_tools" / "packing.py"
UV_INIT = ROOT / "boneforge" / "vrchat" / "cats" / "uv_tools" / "__init__.py"
SIDEBAR = ROOT / "boneforge" / "taskboard" / "sidebar.py"
CATS_PANEL = ROOT / "boneforge" / "vrchat" / "cats" / "cats_panel.py"
INIT = ROOT / "boneforge" / "__init__.py"


def test_material_atlas_has_selectable_sources():
    source = ATLAS.read_text(encoding="utf-8")

    assert "class BF_AtlasMaterialItem" in source
    assert "class BF_AtlasTextureItem" in source
    assert "class BF_UL_VRC_AtlasMaterials" in source
    assert "class BF_UL_VRC_AtlasTextures" in source
    assert "_populate_group_sources(" in source
    assert "allowed_slot_keys=slot_keys" in source
    assert "plan_material_slot_groups(slot_sources)" in source
    assert "_group_enabled_material_count(group)" in source
    assert "_group_enabled_texture_count(group)" in source
    assert "def _route_source_image_nodes_to_uv" in source
    assert "def _route_vector_socket_to_uv" in source
    assert "upstream_input = getattr(link.from_node" in source
    assert 'uv.active_render = (uv.name == "atlas_uv")' in source


def test_material_atlas_has_quality_parity_wiring():
    source = ATLAS.read_text(encoding="utf-8")

    assert "from boneforge.vrchat.cats.material_atlas_quality import" in source
    assert "diagnostic_status: StringProperty" in source
    assert "role: EnumProperty" in source
    assert "size_override: BoolProperty" in source
    assert "packing_preset: EnumProperty" in source
    assert "bake_metallic: BoolProperty" in source
    assert "channel_pack_orm: BoolProperty" in source
    assert "build_multipass_output_plan(" in source
    assert "build_channel_pack_plan(" in source
    assert "Extra output planned" in source
    assert "BF_ATLAS_TARGET" in source


def test_material_atlas_avoids_object_select_all_poll_failure():
    source = ATLAS.read_text(encoding="utf-8")

    assert "bpy.ops.object.select_all(" not in source
    assert "def _deselect_all_objects_directly" in source
    assert "def _ensure_object_mode" in source
    assert "def _run_with_view3d_context" in source
    assert "Bake atlas texture" in source


def test_material_atlas_has_smart_combine_validation_guards():
    source = ATLAS.read_text(encoding="utf-8")

    assert "def _assign_single_atlas_material" in source
    assert "poly.material_index = 0" in source
    assert "def _validate_atlas_mesh" in source
    assert "_validate_atlas_mesh(joined, atlas_mat)" in source
    assert "Source textures forced to sample original UVs during bake" in source
    assert "Atlas mesh validated before originals are hidden" in source
    assert "boneforge_atlas_source_uv_routes" in source


def test_material_atlas_exports_atlas_uv_as_uv0_by_default():
    source = ATLAS.read_text(encoding="utf-8")

    assert "keep_source_uv_maps: BoolProperty" in source
    assert "default=False" in source
    assert "def _prepare_atlas_uv_for_export" in source
    assert 'if uv.name != "atlas_uv":' in source
    assert "mesh.uv_layers.remove(uv)" in source
    assert "mesh.uv_layers.active_index = index" in source
    assert "atlas_uv becomes UV0" in source
    assert "boneforge_atlas_uv0" in source


def test_material_atlas_has_bfa_uv_method_integration():
    source = ATLAS.read_text(encoding="utf-8")
    uv_source = UV_PACKING.read_text(encoding="utf-8")
    uv_init = UV_INIT.read_text(encoding="utf-8")

    assert "from boneforge.vrchat.cats.uv_tools import" in source
    assert "apply_atlas_uv_method(context, joined, settings" in source
    assert "summarize_atlas_uv_result(uv_result)" in source
    assert "items=atlas_uv_method_items(include_advanced=True)" in source
    assert "uv_rotation_step" in source
    assert 'ADVANCED_VARIATION = "ADVANCED_VARIATION"' in uv_source
    assert "BFA_RANDOM_ORIENTED = ADVANCED_VARIATION" in uv_source
    assert "_LEGACY_METHOD_ALIASES" in uv_source
    assert "_LEGACY_BFA_RANDOM_ORIENTED: ADVANCED_VARIATION" in uv_source
    assert "ADVANCED_VARIATION" in uv_init
    assert "BFA_RANDOM_ORIENTED" in uv_init
    assert "Advanced Variation" in uv_source


def test_material_atlas_preserves_source_uvs_by_default():
    source = ATLAS.read_text(encoding="utf-8")
    uv_source = UV_PACKING.read_text(encoding="utf-8")

    assert 'default="SOURCE_PRESERVE"' in source
    assert "SOURCE_PRESERVE = \"SOURCE_PRESERVE\"" in uv_source
    assert "Preserve Source UVs" in uv_source
    assert "def _copy_source_uvs_to_atlas_tiles" in uv_source
    assert "source_uv = mesh.uv_layers.get(source_uv_name)" in uv_source
    assert "_activate_uv_layer(obj.data, \"atlas_uv\", render=True)" in uv_source
    assert "Source UV maps missing; used Smart Pack" in uv_source


def test_material_atlas_has_manual_output_material_type_override():
    source = ATLAS.read_text(encoding="utf-8")

    assert "_OUTPUT_MATERIAL_TYPE_ITEMS" in source
    assert "output_material_type: EnumProperty" in source
    assert 'default="AUTO"' in source
    assert 'adv_col.prop(settings, "output_material_type", text=T("Material Output Type"))' in source
    assert "def _resolve_output_render_type" in source
    assert "output_render_type = _resolve_output_render_type(group, settings)" in source
    assert 'if output_render_type in ("Alpha Blend", "Alpha Clip")' in source
    assert 'elif output_render_type == "Emissive"' in source
    assert 'joined["boneforge_atlas_output_material_type"]' in source
    assert 'joined["boneforge_atlas_output_material_mode"]' in source


def test_material_atlas_has_manual_output_surface_override():
    source = ATLAS.read_text(encoding="utf-8")

    assert "_OUTPUT_SURFACE_SHADER_ITEMS" in source
    assert "output_surface_shader: EnumProperty" in source
    assert 'adv_col.prop(settings, "output_surface_shader", text=T("Surface Output"))' in source
    assert "def _resolve_output_surface_shader" in source
    assert "output_surface_shader = _resolve_output_surface_shader(settings)" in source
    assert 'nodes.new("ShaderNodeBsdfPrincipled")' in source
    assert 'nodes.new("ShaderNodeBsdfDiffuse")' in source
    assert 'nodes.new("ShaderNodeEmission")' in source
    assert 'nodes.new("ShaderNodeBsdfTransparent")' in source
    assert 'nodes.new("ShaderNodeMixShader")' in source
    assert 'joined["boneforge_atlas_output_surface_shader"]' in source
    assert 'joined["boneforge_atlas_output_surface_mode"]' in source


def test_smart_combine_preflights_before_nested_bake_operator():
    source = ATLAS.read_text(encoding="utf-8")

    assert "BF_OT_VRC_AtlasBake()" not in source
    assert "@staticmethod\n    def _build_preflight(context):" in source
    assert "preflight = BF_OT_VRC_AtlasBake._build_preflight(context)" in source
    assert 'if preflight["errors"]:' in source
    assert 'return {"CANCELLED"}' in source
    assert "except RuntimeError as bake_err:" in source
    assert "str(bake_err).splitlines()[-1]" in source


def test_material_atlas_preserves_alpha_cutout_masks():
    source = ATLAS.read_text(encoding="utf-8")

    assert "ROLE_ALPHA" in source
    assert "from array import array" in source
    assert "def _find_alpha_source_image_node" in source
    assert 'output_name="Alpha"' not in source
    assert 'node_label = getattr(node, "label", "") or node.name' in source
    assert "def _bake_alpha_mask_to_atlas" in source
    assert 'target.name = "BF_ALPHA_TARGET"' in source
    assert '"Bake atlas alpha mask"' in source
    assert "type=\"EMIT\"" in source
    assert "def _copy_mask_luminance_to_image_alpha" in source
    assert "target_pixels[index + 3]" in source
    assert "needs_alpha_atlas = _group_needs_alpha_atlas(joined, output_render_type)" in source
    assert "_bake_alpha_mask_to_atlas(context, joined, atlas_img, settings, atlas_name, res)" in source



def test_material_atlas_uses_cycles_safe_mtoon_albedo_bake_and_post_bake_debug():
    source = ATLAS.read_text(encoding="utf-8")

    assert "def _find_albedo_source_image_node" in source
    assert "def _build_albedo_bake_material" in source
    assert "def _bake_albedo_to_atlas" in source
    assert '"Bake atlas albedo"' in source
    assert 'type="DIFFUSE"' not in source
    assert "_bake_albedo_to_atlas(context, joined, atlas_img, settings)" in source
    assert "_store_debug_report(context, result_meshes, settings)" in source

def test_material_atlas_output_section_uses_clean_ui_labels():

    source = ATLAS.read_text(encoding="utf-8")

    assert 'adv_col.prop(settings, "color_fallback_size", text=T("Fallback Size"))' in source
    assert 'adv_col.prop(settings, "output_format", text=T("Format Output"))' in source
    assert 'adv_col.prop(settings, "output_material_type", text=T("Material Output Type"))' in source
    assert 'adv_col.prop(settings, "output_surface_shader", text=T("Surface Output"))' in source
    assert 'adv_col.prop(settings, "output_path", text=T("Path Output"))' in source


def test_material_atlas_backup_duplicate_toggle_is_near_analyze_row():
    source = ATLAS.read_text(encoding="utf-8")

    assert 'name="Preserve Backup Duplicate"' in source
    assert "Create and keep a visible pre-atlas duplicate for Revert." in source
    assert "Turn off to remove originals after atlasing without a backup duplicate." in source
    assert 'backup_row.prop(settings, "preserve_originals", text=T("Preserve Backup Duplicate"))' in source
    assert 'text=T("Off: no Revert backup; originals are removed after atlasing")' in source
    assert source.index('tool_row.operator("boneforge.vrc_atlas_analyze"') < source.index(
        'backup_row.prop(settings, "preserve_originals", text=T("Preserve Backup Duplicate"))'
    )
    assert source.index('backup_row.prop(settings, "preserve_originals", text=T("Preserve Backup Duplicate"))') < source.index(
        'accept_row.operator('
    )
    assert 'text=T("Accept — Delete Backup")' in source
    assert 'text=T("Revert — Restore Originals")' in source
    assert 'backup_row = layout.row(align=True)' not in source
    assert 'preserve_row.prop(settings, "preserve_originals")' not in source
    assert "hidden pre-atlas duplicate" not in source
    assert "WARNING: Originals will not be backed up" not in source


def test_material_atlas_backup_duplicates_are_visible_by_default():
    source = ATLAS.read_text(encoding="utf-8")

    assert '"""Duplicate all target meshes into a visible backup collection."""' in source
    assert "Backup collection: {_BACKUP_COLLECTION_PREFIX}[timestamp] (visible)" in source
    assert "dup.hide_set(False)" in source
    assert "dup.hide_viewport = False" in source
    assert "dup.hide_render = False" in source
    assert "layer_coll.hide_viewport = False" in source
    assert "layer_coll.hide_viewport = True" not in source


def test_taskboard_icons_are_valid_for_bforartists_52():
    source = SIDEBAR.read_text(encoding="utf-8")
    cats_panel = CATS_PANEL.read_text(encoding="utf-8")

    assert "SEQUENCE_COLOR_" not in source
    assert "SEQUENCE_COLOR_" not in cats_panel
    assert "STRIP_COLOR_01" in source
    assert "STRIP_COLOR_04" in source
    assert "STRIP_COLOR_05" in source
    assert "STRIP_COLOR_04" in cats_panel


def test_bfa_release_identity_and_lockout_files():
    init_source = INIT.read_text(encoding="utf-8")

    assert '"name": "BoneCraft"' in init_source
    assert '"version": (9, 0, 0)' in init_source
    assert (ROOT / "boneforge" / "bfa_guard.py").exists()
    assert (ROOT / "boneforge" / "BFA_EXCLUSIVE.md").exists()
    assert (ROOT.parent / "releases" / "BoneCraft-BFA-9.0.0.zip").exists()


def test_alpha_blend_preservation_is_explained_in_preflight_and_panel():
    source = ATLAS.read_text(encoding="utf-8")

    assert "preserved automatically for render order" in source
    assert "Enable manually only if draw-order changes are acceptable" in source


def test_only_successful_atlas_groups_retire_source_materials():
    source = ATLAS.read_text(encoding="utf-8")

    assert "completed_groups = []" in source
    assert "completed_groups.append(group)" in source
    assert "context, completed_groups, settings" in source
    assert "def _dominant_render_type" not in source

def test_material_atlas_rebuilds_each_source_as_one_total_mesh():
    source = ATLAS.read_text(encoding="utf-8")

    assert '_SOURCE_POLYGON_ATTRIBUTE = "boneforge_source_polygon"' in source
    assert '_SOURCE_OBJECT_ATTRIBUTE = "boneforge_source_object"' in source
    assert "_stamp_source_polygon_indices(dup.data, source_object_index)" in source
    assert "combined = obj.copy()" in source
    assert "combined.data = obj.data.copy()" in source
    assert "original_polygon_slots = [" in source
    assert "_mirror_active_uv_to_atlas(combined.data)" in source
    assert "source_face_ids.data[atlas_polygon.index].value" in source
    assert "source_object_ids.data[atlas_polygon.index].value" in source
    assert 'combined.name = f"ATLAS_{obj.name}"' in source
    assert 'combined["boneforge_atlas_preserved_slots"]' in source