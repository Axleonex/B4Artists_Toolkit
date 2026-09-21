"""Build experimental 0.21.0 from the same-hash angular-momentum regression."""
from pathlib import Path
import ast,hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[2];RESULTS=ROOT/'training/b4artists_ml/results';DOCS=ROOT/'docs/b4artists_ml';OUTPUT=ROOT/'releases/b4artists_ml_v0.21.0.zip'
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def runtime_hashes():return {p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')}
def main():
    assert not OUTPUT.exists()
    regression_path=RESULTS/'angular-momentum-full-v2-regression.json';regression=read(regression_path)
    assert len(regression)==46 and len({row['suite'] for row in regression})==46 and sum(row['tests'] for row in regression)==439
    assert all(row['assertions_passed'] and not row.get('errors') and not row.get('failures') and not row.get('skipped') for row in regression)
    tested=regression[0]['runtime_sha256'];assert all(row['runtime_sha256']==tested for row in regression)
    packaged=runtime_hashes();assert packaged==tested
    metrics_path=RESULTS/'angular-momentum-full-v2-angular-host.json';metrics=read(metrics_path);assert metrics['passed'] and len(metrics['rows'])==3
    principal=[row['report']['intervals'][0]['angular_momentum'] for row in metrics['rows'][:2]]
    assert all(row['improvement']>.85 and row['endpoint_rotation_error']<2e-5 for row in principal)
    combined=metrics['rows'][2]['report'];assert all(row['match_acceleration'] and row['normalized_acceleration_jump']<=.1 for row in combined['transitions'])
    current=(ROOT/'b4artists_ml/__init__.py').read_text(encoding='utf-8');tree=ast.parse(current);info=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='bl_info' for t in n.targets));index=next(i for i,k in enumerate(info.keys) if k.value=='version');assert ast.literal_eval(info.values[index])==(0,21,0)
    paths={p.relative_to(ROOT).as_posix():p for p in (ROOT/'b4artists_ml').rglob('*') if p.is_file() and (p.suffix in ('.py','.json','.md','.npz') or p.name=='LICENSE')}
    for path in paths.values():
        if path.suffix=='.py':ast.parse(path.read_bytes())
    with zipfile.ZipFile(OUTPUT,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name,path in sorted(paths.items()):
            item=zipfile.ZipInfo(name,date_time=(2026,9,10,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED;item.external_attr=0o644<<16;archive.writestr(item,path.read_bytes(),compresslevel=9)
    with zipfile.ZipFile(OUTPUT) as archive:assert set(archive.namelist())==set(paths) and all(archive.read(name)==path.read_bytes() for name,path in paths.items())
    report=dict(version='0.21.0',files=len(paths),bytes=OUTPUT.stat().st_size,sha256=sha(OUTPUT),package_matches_source=True,experimental=True,full_goal_complete=False,ready_for_local_testing=False,runtime_sha256=packaged,tested_runtime_sha256=tested,regression=dict(unique_cases=439,suites=46,evidence=regression_path.relative_to(ROOT).as_posix()),angular_refinement=dict(profiles=[row['profile'] for row in metrics['rows']],metrics=[row['report']['intervals'][0]['angular_momentum'] for row in metrics['rows']],evidence=metrics_path.relative_to(ROOT).as_posix()),exact_package_checks='pending',exact_package_ui='pending',host_shutdown_qualified=False,independent_human_usability='unknown',qualification_note='Normalized segment-center point-mass angular refinement is source-qualified. Full segment inertia, forces, collision, secondary motion, learned temporal motion, human review, quadrupeds and Cascadeur parity remain unqualified.')
    (DOCS/'package-test-v0.21.0.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:report[k] for k in ('version','files','bytes','sha256')},indent=2))
if __name__=='__main__':main()
