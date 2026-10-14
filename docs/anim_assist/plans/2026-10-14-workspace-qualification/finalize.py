"""Guarded local 12.7.0 release finalization; no publication or owner prefs."""
import hashlib,json,shutil,zipfile
from pathlib import Path

PACKET=Path(__file__).resolve().parent
ROOT=PACKET.parents[3]
def read(path):return json.loads(path.read_text(encoding='utf-8'))

def main():
    artifact=read(PACKET/'evidence/artifact/artifact.json')
    package=Path(artifact['zip_path']);digest=hashlib.sha256(package.read_bytes()).hexdigest()
    assert artifact['version']=='12.7.0' and digest==artifact['sha256']
    assert package.stat().st_size==artifact['bytes']==599297
    workflow=read(PACKET/'evidence/overhaul/workflow.json')
    assert workflow['passed'] and workflow['sha256']==digest and len(workflow['checks'])==53
    assert all(x['passed'] for x in workflow['checks'])
    initial=read(PACKET/'evidence/overhaul/first-start.json')
    assert initial[0]['height']==112 and initial[0]['controls']
    full=read(PACKET/'evidence/regression/full-coverage.json')
    assert full['passed'] and full['immediate']==80 and full['original_interactive_cases']==18
    assert full['native_bar_buttons']==21 and full['native_row_scalar_cases']==32 and full['recovery_assertions']==56
    assert read(PACKET/'evidence/regression/package-identity.json')['sha256']==digest
    for name,count in (('config',12),('session',6),('layout',5)):
        log=(PACKET/f'evidence/artifact/pure-{name}.log').read_text(encoding='utf-8-sig')
        assert f'Ran {count} tests' in log and '\nOK' in log and 'FAILED' not in log
    with zipfile.ZipFile(ROOT/'releases/b4_anim_assist_v12.6.2.zip') as previous,zipfile.ZipFile(package) as current:
        assert set(previous.namelist())==set(current.namelist())
        changed={x.split('/',1)[1] for x in current.namelist() if current.read(x)!=previous.read(x)}
        assert changed=={'CHANGELOG.md','__init__.py','constants.py','blender_manifest.toml'},changed
    release=ROOT/'docs/anim_assist/releases/12.7.0'
    receipt=dict(artifact,status='qualified local overhaul release',workspace_review='passed; delegated to Codex',
        owner_workspace_provided=False,independent_user_study=False,publication='not pushed',
        workflow_steps=len(workflow['checks']),functional_regression=full,
        changed_from_12_6_2=sorted(changed),qualification='qualification.md')
    (release/'package-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    destination=Path('G:/LapArt/Local-Releases/AnimAssist/12.7.0')
    destination.mkdir(parents=True,exist_ok=True);target=destination/package.name
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()!=digest:
        raise ValueError('Refusing to overwrite a different local release')
    shutil.copyfile(package,target)
    assert hashlib.sha256(target.read_bytes()).hexdigest()==digest
    shutil.copyfile(release/'package-receipt.json',destination/'package-receipt.json')
    notes=(release/'RELEASE-NOTES.md').read_text(encoding='utf-8').replace('../../../../releases/','./')
    (destination/'RELEASE-NOTES.md').write_text(notes,encoding='utf-8')
    qualification=(release/'qualification.md').read_text(encoding='utf-8').replace(
        '../../plans/2026-10-14-workspace-qualification/',PACKET.as_posix()+'/').replace(
        '../12.6.2/',(ROOT/'docs/anim_assist/releases/12.6.2').as_posix()+'/')
    (destination/'qualification.md').write_text(qualification,encoding='utf-8')
    state='''# Workspace qualification state

2026-10-14. Delegated agent usability workflow passed on exact local 12.7.0.
Fresh-start/default and saved generated workspace checked; no owner .blend was
provided. Personal aesthetic approval is not a blocking gate for this delegated
check. Independent user study, personal/production rigs and unsupported cells
remain unverified; see REVIEW.md and release qualification.

Local endpoint: addon-only 12.7.0, 53 workflow steps, 80 immediate effects,
18 original modal cases, 21 native buttons, 32 slider cases, 56 recovery checks,
23 pure tests. Package SHA256 47d25fe0568e7685ca46c58fe7cc5310bd34411f76debaf1839d312d61828027.
No push, merge or publication. Next action only if requested: publication review
and exact Confirm merge update after a before/after table.
'''
    (PACKET/'STATE.md').write_text(state,encoding='utf-8')
    planning=ROOT/'.planning'
    mirror=planning/'phases/03-workspace-qualification';mirror.mkdir(parents=True,exist_ok=True)
    for source in PACKET.glob('*.md'):shutil.copyfile(source,mirror/source.name)
    for name in ('STATE.md','ROADMAP.md','PROJECT.md'):
        path=planning/name;old=path.read_text(encoding='utf-8')
        if 'Delegated agent usability workflow passed on exact local 12.7.0' not in old:
            path.write_text(state+'\n---\n\n## Previous checkpoint (retained)\n'+old,encoding='utf-8')
    config=read(planning/'config.json');config['plan_source']=str(PACKET.relative_to(ROOT)).replace('\\','/')
    config['scope']='Delegated workspace usability check and local Anim Assist 12.7.0 overhaul release'
    (planning/'config.json').write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(qualified=True,local_zip=str(target),sha256=digest),indent=2))

if __name__=='__main__':main()
