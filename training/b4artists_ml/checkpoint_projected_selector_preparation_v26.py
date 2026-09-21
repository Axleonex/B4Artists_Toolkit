"""Preserve fitted-risk preparation without claiming trained model quality."""
import copy,time,subprocess,zipfile
from pathlib import Path
from checkpoint_expanded_goal_v19 import ROOT,read,write,sha,g,evaluate

def main():
    base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/'
    cp=read(base+'checkpoint-record-cache-production-v1.json');prior=cp['state_path'];old=read(prior);s=copy.deepcopy(old);previous=cp['evidence'];e=read(previous)
    dest=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-projected-selector-preparation-v26.json';assert not (ROOT/dest).exists()
    pool=read(res+'projected-pool-diagnostic-v26.json');joint=read(res+'projected-pool-joint-risk-v26.json');checks=read(res+'projected-selector-checks-v26.json');pc=read(res+'projected-pool-checks-v26.json')
    assert pool['complete'] and pool['training_only'] and not pool['validation_loaded'] and not pool['confirmation_read']
    assert pool['diagnostic_windows']==466 and pool['diagnostic_gates']['passed'] and joint['diagnostic_gates']['passed']
    assert checks['passed'] and len(checks['checks'])==12 and pc['passed'] and len(pc['checks'])==6
    for proof in (pool,checks,pc):
        for p,h in proof['source_sha256'].items():assert sha(tr+p)==h
    assert not (ROOT/res/'projected_selector_v26/selection_frozen.json').exists(),'Model finished earlier than preparation boundary; inspect it instead of claiming pending'
    progress=read(res+'projected_selector_v26/projection_progress.json');assert progress['processed']>0 and not progress['complete'] and progress['training_only'] and not progress['validation_loaded']
    meta=read(base+'package-test-v0.17.5.json');current={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in (ROOT/'b4artists_ml').glob('*.py')};assert current==meta['runtime_sha256']
    assert sha(cp['artifact']['path'])==cp['artifact']['sha256']==meta['sha256']
    with zipfile.ZipFile(ROOT/cp['artifact']['path']) as z:assert all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist())
    changed=[p for p,h in e['artifacts'].items() if sha(p)!=h];assert set(changed)=={base+n+'.md' for n in ('PROJECT','ROADMAP','REQUIREMENTS')},changed
    versions={}
    for p in changed:
        snapshot=res+'projected-selector-document-baseline-v26/'+Path(p).name;assert sha(snapshot)==e['artifacts'][p];versions[p]=dict(path=snapshot,sha256=sha(snapshot))
    names=['projected_pool_plan_v26.json','projected_pool_v26.py','diagnose_projected_pool_v26.py','check_projected_pool_v26.py','projected_selector_v26.py','check_projected_selector_v26.py','projected_selector_protocol_v26.json','projected_selector_plan_v26.json','train_projected_selector_v26.py','checkpoint_projected_selector_preparation_v26.py']
    inputs=[tr+n for n in names]+[base+'PROJECTED-SELECTOR-PLAN-v26.md'];added=[p for p in inputs if p not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract'])
    s['explicit_revisions'].append(dict(reason='Add training-only fitted proposal coverage,18pre-fit checks and one frozen selector protocol; full corpus label generation has started. No trained-model or validation result claimed. Full original endpoint, floors,50evaluations and extended deadline unchanged.',prior_state=prior,prior_sha256=sha(prior),prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],added_inputs=added,recorded_at=time.time()))
    fp=g.fingerprint(ROOT,s['contract']['inputs']);paths=set(e['artifacts'])|set(inputs)|{prior,previous,gp+'projected-pool-routing-v26.json'}
    paths.update(res+n for n in ['projected-pool-diagnostic-v26.json','projected-pool-joint-risk-v26.json','projected-pool-checks-v26.json','projected-selector-checks-v26.json'])
    for directory in ('projected-selector-prefit-correction-v26','projected-selector-document-baseline-v26'):
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res/directory).rglob('*') if p.is_file())
    # Running chunks/progress are deliberately not hashed as completed evidence.
    plan=read(tr+'temporal_expansion_plan_v19.json');assert all(not (ROOT/tr/'cache'/(c+'.bvh')).exists() for c in plan['planned_splits']['confirmation'])
    args=['git','-c','safe.directory=X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github'];assert subprocess.check_output(args+['log','-1','--format=%H %an <%ae> %cn <%ce>'],cwd=ROOT,text=True).strip()==cp['publication']['head'];assert not subprocess.check_output(args+['diff','--name-only'],cwd=ROOT,text=True).strip();assert not subprocess.check_output(args+['diff','--cached','--name-only'],cwd=ROOT,text=True).strip()
    e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={p:sha(p) for p in sorted(paths)},previous_evidence_recheck=dict(path=previous,sha256=sha(previous),changed_artifacts=changed,preserved_prior_versions=versions,all_other_prior_artifacts_unchanged=True),projected_pool_training_diagnostic=pool,projected_joint_risk_diagnostic=joint,projected_selector_prefit=checks,projected_pool_prefit=pc,projected_selector_training=dict(status='running_labels_only',session_id=23370,output=res+'projected_selector_v26',processed_at_checkpoint=progress['processed'],model_frozen=False,validation_read=False,complete=False),preserved_milestones=old['passed_progress_milestones'],new_passing_milestones=[])
    e['regression'].update(rerun_this_iteration=False,refreshed_cases=0,reused_cases=345,retained_from=previous,note='Exact0.17.5runtime and archive unchanged. Prior345fresh cases and four offline package cases retained;18new research math checks do not constitute another runtime regression.')
    e['qualification'].update(full_goal_complete=False,temporal_model_qualification=False,temporal_animator_integration=False,independent_usability='unknown',host_shutdown=False,full_responsiveness=False,full_physics_acceptance=False)
    e['limitations']=['Diagnostic oracles use hidden training labels and are not deployable learned quality. No corpus model has frozen yet; development/reproduction/actual-rig checks remain pending.','Selector choices may be procedural; learned-expert usage must be reported honestly. All original motion quality and complete animator workflow requirements remain.','Runtime0.17.5unchanged; full responsiveness, host shutdown, physics/refinement, broad rigs/quadrupeds, optional connector, independent usability and equivalent Cascadeur comparison remain incomplete.']
    ep=gp+'projected-selector-preparation-evidence-v26.json';write(ep,e);obs=read(gp+'record-cache-production-observations-v1.json')
    for group in obs.values():
        for proof in group.values():proof.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
    write(gp+'projected-selector-preparation-observations-v26.json',obs);end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];event='controller-projected-selector-preparation-v26';assert event not in s['work_events'];g.record_work(s,event,duration);result=evaluate(s,obs,ROOT)
    assert result['round']==44 and result['decision']=='iterate' and not result['implementation_progress']['new'] and not result['implementation_progress']['lost'];assert all(not c['regression'] for c in result['categories'].values()) and s['history'][:-1]==old['history'];assert cp['deadline_unix']==1788981845. and s['contract']['max_goalposts']==50
    write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result),encoding='utf-8')
    jobs=[dict(session_id=23370,task='Full projected_selector_v26labels/fit/development',output=res+'projected_selector_v26',max_seconds=10800)]
    cp.update(state_path=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=44,remaining_evaluations=6,decision=result['decision'],stagnant_rounds=s['stagnant_rounds'],evidence=ep,active_jobs=jobs,next_controller_monotonic_start=end,current_turn_classification='Progress: training-only466-cohort fitted proposal coverage and joint-risk diagnostics pass;18pre-fit checks pass after preserving exact stationary reference. One protocol frozen and full7358-row run is live. No new learned quality or release claim.',next_safe_actions=['Poll existing session23370; do not restart while live. Full run budgets10800seconds and128MiB generated output; source/protocol and all parents remain frozen.','After terminal completion inspect report, frozen model, exact baselines and old/new/combined gates. Preserve failures; do not retune or open confirmation for an unqualified model.','Run complete independent label/fit/development reproduction in a new output, then original actual-rig moving/stationary checks. Keep0.17.5unchanged until full qualification and integration.','Preserve the full original goal,50evaluations with6remaining, and deadline2026-09-09T19:24:05Z.'],recorded_at=time.time());write(base+'checkpoint-projected-selector-preparation-v26.json',cp)
    live=read(base+'projected-pool-progress-v26.json');live.update(latest_checkpoint=base+'checkpoint-projected-selector-preparation-v26.json',round=44,remaining_evaluations=6,active_jobs=jobs,recorded_at=time.time());write(base+'projected-pool-progress-v26.json',live)
    print(dict(round=44,remaining=6,decision=result['decision'],active_jobs=jobs,work_seconds=duration,next_controller_monotonic_start=end,full_goal_complete=False))
if __name__=='__main__':main()
