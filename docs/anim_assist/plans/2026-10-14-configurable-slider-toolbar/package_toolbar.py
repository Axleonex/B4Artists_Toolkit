"""Deterministic add-on packaging; preserves old archives and exact inventory."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tomllib
import zipfile

ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'anim_assist'
PACKET=Path(__file__).resolve().parent
NEW=('ui/timeline_config.py','ui/timeline_settings.py','core/timeline_slider_session.py','operators/timeline_slider_ops.py')
EXPECTED={'__init__.py','constants.py','blender_manifest.toml','CHANGELOG.md','prefs.py',
          'core/p5_sampling.py','core/p9_mirror_math.py','operators/p9_mirror_ops.py',
          'operators/__init__.py','operators/curve_tool_ops.py','operators/settings_ops.py',
          'ui/timeline_strip.py','ui/timeline_catalog.py','ui/timeline_overlay.py',*NEW}


def literal(text,name):
    for node in ast.parse(text).body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in node.targets):
            return ast.literal_eval(node.value)
        if isinstance(node,ast.AnnAssign) and isinstance(node.target,ast.Name) and node.target.id==name:
            return ast.literal_eval(node.value)
    raise ValueError('Missing '+name)


def package(next_version=False,release_version=None,evidence_directory=None):
    constants=(SOURCE/'constants.py').read_text()
    version=literal(constants,'ADDON_VERSION_STRING')
    baseline=ROOT/'releases/b4_anim_assist_v12.6.1.zip'
    if next_version or release_version:
        known=[tuple(map(int,version.split('.')))]
        for path in (ROOT/'releases').glob('b4_anim_assist_v*.zip'):
            match=re.fullmatch(r'b4_anim_assist_v(\d+)\.(\d+)\.(\d+)\.zip',path.name)
            if match: known.append(tuple(map(int,match.groups())))
        major,minor,patch=max(known)
        resolved=release_version or f'{major}.{minor}.{patch+1}'
        if not re.fullmatch(r'\d+\.\d+\.\d+',resolved) or tuple(map(int,resolved.split('.')))<=max(known):
            raise ValueError('Choose an unused version newer than all existing Anim Assist versions')
        # Read-only remote identity check; never publish or move branches here.
        occupied=subprocess.check_output(['git','ls-remote','--tags','origin','refs/tags/v'+resolved],cwd=ROOT,text=True).strip()
        if occupied: raise ValueError('The proposed release tag is already occupied: '+resolved)
        for relative in ('__init__.py','constants.py','blender_manifest.toml'):
            path=SOURCE/relative; text=path.read_text()
            text=text.replace('"'+version+'"','"'+resolved+'"')
            text=text.replace('('+', '.join(version.split('.'))+')','('+', '.join(resolved.split('.'))+')')
            path.write_text(text,encoding='utf-8')
        version=resolved
    tuple_version=tuple(map(int,version.split('.')))
    info=literal((SOURCE/'__init__.py').read_text(),'bl_info')
    constants=(SOURCE/'constants.py').read_text()
    manifest=tomllib.loads((SOURCE/'blender_manifest.toml').read_text())
    assert info['version']==literal(constants,'ADDON_VERSION')==tuple_version
    assert literal(constants,'ADDON_VERSION_STRING')==manifest['version']==version
    output=ROOT/'releases'/f'b4_anim_assist_v{version}.zip'
    receipt=(Path(evidence_directory).resolve() if evidence_directory else PACKET/'evidence/final')/'artifact.json'
    receipt.parent.mkdir(parents=True,exist_ok=True)
    if output.exists():
        previous=json.loads(receipt.read_text())
        if previous['version']!=version or previous['sha256']!=hashlib.sha256(output.read_bytes()).hexdigest():
            raise ValueError('Existing archive is not this task’s recorded output')
    with zipfile.ZipFile(baseline) as archive:
        originals={m.filename:archive.read(m) for m in archive.infolist() if not m.is_dir()}
    root={name.split('/')[0] for name in originals}.pop()
    names=set(originals)|{root+'/'+name for name in NEW}
    contents={name:(SOURCE/name.split('/',1)[1]).read_bytes() for name in sorted(names)}
    syntax=0
    for name,data in contents.items():
        assert not name.lower().endswith(('.exe','.dll'))
        if name.endswith('.py'): ast.parse(data.decode('utf-8-sig')); syntax+=1
    changed={name.split('/',1)[1] for name,data in contents.items() if originals.get(name)!=data}
    assert changed==EXPECTED, (changed-EXPECTED,EXPECTED-changed)
    prior=literal(originals[root+'/ui/timeline_catalog.py'].decode(),'ACTIONS')
    current=literal(contents[root+'/ui/timeline_catalog.py'].decode(),'ACTIONS')
    assert len(current)==89 and current==prior, 'Existing dispatch mappings changed'
    model=contents[root+'/ui/timeline_config.py'].decode()
    assert len(literal(model,'SLIDERS'))==8 and len(literal(model,'FAMILY_ORDER'))==7
    pending=output.with_suffix('.zip.pending')
    with zipfile.ZipFile(pending,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name,data in contents.items():
            entry=zipfile.ZipInfo(name,date_time=(2026,10,14,0,0,0)); entry.compress_type=zipfile.ZIP_DEFLATED
            entry.external_attr=0o100644<<16; archive.writestr(entry,data,compresslevel=9)
    pending.replace(output)
    evidence=dict(version=version,zip_path=str(output),sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
        bytes=output.stat().st_size,files=len(contents),python_syntax_files=syntax,changed=sorted(changed),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        application_binaries=0,catalogue_actions=89,scalar_tools=8,
        source_sha256={name:hashlib.sha256(data).hexdigest() for name,data in contents.items()},
        status='local release; final native validation pending')
    receipt.write_text(json.dumps(evidence,indent=2))
    print(json.dumps({key:value for key,value in evidence.items() if key!='source_sha256'},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    versions=parser.add_mutually_exclusive_group()
    versions.add_argument('--next-version',action='store_true')
    versions.add_argument('--release-version',help='Explicit newer minor/major version for an approved overhaul')
    parser.add_argument('--evidence-directory',help='New qualification receipt directory; historical receipts remain intact')
    args=parser.parse_args()
    package(args.next_version,args.release_version,args.evidence_directory)
