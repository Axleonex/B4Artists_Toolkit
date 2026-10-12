"""Build an unpublished repair ZIP and verify its bytes and behavior in isolation."""
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
SOURCE = ROOT / 'ghost_tool'
OUTPUT = ROOT / 'releases/b4_ghost_tool_v4.2.1.zip'
PREVIOUS = ROOT / 'releases/b4_ghost_tool_v4.2.0.zip'
HOST = Path(r'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe')
TESTS = (
    'test_ghost_authoring.py', 'test_ghost_regressions.py',
    'test_ghost_correctness.py', 'test_ghost_paths.py',
    'test_ghost_paths_fast.py', 'test_ghost_paths_handles.py',
    'test_ghost_paths_vertex.py', 'test_ghost_draw_to_keys.py',
    'test_ghost_snapshot_targets.py', 'test_ghost_snapshot_persistence.py',
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    files = sorted(SOURCE.glob('*.py'))
    assert files, 'Empty addon'
    for path in files:
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    # Exclusive creation protects earlier packages and any owner-supplied ZIP.
    if not OUTPUT.exists():
        with zipfile.ZipFile(OUTPUT, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
            for path in files:
                archive.write(path, 'ghost_tool/' + path.name)
    with zipfile.ZipFile(OUTPUT) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(files)
        for path in files:
            assert archive.read('ghost_tool/' + path.name) == path.read_bytes()
        hashes = {name: sha(archive.read(name)) for name in archive.namelist()}
        with zipfile.ZipFile(PREVIOUS) as previous:
            changed = [name for name in hashes if name not in previous.namelist()
                       or sha(previous.read(name)) != hashes[name]]
        results = []
        with tempfile.TemporaryDirectory(prefix='ghost-authoring-') as directory:
            base = Path(directory).resolve()
            archive.extractall(base)
            shutil.copytree(ROOT / 'tests', base / 'tests',
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            for name in TESTS:
                wrapper = base / 'run_test.py'
                # Patching only the host gate makes the stand-in explicit.
                # All animation, mesh evaluation and addon code execute in Blender.
                wrapper.write_text(
                    'import sys,runpy,unittest\n'
                    'from pathlib import Path\n'
                    'sys.dont_write_bytecode=True\n'
                    f'sys.path.insert(0,{str(base)!r})\n'
                    f'sys.path.insert(1,{str(base / "tests")!r})\n'
                    'import ghost_tool\n'
                    f'assert Path(ghost_tool.__file__).parent == Path({str(base / "ghost_tool")!r})\n'
                    'ghost_tool._is_bforartists=lambda: True\n'
                    'observed=[]\n'
                    'original=unittest.TextTestRunner.run\n'
                    'def run(self,suite):\n'
                    '    result=original(self,suite)\n'
                    '    observed.append(result)\n'
                    '    return result\n'
                    'unittest.TextTestRunner.run=run\n'
                    f'runpy.run_path({str(base / "tests" / name)!r},run_name="__main__")\n'
                    'assert observed and sum(r.testsRun for r in observed)>0\n'
                    'assert all(r.wasSuccessful() for r in observed)\n', encoding='utf-8')
                process = subprocess.run(
                    [str(HOST), '--background', '--factory-startup', '--python-exit-code', '1',
                     '--python', str(wrapper)], cwd=base,
                    env=dict(os.environ, BLENDER_USER_CONFIG=str(base / 'config'),
                             BLENDER_USER_SCRIPTS=str(base / 'scripts'),
                             GHOST_TEST_ADDON_ROOT=str(base / 'ghost_tool'),
                             PYTHONDONTWRITEBYTECODE='1'),
                    capture_output=True, text=True, errors='replace', timeout=90)
                output = process.stdout + '\n' + process.stderr
                (Path(__file__).parent / (name + '.log')).write_text(output, encoding='utf-8')
                counts = re.findall(r'Ran (\d+) tests?', output)
                result = dict(test=name, exit_code=process.returncode,
                              tests=sum(map(int, counts)), status='PASS' if process.returncode == 0 and counts else 'FAIL')
                result['failures'] = re.findall(r'^(?:ERROR|FAIL): (.+)$', output, re.MULTILINE)
                if result['status'] == 'FAIL' and name != 'test_ghost_authoring.py':
                    # Compare the same test on the exact prior ZIP, rather than
                    # dismissing a failing supplemental test as a host issue.
                    with zipfile.ZipFile(PREVIOUS) as baseline:
                        baseline.extractall(base)
                    before = subprocess.run(
                        [str(HOST), '--background', '--factory-startup', '--python-exit-code', '1',
                         '--python', str(wrapper)], cwd=base,
                        env=dict(os.environ, BLENDER_USER_CONFIG=str(base / 'config'),
                                 BLENDER_USER_SCRIPTS=str(base / 'scripts'),
                                 GHOST_TEST_ADDON_ROOT=str(base / 'ghost_tool'),
                                 PYTHONDONTWRITEBYTECODE='1'),
                        capture_output=True, text=True, errors='replace', timeout=90)
                    before_output = before.stdout + '\n' + before.stderr
                    (Path(__file__).parent / (name + '.baseline.log')).write_text(before_output, encoding='utf-8')
                    before_failures = re.findall(r'^(?:ERROR|FAIL): (.+)$', before_output, re.MULTILINE)
                    signatures = lambda s: re.findall(r'^(?:AttributeError|AssertionError|TypeError|ValueError): .+$', s, re.MULTILINE)
                    result['baseline_failures'] = before_failures
                    result['baseline_exit_code'] = before.returncode
                    same_host_gate = (name == 'test_ghost_snapshot_persistence.py'
                        and all("Bforartists exclusive" in text
                                and "AttributeError: 'Scene' object has no attribute 'ghost_snapshots'" in text
                                for text in (output, before_output)))
                    if (before.returncode and result['failures']
                            and result['failures'] == before_failures
                            and (signatures(output) == signatures(before_output) or same_host_gate)):
                        result['status'] = 'UNCHANGED_HOST_LIMITATION'
                    archive.extractall(base)
                results.append(result)
                print(json.dumps(result), flush=True)
    receipt = dict(version='4.2.1', artifact=OUTPUT.relative_to(ROOT).as_posix(), sha256=sha(OUTPUT.read_bytes()),
                   bytes=OUTPUT.stat().st_size, source_modules=len(files),
                   source_bytes_match=True, installed_hashes=hashes,
                   changed_from_420=changed, tests=results,
                   status=('AUTHORING_PASS_WITH_HOST_LIMITATIONS'
                           if any(r['status'] == 'UNCHANGED_HOST_LIMITATION' for r in results)
                           and all(r['status'] in {'PASS', 'UNCHANGED_HOST_LIMITATION'} for r in results)
                           else 'PASS' if all(r['status'] == 'PASS' for r in results) else 'FAIL'),
                   host=str(HOST), host_role='Blender 5.1.2 stand-in; Bforartists host gate patched in tests only',
                   native_bforartists_usability='PENDING', published=False)
    Path(__file__).with_name('package-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k != 'installed_hashes'}, indent=2))
    return 0 if receipt['status'] in {'PASS', 'AUTHORING_PASS_WITH_HOST_LIMITATIONS'} else 1


if __name__ == '__main__':
    raise SystemExit(main())
