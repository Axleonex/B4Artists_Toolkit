"""Run the disposable Cascadeur handoff probes from one embedded-console call.

Run from Cascadeur's embedded Python console with::

    exec(compile(open('X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github/training/b4artists_ml/cascadeur_embedded_gate_runner_console_v1.py', encoding='utf-8').read(), '<b4ml-cascadeur-gate-runner>', 'exec'))
    run()

This is a handoff convenience only.  It records the read-only capability
surface, imports the frozen FBX assets, runs the disposable standard-rig
preflight, removes temporary scenes, and records a combined receipt.  It does
not save scenes, export files, change installation files, or claim conversion,
matched animation, parity, or superiority.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import time


ROOT = Path(os.environ.get(
    "B4ML_REPO",
    r"X:\Scripting Attempts\B4Artists_Tools\B4Artists_Anim_Tools_github"))
TRAIN = ROOT / "training" / "b4artists_ml"
OUT = TRAIN / "results" / "cascadeur-embedded-gate-runner-v1.json"
DIAGNOSTIC_OUT = TRAIN / "results" / "cascadeur-embedded-gate-runner-diagnostic-v1.json"
IMPORT_SCRIPT = TRAIN / "cascadeur_import_audit_console_v1.py"
RIG_SCRIPT = TRAIN / "cascadeur_standard_rig_preflight_console_v1.py"
CAPABILITY_SCRIPT = TRAIN / "cascadeur_capability_probe_console_v1.py"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _write(path: Path, report: dict) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n",
                    encoding="utf-8")
    print(json.dumps(report, indent=2, allow_nan=False))
    return report


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load Cascadeur probe: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _missing_csc_report(error: BaseException) -> dict:
    return {
        "schema": "b4ml-cascadeur-embedded-gate-runner-diagnostic-v1",
        "status": "BLOCKED_CSC_UNAVAILABLE",
        "scope": (
            "Embedded-console handoff diagnostic only; the Cascadeur Python API "
            "was unavailable, so no import, preflight, conversion, settings, "
            "animation, or parity claim was attempted."
        ),
        "diagnostic": {
            "missing_module": "csc",
            "exception": type(error).__name__ + ": " + str(error),
            "recommended_surface": "Cascadeur Window menu -> Python console -> Load/Execute",
            "next_step": (
                "Run this file from Cascadeur's embedded Python console, not from "
                "ordinary Windows Python."
            ),
        },
        "claim_boundary": {
            "import_verified": False,
            "conversion_verified": False,
            "standard_rig_converted": False,
            "animation_tested": False,
            "settings_exported": False,
            "parity_verified": False,
            "surpasses_verified": False,
            "full_goal_complete": False,
        },
    }


def run(scene=None):
    began = time.perf_counter()
    try:
        import csc  # noqa: F401  # only available inside Cascadeur
    except ModuleNotFoundError as error:
        if error.name != "csc":
            raise
        return _write(DIAGNOSTIC_OUT, _missing_csc_report(error))

    for path in (IMPORT_SCRIPT, CAPABILITY_SCRIPT, RIG_SCRIPT):
        if not path.is_file():
            raise FileNotFoundError(str(path))

    import_probe = _load_module(IMPORT_SCRIPT, "b4ml_cascadeur_import_probe_v1")
    capability_probe = _load_module(
        CAPABILITY_SCRIPT, "b4ml_cascadeur_capability_probe_v1"
    )
    rig_probe = _load_module(RIG_SCRIPT, "b4ml_cascadeur_standard_rig_probe_v1")
    children = {}
    failures = []

    try:
        children["import_audit"] = import_probe.run()
    except Exception as error:
        failures.append({
            "probe": "import_audit",
            "error": type(error).__name__ + ": " + str(error),
        })
    try:
        children["capability_probe"] = capability_probe.run_with_diagnostic()
    except Exception as error:
        failures.append({
            "probe": "capability_probe",
            "error": type(error).__name__ + ": " + str(error),
        })
    try:
        children["standard_rig_preflight"] = rig_probe.run_with_diagnostic()
    except Exception as error:
        failures.append({
            "probe": "standard_rig_preflight",
            "error": type(error).__name__ + ": " + str(error),
        })

    child_status = {
        name: value.get("status") if isinstance(value, dict) else "INVALID"
        for name, value in children.items()
    }
    complete = (
        not failures and
        child_status.get("import_audit") == "PASS" and
        child_status.get("capability_probe") == "PASS" and
        child_status.get("standard_rig_preflight") == "PASS"
    )
    report = {
        "schema": "b4ml-cascadeur-embedded-gate-runner-v1",
        "status": "PASS" if complete else "FAIL",
        "scope": (
            "Combined disposable Cascadeur import and standard-rig preflight; "
            "no scene save, export, exact-settings capture, matched animation, "
            "conversion-quality, parity, superiority, or full-goal claim."
        ),
        "elapsed_seconds": time.perf_counter() - began,
        "provenance": {
            "runner": {"path": _relative(Path(__file__)), "sha256": _sha256(Path(__file__))},
            "import_probe": {"path": _relative(IMPORT_SCRIPT), "sha256": _sha256(IMPORT_SCRIPT)},
            "capability_probe": {"path": _relative(CAPABILITY_SCRIPT), "sha256": _sha256(CAPABILITY_SCRIPT)},
            "standard_rig_probe": {"path": _relative(RIG_SCRIPT), "sha256": _sha256(RIG_SCRIPT)},
        },
        "child_status": child_status,
        "children": children,
        "failures": failures,
        "conversion_attempted": child_status.get("standard_rig_preflight") == "PASS",
        "conversion_verified": False,
        "standard_rig_converted": False,
        "animation_tested": False,
        "settings_exported": False,
        "parity_verified": False,
        "surpasses_verified": False,
        "full_goal_complete": False,
    }
    result = _write(OUT, report)
    if os.environ.get("B4ML_CASCADEUR_EXIT") == "1":
        import csc
        csc.app.get_application().get_action_manager().call_action("Application.Exit")
    return result
