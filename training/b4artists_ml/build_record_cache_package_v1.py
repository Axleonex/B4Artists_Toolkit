"""Build a local experimental package only after current-source validation."""
from pathlib import Path
import json, hashlib, zipfile, ast
from build_finalization_package_v1 import definitions
ROOT=Path(__file__).resolve().parents[2]
def read(p): return json.loads((ROOT/p).read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    output=ROOT/'releases/b4artists_ml_v0.17.5.zip'
    assert not output.exists()
    plan=read('training/b4artists_ml/record_cache_production_regression_plan_v1.json')
    rows=read('training/b4artists_ml/results/record-cache-production-full-v1-regression.json')
    current={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')}
    assert len(rows)==len(plan['suites'])==33
    assert {r['suite'] for r in rows}==set(plan['suites'])
    assert sum(r['tests'] for r in rows)==plan['expected_cases']==345
    assert all(r['assertions_passed'] and not r['skipped'] and r['runtime_sha256']==current for r in rows)
    bench=read('training/b4artists_ml/results/record-cache-benchmark-production-v1.json')
    assert bench['complete'] and bench['passed']
    assert all(r['runtime_sha256']==current for r in bench['rows'] if r['variant']=='current')
    paths={p.relative_to(ROOT).as_posix():p for p in (ROOT/'b4artists_ml').rglob('*') if p.is_file() and (p.suffix in ('.py','.json','.md','.npz') or p.name=='LICENSE')}
    archive=ROOT/'releases/b4artists_ml_v0.17.4.zip'
    assert sha(archive)=='3a07d44ae2ef4f703f8366befb8e1057b317264e3f909dc689f50279ba59ad66'
    with zipfile.ZipFile(archive) as z:
        assert set(paths)-set(z.namelist())=={'b4artists_ml/record_cache.py'}
        assert not set(z.namelist())-set(paths)
        assert {n for n in z.namelist() if z.read(n)!=paths[n].read_bytes()}=={'b4artists_ml/body_preview.py'}
        before=definitions(z.read('b4artists_ml/body_preview.py'))
        after=definitions(paths['b4artists_ml/body_preview.py'].read_bytes())
        assert set(before)==set(after)
        assert {n for n in before if before[n]!=after[n]}=={'_decode','finish','reset_runtime','before_save'}
        # Check imports, globals and class structure as well as unchanged methods.
        a=ast.parse(z.read('b4artists_ml/body_preview.py')); b=ast.parse(paths['b4artists_ml/body_preview.py'].read_bytes())
        def remainder(tree, newer=False):
            kept=[]
            for node in tree.body:
                if isinstance(node,ast.FunctionDef) and node.name in ('_decode','finish','reset_runtime','before_save'): continue
                if newer and isinstance(node,ast.ImportFrom) and node.module=='record_cache': continue
                if newer and isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='_RECORDS' for t in node.targets): continue
                if isinstance(node,ast.ClassDef) and node.name=='_ReadScope': node.body=node.body[1:]
                kept.append(node)
            tree.body=kept; return ast.dump(tree,include_attributes=False)
        assert remainder(a)==remainder(b,True)
    init=ROOT/'b4artists_ml/__init__.py';old=init.read_bytes()
    new=old.replace(b'"version": (0, 17, 4)',b'"version": (0, 17, 5)')
    assert new!=old and new.replace(b'"version": (0, 17, 5)',b'"version": (0, 17, 4)')==old
    for p in paths.values():
        if p.suffix=='.py': ast.parse(p.read_bytes())
    init.write_bytes(new)
    with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,p in sorted(paths.items()):
            info=zipfile.ZipInfo(n,date_time=(2026,9,8,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
            z.writestr(info,p.read_bytes(),compresslevel=9)
    with zipfile.ZipFile(output) as z: assert all(z.read(n)==p.read_bytes() for n,p in paths.items())
    report=dict(version='0.17.5',files=len(paths),bytes=output.stat().st_size,sha256=sha(output),package_matches_source=True,experimental=True,full_goal_complete=False,ready_for_local_testing=False,
        runtime_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')},
        regression=dict(unique_cases=345,all_refreshed=True,suites=len(rows),rows=rows),
        benchmark='training/b4artists_ml/results/record-cache-benchmark-production-v1.json',benchmark_sha256=sha(ROOT/'training/b4artists_ml/results/record-cache-benchmark-production-v1.json'),
        version_only_change_after_checks=dict(before_sha256=hashlib.sha256(old).hexdigest(),after_sha256=sha(init),literal_only_verified=True),
        source_audit=dict(changed_definitions=['_decode','finish','reset_runtime','before_save'],all_other_functions_unchanged=True,all_other_package_files_identical_before_version_bump=True,new_module='record_cache.py'),
        packaged_host_smoke='pending',packaged_ui_qualification='unverified',host_shutdown_qualified=False,independent_human_usability='unknown',
        qualification_note='Bounded record copying with unchanged solver and validation logic. Scoped headless speed gates pass; no full responsiveness, temporal quality or Cascadeur parity claim.')
    (ROOT/'docs/b4artists_ml/package-test-v0.17.5.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('version','files','bytes','sha256')}),flush=True)
if __name__=='__main__':main()
