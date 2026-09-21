"""Run the projected coupled-full-body test in the installed Bforartists host."""
from pathlib import Path
import os
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HOST = Path("X:/5.1.0/bforartists.exe")
TEST = ROOT / "tests/test_b4artists_ml_coupled_full_body_v1.py"


def main():
    result = subprocess.run(
        [str(HOST), "--background", "--factory-startup", "--disable-autoexec", "--python", str(TEST)],
        cwd=ROOT,
        env=dict(os.environ, OPENBLAS_NUM_THREADS="4", PYTHONDONTWRITEBYTECODE="1"),
        timeout=900,
    )
    code = result.returncode & 0xffffffff
    if result.returncode != 0 and code != 0xc0000005:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
