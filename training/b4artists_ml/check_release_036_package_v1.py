"""Verify the extracted 0.36.0 package with runtime network/process calls denied."""
from pathlib import Path
import hashlib
import importlib
import json
import os
import subprocess
import sys
import time
import zipfile


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
TAG = "release-036-package-v4"
CACHE = ROOT / "training/b4artists_ml/cache" / TAG
OUT = ROOT / "training/b4artists_ml/results" / (TAG + ".json")
ARCHIVE = ROOT / "releases/b4artists_ml_v0.36.0.zip"
PLAN = ROOT / "training/b4artists_ml/results/release-036-v1-suite-plan.json"
PLAN_SHA256 = "730d386581ceb7515b2d0af0c4e3c884b63bd791b87b78c3bf65f2ea6a17d502"
MANIFEST = ROOT / "docs/b4artists_ml/package-test-v0.36.0.json"
FEATURE_COUNTS = {
    "test_b4artists_ml_joint_limit_presets_v1": 5,
    "test_b4artists_ml_chest_target_v1": 3,
    "test_b4artists_ml_chest_orientation_v1": 3,
    "test_b4artists_ml_neck_target_v1": 4,
    "test_b4artists_ml_target_reset_v1": 8,
    "test_b4artists_ml_target_mirror_v1": 7,
    "test_b4artists_ml_rig_diagnostics_v1": 8,
    "test_b4artists_ml_mapping_corrections_v1": 11,
    "test_b4artists_ml_pose_reuse_v1": 8,
    "test_b4artists_ml_pole_align_v1": 4,
    "test_b4artists_ml_pole_flip_v1": 4,
    "test_b4artists_ml_pole_distance_v1": 5,
    "test_b4artists_ml_pose_asset_v1": 5,
    "test_b4artists_ml_contact_interval_edit_v1": 6,
    "test_b4artists_ml_prop_holds_v1": 5,
    "test_b4artists_ml_moving_platforms_v1": 5,
    "test_b4artists_ml_contact_visualization_v1": 6,
    "test_b4artists_ml_quadruped_head_v1": 7,
    "test_b4artists_ml_quadruped_spine_follow_v1": 8,
    "test_b4artists_ml_quadruped_poles_v1": 6,
    "test_b4artists_ml_quadruped_pole_match_v1": 8,
    "test_b4artists_ml_quadruped_gait_phase_v1": 5,
    "test_b4artists_ml_quadruped_target_reset_v1": 9,
    "test_b4artists_ml_quadruped_target_mirror_v1": 8,
    "test_b4artists_ml_quadruped_pose_asset_v1": 7,
    "test_b4artists_ml_quadruped_pole_align_v1": 6,
    "test_b4artists_ml_quadruped_pole_controls_v1": 8,
    "test_b4artists_ml_timing_controls_v1": 7,
    "test_b4artists_ml_transition_timing_v1": 9,
    "test_b4artists_ml_transition_window_v1": 10,
    "test_b4artists_ml_breakdown_pose_v1": 8,
    "test_b4artists_ml_transition_timing_transfer_v1": 6,
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def member_hashes(root):
    return {
        path.relative_to(root).as_posix(): sha(path)
        for path in sorted((root / "b4artists_ml").rglob("*"))
        if path.is_file()
        and (path.suffix in (".py", ".json", ".md", ".npz") or path.name == "LICENSE")
    }


def selected_plan():
    require(sha(PLAN) == PLAN_SHA256, "Frozen package suite plan changed")
    value = json.loads(PLAN.read_text(encoding="utf-8"))
    require(value.get("schema") == 1 and value.get("release") == "0.36.0" and
            value.get("suite_count") == 87 and value.get("tests") == 1017 and
            value.get("candidate_suite_count") == 124 and
            value.get("excluded_suite_count") == 37,
            "Invalid frozen package suite plan")
    rows = value.get("suites", ())[-32:]
    require(len(rows) == 32 and {row["suite"] for row in rows} == set(FEATURE_COUNTS) and
            sum(FEATURE_COUNTS.values()) == 209,
            "Unexpected package-test suite dimensions")
    for row in rows:
        path = ROOT / "tests" / (row["suite"] + ".py")
        require(path.is_file() and sha(path) == row["test_sha256"],
                "Package test source changed: " + row["suite"])
    return rows


def group_plan(rows, index):
    require(index in range(8), "Invalid package-test group")
    group = rows[index * 4:(index + 1) * 4]
    require(len(group) == 4, "Unexpected package-test group size")
    return group


def group_output(index):
    return OUT.with_name(f"{TAG}-group-{index + 1}.json")


def host():
    import unittest
    require(sys.flags.optimize == 0, "Package qualification cannot run with optimized assertions")
    expected_checker = os.environ.get("B4ML_CHECKER_SHA256", "")
    require(expected_checker and sha(HERE) == expected_checker,
            "Package checker identity does not match the parent launch")
    denied = []

    def audit(event, args):
        if event in ("socket.connect", "socket.connect_ex", "socket.getaddrinfo",
                     "socket.sendto", "subprocess.Popen", "os.system"):
            denied.append(event)
            raise RuntimeError("Offline package check blocks " + event)

    sys.addaudithook(audit)
    import socket
    try:
        socket.getaddrinfo("offline-self-test.invalid", 443)
    except RuntimeError:
        pass
    require(denied == ["socket.getaddrinfo"], "Offline guard self-test failed")
    denied.clear()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected_members = manifest.get("distributable_member_sha256")
    before_members = member_hashes(CACHE)
    require(before_members == expected_members, "Extracted package differs from build manifest")
    os.environ["B4ML_PACKAGE"] = str(CACHE)
    sys.path[:0] = [str(CACHE), str(ROOT / "tests")]
    import b4artists_ml
    require(b4artists_ml.bl_info["version"] == (0, 36, 0), "Unexpected extracted add-on version")
    group_index = int(os.environ.get("B4ML_GROUP_INDEX", "-1"))
    plan = group_plan(selected_plan(), group_index)
    expected_tests = sum(FEATURE_COUNTS[row["suite"]] for row in plan)
    suite = unittest.TestSuite()
    for row in plan:
        module = importlib.import_module(row["suite"])
        local_classes = sorted(
            (value for value in vars(module).values()
             if isinstance(value, type) and issubclass(value, unittest.TestCase)
             and value.__module__ == module.__name__),
            key=lambda value: value.__name__)
        loaded = unittest.TestSuite(
            unittest.defaultTestLoader.loadTestsFromTestCase(value) for value in local_classes)
        require(loaded.countTestCases() == FEATURE_COUNTS[row["suite"]],
                "Feature-defined test count changed for package suite: " + row["suite"])
        suite.addTest(loaded)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    modules = {
        name: str(Path(module.__file__).resolve())
        for name, module in sys.modules.items()
        if (name == "b4artists_ml" or name.startswith("b4artists_ml."))
        and getattr(module, "__file__", None)
    }
    isolated = bool(modules) and all(
        Path(path).is_relative_to(CACHE.resolve()) for path in modules.values())
    after_members = member_hashes(CACHE)
    tests_unchanged = all(
        sha(ROOT / "tests" / (row["suite"] + ".py")) == row["test_sha256"] for row in plan)
    passed = (result.wasSuccessful() and result.testsRun == expected_tests and not result.skipped and
              not denied and isolated and before_members == after_members and tests_unchanged and
              sha(PLAN) == PLAN_SHA256)
    report = {
        "schema": 1,
        "passed": passed,
        "tests": result.testsRun,
        "suite_count": len(plan),
        "group_index": group_index,
        "selected_suites": [row["suite"] for row in plan],
        "failures": [(test.id(), trace) for test, trace in result.failures],
        "errors": [(test.id(), trace) for test, trace in result.errors],
        "skips": len(result.skipped),
        "offline_guard_self_test": True,
        "denied_runtime_calls": denied,
        "all_runtime_imports_from_package": isolated,
        "package_members_unchanged_during_tests": before_members == after_members,
        "test_sources_unchanged_during_tests": tests_unchanged,
        "suite_plan_sha256": sha(PLAN),
        "checker_sha256": sha(HERE),
        "modules": modules,
        "distributable_member_sha256": after_members,
        "full_goal_complete": False,
        "human_reviews": 0,
        "cascadeur_comparisons": 0,
    }
    group_output(group_index).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("B4ML_RELEASE_036_PACKAGE: " + json.dumps(report), flush=True)
    if not passed:
        raise SystemExit(1)


def members_match_source():
    source = {
        path.relative_to(ROOT).as_posix(): path.read_bytes()
        for path in (ROOT / "b4artists_ml").rglob("*")
        if path.is_file()
        and (path.suffix in (".py", ".json", ".md", ".npz") or path.name == "LICENSE")
    }
    with zipfile.ZipFile(ARCHIVE) as package:
        return (set(package.namelist()) == set(source)
                and all(package.read(name) == payload for name, payload in source.items()))


def main():
    group_outputs = [group_output(index) for index in range(8)]
    if CACHE.exists() or OUT.exists() or any(path.exists() for path in group_outputs):
        raise RuntimeError("Package evidence already exists; retain it and use a new run identifier")
    require(sys.flags.optimize == 0, "Package qualification cannot run with optimized assertions")
    plan = selected_plan()
    frozen_tests = {row["suite"]: row["test_sha256"] for row in plan}
    frozen_source = member_hashes(ROOT)
    checker_digest = sha(HERE)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(manifest.get("version") == "0.36.0" and
            manifest.get("sha256") == sha(ARCHIVE) and
            manifest.get("distributable_member_sha256") == frozen_source,
            "Build manifest does not bind the current archive and source")
    require(members_match_source(), "Archive does not exactly match source")
    CACHE.mkdir(parents=True)
    with zipfile.ZipFile(ARCHIVE) as package:
        require(all(not Path(name).is_absolute() and ".." not in Path(name).parts
                    for name in package.namelist()), "Unsafe archive member path")
        package.extractall(CACHE)
    require(member_hashes(CACHE) == frozen_source, "Extracted package differs from source")
    started = time.perf_counter()
    groups = []
    for group_index, output in enumerate(group_outputs):
        unchanged_before = (sha(HERE) == checker_digest and sha(PLAN) == PLAN_SHA256 and
                            sha(ARCHIVE) == manifest["sha256"] and
                            member_hashes(ROOT) == frozen_source and
                            member_hashes(CACHE) == frozen_source and
                            all(sha(ROOT / "tests" / (name + ".py")) == digest
                                for name, digest in frozen_tests.items()))
        require(unchanged_before, "Package evidence changed before group launch")
        log = CACHE.with_name(f"{TAG}-group-{group_index + 1}.log")
        child_env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="4",
                         B4ML_PACKAGE=str(CACHE), B4ML_CHECKER_SHA256=checker_digest,
                         B4ML_GROUP_INDEX=str(group_index))
        child_env.pop("PYTHONOPTIMIZE", None)
        with log.open("w", encoding="utf-8") as stream:
            process = subprocess.run(
                [os.environ.get("B4ML_BFORARTISTS", "X:/5.1.0/bforartists.exe"),
                 "--background", "--factory-startup", "--disable-autoexec",
                 "--python", str(HERE), "--", "--host"],
                cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, timeout=900,
                env=child_env)
        require(output.is_file(), "Package-test group produced no report")
        group = json.loads(output.read_text(encoding="utf-8"))
        require(group.get("passed") and group.get("group_index") == group_index and
                group.get("checker_sha256") == checker_digest,
                "Package-test group did not pass")
        group.update({
            "process_exit_code": process.returncode,
            "assertions_completed_before_shutdown": True,
            "host_shutdown_qualified": process.returncode == 0,
            "report": output.relative_to(ROOT).as_posix(),
            "report_sha256": sha(output),
            "log": log.relative_to(ROOT).as_posix(),
            "log_sha256": sha(log),
        })
        groups.append(group)
    unchanged = (sha(HERE) == checker_digest and sha(PLAN) == PLAN_SHA256 and
                 sha(ARCHIVE) == manifest["sha256"] and
                 member_hashes(ROOT) == frozen_source and member_hashes(CACHE) == frozen_source and
                 all(sha(ROOT / "tests" / (name + ".py")) == digest
                     for name, digest in frozen_tests.items()))
    report = {
        "schema": 1,
        "passed": all(group["passed"] for group in groups),
        "tests": sum(group["tests"] for group in groups),
        "suite_count": sum(group["suite_count"] for group in groups),
        "groups": groups,
        "failures": [row for group in groups for row in group["failures"]],
        "errors": [row for group in groups for row in group["errors"]],
        "skips": sum(group["skips"] for group in groups),
        "all_runtime_imports_from_package": all(
            group["all_runtime_imports_from_package"] for group in groups),
        "offline_guard_self_test": all(group["offline_guard_self_test"] for group in groups),
        "denied_runtime_calls": [row for group in groups for row in group["denied_runtime_calls"]],
        "checker_sha256": checker_digest,
        "process_exit_codes": [group["process_exit_code"] for group in groups],
        "assertions_completed_before_shutdown": all(
            group["assertions_completed_before_shutdown"] for group in groups),
        "host_shutdown_qualified": all(group["host_shutdown_qualified"] for group in groups),
        "elapsed_seconds": time.perf_counter() - started,
        "package_sha256": sha(ARCHIVE),
        "exact_package": True,
        "package_members_match_source": members_match_source(),
        "source_package_plan_and_tests_unchanged": unchanged,
        "distributable_member_sha256": frozen_source,
        "suite_plan_sha256": PLAN_SHA256,
        "full_goal_complete": False,
        "human_reviews": 0,
        "cascadeur_comparisons": 0,
    }
    report["passed"] = bool(report["passed"] and report["tests"] == 209 and
                            report["suite_count"] == 32 and not report["failures"] and
                            not report["errors"] and report["skips"] == 0 and
                            report["all_runtime_imports_from_package"] and
                            not report["denied_runtime_calls"] and
                            report["package_members_match_source"] and unchanged)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report.get(key) for key in
                      ("passed", "tests", "suite_count", "process_exit_code",
                       "elapsed_seconds", "package_sha256")}, indent=2))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    host() if "--host" in sys.argv else main()
