"""Validated, per-armature humanoid semantic-role corrections.

Corrections refine an already recognized humanoid adapter.  They never infer a
rig family, change rest data, or make deform/mechanism bones writable.
"""
import hashlib
import json
from dataclasses import replace

from .rigs import REQUIRED, detect_rig


PROPERTY_KEY = "b4ml_humanoid_mapping_corrections_v1"
MAX_PAYLOAD_CHARS = 32768
MAX_BONE_NAME_CHARS = 1024
_PAYLOAD_KEYS = frozenset(("schema", "base_profile", "base_schema",
                           "bone_signature", "roles"))
HUMANOID_ROLES = (
    "hips", "spine.01", "spine.02", "chest", "neck", "head",
    "clavicle.fk-L", "upperarm.fk-L", "forearm.fk-L", "hand.fk-L",
    "clavicle.fk-R", "upperarm.fk-R", "forearm.fk-R", "hand.fk-R",
    "thigh.fk-L", "shin.fk-L", "foot.fk-L",
    "thigh.fk-R", "shin.fk-R", "foot.fk-R",
)


def _bone_names(obj):
    return tuple(sorted(str(name) for name in obj.data.bones.keys()))


def bone_signature(obj):
    rows = []
    for name in _bone_names(obj):
        bone = obj.data.bones[name]
        rows.append("\0".join((name, bone.parent.name if bone.parent else "",
                               "1" if bone.use_connect else "0",
                               "1" if bone.use_deform else "0")))
    encoded = "\1".join(rows).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def structural_category(name):
    lower = name.casefold()
    if lower.startswith("def-") or ".def-" in lower:
        return "deform"
    if lower.startswith("mch-") or ".mch_" in lower:
        return "mechanism"
    if lower.startswith("org-"):
        return "organization"
    if lower.startswith(("wgt-", "wgts_")):
        return "widget"
    if lower.startswith("tweak_") or ".tweak" in lower or "_tweak" in lower:
        return "tweak"
    return None


def _base(obj):
    profile = detect_rig(obj.data.bones.keys())
    if profile.family != "humanoid" or profile.schema != "humanoid_v1":
        raise ValueError("Manual mapping corrections require a recognized humanoid rig")
    if profile.name == "Rigify Deform" or not profile.controls:
        raise ValueError("Manual mapping corrections require an animator control rig, not a deform-only skeleton")
    return profile


def _validate_rows(obj, base, payload):
    if not isinstance(payload, dict) or set(payload) != _PAYLOAD_KEYS:
        raise ValueError("Manual mapping correction payload has an invalid schema")
    if type(payload["schema"]) is not int or payload["schema"] != 1:
        raise ValueError("Manual mapping correction version is unsupported")
    for key in ("base_profile", "base_schema", "bone_signature"):
        if not isinstance(payload[key], str) or not payload[key]:
            raise ValueError("Manual mapping correction metadata is invalid")
    if payload["base_profile"] != base.name or payload["base_schema"] != base.schema:
        raise ValueError("Manual mapping corrections belong to a different rig adapter")
    if payload["bone_signature"] != bone_signature(obj):
        raise ValueError("Manual mapping corrections are stale after a rig bone change")
    rows = payload["roles"]
    if not isinstance(rows, dict) or not rows or len(rows) > len(HUMANOID_ROLES):
        raise ValueError("Manual mapping corrections require one to twenty role rows")
    names = set(_bone_names(obj))
    reserved = {"root"} | ({"torso"} if base.name == "Rigify Generated" else set())
    for role, bone in rows.items():
        if role not in HUMANOID_ROLES:
            raise ValueError("Unsupported humanoid mapping role: " + str(role))
        if (not isinstance(bone, str) or not bone
                or len(bone) > MAX_BONE_NAME_CHARS or bone not in names):
            raise ValueError("Mapped bone does not exist: " + str(bone))
        category = structural_category(bone)
        if category:
            raise ValueError("Animator role cannot use a " + category + " bone: " + bone)
        if bone.casefold() in reserved:
            raise ValueError("Animator role cannot use a reserved master/root control: " + bone)
        if obj.pose.bones.get(bone) is None:
            raise ValueError("Mapped bone has no pose control: " + bone)
    merged = dict(base.roles)
    merged.update(rows)
    semantic_bones = list(merged.values())
    if len(semantic_bones) != len(set(semantic_bones)):
        raise ValueError("Each humanoid semantic role must map to a distinct bone")
    return dict(rows)


