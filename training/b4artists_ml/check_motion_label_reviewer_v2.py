"""Static checks for the strict v2 weak-label reviewer artifact."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from motion_label_review_v2 import digest_document, loads_strict, validate_review
from validate_motion_label_review_v2 import (
    _verify_readback, _write_exclusive, exact_manifest, json_bytes,
)


ROOT = Path(__file__).resolve().parent
QUEUE = ROOT / "results/motion-label-proposals-v1/review-queue.json"
BUILD = ROOT / "results/motion-label-reviewer-v2"
HERE = Path(__file__).resolve()
BUILDER = ROOT / "build_motion_label_reviewer_v2.py"
NODE_CHECK = ROOT / "check_motion_label_reviewer_v2_runtime.js"
MOTION_CONTRACT = ROOT / "motion_label_review_v2.py"
VALIDATOR = ROOT / "validate_motion_label_review_v2.py"
EXPORT_CHECKER = ROOT / "check_motion_label_reviewer_v2_export_contract.py"


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def main():
    page = BUILD / "reviewer.html"
    contract_path = BUILD / "review-contract.json"
    manifest_path = BUILD / "manifest.json"
    export_contract_path = BUILD / "export-contract-validation.json"
    queue_bytes = QUEUE.read_bytes()
    contract_bytes = contract_path.read_bytes()
    manifest_bytes = manifest_path.read_bytes()
    page_bytes = page.read_bytes()
    builder_bytes = BUILDER.read_bytes()
    checker_bytes = HERE.read_bytes()
    node_bytes = NODE_CHECK.read_bytes()
    motion_contract_bytes = MOTION_CONTRACT.read_bytes()
    validator_bytes = VALIDATOR.read_bytes()
    export_checker_bytes = EXPORT_CHECKER.read_bytes()
    export_contract_bytes = export_contract_path.read_bytes()
    frozen_sources = {
        QUEUE: queue_bytes,
        contract_path: contract_bytes,
        manifest_path: manifest_bytes,
        page: page_bytes,
        BUILDER: builder_bytes,
        HERE: checker_bytes,
        NODE_CHECK: node_bytes,
        MOTION_CONTRACT: motion_contract_bytes,
        VALIDATOR: validator_bytes,
        EXPORT_CHECKER: export_checker_bytes,
        export_contract_path: export_contract_bytes,
    }
    manifest = loads_strict(manifest_bytes, "reviewer manifest", maximum_bytes=100_000)
    contract = loads_strict(contract_bytes, "review contract", maximum_bytes=1_000_000)
    queue = loads_strict(queue_bytes, "source queue", maximum_bytes=4_000_000)
    export_contract = loads_strict(
        export_contract_bytes, "export-contract validation", maximum_bytes=100_000
    )
    source = page_bytes.decode("utf-8")
    exact_manifest(manifest)
    if sha_bytes(page_bytes) != manifest["html_sha256"] or sha_bytes(queue_bytes) != manifest["queue_sha256"]:
        raise ValueError("Reviewer source identity mismatch")
    if sha_bytes(contract_bytes) != manifest["review_contract_file_sha256"]:
        raise ValueError("Review-contract file identity mismatch")
    if digest_document(contract) != manifest["review_contract_sha256"]:
        raise ValueError("Review-contract canonical identity mismatch")
    if sha_bytes(builder_bytes) != manifest["builder_sha256"]:
        raise ValueError("Reviewer builder identity mismatch")
    if len(queue["items"]) != 130 or len(contract["items"]) != 130:
        raise ValueError("Reviewer must cover the frozen 130-item queue")
    if [row["review_id"] for row in contract["items"]] != [row["review_id"] for row in queue["items"]]:
        raise ValueError("Reviewer contract order changed")
    required = (
        "Export completed review",
        "Export backup",
        "Next unfinished",
        "independent_animator",
        "review_contract_sha256",
        "b4ml-reviewed-motion-labels-v2",
        "done!==items.length",
        "validReview",
        "source_queue_sha256",
        "localStorage",
    )
    missing = [value for value in required if value not in source]
    if missing:
        raise ValueError("Reviewer controls or gates are missing: " + ", ".join(missing))
    if re.search(r"<(script|link)[^>]+(src|href)=", source, re.I) or "http://" in source or "https://" in source:
        raise ValueError("Reviewer must remain dependency-free and offline")
    completed = subprocess.run(
        ["node", str(NODE_CHECK)], check=True, text=True, capture_output=True
    )
    if page.read_bytes() != page_bytes or NODE_CHECK.read_bytes() != node_bytes:
        raise ValueError("Reviewer page or Node checker changed during executable validation")
    runtime = json.loads(completed.stdout)
    runtime_gates = (
        "missingIdRejected", "missingTimestampRejected", "stringFramesRejected",
        "futureTimestampRejected", "invalidSessionRejected", "overlongReviewerRejected",
        "corruptSavedStateRecovered", "exportEnabled",
    )
    if not all(runtime.get(name) is True for name in runtime_gates):
        raise ValueError("Generated reviewer failed its executable completion-gate contract")
    if runtime.get("notice") or not runtime.get("captured"):
        raise ValueError("Generated reviewer did not produce a clean complete export")
    normalized, python_validation = validate_review(
        runtime["captured"]["value"], queue, sha_bytes(queue_bytes), contract
    )
    if len(normalized["items"]) != 130 or python_validation["reviewed_items"] != 130:
        raise ValueError("Page-complete export failed Python validation")
    static_export_contract = {
        "schema": "motion-label-reviewer-export-contract-v2",
        "valid": True,
        "synthetic_contract_fixture": True,
        "browser_visual_validation": False,
        "page_generated_items": 130,
        "python_validated_items": 130,
        "missing_review_id_rejected_by_page": True,
        "missing_reviewed_utc_rejected_by_page": True,
        "string_frames_rejected_by_page": True,
        "future_review_timestamp_rejected_by_page": True,
        "invalid_session_timestamp_rejected_by_page": True,
        "overlong_reviewer_code_rejected_by_page": True,
        "corrupt_saved_state_recovered": True,
        "page_complete_export_passes_python_validator": True,
        "artifact_manifest_bindings_valid": True,
        "transactional_pair_publication_valid": True,
        "human_reviewed_items": 0,
        "physical_ground_truth": False,
        "model_training_authorized": False,
    }
    expected_export_contract_keys = set(static_export_contract) | {
        "queue_sha256", "review_contract_file_sha256", "review_contract_sha256",
        "manifest_sha256", "html_sha256", "node_check_sha256",
        "motion_contract_sha256", "validator_sha256", "builder_sha256",
        "export_contract_checker_sha256",
    }
    if set(export_contract) != expected_export_contract_keys or any(
        export_contract.get(name) != value for name, value in static_export_contract.items()
    ):
        raise ValueError("Separate export-contract evidence schema or claims changed")
    expected_export_bindings = {
        "queue_sha256": sha_bytes(queue_bytes),
        "review_contract_file_sha256": sha_bytes(contract_bytes),
        "review_contract_sha256": digest_document(contract),
        "manifest_sha256": sha_bytes(manifest_bytes),
        "html_sha256": sha_bytes(page_bytes),
        "node_check_sha256": sha_bytes(node_bytes),
        "motion_contract_sha256": sha_bytes(motion_contract_bytes),
        "validator_sha256": sha_bytes(validator_bytes),
        "builder_sha256": sha_bytes(builder_bytes),
        "export_contract_checker_sha256": sha_bytes(export_checker_bytes),
    }
    for name, observed in expected_export_bindings.items():
        if export_contract.get(name) != observed:
            raise ValueError(f"Export-contract {name} binding failed")
    report = {
        "schema": "motion-label-reviewer-validation-v2",
        "valid": True,
        "items": 130,
        "embedded_frames": manifest["embedded_frames"],
        "queue_order_exact": True,
        "complete_export_gated": True,
        "reviewer_identity_required": True,
        "independent_animator_attestation_required": True,
        "corrected_interval_validation_present": True,
        "resumable_backup_present": True,
        "external_dependencies": False,
        "reviewed_items": 0,
        "physical_ground_truth": False,
        "model_training_authorized": False,
        "full_goal_complete": False,
        "queue_sha256": sha_bytes(queue_bytes),
        "review_contract_file_sha256": sha_bytes(contract_bytes),
        "review_contract_sha256": digest_document(contract),
        "manifest_sha256": sha_bytes(manifest_bytes),
        "html_sha256": sha_bytes(page_bytes),
        "builder_sha256": sha_bytes(builder_bytes),
        "checker_sha256": sha_bytes(checker_bytes),
        "node_check_sha256": sha_bytes(node_bytes),
        "motion_contract_sha256": sha_bytes(motion_contract_bytes),
        "validator_sha256": sha_bytes(validator_bytes),
        "export_contract_checker_sha256": sha_bytes(export_checker_bytes),
        "export_contract_validation_sha256": sha_bytes(export_contract_bytes),
        "page_complete_export_passes_python_validator": True,
        "synthetic_contract_fixture": True,
        "browser_visual_validation": False,
    }
    out = BUILD / "validation.json"
    if out.exists():
        raise RuntimeError("Reviewer v2 validation evidence already exists")
    if any(path.read_bytes() != value for path, value in frozen_sources.items()):
        raise ValueError("Reviewer source or evidence changed during final validation")
    payload = json_bytes(report)
    _write_exclusive(out, payload)
    _verify_readback(out, payload)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
