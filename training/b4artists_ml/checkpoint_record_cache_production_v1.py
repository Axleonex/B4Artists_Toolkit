"""Evidence-backed production cache goalpost under the authorized extension."""
import copy,time,subprocess,zipfile
from pathlib import Path
from checkpoint_expanded_goal_v19 import ROOT,read,sha,write,g,evaluate

def main():
    base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/'
    cp=read(base+'checkpoint-extension20h-v1.json');prior=cp['state_path'];old=read(prior);s=copy.deepcopy(old)
    previous=gp+'record-cache-evidence-v1.json';e=read(previous)
    dest=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-record-cache-production-v1.json'
    assert not (ROOT/dest).exists()
    meta=read(base+'package-test-v0.17.5.json');bench=read(res+'record-cache-benchmark-production-v1.json')
    regression=read(res+'record-cache-production-full-v1-regression.json');offline=read(res+'record-cache-package-v1.json')
    assert meta['ready_for_local_testing'] and meta['packaged_host_smoke']=='passed'
    assert len(regression)==33 and sum(r['tests'] for r in regression)==345
    assert all(r['assertions_passed'] and not r['skipped'] for r in regression)
    assert bench['complete'] and bench['passed'] and all(r['exact_pose_signature_metrics_parity'] and r['source_preserved'] for r in bench['comparisons'])
    assert offline['passed'] and offline['cases']==4 and not offline['denied_runtime_calls']
    current={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in (ROOT/'b4artists_ml').glob('*.py')}
    assert current==meta['runtime_sha256']==offline['runtime_sha256']
    pre=copy.deepcopy(current);pre['b4artists_ml/__init__.py']=meta['version_only_change_after_checks']['before_sha256']
    assert all(r['runtime_sha256']==pre for r in regression)
    assert all(r['runtime_sha256']==pre for r in bench['rows'] if r['variant']=='current')
    archive='releases/b4artists_ml_v0.17.5.zip';assert sha(archive)==meta['sha256']==offline['package_sha256']
    with zipfile.ZipFile(ROOT/archive) as z:assert all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist())
    changed=[p for p,h in e['artifacts'].items() if sha(p)!=h]
    expected={'b4artists_ml/body_preview.py','b4artists_ml/__init__.py'}|{base+n+'.md' for n in ['PROJECT','ROADMAP','REQUIREMENTS','USER_GUIDE']}
    assert set(changed)==expected,changed
    versions={}
    for p in changed:
        snapshot=res+'record-cache-production-baseline-v1/'+p
        assert sha(snapshot)==e['artifacts'][p]
        versions[p]=dict(path=snapshot,sha256=sha(snapshot))
    inputs=['b4artists_ml/record_cache.py','tests/test_b4artists_ml_record_cache.py',
        tr+'record_cache_production_plan_v1.json',tr+'record_cache_production_regression_plan_v1.json',
        tr+'benchmark_record_cache_production_v1.py',tr+'build_record_cache_package_v1.py',tr+'check_record_cache_package_v1.py',
        tr+'finalize_record_cache_package_v1.py',tr+'checkpoint_record_cache_production_v1.py',
        base+'RECORD-CACHE-PRODUCTION-PLAN-v1.md',base+'RECORD-CACHE-PRODUCTION-v1.md']
    added=[p for p in inputs if p not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract'])
    s['explicit_revisions'].append(dict(reason='Integrate bounded JSON record reconstruction with lifecycle cleanup;345fresh regression cases, exact five-profile speed/parity comparison and four offline package cases. Full endpoint, floors,50evaluation limit and explicitly extended deadline unchanged.',prior_state=prior,prior_sha256=sha(prior),prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],added_inputs=added,recorded_at=time.time()))
    fp=g.fingerprint(ROOT,s['contract']['inputs']);paths=set(e['artifacts'])|set(inputs)|{prior,previous,base+'checkpoint-extension20h-v1.json',gp+'record-cache-production-routing-v1.json',base+'package-test-v0.17.5.json',archive}
    for pattern in ['record-cache-production-*.json','record-cache-benchmark-production-v1*.json','record-cache-package-v1*.json']:
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res).glob(pattern) if p.is_file())
    for pattern in ['record-cache-production-*.log','record-cache-benchmark-production-v1*.log','record-cache-package-v1*.log']:
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/tr/'cache').glob(pattern) if p.is_file())
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res/'record-cache-production-baseline-v1').rglob('*') if p.is_file())
    plan=read(tr+'temporal_expansion_plan_v19.json');assert all(not (ROOT/tr/'cache'/(c+'.bvh')).exists() for c in plan['planned_splits']['confirmation'])
    args=['git','-c','safe.directory=X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github']
    assert subprocess.check_output(args+['log','-1','--format=%H %an <%ae> %cn <%ce>'],cwd=ROOT,text=True).strip()==cp['publication']['head']
    assert not subprocess.check_output(args+['diff','--name-only'],cwd=ROOT,text=True).strip()
    assert not subprocess.check_output(args+['diff','--cached','--name-only'],cwd=ROOT,text=True).strip()
    e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={p:sha(p) for p in sorted(paths)},
        previous_evidence_recheck=dict(path=previous,sha256=sha(previous),changed_artifacts=changed,preserved_prior_versions=versions,all_other_prior_artifacts_unchanged=True),
        package=dict(path=archive,sha256=meta['sha256'],files=meta['files'],bytes=meta['bytes'],matches_current_source=True,experimental=True),
        regression=dict(passed=True,unique_cases=345,suites=33,refreshed_cases=345,reused_cases=0,all_current_behavior_runs=True,version_only_metadata_change_after_checks=True,current_coverage_verified=True,rerun_this_iteration=True,note='All prior331cases plus14new cache cases pass without skips; version literal only changes afterward. Host shutdown fails separately.'),
        offline=offline,packaged_ui=dict(status='unverified',note='UI source unchanged; earlier UI evidence remains historical. No current-package UI interaction claim.'),
        production_cache_integrated=True,record_cache_production_comparison=bench['comparisons'],preserved_milestones=old['passed_progress_milestones'],new_passing_milestones=[])
    e['qualification'].update(full_goal_complete=False,temporal_model_qualification=False,temporal_animator_integration=False,host_shutdown=False,independent_usability='unknown',full_physics_acceptance=False,full_responsiveness=False,current_package_ui='unverified')
    e['limitations']=['Cache-local memory bounds and scoped headless speed gates pass, but full workflow memory, viewport latency and50msworst-tick qualification remain incomplete.','Host shutdown still crashes after assertions. Current-package UI and independent usability remain unverified.','All original learned motion, posing quality, physics/refinement, rig/quadruped, optional connector, distribution and equivalent Cascadeur requirements remain incomplete. All candidates remain frozen; fresh confirmation absent.']
    ep=gp+'record-cache-production-evidence-v1.json';write(ep,e);obs=read(gp+'record-cache-observations-v1.json')
    for group in obs.values():
        for proof in group.values():proof.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
    write(gp+'record-cache-production-observations-v1.json',obs)
    end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];event='controller-record-cache-production-v1'
    assert event not in s['work_events'];g.record_work(s,event,duration);result=evaluate(s,obs,ROOT)
    assert result['round']==43 and result['decision']=='iterate'
    assert not result['implementation_progress']['new'] and not result['implementation_progress']['lost']
    assert all(not c['regression'] for c in result['categories'].values()) and s['history'][:-1]==old['history']
    assert s['contract']['max_goalposts']==50 and cp['deadline_unix']==1788981845.0
    write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result),encoding='utf-8')
    cp.update(state_path=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=43,remaining_evaluations=7,decision=result['decision'],stagnant_rounds=s['stagnant_rounds'],evidence=ep,artifact=e['package'],active_jobs=[],next_controller_monotonic_start=end,current_turn_classification='Progress: resolved user time allowance, integrated bounded record copying,345fresh regression cases, exact five-profile speed/parity comparison, four exact-package offline cases and experimental0.17.5local artifact. Full goal incomplete.',work_accounting='Counted only active resumed controller work from extension checkpoint; no blocked waiting time or duplicate prior events.',next_safe_actions=['Continue the full original goal under the same ID,50total evaluations and2026-09-09T19:24:05Z deadline;7evaluations remain.','Prioritize remaining learned temporal quality and integrated animator workflow with fixed training-only hypothesis tests and original validation gates; do not open confirmation for unqualified candidates.','Continue full physics/refinement, broader rigs/quadrupeds, optional connector, responsiveness, independent usability and equivalent Cascadeur comparison. Do not treat0.17.5or green regression as completion.'],recorded_at=time.time())
    write(base+'checkpoint-record-cache-production-v1.json',cp)
    progress=read(base+'record-cache-production-progress-v1.json');progress.update(status='evaluated',latest_checkpoint=base+'checkpoint-record-cache-production-v1.json',round=43,remaining_evaluations=7,active_jobs=[],recorded_at=time.time());write(base+'record-cache-production-progress-v1.json',progress)
    print(dict(round=43,remaining=7,decision=result['decision'],work_seconds=duration,next_controller_monotonic_start=end,deadline_unix=cp['deadline_unix'],full_goal_complete=False))
if __name__=='__main__':main()
