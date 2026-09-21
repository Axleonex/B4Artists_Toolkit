"""Measure unpinned hierarchy-helper drift at endpoint priority poses."""
from pathlib import Path
import json
import math
import os
import sys


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import numpy as np
import torch

from full_hierarchy_sequence_dataset_v1 import HierarchySequenceDataset, load_specs
from full_hierarchy_tcn_v1 import MaskedResidualTCN
from full_hierarchy_torch_kinematics_v1 import forward_kinematics


LIMIT = 100
OUT = ROOT / "results/full-hierarchy-tcn-v1/priority-helper-diagnosis.json"


def tensor(value, device, dtype=None):
    return torch.as_tensor(np.array(value, copy=True), dtype=dtype, device=device)


def main():
    split = json.loads((ROOT / "results/hierarchy-cohorts-v1/split.json").read_text())
    labels = json.loads((ROOT / "motion_label_proposals_plan_v1.json").read_text())
    _, development = load_specs(ROOT)
    dataset = HierarchySequenceDataset(
        development[:LIMIT], "development", split["training_subjects"],
        labels["thresholds"]["contact"], weak_contacts=False, root=ROOT,
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    results = []
    for report_path in sorted((ROOT / "results/full-hierarchy-tcn-v1").glob("*-seed-*.json")):
        report = json.loads(report_path.read_text())
        checkpoint = torch.load(ROOT / report["checkpoint"], map_location=device, weights_only=False)
        model = MaskedResidualTCN().to(device).eval()
        model.load_state_dict(checkpoint["model"])
        maximum_helper_degrees = 0.0
        maximum_semantic_position = 0.0
        helper_angles = []
        semantic_positions = []
        with torch.no_grad():
            for example in dataset:
                features = tensor(example["features"], device).unsqueeze(0)
                baseline = tensor(example["baseline"], device).unsqueeze(0)
                target = tensor(example["target"], device).unsqueeze(0)
                mask = tensor(example["authored_mask"], device, torch.bool).unsqueeze(0)
                offsets = tensor(example["offsets"], device).unsqueeze(0)
                output = model(features, baseline, mask)
                op, orange = forward_kinematics(output, offsets, example["parents"])
                tp, trange = forward_kinematics(target, offsets, example["parents"])
                helpers = sorted(set(range(23)) - set(int(value) for value in example["semantic"]))
                endpoint_o = orange[:, (0, -1)][:, :, helpers]
                endpoint_t = trange[:, (0, -1)][:, :, helpers]
                relative = torch.matmul(endpoint_o.transpose(-1, -2), endpoint_t)
                cosine = torch.clamp((torch.diagonal(relative, dim1=-2, dim2=-1).sum(-1) - 1) / 2, -1, 1)
                angles = torch.acos(cosine) * (180 / math.pi)
                positions = torch.linalg.vector_norm(
                    op[:, (0, -1)][:, :, example["semantic"]]
                    - tp[:, (0, -1)][:, :, example["semantic"]], dim=-1
                )
                helper_angles.extend(angles.cpu().reshape(-1).tolist())
                semantic_positions.extend(positions.cpu().reshape(-1).tolist())
                maximum_helper_degrees = max(maximum_helper_degrees, float(angles.max().item()))
                maximum_semantic_position = max(maximum_semantic_position, float(positions.max().item()))
        results.append({
            "run_id": report["run_id"],
            "windows": len(dataset),
            "maximum_unpinned_helper_rotation_degrees": maximum_helper_degrees,
            "mean_unpinned_helper_rotation_degrees": float(np.mean(helper_angles)),
            "maximum_endpoint_semantic_position_error_body_scales": maximum_semantic_position,
            "mean_endpoint_semantic_position_error_body_scales": float(np.mean(semantic_positions)),
        })
    assert results and any(item["maximum_endpoint_semantic_position_error_body_scales"] > 1e-6 for item in results)
    report = {
        "passed": True,
        "diagnosis": "Current semantic-only endpoint mask does not preserve complete priority poses.",
        "runs": results,
        "development_windows_read": LIMIT,
        "confirmation_read": False,
        "runtime_promoted": False,
        "current_fits_qualified": False,
    }
    temporary = OUT.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, OUT)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
