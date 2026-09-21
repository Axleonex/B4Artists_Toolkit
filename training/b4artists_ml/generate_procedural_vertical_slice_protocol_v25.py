"""Freeze hierarchical run arm follow after v24 isolated world-space IK snap."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v24.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v25.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v25",
        version="25",
        supersedes="procedural_vertical_slice_protocol_v24.json",
        purpose=(
            "Preserve v24's extended symmetric run and seven-degree torso counter-motion, "
            "while removing world-space hand IK targets whose direction reversal produced "
            "forearm acceleration spikes. Arms follow the animated chest hierarchy."
        ),
    )
    for recipe in protocol["full_body_shaping"]["tasks"]["run"].values():
        recipe["limbs"] = {}
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
