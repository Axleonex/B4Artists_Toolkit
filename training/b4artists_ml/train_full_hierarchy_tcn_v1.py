"""Train the prospectively frozen full-hierarchy TCN comparison.

PyTorch is training-only.  Runtime promotion and confirmation evaluation are
separate fail-closed stages.
"""
from collections import defaultdict
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys
import time


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import numpy as np
import torch

from full_hierarchy_sequence_dataset_v1 import HierarchySequenceDataset, load_specs
from full_hierarchy_tcn_v1 import INPUT_WIDTH, STATE_WIDTH, MaskedResidualTCN
from full_hierarchy_torch_kinematics_v1 import motion_loss


PLAN_PATH = ROOT / "full_hierarchy_tcn_training_plan_v1.json"
CACHE = ROOT / "cache-expanded-v1/full-hierarchy-tcn-v1"
RESULTS = ROOT / "results/full-hierarchy-tcn-v1"
CONTACT_FIELDS = (
    "contact_probability",
    "contact_known",
    "contact_confidence",
    "contact_provenance_one_hot",
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def verify_plan():
    plan = json.loads(PLAN_PATH.read_text())
    paths = {
        "trainer": Path(__file__).resolve(),
        "model": ROOT / "full_hierarchy_tcn_v1.py",
        "kinematics": ROOT / "full_hierarchy_torch_kinematics_v1.py",
        "dataset": ROOT / "full_hierarchy_sequence_dataset_v1.py",
        "baseline": ROOT / "masked_hierarchy_baseline_v1.py",
        "model_plan": ROOT / "full_hierarchy_model_comparison_plan_v1.json",
        "sequence_plan": ROOT / "full_hierarchy_sequence_specs_plan_v1.json",
        "sequence_specs": ROOT / "results/full-hierarchy-sequence-specs-v1/specs.json",
        "sequence_report": ROOT / "results/full-hierarchy-sequence-specs-v1/report.json",
        "label_plan": ROOT / "motion_label_proposals_plan_v1.json",
        "subject_split": ROOT / "results/hierarchy-cohorts-v1/split.json",
        "loss_diagnostic": ROOT / "diagnose_full_hierarchy_loss_scale_v1.py",
        "microfit": ROOT / "check_full_hierarchy_tcn_microfit_v1.py",
    }
    actual = {name: sha(path) for name, path in paths.items()}
    if actual != plan["sources"]:
        mismatch = {name: [plan["sources"].get(name), value] for name, value in actual.items()
                    if plan["sources"].get(name) != value}
        raise ValueError("Training plan source mismatch: " + json.dumps(mismatch, sort_keys=True))
    if plan["confirmation_read"] or plan["runtime_promotion_allowed"]:
        raise ValueError("Training plan cannot open confirmation or promote runtime")
    return plan


def materialize(specs, split_name, split, labels, weak_contacts):
    """Prepare each fixed-length gap once in RAM for all prospective runs."""
    dataset = HierarchySequenceDataset(
        specs,
        split_name,
        split["training_subjects"],
        labels["thresholds"]["contact"],
        weak_contacts=weak_contacts,
        root=ROOT,
    )
    positions = defaultdict(list)
    for index, spec in enumerate(specs):
        positions[int(spec["gap"])].append(index)
    result = {}
    layout = None
    started = time.perf_counter()
    completed = 0
    for gap in sorted(positions):
        indices = positions[gap]
        frames = gap + 1
        count = len(indices)
        arrays = {
            "features": np.empty((count, frames, INPUT_WIDTH), np.float32),
            "target": np.empty((count, frames, STATE_WIDTH), np.float32),
            "mask": np.empty((count, frames, STATE_WIDTH), bool),
            "offsets": np.empty((count, 23, 3), np.float32),
            "contact": np.empty((count, frames, 2), np.float32),
            "dt": np.empty((count,), np.float32),
        }
        metadata = []
        for destination, source in enumerate(indices):
            example = dataset[source]
            arrays["features"][destination] = example["features"]
            arrays["target"][destination] = example["target"]
            arrays["mask"][destination] = example["authored_mask"]
            arrays["offsets"][destination] = example["offsets"]
            arrays["contact"][destination] = example["contact_weight"]
            arrays["dt"][destination] = example["dt"]
            metadata.append(example["metadata"])
            if layout is None:
                layout = example["conditioning_layout"]
            completed += 1
            if completed % 250 == 0:
                print(json.dumps({"stage": "materialize", "split": split_name,
                                  "completed": completed, "total": len(specs)}), flush=True)
        arrays["metadata"] = metadata
        result[gap] = arrays
    elapsed = time.perf_counter() - started
    return result, layout, elapsed


def contact_slices(layout):
    ranges = []
    for name in CONTACT_FIELDS:
        start, end = layout[name]
        ranges.append((STATE_WIDTH + int(start), STATE_WIDTH + int(end)))
    return tuple(ranges)


def batch_to_device(group, indices, device, mode, ranges, dropout, rng):
    features = np.array(group["features"][indices], copy=True)
    contact = np.array(group["contact"][indices], copy=True)
    if mode == "unknown_contact":
        for start, end in ranges:
            features[:, :, start:end] = 0
        contact[:] = 0
    elif mode == "weak_contact":
        dropped = rng.random(len(indices)) < dropout
        for start, end in ranges:
            features[dropped, :, start:end] = 0
    else:
        raise ValueError("Unknown contact mode")
    tensors = {
        "features": torch.from_numpy(features).to(device),
        "baseline": torch.from_numpy(features[:, :, :STATE_WIDTH].copy()).to(device),
        "target": torch.from_numpy(np.array(group["target"][indices], copy=True)).to(device),
        "mask": torch.from_numpy(np.array(group["mask"][indices], copy=True)).to(device),
        "offsets": torch.from_numpy(np.array(group["offsets"][indices], copy=True)).to(device),
        "contact": torch.from_numpy(contact).to(device),
        "dt": torch.from_numpy(np.array(group["dt"][indices], copy=True)).to(device),
    }
    return tensors


def batches(group, batch_size, rng, shuffle):
    order = np.arange(len(group["features"]))
    if shuffle:
        rng.shuffle(order)
    for start in range(0, len(order), batch_size):
        yield order[start:start + batch_size]


def evaluate(model, prepared, device, plan, ranges, parents, semantic):
    model.eval()
    total = 0.0
    count = 0
    weights = plan["optimization"]["loss_weights"]
    with torch.no_grad():
        for gap, group in prepared.items():
            rng = np.random.default_rng(0)
            batch_size = int(plan["optimization"]["batch_size_by_gap"][str(gap)])
            for indices in batches(group, batch_size, rng, False):
                data = batch_to_device(
                    group, indices, device, "unknown_contact", ranges, 0.0, rng
                )
                output = model(data["features"], data["baseline"], data["mask"])
                loss, _, _ = motion_loss(
                    output, data["target"], data["offsets"], parents, semantic,
                    data["dt"], data["contact"], weights,
                )
                total += float(loss.item()) * len(indices)
                count += len(indices)
    return total / count


def train_run(mode, seed, training, development, layout, plan, device, parents, semantic):
    run_id = f"{mode}-seed-{seed}"
    run_dir = CACHE / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    current_path = run_dir / "current.pt"
    best_path = run_dir / "best.pt"
    report_path = RESULTS / f"{run_id}.json"
    torch.manual_seed(seed)
    np.random.seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    model = MaskedResidualTCN(**plan["model"]).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=plan["optimization"]["learning_rate"],
        weight_decay=plan["optimization"]["weight_decay"],
    )
    start_epoch = 0
    best_epoch = -1
    best_development = float("inf")
    stale = 0
    history = []
    plan_hash = sha(PLAN_PATH)
    if current_path.exists():
        checkpoint = torch.load(current_path, map_location=device, weights_only=False)
        if checkpoint["plan_sha256"] != plan_hash or checkpoint["run_id"] != run_id:
            raise ValueError("Checkpoint identity mismatch")
        model.load_state_dict(checkpoint["model"])
        optimizer.load_state_dict(checkpoint["optimizer"])
        start_epoch = checkpoint["epoch"] + 1
        best_epoch = checkpoint["best_epoch"]
        best_development = checkpoint["best_development"]
        stale = checkpoint["stale"]
        history = checkpoint["history"]
    ranges = contact_slices(layout)
    maximum = int(plan["optimization"]["maximum_epochs"])
    minimum = int(plan["optimization"]["minimum_epochs"])
    patience = int(plan["optimization"]["early_stopping_patience"])
    minimum_delta = float(plan["optimization"]["minimum_delta"])
    started = time.perf_counter()
    for epoch in range(start_epoch, maximum):
        model.train()
        train_total = 0.0
        train_count = 0
        epoch_started = time.perf_counter()
        for gap, group in training.items():
            rng = np.random.default_rng(seed + 1009 * epoch + 17 * gap)
            batch_size = int(plan["optimization"]["batch_size_by_gap"][str(gap)])
            for indices in batches(group, batch_size, rng, True):
                data = batch_to_device(
                    group, indices, device, mode, ranges,
                    plan["optimization"]["weak_contact_input_dropout"], rng,
                )
                optimizer.zero_grad(set_to_none=True)
                output = model(data["features"], data["baseline"], data["mask"])
                loss, _, _ = motion_loss(
                    output, data["target"], data["offsets"], parents, semantic,
                    data["dt"], data["contact"], plan["optimization"]["loss_weights"],
                )
                if not torch.isfinite(loss):
                    raise FloatingPointError("Non-finite training loss")
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), plan["optimization"]["gradient_clip"])
                optimizer.step()
                train_total += float(loss.detach().item()) * len(indices)
                train_count += len(indices)
        development_loss = evaluate(model, development, device, plan, ranges, parents, semantic)
        record = {
            "epoch": epoch,
            "training_loss": train_total / train_count,
            "development_loss": development_loss,
            "seconds": time.perf_counter() - epoch_started,
        }
        history.append(record)
        improved = development_loss < best_development - minimum_delta
        if improved:
            best_development = development_loss
            best_epoch = epoch
            stale = 0
            torch.save({"plan_sha256": plan_hash, "run_id": run_id,
                        "epoch": epoch, "model": model.state_dict()}, best_path)
        else:
            stale += 1
        checkpoint = {
            "plan_sha256": plan_hash,
            "run_id": run_id,
            "epoch": epoch,
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "best_epoch": best_epoch,
            "best_development": best_development,
            "stale": stale,
            "history": history,
        }
        temporary = current_path.with_suffix(".tmp")
        torch.save(checkpoint, temporary)
        os.replace(temporary, current_path)
        write_json(report_path, {
            "complete": False,
            "run_id": run_id,
            "mode": mode,
            "seed": seed,
            "device": str(device),
            "plan_sha256": plan_hash,
            "best_epoch": best_epoch,
            "best_development_loss": best_development,
            "history": history,
            "confirmation_read": False,
            "runtime_promoted": False,
        })
        print(json.dumps({"stage": "epoch", "run": run_id, **record,
                          "best_epoch": best_epoch, "stale": stale}), flush=True)
        if epoch + 1 >= minimum and stale >= patience:
            break
    if not best_path.exists():
        raise RuntimeError("Training completed without a best checkpoint")
    report = {
        "complete": True,
        "run_id": run_id,
        "mode": mode,
        "seed": seed,
        "device": str(device),
        "device_name": torch.cuda.get_device_name(0) if device.type == "cuda" else "CPU",
        "torch": torch.__version__,
        "plan_sha256": plan_hash,
        "epochs": len(history),
        "best_epoch": best_epoch,
        "best_development_loss": best_development,
        "elapsed_seconds_this_invocation": time.perf_counter() - started,
        "history": history,
        "checkpoint": str(best_path.relative_to(ROOT)).replace("\\", "/"),
        "checkpoint_sha256": sha(best_path),
        "confirmation_read": False,
        "runtime_promoted": False,
        "quality_qualified": False,
    }
    write_json(report_path, report)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    plan = verify_plan()
    if INPUT_WIDTH != plan["model_input_width"]:
        raise ValueError("Model input width does not match plan")
    split = json.loads((ROOT / "results/hierarchy-cohorts-v1/split.json").read_text())
    labels = json.loads((ROOT / "motion_label_proposals_plan_v1.json").read_text())
    training_specs, development_specs = load_specs(ROOT)
    if set(item["subject"] for item in training_specs) & set(item["subject"] for item in development_specs):
        raise ValueError("Training/development subject overlap")
    if args.verify_only:
        print(json.dumps({"passed": True, "plan_sha256": sha(PLAN_PATH),
                          "training_specs": len(training_specs),
                          "development_specs": len(development_specs),
                          "confirmation_read": False}), flush=True)
        return
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if plan["environment"]["cuda_required"] and device.type != "cuda":
        raise RuntimeError("The prospective training plan requires qualified CUDA")
    training, layout, train_seconds = materialize(
        training_specs, "training", split, labels, True
    )
    development, development_layout, development_seconds = materialize(
        development_specs, "development", split, labels, False
    )
    if layout != development_layout:
        raise ValueError("Training and development conditioning layouts differ")
    # Hierarchy identity is global and is read from a streamed example source.
    from full_hierarchy_store_v1 import FullHierarchyStore
    store = FullHierarchyStore(ROOT)
    parents = store.parents
    semantic = store.semantic
    reports = []
    for mode in plan["contact_modes"]:
        for seed in plan["seeds"]:
            reports.append(train_run(mode, int(seed), training, development, layout,
                                     plan, device, parents, semantic))
    write_json(RESULTS / "training-summary.json", {
        "complete": True,
        "plan_sha256": sha(PLAN_PATH),
        "training_materialization_seconds": train_seconds,
        "development_materialization_seconds": development_seconds,
        "runs": [{key: report[key] for key in (
            "run_id", "mode", "seed", "epochs", "best_epoch",
            "best_development_loss", "checkpoint_sha256"
        )} for report in reports],
        "development_subjects": len(set(item["subject"] for item in development_specs)),
        "confirmation_read": False,
        "runtime_promoted": False,
        "quality_qualified": False,
    })
    print(json.dumps({"complete": True, "runs": len(reports),
                      "confirmation_read": False, "runtime_promoted": False}, indent=2))


if __name__ == "__main__":
    main()
