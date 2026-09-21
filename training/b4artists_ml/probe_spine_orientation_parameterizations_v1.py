"""Probe alternative Spine-orientation measurements without changing runtime code.

The distributed-control rows intentionally retain the runtime's existing
distributed-orientation semantics.  The explicit-direct rows are a separate
feasibility probe: they route semantic Spine to a writable mapped control and
leave Spine out of the distributed set so ``apply_fit`` can write it.  Neither
row family changes the runtime or authorizes a package claim.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "training/b4artists_ml/results/spine-orientation-parameterizations-v1.json"


def main() -> None:
    import bpy
    from mathutils import Quaternion

    sys.path[:0] = [str(ROOT), str(ROOT / "tests"), str(ROOT / "training/b4artists_ml")]
    import b4artists_ml
    from b4artists_ml import body_solver as solver, posing, workflow as w
    from test_b4artists_ml_context_rig import ContextRigTests

    b4artists_ml.register()
    fixtures = ContextRigTests()
    ContextRigTests.setUpClass()
    original_supported = solver.SUPPORTED_ORIENTATION_JOINTS
    original_distributed = solver.DISTRIBUTED_ORIENTATION_JOINTS
    original_orientation_bone = solver.orientation_bone
    rows = []

    def run(label: str, measurement: str) -> None:
        ob, source, session, _targets, _mask = fixtures.fixture(label, transformed=True)
        active = session
        try:
            semantic = session.binding["names"][1]
            direct = session.binding["rotations"][
                session.binding["rotations"].index(
                    "spine_fk" if label.startswith("rigify") else semantic
                )
            ]
            if measurement == "deform_output" and label.startswith("rigify"):
                raise ValueError("generated Rigify semantic output bone is not a writable probe control")
            measured = direct if measurement != "deform_output" else semantic
            pb = ob.pose.bones[direct]
            solver._set_quat(pb, solver._quat(pb) @ Quaternion((0.0, 1.0, 0.0), 0.12))
            posing._update(ob)
            wanted = ob.matrix_world.to_quaternion() @ pb.matrix.to_quaternion()
            session.cancel()
            active = solver.Session(ob)
            solver.SUPPORTED_ORIENTATION_JOINTS = tuple(sorted(set(original_supported) | {1}))
            solver.DISTRIBUTED_ORIENTATION_JOINTS = (1, 2, 3)
            if measurement in {"direct_control", "explicit_direct_control", "explicit_direct_control_free_endpoints"}:
                def direct_orientation(binding, index):
                    if index == 1:
                        return direct
                    return original_orientation_bone(binding, index)
                solver.orientation_bone = direct_orientation
            if measurement in {"direct_control_free_endpoints", "explicit_direct_control_free_endpoints"}:
                def direct_orientation(binding, index):
                    if index == 1:
                        return direct
                    return original_orientation_bone(binding, index)
                solver.orientation_bone = direct_orientation
                active.orientations = {}
            if measurement.startswith("explicit_direct_control"):
                solver.DISTRIBUTED_ORIENTATION_JOINTS = original_distributed
            targets = active.world_points(active.baseline)
            mask = np.zeros(17, dtype=bool)
            mask[0] = True
            result = active.solve(
                targets,
                mask,
                learned_influence=0.0,
                iterations=80,
                orientations_world={1: list(wanted)},
            )
            actual = ob.matrix_world.to_quaternion() @ ob.pose.bones[measured].matrix.to_quaternion()
            rows.append({
                "fixture": label,
                "measurement": measurement,
                "semantic_bone": semantic,
                "measured_bone": measured,
                "orientation_error_radians": solver._angle(wanted, actual),
                "pin_error": result["pin_error"],
                "evaluations": result["evaluations"],
                "passed": result["orientation_error_radians"] <= 0.001
                and result["pin_error"] <= 2e-4,
            })
        except Exception as exc:
            rows.append({
                "fixture": label,
                "measurement": measurement,
                "error": f"{type(exc).__name__}: {exc}",
                "passed": False,
            })
        finally:
            try:
                active.cancel()
            except Exception:
                pass
            if ob.as_pointer() in solver._SESSIONS:
                solver._SESSIONS.pop(ob.as_pointer(), None)
            if ob.name in bpy.data.objects:
                bpy.data.objects.remove(ob, do_unlink=True)

    try:
        for label in ("boneforge", "rigify_basic", "rigify_default", "metarig_basic", "metarig_default"):
            for measurement in (
                "deform_output",
                "direct_control",
                "direct_control_free_endpoints",
                "explicit_direct_control",
                "explicit_direct_control_free_endpoints",
            ):
                run(label, measurement)
    finally:
        solver.SUPPORTED_ORIENTATION_JOINTS = original_supported
        solver.DISTRIBUTED_ORIENTATION_JOINTS = original_distributed
        solver.orientation_bone = original_orientation_bone
    payload = {
        "schema": "b4ml-spine-orientation-parameterization-probe-v1",
        "runtime_changed": False,
        "rows": rows,
        "claim_boundary_closed": True,
        "note": "Exploratory monkeypatch only; no runtime capability or package claim.",
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2), flush=True)


if __name__ == "__main__":
    main()
