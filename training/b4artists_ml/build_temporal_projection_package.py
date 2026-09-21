"""Build the local patch only from current-source native regression evidence."""
from pathlib import Path
import json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=ROOT/'releases/b4artists_ml_v0.16.1.zip'
    if out.exists():raise RuntimeError('Package evidence already exists')
    results=ROOT/'training/b4artists_ml/results'
    names=['temporal-projection-protection-v1-regression.json','temporal-projection-final-v2-regression.json']
    rows=[row for name in names for row in json.loads((results/name).read_text())]
    expected={v['suite']:v['tests'] for v in json.loads((results/'imported-regression-v1.json').read_text())['rows']}
    expected.update(test_b4artists_ml_rig_observations=13,test_b4artists_ml_anchor_observations=9,test_b4artists_ml_semantic_motion_data=9,test_b4artists_ml_temporal_projection=15)
    assert len(rows)==len(expected) and {v['suite']:v['tests'] for v in rows}==expected
    current={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')}
    for row in rows:
        assert row['assertions_passed'] and not row.get('skipped') and row['runtime_sha256']==current
    paths={p.relative_to(ROOT).as_posix():p for p in (ROOT/'b4artists_ml').rglob('*') if p.is_file() and (p.suffix in ('.py','.json','.md','.npz') or p.name=='LICENSE')}
    with zipfile.ZipFile(ROOT/'releases/b4artists_ml_v0.16.0.zip') as z:
        assert set(paths)==set(z.namelist())
        assert {n for n,p in paths.items() if z.read(n)!=p.read_bytes()}=={'b4artists_ml/__init__.py','b4artists_ml/body_solver.py','b4artists_ml/workflow.py'}
    with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,p in sorted(paths.items()):
            info=zipfile.ZipInfo(n,date_time=(2026,9,8,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
            z.writestr(info,p.read_bytes(),compresslevel=9)
    with zipfile.ZipFile(out) as z:assert all(z.read(n)==p.read_bytes() for n,p in paths.items())
    reg=dict(passed=True,unique_cases=sum(v['tests'] for v in rows),suites=len(rows),runtime_sha256=current,rows=rows,input_reports={n:sha(results/n) for n in names},host_shutdown_passed=False)
    regpath=results/'temporal-projection-regression-v1.json';regpath.write_text(json.dumps(reg,indent=2)+'\n')
    meta=dict(version='0.16.1',files=len(paths),bytes=out.stat().st_size,sha256=sha(out),package_matches_source=True,experimental=True,full_goal_complete=False,unique_regression_cases=reg['unique_cases'],regression_sha256=sha(regpath),offline_qualification='pending',packaged_ui_qualification='pending',host_shutdown_qualified=False,scope='Runtime explicit proposal and validated sample interfaces; temporal provider orchestration remains research code, no new model or user-facing learned interpolation control.')
    (ROOT/'docs/b4artists_ml/package-test-v0.16.1.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta),flush=True)
if __name__=='__main__':main()
