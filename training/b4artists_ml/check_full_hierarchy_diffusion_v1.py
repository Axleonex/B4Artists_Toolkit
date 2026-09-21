"""Contracts for the distinct full-hierarchy diffusion candidate."""
from pathlib import Path
import json
import sys
import time


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import torch

from full_hierarchy_diffusion_v1 import (
    ConditionalResidualDiffusionUNet, ddim_sample, q_sample,
)
from full_hierarchy_tcn_v1 import INPUT_WIDTH, STATE_WIDTH


def identity_baseline(batch, frames):
    state = torch.zeros(batch, frames, STATE_WIDTH)
    rotation = state[..., 3:].reshape(batch, frames, 23, 6)
    rotation[..., :3] = torch.tensor((1.0, 0.0, 0.0))
    rotation[..., 3:] = torch.tensor((0.0, 1.0, 0.0))
    return state


def main():
    torch.manual_seed(20260914)
    model = ConditionalResidualDiffusionUNet()
    assert model.parameter_count < 8_000_000
    for frames in (9, 17, 33, 65, 97):
        features = torch.randn(2, frames, INPUT_WIDTH)
        baseline = identity_baseline(2, frames)
        mask = torch.zeros_like(baseline, dtype=torch.bool)
        mask[:, (0, -1)] = True
        residual = torch.randn_like(baseline).masked_fill(mask, 0)
        timestep = torch.tensor((0, 99))
        noisy, noise = q_sample(residual, mask, timestep)
        assert torch.count_nonzero(noisy[mask]) == 0 and torch.count_nonzero(noise[mask]) == 0
        clean = model.predict_clean_residual(noisy, features, mask, timestep)
        assert clean.shape == residual.shape and torch.count_nonzero(clean) == 0
        output = model.compose(clean, baseline, mask)
        assert torch.equal(output, baseline) and torch.equal(output[mask], baseline[mask])
    loss = (clean - residual).square().mean()
    loss.backward()
    assert model.output_projection.weight.grad is not None
    assert torch.isfinite(model.output_projection.weight.grad).all()
    assert torch.count_nonzero(model.output_projection.weight.grad) > 0

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device).eval()
    frames = 97
    features = torch.randn(1, frames, INPUT_WIDTH, device=device)
    baseline = identity_baseline(1, frames).to(device)
    mask = torch.zeros_like(baseline, dtype=torch.bool)
    mask[:, (0, -1)] = True
    timings = {}
    with torch.no_grad():
        for steps in (4, 8, 12):
            ddim_sample(model, features, baseline, mask, steps, 20260914)
            if device.type == "cuda":
                torch.cuda.synchronize()
            started = time.perf_counter()
            repeats = 5
            for _ in range(repeats):
                output = ddim_sample(model, features, baseline, mask, steps, 20260914)
            if device.type == "cuda":
                torch.cuda.synchronize()
            timings[str(steps)] = (time.perf_counter() - started) * 1000 / repeats
            assert torch.equal(output, baseline)
            assert torch.equal(output[mask], baseline[mask])
    invalid = 0
    try:
        ddim_sample(model, features, baseline, mask, 5, 1)
    except ValueError:
        invalid += 1
    assert invalid == 1
    print(json.dumps({
        "passed": True,
        "parameters": model.parameter_count,
        "temporal_scales": 4,
        "frames_checked": [9, 17, 33, 65, 97],
        "zero_initialized_equals_procedural_baseline": True,
        "exact_authored_projection": True,
        "finite_gradients": True,
        "warm_training_environment_ddim_ms_97_frames": timings,
        "device": str(device),
        "device_name": torch.cuda.get_device_name(0) if device.type == "cuda" else "CPU",
        "bforartists_latency_qualified": False,
        "runtime_promoted": False,
        "invalid_cases": invalid,
    }, indent=2))


if __name__ == "__main__":
    main()
