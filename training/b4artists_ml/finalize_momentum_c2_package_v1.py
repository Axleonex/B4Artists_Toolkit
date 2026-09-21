"""Seal exact-package and real-window evidence for experimental 0.20.3."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[2]
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    archive=ROOT/'releases/b4artists_ml_v0.20.3.zip';meta_path=ROOT/'docs/b4artists_ml/package-test-v0.20.3.json';meta=read(meta_path)
    package_path=ROOT/'training/b4artists_ml/results/momentum-c2-package-v1.json';package=read(package_path)
    ui_path=ROOT/'docs/b4artists_ml/native-ui-momentum-c2-package-v1.json';ui=read(ui_path)
    process=read(ROOT/'training/b4artists_ml/results/native-ui-process-momentum-c2-package-v1.json')
    assert sha(archive)==meta['sha256']==package['package_sha256'] and package['passed'] and package['tests']==10 and package['exact_package']
    assert not package['denied_runtime_calls'] and not package['host_shutdown_qualified']
    assert ui['passed'] and ui['match_acceleration'] and len(ui['metrics']['transitions'])==2
    assert all(row['match_acceleration'] and row['normalized_jump']<=.02 and row['normalized_acceleration_jump']<=.1 for row in ui['metrics']['transitions'])
    assert ui['runtime_sha256']==meta['runtime_sha256'] and process['exit_code']==3221225477
    with zipfile.ZipFile(archive) as package_zip:
        names=set(package_zip.namelist());source={p.relative_to(ROOT).as_posix():p for p in (ROOT/'b4artists_ml').rglob('*') if p.is_file() and (p.suffix in ('.py','.json','.md','.npz') or p.name=='LICENSE')}
        assert names==set(source) and all(package_zip.read(name)==path.read_bytes() for name,path in source.items())
    meta['exact_package_momentum']=dict(passed=True,tests=package['tests'],offline_guard=True,evidence=package_path.relative_to(ROOT).as_posix())
    meta['exact_package_ui']=dict(passed=True,match_acceleration=True,events=len(ui['events']),step_count=ui['step_count'],step_p95_ms=ui['step_p95_ms'],step_max_ms=ui['step_max_ms'],elapsed_seconds=ui['elapsed_seconds'],evidence=ui_path.relative_to(ROOT).as_posix(),process_evidence='training/b4artists_ml/results/native-ui-process-momentum-c2-package-v1.json')
    meta['ready_for_local_testing']=True;meta['responsiveness_under_50ms_verified']=ui['step_p95_ms']<50 and ui['step_max_ms']<50
    meta['host_shutdown_qualified']=False
    meta_path.write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'package_sha256':meta['sha256'],'exact_package_tests':package['tests'],'ui_passed':ui['passed'],'step_p95_ms':ui['step_p95_ms'],'step_max_ms':ui['step_max_ms'],'responsiveness_under_50ms_verified':meta['responsiveness_under_50ms_verified'],'host_shutdown_qualified':False},indent=2))
if __name__=='__main__':main()
