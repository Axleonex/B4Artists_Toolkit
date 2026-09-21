"""Finalize documentation only after exact-package offline and actual-window checks."""
from pathlib import Path
import json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    path=ROOT/'docs/b4artists_ml/package-test-v0.16.1.json';meta=json.loads(path.read_text())
    if meta['offline_qualification']!='pending':raise RuntimeError('Qualification already finalized')
    archive=ROOT/'releases/b4artists_ml_v0.16.1.zip';assert sha(archive)==meta['sha256']
    with zipfile.ZipFile(archive) as z:assert all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist())
    out=ROOT/'training/b4artists_ml/results';offline_path=out/'offline-projection-v0.16.1.json';offline=json.loads(offline_path.read_text())
    assert offline['passed'] and offline['complete'] and offline['package_sha256']==meta['sha256']
    assert sum(g['tests'] for g in offline['groups'])==110
    current={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')}
    ui=[]
    for tag in ('projection-package-rigify-v1','projection-package-unity-v1'):
        f=out/('live-pose-ui-'+tag+'.json');record=json.loads(f.read_text())
        assert record['passed'] and record['runtime_sha256']==current
        ui.append(dict(file=f.relative_to(ROOT).as_posix(),sha256=sha(f),fixture=record.get('fixture'),events=record['events']))
    meta.update(offline_qualification='passed',offline_cases=110,offline_groups=len(offline['groups']),offline_evidence_sha256=sha(offline_path),packaged_ui_qualification='passed',packaged_ui=ui,qualification_note='Automated functional qualification; UI checks overlapped headless offline tests and are not comparative performance benchmarks. Existing host shutdown failure remains unqualified.')
    path.write_text(json.dumps(meta,indent=2)+'\n')
    f=ROOT/'docs/b4artists_ml/PROJECT.md';s=f.read_text().replace('Status: experimental 0.16.0;','Status: experimental 0.16.1;',1)
    s+='\n\n## Temporal projection integration in 0.16.1\n\nTEMPORAL-PROJECTION-v1.md records the shared-observation to real-rig and editable-action path, with all 17 orientations, exact priorities, source preservation and failure recovery. The runtime interfaces are packaged; temporal orchestration and its procedural provider remain research code. No learned temporal model or new interpolation panel control is promoted. Current-source 303-case regression, 110 offline cases and actual-window Rigify/imported recovery checks pass; host shutdown and full-goal quality remain unqualified.\n'
    f.write_text(s)
    f=ROOT/'docs/b4artists_ml/USER_GUIDE.md';s=f.read_text().replace('Machine Learning 0.16.0 -','Machine Learning 0.16.1 -',1).replace('releases/b4artists_ml_v0.16.0.zip','releases/b4artists_ml_v0.16.1.zip',1)
    s+='\n\n0.16.1 preserves the existing animator workflow. Interpolation in the panel is still procedural; a qualified learned-motion model is not yet enabled. Source recovery and existing posing remain covered by the current package checks in package-test-v0.16.1.json.\n';f.write_text(s)
    f=ROOT/'docs/b4artists_ml/REQUIREMENTS.md';s=f.read_text().replace('Current implementation: NATIVE-SAMPLING-0.14.2.md and package-test-v0.14.2.json','Current implementation: TEMPORAL-PROJECTION-v1.md and package-test-v0.16.1.json',1);f.write_text(s)
    print(json.dumps(dict(version=meta['version'],sha256=meta['sha256'],native_cases=303,offline_cases=110,packaged_ui='passed',host_shutdown=False,full_goal_complete=False)),flush=True)
if __name__=='__main__':main()
