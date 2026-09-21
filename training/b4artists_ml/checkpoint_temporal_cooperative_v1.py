"""Record cooperative research and preserve the full active goal and live training."""
import copy,time,subprocess,zipfile
from pathlib import Path
from checkpoint_expanded_goal_v19 import ROOT,read,write,sha,g,evaluate

def main():
    base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/'
    cp=read(base+'checkpoint-projected-selector-running-v26.json');prior=cp['state_path'];old=read(prior);s=copy.deepcopy(old);previous=cp['evidence'];e=read(previous)
    dest=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-temporal-cooperative-v1.json';assert not (ROOT/dest).exists()
    proof=read(res+'temporal-cooperative-verification-v1.json');assert proof['complete'] and proof['passed'] and proof['native_tests']==25 and proof['reference_cases']==11
    assert not proof['ui_integrated'] and not proof['learned_provider_tested'] and not proof['full_responsiveness'] and not proof['full_goal_complete']
    for n,h in proof['source_sha256'].items():assert sha(n)==h,n
    meta=read(base+'package-test-v0.17.5.json');current={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in (ROOT/'b4artists_ml').glob('*.py')};assert current==meta['runtime_sha256']==proof['runtime_sha256']
    assert sha(cp['artifact']['path'])==cp['artifact']['sha256']==meta['sha256']==proof['package_sha256']
    with zipfile.ZipFile(ROOT/cp['artifact']['path']) as z:assert all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist())
    progress=[]
    for name in ('projected_selector_v26','projected_selector_v26_repeat'):
        row=read(res+name+'/projection_progress.json');assert row['training_only'] and not row['validation_loaded'] and not row['complete']
        assert not (ROOT/res/name/'selection_frozen.json').exists()
        for n,h in row['source_sha256'].items():assert sha(tr+n)==h,n
        progress.append(dict(output=res+name,processed=row['processed'],total=row['total'],model_frozen=False,validation_loaded=False))
    changed=[p for p,h in e['artifacts'].items() if sha(p)!=h];assert set(changed)=={base+n+'.md' for n in ('PROJECT','ROADMAP','REQUIREMENTS')},changed
    versions={}
    for n in changed:
        v=cp['pending_document_revisions'][n];assert sha(v['prior_version'])==v['before_sha256']==e['artifacts'][n] and sha(n)==v['after_sha256'];versions[n]=dict(path=v['prior_version'],sha256=v['before_sha256'])
    names=['temporal_cooperative_v1.py','temporal_cooperative_plan_v1.json','checkpoint_temporal_cooperative_v1.py','selector_edit_stability_v26.py','selector_edit_stability_plan_v26.json','check_projected_selector_host_v26.py','check_stationary_projected_selector_host_v26.py','check_projected_selector_journey_v26.py','verify_projected_selector_reproduction_v26.py','analyze_projected_selector_v26.py']
    inputs=[tr+n for n in names]+['tests/test_b4artists_ml_temporal_cooperative.py','tests/test_b4artists_ml_temporal_cooperative_pipeline.py',base+'TEMPORAL-COOPERATIVE-v1.md']
    added=[p for p in inputs if p not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract'])
    a=copy.deepcopy(s['contract']);b=copy.deepcopy(old['contract']);a.pop('inputs');b.pop('inputs');assert a==b
    s['explicit_revisions'].append(dict(reason='Add cooperative temporal source-visible scheduling and save/load lifecycle evidence:25native tests pass,11reference comparisons across8rigs. Responsiveness remains failed; current runtime/package and v26frozen training stay unchanged. Preserve full original endpoint,all floors,50evaluations and extended deadline.',prior_state=prior,prior_sha256=sha(prior),prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],added_inputs=added,recorded_at=time.time()))
    fp=g.fingerprint(ROOT,s['contract']['inputs']);paths=set(e['artifacts'])|set(inputs)|{prior,previous,res+'temporal-cooperative-verification-v1.json'}
    paths.update(gp+n for n in ['temporal-cooperative-routing-v1.json','temporal-cooperative-review-v1.json','projected-selector-validation-routing-v26.json','projected-selector-validation-review-v26.json'])
    for pattern in ('temporal-cooperative-*','projected-selector-validation-preflight-v26','projected-selector-current-docs-baseline-v26'):
        for p in (ROOT/res).glob(pattern):
            if p.is_file():paths.add(p.relative_to(ROOT).as_posix())
            elif p.is_dir():paths.update(q.relative_to(ROOT).as_posix() for q in p.rglob('*') if q.is_file())
    for p in (ROOT/tr/'cache').glob('temporal-cooperative-*'):
        if p.is_file():paths.add(p.relative_to(ROOT).as_posix())
    for v in versions.values():paths.add(v['path'])
    plan=read(tr+'temporal_expansion_plan_v19.json');assert all(not (ROOT/tr/'cache'/(c+'.bvh')).exists() for c in plan['planned_splits']['confirmation'])
    args=['git','-c','safe.directory=X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github']
    assert subprocess.check_output(args+['log','-1','--format=%H %an <%ae> %cn <%ce>'],cwd=ROOT,text=True).strip()==cp['publication']['head']
    assert not subprocess.check_output(args+['diff','--name-only'],cwd=ROOT,text=True).strip();assert not subprocess.check_output(args+['diff','--cached','--name-only'],cwd=ROOT,text=True).strip()
    e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={n:sha(n) for n in sorted(paths)},previous_evidence_recheck=dict(path=previous,sha256=sha(previous),changed_artifacts=changed,preserved_prior_versions=versions,all_other_prior_artifacts_unchanged=True),cooperative_temporal_research=proof,projected_selector_training=dict(status='both_runs_generating_labels',active_sessions=[23370,87876],runs=progress,model_frozen=False,validation_read=False,complete=False),preserved_milestones=old['passed_progress_milestones'],new_passing_milestones=[])
    e['regression'].update(rerun_this_iteration=False,refreshed_cases=0,reused_cases=345,retained_from=previous,note='Current0.17.5runtime and archive unchanged. Prior345native and four offline package cases retained;25fresh cooperative research cases do not constitute a new full runtime regression.')
    e['qualification'].update(full_goal_complete=False,temporal_model_qualification=False,temporal_animator_integration=False,independent_usability='unknown',host_shutdown=False,full_responsiveness=False,full_physics_acceptance=False)
    e['limitations']=['The cooperative research path passes native source-visible/lifecycle/action checks, but product UI/disable integration and qualified learned-provider coverage remain pending.','Diagnostic Rigify ticks reach320.22ms; no50msresponsiveness or paired performance improvement claim. Host shutdown and independent code review remain unresolved.','Both frozen v26runs are still generating training costs. No new trained model quality, confirmation or release claim.','The full original learned-motion, posing/generalization, physics/refinement, broader rigs/quadrupeds, connector, independent animator and equivalent Cascadeur comparison requirements remain.']
    ep=gp+'temporal-cooperative-evidence-v1.json';write(ep,e);obs=read(gp+'projected-selector-preparation-observations-v26.json')
    for group in obs.values():
        for row in group.values():row.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
    write(gp+'temporal-cooperative-observations-v1.json',obs);end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];event='controller-temporal-cooperative-v1';assert event not in s['work_events'];g.record_work(s,event,duration);result=evaluate(s,obs,ROOT)
    assert result['round']==45 and result['decision']=='iterate' and not result['implementation_progress']['new'] and not result['implementation_progress']['lost'];assert all(not c['regression'] for c in result['categories'].values());assert s['history'][:-1]==old['history']
    assert cp['deadline_unix']==1788981845. and s['contract']['max_goalposts']==50
    write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result),encoding='utf-8')
    cp.update(state_path=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=45,remaining_evaluations=5,decision=result['decision'],stagnant_rounds=s['stagnant_rounds'],evidence=ep,next_controller_monotonic_start=end,pending_document_revisions={},current_turn_classification='Progress: cooperative temporal research backend passes25native source-visible,editable-action,cancellation,save/load and recovery tests. Full responsiveness and product integration remain incomplete. Verified wait: both v26corpus runs remain live; source/inputs frozen.',recorded_at=time.time())
    cp['next_safe_actions']=['Poll existing sessions23370and87876; neither is terminal. Do not restart or mutate frozen training inputs.','After primary completion verify original development gates, run moving/stationary/journey model checks and the prepared edit-stability/failure-attribution diagnostics. After both complete run exact full reproduction.','Exercise the frozen trained provider through the cooperative research path before product integration.25procedural-provider scheduling/lifecycle cases do not establish learned quality or complete responsiveness.','Use measured slow checkpoints to guide a bounded optimization; retain exact source/priority/refit checks and do not promote an unqualified model.','Preserve same full goal and50evaluation ceiling:45used,fiveremain. Deadline2026-09-09T19:24:05Z.']
    write(base+'checkpoint-temporal-cooperative-v1.json',cp)
    live=read(base+'projected-pool-progress-v26.json');live.update(latest_checkpoint=base+'checkpoint-temporal-cooperative-v1.json',round=45,remaining_evaluations=5,active_jobs=cp['active_jobs'],pending_document_revisions={},recorded_at=time.time());write(base+'projected-pool-progress-v26.json',live)
    print(dict(round=45,remaining_evaluations=5,decision=result['decision'],work_seconds=duration,next_controller_monotonic_start=end,active_sessions=[23370,87876],full_goal_complete=False))
if __name__=='__main__':main()
