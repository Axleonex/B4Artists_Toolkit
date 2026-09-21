"""Run v31 through the v30/v29 dense-shaping adapter chain."""
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v31.json"
ADAPTER = TRAIN / "build_procedural_vertical_slice_v30.py"


def load_adapter():
    spec = importlib.util.spec_from_file_location("b4ml_v30_adapter_for_v31", ADAPTER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.HERE = HERE
    module.PROTOCOL = PROTOCOL
    return module


def engine(module):
    while hasattr(module, "load_adapter"):
        module = module.load_adapter()
    return module.load_engine()


def update_schema(path, schema):
    value = json.loads(path.read_text(encoding="utf-8"))
    value["v30_adapter_schema"] = value["schema"]
    value["schema"] = schema
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def main():
    adapter = load_adapter()
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
        adapter.main()
        update_schema(engine(adapter).BASE / args[0] / args[1] / "report.json",
                      "procedural-vertical-slice-case-v31")
    else:
        adapter.main()
        update_schema(engine(adapter).BASE / "summary.json",
                      "procedural-vertical-slice-summary-v31")


if __name__ == "__main__":
    main()
