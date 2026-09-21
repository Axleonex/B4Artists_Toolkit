"""Independently verify the 0.37 development archive against current source."""
from pathlib import Path
import hashlib
import json
import os
import zipfile


ROOT = Path(__file__).resolve().parents[2]
VERSION = os.environ.get("B4ML_DEV_VERSION", "0.37.2-dev")
if not VERSION or any(token in VERSION for token in ("/", "\\", "..")):
    raise ValueError("B4ML_DEV_VERSION must be a simple release label")
ARCHIVE = ROOT / f"releases/b4artists_ml_v{VERSION}.zip"
REPORT = ROOT / f"docs/b4artists_ml/package-test-v{VERSION}.json"


def main():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    source = {
        path.relative_to(ROOT).as_posix(): path.read_bytes()
        for path in sorted((ROOT / "b4artists_ml").rglob("*"))
        if path.is_file()
        and (path.suffix in {".py", ".json", ".md", ".npz"} or path.name == "LICENSE")
    }
    with zipfile.ZipFile(ARCHIVE) as archive:
        names = archive.namelist()
        assert names == sorted(source)
        assert all(archive.read(name) == payload for name, payload in source.items())
        assert archive.testzip() is None
    assert report["package_matches_source"]
    assert report["files"] == len(source)
    assert hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() == report["sha256"]
    print(f"archive=PASS members={len(source)} bytes={ARCHIVE.stat().st_size} sha256={report['sha256']}")


if __name__ == "__main__":
    main()
