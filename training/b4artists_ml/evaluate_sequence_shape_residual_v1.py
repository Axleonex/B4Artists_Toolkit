"""Frozen development evaluation for shape-residual temporal models.

SPDX-License-Identifier: GPL-2.0-or-later
"""
from pathlib import Path
import hashlib
import json
import os
import time

os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")
import numpy as np

from kinematic_trajectory_v20 import predict_packed as control_predict
from motion_coverage import evaluate_predictions
from semantic_projection import load_windows, project_windows
from sequence_model import acceptance
from sequence_shape_ablation_v1 import predict_packed as ablation_predict
from sequence_shape_residual_provider_v1 import Provider


ROOT = Path(__file__).resolve().parents[2]
TR = Path(__file__).resolve().parent
HERE = Path(__file__).resolve()
BASE = TR / "results/sequence-shape-residual-development-v1"
PLAN_PATH = TR / "sequence_shape_residual_evaluation_plan_v1.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def attribution(candidate, ablation):
    metrics = ("position", "rotation", "velocity", "acceleration", "length")
    ratios = {
        name: candidate["aggregate"][name] / max(ablation["aggregate"][name], 1e-12)
        for name in metrics
    }
    cohorts = {
        key: value["position"] / max(ablation["cohorts"][key]["position"], 1e-12)
        for key, value in candidate["cohorts"].items()
    }
    return {
        "passed": ratios["position"] < 1.0,
        "position_improved": ratios["position"] < 1.0,
        "ratios": ratios,
        "max_cohort_position_ratio": max(cohorts.values()),
        "cohort_position_ratios": cohorts,
    }


