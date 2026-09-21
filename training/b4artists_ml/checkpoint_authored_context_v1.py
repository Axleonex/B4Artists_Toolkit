"""Checkpoint authored-context experiment without weakening the full goal."""
import copy,time
from checkpoint_expanded_goal_v19 import ROOT,read,write,sha,g
from evaluate_milestone_goal_v2 import evaluate

def main():
    base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/'
    cp=read(base+'checkpoint-humanoid-workflow-v1.json');prior=cp['state_path'];old=read(prior);s=copy.deepcopy(old);previous=cp['evidence'];e=read(previous)
    dest=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-authored-context-v1.json';assert not (ROOT/dest).exists()
    assert cp['round']==51 and s['contract']['max_goalposts']==75 and cp['deadline_unix']==1788981845.
    changed=[n for n,h in e['artifacts'].items() if sha(n)!=h];assert not changed,changed
    summary=read(res+'authored-context-comparison-v1.json');assert summary['complete'] and len(summary['rows'])==9
    good=[r for r in summary['rows'] if r['variant']=='v5-slerp'];assert len(good)==3
    for r in good:assert r['contacts_passed'] and r['source_restored'] and r['priorities_preserved'] and r['contact_max_after']<=2e-4 and sha(r['scene'])==r['sha256']
    runtime={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in (ROOT/'b4artists_ml').glob('*.py')}
    checked=[read(res+'authored-context-v1-test_b4artists_ml_authored_context_v1.json'),read(res+'authored-context-v1-evaluated-edit-test_b4artists_ml_authored_cooperative_v1.json')]
    for r in checked:assert r['tests']==8 and r['assertions_passed'] and not r['failures'] and not r['errors'] and not r['skipped'] and r['runtime_sha256']==runtime
    reloaded=[read(res+'authored-review-reload-v1/'+profile+'.json') for profile in ('boneforge','rigify_basic','rigify_default')]
    for r in reloaded:assert r['complete'] and r['discard_passed'] and r['keep_restore_passed'] and r['source_scene_unchanged'] and r['contact_checks']==642 and r['max_contact_drift']<=2e-4 and r['max_contact_rotation']<=.001 and r['runtime_sha256']==runtime
    for variant in ('source','slerp'):
        processes=read(res+'humanoid-workflow-review-v5-'+variant+'/processes.json');assert len(processes)==3 and all(r['complete'] for r in processes)
    inputs=[tr+n for n in ('authored_context_v1.py','temporal_authored_cooperative_v1.py','build_humanoid_workflow_review_v5.py','verify_authored_review_reload_v1.py','checkpoint_authored_context_v1.py')]+['tests/test_b4artists_ml_authored_context_v1.py','tests/test_b4artists_ml_authored_cooperative_v1.py',base+'AUTHORED-CONTEXT-WORKFLOW-v1.md']
    added=[n for n in inputs if n not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract']);a=copy.deepcopy(s['contract']);b=copy.deepcopy(old['contract']);a.pop('inputs');b.pop('inputs');assert a==b
    s['explicit_revisions'].append(dict(reason='Add authored-context procedural experiment and native reload evidence. Three controlled humanoid crouch/recover contact workflows pass with unchanged gates; learned quality and independent usability remain unqualified. Same goal, endpoint,75ceiling,deadline,floors and history.',prior_state=prior,prior_sha256=sha(prior),prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],added_inputs=added,recorded_at=time.time()))
    paths=set(e['artifacts'])|set(inputs)|{prior,previous,gp+'authored-context-routing-v1.json',res+'authored-context-comparison-v1.json',res+'authored-context-native-v1-processes.json'}
    for folder in ('humanoid-workflow-review-v5-source','humanoid-workflow-review-v5-slerp','authored-review-reload-v1'):
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res/folder).rglob('*') if p.is_file())
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res).glob('authored-context-v1*') if p.is_file())
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/tr/'cache').glob('authored-context-v1*.log'))
    assert sha(cp['artifact']['path'])==cp['artifact']['sha256'];plan=read(tr+'temporal_expansion_plan_v19.json');assert all(not (ROOT/tr/'cache'/(n+'.bvh')).exists() for n in plan['planned_splits']['confirmation'])
    fp=g.fingerprint(ROOT,s['contract']['inputs']);e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={n:sha(n) for n in sorted(paths)},previous_evidence_recheck=dict(path=previous,sha256=sha(previous),changed_artifacts=[],all_prior_artifacts_unchanged=True),authored_context_workflow=dict(comparison=summary,numerical_cases=8,lifecycle_cases=8,reopened_scenes=reloaded,procedural_only=True,full_goal_complete=False))
    e['qualification'].update(controlled_authored_crouch_workflow=True,full_humanoid_workflow=False,current_source_full_regression=False,current_package_matches_worktree=False,temporal_model_qualification=False,temporal_animator_integration=False,independent_usability='unknown',full_goal_complete=False)
    ep=gp+'authored-context-evidence-v1.json';write(ep,e);obs=read(gp+'humanoid-workflow-observations-v1.json')
    for group in obs.values():
        for row in group.values():row.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
    op=gp+'authored-context-observations-v1.json';write(op,obs);end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];g.record_work(s,'controller-authored-context-v1',duration);result=evaluate(s,obs,ROOT)
    assert result['round']==52 and result['decision']=='iterate' and s['history'][:-1]==old['history'] and s['floors']==old['floors'] and s['passed_checks']==old['passed_checks'] and s['passed_progress_milestones']==old['passed_progress_milestones']
    result['evidence_transport_note']='Authenticated assessments remain unavailable. Raw16newchecks,3passingcontrolledscenesand3freshreloads are retained separately; original floors and endpoint remain unchanged.';s['history'][-1]=result;write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result)+'\n\n'+result['evidence_transport_note']+'\n',encoding='utf-8')
    cp.update(native_goal_status='active_verified_2026-09-09',state_path=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=52,remaining_evaluations=23,evidence=ep,decision='iterate',stagnant_rounds=s['stagnant_rounds'],next_controller_monotonic_start=end,active_jobs=[],current_turn_classification='Progress: authored context removes crouch overshoot; authored rotations allow all3controlledrigstopasscontacts;16newchecks and3freshreloads pass. No learned/UI/package promotion.',recorded_at=time.time(),work_accounting='Recorded controller-authored-context-v1 parent interval once; child durations not added.',blocked_audit=dict(consecutive_goal_turns=0,condition=None))
    cp['next_safe_actions']=['Validate authored-only sampling without unused source neighbors and retain source-context mode explicitly for existing animation.','Assess rotation continuity and broader authored humanoid motion before product-facing scheduling integration.','Keep the contact-key fix isolated until suitable full regression and package validation.','Preserve75total evaluations,existingdeadline,anddeferredfull-goalrequirements; independent animator input remains pending.']
    cp['authored_context']=dict(evidence=ep,controlled_scenes_passed=3,numerical_tests=8,lifecycle_tests=8,reload_scenes=3,ui_integrated=False,learned=False)
    write(base+'checkpoint-authored-context-v1.json',cp);print(dict(round=52,max_goalposts=75,remaining_evaluations=23,controlled_scenes_passed=3,new_tests=16,reload_scenes=3,full_goal_complete=False,work_seconds=duration,prior_artifacts_verified=len(read(previous)['artifacts']),artifacts=len(paths)))
if __name__=='__main__':main()
