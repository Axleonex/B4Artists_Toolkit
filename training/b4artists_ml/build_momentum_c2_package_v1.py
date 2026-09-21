"""Build experimental 0.20.3 from the source-qualified COM acceleration refinement."""
from pathlib import Path
import ast
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parents[2]
RESULTS=ROOT/'training/b4artists_ml/results';DOCS=ROOT/'docs/b4artists_ml'
OUTPUT=ROOT/'releases/b4artists_ml_v0.20.3.zip'
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def runtime_hashes():return {p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')}

def main():
    assert not OUTPUT.exists()
    regression_path=RESULTS/'momentum-c2-full-v2-regression.json';regression=read(regression_path)
    assert len(regression)==45 and len({row['suite'] for row in regression})==45 and sum(row['tests'] for row in regression)==432
    assert all(row['assertions_passed'] and not row.get('errors') and not row.get('failures') and not row.get('skipped') for row in regression)
    tested=regression[0]['runtime_sha256'];assert all(row['runtime_sha256']==tested for row in regression)
    metrics_path=RESULTS/'momentum-c2-v12-acceleration-host.json';metrics=read(metrics_path);assert metrics['passed']
    assert all(row['match_acceleration'] and row['normalized_jump']<=.02 and row['normalized_acceleration_jump']<=.1 for row in metrics['report']['transitions'])
    packaged=runtime_hashes();assert set(packaged)==set(tested)
    for name in packaged:
        if name!='b4artists_ml/__init__.py':assert packaged[name]==tested[name],name
    current=(ROOT/'b4artists_ml/__init__.py').read_text(encoding='utf-8');prior=current.replace('"version": (0, 20, 3)','"version": (0, 20, 2)')
    assert prior!=current and hashlib.sha256(prior.encode()).hexdigest()==tested['b4artists_ml/__init__.py']
    tree=ast.parse(current);info=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='bl_info' for t in n.targets));index=next(i for i,k in enumerate(info.keys) if k.value=='version');assert ast.literal_eval(info.values[index])==(0,20,3)
    paths={p.relative_to(ROOT).as_posix():p for p in (ROOT/'b4artists_ml').rglob('*') if p.is_file() and (p.suffix in ('.py','.json','.md','.npz') or p.name=='LICENSE')}
    for path in paths.values():
        if path.suffix=='.py':ast.parse(path.read_bytes())
    with zipfile.ZipFile(OUTPUT,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name,path in sorted(paths.items()):
            item=zipfile.ZipInfo(name,date_time=(2026,9,10,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED;item.external_attr=0o644<<16;archive.writestr(item,path.read_bytes(),compresslevel=9)
    with zipfile.ZipFile(OUTPUT) as archive:
        assert set(archive.namelist())==set(paths) and all(archive.read(name)==path.read_bytes() for name,path in paths.items())
    report=dict(version='0.20.3',files=len(paths),bytes=OUTPUT.stat().st_size,sha256=sha(OUTPUT),package_matches_source=True,experimental=True,full_goal_complete=False,ready_for_local_testing=False,runtime_sha256=packaged,tested_runtime_sha256=tested,post_test_version_only_revision=True,regression=dict(unique_cases=432,suites=45,evidence=regression_path.relative_to(ROOT).as_posix()),acceleration_refinement=dict(profile=metrics['profile'],transitions=metrics['report']['transitions'],evidence=metrics_path.relative_to(ROOT).as_posix()),exact_package_momentum='pending',exact_package_ui='pending',host_shutdown_qualified=False,independent_human_usability='unknown',qualification_note='Optional source-safe COM acceleration matching advances takeoff/landing refinement. Angular momentum, forces, collision, secondary motion, learned temporal motion, human review, quadrupeds and Cascadeur parity remain unqualified.')
    (DOCS/'package-test-v0.20.3.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('version','files','bytes','sha256')},indent=2))
if __name__=='__main__':main()
