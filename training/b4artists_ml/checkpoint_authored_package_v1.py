"""Record exact packaged workflow evidence while retaining the full original endpoint."""
import copy,time,zipfile
from checkpoint_expanded_goal_v19 import ROOT,read,write,sha,g
from evaluate_milestone_goal_v2 import evaluate

def main():
    base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/'
    cp=read(base+'checkpoint-authored-package-progress-v1.json');prior=cp['state_path'];old=read(prior);s=copy.deepcopy(old);previous=cp['evidence'];e=read(previous)
    dest=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-authored-package-v1.json';assert not (ROOT/dest).exists()
    assert cp['round']==53 and s['contract']['max_goalposts']==75 and cp['deadline_unix']==1788981845.
    changed=[n for n,h in e['artifacts'].items() if sha(n)!=h];assert set(changed)==set(cp['pending_document_revisions']),changed;versions={}
    for n in changed:
        item=cp['pending_document_revisions'][n];assert sha(item['prior_version'])==item['before_sha256']==e['artifacts'][n] and sha(n)==item['after_sha256'];versions[n]=dict(path=item['prior_version'],sha256=item['before_sha256'])
    meta=read(base+'package-test-v0.18.0.json');smoke=read(res+'authored-runtime-package-v1.json');rows=read(res+'authored-runtime-full-v1-regression.json');runtime={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in (ROOT/'b4artists_ml').glob('*.py')}
    assert meta['ready_for_local_testing'] and meta['runtime_sha256']==smoke['runtime_sha256']==runtime and len(rows)==36 and sum(r['tests'] for r in rows)==369
    for r in rows:assert r['assertions_passed'] and not r['failures'] and not r['errors'] and not r['skipped'] and r['runtime_sha256']==runtime and sha(r['log'])==r['sha256']
    assert smoke['passed'] and smoke['cases']==7 and smoke['offline_guard_self_test'] and not smoke['denied_runtime_calls'] and smoke['package_sha256']==meta['sha256']==cp['artifact']['sha256']==sha(cp['artifact']['path'])
    with zipfile.ZipFile(ROOT/cp['artifact']['path']) as z:assert len(z.namelist())==40 and all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist())
    inputs=[tr+'finalize_authored_runtime_package_v1.py',tr+'checkpoint_authored_package_v1.py',base+'AUTHORED-MOTION-v0.18.0.md'];added=[n for n in inputs if n not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract']);a=copy.deepcopy(s['contract']);b=copy.deepcopy(old['contract']);a.pop('inputs');b.pop('inputs');assert a==b
    s['explicit_revisions'].append(dict(reason='Experimental0.18.0exactarchive nowpasses369nativechecks and7offlineworkflows. Procedural authoredmotion is integrated; learnedmotion,continuousvelocity,currentmodalusability andfullendpoint remainunqualified. Preserve75ceiling,deadline,floors andhistory.',prior_state=prior,prior_sha256=sha(prior),prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],added_inputs=added,preserved_prior_versions=versions,recorded_at=time.time()))
    paths=set(e['artifacts'])|set(inputs)|{prior,previous,base+'package-test-v0.18.0.json',cp['artifact']['path'],res+'authored-runtime-full-v1-regression.json',res+'authored-runtime-package-v1.json',res+'authored-runtime-package-v1-process.json',tr+'cache/authored-runtime-package-v1.log'}
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res/'authored-package-finalization-baseline-v1').rglob('*') if p.is_file())
    for r in rows:paths.add(r['log'].replace('\\','/'));paths.add(res+'authored-runtime-full-v1-'+r['suite']+'.json')
    data_plan=read(tr+'temporal_expansion_plan_v19.json');assert all(not (ROOT/tr/'cache'/(n+'.bvh')).exists() for n in data_plan['planned_splits']['confirmation'])
    fp=g.fingerprint(ROOT,s['contract']['inputs']);e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={n:sha(n) for n in sorted(paths)},previous_evidence_recheck=dict(path=previous,sha256=sha(previous),changed_artifacts=changed,preserved_prior_versions=versions,all_other_prior_artifacts_unchanged=True),authored_runtime_package=dict(metadata=meta,offline=smoke,full_regression_cases=369,host_exit_qualified=False,installed=False,published=False))
    e['qualification'].update(current_source_full_regression=True,current_package_matches_worktree=True,packaged_authored_workflow=True,temporal_model_qualification=False,independent_usability='unknown',full_humanoid_workflow=False,full_goal_complete=False)
    ep=gp+'authored-package-evidence-v1.json';write(ep,e);obs=read(gp+'authored-integration-observations-v1.json')
    for group in obs.values():
        for row in group.values():row.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
    op=gp+'authored-package-observations-v1.json';write(op,obs);end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];g.record_work(s,'controller-authored-package-v1',duration);result=evaluate(s,obs,ROOT)
    assert result['round']==54 and result['decision']=='iterate' and s['history'][:-1]==old['history'] and s['floors']==old['floors'] and s['passed_checks']==old['passed_checks'] and s['passed_progress_milestones']==old['passed_progress_milestones']
    result['evidence_transport_note']='Authenticated goal assessment and independent review remain unavailable. Raw369native and7offline results preserved; original floors and full endpoint unchanged.';s['history'][-1]=result;write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result)+'\n\n'+result['evidence_transport_note']+'\n',encoding='utf-8')
    cp.update(state_path=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=54,remaining_evaluations=21,evidence=ep,decision='iterate',stagnant_rounds=s['stagnant_rounds'],next_controller_monotonic_start=end,active_jobs=[],pending_source_revisions={},pending_document_revisions={},recorded_at=time.time(),work_accounting='Recorded controller-authored-package-v1 parent interval once; child durations not added.',current_turn_classification='Progress: standalone authored-only motion UI/controller integrated;369native and7exact-packageofflinecasespass;0.18.0localtestarchive created. Root/rotationvelocitycontinuity andfulllearnedgoal remainincomplete.',blocked_audit=dict(consecutive_goal_turns=0,condition=None))
    cp['next_safe_actions']=['Address observed priority rotation/root velocity jumps while preserving contacts,priorityposes and source recovery.','Expand humanoid authored references beyond the controlled crouch/recover fixtures, and evaluate correction effort.','Keep existing learned temporal qualification gates and deferred full-goal requirements intact; do not resume unproductive selector fitting.','Preserve75total evaluations and existingdeadline; independent animator assessment remains pending.']
    cp['latest_live_observation']={'native_regression':dict(session_id=53809,terminal=True,exit_code=0),'exact_package':dict(session_id=82474,terminal=True,exit_code=0,native_host_exit=3221225477)}
    write(base+'checkpoint-authored-package-v1.json',cp);print(dict(round=54,remaining_evaluations=21,native_cases=369,offline_cases=7,artifact=cp['artifact']['path'],sha256=meta['sha256'],work_seconds=duration,prior_artifacts_checked=len(read(previous)['artifacts']),artifact_count=len(paths),full_goal_complete=False))
if __name__=='__main__':main()
