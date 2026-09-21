"""Run the established 13-workflow offline validator against exact archive 0.19.5."""
from pathlib import Path


SOURCE = Path(__file__).with_name("check_visible_state_package_v1.py")
text = SOURCE.read_text(encoding="utf-8-sig")
replacements = {
    "visible-state-package-v1": "vectorized-tangent-package-v1",
    "(0,19,2)": "(0,19,5)",
    "b4artists_ml_v0.19.2.zip": "b4artists_ml_v0.19.5.zip",
    "package-test-v0.19.2.json": "package-test-v0.19.5.json",
}
for old, new in replacements.items():
    assert old in text
    text = text.replace(old, new)
exec(compile(text, str(Path(__file__)), "exec"))
