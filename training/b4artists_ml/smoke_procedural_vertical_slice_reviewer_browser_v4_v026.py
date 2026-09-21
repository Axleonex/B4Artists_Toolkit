"""Exercise reviewer behavior in isolated local Edge through the DevTools protocol.

Synthetic inputs exist only in a temporary browser profile and never count as human review.
"""
from pathlib import Path
import base64
import hashlib
import json
import os
import subprocess
import tempfile
import time
import urllib.request

import websocket


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
BUILD = TRAIN / "results/procedural-vertical-slice-reviewer-v3-v026"
PAGE = BUILD / "reviewer.html"
SCREENSHOT = BUILD / "browser-interaction-smoke-v3.png"
OUT = BUILD / "browser-interaction-validation-v4.json"
EDGE = Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CDP:
    def __init__(self, url):
        self.socket = websocket.create_connection(url, timeout=10, origin="http://localhost")
        self.identifier = 0
        self.exceptions = []

    def command(self, method, params=None):
        self.identifier += 1
        identifier = self.identifier
        self.socket.send(json.dumps({"id": identifier, "method": method, "params": params or {}}))
        deadline = time.monotonic() + 15.0
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"CDP {method} did not return command id {identifier}")
            self.socket.settimeout(max(0.1, remaining))
            message = json.loads(self.socket.recv())
            if message.get("method") == "Runtime.exceptionThrown":
                self.exceptions.append(message)
            if message.get("id") == identifier:
                if "error" in message:
                    raise RuntimeError(f"CDP {method} failed: {message['error']}")
                return message.get("result", {})

    def evaluate(self, expression):
        result = self.command("Runtime.evaluate", {"expression": expression, "returnByValue": True,
                                                     "awaitPromise": True})
        if "exceptionDetails" in result:
            raise RuntimeError("Browser evaluation failed: " + json.dumps(result["exceptionDetails"]))
        return result["result"].get("value")

    def close(self):
        self.socket.close()


def wait_until(cdp, expression, timeout=10):
    deadline = time.time() + timeout
    while time.time() < deadline:
        value = cdp.evaluate(expression)
        if value:
            return value
        time.sleep(0.05)
    raise TimeoutError("Browser condition did not become true: " + expression)


