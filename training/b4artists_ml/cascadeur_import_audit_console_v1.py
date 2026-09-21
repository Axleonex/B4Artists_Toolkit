"""Cascadeur-console import audit for the frozen comparison FBX assets.

Run from Cascadeur's Python console with::

    exec(compile(open('X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github/training/b4artists_ml/cascadeur_import_audit_console_v1.py', encoding='utf-8').read(), '<b4ml-cascadeur-import-audit>', 'exec'))
    run()

The audit uses disposable Cascadeur application scenes and does not save,
export, modify the source FBX files, or alter B4Artists.
"""

from pathlib import Path
import hashlib
import json
import os
import time


ROOT = Path(os.environ.get(
    "B4ML_REPO",
    r"X:\Scripting Attempts\B4Artists_Tools\B4Artists_Anim_Tools_github"))
TRAIN = ROOT / "training" / "b4artists_ml"
MANIFEST = TRAIN / "reference-assets-v1" / "manifest.json"
OUT = TRAIN / "results" / "cascadeur-import-audit-v1.json"
DIAGNOSTIC_OUT = TRAIN / "results" / "cascadeur-import-audit-diagnostic-v1.json"


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _count_behaviours(viewer, name):
    try:
        values = viewer.get_behaviours(name)
        return len(values)
    except Exception as exc:
        return {"error": type(exc).__name__ + ": " + str(exc)}


def command_name():
    return "B4ML.CascadeurImportAudit"


def _write_report(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, allow_nan=False))
    return report


def _missing_csc_report(error):
    return {
        "schema": "b4ml-cascadeur-import-audit-diagnostic-v1",
        "status": "BLOCKED_CSC_UNAVAILABLE",
        "scope": (
            "Console handoff diagnostic only; the Cascadeur Python API was not "
            "available, so no asset import, conversion, settings, or parity claim "
            "was attempted."
        ),
        "diagnostic": {
            "missing_module": "csc",
            "exception": type(error).__name__ + ": " + str(error),
            "recommended_surface": "Cascadeur Window menu -> Python console -> Load/Execute",
            "next_step": (
                "Run this file from Cascadeur's documented Python console or deploy "
                "the project wrapper as a supported Cascadeur command module."
            ),
        },
        "preserved_success_receipt": str(OUT.relative_to(ROOT)).replace("\\", "/")
        if OUT.is_file() else None,
        "diagnostic_receipt": str(DIAGNOSTIC_OUT.relative_to(ROOT)).replace("\\", "/"),
        "claim_boundary": {
            "cascadeur_import_verified": False,
            "conversion_verified": False,
            "parity_verified": False,
            "surpasses_verified": False,
            "full_goal_complete": False,
        },
    }


def run(scene=None):
    try:
        import csc
    except ModuleNotFoundError as error:
        if error.name != "csc":
            raise
        return _write_report(DIAGNOSTIC_OUT, _missing_csc_report(error))

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    app = csc.app.get_application()
    if app is None:
        raise RuntimeError("Cascadeur application is not available in this console")
    scene_manager = app.get_scene_manager()
    tools_manager = app.get_tools_manager()
    loader_tool = tools_manager.get_tool("FbxSceneLoader")
    rows = []
    for item in manifest["assets"]:
        path = ROOT / item["fbx"]
        began = time.perf_counter()
        application_scene = scene_manager.create_application_scene()
        row = {
            "id": item["id"],
            "fbx": item["fbx"],
            "fbx_sha256": sha(path),
            "expected_fbx_sha256": item["fbx_sha256"],
            "imported": False,
            "scene_removed": False,
        }
        try:
            loader = loader_tool.get_fbx_loader(application_scene)
            loader.add_model(str(path))
            viewer = application_scene.domain_scene().model_viewer().behaviour_viewer()
            row.update({
                "imported": True,
                "joint_behaviours": _count_behaviours(viewer, "Joint"),
                "mesh_behaviours": _count_behaviours(viewer, "MeshObject"),
                "rig_info_behaviours": _count_behaviours(viewer, "RigInfo"),
                "elapsed_seconds": time.perf_counter() - began,
            })
        except Exception as exc:
            row.update({
                "error": type(exc).__name__ + ": " + str(exc),
                "elapsed_seconds": time.perf_counter() - began,
            })
        finally:
            scene_manager.remove_application_scene(application_scene)
            row["scene_removed"] = True
        rows.append(row)

    report = {
        "schema": "b4ml-cascadeur-import-audit-v1",
        "status": "PASS" if all(row["imported"] and row["scene_removed"] for row in rows)
                  else "FAIL",
        "scope": "Cascadeur-console disposable FBX import only; no conversion, settings export, entitlement inspection, animation task, or parity claim.",
        "assets": rows,
        "all_hashes_match": all(row["fbx_sha256"] == row["expected_fbx_sha256"] for row in rows),
        "import_conversion_audit": False,
        "edition": None,
        "entitlement": None,
        "settings_exported": False,
        "parity_verified": False,
        "surpasses_verified": False,
        "full_goal_complete": False,
    }
    _write_report(OUT, report)
    if os.environ.get("B4ML_CASCADEUR_EXIT") == "1":
        app.get_action_manager().call_action("Application.Exit")
    return report
