"""Validate the optional Cascadeur command wrapper without deploying it."""

from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = Path(os.environ.get(
    "B4ML_REPO",
    r"X:\Scripting Attempts\B4Artists_Tools\B4Artists_Anim_Tools_github",
))
TRAIN = ROOT / "training" / "b4artists_ml"
RESULTS = TRAIN / "results"
OUT = RESULTS / "cascadeur-command-wrapper-readiness-v1.json"
COMMAND_ROOT = Path(os.environ.get(
    "B4ML_CASCADEUR_COMMAND_ROOT",
    r"C:\Program Files\Cascadeur\resources\scripts\python\commands",
))

SOURCE_FILES = {
    "package_init": TRAIN / "cascadeur_cli" / "__init__.py",
    "module_init": TRAIN / "cascadeur_cli" / "commands" / "__init__.py",
    "policy": TRAIN / "cascadeur_connector_policy_v1.py",
    "wrapper": TRAIN / "cascadeur_cli" / "commands" / "b4ml_cascadeur_import_audit.py",
}
DESTINATION_RELATIVE = {
    "package_init": Path("cascadeur_cli") / "__init__.py",
    "module_init": Path("cascadeur_cli") / "commands" / "__init__.py",
    "policy": Path("cascadeur_cli") / "commands" / "cascadeur_connector_policy_v1.py",
    "wrapper": Path("cascadeur_cli") / "commands" / "b4ml_cascadeur_import_audit.py",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def wrapper_contract(path: Path) -> dict[str, object]:
    source = path.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(path))
    definitions = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    return {
        "command_name_function": "command_name" in definitions,
        "run_function": "run" in definitions,
        "name_function": "name" in definitions,
        "description_function": "description" in definitions,
        "imports_console_audit": "cascadeur_import_audit_console_v1" in source,
        "imports_connector_policy": "cascadeur_connector_policy_v1" in source,
        "sets_exit_boundary": "B4ML_CASCADEUR_EXIT" in source,
    }


def main() -> dict[str, object]:
    missing_sources = [
        key for key, path in SOURCE_FILES.items()
        if not path.is_file()
    ]
    if missing_sources:
        raise RuntimeError("Missing wrapper source files: " + ", ".join(missing_sources))

    source_report = {
        key: {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
        }
        for key, path in SOURCE_FILES.items()
    }
    contract = wrapper_contract(SOURCE_FILES["wrapper"])
    destination_report = {}
    mismatches = []
    missing_destinations = []
    for key, relative in DESTINATION_RELATIVE.items():
        source = SOURCE_FILES[key]
        destination = COMMAND_ROOT / relative
        row = {
            "path": str(destination),
            "source_sha256": sha256(source),
            "present": destination.is_file(),
        }
        if destination.is_file():
            row["destination_sha256"] = sha256(destination)
            if row["destination_sha256"] != row["source_sha256"]:
                mismatches.append(key)
        else:
            missing_destinations.append(key)
        destination_report[key] = row

    if not COMMAND_ROOT.is_dir():
        status = "DESTINATION_ROOT_MISSING"
    elif mismatches:
        status = "DESTINATION_MISMATCH"
    elif missing_destinations:
        status = "READY_FOR_EXPLICIT_DEPLOYMENT"
    else:
        status = "ALREADY_DEPLOYED"

    contract_valid = all(bool(value) for value in contract.values())
    report = {
        "schema": "b4ml-cascadeur-command-wrapper-readiness-v1",
        "status": status if contract_valid else "SOURCE_CONTRACT_INVALID",
        "scope": (
            "Read-only readiness check for the optional Cascadeur command-module "
            "wrapper. It compares source and destination hashes but never copies, "
            "deletes, or changes Cascadeur files or settings."
        ),
        "destination_root": str(COMMAND_ROOT),
        "source_files": source_report,
        "destination_files": destination_report,
        "missing_destinations": missing_destinations,
        "mismatches": mismatches,
        "wrapper_contract": contract,
        "mutation_performed": False,
        "claims": {
            "wrapper_contract_verified": contract_valid,
            "deployment_verified": status == "ALREADY_DEPLOYED",
            "cascadeur_import_verified": False,
            "conversion_verified": False,
            "parity_verified": False,
            "full_goal_complete": False,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["status"] == "SOURCE_CONTRACT_INVALID":
        raise SystemExit(1)
    return report


if __name__ == "__main__":
    main()
