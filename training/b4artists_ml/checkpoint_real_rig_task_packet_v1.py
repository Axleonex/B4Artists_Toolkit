"""Bind real-rig packet evidence and source identities into one checkpoint."""
from pathlib import Path
import hashlib
import json
import os


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
RESULTS = ROOT / "training/b4artists_ml/results"
OUT = RESULTS / "real-rig-task-packet-v1.json"


def read(name):
    return json.loads((RESULTS / name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise RuntimeError("Evidence exists: " + str(OUT))
    initial = read("rig-packet-eight-profiles-v1-test_b4artists_ml_rig_observations.json")
    rotation_fix = read("rig-packet-eight-profiles-v2-test_b4artists_ml_rig_observations.json")
    final = read("rig-packet-eight-profiles-v3-test_b4artists_ml_rig_observations.json")
    final_process = read("rig-packet-eight-profiles-v3-regression.json")
    diagnostic = read("real-rig-semantic-kinematics-v1.json")
    if initial["assertions_passed"] or len(initial.get("failures", [])) != 1:
        raise ValueError("Initial numerical failure evidence changed")
    if not rotation_fix["assertions_passed"] or rotation_fix["tests"] != 14:
        raise ValueError("Proper-rotation repair evidence is incomplete")
    if not final["assertions_passed"] or final["tests"] != 15:
        raise ValueError("Final packet evidence is incomplete")
    if len(final_process) != 1 or final_process[0]["suite"] != final["suite"]:
        raise ValueError("Final host-process evidence is incomplete")
    if not diagnostic["complete"] or len(diagnostic["profiles"]) != 8:
        raise ValueError("Eight-profile kinematic diagnostic is incomplete")
    if diagnostic["maximum_rigid_parent_residual_body_scales"] > 2e-4:
        raise ValueError("Semantic fixed-offset reconstruction did not qualify")
    sources = {
        path.relative_to(ROOT).as_posix(): sha(path)
        for path in (
            HERE,
            ROOT / "training/b4artists_ml/rig_observations.py",
            ROOT / "training/b4artists_ml/semantic_hierarchy_packet_v1.py",
            ROOT / "training/b4artists_ml/check_real_rig_semantic_kinematics_v1.py",
            ROOT / "tests/test_b4artists_ml_rig_observations.py",
            ROOT / "tests/test_b4artists_ml_posing.py",
            ROOT / "tests/test_b4artists_ml_imported_humanoids.py",
            ROOT / "b4artists_ml/rigs.py",
            ROOT / "b4artists_ml/body_solver.py",
        )
    }
    report = {
        "complete": True,
        "schema": "real-rig-task-packet-checkpoint-v1",
        "profiles": [row["profile"] for row in diagnostic["profiles"]],
        "profile_count": len(diagnostic["profiles"]),
        "final_assertions": final["tests"],
        "maximum_rigid_parent_residual_body_scales": diagnostic["maximum_rigid_parent_residual_body_scales"],
        "maximum_relative_edge_length_change": diagnostic["maximum_relative_edge_length_change"],
        "initial_failure_preserved": True,
        "proper_rotation_repair_pass": True,
        "semantic_hierarchy_packet_pass": True,
        "host_shutdown_qualified": False,
        "host_exit": final_process[0]["host_exit"],
        "sources": sources,
        "evidence": {
            "initial_failure": "rig-packet-eight-profiles-v1-test_b4artists_ml_rig_observations.json",
            "rotation_repair": "rig-packet-eight-profiles-v2-test_b4artists_ml_rig_observations.json",
            "kinematic_diagnostic": "real-rig-semantic-kinematics-v1.json",
            "final_packet_suite": "rig-packet-eight-profiles-v3-test_b4artists_ml_rig_observations.json",
        },
        "model_trained": False,
        "runtime_promoted": False,
        "confirmation_read": False,
        "full_goal_complete": False,
    }
    temporary = OUT.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, OUT)
    print(json.dumps({
        "complete": True,
        "profiles": report["profile_count"],
        "assertions": report["final_assertions"],
        "maximum_residual": report["maximum_rigid_parent_residual_body_scales"],
        "host_shutdown_qualified": False,
        "runtime_promoted": False,
        "confirmation_read": False,
    }, indent=2))


if __name__ == "__main__":
    main()
