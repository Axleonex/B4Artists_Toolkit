"""Build/check 4.2.9; [PowerShell] python docs/ghost_tool/releases/4.2.9/package.py --verify.

Verification extracts the exact ZIP and runs focused regressions in disposable
native Bforartists sessions. Historical packages and receipts are preserved.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
ARCHIVE = ROOT / 'releases/b4_ghost_tool_v4.2.9.zip'
OUTPUT = ROOT / 'build/ghost-toolbar/release-4.2.9'
HOST = Path(r'G:\LapArt\.cache\bforartists\5.2.0\portable\Bforartists-5.2.0-Windows\bforartists.exe')
SUITES = ('test_ghost_toolbar_ui.py', 'test_ghost_display_location.py',
          'test_ghost_cached_display.py', 'test_ghost_authoring.py')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--gui-only', action='store_true', help='Reuse background evidence bound to the same ZIP')
    args = parser.parse_args()
    sources = sorted((ROOT / 'ghost_tool').glob('*.py'))
    for source in sources:
        ast.parse(source.read_text(encoding='utf-8'))
    if not (args.verify or args.gui_only):
        with zipfile.ZipFile(ARCHIVE, 'w', zipfile.ZIP_DEFLATED) as archive:
            for source in sources:
                entry = zipfile.ZipInfo('ghost_tool/' + source.name, (2026, 10, 13, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(entry, source.read_bytes())
        print(json.dumps(dict(archive=ARCHIVE.name, bytes=ARCHIVE.stat().st_size, sha256=sha(ARCHIVE))))
        return
    spec = importlib.util.spec_from_file_location('verifier', ROOT / 'docs/ghost_tool/toolbar/verify.py')
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    verifier.HOST, verifier.OUTPUT = HOST, OUTPUT
    OUTPUT.mkdir(parents=True, exist_ok=True)
    # Native cold starts on this host can exceed the stand-in harness limit,
    # in background mode too. Keep every disposable launch bounded.
    native_run = subprocess.run
    def bounded_run(*args, **kwargs):
        kwargs['timeout'] = 240
        # File capture avoids Windows subprocess pipe-reader threads and
        # leaves live diagnostics available during a slow native cold start.
        command = list(args[0])
        if '--background' not in command:
            command[1:1] = ['--threads', '2']
        args = (command,) + args[1:]
        log_path = OUTPUT / (Path(command[-1]).stem + '.live.log')
        kwargs.pop('capture_output', None)
        with log_path.open('wb') as stream:
            kwargs['stdout'], kwargs['stderr'] = stream, subprocess.STDOUT
            result = native_run(*args, **kwargs)
        result.stdout = log_path.read_text(encoding='utf-8', errors='replace')
        result.stderr = ''
        return result
    verifier.subprocess.run = bounded_run
    results = []
    checkpoint = OUTPUT / 'background-checkpoint.json'
    with tempfile.TemporaryDirectory(prefix='ghost-release-4.2.9-', ignore_cleanup_errors=True) as folder:
        base = Path(folder)
        with zipfile.ZipFile(ARCHIVE) as archive:
            assert archive.testzip() is None
            assert sorted(archive.namelist()) == ['ghost_tool/' + p.name for p in sources]
            assert all(archive.read('ghost_tool/' + p.name) == p.read_bytes() for p in sources)
            archive.extractall(base)
        module = ast.parse((base / 'ghost_tool/__init__.py').read_text(encoding='utf-8'))
        info = next(ast.literal_eval(node.value) for node in module.body
                    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'bl_info' for t in node.targets))
        assert info['version'] == (4, 2, 9)
        shutil.copytree(ROOT / 'tests', base / 'tests', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        preamble = ('import sys,os,runpy;sys.dont_write_bytecode=True;'
                    f'sys.path.insert(0,{str(base)!r});sys.path.insert(0,{str(base / "tests")!r});'
                    'import ghost_tool;assert ghost_tool._is_bforartists();')
        if args.gui_only:
            saved = json.loads(checkpoint.read_text())
            assert saved['archive_sha256'] == sha(ARCHIVE)
            results = saved['results']
            assert [r['suite'] for r in results] == [name[:-3] for name in SUITES]
            assert all(r['status'] == 'PASS' and r['exit_code'] == 0 for r in results)
        else:
            for name in SUITES:
                result = verifier.invoke(base, preamble + f'runpy.run_path({str(base / "tests" / name)!r},run_name="__main__")', name[:-3])
                results.append(result)
                print(json.dumps(result), flush=True)
                assert result['status'] == 'PASS', name
            checkpoint.write_text(json.dumps(dict(archive_sha256=sha(ARCHIVE), results=results), indent=2))
        # This native GUI run does not patch the add-on or its platform gate.
        evidence_path = OUTPUT / 'result.json'
        evidence_path.unlink(missing_ok=True)
        code = preamble + (f'os.environ["GHOST_SPLIT_OUTPUT"]={str(OUTPUT)!r};'
                           f'runpy.run_path({str(base / "tests/test_ghost_toolbar_split.py")!r},run_name="__main__")')
        result = verifier.invoke(base, code, 'native-split', gui=True, width=1920, height=1000)
        data = json.loads(evidence_path.read_text()) if evidence_path.exists() else {}
        assert result['exit_code'] == 0 and data.get('status') == 'PASS', 'Native GUI failed; inspect native-split.live.log'
        result.update(tests=len(data['checks']), evidence=data,
                      status='PASS' if result['exit_code'] == 0 and data['status'] == 'PASS' else 'FAIL')
        results.append(result)
        print(json.dumps(result), flush=True)
        assert result['status'] == 'PASS'
    receipt = dict(version='4.2.9', status='PASS', archive=ARCHIVE.name,
                   bytes=ARCHIVE.stat().st_size, sha256=sha(ARCHIVE), source_modules=len(sources),
                   extracted_bytes_match=True, host='Bforartists 5.2.0 (Blender runtime 5.3.0 Alpha)',
                   native_gui_host_gate_patched=False, results=results,
                   native_output_capture='files',
                   native_gui_thread_limit=2,
                   total_checks=sum(r['tests'] for r in results),
                   source_manifest={p.name: sha(p) for p in sources},
                   pdf={'path': 'docs/ghost_tool/GhostTool_User_Manual.pdf', 'sha256': sha(ROOT / 'docs/ghost_tool/GhostTool_User_Manual.pdf')},
                   published=False)
    (HERE / 'package-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(status='PASS', total_checks=receipt['total_checks'])), flush=True)


if __name__ == '__main__':
    main()
