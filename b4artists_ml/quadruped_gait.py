"""Procedural quadruped support-phase review from accepted paw contacts.

This module reads animator-reviewed contact intervals.  It does not infer a
gait from motion, generate animation, or use a learned model.

SPDX-License-Identifier: GPL-2.0-or-later
"""
import hashlib
import json
import math

from . import contact_math as cm
from . import quadruped_contacts as qc
from . import quadruped_pose as qp
from . import workflow as w


BACKEND = "procedural_quadruped_gait_phase_v1"
MAX_PHASES = 128
_LABELS = {
    "FLIGHT": "Flight",
    "SINGLE_SUPPORT": "Single Support",
    "DIAGONAL_SUPPORT": "Diagonal Support",
    "LATERAL_SUPPORT": "Lateral Support",
    "FORE_SUPPORT": "Fore-Paw Support",
    "HIND_SUPPORT": "Hind-Paw Support",
    "TRIPLE_SUPPORT": "Triple Support",
    "FULL_SUPPORT": "Four-Paw Support",
}


def _frame(scene, value=None):
    if value is None:
        return scene.frame_current + scene.frame_subframe
    scene.frame_set(math.floor(value), subframe=value - math.floor(value))


def classify(limbs):
    """Return a conservative support label for a set of semantic paws."""
    support = frozenset(limbs)
    if not support.issubset(qc.LIMBS):
        raise ValueError("Unknown quadruped support limb")
    count = len(support)
    if count == 0:
        return "FLIGHT"
    if count == 1:
        return "SINGLE_SUPPORT"
    if count == 3:
        return "TRIPLE_SUPPORT"
    if count == 4:
        return "FULL_SUPPORT"
    if support in ({"fore-L", "hind-R"}, {"fore-R", "hind-L"}):
        return "DIAGONAL_SUPPORT"
    if support in ({"fore-L", "hind-L"}, {"fore-R", "hind-R"}):
        return "LATERAL_SUPPORT"
    if support == {"fore-L", "fore-R"}:
        return "FORE_SUPPORT"
    if support == {"hind-L", "hind-R"}:
        return "HIND_SUPPORT"
    raise ValueError("Unsupported quadruped support set")


