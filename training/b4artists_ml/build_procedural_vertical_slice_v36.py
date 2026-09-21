"""Run v36 through v35 and add cadence/speed evidence gates."""
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v36.json"
ADAPTER = TRAIN / "build_procedural_vertical_slice_v35.py"


def load_adapter():
    spec = importlib.util.spec_from_file_location("b4ml_v35_adapter_for_v36", ADAPTER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.HERE = HERE
    module.PROTOCOL = PROTOCOL
    return module


def engine(module):
    while hasattr(module, "load_adapter"):
        module = module.load_adapter()
    return module.load_engine()


def write(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def patch_case(path, task_name):
    value = json.loads(path.read_text(encoding="utf-8"))
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    value["v35_adapter_schema"] = value["schema"]
    value["schema"] = "procedural-vertical-slice-case-v36"
    if task_name == "run":
        task = protocol["tasks"]["run"]
        poses = task["poses"]
        fps = 30.0
        duration = (float(poses[-1]["frame"]) - float(poses[0]["frame"])) / fps
        distance = abs(float(poses[-1]["pelvis"][1]) - float(poses[0]["pelvis"][1]))
        speed = distance / duration
        starts = [float(row[1]) for row in task["contacts"]]
        intervals = [after - before for before, after in zip(starts, starts[1:])]
        cadence = 60.0 * fps / (sum(intervals) / len(intervals))
        timeline = float(poses[-1]["frame"]) - float(poses[0]["frame"]) + 1.0
        flight_fraction = sum(float(end) - float(start) for start, end in task["flights"]) / timeline
        gate = protocol["run_mechanics_gate"]
        passed = (
            gate["minimum_forward_speed_body_per_second"] <= speed <= gate["maximum_forward_speed_body_per_second"]
            and gate["minimum_step_cadence_per_minute"] <= cadence <= gate["maximum_step_cadence_per_minute"]
            and gate["minimum_flight_fraction"] <= flight_fraction <= gate["maximum_flight_fraction"]
        )
        value["run_mechanics"] = {
            "forward_speed_body_per_second": speed,
            "step_cadence_per_minute": cadence,
            "flight_fraction": flight_fraction,
            "contact_starts": starts,
        }
        value["automated_gates"]["review_run_mechanics"] = passed
    value["complete"] = all(value["automated_gates"].values())
    write(path, value)


def main():
    adapter = load_adapter()
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
        adapter.main()
        path = engine(adapter).BASE / args[0] / args[1] / "report.json"
        patch_case(path, args[1])
    else:
        adapter.main()
        path = engine(adapter).BASE / "summary.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["v35_adapter_schema"] = value["schema"]
        value["schema"] = "procedural-vertical-slice-summary-v36"
        value["source_human_review_schema"] = "b4ml-human-review-summary-v8"
        value["training_authorized"] = False
        value["model_promotion_authorized"] = False
        write(path, value)


if __name__ == "__main__":
    main()
