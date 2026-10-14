"""Finite stock-host toolbar verification in a task-owned profile."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import uuid
import zipfile


def owned_profile(path):
    path = Path(path).resolve()
    approved = Path('G:/LapArt/.cache/anim-assist-tests').resolve()
    if not path.is_relative_to(approved) or path == approved:
        raise ValueError('Profile must be a child of the task test-profile root')
    marker = path / 'toolbar-test-owner.json'
    if path.exists() and not marker.is_file():
        raise ValueError('Existing profile is not owned by the toolbar test')
    if marker.exists() and json.loads(marker.read_text()).get('purpose') != 'anim-assist-toolbar-verification':
        raise ValueError('Test profile owner marker does not match')
    path.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps({'purpose': 'anim-assist-toolbar-verification'}))
    for name in ('config', 'scripts/addons', 'datafiles'):
        (path / name).mkdir(parents=True, exist_ok=True)
    return path


def install(package, profile):
    target = profile / 'scripts/addons'
    with zipfile.ZipFile(package) as archive:
        members = archive.infolist()
        for member in members:
            dest = (target / member.filename).resolve()
            if not dest.is_relative_to(target.resolve()):
                raise ValueError('Archive path escapes isolated scripts')
            if member.filename.lower().endswith(('.exe', '.dll')):
                raise ValueError('Application binaries are forbidden')
        archive.extractall(target)
        for member in members:
            if not member.is_dir():
                assert (target/member.filename).read_bytes() == archive.read(member)
    return len([m for m in members if not m.is_dir()])


class Host:
    def __init__(self, args, profile):
        self.root = Path(args.evidence).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.timeout = args.timeout
        self.log = (self.root/'host.log').open('w', encoding='utf-8')
        env = os.environ.copy()
        env.update(BLENDER_USER_CONFIG=str(profile/'config'),
                   BLENDER_USER_SCRIPTS=str(profile/'scripts'),
                   BLENDER_USER_DATAFILES=str(profile/'datafiles'),
                   AA_OVERLAY_EVIDENCE=str(self.root))
        if args.attach:
            self.proc = subprocess.Popen(['powershell.exe','-NoProfile','-Command',
                f'Wait-Process -Id {int(args.attach)}'], stdout=self.log, stderr=subprocess.STDOUT)
        else:
            for name in ('state.json', 'request.json', 'response.json'):
                (self.root/name).unlink(missing_ok=True)
            quote = lambda value: "'"+str(value).replace("'", "''")+"'"
            command = '& '+quote(Path(args.host).resolve())+' --enable-event-simulate --python '+quote(
                Path(__file__).with_name('observe_timeline_overlay.py').resolve())
            self.proc = subprocess.Popen(['powershell.exe','-NoProfile','-Command',command],
                env=env, stdout=self.log, stderr=subprocess.STDOUT)
        try:
            self.await_file('state.json', min(args.timeout, 90))
        except Exception:
            self.proc.terminate()
            self.log.close()
            raise

    def await_file(self, name, seconds):
        end = time.monotonic()+seconds
        while time.monotonic() < end:
            if self.proc.poll() is not None:
                raise RuntimeError('Test host exited; inspect host.log')
            try:
                return json.loads((self.root/name).read_text())
            except (FileNotFoundError, json.JSONDecodeError, PermissionError):
                time.sleep(.1)
        raise TimeoutError(name)

    def request(self, code, delay=.15):
        ident = uuid.uuid4().hex
        pending = self.root/'request.pending'
        pending.write_text(json.dumps({'id': ident, 'code': code}), encoding='utf-8')
        pending.replace(self.root/'request.json')
        end = time.monotonic()+self.timeout
        while time.monotonic() < end:
            result = self.await_file('response.json', self.timeout)
            if result['id'] == ident:
                if not result['ok']:
                    raise AssertionError(result['error'])
                time.sleep(delay)
                return result
            time.sleep(.1)
        raise TimeoutError('Request '+ident)

    def close(self):
        try:
            if self.proc.poll() is None:
                self.request('bpy.ops.wm.quit_blender()', 0)
        except (RuntimeError, AssertionError, TimeoutError):
            pass
        try:
            self.proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            self.proc.terminate()
            self.proc.wait(timeout=10)
        self.log.close()


def run(args):
    profile = owned_profile(args.profile)
    package = Path(args.package).resolve()
    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    files = install(package, profile)
    host = Host(args, profile)
    try:
        source = Path(__file__).with_name('check_timeline_toolbar_tools.py').resolve()
        host.request(f"exec(compile(open({str(source)!r}, encoding='utf-8').read(), {str(source)!r}, 'exec'), globals())")
        host.request("event('ESC')")  # Dismiss the first-start welcome popup before pointer tests.
        host.request('prepare_geometry()')
        host.request('expand_geometry()')
        if not args.only_action:
            host.request('run_immediate_checks()')
        actions=(args.only_action,) if args.only_action else ('B25','B50','B75','NUDGE_LEFT','NUDGE_RIGHT','RIPPLE','RANGE','ENDS','MIRROR_SELECTED','BAKE_STEP','TRAIL_SHOW')
        for action in actions:
            host.request(f'prepare_button({action!r})')
            host.request(f'click_action({action!r})')
            host.request('assert_button()')
            if args.diagnostic_push:
                host.request("bpy.ops.ed.undo_push(message='Diagnostic commit checkpoint')")
            if action=='B50':
                host.request("recover('undo')")
                host.request("assert_recovery('undo')")
                host.request("recover('redo')")
                host.request("assert_recovery('redo')")
        for action in (() if args.only_action else ('DRAG','NEIGHBORS','FRAME','EASE','AMPLIFY','SMOOTH','SCALE_DRAG','OFFSET_DRAG','OFFSET')):
            for ending in ('cancel','commit'):
                host.request(f"begin_modal({action!r},{ending!r})")
                host.request('assert_started()')
                host.request('move_modal()', .35)
                host.request('assert_live()')
                host.request('end_modal()')
                host.request('assert_ending()')
                if ending=='commit':
                    host.request("recover('undo')")
                    host.request("assert_recovery('undo')")
                    host.request("recover('redo')")
                    host.request("assert_recovery('redo')")
        if not args.only_action:
            host.request('write_coverage()')
        (host.root/'package-identity.json').write_text(json.dumps(dict(
            sha256=digest, files=files, package=str(package), profile=str(profile),
            git_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
            stage=args.stage), indent=2))
        print((host.root/('bar-actions.json' if args.only_action else 'coverage.json')).read_text())
    finally:
        host.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=('baseline','final'), required=True)
    for name in ('package','host','evidence','profile'):
        parser.add_argument('--'+name, required=True)
    parser.add_argument('--timeout', type=float, default=300)
    parser.add_argument('--attach', type=int, help='Attach to an already launched owned native test process')
    parser.add_argument('--only-action', help='Diagnostic single button run; not a full verification gate')
    parser.add_argument('--diagnostic-push', action='store_true', help='Diagnose missing native undo checkpoint; never use for qualification')
    run(parser.parse_args())