def main():
    plan = read(PLAN_PATH)
    protocol = read(TR / plan["reference_protocol"])
    reference = read(TR / plan["reference_report"])
    assert sha(TR / plan["reference_protocol"]) == plan["reference_protocol_sha256"]
    assert sha(TR / plan["reference_report"]) == plan["reference_report_sha256"]
    assert protocol["gates"] == reference["protocol"]["gates"]
    assert protocol["projection"] == reference["protocol"]["projection"]
    assert protocol["baselines"] == reference["protocol"]["baselines"]
    for name, digest in plan["sources"].items():
        assert sha(TR / name) == digest, name
    training = TR / "results/sequence-shape-residual-training-v1"
    assert read(training / "active-process.json").get("all_complete") is True
    processes = read(training / "processes.json")
    assert len(processes) == 2 and all(row["exit_code"] == 0 for row in processes)
    models = []
    for item in plan["models"]:
        name = "shape-residual-" + str(item["seed"])
        report_path = training / ("direct-" + str(item["seed"])) / "report.json"
        report = read(report_path)
        assert report["complete"] and report["completed_epochs"] == 60
        assert not report["validation_read"] and not report["confirmation_read"]
        assert report["cpu_export_max_abs_error"] < 5e-5
        assert report["plan_sha256"] == plan["training_plan_sha256"]
        assert sha(ROOT / report["weights"]) == report["weights_sha256"]
        assert sha(report_path) == item["report_sha256"]
        assert report["weights_sha256"] == item["weights_sha256"]
        models.append(
            {
                "name": name,
                "seed": item["seed"],
                "weights": report["weights"],
                "weights_sha256": report["weights_sha256"],
                "report_sha256": item["report_sha256"],
            }
        )
    protected = read(TR / "temporal_expansion_plan_v19.json")["planned_splits"]["confirmation"]
    assert all(not (TR / "cache" / (name + ".bvh")).exists() for name in protected)
    BASE.mkdir(exist_ok=False)
    started = time.perf_counter()
    frozen = {
        "models": models,
        "plan_sha256": sha(PLAN_PATH),
        "script_sha256": sha(HERE),
        "validation_loaded": False,
        "confirmation_read": False,
        "recorded_at": time.time(),
    }
    write(BASE / "frozen-before-validation.json", frozen)

    manifest = read(TR / "temporal_training_manifest_v19.json")
    assert sha(TR / "temporal_training_manifest_v19.json") == protocol["source_manifests"]["temporal_training_manifest_v19.json"]
    windows, skeleton = load_windows(TR, manifest, "validation", protocol)
    old_ids = set(protocol["old_validation_clips"])
    new_ids = set(protocol["new_validation_clips"])
    assert not old_ids & new_ids
    partitions = {
        "old_validation": [window for window in windows if window["clip"] in old_ids],
        "new_validation": [window for window in windows if window["clip"] in new_ids],
    }
    assert len(partitions["old_validation"]) == 480
    assert len(partitions["new_validation"]) == 288
    assert sum(map(len, partitions.values())) == len(windows) == 768
    identities = {
        name: [
            {
                "clip": window["clip"],
                "gap": window["gap"],
                "context": window["context"],
                "frames": window["frame"].tolist(),
            }
            for window in rows
        ]
        for name, rows in partitions.items()
    }
    write(BASE / "window-identities.json", identities)
    reports = {name: {} for name in (*partitions, "combined")}
    methods = [
        {"name": "projected_" + baseline, "control": baseline}
        for baseline in ("linear", "hermite", "shape")
    ]
    methods.append({"name": "observed_shape_ablation", "ablation": True})
    methods.extend(models)
    failures = {}
    for method in methods:
        name = method["name"]
        provider = None if "weights" not in method else Provider(
            ROOT / method["weights"], method["weights_sha256"], seed=method["seed"]
        )
        all_windows = []
        all_output = []
        edges = []
        outdir = BASE / name
        outdir.mkdir()
        try:
            for partition, rows in partitions.items():
                output = []
                fitting = []
                edge = 0.0
                inference_seconds = 0.0
                projection_seconds = 0.0
                for offset in range(0, len(rows), plan["chunk_size"]):
                    assert time.time() < plan["deadline_unix"]
                    batch = rows[offset : offset + plan["chunk_size"]]
                    at = time.perf_counter()
                    if "control" in method:
                        proposal = [
                            control_predict({"kind": "baseline", "baseline": method["control"]}, window["observations"], window["t"])
                            for window in batch
                        ]
                    elif method.get("ablation"):
                        proposal = [ablation_predict(window["observations"], window["t"]) for window in batch]
                    else:
                        proposal = [provider.predict_packed(window["observations"], window["t"]) for window in batch]
                    inference_seconds += time.perf_counter() - at
                    for window, prediction in zip(batch, proposal):
                        assert np.isfinite(prediction).all()
                        assert np.array_equal(prediction[[0, -1]], window["linear"][[0, -1]])
                    at = time.perf_counter()
                    values, metric = project_windows(batch, proposal, skeleton, protocol["projection"])
                    projection_seconds += time.perf_counter() - at
                    output += values
                    edge = max(edge, metric["true_edge_length_max"])
                    fitting.append(metric["position_fit_error"])
                    np.savez_compressed(
                        outdir / (partition + "-" + str(offset) + ".npz"),
                        **{str(index): value for index, value in enumerate(values)},
                    )
                    write(
                        BASE / "progress.json",
                        {
                            "method": name,
                            "partition": partition,
                            "windows_completed": offset + len(batch),
                            "partition_windows": len(rows),
                            "seconds": time.perf_counter() - started,
                        },
                    )
                scored = evaluate_predictions(rows, output)
                scored["aggregate"]["true_edge_length_max"] = edge
                scored["projection"] = {
                    "true_edge_length_max": edge,
                    "position_fit_error": float(np.mean(fitting)),
                }
                reports[partition][name] = scored
                if "control" in method:
                    assert scored == reference["partition_reports"][partition][name]
                write(outdir / (partition + "-metrics.json"), scored)
                write(
                    outdir / (partition + "-timings.json"),
                    {"inference_seconds": inference_seconds, "projection_seconds": projection_seconds},
                )
                all_windows += rows
                all_output += output
                edges.append(edge)
                print(
                    json.dumps(
                        {
                            "method": name,
                            "partition": partition,
                            "position": scored["aggregate"]["position"],
                            "seconds": time.perf_counter() - started,
                        }
                    ),
                    flush=True,
                )
            combined = evaluate_predictions(all_windows, all_output)
            combined["aggregate"]["true_edge_length_max"] = max(edges)
            reports["combined"][name] = combined
            if "control" in method:
                assert combined == reference["partition_reports"]["combined"][name]
            write(outdir / "combined-metrics.json", combined)
        except (ValueError, ArithmeticError, AssertionError) as exc:
            if "control" in method or method.get("ablation"):
                raise
            failures[name] = repr(exc)
            write(outdir / "failed-candidate.json", {"error": repr(exc), "quality_qualified": False})
            print(json.dumps({"method": name, "failed": repr(exc)}), flush=True)

    gates = {}
    attributions = {}
    for model in models:
        name = model["name"]
        if name in failures:
            gates[name] = {partition: {"passed": False, "error": failures[name]} for partition in reports}
            attributions[name] = dict(gates[name])
            continue
        gates[name] = {
            partition: acceptance(
                {
                    **{baseline: reports[partition][baseline] for baseline in protocol["baselines"]},
                    "mlp": reports[partition][name],
                },
                protocol,
            )
            for partition in reports
        }
        attributions[name] = {
            partition: attribution(
                reports[partition][name], reports[partition]["observed_shape_ablation"]
            )
            for partition in reports
        }
    family_passes = all(
        gates[model["name"]][partition]["passed"]
        and attributions[model["name"]][partition]["passed"]
        for model in models
        for partition in reports
    )
    assert all(not (TR / "cache" / (name + ".bvh")).exists() for name in protected)
    for name, digest in plan["sources"].items():
        assert sha(TR / name) == digest
    report = {
        "complete": True,
        "models": models,
        "partition_reports": reports,
        "development_gates": gates,
        "ablation_attribution": attributions,
        "failed_candidates": failures,
        "family_passes": family_passes,
        "protected_baselines_match": True,
        "validation_windows": 768,
        "confirmation_read": False,
        "full_goal_complete": False,
        "runtime_promoted": False,
        "seconds": time.perf_counter() - started,
        "plan_sha256": sha(PLAN_PATH),
        "frozen_sha256": sha(BASE / "frozen-before-validation.json"),
    }
    write(BASE / "report.json", report)
    print(json.dumps({"complete": True, "family_passes": family_passes, "seconds": report["seconds"]}), flush=True)


if __name__ == "__main__":
    main()
