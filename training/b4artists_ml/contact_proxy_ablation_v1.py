"""Test the existing contact solver on a private dependency-closed rig copy."""
from pathlib import Path
import json
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]

import bpy
from mathutils import Vector
import b4artists_ml
from b4artists_ml import body_proxy, contacts, posing, workflow
from test_b4artists_ml_contact_suggestions import ContactSuggestionTests


def dense_error(obj, item):
    mapping = {row["id"]: row for row in posing.bindings(obj)[2]}
    row = mapping[item.limb]
    maximum = 0.0
    for index in range(16, 177):
        contacts._frame(bpy.context.scene, index / 16.0)
        reference = max(sum((obj.pose.bones[row["joints"][i + 1]].head - obj.pose.bones[row["joints"][i]].head).length for i in (0, 1)), 1e-8)
        maximum = max(maximum, (contacts._point(obj, row, item.offset) - Vector(item.point)).length / reference)
    return maximum


def main():
    b4artists_ml.register()
    obj, scene, _ = ContactSuggestionTests().prepared("rigify_default")
    contacts.suggest(obj, scene)
    item = obj.b4ml.contacts[0]
    item.review_state = "ACCEPTED"
    item.enabled = True
    input_action = obj.b4ml.candidate_action
    input_signature = contacts._action_signature(obj)
    profile, root, limbs = posing.bindings(obj)
    seeds = set(profile.controls) | {root}
    for row in limbs:
        seeds.update(row["fk"])
        seeds.update(row["joints"])

    proxy = None
    result_action = None
    started = time.perf_counter()
    try:
        prepare_started = time.perf_counter()
        proxy = body_proxy.EvaluationProxy(obj, seeds)
        prepare_ms = (time.perf_counter() - prepare_started) * 1000.0
        proxy_bones = len(proxy.obj.pose.bones)
        # Research-only adaptation: the source anchors were already validated.
        # A production proxy path would pass their immutable validated request
        # into a host-independent core instead of editing this private copy.
        proxy_rest = workflow._rest_signature(proxy.obj)
        for anchor in proxy.obj.b4ml.anchors:
            payload = json.loads(anchor.payload)
            payload["rest"] = proxy_rest
            payload["switches"] = workflow._switches(proxy.obj)
            anchor.payload = json.dumps(payload, allow_nan=False)
        workflow.assign_action(proxy.obj, input_action, workflow._slot(proxy.obj.animation_data))
        proxy.obj.b4ml.candidate_action = input_action
        layer = proxy.scene.view_layers[0]
        solve_started = time.perf_counter()
        with bpy.context.temp_override(scene=proxy.scene, view_layer=layer, object=proxy.obj, active_object=proxy.obj, selected_objects=[proxy.obj], selected_editable_objects=[proxy.obj]):
            correction = contacts.solve(proxy.obj, proxy.scene)
            result_action = proxy.obj.b4ml.candidate_action.copy()
        solve_ms = (time.perf_counter() - solve_started) * 1000.0
    finally:
        if proxy:
            proxy.close()

    assert result_action is not None
    source_unchanged = obj.b4ml.candidate_action == input_action and contacts._action_signature(obj) == input_signature
    workflow.assign_action(obj, result_action, workflow._slot(obj.animation_data))
    obj.b4ml.candidate_action = result_action
    actual_dense_error = dense_error(obj, item)
    report = {
        "schema": 1,
        "passed": source_unchanged and correction["max_after"] < 2e-4 and actual_dense_error < 2e-4,
        "fixture": "rigify_default",
        "full_bones": len(obj.pose.bones),
        "proxy_bones": proxy_bones,
        "prepare_ms": prepare_ms,
        "solve_ms": solve_ms,
        "total_ms": (time.perf_counter() - started) * 1000.0,
        "source_unchanged_before_publish": source_unchanged,
        "proxy_reported_max_after": correction["max_after"],
        "source_dense_1_16_max_after": actual_dense_error,
        "correction": correction,
        "scope": "Existing dense contact algorithm executed on a temporary private scene, then its copied action was validated on the source default-Rigify rig.",
    }
    output = ROOT / "training/b4artists_ml/results/contact-proxy-ablation-v1.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("CONTACT_PROXY_ABLATION: " + json.dumps(report), flush=True)
    bpy.ops.wm.quit_blender()


if __name__ == "__main__":
    main()
