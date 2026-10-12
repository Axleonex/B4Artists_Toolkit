"""Real Ghost Tool checks in disposable isolated Bforartists processes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NEW_MODULES = {
    'layout': ['test_ghost_afterimage_ui.py'],
    'targets': ['test_ghost_snapshot_targets.py'],
    'variants': ['test_ghost_snapshot_variants.py'],
    'persistence': ['test_ghost_snapshot_persistence.py'],
    'lifecycle': ['test_ghost_afterimage_lifecycle.py'],
}
INTERACTIVE = {'test_ghost_council_workflow.py', 'test_ghost_afterimage_lifecycle.py', 'test_ghost_snapshot_variants.py'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def select_tests(suite):
    old = sorted(p.name for p in (ROOT / 'tests').glob('test_ghost_*.py')
                 if not p.name.startswith(('test_ghost_afterimage_', 'test_ghost_snapshot_')))
    if suite == 'baseline':
        return old
    if suite == 'release':
        return old + [name for names in NEW_MODULES.values() for name in names]
    if suite == 'layout':
        return NEW_MODULES[suite] + ['test_ghost_council_ui.py', 'test_ghost_header_ui.py',
                                     'test_ghost_council_workflow.py']
    return NEW_MODULES[suite]


def bootstrap(script):
    return f'''import sys,json,runpy,unittest,os
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path({str(script.parents[1])!r})
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))
ADDON_PARENT = ROOT / 'user-scripts' / 'addons' if (ROOT / 'user-scripts' / 'addons').is_dir() else ROOT
sys.path.insert(0, str(ADDON_PARENT))
import bpy
results = []
original_run = unittest.TextTestRunner.run
def observed_run(self, suite):
    result = original_run(self, suite)
    results.append(result)
    return result
unittest.TextTestRunner.run = observed_run
runpy.run_path({str(script)!r}, run_name='__main__')
import ghost_tool
if not os.path.samefile(Path(ghost_tool.__file__).parent, ADDON_PARENT / 'ghost_tool'):
    raise RuntimeError('Addon import escaped isolated installation')
if {script.name!r} != 'test_ghost_council_workflow.py':
    count = sum(r.testsRun for r in results)
    if {script.name!r} == 'test_ghost_release_compat.py':
        count = 1
    if count == 0 or any(not r.wasSuccessful() for r in results):
        raise RuntimeError('Empty or unsuccessful behavioral suite')
    import ghost_tool
    if not os.path.samefile(Path(ghost_tool.__file__).parent, ADDON_PARENT / 'ghost_tool'):
        raise RuntimeError('Addon import escaped isolated installation')
    print('AFTERIMAGE_TEST_RESULT '+json.dumps(dict(status='PASS',tests=count,
        host=bpy.app.version_string,addon_file=ghost_tool.__file__,
        installed_hashes={{p.name:__import__('hashlib').sha256(p.read_bytes()).hexdigest() for p in Path(ghost_tool.__file__).parent.glob('*.py')}})), flush=True)
'''


def run_one(host, base, name, timeout, logs):
    script = base / 'tests' / name
    wrapper = base / ('run_' + name)
    code = bootstrap(script)
    if name in {'test_ghost_snapshot_variants.py', 'test_ghost_afterimage_lifecycle.py'}:
        code = ('import bpy,traceback\n'
                'bpy.context.preferences.view.show_splash=False\n'
                'def run_interactive():\n'
                '    try:\n' + ''.join('        '+line+'\n' for line in code.splitlines()) +
                '    except Exception:\n        traceback.print_exc()\n'
                '    bpy.ops.wm.quit_blender()\n    return None\n'
                'bpy.app.timers.register(run_interactive,first_interval=1)\n')
    wrapper.write_text(code, encoding='utf-8')
    command = [str(host), '--factory-startup', '--python-exit-code', '1',
               '--python', str(wrapper)]
    if name not in INTERACTIVE:
        command.insert(1, '--background')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    installation = base / 'user-scripts' / 'addons' / 'ghost_tool'
    env['GHOST_TEST_ADDON_ROOT'] = str(installation if installation.is_dir() else base / 'ghost_tool')
    env['BLENDER_USER_CONFIG'] = str(base / 'user-config')
    env['BLENDER_USER_SCRIPTS'] = str(base / 'user-scripts')
    started = time.monotonic()
    try:
        process = subprocess.run(command, cwd=base, env=env, capture_output=True,
                                 text=True, errors='replace', timeout=timeout)
        text = process.stdout + '\n' + process.stderr
        log = logs / (name + '.log')
        log.write_text(text, encoding='utf-8')
        if name == 'test_ghost_council_workflow.py':
            path = base / 'docs/ghost_tool/council-workflow-result.json'
            evidence = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
            count = len(evidence.get('checks', []))
        else:
            lines = [line.removeprefix('AFTERIMAGE_TEST_RESULT ') for line in text.splitlines()
                     if line.startswith('AFTERIMAGE_TEST_RESULT ')]
            evidence = json.loads(lines[-1]) if lines else {}
            count = evidence.get('tests', 0)
        passed = process.returncode == 0 and evidence.get('status') == 'PASS' and count > 0
        return dict(test=name,status='PASS' if passed else 'FAIL',tests=count,
                    exit_code=process.returncode,command=command,
                    duration_seconds=round(time.monotonic()-started,2),
                    evidence=evidence,log=str(log))
    except subprocess.TimeoutExpired as exc:
        partial = '\n'.join(v.decode('utf-8', errors='replace') if isinstance(v, bytes) else (v or '') for v in (exc.stdout, exc.stderr))
        (logs / (name + '.log')).write_text(str(exc) + '\n' + partial, encoding='utf-8')
        return dict(test=name,status='BLOCKED',reason='host process timed out',tests=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', required=True, type=Path)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--source-root', type=Path)
    source.add_argument('--zip', type=Path)
    parser.add_argument('--suite', required=True, choices=['baseline',*NEW_MODULES,'release'])
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--timeout', type=int, default=120)
    args = parser.parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    report = dict(suite=args.suite,status='BLOCKED',tests=[])
    def finish(code):
        output.write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps({'status':report['status'],'suite':args.suite,
                          'test_scripts':len(report['tests']),
                          'assertion_cases':sum(t.get('tests',0) for t in report['tests']),
                          'output':str(output)}),flush=True)
        return code
    names = select_tests(args.suite)
    if not args.host.is_file() or not names:
        report['reason'] = 'Missing host executable or empty suite'
        return finish(2)
    missing = [name for name in names if not (ROOT / 'tests' / name).is_file()]
    if missing:
        report['reason'] = 'Missing required test modules: '+', '.join(missing)
        return finish(2)
    if args.source_root and not (args.source_root / '__init__.py').is_file():
        report['reason'] = 'Missing addon source'
        return finish(2)
    if args.zip and not args.zip.is_file():
        report['reason'] = 'Missing candidate archive'
        return finish(2)
    logs = output.parent / (output.stem + '-logs')
    logs.mkdir(exist_ok=True)
    report['host'] = str(args.host.resolve())
    report['input'] = str((args.source_root or args.zip).resolve())
    if args.zip:
        report['zip_sha256'] = sha(args.zip)
    else:
        report['source_hashes'] = {p.name:sha(p) for p in args.source_root.glob('*.py')}
    with tempfile.TemporaryDirectory(prefix='ghost-afterimage-') as temporary:
        # Windows temp roots may use an 8.3 alias. Normalize both sides of
        # archive containment checks before comparing their path components.
        base = Path(temporary).resolve()
        if args.zip:
            installation = base / 'user-scripts' / 'addons'
            installation.mkdir(parents=True)
            with zipfile.ZipFile(args.zip) as archive:
                if any(not (installation / name).resolve().is_relative_to(installation) for name in archive.namelist()):
                    report['reason'] = 'Unsafe archive entry'
                    return finish(2)
                archive.extractall(installation)
                report['archive_hashes'] = {name:hashlib.sha256(archive.read(name)).hexdigest() for name in archive.namelist()}
            report['installation_root'] = str(installation)
            report['installation_hashes'] = {str(p.relative_to(installation)).replace('\\','/'):sha(p)
                                              for p in (installation / 'ghost_tool').glob('*.py')}
            if report['archive_hashes'] != report['installation_hashes']:
                report['reason'] = 'Installed bytes do not match exact archive'
                return finish(2)
        else:
            shutil.copytree(args.source_root,base / 'ghost_tool',
                            ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        shutil.copytree(ROOT / 'tests',base / 'tests',
                        ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        shutil.copytree(ROOT / 'releases',base / 'releases')
        (base / 'docs/ghost_tool').mkdir(parents=True)
        for name in names:
            result = run_one(args.host.resolve(),base,name,args.timeout,logs)
            report['tests'].append(result)
            print(name+': '+result['status']+' ('+str(result.get('tests',0))+')',flush=True)
    report['status'] = 'PASS' if report['tests'] and all(t['status']=='PASS' for t in report['tests']) else 'FAIL'
    report['human_usability'] = 'PENDING'
    return finish(0 if report['status']=='PASS' else 1)


if __name__ == '__main__':
    raise SystemExit(main())
