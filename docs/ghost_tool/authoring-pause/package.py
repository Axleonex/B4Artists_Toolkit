"""Build a new candidate and check the exact extracted install in a Blender stand-in."""
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
OUTPUT = ROOT / 'releases/b4_ghost_tool_v4.2.2.zip'
HOST = Path(r'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe')
TESTS = ('test_ghost_authoring.py', 'test_ghost_regressions.py',
         'test_ghost_correctness.py', 'test_ghost_header_ui.py',
         'test_ghost_paths.py', 'test_ghost_paths_fast.py',
         'test_ghost_paths_handles.py', 'test_ghost_paths_vertex.py',
         'test_ghost_snapshot_targets.py')


def main():
    files = sorted((ROOT / 'ghost_tool').glob('*.py'))
    for path in files:
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    if not OUTPUT.exists():
        with zipfile.ZipFile(OUTPUT, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
            for path in files:
                archive.write(path, 'ghost_tool/' + path.name)
    results = []
    with zipfile.ZipFile(OUTPUT) as archive, tempfile.TemporaryDirectory(prefix='ghost-pause-') as folder:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(files)
        assert all(archive.read('ghost_tool/' + path.name) == path.read_bytes() for path in files)
        base = Path(folder)
        archive.extractall(base)
        shutil.copytree(ROOT / 'tests', base / 'tests',
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        environment = dict(os.environ, BLENDER_USER_CONFIG=str(base / 'config'),
                           BLENDER_USER_SCRIPTS=str(base / 'scripts'),
                           GHOST_TEST_ADDON_ROOT=str(base / 'ghost_tool'),
                           PYTHONDONTWRITEBYTECODE='1')
        for name in TESTS:
            code = ('import sys,runpy;sys.dont_write_bytecode=True;'
                    f'sys.path.insert(0,{str(base)!r});'
                    f'sys.path.insert(1,{str(base / "tests")!r});'
                    'import ghost_tool;ghost_tool._is_bforartists=lambda:True;'
                    f'runpy.run_path({str(base / "tests" / name)!r},run_name="__main__")')
            process = subprocess.run([str(HOST), '--background', '--factory-startup',
                                      '--python-exit-code', '1', '--python-expr', code],
                                     cwd=base, env=environment, capture_output=True,
                                     text=True, errors='replace', timeout=90)
            output = process.stdout + '\n' + process.stderr
            (Path(__file__).parent / (name + '.log')).write_text(output, encoding='utf-8')
            counts = re.findall(r'Ran (\d+) tests?', output)
            result = dict(test=name, tests=sum(map(int, counts)), exit_code=process.returncode,
                          status='PASS' if process.returncode == 0 and counts else 'FAIL')
            results.append(result)
            print(json.dumps(result), flush=True)
        native_output = base / 'native-results.json'
        # Windows subprocess startupinfo keeps the disposable GUI engine hidden.
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 0
        native = subprocess.run([str(HOST), '--factory-startup', '--enable-event-simulate',
                                 '--python', str(base / 'tests/test_ghost_native_authoring.py')],
                                cwd=base, env=dict(environment,
                                GHOST_NATIVE_TEST_OUTPUT=str(native_output)), startupinfo=startup,
                                capture_output=True, text=True, errors='replace', timeout=90)
        (Path(__file__).parent / 'native.log').write_text(native.stdout + '\n' + native.stderr,
                                                       encoding='utf-8')
        native_results = json.loads(native_output.read_text(encoding='utf-8'))
        Path(__file__).with_name('native-results.json').write_text(
            json.dumps(native_results, indent=2) + '\n', encoding='utf-8')
    receipt = dict(version='4.2.2', artifact=OUTPUT.relative_to(ROOT).as_posix(),
                   bytes=OUTPUT.stat().st_size,
                   sha256=hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
                   source_modules=len(files), source_bytes_match=True,
                   background_tests=results, native_tests=native_results,
                   status='PASS' if all(r['status'] == 'PASS' for r in results)
                   and native.returncode == 0 and native_results['status'] == 'PASS' else 'FAIL',
                   host=str(HOST), host_role='Blender 5.1.2 stand-in; registration gate patched only',
                   bforartists_production_rig_validation='PENDING', published=False)
    Path(__file__).with_name('package-receipt.json').write_text(
        json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2), flush=True)
    return 0 if receipt['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
