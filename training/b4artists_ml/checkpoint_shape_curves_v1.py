"""Record reproducible continuity research without promoting an untested runtime."""
import copy,time
from checkpoint_expanded_goal_v19 import ROOT,read,write,sha,g
from evaluate_milestone_goal_v2 import evaluate

def main():
    base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/'
    cp=read(base+'checkpoint-authored-package-v1.json');prior=cp['state_path'];old=read(prior);s=copy.deepcopy(old);previous=cp['evidence'];e=read(previous)
    dest=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-shape-curves-v1.json';assert not (ROOT/dest).exists();assert cp['round']==54 and s['contract']['max_goalposts']==75 and cp['deadline_unix']==1788981845.
    changed=[n for n,h in e['artifacts'].items() if sha(n)!=h];assert not changed,changed
    comparison=read(res+'shape-curve-comparison-v1.json');assert comparison['complete'] and comparison['exact_numerical_reproduction'] and len(comparison['rows'])==3
    runtime={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in (ROOT/'b4artists_ml').glob('*.py')};assert runtime==read(base+'package-test-v0.18.0.json')['runtime_sha256'] and sha(cp['artifact']['path'])==cp['artifact']['sha256']
    for r in comparison['rows']:assert r['smooth_contact_drift']<=2e-4 and r['priority_matrix_error']==0 and r['angular_jump_reduction']>.96 and r['contact_checks']==2562 and sha(r['scene'])==r['scene_sha256']
    for version in (1,2):
        processes=read(res+f'shape-curve-workflow-v{version}/processes.json');assert len(processes)==3 and all(r['complete'] for r in processes)
        for r in processes:
            d=read(res+f'shape-curve-workflow-v{version}/'+r['profile']+'/report.json');assert d['complete'] and d['source_preserved'] and d['runtime_sha256']==runtime
            assert [row['contact_gate_passed'] for row in d['rows']]==[False,True,True]
    math=read(res+'shape-curve-v2-test_b4artists_ml_shape_curve_v1.json');native=read(res+'shape-curve-v4-test_b4artists_ml_shape_curve_native_v4.json')
    for d,count in [(math,8),(native,7)]:assert d['tests']==count and d['assertions_passed'] and not d['failures'] and not d['errors'] and not d['skipped'] and d['runtime_sha256']==runtime
    inputs=[tr+f'shape_curve_v{i}.py' for i in range(1,5)]+[tr+f'check_shape_curve_workflow_v{i}.py' for i in (1,2)]+[tr+'checkpoint_shape_curves_v1.py',base+'SHAPE-CURVES-RESEARCH-v1.md','tests/test_b4artists_ml_shape_curve_v1.py']+['tests/'+f'test_b4artists_ml_shape_curve_native_v{i}.py' for i in (2,3,4)]
    added=[n for n in inputs if n not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract']);a=copy.deepcopy(s['contract']);b=copy.deepcopy(old['contract']);a.pop('inputs');b.pop('inputs');assert a==b
    s['explicit_revisions'].append(dict(reason='Fixed-key procedural continuity research reduces local crouch velocity jumps while preserving contacts and priorities on3rigs; repeated numerical results exact.15math/nativechecks pass, including unowned spans and reload. No runtime promotion; full endpoint,75ceiling,deadline,floors/history unchanged.',prior_state=prior,prior_sha256=sha(prior),prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],added_inputs=added,recorded_at=time.time()))
    paths=set(e['artifacts'])|set(inputs)|{prior,previous,gp+'priority-continuity-routing-v1.json',res+'shape-curve-comparison-v1.json'}
    for version in (1,2):paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res/f'shape-curve-workflow-v{version}').rglob('*') if p.is_file())
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res).glob('shape-curve-v*.json'))
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/tr/'cache').glob('shape-curve-v*.log'))
    data_plan=read(tr+'temporal_expansion_plan_v19.json');assert all(not (ROOT/tr/'cache'/(n+'.bvh')).exists() for n in data_plan['planned_splits']['confirmation'])
    fp=g.fingerprint(ROOT,s['contract']['inputs']);e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={n:sha(n) for n in sorted(paths)},previous_evidence_recheck=dict(path=previous,sha256=sha(previous),changed_artifacts=[],all_prior_artifacts_unchanged=True),shape_curve_research=dict(comparison=comparison,math_cases=8,native_boundary_cases=7,production_promoted=False))
    e['qualification'].update(priority_continuity_research=True,full_sequence_continuity=False,full_humanoid_workflow=False,temporal_model_qualification=False,independent_usability='unknown',full_goal_complete=False)
    ep=gp+'shape-curves-evidence-v1.json';write(ep,e);obs=read(gp+'authored-package-observations-v1.json')
    for group in obs.values():
        for row in group.values():row.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
    op=gp+'shape-curves-observations-v1.json';write(op,obs);end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];g.record_work(s,'controller-shape-curves-v1',duration);result=evaluate(s,obs,ROOT)
    assert result['round']==55 and result['decision']=='iterate' and s['history'][:-1]==old['history'] and s['floors']==old['floors'] and s['passed_checks']==old['passed_checks'] and s['passed_progress_milestones']==old['passed_progress_milestones']
    result['evidence_transport_note']='Authenticated assessment and independent review remain unavailable; raw continuity/contact evidence retained, full endpoint and prior floors unchanged.';s['history'][-1]=result;write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result)+'\n\n'+result['evidence_transport_note']+'\n',encoding='utf-8')
    cp.update(state_path=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=55,remaining_evaluations=20,evidence=ep,decision='iterate',stagnant_rounds=s['stagnant_rounds'],next_controller_monotonic_start=end,active_jobs=[],recorded_at=time.time(),current_turn_classification='Progress: smoothing/contact order established; local angular velocity jump reduced96.7percent with unchanged contacts and exact priority poses on3rigs;15math/nativecasespass. Runtime0.18.0unchanged.',blocked_audit=dict(consecutive_goal_turns=0,condition=None),work_accounting='Recorded controller-shape-curves-v1 parent interval once; child durations not added.')
    cp['next_safe_actions']=['Broaden authored references to reach/hold and root-yaw transitions before runtime smoothing promotion.','If broader checks support integration, smooth body curves before contacts and validate smoothed corrected output; never apply after-only smoothing blindly.','Use bounded shape_curve_v4 behavior; preserve automatic boundary handles and unsupported sign/axis-angle rejection.','Preserve original full learned goal,75total evaluations,existingdeadline,andpendingindependentanimator assessment.']
    cp['latest_live_observation']={'shape_comparison':dict(session_id=43943,terminal=True,exit_code=0),'bounded_shape_comparison':dict(session_id=9876,terminal=True,exit_code=0)}
    write(base+'checkpoint-shape-curves-v1.json',cp);print(dict(round=55,remaining_evaluations=20,math_cases=8,native_cases=7,rigs=3,prior_artifacts_checked=len(read(previous)['artifacts']),artifacts=len(paths),work_seconds=duration,runtime_unchanged=True,full_goal_complete=False))
if __name__=='__main__':main()
