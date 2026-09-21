"""Read-only Cascadeur API capability probe for the frozen comparison assets.

Run from Cascadeur's embedded Python console with::

    exec(compile(open('X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github/training/b4artists_ml/cascadeur_capability_probe_console_v1.py', encoding='utf-8').read(), '<b4ml-cascadeur-capability-probe>', 'exec'))
    run()

The probe records the installed session's exposed application, FBX, rigging,
and settings surfaces. It imports the three frozen FBX files into disposable
application scenes, records behaviour counts and removes those scenes. It does
not invoke rig conversion, change settings, save scenes, export files, or
modify the frozen assets or B4Artists.
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
OUT = TRAIN / "results" / "cascadeur-capability-probe-v1.json"


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _error(exc):
    return type(exc).__name__ + ": " + str(exc)


def _public_names(value):
    try:
        return sorted(name for name in dir(value) if not name.startswith("_"))
    except Exception as exc:
        return {"error": _error(exc)}


def _safe_call(callback):
    try:
        return {"ok": True, "value": callback()}
    except Exception as exc:
        return {"ok": False, "error": _error(exc)}


def _json_value(value):
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    return str(value)


def _version_probe(csc):
    result = {}
    variables = getattr(csc, "SystemVariables", None)
    if variables is None:
        return result
    for name in ("git_version", "git_sha", "git_count"):
        callback = getattr(variables, name, None)
        if callable(callback):
            value = _safe_call(callback)
            result[name] = (_json_value(value.get("value"))
                            if value.get("ok") else value)
    return result


def _tool_probe(tools_manager, scene, name):
    result = {"name": name, "available": False}
    try:
        tool = tools_manager.get_tool(name)
        result["available"] = tool is not None
        if tool is None:
            return result
        result["type"] = type(tool).__name__
        result["methods"] = _public_names(tool)
        editor_factory = getattr(tool, "editor", None)
        if callable(editor_factory):
            try:
                editor = editor_factory(scene)
                result["editor_type"] = type(editor).__name__
                result["editor_methods"] = _public_names(editor)
            except Exception as exc:
                result["editor_error"] = _error(exc)
    except Exception as exc:
        result["error"] = _error(exc)
    return result


def _behaviour_count(viewer, name):
    try:
        return len(viewer.get_behaviours(name))
    except Exception as exc:
        return {"error": _error(exc)}


def command_name():
    return "B4ML.CascadeurCapabilityProbe"


def run(scene=None):
    import csc

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    app = csc.app.get_application()
    if app is None:
        raise RuntimeError("Cascadeur application is not available in this console")

    scene_manager = app.get_scene_manager()
    tools_manager = app.get_tools_manager()
    current_scene = app.current_scene()
    tool_names = (
        "FbxSceneLoader",
        "RiggingModeTool",
        "RiggingToolWindowTool",
        "AnimationTool",
        "InbetweeningTool",
        "AutoPhysicsTool",
    )
    tool_diagnostics = [
        _tool_probe(tools_manager, current_scene, name) for name in tool_names
    ]
    setting_manager = _safe_call(app.get_setting_manager)
    settings_surface = {
        "available": setting_manager.get("ok") is True,
        "type": (type(setting_manager.get("value")).__name__
                 if setting_manager.get("ok") else None),
        "methods": (_public_names(setting_manager.get("value"))
                    if setting_manager.get("ok") else setting_manager),
        "values_exported": False,
    }

    loader_tool = None
    for item in tool_diagnostics:
        if item["name"] == "FbxSceneLoader" and item.get("available"):
            try:
                loader_tool = tools_manager.get_tool("FbxSceneLoader")
            except Exception:
                loader_tool = None
            break

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
            "conversion_attempted": False,
            "standard_rig_converted": False,
        }
        try:
            if loader_tool is None:
                raise RuntimeError("FbxSceneLoader is not available")
            loader = loader_tool.get_fbx_loader(application_scene)
            loader.add_model(str(path))
            viewer = application_scene.domain_scene().model_viewer().behaviour_viewer()
            row.update({
                "imported": True,
                "behaviour_counts": {
                    name: _behaviour_count(viewer, name)
                    for name in (
                        "Joint", "MeshObject", "RigInfo", "TechnicalLinks",
                        "Point", "RigidBody", "AutoPosingLink",
                    )
                },
                "elapsed_seconds": time.perf_counter() - began,
            })
        except Exception as exc:
            row.update({
                "error": _error(exc),
                "elapsed_seconds": time.perf_counter() - began,
            })
        finally:
            scene_manager.remove_application_scene(application_scene)
            row["scene_removed"] = True
        rows.append(row)

    report = {
        "schema": "b4ml-cascadeur-capability-probe-v1",
        "status": "PASS" if all(row["imported"] and row["scene_removed"] for row in rows)
                  else "FAIL",
        "scope": (
            "Read-only Cascadeur API/tool/settings capability probe plus disposable "
            "frozen-FBX import metadata; no rig conversion, settings export, scene "
            "save, animation task, or parity claim."
        ),
        "application_api": _version_probe(csc),
        "tool_diagnostics": tool_diagnostics,
        "settings_surface": settings_surface,
        "assets": rows,
        "all_hashes_match": all(
            row["fbx_sha256"] == row["expected_fbx_sha256"] for row in rows
        ),
        "conversion_attempted": False,
        "standard_rig_converted": False,
        "settings_exported": False,
        "parity_verified": False,
        "surpasses_verified": False,
        "full_goal_complete": False,
    }
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, allow_nan=False))
    return report


def run_with_diagnostic(scene=None):
    """Run the probe and persist a fail-closed receipt on early API errors."""
    try:
        return run(scene)
    except Exception as exc:
        report = {
            "schema": "b4ml-cascadeur-capability-probe-v1",
            "status": "ERROR",
            "scope": (
                "Read-only Cascadeur API/tool/settings capability probe; the probe "
                "failed before a complete report was produced."
            ),
            "error": _error(exc),
            "conversion_attempted": False,
            "standard_rig_converted": False,
            "settings_exported": False,
            "parity_verified": False,
            "surpasses_verified": False,
            "full_goal_complete": False,
        }
        OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n",
                       encoding="utf-8")
        print(json.dumps(report, indent=2, allow_nan=False))
        return report
