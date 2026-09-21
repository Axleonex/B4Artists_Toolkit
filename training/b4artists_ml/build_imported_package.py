"""Qualify the imported-adapter regression inventory and build a local candidate."""
from pathlib import Path
import json,hashlib,zipfile,ast
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=ROOT/'releases/b4artists_ml_v0.16.0.zip'
    if out.exists():raise RuntimeError('Package evidence already exists')
    baseline=json.loads((ROOT/'training/b4artists_ml/results/read-scope-regression-composed-v1.json').read_text())
    sources=['imported-protection-v1-regression.json','imported-foundation-v1-regression.json','imported-remaining-v1-regression.json','imported-adapter-v6-regression.json','imported-final-v2-regression.json']
    rows=[];failures=[]
    for name in sources:
        for row in json.loads((ROOT/'training/b4artists_ml/results'/name).read_text()):
            if row['suite']=='test_b4artists_ml_foundation':
                assert row['tests']==0 and not row['assertions_passed'];failures.append(row);continue
            assert row['assertions_passed'] and row['tests']>0 and not row.get('skipped')
            rows.append(row)
    rows=list({r['suite']:r for r in rows}.values())
    expected={r['suite']:r['tests'] for r in baseline['rows']}
    expected['test_b4artists_ml_imported_humanoids']=12
    assert len(rows)==len(expected) and {r['suite']:r['tests'] for r in rows}==expected
    current={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')}
    structure_path=ROOT/'training/b4artists_ml/results/imported-capture-structure-v1.json'
    structure=json.loads(structure_path.read_text());assert structure['unaffected_ast_equal'] and current['b4artists_ml/workflow.py']==structure['after_sha256']
    def covered(hashes):
        changed={n for n,h in hashes.items() if current[n]!=h}
        return not changed or changed=={'b4artists_ml/workflow.py'} and hashes['b4artists_ml/workflow.py']==structure['before_sha256']
    assert all(covered(r['runtime_sha256']) for r in rows)
    for row in rows:row['coverage_origin']='final_capture_correction' if row['runtime_sha256']==current else 'same_turn_prior_runtime_unaffected_profile_branch'
    fresh=sum(r['tests'] for r in rows if r['runtime_sha256']==current)
    ui=[]
    for tag in ('imported-unity-v1','imported-mocap_humanoid-v1','imported-unreal_mannequin-v1'):
        path=ROOT/f'training/b4artists_ml/results/live-pose-ui-{tag}.json';record=json.loads(path.read_text())
        assert record['passed'] and covered(record['runtime_sha256'])
        ui.append(dict(file=path.relative_to(ROOT).as_posix(),sha256=sha(path)))
    report=dict(passed=True,unique_cases=sum(r['tests'] for r in rows),suites=len(rows),fresh_cases=fresh,retained_cases=sum(r['tests'] for r in rows)-fresh,structure_evidence_sha256=sha(structure_path),runtime_sha256=current,rows=rows,inputs=[dict(file='training/b4artists_ml/results/'+n,sha256=sha(ROOT/'training/b4artists_ml/results'/n)) for n in sources],harness_selector_failures=failures,scope='All existing 245 cases executed this turn; final imported-only capture correction followed by 12 imported and 31 foundation cases. Other 214 cases retain their actual preceding-runtime hashes with structural proof that their non-imported capture branch is unchanged. Wrong foundation selector failed with zero cases and is retained; actual foundation module subsequently passed 31 cases. Host shutdown remains unqualified.')
    regpath=ROOT/'training/b4artists_ml/results/imported-regression-v1.json';assert not regpath.exists();regpath.write_text(json.dumps(report,indent=2)+'\n')
    init=ROOT/'b4artists_ml/__init__.py';old=init.read_bytes();new=old.replace(b'"version": (0, 15, 1)',b'"version": (0, 16, 0)');assert new!=old
    assert new.replace(b'"version": (0, 16, 0)',b'"version": (0, 15, 1)')==old;ast.parse(new)
    paths={p.relative_to(ROOT).as_posix():p for p in (ROOT/'b4artists_ml').rglob('*') if p.is_file() and (p.suffix in ('.py','.json','.md','.npz') or p.name=='LICENSE')}
    with zipfile.ZipFile(ROOT/'releases/b4artists_ml_v0.15.1.zip') as z:
        assert set(paths)==set(z.namelist())
        assert {n for n,p in paths.items() if z.read(n)!=p.read_bytes()}=={'b4artists_ml/body_solver.py','b4artists_ml/posing.py','b4artists_ml/workflow.py'}
    init.write_bytes(new)
    with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,p in sorted(paths.items()):
            info=zipfile.ZipInfo(name,date_time=(2026,9,8,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,p.read_bytes(),compresslevel=9)
    with zipfile.ZipFile(out) as z:assert all(z.read(n)==p.read_bytes() for n,p in paths.items())
    package=dict(version='0.16.0',files=len(paths),bytes=out.stat().st_size,sha256=sha(out),package_matches_source=True,experimental=True,full_goal_complete=False,fresh_regression_cases=report['fresh_cases'],retained_regression_cases=report['retained_cases'],unique_regression_cases=report['unique_cases'],regression_sha256=sha(regpath),source_ui=ui,version_only_change_after_checks=dict(before_sha256=hashlib.sha256(old).hexdigest(),after_sha256=sha(init),literal_only_verified=True),offline_qualification='pending',packaged_ui_qualification='pending',host_shutdown_qualified=False)
    (ROOT/'docs/b4artists_ml/package-test-v0.16.0.json').write_text(json.dumps(package,indent=2)+'\n');print(json.dumps(package),flush=True)
if __name__=='__main__':main()
