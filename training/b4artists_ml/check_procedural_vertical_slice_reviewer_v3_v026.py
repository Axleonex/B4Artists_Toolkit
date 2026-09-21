"""Validate the frozen procedural vertical-slice reviewer and its source identity."""
from pathlib import Path
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import tempfile


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
ROOT = HERE.parents[2]
SOURCE = TRAIN / "results/procedural-vertical-slice-v13-v026"
AGGREGATE = SOURCE / "aggregate.json"
PROTOCOL_PATH = TRAIN / "procedural_vertical_slice_protocol_v13.json"
TEMPLATE = TRAIN / "procedural_vertical_slice_review_template_v2.html"
BUILD = TRAIN / "results/procedural-vertical-slice-reviewer-v3-v026"
OUT = BUILD / "validation.json"
PARENTS = [-1, 0, 1, 2, 3, 2, 5, 6, 2, 8, 9, 0, 11, 12, 0, 14, 15]
REQUIRED_METRICS = {
    "priority_matrix_error", "max_pin_residual", "max_sampled_limb_stretch",
    "max_penetration_body_fraction", "max_rotation_velocity_jump_rad_s",
    "contact_error_limb_fraction", "contact_orientation_error_radians",
    "flight_error_body_fraction", "scripted_interaction_count", "scripted_correction_count",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def finite_points(value):
    return (isinstance(value, list) and len(value) == 49 and all(
        isinstance(frame, list) and len(frame) == 17 and all(
            isinstance(point, list) and len(point) == 3 and all(
                isinstance(component, (int, float)) and not isinstance(component, bool) and math.isfinite(component)
                for component in point
            ) for point in frame
        ) for frame in value
    ))


def node_check(source):
    executable = shutil.which("node")
    if not executable:
        return False, "Node.js unavailable"
    handle = tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False)
    try:
        handle.write(source)
        handle.close()
        result = subprocess.run([executable, "--check", handle.name], capture_output=True, text=True, timeout=60)
        if result.returncode:
            raise ValueError("Embedded JavaScript syntax failed: " + (result.stderr or result.stdout))
        return True, None
    finally:
        try:
            os.unlink(handle.name)
        except OSError:
            pass


