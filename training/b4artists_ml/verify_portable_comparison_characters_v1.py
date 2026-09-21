"""Final byte-level verifier for Portable Comparison Characters v1."""
from pathlib import Path
import hashlib
import io
import json
import os
import struct
import sys
import unittest

from portable_comparison_evidence_v1 import V1_PROTOCOL_SHA256, validate_host_audit


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TRAIN = HERE.parent
SPEC = TRAIN / "portable_comparison_characters_v1.json"
TEST_SOURCE = ROOT / "tests/test_b4artists_ml_portable_comparison_characters_v1.py"
MANIFEST = TRAIN / "reference-assets-v1/manifest.json"
HOST_AUDIT = TRAIN / "results/portable-comparison-characters-v1-host.json"
BUILDER = TRAIN / "build_portable_comparison_characters_v1.py"
HOST_CHECKER = TRAIN / "check_portable_comparison_characters_v1.py"
PROTOCOL = TRAIN / "cascadeur_comparison_protocol_v2.json"
PROTOCOL_AUDIT = TRAIN / "results/cascadeur-comparison-protocol-validation-v2.json"
PROTOCOL_CHECKER = TRAIN / "check_cascadeur_comparison_protocol_v2.py"
EVIDENCE_VALIDATOR = TRAIN / "portable_comparison_evidence_v1.py"
V1_PROTOCOL = TRAIN / "cascadeur_comparison_protocol_v1.json"
PREVIEW = TRAIN / "results/portable-comparison-characters-v1.png"
RENDERER = TRAIN / "render_portable_comparison_characters_v1.py"
FROZEN_RELEASE = ROOT / "releases/b4artists_ml_v0.36.0.zip"
OUT = TRAIN / "results/portable-comparison-characters-v1.json"
FROZEN_RELEASE_SHA256 = "3a0423b632cdc0b279a43e45c58321d75833927fb4207d8a2b35d213e282e2e5"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    check_existing = "--check-existing" in sys.argv[1:]
    if OUT.exists() and not check_existing:
        raise RuntimeError("Portable comparison final report already exists")
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromName(
        "tests.test_b4artists_ml_portable_comparison_characters_v1"
    )
    unit = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    if (unit.testsRun != 6 or unit.failures or unit.errors or unit.skipped or
            getattr(unit, "expectedFailures", ()) or getattr(unit, "unexpectedSuccesses", ())):
        raise RuntimeError(stream.getvalue())
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    host = json.loads(HOST_AUDIT.read_text(encoding="utf-8-sig"))
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8-sig"))
    protocol_audit = json.loads(PROTOCOL_AUDIT.read_text(encoding="utf-8-sig"))
    if not manifest.get("complete") or not manifest.get("assets_frozen") or len(manifest.get("assets", ())) != 3:
        raise ValueError("Character manifest is incomplete")
    validate_host_audit(
        manifest, host, ROOT, MANIFEST.relative_to(ROOT).as_posix(), sha(HOST_CHECKER)
    )
    if not protocol_audit.get("complete") or not protocol_audit.get("assets_frozen"):
        raise ValueError("Comparison protocol audit is incomplete")
    if protocol_audit["protocol_sha256"] != sha(PROTOCOL):
        raise ValueError("Comparison protocol identity changed")
    if manifest["builder_sha256"] != sha(BUILDER):
        raise ValueError("Character builder identity changed")
    if host["checker_sha256"] != sha(HOST_CHECKER):
        raise ValueError("Fresh-host checker identity changed")
    if protocol_audit["checker_sha256"] != sha(PROTOCOL_CHECKER):
        raise ValueError("Comparison protocol checker identity changed")
    if protocol_audit.get("evidence_validator_sha256") != sha(EVIDENCE_VALIDATOR):
        raise ValueError("Comparison evidence validator identity changed")
    if (sha(V1_PROTOCOL) != V1_PROTOCOL_SHA256 or
            protocol.get("superseded_protocol_sha256") != V1_PROTOCOL_SHA256 or
            protocol_audit.get("superseded_protocol_sha256") != V1_PROTOCOL_SHA256):
        raise ValueError("Frozen comparison protocol v1 binding changed")
    if protocol["portable_characters"]["asset_manifest_sha256"] != sha(MANIFEST):
        raise ValueError("Protocol no longer binds the character manifest")
    if protocol["portable_characters"]["bforartists_host_audit_sha256"] != sha(HOST_AUDIT):
        raise ValueError("Protocol no longer binds the fresh-host audit")
    assets = []
    for row in manifest["assets"]:
        blend = ROOT / row["source_blend"]
        fbx = ROOT / row["fbx"]
        if sha(blend) != row["source_blend_sha256"] or sha(fbx) != row["fbx_sha256"]:
            raise ValueError("Frozen character bytes changed: " + row["id"])
        assets.append({
            "id": row["id"], "variation": row["variation"],
            "source_blend": row["source_blend"], "source_blend_sha256": row["source_blend_sha256"],
            "fbx": row["fbx"], "fbx_sha256": row["fbx_sha256"],
        })
    if sha(FROZEN_RELEASE) != FROZEN_RELEASE_SHA256:
        raise ValueError("Frozen v0.36.0 package changed")
    png = PREVIEW.read_bytes()
    if png[:8] != b"\x89PNG\r\n\x1a\n" or len(png) < 24:
        raise ValueError("Portable character preview is not a valid PNG")
    width, height = struct.unpack(">II", png[16:24])
    if (width, height) != (1200, 700):
        raise ValueError("Portable character preview dimensions changed")
    report = {
        "schema": "b4ml-portable-comparison-characters-v1",
        "complete": True,
        "assets_frozen": True,
        "asset_count": len(assets),
        "source_and_fresh_fbx_imports_passed": host["passed"],
        "unit_tests_run": unit.testsRun,
        "unit_tests_passed": unit.testsRun - len(unit.failures) - len(unit.errors),
        "unit_tests_skipped": len(unit.skipped),
        "unit_test_output": stream.getvalue().strip(),
        "test_source_sha256": sha(TEST_SOURCE),
        "evidence_validator_sha256": sha(EVIDENCE_VALIDATOR),
        "superseded_protocol_sha256": V1_PROTOCOL_SHA256,
        "same_exact_fbx_required_for_b4ml_and_cascadeur": True,
        "spec": SPEC.relative_to(ROOT).as_posix(),
        "spec_sha256": sha(SPEC),
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "manifest_sha256": sha(MANIFEST),
        "builder_sha256": sha(BUILDER),
        "host_audit": HOST_AUDIT.relative_to(ROOT).as_posix(),
        "host_audit_sha256": sha(HOST_AUDIT),
        "host_checker_sha256": sha(HOST_CHECKER),
        "comparison_protocol": PROTOCOL.relative_to(ROOT).as_posix(),
        "comparison_protocol_sha256": sha(PROTOCOL),
        "comparison_protocol_audit": PROTOCOL_AUDIT.relative_to(ROOT).as_posix(),
        "comparison_protocol_audit_sha256": sha(PROTOCOL_AUDIT),
        "comparison_protocol_checker_sha256": sha(PROTOCOL_CHECKER),
        "inspection_preview": PREVIEW.relative_to(ROOT).as_posix(),
        "inspection_preview_sha256": sha(PREVIEW),
        "inspection_preview_resolution": [width, height],
        "inspection_renderer_sha256": sha(RENDERER),
        "inspection_scope": "Author presentation/readability check; not an independent motion-quality assessment.",
        "verifier_sha256": sha(HERE),
        "frozen_release_sha256": sha(FROZEN_RELEASE),
        "assets": assets,
        "cascadeur_import_audit_present": False,
        "human_review_present": False,
        "learned_temporal_runtime_accepted": False,
        "parity_verified": False,
        "surpasses_verified": False,
        "full_goal_complete": False,
    }
    if check_existing:
        existing = json.loads(OUT.read_text(encoding="utf-8-sig"))
        for key, value in report.items():
            if key != "unit_test_output" and existing.get(key) != value:
                raise ValueError("Existing final report differs at " + key)
        print(json.dumps({
            "schema": report["schema"], "complete": True,
            "existing_report_exact_for_stable_fields": True,
            "assets": report["asset_count"],
            "fresh_imports": report["source_and_fresh_fbx_imports_passed"],
            "frozen_release_unchanged": True,
        }, indent=2))
        return
    temporary = OUT.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, OUT)
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
