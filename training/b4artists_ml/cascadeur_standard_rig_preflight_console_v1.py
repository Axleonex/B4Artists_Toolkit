"""Disposable Cascadeur standard-rig template preflight.

Run inside Cascadeur's embedded Python console. This imports each frozen FBX
into a disposable application scene, invokes the installed Quick Rigging
template/prototype calls, records behaviour counts, and removes the scene.
It does not save scenes, export files, alter the frozen assets, run animation,
or claim final standard-rig conversion or parity.
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
TEMPLATE = Path(os.environ.get(
    "B4ML_CASCADEUR_QRT_TEMPLATE",
    r"C:\Program Files\Cascadeur\resources\autorig_templates\standard.qrigcasc"))
OUT = TRAIN / "results" / "cascadeur-standard-rig-preflight-v1.json"
DIAGNOSTIC_OUT = TRAIN / "results" / "cascadeur-standard-rig-preflight-diagnostic-v1.json"


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def error(exc):
    return type(exc).__name__ + ": " + str(exc)


def public_names(value):
    try:
        return sorted(name for name in dir(value) if not name.startswith("_"))
    except Exception as exc:
        return {"error": error(exc)}


def safe_call(callback):
    try:
        return {"ok": True, "value": callback()}
    except Exception as exc:
        return {"ok": False, "error": error(exc)}


def _write_report(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n",
                    encoding="utf-8")
    print(json.dumps(report, indent=2, allow_nan=False))
    return report


def _missing_csc_report(exc):
    return {
        "schema": "b4ml-cascadeur-standard-rig-preflight-diagnostic-v1",
        "status": "BLOCKED_CSC_UNAVAILABLE",
        "scope": (
            "Console handoff diagnostic only; the Cascadeur Python API was not "
            "available, so no import, standard-rig, settings, animation, or "
            "parity claim was attempted."
        ),
        "diagnostic": {
            "missing_module": "csc",
            "exception": error(exc),
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
            "import_verified": False,
            "conversion_verified": False,
            "standard_rig_converted": False,
            "animation_tested": False,
            "settings_exported": False,
            "parity_verified": False,
            "full_goal_complete": False,
        },
    }


def behaviour_counts(application_scene):
    viewer = application_scene.domain_scene().model_viewer().behaviour_viewer()
    names = (
        "Joint", "MeshObject", "RigInfo", "TechnicalLinks", "Point",
        "RigidBody", "AutoPosingLink", "ProtoObject", "ProtoCenterOfMass",
    )
    result = {}
    for name in names:
        try:
            result[name] = len(viewer.get_behaviours(name))
        except Exception as exc:
            result[name] = {"error": error(exc)}
    return result


def run(scene=None):
    try:
        import csc
    except ModuleNotFoundError as exc:
        if exc.name != "csc":
            raise
        return _write_report(DIAGNOSTIC_OUT, _missing_csc_report(exc))

    if not MANIFEST.exists():
        raise FileNotFoundError(str(MANIFEST))
    if not TEMPLATE.exists():
        raise FileNotFoundError(str(TEMPLATE))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    app = csc.app.get_application()
    if app is None:
        raise RuntimeError("Cascadeur application is not available in this console")
    scene_manager = app.get_scene_manager()
    tools_manager = app.get_tools_manager()
    rig_window_tool = tools_manager.get_tool("RiggingToolWindowTool")
    rows = []

    for item in manifest["assets"]:
        path = ROOT / item["fbx"]
        began = time.perf_counter()
        row = {
            "id": item["id"],
            "fbx": item["fbx"],
            "fbx_sha256": sha(path),
            "expected_fbx_sha256": item["fbx_sha256"],
            "imported": False,
            "scene_removed": False,
            "template_path": str(TEMPLATE),
            "template_attempted": False,
            "template_call_ok": False,
            "generate_attempted": False,
            "generate_call_ok": False,
            "standard_rig_converted": False,
            "animation_tested": False,
            "parity_verified": False,
        }
        application_scene = None
        try:
            application_scene = scene_manager.create_application_scene()
            loader_tool = tools_manager.get_tool("FbxSceneLoader")
            loader = loader_tool.get_fbx_loader(application_scene)
            loader.add_model(str(path))
            row["imported"] = True
            row["pre_counts"] = behaviour_counts(application_scene)

            editor = rig_window_tool.editor(application_scene)
            row["rigging_window_type"] = type(editor).__name__
            row["rigging_window_methods"] = public_names(editor)
            row["quick_rig_enabled_before"] = safe_call(editor.is_create_qrt)

            row["template_attempted"] = True
            template_result = safe_call(
                lambda: editor.create_from_qrt_by_fileName(str(TEMPLATE)))
            row["template_call_ok"] = template_result["ok"]
            if not template_result["ok"]:
                row["template_error"] = template_result["error"]
            row["post_template_counts"] = behaviour_counts(application_scene)

            row["generate_attempted"] = True
            generate_result = safe_call(editor.generate_rig_elements)
            row["generate_call_ok"] = generate_result["ok"]
            if not generate_result["ok"]:
                row["generate_error"] = generate_result["error"]
            row["post_generate_counts"] = behaviour_counts(application_scene)
            post = row["post_generate_counts"]
            row["prototype_markers_observed"] = any(
                isinstance(post.get(name), int) and post.get(name, 0) > 0
                for name in ("RigInfo", "Point", "ProtoObject", "AutoPosingLink")
            )
        except Exception as exc:
            row["error"] = error(exc)
        finally:
            if application_scene is not None:
                try:
                    scene_manager.remove_application_scene(application_scene)
                    row["scene_removed"] = True
                except Exception as exc:
                    row["scene_remove_error"] = error(exc)
        row["elapsed_seconds"] = time.perf_counter() - began
        rows.append(row)

    report = {
        "schema": "b4ml-cascadeur-standard-rig-preflight-v1",
        "status": "PASS" if all(
            row["imported"] and row["scene_removed"] and
            row["template_call_ok"] and row["generate_call_ok"]
            for row in rows
        ) else "FAIL",
        "scope": (
            "Disposable Quick Rigging template/prototype preflight for frozen "
            "FBX assets; no scene save, export, animation task, final rig "
            "quality, parity, or superiority claim."
        ),
        "template": {
            "path": str(TEMPLATE),
            "sha256": sha(TEMPLATE),
            "bytes": TEMPLATE.stat().st_size,
        },
        "assets": rows,
        "conversion_attempted": True,
        "standard_rig_converted": False,
        "animation_tested": False,
        "settings_exported": False,
        "parity_verified": False,
        "surpasses_verified": False,
        "full_goal_complete": False,
    }
    return _write_report(OUT, report)


def run_with_diagnostic(scene=None):
    try:
        return run(scene)
    except Exception as exc:
        report = {
            "schema": "b4ml-cascadeur-standard-rig-preflight-diagnostic-v1",
            "status": "ERROR",
            "scope": "Disposable standard-rig preflight failed before a complete report.",
            "error": error(exc),
            "preserved_success_receipt": str(OUT.relative_to(ROOT)).replace("\\", "/")
            if OUT.is_file() else None,
            "diagnostic_receipt": str(DIAGNOSTIC_OUT.relative_to(ROOT)).replace("\\", "/"),
            "conversion_attempted": False,
            "standard_rig_converted": False,
            "animation_tested": False,
            "settings_exported": False,
            "parity_verified": False,
            "surpasses_verified": False,
            "full_goal_complete": False,
        }
        return _write_report(DIAGNOSTIC_OUT, report)
