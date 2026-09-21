"""Bind the frozen-proportion paired torso probe to current source and assets."""
from pathlib import Path
import hashlib
import json
import os


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training/b4artists_ml/results"
REPORT = RESULTS / "production-character-paired-torso-orientation-v1-20260917.json"
OUT = RESULTS / "production-character-paired-torso-orientation-v1-20260917-validation.json"
SOURCE = ROOT / "b4artists_ml/body_solver.py"
TEST = ROOT / "tests/test_b4artists_ml_production_character_paired_torso_orientation_v1.py"
MANIFEST = ROOT / "training/b4artists_ml/reference-assets-v1/manifest.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise RuntimeError("Production-character paired torso validation already exists")
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    if report.get("schema") != "b4ml-production-character-paired-torso-orientation-v1":
        raise ValueError("Unexpected production-character paired torso schema")
    if report.get("passed") is not True or report.get("tests") != 3:
        raise ValueError("Production-character paired torso probe did not pass 3/3")
    records = report.get("records", [])
    expected = {"standard", "tall_long_limbed", "short_broad"}
    if {row.get("profile") for row in records} != expected:
        raise ValueError("Frozen proportion set changed")
    if any(row.get("pin_error_body_scales", 1) >= 2e-4 for row in records):
        raise ValueError("Frozen proportion pin gate failed")
    if any(max(row.get("spine_orientation_error_radians", 1),
               row.get("chest_orientation_error_radians", 1)) >= 0.001 for row in records):
        raise ValueError("Frozen proportion orientation gate failed")
    if any(row.get("maximum_mesh_deformation", 0) <= 1e-4 for row in records):
        raise ValueError("Frozen proportion mesh deformation was not observed")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    if {row.get("id") for row in manifest.get("assets", [])} != expected:
        raise ValueError("Portable comparison-character manifest changed")

    validation = {
        "schema": "b4ml-production-character-paired-torso-orientation-v1-validation",
        "status": "PASS_FOCUSED_DETERMINISTIC",
        "report": REPORT.relative_to(ROOT).as_posix(),
        "report_sha256": sha(REPORT),
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "source_sha256": sha(SOURCE),
        "test": TEST.relative_to(ROOT).as_posix(),
        "test_sha256": sha(TEST),
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "manifest_sha256": sha(MANIFEST),
        "profiles": sorted(expected),
        "maximum_pin_error_body_scales": max(row["pin_error_body_scales"] for row in records),
        "maximum_orientation_error_radians": max(
            max(row["spine_orientation_error_radians"], row["chest_orientation_error_radians"])
            for row in records
        ),
        "minimum_mesh_deformation": min(row["maximum_mesh_deformation"] for row in records),
        "host_process_exit_capture": False,
        "known_host_shutdown_fault_not_qualified": True,
        "claim_boundary": report["claim_boundary"],
    }
    temporary = OUT.with_suffix(".tmp")
    temporary.write_text(json.dumps(validation, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, OUT)
    print(json.dumps(validation, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
