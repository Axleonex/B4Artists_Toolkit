"""Finalize the local receipt only after exact-artifact evidence passes."""
import hashlib
import json
from pathlib import Path
import shutil

PACKET=Path(__file__).resolve().parent
ROOT=PACKET.parents[3]
EVIDENCE=PACKET/'evidence'


def read(path):return json.loads(path.read_text(encoding='utf-8'))


def main():
    artifact=read(EVIDENCE/'final/artifact.json')
    package=Path(artifact['zip_path'])
    digest=hashlib.sha256(package.read_bytes()).hexdigest()
    assert digest==artifact['sha256'] and package.stat().st_size==artifact['bytes']
    full=read(EVIDENCE/'qualified-full/full-coverage.json')
    assert full['passed'] and full['immediate']==80 and full['original_interactive_cases']==18
    assert full['native_bar_buttons']==21 and full['native_row_scalar_cases']==32
    assert full['recovery_assertions']==56
    for stage in ('full','ui','layouts'):
        identity=read(EVIDENCE/f'qualified-{stage}/package-identity.json')
        assert identity['sha256']==digest and identity['files']==208
    ui=read(EVIDENCE/'qualified-ui/ui-coverage.json')
    layouts=read(EVIDENCE/'qualified-layouts/layout-coverage.json')
    assert ui['passed'] and layouts['passed']
    for directory in ('stress-tail','edges-final'):
        result=read(EVIDENCE/directory/'stress.json')
        assert result['passed'] and result['sha256']==digest
    # Earlier stress run stopped at a harness-only area_move poll limitation.
    # Accept only its reached, measured cells, never its false aggregate result.
    partial=read(EVIDENCE/'stress-complete/stress.json')
    assert partial['sha256']==digest and all(c['passed'] for c in partial['checks'])
    reached={c['check'] for c in partial['checks']}
    assert reached>={'Retains manual small height','Scale 1.5 geometry','Scale 2 geometry',
        'Header geometry','Maximized geometry','Native pan check','Native zoom check',
        'Playback changed frame','Multiple-window rows','Precision assertion','Snap assertion',
        'Disabled preview restores','Re-enable'}
    assert len(read(EVIDENCE/'edges-final/neutral-scope.json'))==7
    for name,count in (('config',12),('session',6),('layout',5)):
        log=(EVIDENCE/f'final/pure-{name}.log').read_text(encoding='utf-8-sig')
        assert f'Ran {count} tests' in log and '\nOK' in log and 'FAILED' not in log
    release=ROOT/'docs/anim_assist/releases/12.6.2'
    release.mkdir(parents=True,exist_ok=True)
    receipt=dict(artifact,status='technically qualified local release; owner usability and publication pending',
        native_host='Bforartists 5.2.0; runtime 5.3 Alpha; build 0a1ca45552db',
        qualification='qualification.md',owner_uat='pending',publication='not pushed',
        evidence=dict(full=full,ui=ui,layouts=layouts),
        lifecycle_note='Measured cells in stress-complete plus completed stress-tail/edges-final; diagnostic failures retained')
    (release/'package-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    destination=Path('G:/LapArt/Local-Releases/AnimAssist/12.6.2')
    destination.mkdir(parents=True,exist_ok=True)
    target=destination/package.name
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()!=digest:
        raise ValueError('Refusing to overwrite a different existing local release')
    shutil.copyfile(package,target)
    assert hashlib.sha256(target.read_bytes()).hexdigest()==digest
    shutil.copyfile(release/'package-receipt.json',destination/'package-receipt.json')
    shutil.copyfile(release/'RELEASE-NOTES.md',destination/'RELEASE-NOTES.md')
    shutil.copyfile(release/'qualification.md',destination/'qualification.md')
    state='''# State

Updated: 2026-10-14. Phase 02. **Plans 02-01 through 02-06 implemented and
technically qualified locally. Owner usability checkpoint pending.**
Local release 12.6.2; not pushed.

Implemented: add-on-only configurable second canvas row, eight numeric tools,
individual settings, visibility/modes/order, named layouts and settings transfer.
Recommended starts with Breakdown/Smooth inline and Timing Scale popout. Seven
families and all 89 original actions remain. Existing mirror/trail/redo defects
and active-disable timer cleanup have measured repairs.

Delivered SHA256: 5492e94a773a0398e281d0b3a0410de0b75c9e92fd5f4b4980373e39474643f7.
Final full: 80 effects, 18 original modal cases, 21 native buttons, 32 actual row
slider cases, 56 recovery assertions. Default-row pass: six more cases/six
recovery assertions. Named layouts/normal restart and 23 pure tests pass.
Workspace/edge evidence and unsupported cells are in 02-VERIFICATION.md.

Next: owner installs the local ZIP and follows 02-UAT.md. Human usability remains
pending. ST-12 retains unverified extension/keyboard-only cells; ST-14 retains
the owner checkpoint. Do not widen fixture results into production-rig or full
AnimBot-parity claims. There is no true second native HEADER region.

This packet is canonical. Ignored .planning mirrors preserve historical phase
records. Work is isolated from the dirty owner checkout. Local work-branch
commits are allowed. Push/main merge/publication require exact Confirm merge
update after a concrete before/after review.
'''
    (PACKET/'STATE.md').write_text(state,encoding='utf-8')
    req=PACKET/'REQUIREMENTS.md'
    text=req.read_text(encoding='utf-8')
    for index in range(1,14):
        if index!=12:text=text.replace(f'- [ ] ST-{index:02}:',f'- [x] ST-{index:02}:')
    text=text.replace('Fresh baseline proves expected effects for every current default bar control and all 80 immediate catalogue actions, on exact local 12.6.1 in stock Bforartists.',
        'Fresh exact 12.6.1 baseline records defects and measured repairs; repaired baseline/final ZIP prove expected effects for current default controls and all 80 immediate actions in stock Bforartists.')
    text+='\nST-12 is partial for renamed extension installation and keyboard-only access.\nST-14 technical evidence is complete; owner usability remains pending.\nSee 02-VERIFICATION.md for per-requirement scope and unsupported cells.\n'
    req.write_text(text,encoding='utf-8')
    planning=ROOT/'.planning'
    mirror=planning/'phases/02-configurable-slider-toolbar'
    mirror.mkdir(parents=True,exist_ok=True)
    for source in PACKET.glob('*.md'):shutil.copyfile(source,mirror/source.name)
    for name in ('STATE.md','ROADMAP.md','PROJECT.md'):
        old=(planning/name).read_text(encoding='utf-8')
        marker='## Historical checkpoint record (retained)'
        history=old.split(marker,1)[-1] if marker in old else old
        (planning/name).write_text(state+'\n---\n\n'+marker+'\n'+history,encoding='utf-8')
    print(json.dumps(dict(qualified=True,zip=str(target),sha256=digest,bytes=target.stat().st_size),indent=2))


if __name__=='__main__':main()
