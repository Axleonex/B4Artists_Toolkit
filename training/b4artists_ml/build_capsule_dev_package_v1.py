"""Build a deterministic development archive for the bounded capsule slice."""

from pathlib import Path
import hashlib
import json
import zipfile


ROOT = Path(__file__).resolve().parents[2]
VERSION = "0.37.28-dev"
ARCHIVE = ROOT / f"releases/b4artists_ml_v{VERSION}.zip"
REPORT = ROOT / f"docs/b4artists_ml/package-test-v{VERSION}.json"


def packaged_source():
    return {
        path.relative_to(ROOT).as_posix(): path.read_bytes()
        for path in sorted((ROOT / "b4artists_ml").rglob("*"))
        if path.is_file()
        and (path.suffix in {".py", ".json", ".md", ".npz"} or path.name == "LICENSE")
    }


def main():
    source = packaged_source()
    if ARCHIVE.exists():
        raise RuntimeError(f"development archive already exists: {ARCHIVE}")
    with zipfile.ZipFile(ARCHIVE, "x", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=9) as archive:
        for name, payload in sorted(source.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 9, 13, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, payload, compresslevel=9)
    with zipfile.ZipFile(ARCHIVE) as archive:
        assert archive.namelist() == sorted(source)
        assert archive.testzip() is None
        assert all(archive.read(name) == payload
                   for name, payload in source.items())

    prior = json.loads(
        (ROOT / "docs/b4artists_ml/package-test-v0.37.27-dev.json").read_text(
            encoding="utf-8"))
    report = dict(prior)
    report.update({
        "version": VERSION,
        "files": len(source),
        "bytes": ARCHIVE.stat().st_size,
        "sha256": hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
        "package_matches_source": True,
        "runtime_sha256": {
            name: hashlib.sha256(payload).hexdigest()
            for name, payload in source.items()
        },
        "blender_binding_qualification": "pending",
        "affected_regression": "pending",
        "foreground_lifecycle": "pending",
    })
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "archive": str(ARCHIVE),
        "version": VERSION,
        "files": len(source),
        "bytes": ARCHIVE.stat().st_size,
        "sha256": report["sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
