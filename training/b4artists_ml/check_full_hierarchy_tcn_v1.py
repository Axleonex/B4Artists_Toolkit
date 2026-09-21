"""Torch contracts for the masked full-hierarchy TCN candidate."""
from pathlib import Path
import json
import sys
import time


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import torch

from full_hierarchy_tcn_v1 import INPUT_WIDTH, STATE_WIDTH, MaskedResidualTCN


def main():
    torch.manual_seed(20260909)
    model = MaskedResidualTCN(width=128)
    assert model.parameter_count < 3_000_000
    batch, frames = 2, 97
    features = torch.randn(batch, frames, INPUT_WIDTH)
    baseline = torch.randn(batch, frames, STATE_WIDTH)
    rotation = baseline[..., 3:].reshape(batch, frames, 23, 6)
    rotation[..., :3] = torch.tensor((1.0, 0.0, 0.0))
    rotation[..., 3:] = torch.tensor((0.0, 1.0, 0.0))
    mask = torch.zeros_like(baseline, dtype=torch.bool)
    mask[:, (0, -1)] = True
    output = model(features, baseline, mask)
    assert output.shape == baseline.shape and torch.isfinite(output).all()
    assert torch.equal(output[mask], baseline[mask])
    assert torch.equal(output, baseline)

    loss = (output[:, 1:-1] - torch.randn_like(output[:, 1:-1])).square().mean()
    loss.backward()
    assert model.output_projection.weight.grad is not None
    assert torch.isfinite(model.output_projection.weight.grad).all()
    assert torch.count_nonzero(model.output_projection.weight.grad) > 0

    with torch.no_grad():
        model.output_projection.weight[0, 0, 0] = 0.1
        changed = model(features, baseline, mask)
    assert not torch.equal(changed[:, 1:-1], baseline[:, 1:-1])
    assert torch.equal(changed[mask], baseline[mask])

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device).eval()
    inputs = (features[:1].to(device), baseline[:1].to(device), mask[:1].to(device))
    with torch.no_grad():
        for _ in range(3):
            model(*inputs)
        if device.type == "cuda":
            torch.cuda.synchronize()
        started = time.perf_counter()
        repeats = 20
        for _ in range(repeats):
            model(*inputs)
        if device.type == "cuda":
            torch.cuda.synchronize()
    elapsed = (time.perf_counter() - started) * 1000 / repeats
    result = {
        "passed": True,
        "torch": torch.__version__,
        "device": str(device),
        "device_name": torch.cuda.get_device_name(0) if device.type == "cuda" else "CPU",
        "parameters": model.parameter_count,
        "maximum_frames_checked": frames,
        "exact_initial_zero_residual": True,
        "exact_authored_projection": True,
        "finite_gradients": True,
        "warm_training_environment_inference_ms": elapsed,
        "bforartists_latency_qualified": False,
        "runtime_promoted": False,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
