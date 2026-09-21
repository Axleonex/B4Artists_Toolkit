"""Train the prospectively fixed complete-priority diffusion comparison."""
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

import train_full_hierarchy_tcn_v1 as engine
import train_full_hierarchy_tcn_v2 as data_v2
from full_hierarchy_diffusion_v1 import (
    DIFFUSION_STEPS, ConditionalResidualDiffusionUNet, ddim_sample, q_sample,
)
from full_hierarchy_sequence_dataset_v2 import load_priority_specs
from full_hierarchy_torch_kinematics_v1 import motion_loss
from full_hierarchy_store_v1 import FullHierarchyStore


PLAN_PATH = ROOT / "full_hierarchy_diffusion_training_plan_v1.json"
CACHE = ROOT / "cache-expanded-v1/full-hierarchy-diffusion-v1"
RESULTS = ROOT / "results/full-hierarchy-diffusion-v1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_plan():
    plan = json.loads(PLAN_PATH.read_text())
    paths = {
        "trainer": Path(__file__).resolve(),
        "data_engine": ROOT / "train_full_hierarchy_tcn_v2.py",
        "batch_engine": ROOT / "train_full_hierarchy_tcn_v1.py",
        "model": ROOT / "full_hierarchy_diffusion_v1.py",
        "model_contract": ROOT / "check_full_hierarchy_diffusion_v1.py",
        "microfit": ROOT / "check_full_hierarchy_diffusion_microfit_v1.py",
        "kinematics": ROOT / "full_hierarchy_torch_kinematics_v1.py",
        "dataset": ROOT / "full_hierarchy_sequence_dataset_v2.py",
        "priority_split": ROOT / "results/priority-cohorts-v2/split.json",
        "priority_specs": ROOT / "results/priority-sequence-specs-v2/specs.json",
        "tcn_evaluation": ROOT / "results/full-hierarchy-tcn-v2/evaluation.json",
    }
    actual = {name: sha(path) for name, path in paths.items()}
    if actual != plan["sources"]:
        mismatch = {name: [plan["sources"].get(name), value] for name, value in actual.items()
                    if plan["sources"].get(name) != value}
        raise ValueError("Diffusion plan source mismatch: " + json.dumps(mismatch, sort_keys=True))
    if plan["confirmation_read"] or plan["runtime_promotion_allowed"]:
        raise ValueError("Diffusion training cannot open confirmation or promote runtime")
    return plan


def zero_feature_fields(features, layout, names, dropped):
    for name in names:
        start, end = layout[name]
        features[dropped, :, 141 + int(start):141 + int(end)] = 0


def training_batch(group, indices, device, mode, layout, plan, rng, generator):
    ranges = engine.contact_slices(layout)
    data = engine.batch_to_device(
        group, indices, device, mode, ranges,
        plan["optimization"]["weak_contact_input_dropout"], rng,
    )
    style_drop = rng.random(len(indices)) < plan["optimization"]["style_input_dropout"]
    if np.any(style_drop):
        dropped = torch.as_tensor(style_drop, device=device)
        zero_feature_fields(
            data["features"], layout,
            ("style_weight", "style_known", "style_confidence", "style_provenance_one_hot"),
            dropped,
        )
    clean = (data["target"] - data["baseline"]).masked_fill(data["mask"], 0)
    timestep = torch.randint(0, DIFFUSION_STEPS, (len(indices),), generator=generator, device=device)
    noise = torch.randn(clean.shape, generator=generator, device=device, dtype=clean.dtype)
    noisy, _ = q_sample(clean, data["mask"], timestep, noise)
    return data, clean, noisy, timestep


