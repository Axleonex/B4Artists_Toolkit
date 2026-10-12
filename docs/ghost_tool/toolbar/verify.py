"""Isolated toolbar verification; [PowerShell] python docs/ghost_tool/toolbar/verify.py.

Builds an unpublished candidate under ignored build/. It never replaces a
released archive or changes the user's installed add-on/preferences.
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / 'build/ghost-toolbar'
HOST = Path(r'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe')
SUITES = (
    'test_ghost_display_location.py', 'test_ghost_toolbar_ui.py',
    'test_ghost_cached_display.py', 'test_ghost_marker_targets_ui.py',
    'test_ghost_compare_targets_ui.py', 'test_ghost_afterimage_ui.py',
    'test_ghost_header_ui.py', 'test_ghost_council_ui.py',
    'test_ghost_authoring.py', 'test_ghost_snapshot_targets.py',
)


def invoke(base, code, name, *, gui=False, width=1800, height=1000):
    wrapper = base / (name + '.py')
    wrapper.write_text(code, encoding='utf-8')
    command = [str(HOST), '--factory-startup', '--python-exit-code', '1',
               '--python', str(wrapper)]
    if gui:
        command[1:1] = ['--enable-event-simulate', '--window-geometry',
                        '0', '0', str(width), str(height)]
    else:
        command.insert(1, '--background')
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    env = dict(os.environ, BLENDER_USER_CONFIG=str(base / 'config'),
               BLENDER_USER_SCRIPTS=str(base / 'scripts'),
               GHOST_TEST_ADDON_ROOT=str(base / 'ghost_tool'),
               PYTHONDONTWRITEBYTECODE='1')
    process = subprocess.run(command, cwd=base, env=env, startupinfo=startup,
                             capture_output=True, text=True, errors='replace', timeout=120)
    output = process.stdout + '\n' + process.stderr
    (OUTPUT / (name + '.log')).write_text(output, encoding='utf-8')
    counts = re.findall(r'Ran (\d+) tests?', output)
    return dict(suite=name, tests=sum(map(int, counts)), exit_code=process.returncode,
                status='PASS' if process.returncode == 0 and counts else 'FAIL')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-only', action='store_true', help='Recheck changed GUI evidence only')
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    sources = sorted((ROOT / 'ghost_tool').glob('*.py'))
    for source in sources:
        ast.parse(source.read_text(encoding='utf-8'))
    module = ast.parse((ROOT / 'ghost_tool/__init__.py').read_text(encoding='utf-8'))
    info = next(ast.literal_eval(node.value) for node in module.body
                if isinstance(node, ast.Assign) and any(
                    isinstance(target, ast.Name) and target.id == 'bl_info'
                    for target in node.targets))
    version = '.'.join(map(str, info['version']))
    candidate = OUTPUT / f'b4_ghost_tool_v{version}-toolbar-candidate.zip'
    with zipfile.ZipFile(candidate, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for source in sources:
            archive.write(source, 'ghost_tool/' + source.name)
    results = []
    with tempfile.TemporaryDirectory(prefix='ghost-toolbar-') as folder:
        base = Path(folder).resolve()
        with zipfile.ZipFile(candidate) as archive:
            assert archive.testzip() is None
            assert all(archive.read('ghost_tool/' + p.name) == p.read_bytes() for p in sources)
            archive.extractall(base)
        shutil.copytree(ROOT / 'tests', base / 'tests',
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        preamble = ('import sys,runpy;sys.dont_write_bytecode=True;'
                    f'sys.path.insert(0,{str(base)!r});'
                    f'sys.path.insert(0,{str(base / "tests")!r});'
                    'import ghost_tool;ghost_tool._is_bforartists=lambda:True;')
        for name in (() if args.native_only else SUITES):
            result = invoke(base, preamble +
                            f'runpy.run_path({str(base / "tests" / name)!r},run_name="__main__")',
                            name.removesuffix('.py'))
            results.append(result)
            print(json.dumps(result), flush=True)
        for width, scale, maximize, tier in ((1920, 1.0, True, 'FULL'),
                (1700, 1.0, False, 'COMPACT'), (1100, 1.0, False, 'MINIMAL'),
                (1920, 1.5, True, 'COMPACT')):
            name = f'native-{width}-scale-{scale}'
            evidence_file = OUTPUT / (name + '.json')
            evidence_file.unlink(missing_ok=True)
            code = preamble + (
                'import os;'
                f'os.environ["GHOST_TOOLBAR_TEST_OUTPUT"]={str(OUTPUT / (name + ".json"))!r};'
                f'os.environ["GHOST_TOOLBAR_TEST_SCALE"]={str(scale)!r};'
                f'os.environ["GHOST_TOOLBAR_TEST_MAXIMIZE"]={str(int(maximize))!r};'
                f'os.environ["GHOST_TOOLBAR_TEST_TIER"]={tier!r};'
                f'os.environ["GHOST_TOOLBAR_SCREEN_PREFIX"]={str(OUTPUT / name)!r};'
                f'runpy.run_path({str(base / "tests/test_ghost_toolbar_native.py")!r},run_name="__main__")')
            result = invoke(base, code, name, gui=True, width=width)
            evidence = json.loads(evidence_file.read_text()) if evidence_file.exists() else {}
            result.update(tests=len(evidence.get('checks', [])), evidence=evidence,
                          status='PASS' if result['exit_code'] == 0 and evidence.get('status') == 'PASS' else 'FAIL')
            results.append(result)
            print(json.dumps({k:v for k,v in result.items() if k != 'evidence'}), flush=True)
        native_output = OUTPUT / 'native-authoring.json'
        native_output.unlink(missing_ok=True)
        code = preamble + ('import os,bpy;'
            f'os.environ["GHOST_NATIVE_TEST_OUTPUT"]={str(native_output)!r};'
            'ghost_tool.register();'
            'bpy.context.preferences.addons.new().module="ghost_tool";'
            'p=bpy.context.preferences.addons["ghost_tool"].preferences;p.display_location="TOOLBAR";'
            'ghost_tool.unregister();'
            f'runpy.run_path({str(base / "tests/test_ghost_native_authoring.py")!r},run_name="__main__")')
        result = invoke(base, code, 'native-authoring', gui=True)
        evidence = json.loads(native_output.read_text()) if native_output.exists() else {}
        result.update(tests=len(evidence.get('cases', [])), evidence=evidence,
                      status='PASS' if result['exit_code'] == 0 and evidence.get('status') == 'PASS' else 'FAIL')
        results.append(result)
        print(json.dumps({k:v for k,v in result.items() if k != 'evidence'}), flush=True)
    receipt = dict(status='PASS' if all(r['status'] == 'PASS' for r in results) else 'FAIL',
        candidate=candidate.name, sha256=hashlib.sha256(candidate.read_bytes()).hexdigest(),
        source_modules=len(sources), extracted_bytes_match=True, results=results,
        source_version=version,
        host='Blender 5.1.2 stand-in; registration gate patched only',
        bforartists_validation='NOT VERIFIED', published=False)
    receipt_name = 'native-receipt.json' if args.native_only else 'receipt.json'
    (OUTPUT / receipt_name).write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(status=receipt['status'], tests=sum(r['tests'] for r in results))), flush=True)
    return 0 if receipt['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
