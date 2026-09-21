"""Fixed train-only fits for a learned residual over observed-only shape curves.

SPDX-License-Identifier: GPL-2.0-or-later
The development and confirmation partitions are never read by this script.
"""
from pathlib import Path
import ctypes
import hashlib
import json
import os
import subprocess
import sys
import time
from ctypes import wintypes


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
TR = HERE.parent
BASE = TR / "results/sequence-shape-residual-training-v1"
PLAN_PATH = TR / "sequence_shape_residual_fit_plan_v1.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def rss():
    class Counters(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
            (name, ctypes.c_size_t)
            for name in (
                "PeakWorkingSetSize",
                "WorkingSetSize",
                "QuotaPeakPagedPoolUsage",
                "QuotaPagedPoolUsage",
                "QuotaPeakNonPagedPoolUsage",
                "QuotaNonPagedPoolUsage",
                "PagefileUsage",
                "PeakPagefileUsage",
                "PrivateUsage",
            )
        ]

    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    ctypes.windll.kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    if not ctypes.windll.psapi.GetProcessMemoryInfo(
        ctypes.c_void_p(ctypes.windll.kernel32.GetCurrentProcess()),
        ctypes.byref(counters),
        counters.cb,
    ):
        raise RuntimeError("Process memory measurement unavailable")
    return counters.WorkingSetSize


def reshape_baselines(data):
    import numpy as np

    from sequence_shape_conditioning_v1 import build

    changed = 0
    maximum_change = 0.0
    for bucket in data:
        conditions = bucket["condition"]
        baselines = bucket["baseline"]
        for index in range(len(conditions)):
            condition = conditions[index]
            observed = condition[:, 153:306].reshape(len(condition), 17, 9)
            raw_mask = condition[:, 306:340].reshape(len(condition), 17, 2).astype(bool)
            rest = condition[0, 340:391].reshape(17, 3)
            times = condition[:, 392].astype(np.float64)
            shaped = build(times, observed, raw_mask, rest)["request"]["baseline"].reshape(len(condition), 153)
            difference = float(np.max(np.abs(shaped - baselines[index])))
            maximum_change = max(maximum_change, difference)
            changed += int(difference > 1e-6)
            assert np.array_equal(shaped[bucket["mask"][index]], baselines[index][bucket["mask"][index]])
            baselines[index] = shaped
            conditions[index, :, :153] = shaped
    if not changed or maximum_change <= 1e-6:
        raise AssertionError("Contextual baseline did not change any training window")
    return {"changed_windows": changed, "maximum_abs_change": maximum_change}


