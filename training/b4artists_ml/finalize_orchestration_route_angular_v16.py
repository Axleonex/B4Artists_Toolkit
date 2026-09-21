"""Bind the active routing/evaluation contract to the 0.21.0 release evidence."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'training/b4artists_ml/results/orchestration-route-angular-momentum-v16.json'
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    assert not OUT.exists()
    prior=read(ROOT/'training/b4artists_ml/results/orchestration-route-com-acceleration-v15.json')
    regression_path=ROOT/'training/b4artists_ml/results/angular-momentum-full-v2-regression.json';regression=read(regression_path)
    package_path=ROOT/'training/b4artists_ml/results/angular-momentum-package-v1.json';package=read(package_path)
    ui_path=ROOT/'docs/b4artists_ml/native-ui-angular-momentum-package-v1.json';ui=read(ui_path)
    meta_path=ROOT/'docs/b4artists_ml/package-test-v0.21.0.json';meta=read(meta_path)
    assert len(regression)==46 and sum(row['tests'] for row in regression)==439 and all(row['assertions_passed'] for row in regression)
    assert len({json.dumps(row['runtime_sha256'],sort_keys=True) for row in regression})==1
    assert package['passed'] and package['tests']==16 and not package['denied_runtime_calls']
    assert ui['passed'] and ui['runtime_sha256']==regression[0]['runtime_sha256']==package['runtime_sha256']==meta['runtime_sha256']
    result=dict(schema=1,recorded_date='2026-09-10',session_scope='B4Artists Machine Learning experimental 0.21.0 airborne angular-momentum refinement',canonical=prior['canonical'],execution=prior['execution'],evaluation=dict(depth='S3',mode='shadow/classification-only',runnable=True,model_calls=0,policy_fingerprint=prior['evaluation']['policy_fingerprint'],release='0.21.0',archive='releases/b4artists_ml_v0.21.0.zip',archive_sha256=meta['sha256'],source_regression=regression_path.relative_to(ROOT).as_posix(),source_regression_sha256=sha(regression_path),source_suites=46,source_tests=439,source_assertions_passed=True,exact_package=package_path.relative_to(ROOT).as_posix(),exact_package_sha256=sha(package_path),exact_package_tests=16,exact_package_assertions_passed=True,real_window=ui_path.relative_to(ROOT).as_posix(),real_window_sha256=sha(ui_path),real_window_passed=True,step_p95_ms=ui['step_p95_ms'],step_max_ms=ui['step_max_ms'],responsiveness_under_50ms_verified=ui['step_p95_ms']<50 and ui['step_max_ms']<50,angular_variation_improvement=ui['metrics']['intervals'][0]['angular_momentum']['improvement'],host_shutdown_qualified=False,human_reviewed_cases=0,cascadeur_results_present=False),formal_goal=dict(state_unchanged=True,complete=False,remaining_primary_gates=['completed independent animator export and timed correction pass','reviewed motion labels','accepted learned temporal motion','full segment inertia, forces, collision and secondary motion','quadrupeds','executed matched Cascadeur evaluation']))
    assert result['execution']['continuation']=='native' and not result['execution']['production_state_changed'] and result['evaluation']['model_calls']==0
    OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({'receipt':OUT.relative_to(ROOT).as_posix(),'sha256':sha(OUT),'route':result['execution']['continuation'],'evaluation':result['evaluation']['mode'],'release':result['evaluation']['release']},indent=2))
if __name__=='__main__':main()
