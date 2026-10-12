from pathlib import Path
import importlib.util
import sys


ROOT = Path(__file__).resolve().parents[1]
QUALITY = ROOT / "boneforge" / "vrchat" / "cats" / "material_atlas_quality.py"


def load_quality():
    spec = importlib.util.spec_from_file_location("material_atlas_quality", QUALITY)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_texture_role_detection_from_shader_sockets():
    q = load_quality()

    assert q.detect_texture_role("Base Color") == q.ROLE_ALBEDO
    assert q.detect_texture_role("Normal", via_node_type="Normal Map") == q.ROLE_NORMAL
    assert q.detect_texture_role("Emission Color") == q.ROLE_EMISSION
    assert q.detect_texture_role("Metallic") == q.ROLE_METALLIC
    assert q.detect_texture_role("Roughness") == q.ROLE_ROUGHNESS
    assert q.detect_texture_role("Unconnected") == q.ROLE_UNKNOWN


def test_material_diagnostics_report_color_only_and_unsupported_cases():
    q = load_quality()

    color_only = q.diagnose_material({
        "material_name": "Robe Tint",
        "shader_type": "BSDF_PRINCIPLED",
        "textures": [],
    })
    unsupported = q.diagnose_material({
        "material_name": "Custom Shader",
        "shader_type": "CUSTOM_GROUP",
        "textures": [{"image_name": "custom.png", "width": 512, "height": 512, "socket_name": "Base Color"}],
    })

    assert color_only["status"] == "no_image_color_only"
    assert any("color-only fallback" in warning for warning in color_only["warnings"])
    assert unsupported["status"] == "unsupported_shader"
    assert any("unsupported shader" in warning for warning in unsupported["warnings"])


def test_duplicate_detection_excludes_alpha_and_emission_by_default():
    q = load_quality()

    textures = [
        {"material": "A", "image": "robe.png", "path": "//robe.png", "width": 1024, "height": 1024, "socket": "Base Color"},
        {"material": "B", "image": "robe.png", "path": "//robe.png", "width": 1024, "height": 1024, "socket": "Base Color"},
        {"material": "C", "image": "glow.png", "path": "//glow.png", "width": 512, "height": 512, "socket": "Emission"},
        {"material": "D", "image": "glow.png", "path": "//glow.png", "width": 512, "height": 512, "socket": "Emission"},
    ]

    groups = q.find_duplicate_texture_groups(textures)

    assert len(groups) == 1
    assert groups[0]["role"] == q.ROLE_ALBEDO
    assert groups[0]["materials"] == ["A", "B"]


def test_size_and_packing_presets_are_validated():
    q = load_quality()

    source = q.resolve_size_preset("SOURCE", source_width=300, source_height=500)
    custom_bad = q.resolve_size_preset("CUSTOM", custom_width=8, custom_height=1024)
    pixel_art = q.packing_preset_settings("PIXEL_ART")

    assert source["valid"] is True
    assert any("non-power-of-two" in warning for warning in source["warnings"])
    assert custom_bad["valid"] is False
    assert pixel_art["pixel_art_no_bleed"] is True
    assert pixel_art["padding_pixels"] <= q.PACKING_PRESETS["SAFE_DEFAULT"]["padding_pixels"]


def test_multipass_plan_blocks_unknown_roles_and_names_outputs():
    q = load_quality()

    textures = [
        {"image": "robe.png", "width": 1024, "height": 1024, "socket": "Base Color"},
        {"image": "robe_n.png", "width": 1024, "height": 1024, "socket": "Normal", "via_node": "Normal Map"},
        {"image": "mystery.png", "width": 1024, "height": 1024},
    ]

    plan = q.build_multipass_output_plan([q.ROLE_ALBEDO, q.ROLE_NORMAL, q.ROLE_ROUGHNESS], textures, base_name="robe")

    output_names = {entry["image_name"] for entry in plan["outputs"]}
    skipped_roles = {entry["role"] for entry in plan["skipped"]}
    assert "robe_albedo" in output_names
    assert "robe_normal" in output_names
    assert q.ROLE_ROUGHNESS in skipped_roles
    assert plan["errors"] == ["Unknown texture roles must be labeled or disabled before multi-pass bake."]


def test_channel_pack_plan_uses_documented_convention_and_fallbacks():
    q = load_quality()

    textures = [
        {"image": "metal.png", "width": 1024, "height": 1024, "socket": "Metallic"},
        {"image": "rough.png", "width": 1024, "height": 1024, "socket": "Roughness"},
    ]

    plan = q.build_channel_pack_plan(textures, base_name="robe")

    assert plan["image_name"] == "robe_orm"
    assert plan["colorspace"] == "Non-Color"
    assert plan["channels"]["R"]["source"] == "metal.png"
    assert plan["channels"]["G"]["source"] == "rough.png"
    assert plan["channels"]["B"]["fallback"] == 0.0
    assert plan["channels"]["A"]["fallback"] == 1.0
