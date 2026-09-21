"""Build v23 with collision-aware landing impulses and shape-only air keys."""
import importlib.util
import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
TRAIN = ROOT / "training/b4artists_ml"
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v23.json"


def load_engine():
    path = TRAIN / "build_procedural_vertical_slice_v21_repair2.py"
    spec = importlib.util.spec_from_file_location("b4ml_v21_repair2_engine_v23", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.HERE = HERE
    module.PROTOCOL_PATH = PROTOCOL
    module.BASE = ROOT / "training/b4artists_ml/results" / os.environ.get(
        "B4ML_VERTICAL_TAG", "procedural-vertical-slice-v23"
    )
    return module


def patch_report(engine, profile, task_name):
    path = engine.BASE / profile / task_name / "report.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    directed = report["automated_metrics"]["review_directed"]
    flight_report = report["automated_metrics"].get("flight_report") or {}
    transitions = flight_report.get("transitions", [])
    limit = protocol["review_directed_gates"]["flight_transition_velocity_jump_body_per_second"]
    transition_pass = bool(transitions) and all(row["normalized_jump"] <= limit for row in transitions)
    collision_impulse_pass = task_name != "jump" or (
        any(row.get("collision_impulse") for row in transitions if row["landing"])
        and report["automated_gates"].get("penetration", False)
        and report["automated_metrics"].get("contact_report") is not None
    )
    run_range_pass = (
        task_name != "run"
        or directed["coupled_chest_pitch_range_degrees"]
        >= protocol["review_directed_gates"]["run_chest_pitch_range_degrees"]
    )
    report["engine_schema"] = report["schema"]
    report["schema"] = "procedural-vertical-slice-case-v23"
    report["automated_gates"]["review_flight_transition_velocity"] = transition_pass
    report["automated_gates"]["review_contact_impulse_clearance"] = collision_impulse_pass
    report["automated_gates"]["review_run_upper_body_range"] = run_range_pass
    report["complete"] = all(report["automated_gates"].values())
    report["v23_metrics"] = dict(
        maximum_transition_velocity_jump_body_per_second=max(
            (row["normalized_jump"] for row in transitions), default=None),
        maximum_full_impact_jump_body_per_second=max(
            (row.get("normalized_full_jump", row["normalized_jump"]) for row in transitions), default=None),
        collision_impulse_transitions=sum("collision_impulse" in row for row in transitions),
        jump_chest_pitch_range_degrees=(
            directed["coupled_chest_pitch_range_degrees"] if task_name == "jump" else None),
    )
    engine.write(path, report)


def patch_summary(engine):
    path = engine.BASE / "summary.json"
    summary = json.loads(path.read_text(encoding="utf-8"))
    summary["engine_schema"] = summary["schema"]
    summary["schema"] = "procedural-vertical-slice-summary-v23"
    summary["source_human_review_schema"] = "b4ml-human-review-summary-v6"
    summary["preserved_landings"] = ["rigify_default/land", "imported_unity/land"]
    engine.write(path, summary)


def install_flight_protocol(engine, task_name):
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from b4artists_ml import flight

    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    settings = protocol["tasks"][task_name].get("flight_transitions", [])
    original_add = flight.add
    original_solve = flight.solve
    index = 0

    def add(obj, scene):
        nonlocal index
        item = original_add(obj, scene)
        if index < len(settings):
            row = settings[index]
            item.takeoff_blend = float(row["takeoff_blend_frames"])
            item.landing_blend = float(row["landing_blend_frames"])
            item.match_acceleration = bool(row["match_acceleration"])
            item.contact_impulse_strength = float(row.get("contact_impulse_strength", 0.0))
            item.collision_strength = float(row.get("collision_strength", 0.0))
            item.collision_clearance = float(row.get("collision_clearance", 0.0))
        index += 1
        return item

    def solve(obj, scene):
        shape_frames = {
            float(frame)
            for row in settings for frame in row.get("non_priority_shape_frames", [])
        }
        if not shape_frames:
            return original_solve(obj, scene)
        anchors = sorted((float(item.frame), item.payload) for item in obj.b4ml.anchors)
        obj.b4ml.anchors.clear()
        for frame, payload in anchors:
            if frame not in shape_frames:
                item = obj.b4ml.anchors.add(); item.frame = frame; item.payload = payload
        try:
            return original_solve(obj, scene)
        finally:
            obj.b4ml.anchors.clear()
            for frame, payload in anchors:
                item = obj.b4ml.anchors.add(); item.frame = frame; item.payload = payload

    flight.add = add
    flight.solve = solve


def main():
    engine = load_engine()
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
        install_flight_protocol(engine, args[1])
        engine.host(args[0], args[1])
        patch_report(engine, args[0], args[1])
    else:
        engine.main()
        patch_summary(engine)


if __name__ == "__main__":
    main()
