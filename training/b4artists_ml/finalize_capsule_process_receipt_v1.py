"""Attach the observed host process exit to a completed capsule receipt."""

from pathlib import Path
import argparse
import json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    parser.add_argument("process_exit_code", type=int)
    args = parser.parse_args()

    report = json.loads(args.receipt.read_text(encoding="utf-8"))
    passed = bool(report.get("passed", report.get("result", {}).get("was_successful", False)))
    code = args.process_exit_code
    report["process_exit"] = {
        "code": code,
        "status": (
            "known_shutdown_only"
            if passed and code != 0
            else "clean"
            if passed and code == 0
            else "assertion_or_harness_failure"
        ),
        "interpretation": (
            "Bforartists wrote a passing receipt before the known ucrtbase.dll "
            "access violation during host shutdown."
            if passed and code != 0
            else "No nonzero host exit followed a passing receipt."
            if passed
            else "The receipt does not establish a passing assertion result."
        ),
    }
    args.receipt.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(args.receipt),
        "process_exit_code": code,
        "status": report["process_exit"]["status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
