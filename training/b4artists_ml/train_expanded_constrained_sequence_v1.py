"""Two fixed expanded-data fits with a C2-constrained learned residual.

SPDX-License-Identifier: GPL-2.0-or-later
Train-only research; development and confirmation data are never read.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
TR = HERE.parent
PLAN_PATH = TR / "expanded_constrained_sequence_fit_plan_v1.json"
BASE = TR / "results/expanded-constrained-sequence-training-v1"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def worker(seed):
    sys.path.insert(0, str(TR))
    import numpy as np
    import torch

    from sequence_model_v1 import SequenceModel
    from sequence_numpy_v1 import forward
    from sequence_store_v1 import SequenceStore

    plan = read(PLAN_PATH)
    assert sha256(PLAN_PATH) == read(BASE / "frozen-plan.json")["plan_sha256"]
    assert all(sha256(TR / name) == digest for name, digest in plan["sources"].items())
    assert seed in plan["training"]["seeds"]
    for contract in plan["contracts"]:
        report = read(TR / contract["path"])
        assert sha256(TR / contract["path"]) == contract["sha256"]
        assert report["complete"] and not report["validation_read"] and not report["confirmation_read"]
    acquisition = read(TR / "results/cmu-corpus-inventory-v1/train-download-manifest.json")
    assert acquisition["complete"] and not acquisition["development_motion_downloaded"] and not acquisition["confirmation_motion_downloaded"]
    store = SequenceStore(cache_clips=64)
    assert len(store.entries) == 1840 and len(store.subjects) == 85
    torch.set_num_threads(4)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.cuda.set_per_process_memory_fraction(0.25)
    model = SequenceModel().cuda()
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=plan["training"]["learning_rate"],
        weight_decay=plan["training"]["weight_decay"],
    )
    out = BASE / ("direct-" + str(seed))
    out.mkdir(exist_ok=False)
    history = []
    started = time.perf_counter()
    examples = 0
    status = "running"
    gaps = plan["training"]["gaps"]
    report = {
        "kind": "expanded_direct_c2",
        "seed": seed,
        "complete": False,
        "quality_qualified": False,
        "plan_sha256": sha256(PLAN_PATH),
        "script_sha256": sha256(HERE),
        "clips": len(store.entries),
        "subjects": len(store.subjects),
        "source_hours": store.report["source_hours"],
        "history": history,
        "python": sys.version,
        "torch": torch.__version__,
        "numpy": np.__version__,
        "validation_read": False,
        "confirmation_read": False,
        "full_goal_complete": False,
    }

    def objective(prediction, base, target, mask, dt):
        error = (base + prediction - target).reshape(*prediction.shape[:2], 17, 9)
        unknown = (~mask).reshape(error.shape)
        position = (error[..., :3].square() * unknown[..., :3]).sum() / unknown[..., :3].sum().clamp_min(1)
        rotation = (error[..., 3:].square() * unknown[..., 3:]).sum() / unknown[..., 3:].sum().clamp_min(1)
        velocity = (error[:, 1:] - error[:, :-1]) / dt[:, None, None, None]
        velocity_mask = unknown[:, 1:] | unknown[:, :-1]
        velocity_loss = (velocity.square() * velocity_mask).sum() / velocity_mask.sum().clamp_min(1)
        acceleration = (error[:, 2:] - 2 * error[:, 1:-1] + error[:, :-2]) / dt[:, None, None, None].square()
        acceleration_mask = unknown[:, 2:] | unknown[:, 1:-1] | unknown[:, :-2]
        acceleration_loss = (acceleration.square() * acceleration_mask).sum() / acceleration_mask.sum().clamp_min(1)
        return position + 0.1 * rotation + 0.01 * velocity_loss + 0.0001 * acceleration_loss

    try:
        for step in range(plan["training"]["steps"]):
            if time.perf_counter() - started >= plan["training"]["maximum_seconds_each"]:
                raise TimeoutError("Fixed training time cap reached")
            if time.time() >= plan["deadline_unix"]:
                raise TimeoutError("Goal deadline reached")
            gap = gaps[step % len(gaps)]
            context = bool((step // len(gaps)) % 2)
            batch = store.sample_batch(
                plan["training"]["batch_size"],
                gap=gap,
                context=context,
                seed=seed * 100000 + step,
                constrained=True,
            )
            condition = torch.tensor(batch["condition"], device="cuda")
            base = torch.tensor(batch["baseline"], device="cuda")
            target = torch.tensor(batch["target"], device="cuda")
            mask = torch.tensor(batch["mask"], device="cuda")
            envelope = torch.tensor(batch["envelope"], device="cuda")
            dt = torch.tensor(batch["dt"], device="cuda")
            optimizer.zero_grad(set_to_none=True)
            raw = model(
                condition,
                torch.zeros_like(target),
                torch.zeros(len(target), device="cuda"),
            )
            prediction = raw * envelope
            loss = objective(prediction, base, target, mask, dt)
            assert torch.isfinite(loss)
            loss.backward()
            norm = torch.nn.utils.clip_grad_norm_(model.parameters(), plan["training"]["gradient_clip"])
            assert torch.isfinite(norm)
            optimizer.step()
            examples += len(target)
            if (step + 1) % 100 == 0:
                row = {
                    "step": step + 1,
                    "examples": examples,
                    "loss": float(loss.detach()),
                    "seconds": time.perf_counter() - started,
                    "gap": gap,
                    "context": context,
                }
                history.append(row)
                write(out / "progress.json", report)
                print(json.dumps({"seed": seed, **row}), flush=True)
        status = "complete"
        report["complete"] = True
    except BaseException as exc:
        status = "failed"
        report["error"] = repr(exc)
        raise
    finally:
        weights = {name: value.detach().cpu().numpy().copy() for name, value in model.state_dict().items()}
        path = out / ("weights.npz" if status == "complete" else "partial-weights.npz")
        np.savez(path, **weights)
        report.update(
            status=status,
            completed_steps=history[-1]["step"] if history else 0,
            examples=examples,
            weights=path.relative_to(ROOT).as_posix(),
            weights_sha256=sha256(path),
            weight_bytes=path.stat().st_size,
            training_seconds=time.perf_counter() - started,
            peak_cuda_bytes=torch.cuda.max_memory_allocated(),
        )
        if status == "complete":
            model.eval().cpu()
            batch = store.sample_batch(2, gap=32, context=True, seed=seed + 900000, constrained=True)
            condition = batch["condition"]
            noise = np.random.default_rng(seed).normal(size=(2, len(condition[0]), 153)).astype(np.float32)
            level = np.array([0.25, 0.75], dtype=np.float32)
            with torch.no_grad():
                expected = model(
                    torch.from_numpy(condition), torch.from_numpy(noise), torch.from_numpy(level)
                ).numpy()
            actual = forward(weights, condition, noise, level)
            report["cpu_export_max_abs_error"] = float(np.max(np.abs(expected - actual)))
            assert report["cpu_export_max_abs_error"] < 5e-5
        write(out / "report.json", report)


def main():
    BASE.mkdir(exist_ok=False)
    write(
        BASE / "frozen-plan.json",
        {
            "plan_sha256": sha256(PLAN_PATH),
            "script_sha256": sha256(HERE),
            "recorded_at": time.time(),
            "validation_read": False,
            "confirmation_read": False,
        },
    )
    rows = []
    environment = dict(
        os.environ,
        OPENBLAS_NUM_THREADS="4",
        PYTHONDONTWRITEBYTECODE="1",
        CUBLAS_WORKSPACE_CONFIG=":4096:8",
    )
    for seed in (20260909, 20260910):
        log = BASE / ("direct-" + str(seed) + ".log")
        started = time.perf_counter()
        with log.open("w") as output:
            process = subprocess.Popen(
                [
                    "X:/ComfyUI/ComfyUI_windows_portable/python_embeded/python.exe",
                    "-B",
                    str(HERE),
                    "--worker",
                    str(seed),
                ],
                stdout=output,
                stderr=subprocess.STDOUT,
                env=environment,
            )
            write(
                BASE / "active-process.json",
                {"pid": process.pid, "seed": seed, "started_at": time.time(), "log": log.relative_to(ROOT).as_posix()},
            )
            try:
                code = process.wait(timeout=plan_timeout())
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=30)
                raise
        row = {"seed": seed, "exit_code": code, "seconds": time.perf_counter() - started, "log_sha256": sha256(log)}
        rows.append(row)
        write(BASE / "processes.json", rows)
        print(json.dumps(row), flush=True)
        if code:
            raise SystemExit(code)
    write(BASE / "active-process.json", {"terminal": True, "all_complete": True})


def plan_timeout():
    return read(PLAN_PATH)["training"]["process_timeout_seconds"]


if __name__ == "__main__":
    if "--worker" in sys.argv:
        worker(int(sys.argv[-1]))
    else:
        main()
