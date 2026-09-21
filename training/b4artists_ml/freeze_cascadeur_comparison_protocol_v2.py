"""Freeze the prospective Cascadeur protocol around the audited character assets."""
from pathlib import Path
import hashlib
import json
import os

from portable_comparison_evidence_v1 import V1_PROTOCOL_SHA256, validate_host_audit


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
TRAIN = HERE.parent
BASE_PATH = TRAIN / "cascadeur_comparison_protocol_v1.json"
MANIFEST_PATH = TRAIN / "reference-assets-v1/manifest.json"
AUDIT_PATH = TRAIN / "results/portable-comparison-characters-v1-host.json"
OUT = TRAIN / "cascadeur_comparison_protocol_v2.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise RuntimeError("Cascadeur comparison protocol v2 already exists")
    protocol = json.loads(BASE_PATH.read_text(encoding="utf-8-sig"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8-sig"))
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8-sig"))
    if sha(BASE_PATH) != V1_PROTOCOL_SHA256:
        raise ValueError("Frozen Cascadeur comparison protocol v1 identity changed")
    if not manifest.get("assets_frozen") or manifest.get("asset_count") != 3:
        raise ValueError("Portable comparison assets are not frozen")
    validate_host_audit(
        manifest, audit, ROOT, MANIFEST_PATH.relative_to(ROOT).as_posix(),
        sha(TRAIN / "check_portable_comparison_characters_v1.py"),
    )
    protocol["schema"] = "b4ml-cascadeur-matched-comparison-protocol-v2"
    protocol["status"] = "prospective-assets-frozen"
    protocol["frozen_date"] = "2026-09-13"
    protocol["supersedes"] = BASE_PATH.name
    protocol["superseded_protocol_sha256"] = V1_PROTOCOL_SHA256
    protocol["revision_reason"] = (
        "Freeze three project-owned, proportion-varied Unity-style FBX characters and their "
        "Bforartists source/import audit before any Cascadeur run. Claim gates and matched tasks are unchanged."
    )
    characters = protocol["portable_characters"]
    characters["current_status"] = "assets frozen in Bforartists; Cascadeur import/conversion audit pending"
    characters["asset_manifest"] = MANIFEST_PATH.relative_to(ROOT).as_posix()
    characters["asset_manifest_sha256"] = sha(MANIFEST_PATH)
    characters["bforartists_host_audit"] = AUDIT_PATH.relative_to(ROOT).as_posix()
    characters["bforartists_host_audit_sha256"] = sha(AUDIT_PATH)
    characters["license"] = manifest["license"]
    characters["third_party_assets"] = manifest["third_party_assets"]
    characters["assets"] = [{
        "id": row["id"],
        "variation": row["variation"],
        "fbx": row["fbx"],
        "fbx_sha256": row["fbx_sha256"],
        "source_blend": row["source_blend"],
        "source_blend_sha256": row["source_blend_sha256"],
        "skeleton_height_m": row["skeleton_height_m"],
    } for row in manifest["assets"]]
    protocol["blocked_comparisons"] = [
        "B4ML has no accepted learned temporal runtime, so learned Inbetweening parity cannot be run",
        "Cascadeur import, unit/rest-pose conversion and standard-rig mapping of the three frozen FBX assets have not been audited",
        "no independent animator panel has completed matched tasks",
        "Cascadeur version, edition, entitlement and exact settings are not recorded",
        "quadruped comparison is outside this humanoid protocol",
    ]
    protocol["results"] = None
    protocol["parity_verified"] = False
    protocol["surpasses_verified"] = False
    protocol["full_goal_complete"] = False
    temporary = OUT.with_suffix(".tmp")
    temporary.write_text(json.dumps(protocol, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, OUT)
    print(json.dumps({
        "schema": protocol["schema"],
        "protocol": OUT.relative_to(ROOT).as_posix(),
        "protocol_sha256": sha(OUT),
        "assets": len(characters["assets"]),
        "results_present": False,
        "parity_verified": False,
        "surpasses_verified": False,
    }, indent=2))


if __name__ == "__main__":
    main()
