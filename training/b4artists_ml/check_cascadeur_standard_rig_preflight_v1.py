"""Validate the disposable Cascadeur standard-rig preflight receipt."""

from pathlib import Path
import hashlib
import json
import os
import re


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
TRAIN = HERE.parent
MANIFEST = TRAIN / "reference-assets-v1/manifest.json"
PROBE = TRAIN / "cascadeur_standard_rig_preflight_console_v1.py"
RECEIPT = TRAIN / "results/cascadeur-standard-rig-preflight-v1.json"
OUT = Path(os.environ.get(
    "B4ML_CASCADEUR_STANDARD_RIG_VALIDATION_OUT",
    str(TRAIN / "results/cascadeur-standard-rig-preflight-validation-v1.json")))
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if not RECEIPT.exists():
        raise RuntimeError("Cascadeur standard-rig preflight receipt is missing")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8-sig"))
    if receipt.get("schema") != "b4ml-cascadeur-standard-rig-preflight-v1":
        raise ValueError("Unexpected standard-rig preflight schema")
    if receipt.get("status") != "PASS":
        raise ValueError("Standard-rig preflight did not pass")
    template = receipt.get("template")
    if not isinstance(template, dict) or not SHA256.fullmatch(template.get("sha256", "")):
        raise ValueError("Standard-rig template provenance is invalid")
    assets = {row["id"]: row for row in manifest["assets"]}
    observed = {row.get("id"): row for row in receipt.get("assets", [])}
    if set(observed) != set(assets) or len(observed) != 3:
        raise ValueError("Standard-rig preflight asset set is incomplete")
    for asset_id, expected in assets.items():
        row = observed[asset_id]
        if (row.get("fbx_sha256") != expected["fbx_sha256"] or
                row.get("expected_fbx_sha256") != expected["fbx_sha256"] or
                row.get("imported") is not True or
                row.get("scene_removed") is not True or
                row.get("template_attempted") is not True or
                row.get("template_call_ok") is not True or
                row.get("generate_attempted") is not True or
                row.get("generate_call_ok") is not True):
            raise ValueError("Standard-rig preflight boundary mismatch: " + asset_id)
    for key in (
        "standard_rig_converted", "animation_tested", "settings_exported",
        "parity_verified", "surpasses_verified", "full_goal_complete",
    ):
        if receipt.get(key) is not False:
            raise ValueError("Standard-rig preflight crossed claim boundary: " + key)
    report = {
        "schema": "b4ml-cascadeur-standard-rig-preflight-validation-v1",
        "complete": True,
        "status": "PASS",
        "scope": "Disposable template/prototype-call validation only; no final rig, animation, or parity claim.",
        "probe": PROBE.relative_to(ROOT).as_posix(),
        "probe_sha256": sha(PROBE),
        "receipt": RECEIPT.relative_to(ROOT).as_posix(),
        "receipt_sha256": sha(RECEIPT),
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "manifest_sha256": sha(MANIFEST),
        "template_sha256": template["sha256"],
        "assets": len(observed),
        "conversion_attempted": True,
        "standard_rig_converted": False,
        "animation_tested": False,
        "settings_exported": False,
        "parity_verified": False,
        "surpasses_verified": False,
        "full_goal_complete": False,
    }
    temporary = OUT.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, OUT)
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
