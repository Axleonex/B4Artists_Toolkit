"""Read-only probe for generated Rigify quadruped pole-toggle bindings."""
from pathlib import Path
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]

import addon_utils
import bpy

import b4artists_ml
from b4artists_ml import quadruped_pose
from test_b4artists_ml_quadruped_pose import _generate


addon_utils.enable("rigify", default_set=True, persistent=False)
b4artists_ml.register()

records = []
for kind in ("cat", "horse", "wolf"):
    scene, obj = _generate(kind, normalize_rotation_modes=False)
    rig_id = obj.data.get("rig_id", "")
    marker = "pose.rigify_limb_toggle_pole_" + rig_id
    profile, _, limbs = quadruped_pose.binding(obj)
    match_rows = quadruped_pose._pole_match_rows(profile, obj, limbs)
    matches = []
    for text in bpy.data.texts:
        body = text.as_string()
        if marker not in body:
            continue
        lines = body.splitlines()
        for index, line in enumerate(lines):
            if marker in line:
                matches.append({
                    "text": text.name,
                    "line": index + 1,
                    "context": lines[max(0, index - 5):index + 10],
                })
    records.append({
        "profile": kind,
        "rig_id": rig_id,
        "operator": marker,
        "operator_exists": hasattr(bpy.ops.pose, "rigify_limb_toggle_pole_" + rig_id),
        "control_channels": {name: {
            "lock_location": list(obj.pose.bones[name].lock_location),
            "lock_rotation": list(obj.pose.bones[name].lock_rotation),
            "lock_scale": list(obj.pose.bones[name].lock_scale),
            "rotation_mode": obj.pose.bones[name].rotation_mode,
            "constraints": len(obj.pose.bones[name].constraints),
        } for row in match_rows for name in [*row["ctrl_bones"], *row["extra_ctrls"]]},
        "matches": matches,
    })

out = ROOT / "training/b4artists_ml/results/quadruped-pole-operator-probe.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps({"schema": 1, "records": records}, indent=2), encoding="utf-8")
print("B4ML_POLE_OPERATOR_PROBE:", out)
