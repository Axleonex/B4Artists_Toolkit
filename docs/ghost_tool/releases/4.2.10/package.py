"""Build/check the unpublished 4.2.10 candidate in disposable native sessions.

[PowerShell] python docs/ghost_tool/releases/4.2.10/package.py --verify
--shelf-only records native width evidence; --verify reuses it only when the
archive, native test, result and log hashes still match.
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

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
ARCHIVE = ROOT / 'releases/b4_ghost_tool_v4.2.10.zip'
OUTPUT = ROOT / 'build/ghost-toolbar/release-4.2.10'
HOST = Path(r'G:\LapArt\.cache\bforartists\5.2.0\portable\Bforartists-5.2.0-Windows\bforartists.exe')
SUITES = ('test_ghost_display_location.py', 'test_ghost_toolbar_ui.py',
          'test_ghost_cached_display.py', 'test_ghost_authoring.py', 'test_ghost_shelf_width.py')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def invoke(base, code, name, *, gui=False):
    wrapper = base / (name + '.py')
    wrapper.write_text(code, encoding='utf-8')
    command = [str(HOST), '--factory-startup', '--threads', '2', '--python-exit-code', '1', '--python', str(wrapper)]
    command[1:1] = (['--enable-event-simulate', '--window-geometry', '0', '0', '1920', '1000']
                    if gui else ['--background'])
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    env = dict(os.environ, BLENDER_USER_CONFIG=str(base / 'config'),
               BLENDER_USER_SCRIPTS=str(base / 'scripts'), PYTHONUNBUFFERED='1',
               PYTHONDONTWRITEBYTECODE='1', GHOST_SHELF_OUTPUT=str(OUTPUT), GHOST_SPLIT_OUTPUT=str(OUTPUT))
    log = OUTPUT / (name + '.log')
    with log.open('wb') as stream:
        result = subprocess.run(command, cwd=base, env=env, startupinfo=startup,
                                stdout=stream, stderr=subprocess.STDOUT, timeout=240)
    text = log.read_text(encoding='utf-8', errors='replace')
    assert result.returncode == 0, text[-6000:]
    return dict(suite=name, exit_code=result.returncode, status='PASS',
                log_sha256=sha(log), tests=sum(map(int, re.findall(r'Ran (\d+) tests?', text))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--shelf-only', action='store_true')
    args = parser.parse_args()
    sources = sorted((ROOT / 'ghost_tool').glob('*.py'))
    for source in sources:
        ast.parse(source.read_text(encoding='utf-8'))
    if not (args.verify or args.shelf_only):
        with zipfile.ZipFile(ARCHIVE, 'w', zipfile.ZIP_DEFLATED) as archive:
            for source in sources:
                entry = zipfile.ZipInfo('ghost_tool/' + source.name, (2026, 10, 13, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(entry, source.read_bytes())
        print(json.dumps(dict(archive=ARCHIVE.name, bytes=ARCHIVE.stat().st_size, sha256=sha(ARCHIVE))))
        return
    OUTPUT.mkdir(parents=True, exist_ok=True)
    results = []
    with tempfile.TemporaryDirectory(prefix='ghost-release-4.2.10-', ignore_cleanup_errors=True) as folder:
        base = Path(folder)
        with zipfile.ZipFile(ARCHIVE) as archive:
            assert archive.testzip() is None
            assert sorted(archive.namelist()) == ['ghost_tool/' + p.name for p in sources]
            assert all(archive.read('ghost_tool/' + p.name) == p.read_bytes() for p in sources)
            archive.extractall(base)
        info = next(ast.literal_eval(n.value) for n in ast.parse((base / 'ghost_tool/__init__.py').read_text()).body
                    if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'bl_info' for t in n.targets))
        assert info['version'] == (4, 2, 10)
        shutil.copytree(ROOT / 'tests', base / 'tests', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        preamble = ('import sys,runpy;sys.dont_write_bytecode=True;'
                    f'sys.path.insert(0,{str(base)!r});sys.path.insert(0,{str(base / "tests")!r});'
                    'import ghost_tool;assert ghost_tool._is_bforartists();')
        if args.verify:
            background = preamble + (
                'import unittest,test_ghost_header_ui as h;ghost_tool.register();'
                "s=unittest.TestSuite([h.GhostHeaderUI('test_optional_sidebar_and_toolbar_preserved_without_duplicate_header')]);"
                'r=unittest.TextTestRunner(verbosity=2).run(s);ghost_tool.unregister();assert r.wasSuccessful();')
            for name in SUITES:
                background += f'runpy.run_path({str(base / "tests" / name)!r},run_name="__main__");'
            result = invoke(base, background, 'background')
            assert result['tests'] > 0
            results.append(result)
            print(json.dumps(result), flush=True)
        checkpoint = OUTPUT / 'shelf-checkpoint.json'
        shelf_test = ROOT / 'tests/test_ghost_shelf_width_native.py'
        shelf_result = OUTPUT / 'shelf-result.json'
        saved = json.loads(checkpoint.read_text()) if checkpoint.exists() else {}
        reuse = (saved.get('archive_sha256') == sha(ARCHIVE)
                 and saved.get('test_sha256') == sha(shelf_test)
                 and shelf_result.exists() and saved.get('result_sha256') == sha(shelf_result)
                 and (OUTPUT / 'native-shelf.log').exists()
                 and saved.get('log_sha256') == sha(OUTPUT / 'native-shelf.log'))
        if reuse:
            result = saved['result']
            assert result['status'] == 'PASS' and result['exit_code'] == 0
        else:
            shelf_result.unlink(missing_ok=True)
            result = invoke(base, preamble + f'runpy.run_path({str(base / "tests/test_ghost_shelf_width_native.py")!r},run_name="__main__")', 'native-shelf', gui=True)
            data = json.loads(shelf_result.read_text()) if shelf_result.exists() else {}
            assert data.get('status') == 'PASS', data
            result.update(tests=len(data['checks']), evidence=data)
            checkpoint.write_text(json.dumps(dict(archive_sha256=sha(ARCHIVE), test_sha256=sha(shelf_test),
                result_sha256=sha(shelf_result), log_sha256=result['log_sha256'], result=result), indent=2))
        results.append(result)
        print(json.dumps(dict(result, reused_exact_archive_evidence=reuse)), flush=True)
        if args.shelf_only:
            return
        split_result = OUTPUT / 'result.json'
        split_result.unlink(missing_ok=True)
        result = invoke(base, preamble + f'runpy.run_path({str(base / "tests/test_ghost_toolbar_split.py")!r},run_name="__main__")', 'native-split', gui=True)
        data = json.loads(split_result.read_text()) if split_result.exists() else {}
        assert data.get('status') == 'PASS', data
        result.update(tests=len(data['checks']), evidence=data)
        results.append(result)
        print(json.dumps(result), flush=True)
    receipt = dict(version='4.2.10', status='PASS', archive=ARCHIVE.name,
        bytes=ARCHIVE.stat().st_size, sha256=sha(ARCHIVE), source_modules=len(sources),
        extracted_bytes_match=True, host='Bforartists 5.2.0 (Blender runtime 5.3.0 Alpha)',
        native_gui_host_gate_patched=False, native_output_capture='files', native_thread_limit=2,
        results=results, total_checks=sum(r['tests'] for r in results),
        source_manifest={p.name: sha(p) for p in sources},
        pdf={'path': 'docs/ghost_tool/GhostTool_User_Manual.pdf', 'sha256': sha(ROOT / 'docs/ghost_tool/GhostTool_User_Manual.pdf')},
        published=False)
    (HERE / 'package-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(status='PASS', total_checks=receipt['total_checks'])), flush=True)


if __name__ == '__main__':
    main()
