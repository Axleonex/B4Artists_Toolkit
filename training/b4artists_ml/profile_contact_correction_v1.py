"""Profile the evaluated default-Rigify contact-correction path.

This is diagnostic evidence only. It does not change solver behavior or lower
the existing geometric acceptance thresholds.
"""
from pathlib import Path
from collections import defaultdict
import json
import os
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]

import bpy
import b4artists_ml
from b4artists_ml import contacts, posing, rig_state, workflow
from test_b4artists_ml_contact_suggestions import ContactSuggestionTests


def percentile(values, fraction):
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(fraction * len(ordered)))]


def main():
    b4artists_ml.register()
    case = ContactSuggestionTests()
    obj, scene, _ = case.prepared("rigify_default")
    suggestion = contacts.suggest(obj, scene)
    assert suggestion["suggestions"] >= 2
    obj.b4ml.contacts[0].review_state = "ACCEPTED"
    obj.b4ml.contacts[0].enabled = True

    calls = defaultdict(lambda: {"calls": 0, "total_ms": 0.0, "max_ms": 0.0})
    originals = []

    def instrument(module, name, label=None):
        original = getattr(module, name)
        originals.append((module, name, original))

        def measured(*args, **kwargs):
            started = time.perf_counter()
            try:
                return original(*args, **kwargs)
            finally:
                elapsed = (time.perf_counter() - started) * 1000.0
                row = calls[label or f"{module.__name__}.{name}"]
                row["calls"] += 1
                row["total_ms"] += elapsed
                row["max_ms"] = max(row["max_ms"], elapsed)

        setattr(module, name, measured)

    for module, names in (
        (contacts, ("_frame", "_solve_limb", "_action_signature", "_flight_intervals", "_point")),
        (posing, ("_update", "bindings", "_check_space", "_check_controls", "_aim", "_write_rotation")),
        (workflow, ("assign_action", "raw_pose", "restore_pose", "_rest_signature", "action_curves", "display_world")),
        (rig_state, ("mode_values", "restore_values")),
    ):
        for name in names:
            instrument(module, name)

    steps = []
    started = time.perf_counter()
    iterator = contacts.correction_steps(obj, scene)
    try:
        while True:
            tick = time.perf_counter()
            try:
                info = next(iterator)
            except StopIteration as stop:
                steps.append({"phase": "Commit result", "frame": None, "elapsed_ms": (time.perf_counter() - tick) * 1000.0})
                correction = stop.value
                break
            steps.append({"phase": info["phase"], "frame": info["frame"], "elapsed_ms": (time.perf_counter() - tick) * 1000.0})
    finally:
        for module, name, original in reversed(originals):
            setattr(module, name, original)

    elapsed_ms = (time.perf_counter() - started) * 1000.0
    durations = [row["elapsed_ms"] for row in steps]
    by_phase = {}
    for phase in sorted({row["phase"] for row in steps}):
        values = [row["elapsed_ms"] for row in steps if row["phase"] == phase]
        by_phase[phase] = {
            "steps": len(values),
            "total_ms": sum(values),
            "median_ms": statistics.median(values),
            "p95_ms": percentile(values, 0.95),
            "max_ms": max(values),
        }
    hot = sorted(
        ({"function": name, **row} for name, row in calls.items()),
        key=lambda row: row["total_ms"],
        reverse=True,
    )
    report = {
        "schema": 1,
        "passed": correction["max_after"] < 2e-4,
        "fixture": "rigify_default",
        "accepted_contacts": correction["contacts"],
        "frames": correction["frames"],
        "validation_frames": correction["validation_frames"],
        "elapsed_ms": elapsed_ms,
        "solver_elapsed_ms": correction["elapsed_ms"],
        "step_p95_ms": percentile(durations, 0.95),
        "step_max_ms": max(durations),
        "by_phase": by_phase,
        "instrumented_calls": hot,
        "steps": steps,
        "correction": correction,
        "scope": "Single generated default-Rigify crouch/recovery candidate with one accepted foot contact; inclusive instrumentation timings overlap by call nesting.",
    }
    output = ROOT / "training/b4artists_ml/results/contact-correction-profile-v1.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("CONTACT_CORRECTION_PROFILE: " + json.dumps(report), flush=True)
    bpy.ops.wm.quit_blender()


if __name__ == "__main__":
    main()
