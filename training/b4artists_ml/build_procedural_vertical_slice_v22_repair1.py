"""Run v22 repair 1 through the isolated v22 adapter."""
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v22_repair1.json"
ADAPTER = TRAIN / "build_procedural_vertical_slice_v22.py"


def load_adapter():
    spec = importlib.util.spec_from_file_location("b4ml_v22_adapter", ADAPTER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.HERE = HERE
    module.PROTOCOL = PROTOCOL
    return module


def update_schema(path, schema):
    value = json.loads(path.read_text(encoding="utf-8"))
    value["adapter_schema"] = value["schema"]
    value["schema"] = schema
    value["source_human_review_schema"] = "b4ml-human-review-summary-v6"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def main():
    adapter = load_adapter()
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
        adapter.main()
        update_schema(
            adapter.load_engine().BASE / args[0] / args[1] / "report.json",
            "procedural-vertical-slice-case-v22-repair1",
        )
    else:
        adapter.main()
        update_schema(
            adapter.load_engine().BASE / "summary.json",
            "procedural-vertical-slice-summary-v22-repair1",
        )


if __name__ == "__main__":
    main()
