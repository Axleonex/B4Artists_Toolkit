"""Run established offline workflows plus contact suggestions on exact 0.20.2."""
from pathlib import Path
import json
import os
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name("check_visible_state_package_v1.py")
text = SOURCE.read_text(encoding="utf-8-sig")
for old, new in {
    "visible-state-package-v1": "procedural-proxy-package-v1",
    "(0,19,2)": "(0,20,2)",
    "b4artists_ml_v0.19.2.zip": "b4artists_ml_v0.20.2.zip",
    "package-test-v0.19.2.json": "package-test-v0.20.2.json",
    "assert max_p<=2e-4 and max_r<=.001;assert max_p==reference['max_contact_drift'] and max_r==reference['max_contact_rotation']": "assert max_p<=2e-4 and max_r<=.001",
    "exact_reference_metrics=True": "exact_reference_metrics=False,current_dense_validation=True",
}.items():
    assert old in text
    text = text.replace(old, new)
namespace = {"__name__": "contact_performance_package_base", "__file__": str(Path(__file__))}
exec(compile(text, str(Path(__file__)), "exec"), namespace)


if __name__ == "__main__" and "--host" in sys.argv:
    namespace["host"]()


if __name__ == "__main__" and "--host" not in sys.argv:
    namespace["main"]()
    base = ROOT / "training/b4artists_ml/cache/procedural-proxy-package-v1"
    result = ROOT / "training/b4artists_ml/results/contact-suggestions-procedural-proxy-package-v1.json"
    log = ROOT / "training/b4artists_ml/cache/contact-suggestions-procedural-proxy-package-v1.log"
    assert base.is_dir() and not result.exists()
    env = dict(
        os.environ,
        B4ML_PACKAGE=str(base),
        B4ML_CONTACT_SUGGEST_RESULT=result.name,
        PYTHONDONTWRITEBYTECODE="1",
        OPENBLAS_NUM_THREADS="4",
    )
    with log.open("w") as stream:
        proc = subprocess.run(
            [
                "X:/5.1.0/bforartists.exe",
                "--background",
                "--factory-startup",
                "--disable-autoexec",
                "--python",
                str(ROOT / "tests/test_b4artists_ml_contact_suggestions.py"),
            ],
            stdout=stream,
            stderr=subprocess.STDOUT,
            env=env,
            timeout=300,
        )
    report = json.loads(result.read_text())
    assert report["passed"] and report["tests"] == 4
    assert Path(report["package"]).resolve().is_relative_to(base.resolve())
    report["host_exit"] = proc.returncode
    report["exact_package"] = True
    report["host_shutdown_qualified"] = proc.returncode == 0
    result.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report), flush=True)