def main():
    if OUT.exists():
        raise RuntimeError("Reviewer validation evidence already exists")
    aggregate = read(AGGREGATE)
    protocol = read(PROTOCOL_PATH)
    manifest = read(BUILD / "manifest.json")
    data_path = BUILD / "review-data.json"
    raw = data_path.read_text(encoding="utf-8")
    data = json.loads(raw)
    page_path = BUILD / "reviewer.html"
    page = page_path.read_text(encoding="utf-8")
    if data["schema"] != "b4ml-procedural-vertical-slice-review-data-v2":
        raise ValueError("Unexpected review data schema")
    if manifest["schema"] != "b4ml-procedural-vertical-slice-reviewer-manifest-v2":
        raise ValueError("Unexpected reviewer manifest schema")
    if not sha(AGGREGATE) == data["aggregate_sha256"] == manifest["aggregate_sha256"]:
        raise ValueError("Aggregate identity mismatch")
    if not sha(PROTOCOL_PATH) == data["protocol_sha256"] == manifest["protocol_sha256"]:
        raise ValueError("Protocol identity mismatch")
    data_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    if data_hash != manifest["data_sha256"] or sha(page_path) != manifest["html_sha256"]:
        raise ValueError("Reviewer artifact hash mismatch")
    template = TEMPLATE.read_text(encoding="utf-8")
    expected_page = template.replace("__REVIEW_DATA__", raw.replace("<", "\\u003c")).replace("__DATA_SHA256__", data_hash)
    if page != expected_page:
        raise ValueError("Reviewer page is not the deterministic template/data composition")
    expected = [(profile, task) for profile in protocol["rigs"] for task in protocol["tasks"]]
    expected_ids = [f"{profile}/{task}" for profile, task in expected]
    if len(data["cases"]) != 32 or [case["id"] for case in data["cases"]] != expected_ids:
        raise ValueError("Reviewer case matrix or order changed")
    if data["parents"] != PARENTS or len(data["names"]) != 17 or len(data["roles"]) != 17:
        raise ValueError("Reviewer semantic hierarchy changed")
    ranked = sorted(expected_ids, key=lambda case_id: hashlib.sha256(
        (data["aggregate_sha256"] + ":" + case_id).encode()
    ).digest())
    corrected_as_a = set(ranked[:16])
    max_priority_error = 0.0
    for case, (profile, task) in zip(data["cases"], expected):
        if case["profile"] != profile or case["task"] != task:
            raise ValueError("Case metadata mismatch")
        expected_frames = [1.0 + index * 0.5 for index in range(49)]
        if case["frames"] != expected_frames or not math.isfinite(case["fps"]) or case["fps"] <= 0:
            raise ValueError("Case sampling changed: " + case["id"])
        if set(case["methods"]) != {"A", "B"} or not all(finite_points(value) for value in case["methods"].values()):
            raise ValueError("Malformed skeleton samples: " + case["id"])
        expected_mapping = {"A": "corrected", "B": "pre_contact"} if case["id"] in corrected_as_a else {"A": "pre_contact", "B": "corrected"}
        if {label: value["kind"] for label, value in case["reveal"].items()} != expected_mapping:
            raise ValueError("Blind assignment changed: " + case["id"])
        report_path = SOURCE / profile / task / "report.json"
        report = read(report_path)
        blend_path = ROOT / report["blend_path"]
        if (case["source_blend"] != report["blend_path"] or
                case["source_blend_sha256"] != report["blend_sha256"] or
                sha(blend_path) != report["blend_sha256"] or
                case["source_report_sha256"] != sha(report_path)):
            raise ValueError("Frozen source identity mismatch: " + case["id"])
        if not report["complete"] or not all(report["automated_gates"].values()):
            raise ValueError("Source case gates are no longer complete: " + case["id"])
        expected_contacts = [dict(limb=row[0], start=float(row[1]), end=float(row[2]))
                             for row in protocol["tasks"][task]["contacts"]]
        if case["contacts"] != expected_contacts:
            raise ValueError("Contact intervals changed: " + case["id"])
        if set(case["automated_metrics"]) != REQUIRED_METRICS:
            raise ValueError("Automated metric disclosure changed")
        indices = [int(round((value - 1.0) * 2.0)) for value in case["priority_frames"]]
        for index in indices:
            for a, b in zip(case["methods"]["A"][index], case["methods"]["B"][index]):
                max_priority_error = max(max_priority_error, max(abs(x - y) for x, y in zip(a, b)))
        if case["priority_variant_error"] > 1e-5:
            raise ValueError("Priority variant mismatch exceeds review tolerance")
        if not all(math.isfinite(value) for value in case["center"]) or not math.isfinite(case["radius"]) or case["radius"] <= 0:
            raise ValueError("Invalid display bounds")
    if max_priority_error > 1e-5:
        raise ValueError("Displayed priority poses changed between variants")
    a_count = sum(case["reveal"]["A"]["kind"] == "corrected" for case in data["cases"])
    if (a_count, len(data["cases"]) - a_count) != (16, 16) or manifest["balanced_blinding"] != {"corrected_as_A": 16, "corrected_as_B": 16}:
        raise ValueError("A/B assignment is not balanced")
    required = (
        "Lock rating and reveal", "Export completed review", "source_data_sha256",
        "b4ml-procedural-vertical-slice-human-review-v2", "localStorage", "naturalnessA",
        "contactA", "continuityA", "intentA", "correctionsA", "interactionsA",
        "human_authored:true", "Complete and lock all cases before export",
    )
    if any(value not in page for value in required):
        raise ValueError("Reviewer controls or export contract are missing")
    if re.search(r"<(script|link|img|iframe)[^>]+(?:src|href)\s*=", page, re.I) or "http://" in page or "https://" in page:
        raise ValueError("Reviewer must not load external dependencies")
    scripts = re.findall(r"<script>(.*?)</script>", page, re.S | re.I)
    if len(scripts) != 1:
        raise ValueError("Expected one embedded reviewer script")
    javascript_valid, javascript_note = node_check(scripts[0])
    report = dict(
        schema="b4ml-procedural-vertical-slice-reviewer-validation-v2",
        complete=True,
        cases=len(data["cases"]),
        variants=2,
        displayed_skeleton_frames=sum(len(case["frames"]) for case in data["cases"]) * 2,
        semantic_joints=17,
        source_scene_hashes_exact=True,
        source_report_hashes_exact=True,
        protocol_case_order_exact=True,
        deterministic_page_composition=True,
        finite_skeleton_samples=True,
        priority_variant_max_component_error=max_priority_error,
        balanced_blinding=True,
        identity_hidden_until_lock=True,
        automated_metrics_hidden_until_lock=True,
        complete_ratings_required_for_export=True,
        reviewer_identity_required_for_export=True,
        javascript_syntax_valid=javascript_valid,
        javascript_validation_note=javascript_note,
        external_dependencies=False,
        rendered_browser_validation=False,
        reviewed_cases=0,
        human_assessment="unverified until an independent animator exports a complete review",
        cascadeur_comparison=False,
        full_goal_complete=False,
        data_sha256=data_hash,
        html_sha256=sha(page_path),
        checker_sha256=sha(HERE),
    )
    temp = OUT.with_suffix(".tmp")
    temp.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temp, OUT)
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
