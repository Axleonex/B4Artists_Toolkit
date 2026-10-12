"""Build and verify Ghost Tool 4.2.4 from the exact current-main baseline."""
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[4]
OUTPUT = ROOT / 'releases/b4_ghost_tool_v4.2.4.zip'
HOST = Path(r'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe')
TESTS = ('test_ghost_council_ui.py', 'test_ghost_header_ui.py',
         'test_ghost_marker_targets_ui.py', 'test_ghost_authoring.py')
sys.path.insert(0, str(ROOT / 'tests'))
from run_ghost_afterimage import bootstrap


def main():
    files = sorted((ROOT / 'ghost_tool').glob('*.py'))
    assert files
    for path in files:
        tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
        if path.name == '__init__.py':
            info = next(ast.literal_eval(n.value) for n in tree.body
                        if isinstance(n, ast.Assign)
                        and any(isinstance(t, ast.Name) and t.id == 'bl_info' for t in n.targets))
            assert info['version'] == (4, 2, 4)
        if path.name == 'ui_panel.py':
            assert 'ghost_tool.open_settings_editor' not in path.read_text(encoding='utf-8')
            assert not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                           and n.func.attr == 'operator' and n.args
                           and isinstance(n.args[0], ast.Constant)
                           and n.args[0].value == 'ghost_tool.open_window' for n in ast.walk(tree))
    if not OUTPUT.exists():
        with zipfile.ZipFile(OUTPUT, 'x', zipfile.ZIP_DEFLATED) as archive:
            for path in files:
                archive.write(path, 'ghost_tool/' + path.name)
    results = []
    with zipfile.ZipFile(OUTPUT) as archive, tempfile.TemporaryDirectory(prefix='ghost-424-') as folder:
        assert archive.testzip() is None
        assert set(archive.namelist()) == {'ghost_tool/' + p.name for p in files}
        assert all(archive.read('ghost_tool/' + p.name) == p.read_bytes() for p in files)
        normalize = lambda data: data.replace(b'\r\n', b'\n')
        with zipfile.ZipFile(ROOT / 'releases/b4_ghost_tool_v4.2.3.zip') as previous:
            changed = [name for name in archive.namelist()
                       if name not in previous.namelist()
                       or normalize(archive.read(name)) != normalize(previous.read(name))]
        assert set(changed) == {'ghost_tool/__init__.py', 'ghost_tool/ui_panel.py'}, changed
        base = Path(folder)
        archive.extractall(base)
        shutil.copytree(ROOT / 'tests', base / 'tests',
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        for name in TESTS:
            wrapper = base / 'run_test.py'
            wrapper.write_text(
                'import sys\nsys.dont_write_bytecode=True\n'
                f'sys.path.insert(0,{str(base)!r})\nimport ghost_tool\n'
                'ghost_tool._is_bforartists=lambda: True\n'
                'ghost_tool._clear_pycache=lambda: None\n' + bootstrap(base / 'tests' / name),
                encoding='utf-8')
            process = subprocess.run(
                [str(HOST), '--background', '--factory-startup', '--python-exit-code', '1',
                 '--python', str(wrapper)], cwd=base, capture_output=True, text=True,
                errors='replace', timeout=90, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
                BLENDER_USER_CONFIG=str(base / 'config'), BLENDER_USER_SCRIPTS=str(base / 'scripts'),
                GHOST_TEST_ADDON_ROOT=str(base / 'ghost_tool')))
            output = process.stdout + '\n' + process.stderr
            Path(__file__).with_name(name + '.log').write_text(output, encoding='utf-8')
            observed = [json.loads(line.split('AFTERIMAGE_TEST_RESULT ', 1)[1])
                        for line in output.splitlines() if line.startswith('AFTERIMAGE_TEST_RESULT ')]
            result = dict(test=name, exit_code=process.returncode,
                          tests=sum(r['tests'] for r in observed),
                          status='PASS' if process.returncode == 0 and observed else 'FAIL')
            results.append(result)
            print(json.dumps(result), flush=True)
    receipt = dict(version='4.2.4', artifact=str(OUTPUT), bytes=OUTPUT.stat().st_size,
                   sha256=hashlib.sha256(OUTPUT.read_bytes()).hexdigest(), source_modules=len(files),
                   source_bytes_match=True, changed_from_423=changed, comparison_lf_normalized=True,
                   tests=results,
                   status='PASS' if all(r['status'] == 'PASS' for r in results) else 'FAIL',
                   host=str(HOST), host_role='Blender stand-in; Bforartists gate patched in tests only',
                   native_bforartists_usability='NOT VERIFIED', published=False,
                   routing=dict(recommended_lane='T3_PRIME_OMP', actual_lane='T3_PRIME_OMP',
                   policy_fingerprint='29fa965cada3128ffe57b5d85d3b9f8e5d749d780954ea14ba5f45dcca1ad8b8',
                   outcome='Native fallback: OMP runtime unavailable on Windows (Unix sockets required)',
                   authorization_risk='low_static', escalation_count=0))
    Path(__file__).with_name('package-receipt.json').write_text(
        json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))
    return 0 if receipt['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
