"""Prove that a page-complete v2 export satisfies the Python validator."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from motion_label_review_v2 import loads_strict, validate_review
from validate_motion_label_review_v2 import (
    _verify_readback, _write_exclusive, artifact_inputs, json_bytes, publish_pair,
)


QUEUE = ROOT / "results/motion-label-proposals-v1/review-queue.json"
BUILD = ROOT / "results/motion-label-reviewer-v2"
NODE_CHECK = ROOT / "check_motion_label_reviewer_v2_runtime.js"
HERE = Path(__file__).resolve()
PAGE = BUILD / "reviewer.html"
MANIFEST = BUILD / "manifest.json"
CONTRACT = BUILD / "review-contract.json"
MOTION_CONTRACT = ROOT / "motion_label_review_v2.py"
VALIDATOR = ROOT / "validate_motion_label_review_v2.py"
BUILDER = ROOT / "build_motion_label_reviewer_v2.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    sources = (QUEUE, CONTRACT, MANIFEST, PAGE, NODE_CHECK, MOTION_CONTRACT, VALIDATOR, BUILDER, HERE)
    frozen = {path: path.read_bytes() for path in sources}
    completed = subprocess.run(
        ["node", str(NODE_CHECK)], check=True, text=True, capture_output=True
    )
    if any(path.read_bytes() != value for path, value in frozen.items()):
        raise ValueError("Reviewer artifact changed while the Node contract was running")
    result = loads_strict(
        completed.stdout.encode("utf-8"), "Node export contract", maximum_bytes=2_000_000
    )
    required_rejections = (
        "missingIdRejected", "missingTimestampRejected", "stringFramesRejected",
        "futureTimestampRejected", "invalidSessionRejected", "overlongReviewerRejected",
    )
    if not all(result[name] for name in required_rejections):
        raise ValueError("Browser-side completion gate accepted corrupt stored reviews")
    if not result["corruptSavedStateRecovered"]:
        raise ValueError("Reviewer did not recover from corrupt saved browser state")
    if not result["exportEnabled"] or result["notice"] or not result["captured"]:
        raise ValueError("Browser-side complete export did not become available")
    if result["captured"]["name"] != "b4ml-reviewed-motion-labels-v2.json":
        raise ValueError("Unexpected completed-export filename")
    with tempfile.TemporaryDirectory() as directory:
        temporary = Path(directory)
        export_path = temporary / "page-export.json"
        export_path.write_text(
            json.dumps(result["captured"]["value"], indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        frozen_queue, frozen_contract, frozen_document, _, _, identities = artifact_inputs(export_path)
        second_normalized, second_validation = validate_review(
            frozen_document, frozen_queue, identities["queue_sha256"], frozen_contract
        )
        labels_path, validation_path = publish_pair(
            temporary / "published", second_normalized, second_validation
        )
        if not labels_path.is_file() or not validation_path.is_file():
            raise ValueError("Transactional publication contract failed")
    if any(path.read_bytes() != value for path, value in frozen.items()):
        raise ValueError("Reviewer artifact changed during Python validation")
    if len(second_normalized["items"]) != 130 or second_validation["reviewed_items"] != 130:
        raise ValueError("Python validator did not accept the complete 130-item contract fixture")
    report = {
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
        "queue_sha256": hashlib.sha256(frozen[QUEUE]).hexdigest(),
        "review_contract_file_sha256": hashlib.sha256(frozen[CONTRACT]).hexdigest(),
        "review_contract_sha256": identities["review_contract_sha256"],
        "manifest_sha256": hashlib.sha256(frozen[MANIFEST]).hexdigest(),
        "html_sha256": hashlib.sha256(frozen[PAGE]).hexdigest(),
        "node_check_sha256": hashlib.sha256(frozen[NODE_CHECK]).hexdigest(),
        "motion_contract_sha256": hashlib.sha256(frozen[MOTION_CONTRACT]).hexdigest(),
        "validator_sha256": hashlib.sha256(frozen[VALIDATOR]).hexdigest(),
        "builder_sha256": hashlib.sha256(frozen[BUILDER]).hexdigest(),
        "export_contract_checker_sha256": hashlib.sha256(frozen[HERE]).hexdigest(),
    }
    out = BUILD / "export-contract-validation.json"
    if out.exists():
        raise RuntimeError("Export-contract validation evidence already exists")
    payload = json_bytes(report)
    _write_exclusive(out, payload)
    _verify_readback(out, payload)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
