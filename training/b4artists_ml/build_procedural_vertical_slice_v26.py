"""Run v26 through the v25/v24/v23 isolated builder chain."""
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v26.json"
ADAPTER = TRAIN / "build_procedural_vertical_slice_v25.py"


def load_adapter():
    spec = importlib.util.spec_from_file_location("b4ml_v25_adapter_for_v26", ADAPTER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.HERE = HERE
    module.PROTOCOL = PROTOCOL
    return module


def update_schema(path, schema):
    value = json.loads(path.read_text(encoding="utf-8"))
    value["v25_adapter_schema"] = value["schema"]
    value["schema"] = schema
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def main():
    adapter = load_adapter()
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
        adapter.main()
        engine = adapter.load_adapter().load_adapter().load_engine()
        update_schema(engine.BASE / args[0] / args[1] / "report.json",
                      "procedural-vertical-slice-case-v26")
    else:
        adapter.main()
        engine = adapter.load_adapter().load_adapter().load_engine()
        update_schema(engine.BASE / "summary.json",
                      "procedural-vertical-slice-summary-v26")


if __name__ == "__main__":
    main()