def objective(model, data, clean, noisy, timestep, plan, parents, semantic):
    prediction = model.predict_clean_residual(noisy, data["features"], data["mask"], timestep)
    hidden = ~data["mask"]
    diffusion = torch.sum((prediction - clean).square() * hidden) / hidden.sum()
    output = model.compose(prediction, data["baseline"], data["mask"])
    motion, terms, _ = motion_loss(
        output, data["target"], data["offsets"], parents, semantic,
        data["dt"], data["contact"], plan["optimization"]["loss_weights"],
    )
    total = diffusion + plan["optimization"]["motion_loss_weight"] * motion
    return total, diffusion, motion, terms


def evaluate(model, prepared, device, plan, layout, parents, semantic):
    model.eval()
    total = 0.0
    count = 0
    ranges = engine.contact_slices(layout)
    with torch.no_grad():
        for gap, group in prepared.items():
            rng = np.random.default_rng(0)
            batch_size = int(plan["optimization"]["batch_size_by_gap"][str(gap)])
            for batch_number, indices in enumerate(engine.batches(group, batch_size, rng, False)):
                data = engine.batch_to_device(
                    group, indices, device, "unknown_contact", ranges, 0.0, rng
                )
                output = ddim_sample(
                    model, data["features"], data["baseline"], data["mask"],
                    plan["optimization"]["selection_ddim_steps"],
                    plan["optimization"]["selection_noise_seed"] + gap * 1000 + batch_number,
                )
                loss, _, _ = motion_loss(
                    output, data["target"], data["offsets"], parents, semantic,
                    data["dt"], data["contact"], plan["optimization"]["loss_weights"],
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
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    model = ConditionalResidualDiffusionUNet(**plan["model"]).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=plan["optimization"]["learning_rate"],
        weight_decay=plan["optimization"]["weight_decay"],
    )
    start_epoch, best_epoch, stale = 0, -1, 0
    best_development = float("inf")
    history = []
    plan_hash = sha(PLAN_PATH)
    if current_path.exists():
        checkpoint = torch.load(current_path, map_location=device, weights_only=False)
        if checkpoint["plan_sha256"] != plan_hash or checkpoint["run_id"] != run_id:
            raise ValueError("Diffusion checkpoint identity mismatch")
        model.load_state_dict(checkpoint["model"])
        optimizer.load_state_dict(checkpoint["optimizer"])
        start_epoch = checkpoint["epoch"] + 1
        best_epoch = checkpoint["best_epoch"]
        best_development = checkpoint["best_development"]
        stale = checkpoint["stale"]
        history = checkpoint["history"]
    maximum = int(plan["optimization"]["maximum_epochs"])
    minimum = int(plan["optimization"]["minimum_epochs"])
    patience = int(plan["optimization"]["early_stopping_patience"])
    minimum_delta = float(plan["optimization"]["minimum_delta"])
    started = time.perf_counter()
    for epoch in range(start_epoch, maximum):
        model.train()
        epoch_total = diffusion_total = motion_total = 0.0
        count = 0
        epoch_started = time.perf_counter()
        for gap, group in training.items():
            rng = np.random.default_rng(seed + epoch * 1009 + gap * 17)
            generator = torch.Generator(device=device).manual_seed(seed + epoch * 100003 + gap)
            batch_size = int(plan["optimization"]["batch_size_by_gap"][str(gap)])
            for indices in engine.batches(group, batch_size, rng, True):
                data, clean, noisy, timestep = training_batch(
                    group, indices, device, mode, layout, plan, rng, generator
                )
                optimizer.zero_grad(set_to_none=True)
                loss, diffusion, motion, _ = objective(
                    model, data, clean, noisy, timestep, plan, parents, semantic
                )
                if not torch.isfinite(loss):
                    raise FloatingPointError("Non-finite diffusion loss")
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), plan["optimization"]["gradient_clip"])
                optimizer.step()
                size = len(indices)
                epoch_total += float(loss.detach().item()) * size
                diffusion_total += float(diffusion.detach().item()) * size
                motion_total += float(motion.detach().item()) * size
                count += size
        development_loss = evaluate(model, development, device, plan, layout, parents, semantic)
        record = {
            "epoch": epoch,
            "training_loss": epoch_total / count,
            "training_diffusion_loss": diffusion_total / count,
            "training_motion_loss": motion_total / count,
            "development_motion_loss_4_step": development_loss,
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
            "plan_sha256": plan_hash, "run_id": run_id, "epoch": epoch,
            "model": model.state_dict(), "optimizer": optimizer.state_dict(),
            "best_epoch": best_epoch, "best_development": best_development,
            "stale": stale, "history": history,
        }
        temporary = current_path.with_suffix(".tmp")
        torch.save(checkpoint, temporary)
        os.replace(temporary, current_path)
        engine.write_json(report_path, {
            "complete": False, "run_id": run_id, "mode": mode, "seed": seed,
            "plan_sha256": plan_hash, "best_epoch": best_epoch,
            "best_development_loss": best_development, "history": history,
            "confirmation_read": False, "runtime_promoted": False,
        })
        print(json.dumps({"stage": "diffusion-epoch", "run": run_id, **record,
                          "best_epoch": best_epoch, "stale": stale}), flush=True)
        if epoch + 1 >= minimum and stale >= patience:
            break
    if not best_path.exists():
        raise RuntimeError("Diffusion training completed without a best checkpoint")
    report = {
        "complete": True, "run_id": run_id, "mode": mode, "seed": seed,
        "device": str(device),
        "device_name": torch.cuda.get_device_name(0) if device.type == "cuda" else "CPU",
        "torch": torch.__version__, "plan_sha256": plan_hash,
        "epochs": len(history), "best_epoch": best_epoch,
        "best_development_loss": best_development,
        "elapsed_seconds_this_invocation": time.perf_counter() - started,
        "history": history,
        "checkpoint": str(best_path.relative_to(ROOT)).replace("\\", "/"),
        "checkpoint_sha256": sha(best_path),
        "confirmation_read": False, "runtime_promoted": False,
        "quality_qualified": False,
    }
    engine.write_json(report_path, report)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    plan = verify_plan()
    split = json.loads((ROOT / "results/priority-cohorts-v2/split.json").read_text())
    labels = json.loads((ROOT / "motion_label_proposals_plan_v1.json").read_text())
    training_specs, development_specs = load_priority_specs(ROOT)
    if args.verify_only:
        print(json.dumps({"passed": True, "plan_sha256": sha(PLAN_PATH),
                          "training_specs": len(training_specs),
                          "development_specs": len(development_specs),
                          "confirmation_read": False}), flush=True)
        return
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if plan["environment"]["cuda_required"] and device.type != "cuda":
        raise RuntimeError("Diffusion plan requires qualified CUDA")
    training, layout, train_seconds = data_v2.materialize(
        training_specs, "training", split, labels, True
    )
    development, dev_layout, dev_seconds = data_v2.materialize(
        development_specs, "development", split, labels, False
    )
    if layout != dev_layout:
        raise ValueError("Diffusion conditioning layouts differ")
    store = FullHierarchyStore(ROOT)
    reports = []
    for mode in plan["contact_modes"]:
        for seed in plan["seeds"]:
            reports.append(train_run(
                mode, int(seed), training, development, layout, plan, device,
                store.parents, store.semantic,
            ))
    engine.write_json(RESULTS / "training-summary.json", {
        "complete": True, "plan_sha256": sha(PLAN_PATH),
        "training_materialization_seconds": train_seconds,
        "development_materialization_seconds": dev_seconds,
        "runs": [{key: report[key] for key in (
            "run_id", "mode", "seed", "epochs", "best_epoch",
            "best_development_loss", "checkpoint_sha256"
        )} for report in reports],
        "confirmation_read": False, "runtime_promoted": False,
        "quality_qualified": False,
    })
    print(json.dumps({"complete": True, "runs": len(reports),
                      "confirmation_read": False, "runtime_promoted": False}, indent=2))


if __name__ == "__main__":
    main()
