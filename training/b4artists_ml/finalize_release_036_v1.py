"""Finalize the local experimental 0.36.0 release manifest and documentation."""
from pathlib import Path
import hashlib
import json
import os
import zipfile


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs/b4artists_ml"
RESULTS = ROOT / "training/b4artists_ml/results"
ARCHIVE = ROOT / "releases/b4artists_ml_v0.36.0.zip"
MANIFEST = DOCS / "package-test-v0.36.0.json"
REGRESSION = RESULTS / "release-036-v1-regression.json"
PACKAGE = RESULTS / "release-036-package-v4.json"
PACKAGE_SHA256 = "3a0423b632cdc0b279a43e45c58321d75833927fb4207d8a2b35d213e282e2e5"
REGRESSION_SHA256 = "7bc3811d63e35862e186f132afd9ab8f087cc11032d80e82b6a7c16d48d9c5ae"
PACKAGE_REPORT_SHA256 = "27892bc4445ff9334958c9ae5b4d1f2aa87ade7f2d121b744b8979ac15cfbb46"
CHECKER_SHA256 = "2a0e551bfe444e188a80cfdb45248e0650b95f56239e60c62dbaf383edb00ef6"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def appended_payload(path, marker, text):
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    current = raw.decode("utf-8-sig")
    require(marker not in current, "Documentation section already exists: " + marker)
    newline = "\r\n" if "\r\n" in current else "\n"
    addition = text.strip().replace("\n", newline)
    payload = (current.rstrip() + newline * 2 + addition + newline).encode("utf-8")
    return (b"\xef\xbb\xbf" if bom else b"") + payload


def publish_transaction(outputs):
    originals = {path: path.read_bytes() if path.exists() else None for path in outputs}
    staged = {}
    replaced = []
    try:
        for path, payload in outputs.items():
            temporary = path.with_name(path.name + ".b4ml036.tmp")
            require(not temporary.exists(), "Stale release staging file: " + str(temporary))
            staged[path] = temporary
            temporary.write_bytes(payload)
            require(temporary.read_bytes() == payload, "Staged release payload mismatch")
        for path, temporary in staged.items():
            os.replace(temporary, path)
            replaced.append(path)
    except Exception:
        for path in reversed(replaced):
            original = originals[path]
            if original is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(original)
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)
        raise


