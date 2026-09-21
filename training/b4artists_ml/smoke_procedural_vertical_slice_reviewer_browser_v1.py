"""Qualify offline reviewer initialization in a real local Chromium renderer."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
BUILD = TRAIN / "results/procedural-vertical-slice-reviewer-v1"
PAGE = BUILD / "reviewer.html"
SCREENSHOT = BUILD / "browser-smoke.png"
OUT = BUILD / "browser-validation.json"
EDGE = Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists() or SCREENSHOT.exists():
        raise RuntimeError("Browser smoke evidence already exists")
    started = time.perf_counter()
    version = subprocess.run([str(EDGE), "--version"], capture_output=True, text=True, timeout=30)
    if version.returncode:
        raise RuntimeError("Cannot identify the local browser")
    with tempfile.TemporaryDirectory(prefix="b4ml-review-browser-") as profile:
        command = [
            str(EDGE), "--headless=new", "--disable-gpu", "--no-first-run",
            "--disable-background-networking", "--disable-component-update", "--disable-sync",
            "--metrics-recording-only", "--no-default-browser-check", "--disable-features=Translate",
            f"--user-data-dir={profile}", "--virtual-time-budget=2500", "--window-size=1440,1000",
            "--dump-dom", PAGE.as_uri(),
        ]
        rendered = subprocess.run(command, capture_output=True, text=True, timeout=90)
        if rendered.returncode:
            raise RuntimeError("Headless reviewer DOM load failed: " + rendered.stderr[-1000:])
        dom = rendered.stdout
        if "0 / 32 locked" not in dom or "Independent human assessment pending" not in dom:
            raise ValueError("Reviewer initialization markers are missing")
        case_match = re.search(r'<select id="case">(.*?)</select>', dom, re.S)
        if not case_match or case_match.group(1).count("<option") != 32:
            raise ValueError("The rendered case selector is incomplete")
        if not re.search(r'<canvas id="canvasA"[^>]+width="[1-9][0-9]+"[^>]+height="[1-9][0-9]+"', dom):
            raise ValueError("Candidate A canvas was not initialized")
        if not re.search(r'<canvas id="canvasB"[^>]+width="[1-9][0-9]+"[^>]+height="[1-9][0-9]+"', dom):
            raise ValueError("Candidate B canvas was not initialized")
        reveal = re.search(r'<div id="reveal"([^>]*)>(.*?)</div>', dom, re.S)
        if not reveal or reveal.group(2).strip() or "display: none" not in reveal.group(1):
            raise ValueError("Method identity was revealed before rating lock")
        shot = command[:-3] + [f"--screenshot={SCREENSHOT}", PAGE.as_uri()]
        captured = subprocess.run(shot, capture_output=True, text=True, timeout=90)
        if captured.returncode or not SCREENSHOT.exists() or SCREENSHOT.stat().st_size < 10000:
            raise RuntimeError("Headless reviewer screenshot failed")
    report = dict(
        schema="b4ml-procedural-vertical-slice-reviewer-browser-smoke-v1",
        complete=True,
        browser=version.stdout.strip() or version.stderr.strip(),
        local_file_loaded=True,
        javascript_initialized=True,
        rendered_case_options=32,
        candidate_canvases_initialized=True,
        method_identity_hidden_before_lock=True,
        screenshot_sha256=sha(SCREENSHOT),
        screenshot_bytes=SCREENSHOT.stat().st_size,
        reviewer_html_sha256=sha(PAGE),
        interaction_automation=False,
        reviewed_cases=0,
        human_assessment="unverified",
        full_goal_complete=False,
        script_sha256=sha(HERE),
        seconds=time.perf_counter() - started,
    )
    temp = OUT.with_suffix(".tmp")
    temp.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temp, OUT)
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
