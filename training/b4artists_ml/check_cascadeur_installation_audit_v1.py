"""Record read-only Cascadeur installation and frozen-asset provenance."""

from pathlib import Path
import ctypes
import hashlib
import json
import os
import struct


ROOT = Path(__file__).resolve().parents[2]
TRAIN = ROOT / "training" / "b4artists_ml"
PROTOCOL = TRAIN / "cascadeur_comparison_protocol_v2.json"
MANIFEST = TRAIN / "reference-assets-v1" / "manifest.json"
OUT = TRAIN / "results" / "cascadeur-installation-audit-v1.json"
CASCADEUR = Path(os.environ.get(
    "B4ML_CASCADEUR_EXE", r"C:\Program Files\Cascadeur\cascadeur.exe"))


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def windows_file_version(path):
    """Read the PE fixed-file version without launching the application."""
    if os.name != "nt":
        return None
    version = ctypes.WinDLL("version", use_last_error=True)
    size = version.GetFileVersionInfoSizeW(str(path), None)
    if not size:
        return None
    data = ctypes.create_string_buffer(size)
    if not version.GetFileVersionInfoW(str(path), 0, size, data):
        return None
    value = ctypes.c_void_p()
    length = ctypes.c_uint()
    if not version.VerQueryValueW(data, "\\", ctypes.byref(value), ctypes.byref(length)):
        return None
    fixed = ctypes.string_at(value.value, 16)
    version_ms, version_ls = struct.unpack_from("<II", fixed, 8)
    major, minor = version_ms >> 16, version_ms & 0xFFFF
    build, revision = version_ls >> 16, version_ls & 0xFFFF
    return f"{major}.{minor}.{build}.{revision}"


def main():
    if OUT.exists():
        raise RuntimeError(f"audit already exists: {OUT}")
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assets = []
    for item in manifest["assets"]:
        path = ROOT / item["fbx"]
        assets.append({
            "id": item["id"],
            "path": item["fbx"],
            "exists": path.is_file(),
            "bytes": path.stat().st_size if path.is_file() else None,
            "sha256": sha(path) if path.is_file() else None,
            "expected_sha256": item["fbx_sha256"],
            "matches_expected": path.is_file() and sha(path) == item["fbx_sha256"],
        })
    executable_present = CASCADEUR.is_file()
    report = {
        "schema": "b4ml-cascadeur-installation-audit-v1",
        "status": "INSTALLATION_PRESENT_IMPORT_AUDIT_PENDING" if executable_present
                  else "INSTALLATION_NOT_FOUND",
        "scope": "Read-only executable/version and frozen-FBX provenance; no Cascadeur launch, import, conversion, entitlement change, or connector change.",
        "cascadeur": {
            "executable": str(CASCADEUR),
            "present": executable_present,
            "bytes": CASCADEUR.stat().st_size if executable_present else None,
            "sha256": sha(CASCADEUR) if executable_present else None,
            "file_version": windows_file_version(CASCADEUR) if executable_present else None,
            "edition": None,
            "entitlement": None,
            "settings_exported": False,
        },
        "protocol": {
            "path": PROTOCOL.relative_to(ROOT).as_posix(),
            "sha256": sha(PROTOCOL),
            "schema": protocol["schema"],
            "status": protocol["status"],
        },
        "portable_assets": {
            "manifest": MANIFEST.relative_to(ROOT).as_posix(),
            "manifest_sha256": sha(MANIFEST),
            "assets": assets,
            "all_frozen_fbx_match": all(item["matches_expected"] for item in assets),
            "import_conversion_audit": False,
        },
        "claim_boundary": {
            "cascadeur_import_verified": False,
            "parity_verified": False,
            "surpasses_verified": False,
            "independent_animator_sessions": 0,
            "full_goal_complete": False,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
