"""Capture filtered Cascadeur license provenance without account identifiers."""

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
TRAIN = HERE.parent
LOG = Path(os.environ.get(
    "B4ML_CASCADEUR_LOG",
    r"C:\Users\Jonvilario\AppData\Local\Nekki Limited\Cascadeur\logs\cascadeur_log.log"))
INSTALLATION = TRAIN / "results/cascadeur-installation-audit-v3.json"
OUT = TRAIN / "results/cascadeur-license-audit-v1.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def last_value(lines, prefix):
    values = []
    for line in lines:
        marker = line.find(prefix)
        if marker >= 0:
            values.append(line[marker + len(prefix):].strip())
    return values[-1] if values else None


def main():
    if not LOG.exists():
        raise RuntimeError("Cascadeur runtime log is missing")
    lines = LOG.read_text(encoding="utf-8", errors="replace").splitlines()
    installation = json.loads(INSTALLATION.read_text(encoding="utf-8-sig"))
    executable = installation["executable"]
    license_name = last_value(lines, "License name: ")
    license_type = last_value(lines, "License type: ")
    actual_type = last_value(lines, "Actual license type: ")
    feature_flags = last_value(lines, "License flags: ")
    end_date = last_value(lines, "License end data: ")
    paid = last_value(lines, "Is paid: ")
    complete = all((license_name, license_type, actual_type, feature_flags, end_date))
    report = {
        "schema": "b4ml-cascadeur-license-audit-v1",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if complete else "INCOMPLETE",
        "scope": "Filtered local Cascadeur license/entitlement provenance; no account identifier, credential, settings, conversion, animation, or parity claim.",
        "executable": {
            "path": executable.get("path"),
            "file_version": executable.get("file_version"),
            "sha256": executable.get("sha256"),
        },
        "license": {
            "name": license_name,
            "type": license_type,
            "actual_type": actual_type,
            "feature_flags": feature_flags,
            "end_date": end_date,
            "paid_reported": paid == "1" if paid is not None else None,
        },
        "source": {
            "kind": "Cascadeur local runtime log",
            "sha256": sha(LOG),
            "account_identifier_recorded": False,
        },
        "settings_exported": False,
        "conversion_verified": False,
        "parity_verified": False,
        "surpasses_verified": False,
        "full_goal_complete": False,
    }
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
