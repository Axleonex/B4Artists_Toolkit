"""Record integration milestone and verified ongoing regression without resetting goal."""
import copy,time,ast
from checkpoint_expanded_goal_v19 import ROOT,read,write,sha,g
from evaluate_milestone_goal_v2 import evaluate

def main():
    base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/'
    cp=read(base+'checkpoint-authored-integration-progress-v1.json');prior=cp['state_path'];old=read(prior);s=copy.deepcopy(old);previous=cp['evidence'];e=read(previous)
    dest=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-authored-integration-v1.json';assert not (ROOT/dest).exists()
    assert cp['round']==52 and s['contract']['max_goalposts']==75 and cp['deadline_unix']==1788981845.
    revisions=dict(cp['pending_source_revisions'],**cp['pending_document_revisions']);changed=[n for n,h in e['artifacts'].items() if sha(n)!=h];assert set(changed)==set(revisions)&set(e['artifacts']),changed
    versions={}
    for n,item in revisions.items():
        assert sha(item['prior_version'])==item['before_sha256'] and sha(n)==item['after_sha256']
        if n in e['artifacts']:assert item['before_sha256']==e['artifacts'][n]
        versions[n]=dict(path=item['prior_version'],sha256=item['before_sha256'])
    runtime={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in (ROOT/'b4artists_ml').glob('*.py')};plan=read(tr+'authored_runtime_regression_plan_v1.json');audit=read(res+'authored-runtime-source-audit-v1.json');assert audit['passed'] and runtime==audit['runtime_sha256']==plan['runtime_sha256']
    old_runtime=dict(runtime);old_runtime['b4artists_ml/__init__.py']=versions['b4artists_ml/__init__.py']['sha256']
    assertions=[]
    for name in ('authored-runtime-v1-test_b4artists_ml_temporal_runtime_math_v1.json','authored-runtime-v1-test_b4artists_ml_temporal_runtime_v1.json','authored-preview-v1-test_b4artists_ml_temporal_preview_v1.json'):
        row=read(res+name);assert row['assertions_passed'] and row['tests']==8 and not row['failures'] and not row['errors'] and not row['skipped'] and row['runtime_sha256']==old_runtime;assertions.append(row)
    reports=[]
    for profile in ('boneforge','rigify_basic','rigify_default'):
        r=read(res+'humanoid-workflow-review-v6-runtime/'+profile+'/report.json');assert r['full_humanoid_workflow_passed'] and r['research_reference_max_component_error']==0 and r['runtime_sha256']==old_runtime and sha(r['blend_path'])==r['blend_sha256'];reports.append(r)
    partial=read(res+'authored-runtime-full-v1-regression.json');assert partial and len(partial)<=36
    for r in partial:assert r['assertions_passed'] and not r['errors'] and not r['failures'] and not r['skipped'] and r['runtime_sha256']==runtime and sha(r['log'])==r['sha256']
    frozen=res+'authored-runtime-partial-eval53.json';assert not (ROOT/frozen).exists();write(frozen,dict(rows=partial,expected_suites=36,expected_cases=369,complete=len(partial)==36,live_session_at_previous_observation=53809,recorded_at=time.time()))
    inputs=[n for n in set(runtime)|set(revisions) if n not in s['contract']['inputs']]+[tr+n for n in ('authored_runtime_regression_plan_v1.json','build_humanoid_workflow_review_v6.py','audit_authored_runtime_v1.py','diagnose_authored_rotation_continuity_v1.py','build_authored_runtime_package_v1.py','check_authored_runtime_package_v1.py','checkpoint_authored_integration_v1.py')]+['tests/'+n for n in ('test_b4artists_ml_temporal_runtime_math_v1.py','test_b4artists_ml_temporal_runtime_v1.py','test_b4artists_ml_temporal_preview_v1.py')]
    added=[n for n in inputs if n not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract']);a=copy.deepcopy(s['contract']);b=copy.deepcopy(old['contract']);a.pop('inputs');b.pop('inputs');assert a==b
    s['explicit_revisions'].append(dict(reason='Standalone authored-only trajectory and cancellable product preview integration.24newchecks and3exactnativecomparisons pass; full regression in progress and no package promoted. Original learned endpoint, usability,75ceiling,deadline,floors and history preserved.',prior_state=prior,prior_sha256=sha(prior),prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],added_inputs=added,preserved_prior_versions=versions,recorded_at=time.time()))
    paths=set(e['artifacts'])|set(inputs)|set(runtime)|{prior,previous,frozen,gp+'authored-integration-routing-v1.json',gp+'authored-integration-review-v1.json',res+'authored-runtime-source-audit-v1.json'}
    for folder in ('humanoid-workflow-review-v6-runtime','authored-integration-baseline-v1','authored-rotation-continuity-v1'):
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res/folder).rglob('*') if p.is_file())
    for prefix in ('authored-runtime-v1','authored-preview-v1'):
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res).glob(prefix+'*.json'));paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/tr/'cache').glob(prefix+'*.log'))
    for r in partial:paths.add(r['log'].replace('\\','/'));paths.add(res+'authored-runtime-full-v1-'+r['suite']+'.json')
    assert sha(cp['artifact']['path'])==cp['artifact']['sha256'];data_plan=read(tr+'temporal_expansion_plan_v19.json');assert all(not (ROOT/tr/'cache'/(n+'.bvh')).exists() for n in data_plan['planned_splits']['confirmation'])
    fp=g.fingerprint(ROOT,s['contract']['inputs']);e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={n:sha(n) for n in sorted(paths)},previous_evidence_recheck=dict(path=previous,sha256=sha(previous),changed_artifacts=changed,preserved_prior_versions=versions,all_other_prior_artifacts_unchanged=True),authored_runtime_integration=dict(new_assertions=assertions,exact_research_parity_rigs=3,source_audit=audit,partial_regression=frozen,procedural_only=True,ui_operator_backend_tested=True,modal_viewport_assessment='unverified'))
    e['qualification'].update(authored_procedural_ui_option=True,temporal_animator_integration='procedural_only_headless_operator_checks',current_source_full_regression=len(partial)==36,current_package_matches_worktree=False,full_humanoid_workflow=False,temporal_model_qualification=False,independent_usability='unknown',full_goal_complete=False)
    ep=gp+'authored-integration-evidence-v1.json';write(ep,e);obs=read(gp+'authored-context-observations-v1.json')
    for group in obs.values():
        for row in group.values():row.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
    op=gp+'authored-integration-observations-v1.json';write(op,obs);end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];g.record_work(s,'controller-authored-integration-v1',duration);result=evaluate(s,obs,ROOT)
    assert result['round']==53 and result['decision']=='iterate' and s['history'][:-1]==old['history'] and s['floors']==old['floors'] and s['passed_checks']==old['passed_checks'] and s['passed_progress_milestones']==old['passed_progress_milestones']
    result['evidence_transport_note']='Authenticated assessments and independent review remain unavailable. Raw implementation evidence is preserved separately; original floors and full endpoint unchanged.';s['history'][-1]=result;write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result)+'\n\n'+result['evidence_transport_note']+'\n',encoding='utf-8')
    cp.update(state_path=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=53,remaining_evaluations=22,evidence=ep,decision='iterate',stagnant_rounds=s['stagnant_rounds'],next_controller_monotonic_start=end,pending_source_revisions={},pending_document_revisions={},recorded_at=time.time(),work_accounting='Recorded controller-authored-integration-v1 parent interval once; child time not added.')
    cp['next_safe_actions']=['Observe native regression session53809; never restart on an observation timeout.','After all369casespass on unchangedsource, build and offline-test exact0.18.0archive.','Preserve derivative findings; improve rotation continuity and broader humanoid references next.','Preservefullgoal,75totalceiling,existingdeadline and pending independentanimator assessment.']
    write(base+'checkpoint-authored-integration-v1.json',cp);print(dict(round=53,remaining_evaluations=22,partial_suites=len(partial),partial_cases=sum(r['tests'] for r in partial),new_assertions=24,exact_comparison_rigs=3,work_seconds=duration,full_goal_complete=False))
if __name__=='__main__':main()
