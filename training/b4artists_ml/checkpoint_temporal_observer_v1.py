"""Preserve full-goal history after measured research scheduling changes."""
import copy,time,subprocess,zipfile
from checkpoint_expanded_goal_v19 import ROOT,read,write,sha,g,evaluate

def main():
    base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/'
    cp=read(base+'checkpoint-temporal-cooperative-v1.json');prior=cp['state_path'];old=read(prior);s=copy.deepcopy(old);previous=cp['evidence'];e=read(previous)
    dest=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-temporal-observer-v1.json';assert not (ROOT/dest).exists()
    proof=read(res+'temporal-observer-verification-v1.json');assert proof['complete'] and proof['passed'] and proof['native_tests']==28 and proof['exact_observation_cases']==16
    assert not any(proof[k] for k in ('ui_integrated','learned_provider_tested','full_responsiveness','full_goal_complete','host_shutdown_passed','independent_code_review'))
    for group in ('source_sha256','result_sha256'):
        for n,h in proof[group].items():assert sha(n)==h,n
    meta=read(base+'package-test-v0.17.5.json');current={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in (ROOT/'b4artists_ml').glob('*.py')};assert current==meta['runtime_sha256']==proof['runtime_sha256']
    assert sha(cp['artifact']['path'])==cp['artifact']['sha256']==meta['sha256']==proof['package_sha256']
    with zipfile.ZipFile(ROOT/cp['artifact']['path']) as z:assert all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist())
    changed=[p for p,h in e['artifacts'].items() if sha(p)!=h];assert set(changed)=={tr+'temporal_cooperative_v1.py',base+'TEMPORAL-COOPERATIVE-v1.md'},changed
    versions={}
    for n in changed:
        path=res+'temporal-restore-baseline-v1/temporal_cooperative_v1.py' if n.endswith('.py') else cp['pending_document_revisions'][n]['prior_version']
        assert sha(path)==e['artifacts'][n];versions[n]=dict(path=path,sha256=sha(path))
    middle=read(res+'temporal-observer-baseline-v1/receipt.json');restore=read(res+'temporal-restore-baseline-v1/receipt.json')
    assert sha(middle['baseline_source'])==middle['before_sha256']==restore['after_sha256'] and sha(tr+'temporal_cooperative_v1.py')==middle['after_sha256']
    progress=[]
    for name in ('projected_selector_v26','projected_selector_v26_repeat'):
        row=read(res+name+'/projection_progress.json');assert row['training_only'] and not row['validation_loaded'] and not row['complete']
        assert not (ROOT/res/name/'selection_frozen.json').exists()
        for n,h in row['source_sha256'].items():assert sha(tr+n)==h,n
        progress.append(dict(output=res+name,processed=row['processed'],total=row['total'],model_frozen=False,validation_loaded=False))
    names=['temporal_observer_steps_v1.py','temporal_observer_plan_v1.json','benchmark_temporal_observer_v1.py','checkpoint_temporal_observer_v1.py','temporal_restore_optimization_v1.py','temporal_restore_optimization_plan_v1.json','benchmark_temporal_restore_v1.py','profile_temporal_cooperative_v1.py','check_projected_selector_cooperative_v26.py']
    inputs=[tr+n for n in names]+['tests/test_b4artists_ml_temporal_observer_cooperative.py',base+'TEMPORAL-SCHEDULING-PERFORMANCE-v1.md']
    added=[p for p in inputs if p not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract'])
    a=copy.deepcopy(s['contract']);b=copy.deepcopy(old['contract']);a.pop('inputs');b.pop('inputs');assert a==b
    s['explicit_revisions'].append(dict(reason='Measured research-only selective restoration and cooperative known-pose sampling;28native methods and24counterbalanced observation runs pass. Preserve original source versions, all floors, full endpoint,50evaluations and authorized20-hour extension. Loaded-host scheduling tradeoff does not change the50msproduct target.',prior_state=prior,prior_sha256=sha(prior),prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],added_inputs=added,preserved_prior_versions=versions,recorded_at=time.time()))
    fp=g.fingerprint(ROOT,s['contract']['inputs']);paths=set(e['artifacts'])|set(inputs)|{prior,previous,res+'temporal-observer-verification-v1.json',gp+'temporal-observer-routing-v1.json',gp+'temporal-cooperative-profile-routing-v1.json'}
    for pattern in ('temporal-restore-*','temporal-observer-*','temporal-cooperative-profile-v1*'):
        for p in (ROOT/res).glob(pattern):
            if p.is_file():paths.add(p.relative_to(ROOT).as_posix())
            elif p.is_dir():paths.update(q.relative_to(ROOT).as_posix() for q in p.rglob('*') if q.is_file())
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/tr/'cache').glob(pattern) if p.is_file())
    plan=read(tr+'temporal_expansion_plan_v19.json');assert all(not (ROOT/tr/'cache'/(c+'.bvh')).exists() for c in plan['planned_splits']['confirmation'])
    args=['git','-c','safe.directory=X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github']
    assert subprocess.check_output(args+['log','-1','--format=%H %an <%ae> %cn <%ce>'],cwd=ROOT,text=True).strip()==cp['publication']['head']
    assert not subprocess.check_output(args+['diff','--name-only'],cwd=ROOT,text=True).strip();assert not subprocess.check_output(args+['diff','--cached','--name-only'],cwd=ROOT,text=True).strip()
    e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={n:sha(n) for n in sorted(paths)},previous_evidence_recheck=dict(path=previous,sha256=sha(previous),changed_artifacts=changed,preserved_prior_versions=versions,all_other_prior_artifacts_unchanged=True),cooperative_observation_research=proof,projected_selector_training=dict(status='both_runs_generating_labels',active_sessions=[23370,87876],runs=progress,model_frozen=False,validation_read=False,complete=False),preserved_milestones=old['passed_progress_milestones'],new_passing_milestones=[])
    e['regression'].update(rerun_this_iteration=False,refreshed_cases=0,reused_cases=345,retained_from=previous,note='Current0.17.5runtime and archive unchanged. Prior345native and four packaged offline cases retained. Research restoration25and observer28native methods pass; neither is a fresh full-product regression.')
    e['qualification'].update(full_goal_complete=False,temporal_model_qualification=False,temporal_animator_integration=False,independent_usability='unknown',host_shutdown=False,full_responsiveness=False,full_physics_acceptance=False)
    e['limitations']=['Research scheduling passes28native methods and exact known-observation/sample comparisons; product UI and trained-provider cooperative verification remain pending.','Loaded-host counterbalance shows shorter default Rigify worst steps with1.1to9.5percent extra total work by fixture. Two training jobs and overlapping native checks were active.50msfull responsiveness still fails.','Both frozen v26runs still generate training labels; no new trained quality, confirmation or release claim.','Host shutdown access violation and independent code review remain unresolved.','Full original learned motion, generalization, physics/refinement, broader rigs/quadrupeds, optional connector, independent animator and equivalent Cascadeur comparison remain incomplete.']
    ep=gp+'temporal-observer-evidence-v1.json';write(ep,e);obs=read(gp+'temporal-cooperative-observations-v1.json')
    for group in obs.values():
        for row in group.values():row.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
    write(gp+'temporal-observer-observations-v1.json',obs);end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];event='controller-temporal-observer-v1';assert event not in s['work_events'];g.record_work(s,event,duration);result=evaluate(s,obs,ROOT)
    assert result['round']==46 and result['decision']=='iterate' and not result['implementation_progress']['new'] and not result['implementation_progress']['lost'];assert all(not c['regression'] for c in result['categories'].values());assert s['history'][:-1]==old['history']
    assert cp['deadline_unix']==1788981845. and s['contract']['max_goalposts']==50
    write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result),encoding='utf-8')
    cp.update(state_path=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=46,remaining_evaluations=4,decision=result['decision'],stagnant_rounds=s['stagnant_rounds'],evidence=ep,next_controller_monotonic_start=end,pending_document_revisions={},pending_source_revisions={},current_turn_classification='Progress: selective restoration and cooperative observation scheduling pass native exact-source/lifecycle/reference checks and predeclared research latency comparisons.28native methods pass on final research source. Verified wait: both v26training jobs live and frozen; no temporal-model or product qualification.',recorded_at=time.time())
    cp['next_safe_actions']=['Poll existing23370and87876; do not restart or change frozen training inputs.','After primary completes, inspect original development gates and run prepared moving16/stationary16/journey15checks, failure-attribution and edit-stability diagnostics. After both terminal verify exact reproduction.','Run check_projected_selector_cooperative_v26.py only after primary complete; it exercises25existing cooperative/lifecycle/action methods with the actual trained provider. No automatic promotion even if native tests pass.','Current research source has selective restoration plus per-known-pose yields.28native checks and24counterbalanced observer cases passed; performance remains above50ms. Preserve evidence/source versions before further edits.','Keep same full goal:46of50evaluations used,four remain; deadline2026-09-09T19:24:05Z.']
    write(base+'checkpoint-temporal-observer-v1.json',cp)
    live=read(base+'projected-pool-progress-v26.json');live.update(latest_checkpoint=base+'checkpoint-temporal-observer-v1.json',round=46,remaining_evaluations=4,active_jobs=cp['active_jobs'],pending_document_revisions={},recorded_at=time.time());write(base+'projected-pool-progress-v26.json',live)
    print(dict(round=46,remaining_evaluations=4,decision=result['decision'],work_seconds=duration,next_controller_monotonic_start=end,active_sessions=[23370,87876],full_goal_complete=False))
if __name__=='__main__':main()