def main():
    require(sha(ARCHIVE) == PACKAGE_SHA256, "Release archive changed")
    require(sha(REGRESSION) == REGRESSION_SHA256, "Release regression changed")
    require(sha(PACKAGE) == PACKAGE_REPORT_SHA256, "Exact-package report changed")
    regression = read(REGRESSION)
    package = read(PACKAGE)
    require(regression.get("passed") and regression.get("tests") == 1017 and
            regression.get("suite_count") == 87 and
            regression.get("distributable_member_count") == 54,
            "Source regression does not qualify the release")
    require(package.get("passed") and package.get("tests") == 209 and
            package.get("suite_count") == 32 and package.get("skips") == 0 and
            len(package.get("groups", ())) == 8 and
            package.get("checker_sha256") == CHECKER_SHA256 and
            package.get("package_sha256") == PACKAGE_SHA256 and
            package.get("all_runtime_imports_from_package") and
            package.get("offline_guard_self_test") and
            not package.get("denied_runtime_calls") and
            package.get("package_members_match_source") and
            package.get("source_package_plan_and_tests_unchanged"),
            "Exact-package evidence does not qualify the release")
    require(all(group.get("passed") and group.get("skips") == 0
                for group in package["groups"]), "A package group did not pass")
    with zipfile.ZipFile(ARCHIVE) as archive:
        require(len(archive.namelist()) == 54 and archive.testzip() is None,
                "Release archive integrity failed")

    manifest = read(MANIFEST)
    require(manifest.get("sha256") == PACKAGE_SHA256 and
            manifest.get("regression", {}).get("sha256") == REGRESSION_SHA256,
            "Build manifest does not match final evidence")
    manifest["ready_for_local_testing"] = True
    manifest["exact_package_checks"] = {
        "evidence": "training/b4artists_ml/results/release-036-package-v4.json",
        "sha256": PACKAGE_REPORT_SHA256,
        "passed": True,
        "groups": 8,
        "suites": 32,
        "tests": 209,
        "skips": 0,
        "all_runtime_imports_from_package": True,
        "offline_guard_self_test": True,
        "package_members_unchanged": True,
        "checker_sha256": CHECKER_SHA256,
        "elapsed_seconds": package["elapsed_seconds"],
        "preserved_failed_attempts": [
            "release-036-package-v1 (900-second timeout; no pass report)",
            "release-036-package-v2 (900-second timeout; no pass report)",
            "release-036-package-v3 group 2 (900-second timeout; no aggregate pass report)",
        ],
    }
    manifest_payload = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")

    release = f"""# B4Artists Machine Learning 0.36.0

This is a local experimental Bforartists-only package that consolidates the procedural workflow work through development 0.36. It is ready for local testing from `releases/b4artists_ml_v0.36.0.zip`.

## Included workflow surface

- Humanoid and generated-Rigify quadruped rig diagnostics, targets, pole controls, pose reuse and semantic pose assets.
- Contact review, interval editing, prop holds, moving platforms and contact visualization.
- Timing presets, transition easing/bias/holds, Breakdown Pose and Transition Timing Transfer.
- Existing local static pose models and deterministic physics/refinement helpers.

## Qualification

- Curated source regression: 87 suites, 1,017 loader-visible tests, zero failures/errors/skips.
- Exact extracted package: 8 fresh Bforartists groups, 32 feature suites, 209 feature-defined tests, zero failures/errors/skips.
- All 44 runtime Python files and all 54 distributable Python/model/map/license/model-card members were hash-frozen.
- Breakdown Pose and Transition Timing Transfer passed foreground Bforartists operator, Undo/Redo and source-Action recovery journeys.
- Package imports were proven to come from the extracted ZIP cache with network/process calls denied.
- Serial reviewer result: PASS after the release gates were hardened.

## Artifact

- File: `releases/b4artists_ml_v0.36.0.zip`
- Size: 389,957 bytes
- SHA-256: `{PACKAGE_SHA256}`
- Manifest: `docs/b4artists_ml/package-test-v0.36.0.json`
- Source regression: `training/b4artists_ml/results/release-036-v1-regression.json`
- Exact-package evidence: `training/b4artists_ml/results/release-036-package-v4.json`

## Claim boundary

This release does not qualify learned temporal generation, independent animator usability, clean Bforartists host shutdown, Cascadeur parity/superiority, or the full project goal. The known Bforartists 5.2.0 Alpha `ucrtbase.dll` shutdown fault remains: assertions and reports complete before exit code 3221225477. No installation, commit, push, or external publication was performed.
"""
    release_path = DOCS / "RELEASE-v0.36.0.md"
    require(not release_path.exists(), "Release note already exists")

    status = """## Local experimental 0.36.0 package

The installable local package `releases/b4artists_ml_v0.36.0.zip` consolidates the procedural workflow surface through Breakdown Pose and Transition Timing Transfer. The frozen 54-member distributable passed 1,017 source tests across 87 curated suites and 209 exact-package feature tests across 32 suites in eight fresh Bforartists processes, with zero skips. Foreground Breakdown Pose and timing-transfer journeys pass on the exact runtime. The package is ready for local testing. Learned temporal generation, independent animator usability, clean host shutdown and Cascadeur parity remain unqualified; the full goal remains active. See `RELEASE-v0.36.0.md` and `package-test-v0.36.0.json`."""
    guide = """## Installing the local experimental 0.36.0 package

In Bforartists, open **Edit > Preferences > Add-ons**, choose **Install from Disk**, and select `releases/b4artists_ml_v0.36.0.zip`. Enable **B4Artists Machine Learning**, then use **View3D > Sidebar > B4Artists ML**. This package is Bforartists-only and intended for local testing. The release does not claim learned temporal generation or Cascadeur parity; see `RELEASE-v0.36.0.md` for the measured scope."""
    outputs = {
        MANIFEST: manifest_payload,
        release_path: release.encode("utf-8"),
        DOCS / "PROJECT.md": appended_payload(
            DOCS / "PROJECT.md", "## Local experimental 0.36.0 package", status),
        DOCS / "VALIDATION.md": appended_payload(
            DOCS / "VALIDATION.md", "## 0.36.0 package consolidation", status.replace(
                "## Local experimental 0.36.0 package", "## 0.36.0 package consolidation")),
        DOCS / "DELIVERY-ORDER-v1.md": appended_payload(
            DOCS / "DELIVERY-ORDER-v1.md", "## Completed 0.36.0 consolidation checkpoint", status.replace(
                "## Local experimental 0.36.0 package", "## Completed 0.36.0 consolidation checkpoint")),
        DOCS / "REQUIREMENTS.md": appended_payload(
            DOCS / "REQUIREMENTS.md", "## 0.36.0 procedural release evidence", status.replace(
                "## Local experimental 0.36.0 package", "## 0.36.0 procedural release evidence")),
        DOCS / "ROADMAP.md": appended_payload(
            DOCS / "ROADMAP.md", "## 0.36.0 procedural release checkpoint", status.replace(
                "## Local experimental 0.36.0 package", "## 0.36.0 procedural release checkpoint")),
        DOCS / "USER_GUIDE.md": appended_payload(
            DOCS / "USER_GUIDE.md", "## Installing the local experimental 0.36.0 package", guide),
    }
    require(len(outputs) == 8, "Unexpected finalization destination set")
    publish_transaction(outputs)
    print(json.dumps({
        "passed": True,
        "archive": str(ARCHIVE),
        "archive_sha256": PACKAGE_SHA256,
        "regression_tests": 1017,
        "package_tests": 209,
        "release_note": str(release_path),
        "manifest": str(MANIFEST),
    }, indent=2))


if __name__ == "__main__":
    main()
