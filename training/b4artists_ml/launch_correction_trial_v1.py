"""Launch one blind hands-on correction trial in Bforartists."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
ROOT = HERE.parents[2]
REVIEW_DATA = TRAIN / "results/procedural-vertical-slice-reviewer-v2/review-data.json"
TRIAL = TRAIN / "correction_trial_v1.py"
DEFAULT_HOST = Path("X:/5.1.0/bforartists.exe")


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewer", required=True, help="Reviewer name or anonymous code")
    parser.add_argument("--case", required=True, dest="case_id", help="Case ID, for example boneforge/reach")
    parser.add_argument("--side", choices=("A", "B"), required=True, help="Blind candidate side")
    parser.add_argument("--output", type=Path, default=TRAIN / "results/hands-on-correction-trials-v1")
    parser.add_argument("--bforartists", type=Path, default=DEFAULT_HOST)
    parser.add_argument("--dry-run", action="store_true", help="Write configuration without launching Bforartists")
    args = parser.parse_args()
    reviewer = args.reviewer.strip()
    if not reviewer or len(reviewer) > 200:
        raise SystemExit("Reviewer ID must contain 1-200 non-space characters")
    data = read(REVIEW_DATA)
    cases = {case["id"]: case for case in data["cases"]}
    if args.case_id not in cases:
        raise SystemExit("Unknown case ID: " + args.case_id)
    scene = ROOT / cases[args.case_id]["source_blend"]
    if not scene.is_file() or not args.bforartists.is_file():
        raise SystemExit("Review scene or Bforartists executable is unavailable")
    output = args.output.resolve()
    config_dir = output / "configs"
    config_dir.mkdir(parents=True, exist_ok=True)
    opaque = hashlib.sha256((reviewer + ":" + args.case_id + ":" + args.side).encode()).hexdigest()[:16]
    config_path = config_dir / (opaque + ".json")
    config = dict(
        review_data=str(REVIEW_DATA.resolve()), case_id=args.case_id, side=args.side,
        reviewer_id=reviewer, output_directory=str(output), mode="HUMAN",
    )
    temporary = config_path.with_suffix(".tmp")
    temporary.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, config_path)
    command = [
        str(args.bforartists), "--disable-autoexec", str(scene),
        "--python", str(TRIAL), "--", str(config_path),
    ]
    print(json.dumps(dict(
        configured=True, case_id=args.case_id, blind_side=args.side,
        scene=str(scene), config=str(config_path), output=str(output),
        method_identity_disclosed=False, dry_run=args.dry_run,
    )), flush=True)
    if not args.dry_run:
        raise SystemExit(subprocess.call(command, cwd=ROOT))


if __name__ == "__main__":
    main()
