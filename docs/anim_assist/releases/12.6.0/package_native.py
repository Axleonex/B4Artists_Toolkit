"""Refresh the task-owned portable release without changing compiled runtime bytes."""
from pathlib import Path,PurePosixPath
import hashlib
import json
import os
import shutil
import zipfile

PROJECT=Path(__file__).resolve().parents[4]
DOCS=Path(__file__).resolve().parent
RELEASE=Path('G:/LapArt/Local-Releases/AnimAssist/12.6.0').resolve()
NAME='Bforartists_5.2.0_AnimAssist_12.6.0_Windows_x64.zip'
archive=RELEASE/NAME
temporary=RELEASE/(NAME+'.refresh.zip')
assert archive.resolve().parent==temporary.resolve().parent==RELEASE
old=json.loads((RELEASE/'release-receipt.json').read_text())
digest=lambda path: hashlib.file_digest(path.open('rb'),'sha256').hexdigest()
assert digest(archive)==old['application_archive_sha256'],'Existing task release differs from receipt'
addon=PROJECT/'releases/b4_anim_assist_v12.6.0.zip'
package=json.loads((DOCS/'package-receipt.json').read_text())
assert digest(addon)==package['sha256']
mapping={
 'AnimAssist/b4_anim_assist_v12.6.0.zip':addon,
 'README-FIRST.txt':RELEASE/'README-FIRST.txt',
}
for name in ('RELEASE-NOTES.md','qualification.md','tool-access-coverage.md',
             'package-receipt.json','native-observations.json'):
    mapping['AnimAssist/'+name]=DOCS/name
for path in (PROJECT/'native_patches/bforartists/5.2.0').iterdir():
    if path.name in {'README.md','build-info.json','native-timeline-toolbar.patch','review-summary.md'}:
        mapping['AnimAssist/NativeSource/'+path.name]=path
for filename,newname in (
 ('docs/superpowers/specs/2026-10-12-native-timeline-toolbar-design.md','native-timeline-toolbar-design.md'),
 ('docs/superpowers/specs/2026-10-12-native-timeline-toolbar-access.md','native-timeline-toolbar-access.md'),
 ('docs/plans/2026-10-13-native-timeline-toolbar-implementation.md','native-timeline-toolbar-implementation.md')):
    mapping['AnimAssist/Design/'+newname]=PROJECT/filename
for path in (DOCS/'native-evidence').rglob('*'):
    if path.is_file():
        mapping['AnimAssist/native-evidence/'+path.relative_to(DOCS/'native-evidence').as_posix()]=path
for filename in ('native_timeline_validation.py','unpatched_timeline_validation.py','summarize_native_validation.py'):
    mapping['AnimAssist/Validation/'+filename]=PROJECT/'tests'/filename

with zipfile.ZipFile(archive) as previous:
    names=previous.namelist()
    roots={PurePosixPath(n).parts[0] for n in names}
    assert len(roots)==1
    prefix=roots.pop()+'/'
    runtime=[n for n in names if not n.startswith(prefix+'AnimAssist/')
             and n not in {prefix+'Launch Anim Assist (isolated).cmd',prefix+'README-FIRST.txt'}]
    assert len(runtime)==8818,len(runtime)
    assert hashlib.sha256(previous.read(prefix+'bforartists.exe')).hexdigest()==old['application_executable_sha256']
    launcher=previous.read(prefix+'Launch Anim Assist (isolated).cmd')
    with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as output:
        for index,name in enumerate(runtime):
            with previous.open(name) as src,output.open(name,'w') as target:
                shutil.copyfileobj(src,target,1024*1024)
            if index%2000==0: print('Runtime files copied:',index,flush=True)
        output.writestr(prefix+'Launch Anim Assist (isolated).cmd',launcher)
        for relative,path in sorted(mapping.items()):
            output.write(path,prefix+relative)

with zipfile.ZipFile(archive) as previous,zipfile.ZipFile(temporary) as rebuilt:
    assert len(set(rebuilt.namelist()))==len(rebuilt.namelist()),'Duplicate paths'
    assert rebuilt.testzip() is None,'CRC failure'
    for name in runtime:
        assert rebuilt.getinfo(name).CRC==previous.getinfo(name).CRC
        assert rebuilt.getinfo(name).file_size==previous.getinfo(name).file_size
    assert rebuilt.read(prefix+'AnimAssist/b4_anim_assist_v12.6.0.zip')==addon.read_bytes()
    assert hashlib.sha256(rebuilt.read(prefix+'bforartists.exe')).hexdigest()==old['application_executable_sha256']
    for relative,path in mapping.items():
        assert rebuilt.read(prefix+relative)==path.read_bytes(),relative

os.replace(temporary,archive)
shutil.copy2(addon,RELEASE/addon.name)
receipt=json.loads((DOCS/'native-package-receipt.json').read_text())
receipt.update(status='built; available-host validation matrix passed with documented render/DPI limits; unpublished',
 application_archive_bytes=archive.stat().st_size,application_archive_sha256=digest(archive),
 addon_archive_bytes=addon.stat().st_size,addon_archive_sha256=digest(addon),
 observed=['All80 immediate action effects in patched and genuine unpatched hosts',
           'All9 native modal actions with live geometry, commit and cancellation',
           'Fresh row, pin/search/reset/empty/custom process persistence',
           'Editor resize in-gesture framebuffer samples at100%/150%; settled window resizing',
           'Migration, saved layouts, workspaces, multiple windows and maximized visibility lifecycle',
           'Native playback/scrub/keying/Undo/Redo; exact203 installed archive files'],
 limits=['Window-border native renders cover before/after only; universal absence of flicker not certified',
         'Windows global display DPI transitions unrun pending authorization',
         'Representative fixtures do not establish exhaustive production-rig or full AnimBot parity'],
 formal_tests='Native GUI integration assertions plus actual input; tests/summarize_native_validation.py audited evidence',
 validation_summary='native-evidence/full-validation/summary.json')
(DOCS/'native-package-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
external=dict(receipt)
external['qualification']='available-host matrix passed; documented window-render/DPI and algorithm limits'
(RELEASE/'release-receipt.json').write_text(json.dumps(external,indent=2)+'\n')
(RELEASE/(NAME+'.sha256')).write_text(receipt['application_archive_sha256']+'  '+NAME+'\n')
print(json.dumps({key:receipt[key] for key in ('application_archive_bytes','application_archive_sha256',
                                            'addon_archive_bytes','addon_archive_sha256')},indent=2))
