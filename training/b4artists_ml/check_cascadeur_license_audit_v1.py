"""Validate filtered Cascadeur license/entitlement provenance."""

from pathlib import Path
import hashlib
import json
import os
import re


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
TRAIN = HERE.parent
RECEIPT = TRAIN / "results/cascadeur-license-audit-v1.json"
OUT = Path(os.environ.get(
    "B4ML_CASCADEUR_LICENSE_VALIDATION_OUT",
    str(TRAIN / "results/cascadeur-license-audit-validation-v1.json")))
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if not RECEIPT.exists():
        raise RuntimeError("Cascadeur license-audit receipt is missing")
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8-sig"))
    if receipt.get("schema") != "b4ml-cascadeur-license-audit-v1":
        raise ValueError("Unexpected Cascadeur license-audit schema")
    if receipt.get("status") != "PASS":
        raise ValueError("Cascadeur license-audit did not pass")
    executable = receipt.get("executable")
    license_info = receipt.get("license")
    source = receipt.get("source")
    if not isinstance(executable, dict) or not isinstance(license_info, dict):
        raise ValueError("License-audit executable or license data is missing")
    if not isinstance(source, dict):
        raise ValueError("License-audit source data is missing")
    if not executable.get("file_version") or not SHA256.fullmatch(executable.get("sha256", "")):
        raise ValueError("License-audit executable provenance is invalid")
    if (license_info.get("type") != "yearly" or
            license_info.get("actual_type") != "yearly" or
            license_info.get("paid_reported") is not True or
            not license_info.get("end_date") or
            "export" not in license_info.get("feature_flags", "") or
            "profeatures" not in license_info.get("feature_flags", "")):
        raise ValueError("License-audit entitlement fields are incomplete")
    if (source.get("account_identifier_recorded") is not False or
            not SHA256.fullmatch(source.get("sha256", ""))):
        raise ValueError("License-audit source boundary is invalid")
    for key in (
        "settings_exported", "conversion_verified", "parity_verified",
        "surpasses_verified", "full_goal_complete",
    ):
        if receipt.get(key) is not False:
            raise ValueError("License-audit crossed claim boundary: " + key)
    report = {
        "schema": "b4ml-cascadeur-license-audit-validation-v1",
        "complete": True,
        "status": "PASS",
        "scope": "Filtered entitlement provenance only; no settings, conversion, animation, or parity claim.",
        "receipt": RECEIPT.relative_to(ROOT).as_posix(),
        "receipt_sha256": sha(RECEIPT),
        "executable_version": executable["file_version"],
        "feature_flags": license_info["feature_flags"],
        "account_identifier_recorded": False,
        "settings_exported": False,
        "conversion_verified": False,
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
