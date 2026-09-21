"""Build experimental 0.29.0 from the exact quadruped-orientation source regression."""
from pathlib import Path
import ast
import hashlib
import json
import zipfile


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training/b4artists_ml/results"
DOCS = ROOT / "docs/b4artists_ml"
OUTPUT = ROOT / "releases/b4artists_ml_v0.29.0.zip"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUTPUT.exists():
        raise RuntimeError("Package exists: " + str(OUTPUT))
    evidence_path = RESULTS / "quadruped-orientation-source-v1.json"
    evidence = read(evidence_path)
    protocol_path = ROOT / "training/b4artists_ml/quadruped_orientation_protocol_v1.json"
    protocol = read(protocol_path)
    assert evidence["complete"] and not evidence["full_goal_complete"]
    assert evidence["release"] == protocol["release"] == "0.29.0"
    assert evidence["suites"] == 51 and evidence["tests"] == 478
    assert evidence["runtime_hash_sets"] == 1
    assert evidence["protocol_sha256"] == sha(protocol_path)
    runtime = {path.relative_to(ROOT).as_posix(): sha(path)
               for path in (ROOT / "b4artists_ml").glob("*.py")}
    assert runtime == evidence["runtime_sha256"]
    tree = ast.parse((ROOT / "b4artists_ml/__init__.py").read_bytes())
    info = next(node.value for node in tree.body if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == "bl_info"
                        for target in node.targets))
    index = next(i for i, key in enumerate(info.keys) if key.value == "version")
    assert ast.literal_eval(info.values[index]) == (0, 29, 0)
    paths = {path.relative_to(ROOT).as_posix(): path
             for path in (ROOT / "b4artists_ml").rglob("*")
             if path.is_file()
             and (path.suffix in (".py", ".json", ".md", ".npz") or path.name == "LICENSE")}
    forbidden = (b"jonvilario", b"atonlotus")
    for path in paths.values():
        payload = path.read_bytes()
        assert not any(name in payload.lower() for name in forbidden)
        if path.suffix == ".py":
            ast.parse(payload)
    with zipfile.ZipFile(OUTPUT, "x", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, path in sorted(paths.items()):
            item = zipfile.ZipInfo(name, date_time=(2026, 9, 11, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = 0o644 << 16
            archive.writestr(item, path.read_bytes(), compresslevel=9)
    with zipfile.ZipFile(OUTPUT) as archive:
        assert set(archive.namelist()) == set(paths)
        assert all(archive.read(name) == path.read_bytes() for name, path in paths.items())
    report = {
        "version": "0.29.0",
        "files": len(paths),
        "bytes": OUTPUT.stat().st_size,
        "sha256": sha(OUTPUT),
        "package_matches_source": True,
        "forbidden_identities_absent": True,
        "experimental": True,
        "full_goal_complete": False,
        "ready_for_local_testing": False,
        "runtime_sha256": runtime,
        "source_regression": {"passed": True, "suites": evidence["suites"],
                              "tests": evidence["tests"],
                              "evidence": evidence_path.relative_to(ROOT).as_posix()},
        "quadruped_orientation": {"profiles": ["Rigify cat", "Rigify horse", "Rigify wolf"],
                                    "family": "quadruped", "schema": "quadruped_v1",
                                    "qualified": protocol["claim_boundaries"]["qualified"],
                                    "not_qualified": protocol["claim_boundaries"]["not_qualified"]},
        "exact_package_checks": "pending",
        "host_shutdown_qualified": False,
        "human_reviews": 0,
        "cascadeur_comparisons": 0
    }
    meta = DOCS / "package-test-v0.29.0.json"
    meta.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("version", "files", "bytes", "sha256")}, indent=2))


if __name__ == "__main__":
    main()
