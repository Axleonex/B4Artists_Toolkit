"""Validate the asset-frozen prospective comparison protocol without running it."""
from pathlib import Path
import hashlib
import json
import os
from urllib.parse import urlparse

from portable_comparison_evidence_v1 import V1_PROTOCOL_SHA256, validate_host_audit


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
TRAIN = HERE.parent
PROTOCOL = TRAIN / "cascadeur_comparison_protocol_v2.json"
BASE = TRAIN / "cascadeur_comparison_protocol_v1.json"
OUT = Path(os.environ.get(
    "B4ML_CASCADEUR_PROTOCOL_VALIDATION_OUT",
    str(TRAIN / "results/cascadeur-comparison-protocol-validation-v2.json")))
IMPORT_AUDIT = ROOT / "training/b4artists_ml/results/cascadeur-import-audit-v1.json"
PROSPECTIVE_STATUS = "prospective-assets-frozen"
PORTABLE_STATUS = (
    "assets frozen in Bforartists; Cascadeur disposable import audit passed; "
    "conversion and matched human execution pending"
)
REQUIRED_BLOCKERS = {
    "B4ML has no accepted learned temporal runtime, so learned Inbetweening parity cannot be run",
    "Cascadeur unit/rest-pose conversion, standard-rig mapping and matched animation have not been audited",
    "no independent animator panel has completed matched tasks",
    "Cascadeur version, edition, entitlement and exact settings are not recorded",
    "quadruped comparison is outside this humanoid protocol",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_claim_boundary(protocol):
    if protocol.get("status") != PROSPECTIVE_STATUS:
        raise ValueError("Comparison protocol v2 is not prospective")
    if protocol.get("results") is not None:
        raise ValueError("Prospective comparison contains results")
    for key in ("parity_verified", "surpasses_verified", "full_goal_complete"):
        if protocol.get(key) is not False:
            raise ValueError("Prospective comparison contains unsupported claim: " + key)
    portable = protocol.get("portable_characters")
    if not isinstance(portable, dict) or portable.get("current_status") != PORTABLE_STATUS:
        raise ValueError("Cascadeur import/conversion boundary changed")
    blockers = protocol.get("blocked_comparisons")
    if (not isinstance(blockers, list) or len(blockers) != len(REQUIRED_BLOCKERS) or
            set(blockers) != REQUIRED_BLOCKERS):
        raise ValueError("Required comparison blockers changed")


def main():
    if OUT.exists():
        raise RuntimeError("Cascadeur comparison protocol v2 validation already exists")
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8-sig"))
    base = json.loads(BASE.read_text(encoding="utf-8-sig"))
    if protocol.get("schema") != "b4ml-cascadeur-matched-comparison-protocol-v2":
        raise ValueError("Comparison protocol v2 schema changed")
    if sha(BASE) != V1_PROTOCOL_SHA256:
        raise ValueError("Frozen comparison protocol v1 identity changed")
    if (protocol.get("status") != PROSPECTIVE_STATUS or
            protocol.get("supersedes") != BASE.name or
            protocol.get("superseded_protocol_sha256") != V1_PROTOCOL_SHA256):
        raise ValueError("Comparison protocol v2 is not a prospective additive revision")
    for key in ("tasks", "common_scene", "workflows", "automated_metrics", "human_metrics",
                "human_protocol", "runs", "claim_gates"):
        if protocol[key] != base[key]:
            raise ValueError("Frozen comparison contract changed: " + key)
    validate_claim_boundary(protocol)
    sources = protocol["cascadeur"]["official_sources"]
    if len(sources) < 5 or len(sources) != len(set(sources)):
        raise ValueError("Official source list is incomplete")
    if any(urlparse(url).scheme != "https" or urlparse(url).netloc != "cascadeur.com" for url in sources):
        raise ValueError("Comparison research must cite official Cascadeur sources")
    characters = protocol["portable_characters"]
    if characters["minimum"] != 3 or len(characters["assets"]) != 3:
        raise ValueError("Portable asset matrix is incomplete")
    if [row["variation"] for row in characters["assets"]] != characters["required_variation"]:
        raise ValueError("Portable asset variations changed")
    manifest_path = ROOT / characters["asset_manifest"]
    audit_path = ROOT / characters["bforartists_host_audit"]
    if sha(manifest_path) != characters["asset_manifest_sha256"]:
        raise ValueError("Portable asset manifest hash mismatch")
    if sha(audit_path) != characters["bforartists_host_audit_sha256"]:
        raise ValueError("Portable host audit hash mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    audit = json.loads(audit_path.read_text(encoding="utf-8-sig"))
    if not manifest.get("assets_frozen"):
        raise ValueError("Portable character manifest is incomplete")
    validate_host_audit(
        manifest, audit, ROOT, characters["asset_manifest"],
        sha(TRAIN / "check_portable_comparison_characters_v1.py"),
    )
    import_audit = json.loads(IMPORT_AUDIT.read_text(encoding="utf-8"))
    if (import_audit.get("schema") != "b4ml-cascadeur-import-audit-v1" or
            import_audit.get("status") != "PASS" or
            import_audit.get("all_hashes_match") is not True or
            import_audit.get("import_conversion_audit") is not False or
            import_audit.get("parity_verified") is not False or
            import_audit.get("surpasses_verified") is not False):
        raise ValueError("Cascadeur disposable import audit is not a bounded PASS")
    imported = {row.get("id"): row for row in import_audit.get("assets", [])}
    if set(imported) != {row["id"] for row in characters["assets"]}:
        raise ValueError("Cascadeur import audit asset set does not match the protocol")
    for row in characters["assets"]:
        observed = imported[row["id"]]
        if (observed.get("fbx_sha256") != row["fbx_sha256"] or
                observed.get("expected_fbx_sha256") != row["fbx_sha256"] or
                observed.get("imported") is not True or
                observed.get("scene_removed") is not True):
            raise ValueError("Cascadeur import audit mismatch: " + row["id"])
    manifest_assets = {row["id"]: row for row in manifest["assets"]}
    for row in characters["assets"]:
        source = manifest_assets.get(row["id"])
        if source is None:
            raise ValueError("Protocol asset is absent from manifest")
        for key in ("variation", "fbx", "fbx_sha256", "source_blend", "source_blend_sha256", "skeleton_height_m"):
            if row[key] != source[key]:
                raise ValueError(f"Protocol asset field changed: {row['id']} {key}")
        if sha(ROOT / row["fbx"]) != row["fbx_sha256"] or sha(ROOT / row["source_blend"]) != row["source_blend_sha256"]:
            raise ValueError("Frozen asset bytes changed: " + row["id"])
    report = {
        "schema": "b4ml-cascadeur-comparison-protocol-validation-v2",
        "complete": True,
        "prospective": True,
        "assets_frozen": True,
        "assets": len(characters["assets"]),
        "tasks": len(protocol["tasks"]),
        "matched_cases_per_animator": protocol["human_protocol"]["matched_cases_per_animator"],
        "independent_animators_required": protocol["human_protocol"]["independent_animators_minimum"],
        "claim_gates_unchanged_from_v1": True,
        "matched_work_unchanged_from_v1": True,
        "superseded_protocol_sha256": V1_PROTOCOL_SHA256,
        "cascadeur_import_audit_present": True,
        "cascadeur_import_audit": IMPORT_AUDIT.relative_to(ROOT).as_posix(),
        "cascadeur_import_audit_sha256": sha(IMPORT_AUDIT),
        "results_present": False,
        "parity_verified": False,
        "surpasses_verified": False,
        "full_goal_complete": False,
        "protocol": PROTOCOL.relative_to(ROOT).as_posix(),
        "protocol_sha256": sha(PROTOCOL),
        "checker_sha256": sha(HERE),
        "evidence_validator_sha256": sha(TRAIN / "portable_comparison_evidence_v1.py"),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUT.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, OUT)
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
