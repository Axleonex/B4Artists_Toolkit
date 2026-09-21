"""Run v29 with dense candidate-only FK gait shaping."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v29.json"
ADAPTER = TRAIN / "build_procedural_vertical_slice_v28.py"


def load_adapter():
    spec = importlib.util.spec_from_file_location("b4ml_v28_adapter_for_v29", ADAPTER)
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


def patch_case(path, shaping):
    value = json.loads(path.read_text(encoding="utf-8"))
    value["v28_adapter_schema"] = value["schema"]
    value["schema"] = "procedural-vertical-slice-case-v29"
    value["dense_gait_shaping"] = shaping
    value["v29_builder_sha256"] = hashlib.sha256(HERE.read_bytes()).hexdigest()
    value["complete"] = all(value["automated_gates"].values())
    write(path, value)


def install_dense_shaping(task_name):
    if task_name != "run":
        return None, lambda: None
    if str(TRAIN.parents[1]) not in sys.path:
        sys.path.insert(0, str(TRAIN.parents[1]))
    from b4artists_ml import contacts, gait_shaping

    request = json.loads(PROTOCOL.read_text(encoding="utf-8"))["dense_gait_shaping"]
    original = contacts.solve
    receipt = {}

    def solve(obj, scene):
        result = original(obj, scene)
        if obj.b4ml.candidate_action is not None and not receipt:
            receipt.update(gait_shaping.apply_dense_arm_swing(
                obj,
                scene,
                first_frame=int(request["first_frame"]),
                last_frame=int(request["last_frame"]),
                cycle_frames=float(request["cycle_frames"]),
                amplitude=float(request["amplitude"]),
                drop=float(request["drop"]),
                outward=float(request["outward"]),
            ))
        return result

    contacts.solve = solve
    return receipt, lambda: setattr(contacts, "solve", original)


def main():
    adapter = load_adapter()
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
        receipt, restore = install_dense_shaping(args[1])
        try:
            adapter.main()
        finally:
            restore()
        path = engine(adapter).BASE / args[0] / args[1] / "report.json"
        patch_case(path, receipt)
    else:
        adapter.main()
        path = engine(adapter).BASE / "summary.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["v28_adapter_schema"] = value["schema"]
        value["schema"] = "procedural-vertical-slice-summary-v29"
        value["source_human_review_schema"] = "b4ml-human-review-summary-v7"
        value["training_authorized"] = False
        value["model_promotion_authorized"] = False
        write(path, value)


if __name__ == "__main__":
    main()
