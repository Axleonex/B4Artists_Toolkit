"""Run v50 through the v49/v47 mechanics-gated chain."""
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v50.json"
ADAPTER = TRAIN / "build_procedural_vertical_slice_v49.py"


def load_adapter():
    spec = importlib.util.spec_from_file_location("b4ml_v49_adapter_for_v50", ADAPTER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.HERE = HERE
    module.PROTOCOL = PROTOCOL
    return module


def engine(module):
    while hasattr(module, "load_adapter"):
        module = module.load_adapter()
    return module.load_engine()


def update(path, schema):
    value = json.loads(path.read_text(encoding="utf-8"))
    value["v49_adapter_schema"] = value["schema"]
    value["schema"] = schema
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def main():
    adapter = load_adapter()
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
        adapter.main()
        update(engine(adapter).BASE / args[0] / args[1] / "report.json",
               "procedural-vertical-slice-case-v50")
    else:
        adapter.main()
        update(engine(adapter).BASE / "summary.json", "procedural-vertical-slice-summary-v50")


if __name__ == "__main__":
    main()
