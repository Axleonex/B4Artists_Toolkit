"""Smallest gate-first temporal learner.

The current corpus is expected to stop before importing the learner.  A future
corpus may pass the same receipts and produce one research-only ridge candidate;
this module never promotes weights or changes the add-on runtime.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import time
from pathlib import Path
from typing import Any

from check_temporal_training_boundary_v1 import build_gate
from validate_temporal_corpus_intake_v1 import build_report as build_intake_report


ROOT = Path(os.environ.get(
    "B4ML_REPO",
    r"X:\Scripting Attempts\B4Artists_Tools\B4Artists_Anim_Tools_github"))
TRAIN = ROOT / "training" / "b4artists_ml"
RESULTS = TRAIN / "results"
DEFAULT_MANIFEST = TRAIN / "data_manifest.json"
DEFAULT_INTAKE = RESULTS / "temporal-corpus-intake-v1.json"
DEFAULT_BOUNDARY = RESULTS / "temporal-training-boundary-v1.json"
DEFAULT_LABELS = RESULTS / "reviewed-contact-intent-v1.json"
DEFAULT_IDENTITY = RESULTS / "temporal-reviewer-identity-v1.json"
DEFAULT_REPORT = RESULTS / "temporal-minimal-pipeline-v1.json"
DEFAULT_CANDIDATE = RESULTS / "temporal-minimal-candidate-v1.npz"


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    with path.open("r", encoding="utf-8-sig") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object: " + str(path))
    return value


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def evaluate_preflight(
    audit: dict[str, Any] | None,
    protocol: dict[str, Any] | None,
    skeleton: dict[str, Any] | None,
    joint: dict[str, Any] | None,
    intake: dict[str, Any] | None,
    recomputed_intake: dict[str, Any] | None,
    boundary: dict[str, Any] | None,
    corpus_manifest_sha256: str | None,
) -> dict[str, Any]:
    """Recompute every authorization condition without importing model code."""
    failures: list[str] = []
    audit = audit or {}
    protocol = protocol or {}
    recomputed = build_gate(audit, protocol, skeleton, joint, recomputed_intake)
    failures.extend(recomputed["failures"])

    if recomputed_intake is None:
        failures.append("temporal corpus intake could not be recomputed from source receipts")
    else:
        labels = recomputed_intake.get("reviewed_contact_intent", {})
        identity = recomputed_intake.get("identity_authorization", {})
        if labels.get("valid") is not True:
            failures.append("human-reviewed contact/intent receipt is not valid")
        if identity.get("valid") is not True:
            failures.append("separate identity/authorization receipt is not valid")
        if recomputed_intake.get("qualified_for_parent_boundary") is not True:
            failures.append("recomputed corpus intake is not qualified for the parent boundary")

    if intake is None:
        failures.append("temporal corpus intake receipt is unavailable to the minimal runner")
    else:
        if recomputed_intake is None:
            failures.append("stored corpus intake cannot be verified without recomputation")
        else:
            for field in ("status", "qualified_for_parent_boundary", "failures"):
                if intake.get(field) != recomputed_intake.get(field):
                    failures.append("stored corpus intake does not match recomputed field: " + field)
            for section in ("reviewed_contact_intent", "identity_authorization"):
                stored_receipt = intake.get(section, {}).get("receipt_sha256")
                current_receipt = recomputed_intake.get(section, {}).get("receipt_sha256")
                if stored_receipt != current_receipt:
                    failures.append("stored corpus intake receipt hash changed: " + section)
        intake_hash = intake.get("manifest", {}).get("manifest_sha256")
        if corpus_manifest_sha256 is None or intake_hash != corpus_manifest_sha256:
            failures.append("intake receipt is not bound to the exact corpus manifest")

    if boundary is None:
        failures.append("temporal training boundary receipt is missing")
    else:
        if boundary.get("status") != recomputed.get("status"):
            failures.append("stored temporal boundary does not match the recomputed boundary")
        if boundary.get("model_training_permitted") != recomputed.get("model_training_permitted"):
            failures.append("stored training permission does not match the recomputed boundary")
        if boundary.get("model_promotion_permitted") is not False:
            failures.append("stored boundary must keep model promotion disabled")

    ready = not failures
    return {
        "schema": "b4ml-temporal-minimal-preflight-v1",
        "status": "READY_FOR_RESEARCH_TRAINING" if ready else "BLOCKED_BEFORE_TRAINING",
        "failures": failures,
        "recomputed_parent_boundary": recomputed,
        "training_authorized": ready,
        "model_training_permitted": ready,
        "model_promotion_permitted": False,
        "identity_and_review_required": True,
        "claim_boundary": {
            "learned_temporal_quality_verified": False,
            "runtime_promoted": False,
            "independent_animator_usability_verified": False,
            "cascadeur_parity_verified": False,
            "full_goal_complete": False,
        },
    }


def build_preflight(
    manifest_path: Path = DEFAULT_MANIFEST,
    intake_path: Path = DEFAULT_INTAKE,
    boundary_path: Path = DEFAULT_BOUNDARY,
    labels_path: Path = DEFAULT_LABELS,
    identity_path: Path = DEFAULT_IDENTITY,
) -> dict[str, Any]:
    """Load the receipts and return a deterministic authorization decision."""
    manifest = load_json(manifest_path)
    intake = load_json(intake_path)
    boundary = load_json(boundary_path)
    audit = load_json(RESULTS / "action-rig-disjoint-audit-v1.json")
    protocol = load_json(RESULTS / "action-disjoint-protocol-v1.json")
    skeleton = load_json(RESULTS / "cached-skeleton-provenance-v1.json")
    joint = load_json(RESULTS / "joint-action-skeleton-protocol-v1.json")
    manifest_hash = digest(manifest_path) if manifest_path.is_file() else None
    recomputed_intake = None
    intake_recompute_error = None
    if manifest_path.is_file():
        try:
            recomputed_intake = build_intake_report(
                manifest_path, labels_path, identity_path
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            intake_recompute_error = str(exc)
    decision = evaluate_preflight(
        audit, protocol, skeleton, joint, intake, recomputed_intake,
        boundary, manifest_hash
    )
    if intake_recompute_error:
        decision["failures"].append(
            "temporal corpus intake recomputation failed: " + intake_recompute_error
        )
        decision["status"] = "BLOCKED_BEFORE_TRAINING"
        decision["training_authorized"] = False
        decision["model_training_permitted"] = False
    decision["inputs"] = {
        "manifest": {"path": display_path(manifest_path), "sha256": manifest_hash},
        "intake": {"path": display_path(intake_path), "present": intake is not None},
        "labels": {"path": display_path(labels_path), "present": labels_path.is_file()},
        "identity": {"path": display_path(identity_path), "present": identity_path.is_file()},
        "boundary": {"path": display_path(boundary_path), "present": boundary is not None},
    }
    return decision


def _candidate_bytes(model: dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    import numpy as np

    np.savez_compressed(
        buffer,
        kind=np.array(model["kind"]),
        mean=model["mean"],
        std=model["std"],
        coef=model["coef"],
    )
    return buffer.getvalue()


def train_and_evaluate(
    manifest_path: Path,
    protocol_path: Path,
    data_root: Path,
) -> tuple[dict[str, Any], bytes]:
    """Fit one ridge candidate and evaluate it only after the preflight passes."""
    import numpy as np
    from temporal_data import load_split, training_arrays, validate_manifests
    from temporal_model import evaluate, fit_ridge, selection, standardize, predict

    protocol = load_json(protocol_path)
    manifest = load_json(manifest_path)
    if protocol is None or manifest is None:
        raise ValueError("Temporal protocol or corpus manifest is missing")
    validate_manifests([manifest])
    train = load_split(data_root, manifest, "train", protocol)
    validation = load_split(data_root, manifest, "validation", protocol)
    test = load_split(data_root, manifest, "test", protocol)
    data = training_arrays(train)
    mean, std = standardize(data)
    validation_baselines = {
        name: evaluate(validation, lambda row, key=name: row[key])
        for name in ("linear", "hermite")
    }
    trials = []
    best = None
    for regularization in protocol.get("ridge_trials", [0.01]):
        candidate = fit_ridge(data, mean, std, float(regularization))
        report = evaluate(validation, lambda row, model=candidate: predict(model, row))
        trials.append({
            "regularization": float(regularization),
            "selection_score": float(selection(report)),
            "report": report,
        })
        if best is None or trials[-1]["selection_score"] < best["selection_score"]:
            best = {"model": candidate, **trials[-1]}
    if best is None:
        raise ValueError("No deterministic temporal candidate was fitted")
    test_baselines = {
        name: evaluate(test, lambda row, key=name: row[key])
        for name in ("linear", "hermite")
    }
    test_report = evaluate(test, lambda row: predict(best["model"], row))
    artifact = _candidate_bytes(best["model"])
    return {
        "schema": "b4ml-temporal-minimal-training-v1",
        "status": "RESEARCH_ONLY_CANDIDATE",
        "model_kind": "ridge",
        "protocol": {
            "path": display_path(protocol_path),
            "sha256": digest(protocol_path),
        },
        "corpus": {
            "path": display_path(manifest_path),
            "sha256": digest(manifest_path),
            "train_clips": len(train),
            "validation_clips": len(validation),
            "test_clips": len(test),
            "training_queries": int(len(data["x"])),
        },
        "selection": {
            "regularization": best["regularization"],
            "validation_score": best["selection_score"],
            "trials": trials,
            "baselines": validation_baselines,
            "selected_on": "validation",
        },
        "evaluation": {"baselines": test_baselines, "candidate": test_report},
        "artifact_sha256": hashlib.sha256(artifact).hexdigest(),
        "model_promotion_permitted": False,
        "model_promoted": False,
        "runtime_integration_permitted": False,
        "claim_boundary": {
            "learned_temporal_quality_verified": False,
            "unseen_task_quality_verified": False,
            "animator_usability_verified": False,
            "cascadeur_parity_verified": False,
            "full_goal_complete": False,
        },
    }, artifact


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
                         encoding="utf-8")
    os.replace(temporary, path)


def run_pipeline(
    manifest_path: Path = DEFAULT_MANIFEST,
    intake_path: Path = DEFAULT_INTAKE,
    boundary_path: Path = DEFAULT_BOUNDARY,
    report_path: Path = DEFAULT_REPORT,
    candidate_path: Path | None = None,
    protocol_path: Path = TRAIN / "temporal_protocol_v1.json",
    data_root: Path | None = None,
) -> dict[str, Any]:
    began = time.perf_counter()
    preflight = build_preflight(manifest_path, intake_path, boundary_path)
    report: dict[str, Any] = {
        "schema": "b4ml-temporal-minimal-pipeline-v1",
        "status": preflight["status"],
        "preflight": preflight,
        "training_started": False,
        "candidate_artifact_created": False,
        "model_promotion_permitted": False,
        "model_promoted": False,
        "runtime_integration_permitted": False,
        "full_goal_complete": False,
    }
    if not preflight["training_authorized"]:
        report["scope"] = "Fail-closed preflight; no learner module imported and no model artifact created."
        report["elapsed_seconds"] = time.perf_counter() - began
        write_json(report_path, report)
        return report

    result, artifact = train_and_evaluate(
        manifest_path, protocol_path, data_root or manifest_path.parent
    )
    report.update(result)
    report["training_started"] = True
    if candidate_path is not None:
        if candidate_path.exists():
            raise FileExistsError("Refusing to overwrite candidate artifact: " + str(candidate_path))
        candidate_path.parent.mkdir(parents=True, exist_ok=True)
        with candidate_path.open("xb") as stream:
            stream.write(artifact)
        report["candidate_artifact_created"] = True
        report["candidate_artifact"] = {
            "path": display_path(candidate_path),
            "sha256": digest(candidate_path),
        }
    report["elapsed_seconds"] = time.perf_counter() - began
    write_json(report_path, report)
    return report


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--intake", type=Path, default=DEFAULT_INTAKE)
    parser.add_argument("--boundary", type=Path, default=DEFAULT_BOUNDARY)
    parser.add_argument("--protocol", type=Path, default=TRAIN / "temporal_protocol_v1.json")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--candidate", type=Path, default=None)
    parser.add_argument("--data-root", type=Path, default=None)
    args = parser.parse_args()
    report = run_pipeline(
        args.manifest, args.intake, args.boundary, args.report,
        args.candidate, args.protocol, args.data_root,
    )
    print(json.dumps({
        "status": report["status"],
        "training_started": report["training_started"],
        "candidate_artifact_created": report["candidate_artifact_created"],
        "model_promotion_permitted": report["model_promotion_permitted"],
        "failures": report["preflight"]["failures"],
    }, indent=2), flush=True)
    return report


if __name__ == "__main__":
    result = main()
    if result["status"] == "BLOCKED_BEFORE_TRAINING":
        raise SystemExit(2)
