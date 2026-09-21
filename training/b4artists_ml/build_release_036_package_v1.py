"""Build deterministic experimental 0.36.0 from frozen release evidence."""
from pathlib import Path
import ast
import hashlib
import json
import zipfile


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training/b4artists_ml/results"
DOCS = ROOT / "docs/b4artists_ml"
OUTPUT = ROOT / "releases/b4artists_ml_v0.36.0.zip"
PLAN = RESULTS / "release-036-v1-suite-plan.json"
PLAN_SHA256 = "730d386581ceb7515b2d0af0c4e3c884b63bd791b87b78c3bf65f2ea6a17d502"
RUNNER = ROOT / "training/b4artists_ml/run_release_036_regression_v1.py"
HARNESS = ROOT / "training/b4artists_ml/run_unittest_report.py"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_hashes():
    return {
        path.relative_to(ROOT).as_posix(): sha(path)
        for path in sorted((ROOT / "b4artists_ml").glob("*.py"))
    }


def distributable_hashes():
    return {
        path.relative_to(ROOT).as_posix(): sha(path)
        for path in sorted((ROOT / "b4artists_ml").rglob("*"))
        if path.is_file()
        and (path.suffix in (".py", ".json", ".md", ".npz") or path.name == "LICENSE")
    }


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    if OUTPUT.exists():
        raise RuntimeError("Release archive already exists; retain it or choose a new release")
    regression_path = RESULTS / "release-036-v1-regression.json"
    regression_digest = sha(regression_path)
    regression = read(regression_path)
    current = runtime_hashes()
    distributable = distributable_hashes()
    require(sha(PLAN) == PLAN_SHA256, "Frozen release suite plan changed")
    plan = read(PLAN)
    plan_rows = plan.get("suites", ())
    require(plan.get("release") == "0.36.0" and plan.get("suite_count") == 87 and
            plan.get("tests") == 1017 and plan.get("candidate_suite_count") == 124 and
            plan.get("excluded_suite_count") == 37 and len(plan.get("excluded_suites", ())) == 37,
            "Invalid curated suite plan")
    for row in list(plan_rows) + list(plan["excluded_suites"]):
        test_path = ROOT / "tests" / (row["suite"] + ".py")
        require(test_path.is_file() and sha(test_path) == row["test_sha256"],
                "Test source changed after suite inventory: " + row["suite"])
    require(regression.get("passed") and regression.get("release") == "0.36.0",
            "Release regression did not pass")
    require(regression.get("suite_count") == 87 and regression.get("tests") == 1017,
            "Unexpected regression dimensions")
    require(regression.get("runtime_source_count") == 44 and
            regression.get("runtime_source_sha256") == current,
            "Regression runtime does not match current source")
    require(regression.get("distributable_member_count") == len(distributable) and
            regression.get("distributable_member_sha256") == distributable,
            "Regression distributable members do not match current package source")
    require(regression.get("suite_plan_sha256") == PLAN_SHA256 and
            regression.get("runner_sha256") == sha(RUNNER) and
            regression.get("unittest_harness_sha256") == sha(HARNESS),
            "Regression evidence tools or suite plan changed")
    expected = [(row["suite"], row["tests"]) for row in plan_rows]
    actual = [(row.get("suite"), row.get("tests")) for row in regression.get("suites", ())]
    require(actual == expected and len(set(actual)) == 87, "Regression suite rows do not match plan")
    child_report_digests = {}
    for summary, plan_row in zip(regression["suites"], plan_rows):
        report_path = ROOT / summary["report"]
        require(summary.get("passed") and summary.get("assertions_completed_before_shutdown") and
                report_path.is_file() and sha(report_path) == summary.get("report_sha256"),
                "Invalid child report summary: " + plan_row["suite"])
        child = read(report_path)
        child_report_digests[report_path] = summary["report_sha256"]
        require(child.get("passed") and child.get("python_optimize") == 0 and
                child.get("tests") == plan_row["tests"] and
                not child.get("failures") and not child.get("errors") and not child.get("skips") and
                child.get("test_sha256") == plan_row["test_sha256"] and
                child.get("runtime_source_sha256") == current and
                child.get("distributable_member_sha256") == distributable,
                "Invalid child regression report: " + plan_row["suite"])
    claims = regression.get("claims", {})
    require(claims.get("procedural_release") and not claims.get("learned_temporal_qualified") and
            not claims.get("cascadeur_parity") and not claims.get("full_goal_complete"),
            "Regression claim boundary is invalid")

    ui_digests = {}
    for name in ("breakdown-pose-ui-v1.json", "transition-timing-transfer-ui-v1.json"):
        evidence_path = DOCS / name
        evidence = read(evidence_path)
        ui_digests[evidence_path] = sha(evidence_path)
        require(evidence.get("passed") and evidence.get("source_action_unchanged"),
                "Foreground workflow did not pass: " + name)
        require(evidence.get("runtime_source_count") == 44 and
                evidence.get("runtime_source_sha256") == current,
                "Foreground workflow does not match current runtime: " + name)

    tree = ast.parse((ROOT / "b4artists_ml/__init__.py").read_bytes())
    info = next(
        node.value for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "bl_info" for target in node.targets)
    )
    index = next(i for i, key in enumerate(info.keys) if key.value == "version")
    require(ast.literal_eval(info.values[index]) == (0, 36, 0), "Unexpected add-on version")
    author_index = next(i for i, key in enumerate(info.keys) if key.value == "author")
    require(ast.literal_eval(info.values[author_index]) == "axlbot", "Unexpected add-on author")
    require("axlbot <axleonex@gmail.com>" in
            (ROOT / "b4artists_ml/ATTRIBUTION.md").read_text(encoding="utf-8-sig"),
            "Required axlbot attribution is missing")

    paths = {
        path.relative_to(ROOT).as_posix(): path
        for path in (ROOT / "b4artists_ml").rglob("*")
        if path.is_file()
        and (path.suffix in (".py", ".json", ".md", ".npz") or path.name == "LICENSE")
    }
    forbidden = (b"jonvilario", b"atonlotus")
    require(set(paths) == set(distributable), "Build member selection differs from regression")
    payloads = {name: path.read_bytes() for name, path in paths.items()}
    for name, payload in payloads.items():
        require(hashlib.sha256(payload).hexdigest() == distributable[name],
                "Package source changed after regression freeze: " + name)
        normalized_name = name.lower().encode("utf-8")
        require(not any(value in payload.lower() or value in normalized_name for value in forbidden),
                "Forbidden identity in package member: " + name)
        if name.endswith(".py"):
            ast.parse(payload)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, payload in sorted(payloads.items()):
            item = zipfile.ZipInfo(name, date_time=(2026, 9, 12, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = 0o644 << 16
            archive.writestr(item, payload, compresslevel=9)
    with zipfile.ZipFile(OUTPUT) as archive:
        require(set(archive.namelist()) == set(payloads), "Archive member set mismatch")
        require(all(archive.read(name) == payload for name, payload in payloads.items()),
                "Archive payload mismatch")
    require(distributable_hashes() == distributable and sha(regression_path) == regression_digest and
            sha(PLAN) == PLAN_SHA256 and sha(RUNNER) == regression["runner_sha256"] and
            sha(HARNESS) == regression["unittest_harness_sha256"] and
            all(sha(path) == digest for path, digest in child_report_digests.items()) and
            all(sha(path) == digest for path, digest in ui_digests.items()),
            "Source or release evidence changed during package build")

    report = {
        "schema": 1,
        "version": "0.36.0",
        "files": len(paths),
        "bytes": OUTPUT.stat().st_size,
        "sha256": sha(OUTPUT),
        "package_matches_source": True,
        "forbidden_identities_absent": True,
        "experimental": True,
        "full_goal_complete": False,
        "ready_for_local_testing": False,
        "runtime_sha256": current,
        "distributable_member_sha256": distributable,
        "suite_plan_sha256": PLAN_SHA256,
        "regression": {
            "tests": 1017,
            "suites": 87,
            "evidence": regression_path.relative_to(ROOT).as_posix(),
            "sha256": regression_digest,
        },
        "foreground_workflows": [
            "docs/b4artists_ml/breakdown-pose-ui-v1.json",
            "docs/b4artists_ml/transition-timing-transfer-ui-v1.json",
        ],
        "exact_package_checks": "pending",
        "host_shutdown_qualified": False,
        "independent_human_usability": "unknown",
        "cascadeur_comparisons": 0,
        "qualification_note": (
            "Experimental standalone Bforartists package with deterministic workflow, posing, contact, "
            "quadruped and interpolation assistance. It does not qualify clean host shutdown, learned "
            "temporal generation, independent animator acceptance, or Cascadeur parity."
        ),
    }
    (DOCS / "package-test-v0.36.0.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("version", "files", "bytes", "sha256")}, indent=2))


if __name__ == "__main__":
    main()
