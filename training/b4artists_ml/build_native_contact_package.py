"""Patch package: refreshed affected suites plus explicitly audited evidence reuse."""
from pathlib import Path
import json,hashlib,zipfile,ast
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_text())
def normalized(raw):return raw.decode('utf-8').replace('\r\n','\n')
def stripped_tree(source,ignored):
    tree=ast.parse(source);tree.body=[n for n in tree.body if not isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) or n.name not in ignored];return ast.dump(tree,include_attributes=False)
def main():
    out=ROOT/'releases/b4artists_ml_v0.17.1.zip';assert not out.exists()
    old=read('training/b4artists_ml/results/momentum-regression-v1.json')
    reports=['native-contact-final-v1-regression.json']
    fresh=[r for name in reports for r in read('training/b4artists_ml/results/'+name)]
    expected={'test_b4artists_ml_native_contacts':6,'test_b4artists_ml_contacts':14,'test_b4artists_ml_flight':17,'test_b4artists_ml_momentum':8,'test_b4artists_ml_native_flight':14,'test_b4artists_ml_imported_humanoids':12}
    assert {r['suite']:r['tests'] for r in fresh}==expected and len(fresh)==6
    current={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')}
    assert all(r['assertions_passed'] and not r['skipped'] and r['runtime_sha256']==current for r in fresh)
    paths={p.relative_to(ROOT).as_posix():p for p in (ROOT/'b4artists_ml').rglob('*') if p.is_file() and (p.suffix in ('.py','.json','.md','.npz') or p.name=='LICENSE')}
    with zipfile.ZipFile(ROOT/'releases/b4artists_ml_v0.17.0.zip') as archive:
        assert set(paths)==set(archive.namelist());changed={n for n,p in paths.items() if archive.read(n)!=p.read_bytes()}
        assert changed=={'b4artists_ml/__init__.py','b4artists_ml/contacts.py','b4artists_ml/native_flight.py'}
        for n,h in old['runtime_sha256'].items():assert hashlib.sha256(archive.read(n)).hexdigest()==h
        assert all(r['assertions_passed'] and r['runtime_sha256']==old['runtime_sha256'] for r in old['rows'])
        before=normalized(archive.read('b4artists_ml/__init__.py'));after=(ROOT/'b4artists_ml/__init__.py').read_text();assert before.replace('"version": (0, 17, 0)','"version": (0, 17, 1)')==after
        before=normalized(archive.read('b4artists_ml/native_flight.py'));after=(ROOT/'b4artists_ml/native_flight.py').read_text()
        added="        instance['b4ml_flight']=json.dumps(dict(flights=raw['flights']),allow_nan=False)\n"
        assert after.count(added)==1 and after.replace(added,'')==before
        before=normalized(archive.read('b4artists_ml/contacts.py'));after=(ROOT/'b4artists_ml/contacts.py').read_text()
        assert stripped_tree(before,{'correction_steps','_solve_limb'})==stripped_tree(after,{'correction_steps','_solve_limb','_flight_intervals'})
    retained=[dict(r,evidence_reused=True,reuse_reason='Unchanged workflow definitions and runtime dependencies; modified flight/contact solve paths refreshed separately.') for r in old['rows'] if r['suite'] not in expected]
    assert sum(r['tests'] for r in retained)==246
    audit=dict(changed_files=sorted(changed),prior_runtime_sha256=old['runtime_sha256'],current_runtime_sha256=current,unchanged_other_contacts_definitions=True,modified_contacts_functions=['_flight_intervals','correction_steps','_solve_limb'],native_change='Only generated flight request snapshot added after native layer creation',version_only_init=True,refreshed_suites=expected,reused_cases=246,refreshed_cases=71,scope='Affected contact/native-flight call sites include imported humanoids; all refreshed. Old source hashes retained on reused evidence rows, not rewritten as new runs.')
    (ROOT/'docs/b4artists_ml/native-contact-source-audit-v1.json').write_text(json.dumps(audit,indent=2)+'\n')
    with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for n,p in sorted(paths.items()):
            info=zipfile.ZipInfo(n,date_time=(2026,9,8,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;archive.writestr(info,p.read_bytes(),compresslevel=9)
    with zipfile.ZipFile(out) as archive:assert all(archive.read(n)==p.read_bytes() for n,p in paths.items())
    reg=dict(passed=True,unique_cases=317,suites=len(retained)+len(fresh),refreshed_cases=71,reused_cases=246,runtime_sha256=current,rows=retained+fresh,source_audit_sha256=sha(ROOT/'docs/b4artists_ml/native-contact-source-audit-v1.json'),host_shutdown_passed=False)
    regpath=ROOT/'training/b4artists_ml/results/native-contact-regression-v1.json';regpath.write_text(json.dumps(reg,indent=2)+'\n')
    meta=dict(version='0.17.1',files=len(paths),bytes=out.stat().st_size,sha256=sha(out),package_matches_source=True,experimental=True,full_goal_complete=False,unique_regression_cases=317,refreshed_cases=71,reused_cases=246,regression_sha256=sha(regpath),offline_qualification='pending',packaged_ui_qualification='pending',host_shutdown_qualified=False,scope='Native transitions and contact composition, generated timing metadata, legacy archive compatibility and editable recovery. No temporal model promoted.')
    (ROOT/'docs/b4artists_ml/package-test-v0.17.1.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta),flush=True)
if __name__=='__main__':main()
