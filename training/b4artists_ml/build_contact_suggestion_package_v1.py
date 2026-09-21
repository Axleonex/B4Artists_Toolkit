"""Build experimental 0.20.0 after scene-contact source qualification."""
from pathlib import Path
import ast,hashlib,json,zipfile

ROOT=Path(__file__).resolve().parents[2]
RESULTS=ROOT/'training/b4artists_ml/results'
OUTPUT=ROOT/'releases/b4artists_ml_v0.20.0.zip'

def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def runtime_hashes():return {p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'b4artists_ml').glob('*.py')}

def main():
    assert not OUTPUT.exists()
    rows=read('training/b4artists_ml/results/contact-suggestions-production-full-v1-regression.json');tested=runtime_hashes()
    assert len(rows)==45 and sum(r['tests'] for r in rows)==428
    assert all(r['assertions_passed'] and not r.get('errors') and not r.get('failures') and not r.get('skipped') for r in rows)
    assert all(r['runtime_sha256']==tested for r in rows)
    source=read('training/b4artists_ml/results/contact-suggestions-v1-cooperative.json');assert source['passed'] and source['tests']==4
    ui=read('training/b4artists_ml/results/contact-suggestions-ui-v1.json')
    assert ui['passed'] and ui['suggestion']['provisional'] and ui['suggestion']['suggestions']==2
    assert ui['suggestion_step_p95_ms']<=50 and ui['suggestion_step_max_ms']<=50
    assert ui['correction']['contacts']==1 and ui['correction']['max_after']<2e-4
    assert (ROOT/ui['screenshot']).is_file()
    init=ROOT/'b4artists_ml/__init__.py';old=init.read_text(encoding='utf-8-sig');needle='"version": (0, 19, 5)';assert old.count(needle)==1
    updated=old.replace(needle,'"version": (0, 20, 0)',1);old_tree=ast.parse(old);new_tree=ast.parse(updated)
    def info(tree):return next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='bl_info' for t in n.targets)).value
    a=info(old_tree);b=info(new_tree);index=next(i for i,key in enumerate(a.keys) if key.value=='version');assert ast.literal_eval(b.values[index])==(0,20,0);b.values[index]=a.values[index];assert ast.dump(old_tree)==ast.dump(new_tree)
    baseline=RESULTS/'contact-suggestion-package-baseline-v1';baseline.mkdir(exist_ok=False);(baseline/'__init__.py').write_bytes(init.read_bytes());init.write_text(updated,encoding='utf-8',newline='\n')
    packaged=runtime_hashes();assert {n for n in tested if tested[n]!=packaged[n]}=={'b4artists_ml/__init__.py'}
    paths={p.relative_to(ROOT).as_posix():p for p in (ROOT/'b4artists_ml').rglob('*') if p.is_file() and (p.suffix in ('.py','.json','.md','.npz') or p.name=='LICENSE')}
    for path in paths.values():
        if path.suffix=='.py':ast.parse(path.read_bytes())
    with zipfile.ZipFile(OUTPUT,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name,path in sorted(paths.items()):
            item=zipfile.ZipInfo(name,date_time=(2026,9,10,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED;item.external_attr=0o644<<16;archive.writestr(item,path.read_bytes(),compresslevel=9)
    with zipfile.ZipFile(OUTPUT) as archive:assert set(archive.namelist())==set(paths) and all(archive.read(name)==path.read_bytes() for name,path in paths.items())
    report=dict(version='0.20.0',files=len(paths),bytes=OUTPUT.stat().st_size,sha256=sha(OUTPUT),package_matches_source=True,experimental=True,full_goal_complete=False,ready_for_local_testing=False,runtime_sha256=packaged,
        regression=dict(unique_cases=428,suites=45,evidence='training/b4artists_ml/results/contact-suggestions-production-full-v1-regression.json',tested_runtime_sha256=tested,post_test_version_only_revision=dict(before_sha256=tested['b4artists_ml/__init__.py'],after_sha256=packaged['b4artists_ml/__init__.py'],only_version_literal_changed=True)),
        source_contact_suggestions='training/b4artists_ml/results/contact-suggestions-v1-cooperative.json',ui_contact_suggestions='training/b4artists_ml/results/contact-suggestions-ui-v1.json',packaged_host_smoke='pending',host_shutdown_qualified=False,independent_human_usability='unknown',
        qualification_note='Scene-aware foot-contact suggestions are provisional, animator-reviewed and source-safe on the qualified humanoid fixtures. Moving surfaces, arbitrary collision geometry, hand/object detection, independent usability, learned temporal quality, quadrupeds and Cascadeur parity remain unqualified.')
    (ROOT/'docs/b4artists_ml/package-test-v0.20.0.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('version','files','bytes','sha256')},indent=2))

if __name__=='__main__':main()
