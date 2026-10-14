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
    for name in ('config', 'scripts/addons', 'datafiles', 'tmp'):
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
                   TMP=str(profile/'tmp'), TEMP=str(profile/'tmp'),
                   AA_OVERLAY_EVIDENCE=str(self.root))
        if getattr(args,'resume',False): env['AA_TOOLBAR_RESUME']='1'
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
            subprocess.run(['taskkill','/PID',str(self.proc.pid),'/T','/F'],capture_output=True)
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
            subprocess.run(['taskkill','/PID',str(self.proc.pid),'/T','/F'],capture_output=True)
            self.proc.wait(timeout=10)
        self.log.close()


def run(args):
    profile = owned_profile(args.profile)
    package = Path(args.package).resolve()
    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    files = install(package, profile)
    host = Host(args, profile)
    try:
        (host.root/'package-identity.json').write_text(json.dumps(dict(
            sha256=digest, files=files, package=str(package), profile=str(profile),
            git_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
            stage=args.stage), indent=2))
        source = Path(__file__).with_name('check_timeline_toolbar_tools.py').resolve()
        host.request(f"exec(compile(open({str(source)!r}, encoding='utf-8').read(), {str(source)!r}, 'exec'), globals())")
        host.request("event('ESC')")  # Dismiss the first-start welcome popup before pointer tests.
        host.request('prepare_geometry()')
        host.request('expand_geometry()')
        if args.full:
            host.request('full_legacy_layout()')
        if args.layouts:
            host.request('ui_defaults()')
            host.request('layouts_prepare()')
            for name in ('Blocking','Polish'):
                host.request(f'layout_save_open({name!r})')
                host.request("ui_screenshot('layout-save')")
                host.request("event('RET')")
                host.request(f'layout_saved({name!r})')
            host.request('layout_manage()')
            host.request('layout_transfer_and_save()')
            host.request('ui_settings_open()')
            host.request("ui_screenshot('named-layout-settings')")
            host.request("event('ESC')")
            host.close()
            args.resume=True
            host=Host(args,profile)
            host.request(f"exec(compile(open({str(source)!r}, encoding='utf-8').read(), {str(source)!r}, 'exec'), globals())")
            host.request('layout_restart_check()')
            print((host.root/'layout-coverage.json').read_text())
            return
        if args.ui:
            host.request('ui_defaults()')
            for action,mode in (('DRAG','INLINE'),('SMOOTH','INLINE'),('SCALE_DRAG','POPOUT')):
                for ending in ('cancel','commit'):
                    host.request(f'prepare_slider({action!r},{mode!r},{ending!r})')
                    host.request('begin_slider_ui()')
                    host.request('move_slider()')
                    host.request('check_slider_live()')
                    host.request("ui_screenshot('drag-'+slider_case['action'])")
                    host.request('end_slider()')
                    host.request('check_slider_end()')
                    if ending=='commit':
                        host.request("recover('undo')")
                        host.request("assert_recovery('undo')")
                        host.request("recover('redo')")
                        host.request("assert_recovery('redo')")
            host.request('ui_settings_open()')
            host.request('ui_settings_check()')
            host.request("event('ESC')")
            host.request('ui_settings_cancelled()')
            host.request('ui_tool_open()')
            host.request("ui_screenshot('tool-settings')")
            host.request("event('ESC')")
            host.request('ui_tool_cancelled()')
            host.request('ui_finish()')
            print((host.root/'ui-coverage.json').read_text())
            return
        if args.adapters:
            for action in ('DRAG','SMOOTH','NEIGHBORS','FRAME','EASE','AMPLIFY','SCALE_DRAG','OFFSET_DRAG'):
                for mode in ('INLINE','POPOUT'):
                    for ending in ('cancel','commit'):
                        host.request(f'prepare_slider({action!r},{mode!r},{ending!r})')
                        host.request('begin_slider()')
                        host.request('move_slider()')
                        host.request('check_slider_live()')
                        host.request('end_slider()')
                        host.request('check_slider_end()')
                        if ending=='commit':
                            host.request("recover('undo')")
                            host.request("assert_recovery('undo')")
                            host.request("recover('redo')")
                            host.request("assert_recovery('redo')")
            host.request('write_slider_coverage()')
            print((host.root/'slider-coverage.json').read_text())
            return
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
        if args.full:
            host.request('ui_defaults()')
            for action in ('B25','B50','B75','NUDGE_LEFT','NUDGE_RIGHT','COPY_KEYS','PASTE_KEYS','MIRROR_SELECTED','BAKE_STEP','TRAIL_SHOW'):
                host.request(f'prepare_button({action!r})')
                host.request(f'click_action({action!r})')
                host.request('assert_button()')
            for action in ('DRAG','SMOOTH','NEIGHBORS','FRAME','EASE','AMPLIFY','SCALE_DRAG','OFFSET_DRAG'):
                for mode in ('INLINE','POPOUT'):
                    for ending in ('cancel','commit'):
                        host.request(f'prepare_slider({action!r},{mode!r},{ending!r})')
                        host.request('select_slider_mode()')
                        host.request('begin_slider_ui()')
                        host.request('move_slider()')
                        host.request('check_slider_live()')
                        host.request('end_slider()')
                        host.request('check_slider_end()')
                        if ending=='commit':
                            host.request("recover('undo')")
                            host.request("assert_recovery('undo')")
                            host.request("recover('redo')")
                            host.request("assert_recovery('redo')")
            host.request('ui_defaults()')
            host.request('ui_settings_open()')
            host.request('settings_change()')
            host.request("event('RET')")
            host.request('settings_accepted()')
            host.request('ui_tool_open()')
            host.request('tool_change()')
            host.request("ui_screenshot('tool-settings-final')")
            host.request("event('RET')")
            host.request('tool_accepted()')
            for value in (-100,200):
                host.request(f'numeric_prepare({value})')
                host.request("event('RET')")
                host.request('numeric_check()')
                host.request("recover('undo')")
                host.request("assert_recovery('undo')")
                host.request("recover('redo')")
                host.request("assert_recovery('redo')")
            host.request('misuse_checks()')
            host.request('ui_defaults()')
            for kind,key in (('MENU','tween'),('MORE',''),('SEARCH','')):
                host.request(f'ui_click({kind!r},{key!r})')
                host.request(f"ui_screenshot('menu-{kind.lower()}')")
                host.request("event('ESC')")
            host.request('scrub_prepare()')
            host.request('scrub_check()')
            host.request('hide_check()')
            host.request('lifecycle_disable()')
            host.request('lifecycle_enable()')
            host.request('migration_checks()')
            host.request('write_full_coverage()')
            print((host.root/'full-coverage.json').read_text())
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
    parser.add_argument('--adapters', action='store_true', help='Exercise new scalar adapters before row integration')
    parser.add_argument('--ui', action='store_true', help='Exercise actual row controls and native settings windows')
    parser.add_argument('--layouts', action='store_true', help='Verify named layouts, transfer and normal restart')
    parser.add_argument('--full', action='store_true', help='Final legacy/default/actual-row and recovery regression')
    run(parser.parse_args())