def read_corrections(obj):
    """Return a validated correction map; absent data returns an empty map."""
    value = obj.get(PROPERTY_KEY)
    if value is None:
        return {}
    if not isinstance(value, str) or not value or len(value) > MAX_PAYLOAD_CHARS:
        raise ValueError("Manual mapping correction payload is invalid or too large")
    try:
        payload = json.loads(value)
    except (TypeError, ValueError, RecursionError) as exc:
        raise ValueError("Manual mapping correction payload is not valid JSON") from exc
    return _validate_rows(obj, _base(obj), payload)


def profile_for_object(obj):
    """Return the detected profile with validated semantic corrections applied."""
    base = detect_rig(obj.data.bones.keys())
    if obj.get(PROPERTY_KEY) is None:
        return base
    if base.family != "humanoid" or base.schema != "humanoid_v1":
        raise ValueError("Manual mapping corrections require a recognized humanoid rig")
    rows = read_corrections(obj)
    roles = dict(base.roles)
    roles.update(rows)
    controls = set(base.controls)
    controls.update(rows.values())
    missing = tuple(role for role in REQUIRED if role not in roles)
    warnings = tuple(base.warnings) + (
        f"Manual semantic mapping: {len(rows)} corrected role{'s' if len(rows) != 1 else ''} active.",)
    return replace(base, roles=roles, controls=tuple(sorted(controls)),
                   missing=missing, warnings=warnings)


def status(obj):
    """Return a UI/diagnostic snapshot without hiding invalid correction data."""
    base = detect_rig(obj.data.bones.keys())
    try:
        rows = read_corrections(obj)
    except ValueError as exc:
        return base, (), str(exc)
    if not rows:
        return base, (), ""
    return profile_for_object(obj), tuple(sorted(rows.items())), ""


def _payload(obj, base, rows):
    return json.dumps({
        "schema": 1,
        "base_profile": base.name,
        "base_schema": base.schema,
        "bone_signature": bone_signature(obj),
        "roles": dict(sorted(rows.items())),
    }, sort_keys=True, separators=(",", ":"), allow_nan=False)


def set_correction(obj, role, bone):
    base = _base(obj)
    if role not in HUMANOID_ROLES:
        raise ValueError("Choose a supported humanoid semantic role")
    if not isinstance(bone, str) or not bone:
        raise ValueError("Choose an animator bone for the semantic role")
    rows = read_corrections(obj)
    if base.roles.get(role) == bone:
        rows.pop(role, None)
    else:
        rows[role] = bone
    if not rows:
        clear_all(obj)
        return {}
    candidate = {
        "schema": 1, "base_profile": base.name, "base_schema": base.schema,
        "bone_signature": bone_signature(obj), "roles": rows,
    }
    rows = _validate_rows(obj, base, candidate)
    text = _payload(obj, base, rows)
    if len(text) > MAX_PAYLOAD_CHARS:
        raise ValueError("Manual mapping correction payload is too large")
    obj[PROPERTY_KEY] = text
    return rows


def clear_correction(obj, role):
    if role not in HUMANOID_ROLES:
        raise ValueError("Choose a supported humanoid semantic role")
    rows = read_corrections(obj)
    if role not in rows:
        raise ValueError("The selected role has no manual correction")
    del rows[role]
    if rows:
        base = _base(obj)
        candidate = {
            "schema": 1, "base_profile": base.name, "base_schema": base.schema,
            "bone_signature": bone_signature(obj), "roles": rows,
        }
        rows = _validate_rows(obj, base, candidate)
        obj[PROPERTY_KEY] = _payload(obj, base, rows)
    else:
        clear_all(obj)
    return rows


def clear_all(obj):
    if PROPERTY_KEY in obj:
        del obj[PROPERTY_KEY]