def worker(seed):
    sys.path.insert(0, str(TR))
    import numpy as np
    import torch

    from sequence_model_v1 import SequenceModel
    from sequence_numpy_v1 import forward

    plan = json.loads(PLAN_PATH.read_text())
    frozen = json.loads((BASE / "frozen-plan.json").read_text())
    assert sha(PLAN_PATH) == frozen["plan_sha256"]
    assert all(sha(TR / name) == digest for name, digest in plan["sources"].items())
    assert seed in plan["training"]["seeds"]
    manifest_path = TR / "results/sequence-corpus-v2/manifest.json"
    manifest = json.loads(manifest_path.read_text())
    assert sha(manifest_path) == plan["frozen_manifest_sha256"]
    assert manifest["complete"] and not manifest["validation_read"] and not manifest["confirmation_read"]
    contract = json.loads((TR / plan["baseline_contract"]["path"]).read_text())
    assert sha(TR / plan["baseline_contract"]["path"]) == plan["baseline_contract"]["sha256"]
    assert contract["complete"] and contract["contracts"] == 7
    out = BASE / ("direct-" + str(seed))
    out.mkdir(exist_ok=False)
    data = []
    load_started = time.perf_counter()
    read_bytes = 0
    for row in manifest["files"]:
        path = ROOT / row["path"]
        assert sha(path) == row["sha256"]
        with np.load(path, allow_pickle=False) as archive:
            arrays = {name: archive[name].copy() for name in archive.files}
        assert all(np.isfinite(value).all() for value in arrays.values())
        assert arrays["condition"].shape[0] == row["windows"]
        assert np.array_equal(arrays["target"][arrays["mask"]], arrays["baseline"][arrays["mask"]])
        read_bytes += sum(value.nbytes for value in arrays.values())
        data.append(arrays)
    assert read_bytes == manifest["array_bytes"] and read_bytes < 3221225472 and rss() < 4 * 1024**3
    transform_started = time.perf_counter()
    transform = reshape_baselines(data)
    transform["seconds"] = time.perf_counter() - transform_started
    assert all(np.array_equal(bucket["target"][bucket["mask"]], bucket["baseline"][bucket["mask"]]) for bucket in data)
    assert rss() < 4 * 1024**3
    protected = json.loads((TR / "temporal_expansion_plan_v19.json").read_text())["planned_splits"]["confirmation"]
    assert all(not (TR / "cache" / (name + ".bvh")).exists() for name in protected)

    torch.set_num_threads(4)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.cuda.set_per_process_memory_fraction(0.25)
    model = SequenceModel().cuda()
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.0003, weight_decay=0.0001)
    rng = np.random.default_rng(seed)
    history = []
    maximum_rss = rss()
    begin = time.perf_counter()
    status = "running"
    report = {
        "kind": "direct_shape_residual",
        "seed": seed,
        "complete": False,
        "quality_qualified": False,
        "manifest_sha256": sha(manifest_path),
        "plan_sha256": sha(PLAN_PATH),
        "script_sha256": sha(HERE),
        "windows": manifest["window_count"],
        "clip_count": manifest["clip_count"],
        "loaded_array_bytes": read_bytes,
        "load_seconds": transform_started - load_started,
        "baseline_transform": transform,
        "history": history,
        "python": sys.version,
        "torch": torch.__version__,
        "numpy": np.__version__,
        "source_sha256": {name: sha(TR / name) for name in plan["sources"]},
        "validation_read": False,
        "confirmation_read": False,
        "full_goal_complete": False,
    }

    def objective(prediction, base, target, mask, dt):
        error = (base + prediction.masked_fill(mask, 0) - target).reshape(*prediction.shape[:2], 17, 9)
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
        for epoch in range(plan["training"]["epochs"]):
            batches = []
            for bucket_index, bucket in enumerate(data):
                indices = rng.permutation(len(bucket["condition"]))
                batches.extend(
                    (bucket_index, indices[start : start + 16])
                    for start in range(0, len(indices), 16)
                )
            rng.shuffle(batches)
            total = 0.0
            examples = 0
            for bucket_index, ids in batches:
                if time.perf_counter() - begin >= plan["training"]["maximum_seconds_each"]:
                    raise TimeoutError("Fixed training budget reached")
                if time.time() >= plan["deadline_unix"]:
                    raise TimeoutError("Goal deadline reached")
                bucket = data[bucket_index]
                condition = torch.tensor(bucket["condition"][ids], device="cuda")
                base = torch.tensor(bucket["baseline"][ids], device="cuda")
                target = torch.tensor(bucket["target"][ids], device="cuda")
                mask = torch.tensor(bucket["mask"][ids], device="cuda")
                dt = torch.tensor(bucket["dt"][ids], device="cuda")
                optimizer.zero_grad(set_to_none=True)
                prediction = model(
                    condition,
                    torch.zeros_like(target),
                    torch.zeros(len(ids), device="cuda"),
                )
                loss = objective(prediction, base, target, mask, dt)
                assert torch.isfinite(loss)
                loss.backward()
                norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                assert torch.isfinite(norm)
                optimizer.step()
                total += float(loss.detach()) * len(ids)
                examples += len(ids)
            maximum_rss = max(maximum_rss, rss())
            assert maximum_rss < 4 * 1024**3 and examples == manifest["window_count"]
            row = {
                "epoch": epoch + 1,
                "mean_training_loss": total / examples,
                "seconds": time.perf_counter() - begin,
                "examples": examples,
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
            completed_epochs=len(history),
            weights=path.relative_to(ROOT).as_posix(),
            weights_sha256=sha(path),
            weight_bytes=path.stat().st_size,
            training_seconds=time.perf_counter() - begin,
            peak_cuda_bytes=torch.cuda.max_memory_allocated(),
            peak_observed_rss=maximum_rss,
        )
        assert all(not (TR / "cache" / (name + ".bvh")).exists() for name in protected)
        if status == "complete":
            model.eval().cpu()
            bucket = data[-1]
            condition = bucket["condition"][:1]
            noise = np.random.default_rng(seed).normal(size=(1, condition.shape[1], 153)).astype(np.float32)
            level = np.array([0.5], dtype=np.float32)
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
            "plan_sha256": sha(PLAN_PATH),
            "script_sha256": sha(HERE),
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
                {
                    "pid": process.pid,
                    "kind": "direct_shape_residual",
                    "seed": seed,
                    "started_at": time.time(),
                    "log": log.relative_to(ROOT).as_posix(),
                },
            )
            try:
                code = process.wait(timeout=2460)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=30)
                raise
        row = {
            "kind": "direct_shape_residual",
            "seed": seed,
            "exit_code": code,
            "seconds": time.perf_counter() - started,
            "log_sha256": sha(log),
        }
        rows.append(row)
        write(BASE / "processes.json", rows)
        print(json.dumps(row), flush=True)
        if code:
            raise SystemExit(code)
    write(BASE / "active-process.json", {"terminal": True, "all_complete": True})
    assert len(rows) == 2


if __name__ == "__main__":
    if "--worker" in sys.argv:
        worker(int(sys.argv[-1]))
    else:
        main()