def _contacts_signature(rows):
    payload = [{key: row[key] for key in
                ("limb", "start", "end", "blend", "strength", "point",
                 "rotation", "offset", "lock_rotation")} for row in rows]
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _anchors_signature(obj):
    payload = [(item.frame, item.payload) for item in obj.b4ml.anchors]
    text = json.dumps(payload, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _action_digest(obj, candidate):
    def scalar(value):
        if value is None or isinstance(value, (str, bool, int)):
            return value
        if isinstance(value, float):
            if not math.isfinite(value):
                raise ValueError("Candidate action contains a non-finite setting")
            return value
        if isinstance(value, set):
            return [scalar(item) for item in sorted(value)]
        if isinstance(value, (list, tuple)) or hasattr(value, "to_list"):
            return [scalar(item) for item in value]
        raise TypeError

    def rna_scalars(value):
        if value is None or not hasattr(value, "bl_rna"):
            return []
        result = []
        for definition in value.bl_rna.properties:
            if (definition.identifier == "rna_type" or
                    definition.type in {"POINTER", "COLLECTION"}):
                continue
            try:
                current = getattr(value, definition.identifier)
                if getattr(definition, "is_array", False):
                    current = list(current)
                result.append([definition.identifier, scalar(current)])
            except (AttributeError, ReferenceError, RuntimeError, TypeError):
                continue
        return result

    slot = getattr(obj.animation_data, "action_slot", None)
    curves = w.action_curves(candidate, slot)
    point_count = sum(len(curve.keyframe_points) + len(curve.sampled_points) for curve in curves)
    if point_count > w.MAX_KEYS:
        raise ValueError("Gait-phase source exceeds the editable key budget")
    curve_rows = []
    modifier_count = 0
    envelope_point_count = 0
    for curve in curves:
        modifiers = []
        for modifier in curve.modifiers:
            modifier_count += 1
            if modifier_count > 1024:
                raise ValueError("Gait-phase source exceeds the animation-modifier budget")
            envelope = []
            if modifier.type == "ENVELOPE":
                for point in modifier.control_points:
                    envelope_point_count += 1
                    if envelope_point_count > 4096:
                        raise ValueError("Gait-phase source exceeds the envelope-point budget")
                    envelope.append([scalar(point.frame), scalar(point.min), scalar(point.max)])
            modifiers.append({"settings": rna_scalars(modifier),
                              "envelope_control_points": envelope})
        group = curve.group
        curve_rows.append({
            "data_path": curve.data_path,
            "array_index": curve.array_index,
            "lock": curve.lock,
            "mute": curve.mute,
            "extrapolation": curve.extrapolation,
            "auto_smoothing": getattr(curve, "auto_smoothing", None),
            "group": rna_scalars(group),
            "keys": [[list(key.co), list(key.handle_left), list(key.handle_right),
                      key.handle_left_type, key.handle_right_type, key.interpolation,
                      key.easing, key.amplitude, key.back, key.period, key.type]
                     for key in curve.keyframe_points],
            "samples": [list(point.co) for point in curve.sampled_points],
            "modifiers": modifiers,
        })
    structure = []
    if hasattr(candidate, "layers"):
        for layer in candidate.layers:
            strips = []
            for strip in layer.strips:
                try:
                    bag = strip.channelbag(slot) if slot else None
                except (AttributeError, RuntimeError, TypeError):
                    bag = None
                strips.append({"settings": rna_scalars(strip),
                               "channelbag": rna_scalars(bag)})
            structure.append({"settings": rna_scalars(layer), "strips": strips})
    payload = {
        "action_settings": [[key, scalar(getattr(candidate, key, None))]
                            for key in ("use_frame_range", "frame_start", "frame_end",
                                        "use_cyclic")],
        "animation_settings": [[key, scalar(getattr(obj.animation_data, key, None))]
                               for key in ("action_blend_type", "action_extrapolation",
                                           "action_influence", "use_nla", "action_slot_handle")],
        "slot": rna_scalars(slot),
        "structure": structure,
        "curves": curve_rows,
    }
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _source(obj):
    state = obj.b4ml
    w._reject_nla(obj)
    candidate = state.candidate_action
    if candidate is None or not obj.animation_data or obj.animation_data.action != candidate:
        raise ValueError("Generate and select a quadruped Pose Blending candidate first")
    if w.motion_layer.find(obj):
        raise ValueError("Restore the kept motion source before gait-phase analysis")
    if (state.contact_running or state.contact_suggest_running or state.flight_running or
            state.secondary_running or state.cleanup_running or state.temporal_running or
            state.body_running or state.body_live):
        raise ValueError("Finish the active animation process first")
    if state.body_payload or state.posing_payload or state.quadruped_payload:
        raise ValueError("Finish the active posing preview first")
    profile, _, mapping_rows = qp.binding(obj)
    if not profile.name.startswith("Rigify Generated Quadruped"):
        raise ValueError("Gait-phase review currently supports generated Rigify quadrupeds")
    mapping = {row["id"] for row in mapping_rows}
    anchors = w.read_anchors(obj)
    first, last = anchors[0][0], anchors[-1][0]
    rows = cm.validate(qc.rows(obj), first, last)
    if any(row["limb"] not in mapping for row in rows):
        raise ValueError("Accepted contacts contain a paw outside this quadruped rig")
    if any(row["end"] <= row["start"] for row in rows):
        raise ValueError("Accepted gait contacts need positive-duration intervals")
    return candidate, anchors, rows, first, last


def _stable_signature(obj, candidate, anchors, rows):
    return {
        "action": candidate.name,
        "action_session_uid": getattr(candidate, "session_uid", 0),
        "object_session_uid": getattr(obj, "session_uid", 0),
        "action_slot": w._slot(obj.animation_data),
        "action_sha256": _action_digest(obj, candidate),
        "anchors_sha256": _anchors_signature(obj),
        "contacts_sha256": _contacts_signature(rows),
    }


def _derive_phases(rows, first, last, anchor_frames=()):
    boundaries = sorted({first, last, *anchor_frames, *(row["start"] for row in rows),
                         *(row["end"] for row in rows)})
    phases = []
    for start, end in zip(boundaries, boundaries[1:]):
        if end <= start:
            continue
        sample = start + (end - start) * 0.5
        support = [limb for limb in qc.LIMBS
                   if any(row["limb"] == limb and row["start"] < sample < row["end"]
                          for row in rows)]
        phase = classify(support)
        phases.append({
            "index": len(phases),
            "start": start,
            "end": end,
            "duration": end - start,
            "phase": phase,
            "label": _LABELS[phase],
            "support_count": len(support),
            "support_limbs": support,
        })
    if not phases:
        raise ValueError("Accepted contacts do not define a gait review range")
    if len(phases) > MAX_PHASES:
        raise ValueError(f"Gait-phase review exceeds the {MAX_PHASES}-phase limit")
    return phases


def analyze(obj, scene):
    """Build and persist a read-only phase report for the active candidate."""
    w.require_rig(obj)
    candidate, anchors, rows, first, last = _source(obj)
    before = _stable_signature(obj, candidate, anchors, rows)
    phases = _derive_phases(rows, first, last, (frame for frame, _ in anchors))
    candidate2, anchors2, rows2, first2, last2 = _source(obj)
    after = _stable_signature(obj, candidate2, anchors2, rows2)
    if candidate2 is not candidate or first2 != first or last2 != last or after != before:
        raise ValueError("Candidate, anchors, or contacts changed during gait-phase analysis")
    report = {
        "schema": 1,
        "backend": BACKEND,
        "procedural": True,
        "learned": False,
        "gait_inference": False,
        "gait_generation": False,
        "source": "animator_accepted_quadruped_contacts",
        "candidate_action": candidate.name,
        "candidate_action_session_uid": before["action_session_uid"],
        "source_object_session_uid": before["object_session_uid"],
        "action_slot": before["action_slot"],
        "action_sha256": before["action_sha256"],
        "range": [first, last],
        "contact_count": len(rows),
        "phase_count": len(phases),
        "boundary_policy": "Support is classified on each open interval between exact contact/anchor boundaries.",
        "anchors_sha256": before["anchors_sha256"],
        "contacts_sha256": before["contacts_sha256"],
        "phases": phases,
    }
    text = json.dumps(report, sort_keys=True, allow_nan=False)
    if len(text) > 131072:
        raise ValueError("Gait-phase report exceeds the serialized size limit")
    obj.b4ml.quadruped_gait_report = text
    current = _frame(scene)
    containing = next((row["index"] for row in phases if row["start"] <= current < row["end"]), None)
    obj.b4ml.quadruped_gait_index = containing if containing is not None else 0
    obj.b4ml.status = f"Reviewed {len(phases)} procedural gait support phases; animation unchanged"
    return report


def _decode_report(text):
    if not text:
        raise ValueError("Analyze gait phases first")
    if len(text) > 131072:
        raise ValueError("Invalid gait-phase report")
    try:
        value = json.loads(text)
    except (TypeError, ValueError, RecursionError) as exc:
        raise ValueError("Invalid gait-phase report") from exc
    if (not isinstance(value, dict) or value.get("schema") != 1 or
            value.get("backend") != BACKEND or not isinstance(value.get("phases"), list) or
            not 1 <= len(value["phases"]) <= MAX_PHASES or
            value.get("procedural") is not True or value.get("learned") is not False or
            value.get("gait_inference") is not False or value.get("gait_generation") is not False or
            value.get("source") != "animator_accepted_quadruped_contacts" or
            value.get("boundary_policy") !=
            "Support is classified on each open interval between exact contact/anchor boundaries."):
        raise ValueError("Invalid gait-phase report")
    for key in ("action_sha256", "anchors_sha256", "contacts_sha256"):
        digest = value.get(key)
        if (not isinstance(digest, str) or len(digest) != 64 or
                any(character not in "0123456789abcdef" for character in digest)):
            raise ValueError("Invalid gait-phase report")
    for key in ("candidate_action_session_uid", "source_object_session_uid"):
        if isinstance(value.get(key), bool) or not isinstance(value.get(key), int):
            raise ValueError("Invalid gait-phase report")
    if not isinstance(value.get("candidate_action"), str) or not value["candidate_action"]:
        raise ValueError("Invalid gait-phase report")
    if not isinstance(value.get("action_slot"), str):
        raise ValueError("Invalid gait-phase report")
    ranges = value.get("range")
    if (not isinstance(ranges, list) or len(ranges) != 2 or
            any(isinstance(number, bool) or not isinstance(number, (int, float)) or
                not math.isfinite(number) for number in ranges) or ranges[0] >= ranges[1] or
            isinstance(value.get("phase_count"), bool) or
            value.get("phase_count") != len(value["phases"]) or
            isinstance(value.get("contact_count"), bool) or
            not isinstance(value.get("contact_count"), int) or
            not 1 <= value["contact_count"] <= 32):
        raise ValueError("Invalid gait-phase report")
    previous = ranges[0]
    for index, phase in enumerate(value["phases"]):
        if not isinstance(phase, dict):
            raise ValueError("Invalid gait-phase report")
        start, end, duration = (phase.get(key) for key in ("start", "end", "duration"))
        numbers = (start, end, duration)
        support = phase.get("support_limbs")
        if (any(isinstance(number, bool) or not isinstance(number, (int, float)) or
                not math.isfinite(number) for number in numbers) or start != previous or
                not start < end <= ranges[1] or duration != end - start or
                phase.get("index") != index or not isinstance(support, list) or
                any(not isinstance(limb, str) or limb not in qc.LIMBS for limb in support) or
                phase.get("support_count") != len(support)):
            raise ValueError("Invalid gait-phase report")
        if len(support) != len(set(support)):
            raise ValueError("Invalid gait-phase report")
        kind = classify(support)
        if phase.get("phase") != kind or phase.get("label") != _LABELS[kind]:
            raise ValueError("Invalid gait-phase report")
        previous = end
    if previous != ranges[1]:
        raise ValueError("Invalid gait-phase report")
    return value


def display_report(obj):
    """Validate contact-derived display data without rescanning animation curves."""
    value = _decode_report(obj.b4ml.quadruped_gait_report)
    state = obj.b4ml
    candidate = state.candidate_action
    if candidate is None or not obj.animation_data or obj.animation_data.action != candidate:
        raise ValueError("Gait-phase report is stale; analyze again")
    anchor_frames = sorted(item.frame for item in state.anchors)
    if (len(anchor_frames) < 2 or any(not math.isfinite(frame) for frame in anchor_frames) or
            any(right <= left for left, right in zip(anchor_frames, anchor_frames[1:]))):
        raise ValueError("Gait-phase report is stale; analyze again")
    first, last = anchor_frames[0], anchor_frames[-1]
    rows = cm.validate(qc.rows(obj), first, last)
    if (value["candidate_action"] != candidate.name or
            value["range"] != [first, last] or
            value["contact_count"] != len(rows) or
            value["phases"] != _derive_phases(rows, first, last, anchor_frames) or
            value["anchors_sha256"] != _anchors_signature(obj) or
            value["contacts_sha256"] != _contacts_signature(rows)):
        raise ValueError("Gait-phase report is stale; analyze again")
    return value


def report(obj):
    """Return a fully source-validated report, rejecting stale animation data."""
    value = display_report(obj)
    candidate, anchors, rows, first, last = _source(obj)
    same_object_session = (value["source_object_session_uid"] == getattr(obj, "session_uid", 0))
    same_action_session = (value["candidate_action_session_uid"] ==
                           getattr(candidate, "session_uid", 0))
    if (same_object_session and not same_action_session or
            value.get("range") != [first, last] or
            value.get("action_slot") != w._slot(obj.animation_data) or
            value.get("action_sha256") != _action_digest(obj, candidate) or
            value.get("anchors_sha256") != _anchors_signature(obj)):
        raise ValueError("Gait-phase report is stale; analyze again")
    return value


def current(obj):
    value = report(obj)
    index = min(max(int(obj.b4ml.quadruped_gait_index), 0), len(value["phases"]) - 1)
    obj.b4ml.quadruped_gait_index = index
    return value["phases"][index]


def navigate(obj, scene, step):
    if step not in (-1, 1):
        raise ValueError("Gait navigation step must be previous or next")
    value = report(obj)
    index = (min(max(int(obj.b4ml.quadruped_gait_index), 0), len(value["phases"]) - 1) + step) % len(value["phases"])
    obj.b4ml.quadruped_gait_index = index
    phase = value["phases"][index]
    _frame(scene, phase["start"] + phase["duration"] * 0.5)
    obj.b4ml.status = f"Gait phase {index + 1} of {len(value['phases'])}: {value['phases'][index]['label']}"
    return phase


def clear(obj):
    obj.b4ml.quadruped_gait_report = ""
    obj.b4ml.quadruped_gait_index = 0
    obj.b4ml.status = "Procedural gait-phase report cleared"
