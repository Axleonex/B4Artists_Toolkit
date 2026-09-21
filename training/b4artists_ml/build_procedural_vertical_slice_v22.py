"""Run the v22 repair through the proven v21 repair-2 builder engine.

The adapter supplies v22's frozen protocol and native flight-transition
settings, then rewrites the inherited engine schema before evidence is read by
the parent process.  The v21 builder remains byte-for-byte unchanged.
"""
import importlib.util
import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
TRAIN = ROOT / "training/b4artists_ml"
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v22.json"


def load_engine():
    path = TRAIN / "build_procedural_vertical_slice_v21_repair2.py"
    spec = importlib.util.spec_from_file_location("b4ml_v21_repair2_engine", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.HERE = HERE
    module.PROTOCOL_PATH = PROTOCOL
    module.BASE = ROOT / "training/b4artists_ml/results" / os.environ.get(
        "B4ML_VERTICAL_TAG", "procedural-vertical-slice-v22"
    )
    return module


def patch_report(engine, profile, task_name):
    path = engine.BASE / profile / task_name / "report.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    directed = report["automated_metrics"]["review_directed"]
    transitions = report["automated_metrics"]["flight_report"]["transitions"]
    limit = protocol["review_directed_gates"][
        "flight_transition_velocity_jump_body_per_second"
    ]
    transition_pass = bool(transitions) and all(
        row["normalized_jump"] <= limit for row in transitions
    )
    run_range_pass = (
        task_name != "run"
        or directed["coupled_chest_pitch_range_degrees"]
        >= protocol["review_directed_gates"]["run_chest_pitch_range_degrees"]
    )
    report["engine_schema"] = report["schema"]
    report["schema"] = "procedural-vertical-slice-case-v22"
    report["automated_gates"]["review_flight_transition_velocity"] = transition_pass
    report["automated_gates"]["review_run_upper_body_range"] = run_range_pass
    report["complete"] = all(report["automated_gates"].values())
    report["v22_metrics"] = {
        "maximum_transition_velocity_jump_body_per_second": max(
            (row["normalized_jump"] for row in transitions), default=None
        ),
        "transition_count": len(transitions),
        "run_chest_pitch_range_degrees": (
            directed["coupled_chest_pitch_range_degrees"]
            if task_name == "run"
            else None
        ),
    }
    engine.write(path, report)


def patch_summary(engine):
    path = engine.BASE / "summary.json"
    summary = json.loads(path.read_text(encoding="utf-8"))
    summary["engine_schema"] = summary["schema"]
    summary["schema"] = "procedural-vertical-slice-summary-v22"
    summary["source_human_review_schema"] = "b4ml-human-review-summary-v6"
    summary["preserved_landings"] = ["rigify_default/land", "imported_unity/land"]
    engine.write(path, summary)


def install_flight_transitions(engine, task_name):
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from b4artists_ml import flight

    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    settings = protocol["tasks"][task_name].get("flight_transitions", [])
    original = flight.add
    index = 0

    def add(obj, scene):
        nonlocal index
        item = original(obj, scene)
        if index < len(settings):
            row = settings[index]
            item.takeoff_blend = float(row["takeoff_blend_frames"])
            item.landing_blend = float(row["landing_blend_frames"])
            item.match_acceleration = bool(row["match_acceleration"])
        index += 1
        return item

    flight.add = add


def main():
    engine = load_engine()
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
        install_flight_transitions(engine, args[1])
        engine.host(args[0], args[1])
        patch_report(engine, args[0], args[1])
    else:
        engine.main()
        patch_summary(engine)


if __name__ == "__main__":
    main()