def main():
    if OUT.exists() or SCREENSHOT.exists():
        raise RuntimeError("Browser interaction evidence already exists")
    started = time.perf_counter()
    version = subprocess.run([
        "powershell.exe", "-NoProfile", "-Command",
        f"(Get-Item -LiteralPath '{EDGE}').VersionInfo.ProductVersion"
    ], capture_output=True, text=True, timeout=30)
    if version.returncode or not version.stdout.strip():
        raise RuntimeError("Cannot read local Edge product version")
    process = None
    cdp = None
    local_temp = Path(os.environ.get("LOCALAPPDATA", tempfile.gettempdir())) / "Temp"
    local_temp.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="b4ml-review-cdp-", dir=local_temp, ignore_cleanup_errors=True
    ) as profile:
        try:
            print(json.dumps({"stage": "launch", "profile": profile}), flush=True)
            process = subprocess.Popen([
                str(EDGE), "--headless=new", "--disable-gpu", "--no-first-run",
                "--disable-background-networking", "--disable-component-update", "--disable-sync",
                "--metrics-recording-only", "--no-default-browser-check", "--disable-features=Translate",
                "--remote-debugging-port=0", "--remote-allow-origins=*", f"--user-data-dir={profile}",
                "--window-size=1440,1000", PAGE.as_uri(),
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            port_file = Path(profile) / "DevToolsActivePort"
            deadline = time.time() + 15
            while not port_file.exists() and time.time() < deadline:
                if process.poll() is not None:
                    raise RuntimeError("Edge exited before opening a DevTools port")
                time.sleep(0.05)
            if not port_file.exists():
                raise TimeoutError("Edge did not open a DevTools port")
            port = int(port_file.read_text().splitlines()[0])
            print(json.dumps({"stage": "port", "port": port}), flush=True)
            tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=5))
            tab = next(row for row in tabs if row.get("type") == "page" and row.get("url") == PAGE.as_uri())
            cdp = CDP(tab["webSocketDebuggerUrl"])
            print(json.dumps({"stage": "connected"}), flush=True)
            cdp.command("Runtime.enable")
            cdp.command("Page.enable")
            cdp.command("Emulation.setDeviceMetricsOverride", {
                "width": 1440, "height": 1000, "deviceScaleFactor": 1, "mobile": False,
            })
            initial = wait_until(cdp, "document.readyState==='complete' && $('progress').textContent==='0 / 32 locked' && $('case').options.length===32")
            print(json.dumps({"stage": "initialized"}), flush=True)
            export_gate = cdp.evaluate("(()=>{$('reviewer').value='browser-smoke';$('experience').value='3-5 years';exportReview();return $('notice').textContent})()")
            if "32 remain" not in export_gate:
                raise ValueError("Incomplete review export was not blocked")
            locked = cdp.evaluate("""(()=>{
                for(const d of dimensions)for(const side of labels)$(d+side).value='4';
                $('acceptableA').value='yes';$('acceptableB').value='yes';
                $('correctionsA').value='1';$('correctionsB').value='2';
                $('interactionsA').value='2';$('interactionsB').value='3';
                $('preference').value='A';$('notes').value='synthetic browser smoke only';
                lockRating();return {progress:$('progress').textContent,locked:$('lock').disabled,
                reveal:$('reveal').style.display,text:$('reveal').textContent,stored:Object.keys(state.reviews).length};
            })()""")
            if locked != {"progress": "1 / 32 locked", "locked": True, "reveal": "block",
                           "text": locked.get("text"), "stored": 1}:
                raise ValueError("Case lock state did not initialize correctly")
            if "A:" not in locked["text"] or "Automated v13 case measurements" not in locked["text"]:
                raise ValueError("Locked case did not reveal method identity and measurements")
            next_case = cdp.evaluate("(()=>{move(1);return {hidden:$('reveal').style.display,progress:$('progress').textContent,locked:$('lock').disabled}})()")
            if next_case != {"hidden": "none", "progress": "1 / 32 locked", "locked": False}:
                raise ValueError("Navigation leaked the previous case reveal or lock")
            filtered = cdp.evaluate("(()=>{$('profile').value='boneforge';rebuildFilter();return $('case').options.length})()")
            if filtered != 8:
                raise ValueError("Rig filter did not expose eight task cases")
            cdp.evaluate("togglePlay()")
            time.sleep(0.25)
            playback_frame = cdp.evaluate("(()=>{if(playing)togglePlay();return frame})()")
            if not isinstance(playback_frame, int) or playback_frame <= 0:
                raise ValueError("Playback did not advance")
            cdp.command("Page.reload", {"ignoreCache": True})
            persisted = wait_until(cdp, "document.readyState==='complete' && $('progress').textContent==='1 / 32 locked'")
            state_after_reload = cdp.evaluate("({progress:$('progress').textContent,locked:$('lock').disabled,reveal:$('reveal').style.display,reviews:Object.keys(state.reviews).length})")
            if state_after_reload != {"progress": "1 / 32 locked", "locked": True, "reveal": "block", "reviews": 1}:
                raise ValueError("Locked review did not persist across reload")
            cdp.evaluate("$('reveal').scrollIntoView({block:'center'})")
            image = cdp.command("Page.captureScreenshot", {"format": "png", "fromSurface": True})
            SCREENSHOT.write_bytes(base64.b64decode(image["data"]))
            if SCREENSHOT.stat().st_size < 10000:
                raise ValueError("Interaction screenshot is unexpectedly small")
            if cdp.exceptions:
                raise RuntimeError(f"Browser reported {len(cdp.exceptions)} uncaught exceptions")
            print(json.dumps({"stage": "validated"}), flush=True)
        finally:
            if cdp is not None:
                cdp.close()
            if process is not None and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)
    report = dict(
        schema="b4ml-procedural-vertical-slice-reviewer-browser-interaction-v4",
        complete=True,
        browser_executable=str(EDGE),
        browser_product_version=version.stdout.strip(),
        local_file_loaded=bool(initial),
        javascript_initialized=True,
        synthetic_review_isolated=True,
        incomplete_export_blocked=True,
        lock_before_reveal=True,
        navigation_hides_unrated_identity=True,
        rig_filter_cases=filtered,
        playback_advanced_to_sample=playback_frame,
        local_storage_reload_persisted=bool(persisted),
        uncaught_browser_exceptions=0,
        screenshot_sha256=sha(SCREENSHOT),
        screenshot_bytes=SCREENSHOT.stat().st_size,
        reviewer_html_sha256=sha(PAGE),
        reviewed_cases=0,
        human_assessment="unverified; synthetic interaction is not a rating",
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
