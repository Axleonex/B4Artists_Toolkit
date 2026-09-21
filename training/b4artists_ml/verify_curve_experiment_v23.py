"""Consolidated scoped checks; no new claim of a full runtime test run."""
from pathlib import Path
import json,hashlib,zipfile,subprocess
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
 tr='training/b4artists_ml/';res=tr+'results/';base='docs/b4artists_ml/'
 report=read(res+'curve_mixture_v23/report.json');repro=read(res+'curve-mixture-reproduction-v23.json');checks=read(res+'curve-mixture-checks-v23.json');old=read(res+'kinematic_trajectory_v20/report.json')
 assert repro['passed'] and checks['passed'] and len(checks['checks'])==18
 assert read(res+'curve-compatibility-v23.json')['passed']
 feature=read(res+'curve_mixture_v23/feature_audit.json');assert feature['finite'] and feature['new_nonnegative'] and feature['rows']==7358 and feature['columns']==596
 assert report['protocol']['gates']==old['protocol']['gates'] and report['protocol']['projection']==old['protocol']['projection']
 for part in ['old_validation','new_validation','combined']:
  for name in report['protocol']['baselines']:assert report['partition_reports'][part][name]==old['partition_reports'][part][name]
 assert not report['confirmation_read']
 plan=read(tr+'temporal_expansion_plan_v19.json');assert all(not (ROOT/tr/'cache'/(c+'.bvh')).exists() for c in plan['planned_splits']['confirmation'])
 for name,h in report['source_sha256'].items():assert sha(tr+name)==h
 for name,h in report['protocol']['parent_files'].items():assert sha(tr+name)==h
 moving=read(res+'curve-mixture-host-v23.json');stationary=read(res+'stationary-curve-host-v23.json');meta=read(base+'package-test-v0.17.4.json')
 current={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in (ROOT/'b4artists_ml').glob('*.py')};assert current==meta['runtime_sha256']
 for host in [moving,stationary]:assert host['complete'] and host['passed'] and len(host['rows'])==16 and host['runtime_sha256']==current and host['model_sha256']==report['selection']['best_learned_sha256']
 with zipfile.ZipFile(ROOT/'releases/b4artists_ml_v0.17.4.zip') as archive:assert all(archive.read(n)==(ROOT/n).read_bytes() for n in archive.namelist())
 assert sha('releases/b4artists_ml_v0.17.4.zip')==meta['sha256']
 args=['git','-c','safe.directory=X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github'];cp=read(base+'checkpoint-relative-mixture-v22.json')
 assert subprocess.check_output(args+['log','-1','--format=%H %an <%ae> %cn <%ce>'],cwd=ROOT,text=True).strip()==cp['publication']['head']
 assert not subprocess.check_output(args+['diff','--name-only'],cwd=ROOT,text=True).strip();assert not subprocess.check_output(args+['diff','--cached','--name-only'],cwd=ROOT,text=True).strip()
 result=dict(passed=True,pre_fit_checks=18,zero_extension_compatibility=True,feature_audit=feature,moving_rig_cases=16,stationary_rig_cases=16,reproduction_passed=True,matched_controls_unchanged=True,sources_and_parent_artifacts_unchanged=True,confirmation_absent=True,model_sha256=report['selection']['best_learned_sha256'],runtime_unchanged=True,package_unchanged=True,package_sha256=meta['sha256'],retained_runtime_regression=dict(cases=330,suites=31,offline_package_cases=4,rerun=False),host_processes=[read(res+n+'-process.json') for n in ['curve-mixture-host-v23','stationary-curve-host-v23']],development_quality_passed=report['gates']['best_learned']['passed'],full_goal_complete=False,publication=cp['publication'],source_sha256={Path(__file__).name:sha(Path(__file__))})
 out=ROOT/res/'curve-experiment-verification-v23.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
