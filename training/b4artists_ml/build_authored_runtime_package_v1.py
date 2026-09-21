"""Build0.18.0 only after complete current-source regression and port audit."""
from pathlib import Path
import json,hashlib,zipfile,ast
ROOT=Path(__file__).resolve().parents[2]
def read(n):return json.loads((ROOT/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    output=ROOT/'releases/b4artists_ml_v0.18.0.zip';assert not output.exists()
    plan=read('training/b4artists_ml/authored_runtime_regression_plan_v1.json');rows=read('training/b4artists_ml/results/authored-runtime-full-v1-regression.json');audit=read('training/b4artists_ml/results/authored-runtime-source-audit-v1.json')
    runtime={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')}
    assert runtime==plan['runtime_sha256']==audit['runtime_sha256'] and audit['passed']
    assert len(rows)==len(plan['suites'])==36 and {r['suite'] for r in rows}==set(plan['suites']) and sum(r['tests'] for r in rows)==plan['expected_cases']==369
    for r in rows:assert r['assertions_passed'] and not r['errors'] and not r['failures'] and not r['skipped'] and r['runtime_sha256']==runtime and sha(ROOT/r['log'])==r['sha256']
    prior_init=sha(ROOT/'training/b4artists_ml/results/authored-integration-baseline-v1/__init__.py')
    for profile in ('boneforge','rigify_basic','rigify_default'):
        d=read('training/b4artists_ml/results/humanoid-workflow-review-v6-runtime/'+profile+'/report.json');expected=dict(runtime);expected['b4artists_ml/__init__.py']=prior_init
        assert d['full_humanoid_workflow_passed'] and d['research_reference_max_component_error']==0 and d['runtime_sha256']==expected and sha(ROOT/d['blend_path'])==d['blend_sha256']
    paths={p.relative_to(ROOT).as_posix():p for p in (ROOT/'b4artists_ml').rglob('*') if p.is_file() and (p.suffix in ('.py','.json','.md','.npz') or p.name=='LICENSE')};assert len(paths)==40
    for p in paths.values():
        if p.suffix=='.py':ast.parse(p.read_bytes())
    with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,p in sorted(paths.items()):
            info=zipfile.ZipInfo(name,date_time=(2026,9,9,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,p.read_bytes(),compresslevel=9)
    with zipfile.ZipFile(output) as z:assert set(z.namelist())==set(paths) and all(z.read(n)==p.read_bytes() for n,p in paths.items())
    report=dict(version='0.18.0',files=len(paths),bytes=output.stat().st_size,sha256=sha(output),package_matches_source=True,experimental=True,full_goal_complete=False,ready_for_local_testing=False,runtime_sha256=runtime,regression=dict(unique_cases=369,suites=36,all_refreshed=True,evidence='training/b4artists_ml/results/authored-runtime-full-v1-regression.json'),source_audit='training/b4artists_ml/results/authored-runtime-source-audit-v1.json',packaged_host_smoke='pending',packaged_ui_qualification='unverified',host_shutdown_qualified=False,independent_human_usability='unknown',qualification_note='Authored-only procedural whole-body motion integrated with cancellable preview. Exact research parity on3controlledrigs. SLERP and baked motion are not rotation-velocity-continuous; responsiveness and learned temporal quality remain unqualified.')
    (ROOT/'docs/b4artists_ml/package-test-v0.18.0.json').write_text(json.dumps(report,indent=2)+'\n');print({k:report[k] for k in ('version','files','bytes','sha256')})
if __name__=='__main__':main()
