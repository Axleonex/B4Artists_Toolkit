"""Build and verify Ghost Tool 4.2.7 in disposable native Bforartists sessions.

[PowerShell] python docs/ghost_tool/releases/4.2.7/package.py
Use --verify after the final guides/PDF are ready. Existing archives are preserved.
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
ARCHIVE = ROOT / 'releases/b4_ghost_tool_v4.2.7.zip'
HOST = Path(r'G:\LapArt\.cache\bforartists\5.2.0\portable\Bforartists-5.2.0-Windows\bforartists.exe')
OUTPUT = ROOT / 'build/ghost-toolbar/release-4.2.7'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    sources = sorted((ROOT / 'ghost_tool').glob('*.py'))
    for source in sources:
        ast.parse(source.read_text(encoding='utf-8'))
    if not args.verify:
        with zipfile.ZipFile(ARCHIVE, 'w', zipfile.ZIP_DEFLATED) as archive:
            for source in sources:
                entry = zipfile.ZipInfo('ghost_tool/' + source.name, (2026, 10, 12, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(entry, source.read_bytes())
        print(json.dumps(dict(archive=ARCHIVE.name, bytes=ARCHIVE.stat().st_size, sha256=sha(ARCHIVE))))
        return
    spec = importlib.util.spec_from_file_location('verifier', ROOT / 'docs/ghost_tool/toolbar/verify.py')
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    verifier.HOST = HOST
    verifier.OUTPUT = OUTPUT
    OUTPUT.mkdir(parents=True, exist_ok=True)
    results = []
    legacy = '''import bpy
class LegacyPrefs(bpy.types.AddonPreferences):
 bl_idname='ghost_tool'
 display_location:bpy.props.EnumProperty(items=(('HEADER','Header','',0),('SIDEBAR','Sidebar','',1),('TOOLS','Tools','',2),('TOOLBAR','Toolbar','',3)),default='HEADER')
 show_toolbar:bpy.props.BoolProperty(default=True)
bpy.utils.register_class(LegacyPrefs)
addon=bpy.context.preferences.addons.new();addon.module='ghost_tool'
addon.preferences.display_location='HEADER';addon.preferences.show_toolbar=False
bpy.utils.unregister_class(LegacyPrefs)
'''
    with tempfile.TemporaryDirectory(prefix='ghost-release-4.2.7-') as folder:
        base = Path(folder)
        with zipfile.ZipFile(ARCHIVE) as archive:
            assert archive.testzip() is None
            assert sorted(archive.namelist()) == ['ghost_tool/' + p.name for p in sources]
            assert all(archive.read('ghost_tool/' + p.name) == p.read_bytes() for p in sources)
            archive.extractall(base)
        module = ast.parse((base / 'ghost_tool/__init__.py').read_text(encoding='utf-8'))
        info = next(ast.literal_eval(node.value) for node in module.body
                    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'bl_info' for t in node.targets))
        assert info['version'] == (4, 2, 7)
        shutil.copytree(ROOT / 'tests', base / 'tests', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        preamble = ('import sys,os,runpy;sys.dont_write_bytecode=True;'
                    f'sys.path.insert(0,{str(base)!r});sys.path.insert(0,{str(base / "tests")!r});'
                    'import ghost_tool;assert ghost_tool._is_bforartists();')
        for name in verifier.SUITES:
            try:
                result = verifier.invoke(base, preamble + f'runpy.run_path({str(base / "tests" / name)!r},run_name="__main__")', name.removesuffix('.py'))
            except subprocess.TimeoutExpired as exc:
                partial = (exc.stdout or b'') + (exc.stderr or b'')
                if isinstance(partial, bytes):
                    partial = partial.decode('utf-8', errors='replace')
                (OUTPUT / (name + '.timeout.log')).write_text(partial, encoding='utf-8')
                raise
            results.append(result)
            print(json.dumps(result), flush=True)
            assert result['status'] == 'PASS', name
        for name, migrate in (('native-default', False), ('native-migrated', True)):
            evidence = OUTPUT / (name + '.json')
            evidence.unlink(missing_ok=True)
            code = preamble + (f'exec({legacy!r});' if migrate else '') + (
                f'os.environ["GHOST_TOOLBAR_TEST_OUTPUT"]={str(evidence)!r};'
                'os.environ["GHOST_TOOLBAR_TEST_SCALE"]="1.0";os.environ["GHOST_TOOLBAR_TEST_MAXIMIZE"]="1";'
                'os.environ["GHOST_TOOLBAR_TEST_TIER"]="FULL";'
                f'os.environ["GHOST_TOOLBAR_SCREEN_PREFIX"]={str(OUTPUT / name)!r};'
                f'runpy.run_path({str(base / "tests/test_ghost_toolbar_native.py")!r},run_name="__main__")')
            result = verifier.invoke(base, code, name, gui=True, width=1920, height=1000)
            data = json.loads(evidence.read_text()) if evidence.exists() else {}
            result.update(tests=len(data.get('checks', [])), evidence=data,
                          status='PASS' if result['exit_code'] == 0 and data.get('status') == 'PASS' else 'FAIL')
            results.append(result)
            print(json.dumps(result), flush=True)
            assert result['status'] == 'PASS', name
    receipt = dict(version='4.2.7', status='PASS', archive=ARCHIVE.name,
                   bytes=ARCHIVE.stat().st_size, sha256=sha(ARCHIVE), source_modules=len(sources),
                   extracted_bytes_match=True, host='Bforartists 5.2.0 (Blender runtime 5.3.0 Alpha)',
                   host_registration_gate_patched=False, results=results,
                   total_checks=sum(r['tests'] for r in results),
                   source_manifest={p.name: sha(p) for p in sources},
                   pdf={'path': 'docs/ghost_tool/GhostTool_User_Manual.pdf', 'sha256': sha(ROOT / 'docs/ghost_tool/GhostTool_User_Manual.pdf')},
                   published=False)
    (HERE / 'package-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'PASS', 'total_checks': receipt['total_checks']}), flush=True)


if __name__ == '__main__':
    main()
