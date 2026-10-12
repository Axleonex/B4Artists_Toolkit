from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VRM_INIT = ROOT / "boneforge" / "vrm" / "__init__.py"
VRM_LINT = ROOT / "boneforge" / "vrm" / "lint.py"
VRM_UI = ROOT / "boneforge" / "vrm" / "ui.py"


def test_vrm_lint_has_humanoid_alias_fix_button():
    lint_source = VRM_LINT.read_text(encoding="utf-8")
    ui_source = VRM_UI.read_text(encoding="utf-8")
    init_source = VRM_INIT.read_text(encoding="utf-8")

    assert 'bl_idname = "boneforge.vrm_fix_humanoid_aliases"' in lint_source
    assert "def fix_humanoid_aliases(" in lint_source
    assert "humanoid_mapper.auto_map_humanoid" in lint_source
    assert 'target[_HUMANOID_ALIAS_PROP] = slot' in lint_source
    assert "_store_lint_results(context, [])" in lint_source
    assert '"boneforge.vrm_fix_humanoid_aliases"' in ui_source
    assert "fix_op.target = settings.lint_target" in ui_source
    assert "lint.BF_OT_VRMFixHumanoidAliases" in init_source
