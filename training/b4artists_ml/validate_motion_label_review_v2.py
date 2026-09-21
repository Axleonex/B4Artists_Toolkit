"""Validate a completed v2 animator export and freeze normalized labels."""
from argparse import ArgumentParser
from pathlib import Path
import hashlib
import json
import os
import sys
import uuid


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from motion_label_review_v2 import digest_document, loads_strict, validate_review


QUEUE = ROOT / "results/motion-label-proposals-v1/review-queue.json"
CONTRACT = ROOT / "results/motion-label-reviewer-v2/review-contract.json"
MANIFEST = ROOT / "results/motion-label-reviewer-v2/manifest.json"
PAGE = ROOT / "results/motion-label-reviewer-v2/reviewer.html"
BUILDER = ROOT / "build_motion_label_reviewer_v2.py"


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def frozen_bytes(path, maximum_bytes, name):
    value = path.read_bytes()
    if not value or len(value) > maximum_bytes:
        raise ValueError(f"{name} size must be between 1 and {maximum_bytes} bytes")
    return value


def exact_manifest(manifest):
    expected = {
        "schema", "complete", "items", "embedded_frames", "queue_sha256",
        "review_contract_sha256", "review_contract_file_sha256", "builder_sha256",
        "html_sha256", "v1_html_sha256", "external_dependencies", "reviewed_items",
        "physical_ground_truth", "model_training_authorized", "full_goal_complete",
    }
    if set(manifest) != expected:
        raise ValueError("Reviewer manifest fields differ from the frozen schema")
    if not (
        manifest["schema"] == "motion-label-reviewer-v2"
        and manifest["complete"] is True
        and manifest["items"] == 130
        and not isinstance(manifest["embedded_frames"], bool)
        and manifest["embedded_frames"] == 7163
        and manifest["v1_html_sha256"] == "ac6e084ab70611cc4df382b2dd21dae93ab9ab4c40e343e3b628efb35f03afa0"
        and manifest["external_dependencies"] is False
        and manifest["reviewed_items"] == 0
        and manifest["physical_ground_truth"] is False
        and manifest["model_training_authorized"] is False
        and manifest["full_goal_complete"] is False
    ):
        raise ValueError("Reviewer manifest evidence boundary changed")


def artifact_inputs(export_path):
    queue_bytes = frozen_bytes(QUEUE, 4_000_000, "source queue")
    contract_bytes = frozen_bytes(CONTRACT, 1_000_000, "review contract")
    manifest_bytes = frozen_bytes(MANIFEST, 100_000, "reviewer manifest")
    page_bytes = frozen_bytes(PAGE, 30_000_000, "reviewer page")
    builder_bytes = frozen_bytes(BUILDER, 1_000_000, "reviewer builder")
    export_bytes = frozen_bytes(export_path, 2_000_000, "review export")
    queue = loads_strict(queue_bytes, "source queue", maximum_bytes=4_000_000)
    contract = loads_strict(contract_bytes, "review contract", maximum_bytes=1_000_000)
    manifest = loads_strict(manifest_bytes, "reviewer manifest", maximum_bytes=100_000)
    document = loads_strict(export_bytes, "review export", maximum_bytes=2_000_000)
    exact_manifest(manifest)
    identities = {
        "queue_sha256": sha_bytes(queue_bytes),
        "review_contract_file_sha256": sha_bytes(contract_bytes),
        "review_contract_sha256": digest_document(contract),
        "html_sha256": sha_bytes(page_bytes),
        "builder_sha256": sha_bytes(builder_bytes),
    }
    for name, observed in identities.items():
        if manifest[name] != observed:
            raise ValueError(f"Reviewer manifest {name} binding failed")
    if identities["review_contract_file_sha256"] != identities["review_contract_sha256"]:
        raise ValueError("Review contract is not stored in canonical form")
    if len(queue.get("items", ())) != 130 or len(contract.get("items", ())) != 130:
        raise ValueError("Frozen review artifacts must contain exactly 130 items")
    return queue, contract, document, export_bytes, manifest_bytes, identities


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def _write_exclusive(path, value):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        Path(path).unlink(missing_ok=True)
        raise


def _verify_readback(path, value):
    if path.read_bytes() != value:
        raise IOError("Review evidence readback failed")


def publish_pair(output_dir, labels, report):
    output_dir.mkdir(parents=True, exist_ok=True)
    labels_path = output_dir / "validated-labels.json"
    report_path = output_dir / "validation.json"
    if labels_path.exists() or report_path.exists():
        raise FileExistsError("Refusing to replace existing review evidence")
    token = uuid.uuid4().hex
    labels_stage = output_dir / f".validated-labels.{token}.stage"
    report_stage = output_dir / f".validation.{token}.stage"
    payloads = ((labels_stage, json_bytes(labels)), (report_stage, json_bytes(report)))
    published = []
    try:
        for path, value in payloads:
            _write_exclusive(path, value)
            _verify_readback(path, value)
        for stage, destination in ((labels_stage, labels_path), (report_stage, report_path)):
            value = stage.read_bytes()
            _write_exclusive(destination, value)
            published.append(destination)
            _verify_readback(destination, value)
    except Exception:
        for destination in reversed(published):
            destination.unlink(missing_ok=True)
        raise
    finally:
        labels_stage.unlink(missing_ok=True)
        report_stage.unlink(missing_ok=True)
    return labels_path, report_path


def main(argv=None):
    parser = ArgumentParser()
    parser.add_argument("export", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    queue, contract, document, export_bytes, manifest_bytes, identities = artifact_inputs(args.export)
    normalized, report = validate_review(document, queue, identities["queue_sha256"], contract)
    report.update({
        "source_export_path": str(args.export.resolve()),
        "source_export_file_sha256": sha_bytes(export_bytes),
        "reviewer_manifest_sha256": sha_bytes(manifest_bytes),
        **identities,
    })
    labels_payload = json_bytes(normalized)
    report["validated_labels_sha256"] = sha_bytes(labels_payload)
    labels_path, report_path = publish_pair(args.output_dir, normalized, report)
    if sha_bytes(labels_path.read_bytes()) != report["validated_labels_sha256"]:
        labels_path.unlink(missing_ok=True)
        report_path.unlink(missing_ok=True)
        raise IOError("Final validated-label identity check failed")
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
