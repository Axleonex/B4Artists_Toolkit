"""Run v35 and apply its evidence-bearing declared-layer priority gate."""
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v35.json"
ADAPTER = TRAIN / "build_procedural_vertical_slice_v34.py"


def load_adapter():
    spec = importlib.util.spec_from_file_location("b4ml_v34_adapter_for_v35", ADAPTER)
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


def patch_case(path):
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    request = protocol["declared_layer_priority_gate"]
    value = json.loads(path.read_text(encoding="utf-8"))
    receipt = value.get("dense_gait_shaping") or {}
    controls = receipt.get("written_controls", [])
    legacy = bool(value["automated_gates"].get("priority"))
    non_arm = (
        isinstance(receipt.get("non_arm_priority_matrix_error"), (int, float))
        and receipt["non_arm_priority_matrix_error"]
        <= protocol["automated_gates"]["priority_matrix_error"]
    )
    bounded = (
        isinstance(receipt.get("minimum_flexion_degrees"), (int, float))
        and isinstance(receipt.get("maximum_flexion_degrees"), (int, float))
        and receipt["minimum_flexion_degrees"] >= request["minimum_flexion_degrees"]
        and receipt["maximum_flexion_degrees"] <= request["maximum_flexion_degrees"]
        and 0 < receipt.get("written_curve_count", 0)
        and len(controls) == len(set(controls)) <= request["maximum_written_controls"]
        and receipt.get("source_action_unchanged") is request["require_source_action_unchanged"]
    )
    value["v34_adapter_schema"] = value["schema"]
    value["schema"] = "procedural-vertical-slice-case-v35"
    value["legacy_priority_including_declared_arm_layer"] = legacy
    value["automated_gates"]["priority"] = non_arm and bounded
    value["automated_gates"]["priority_non_arm_exact"] = non_arm
    value["automated_gates"]["priority_declared_arm_layer"] = bounded
    value["declared_layer_priority"] = dict(
        schema=request["schema"],
        legacy_result=legacy,
        non_arm_exact=non_arm,
        arm_layer_bounded=bounded,
        written_controls=controls,
        gate_relaxed=False,
    )
    value["complete"] = all(value["automated_gates"].values())
    write(path, value)


def main():
    adapter = load_adapter()
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
        adapter.main()
        path = engine(adapter).BASE / args[0] / args[1] / "report.json"
        patch_case(path)
    else:
        adapter.main()
        path = engine(adapter).BASE / "summary.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["v34_adapter_schema"] = value["schema"]
        value["schema"] = "procedural-vertical-slice-summary-v35"
        write(path, value)


if __name__ == "__main__":
    main()
