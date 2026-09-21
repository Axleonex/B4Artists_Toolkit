"""Strict pure-Python validation for portable-character host evidence."""
from pathlib import Path
import hashlib
import json
import math


V1_PROTOCOL_SHA256 = "5fedbc2cef2f6048e13e57622e9e44396d1623890ce12477e13892ac69632a4e"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _close(actual, expected, tolerance=2e-5):
    return math.isclose(float(actual), float(expected), rel_tol=tolerance, abs_tol=tolerance)


def validate_host_audit(manifest, audit, root, manifest_relative, checker_sha256):
    """Require the complete per-asset source/import evidence used by published claims."""
    root = Path(root)
    _require(audit.get("schema") == "b4ml-portable-comparison-character-host-audit-v1",
             "Host audit schema changed")
    _require(audit.get("complete") is True, "Host audit is incomplete")
    _require(audit.get("expected") == manifest.get("asset_count") == 3,
             "Host audit expected count changed")
    _require(audit.get("passed") == 3, "Host audit pass count changed")
    _require(audit.get("manifest") == manifest_relative, "Host audit manifest path changed")
    _require(audit.get("manifest_sha256_before_audit_binding") == sha(root / manifest_relative),
             "Host audit manifest hash changed")
    _require(audit.get("checker_sha256") == checker_sha256, "Host audit checker identity changed")
    _require(audit.get("same_asset_required_for_each_matched_pair") is True,
             "Host audit matched-pair requirement changed")
    _require(audit.get("cascadeur_import_not_yet_run") is True,
             "Host audit Cascadeur claim boundary changed")
    _require(audit.get("human_review_not_yet_run") is True,
             "Host audit human-review boundary changed")
    _require(not audit.get("parity_verified") and not audit.get("surpasses_verified")
             and not audit.get("full_goal_complete"), "Host audit contains an unsupported claim")
    expected_rows = manifest.get("assets", [])
    actual_rows = audit.get("assets", [])
    _require([row.get("id") for row in actual_rows] == [row.get("id") for row in expected_rows],
             "Host audit asset identities or order changed")
    required_boolean_fields = (
        "all_weights_normalized", "armature_modifier_bound", "mesh_parent_bound",
        "mesh_deforms_under_pose",
    )
    signature_fields = ("geometry_sha256", "topology_sha256", "weighting_sha256")
    dimension_fields = {
        "skeleton_height_m": lambda row: row["skeleton_height_m"],
        "shoulder_span_m": lambda row: row["dimensions_m"]["shoulder_half_width"] * 2.0,
        "hip_span_m": lambda row: row["dimensions_m"]["hip_half_width"] * 2.0,
        "left_arm_horizontal_reach_m": lambda row: row["dimensions_m"]["arm"],
    }
    for expected, actual in zip(expected_rows, actual_rows):
        asset_id = expected["id"]
        _require(actual.get("variation") == expected["variation"],
                 "Host audit variation changed: " + asset_id)
        for field in ("source_blend_sha256", "fbx_sha256"):
            _require(actual.get(field) == expected[field],
                     f"Host audit {field} changed: {asset_id}")
        _require(actual.get("roundtrip_geometry_exact_at_1e_5") is True,
                 "Host audit geometry roundtrip is not exact: " + asset_id)
        _require(actual.get("roundtrip_topology_exact_at_1e_5") is True,
                 "Host audit topology roundtrip is not exact: " + asset_id)
        _require(actual.get("roundtrip_weights_exact_at_1e_6") is True,
                 "Host audit weighting roundtrip is not exact: " + asset_id)
        source = actual.get("source", {})
        imported = actual.get("imported", {})
        _require(source.get("kind") == "source_blend" and imported.get("kind") == "fresh_fbx_import",
                 "Host audit source/import kinds changed: " + asset_id)
        for record in (source, imported):
            _require(record.get("objects") == expected["object_count"] == 2,
                     "Host audit object count changed: " + asset_id)
            _require(record.get("bones") == len(expected["bones"]),
                     "Host audit bone count changed: " + asset_id)
            _require(record.get("vertices") == expected["vertices"],
                     "Host audit vertex count changed: " + asset_id)
            _require(record.get("faces") == expected["faces"],
                     "Host audit face count changed: " + asset_id)
            _require(record.get("weighted_vertices") == expected["weighted_vertices"],
                     "Host audit weighted-vertex count changed: " + asset_id)
            _require(record.get("detected_profile") == "Unity Humanoid" and record.get("missing_roles") == [],
                     "Host audit rig mapping changed: " + asset_id)
            _require(record.get("armature_modifier_count") == 1,
                     "Host audit Armature modifier count changed: " + asset_id)
            _require(all(record.get(field) is True for field in required_boolean_fields),
                     "Host audit binding/deformation proof changed: " + asset_id)
            _require(float(record.get("deformation_probe_delta", 0.0)) > 1e-4,
                     "Host audit deformation probe is ineffective: " + asset_id)
            _require(record.get("actions") == record.get("images") == record.get("libraries") == 0,
                     "Host audit external or animation data changed: " + asset_id)
            for field, expected_value in dimension_fields.items():
                _require(_close(record.get(field), expected_value(expected)),
                         f"Host audit {field} changed: {asset_id}")
            for field in signature_fields:
                value = record.get(field)
                _require(isinstance(value, str) and len(value) == 64,
                         f"Host audit {field} is malformed: {asset_id}")
        for field in signature_fields:
            _require(source[field] == imported[field],
                     f"Host audit source/import {field} differs: {asset_id}")
    return True
