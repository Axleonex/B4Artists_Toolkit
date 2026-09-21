"""Validate the bounded Cascadeur capability-probe receipt."""

from pathlib import Path
import hashlib
import json
import os


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
TRAIN = HERE.parent
MANIFEST = TRAIN / "reference-assets-v1/manifest.json"
PROBE = TRAIN / "cascadeur_capability_probe_console_v1.py"
RECEIPT = TRAIN / "results/cascadeur-capability-probe-v1.json"
OUT = Path(os.environ.get(
    "B4ML_CASCADEUR_CAPABILITY_VALIDATION_OUT",
    str(TRAIN / "results/cascadeur-capability-probe-validation-v1.json")))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if not RECEIPT.exists():
        raise RuntimeError("Cascadeur capability-probe receipt is missing")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8-sig"))
    if receipt.get("schema") != "b4ml-cascadeur-capability-probe-v1":
        raise ValueError("Unexpected capability-probe schema")
    if receipt.get("status") != "PASS":
        raise ValueError("Capability probe did not pass")
    if receipt.get("all_hashes_match") is not True:
        raise ValueError("Capability probe asset hashes do not match")
    for key in (
        "conversion_attempted", "standard_rig_converted", "settings_exported",
        "parity_verified", "surpasses_verified", "full_goal_complete",
    ):
        if receipt.get(key) is not False:
            raise ValueError("Capability probe crossed claim boundary: " + key)
    assets = {row["id"]: row for row in manifest["assets"]}
    observed = {row.get("id"): row for row in receipt.get("assets", [])}
    if set(observed) != set(assets) or len(observed) != 3:
        raise ValueError("Capability probe asset set is incomplete")
    for asset_id, expected in assets.items():
        row = observed[asset_id]
        if (row.get("fbx_sha256") != expected["fbx_sha256"] or
                row.get("expected_fbx_sha256") != expected["fbx_sha256"] or
                row.get("imported") is not True or
                row.get("scene_removed") is not True or
                row.get("conversion_attempted") is not False or
                row.get("standard_rig_converted") is not False):
            raise ValueError("Capability probe asset boundary mismatch: " + asset_id)
        counts = row.get("behaviour_counts")
        if not isinstance(counts, dict) or counts.get("Joint") != 26 or counts.get("MeshObject") != 1:
            raise ValueError("Capability probe behaviour counts mismatch: " + asset_id)
    if not isinstance(receipt.get("tool_diagnostics"), list):
        raise ValueError("Capability probe tool diagnostics are missing")
    if not isinstance(receipt.get("settings_surface"), dict):
        raise ValueError("Capability probe settings surface is missing")
    report = {
        "schema": "b4ml-cascadeur-capability-probe-validation-v1",
        "complete": True,
        "status": "PASS",
        "scope": "Bounded API/tool-surface and disposable frozen-FBX import validation; no conversion or parity claim.",
        "probe": PROBE.relative_to(ROOT).as_posix(),
        "probe_sha256": sha(PROBE),
        "receipt": RECEIPT.relative_to(ROOT).as_posix(),
        "receipt_sha256": sha(RECEIPT),
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "manifest_sha256": sha(MANIFEST),
        "assets": len(observed),
        "all_hashes_match": True,
        "conversion_attempted": False,
        "standard_rig_converted": False,
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
