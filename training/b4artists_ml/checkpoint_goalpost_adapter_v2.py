"""Finish the pending goalpost using the canonical unknown-evidence semantics."""
import copy,time,subprocess,zipfile
from checkpoint_expanded_goal_v19 import ROOT,read,write,sha,g
from evaluate_milestone_goal_v2 import evaluate

def main():
    base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/'
    cp=read(base+'checkpoint-temporal-observer-pending-v1.json');prior=cp['state_path'];old=read(prior);s=copy.deepcopy(old);previous=cp['evidence'];e=read(previous)
    dest=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-goalpost-adapter-v2.json';assert not (ROOT/dest).exists()
    assert len(s['history'])==45 and s['pending_evaluation'] and cp['remaining_evaluations']==5
    proof=read(res+'goalpost-adapter-checks-v2.json');assert proof['passed'] and proof['tests']==7 and proof['no_signing_material_created'] and proof['no_shared_code_changed']
    for n,h in proof['source_sha256'].items():assert sha(n)==h,n
    assert all(sha(n)==h for n,h in e['artifacts'].items())
    inputs=[tr+'evaluate_milestone_goal_v2.py',tr+'checkpoint_goalpost_adapter_v2.py','tests/test_b4artists_ml_goal_progress_v2.py']
    added=[n for n in inputs if n not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract'])
    a=copy.deepcopy(s['contract']);b=copy.deepcopy(old['contract']);a.pop('inputs');b.pop('inputs');assert a==b
    s['explicit_revisions'].append(dict(reason='Project-only compatibility with the current canonical signed-assessment interface. Missing host-authenticated receipts are unknown, never forged or self-signed. Preserve full endpoint, original floors, accepted historical results,50evaluation ceiling and extended deadline.',prior_state=prior,prior_sha256=sha(prior),prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],added_inputs=added,recorded_at=time.time()))
    fp=g.fingerprint(ROOT,s['contract']['inputs']);paths=set(e['artifacts'])|set(inputs)|{prior,previous,gp+'goalpost-adapter-routing-v2.json',res+'goalpost-adapter-checks-v2.json'}
    progress=[]
    for name in ('projected_selector_v26','projected_selector_v26_repeat'):
        row=read(res+name+'/projection_progress.json');assert row['training_only'] and not row['validation_loaded'] and not row['complete']
        for n,h in row['source_sha256'].items():assert sha(tr+n)==h,n
        progress.append(dict(output=res+name,processed=row['processed'],total=row['total'],model_frozen=False,validation_loaded=False))
    meta=read(base+'package-test-v0.17.5.json');runtime={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in (ROOT/'b4artists_ml').glob('*.py')};assert runtime==meta['runtime_sha256'] and sha(cp['artifact']['path'])==meta['sha256']==cp['artifact']['sha256']
    args=['git','-c','safe.directory=X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github'];assert subprocess.check_output(args+['log','-1','--format=%H %an <%ae> %cn <%ce>'],cwd=ROOT,text=True).strip()==cp['publication']['head'];assert not subprocess.check_output(args+['diff','--name-only'],cwd=ROOT,text=True).strip();assert not subprocess.check_output(args+['diff','--cached','--name-only'],cwd=ROOT,text=True).strip()
    e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={n:sha(n) for n in sorted(paths)},previous_evidence_recheck=dict(path=previous,sha256=sha(previous),changed_artifacts=[],all_prior_artifacts_unchanged=True),goalpost_adapter=proof,projected_selector_training=dict(status='both_runs_generating_labels',active_sessions=[23370,87876],runs=progress,complete=False),formal_assessment=dict(status='Legacy hash-bound observations lack the current host-signed goal-assessment.v1 envelopes; the canonical evaluator will mark them unknown. Raw native test/benchmark evidence remains preserved. No signing state or receipt producer was invented.',prior_accepted_evaluations=45,all_prior_floors_preserved=True,software_regression_claim=False))
    ep=gp+'goalpost-adapter-evidence-v2.json';write(ep,e);obs=read(gp+'temporal-observer-observations-v1.json')
    for group in obs.values():
        for row in group.values():row.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
    write(gp+'goalpost-adapter-observations-v2.json',obs);end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];event='controller-goalpost-adapter-v2';assert event not in s['work_events'];g.record_work(s,event,duration)
    result=evaluate(s,obs,ROOT)
    assert result['round']==46 and result['decision']=='iterate';assert s['history'][:-1]==old['history'];assert s['floors']==old['floors'] and s['passed_checks']==old['passed_checks'] and s['passed_progress_milestones']==old['passed_progress_milestones']
    assert all(v=='unknown' for v in result['endpoint'].values()) and all(v=='unknown' for c in result['categories'].values() for v in c['checks'].values())
    assert not result['implementation_progress']['accepted'] and cp['deadline_unix']==1788981845. and s['contract']['max_goalposts']==50
    result['evidence_transport_note']='Current canonical signed-assessment enforcement cannot authenticate legacy project observation envelopes. Unknown checks/flagged regressions are evidence availability failures; raw tests and all historical floors/results are preserved. No measured product regression is asserted.'
    s['history'][-1]=result;write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result)+'\n\n'+result['evidence_transport_note']+'\n')
    cp.update(state_path=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=46,remaining_evaluations=4,evidence=ep,decision=result['decision'],pending_evaluation=False,assessment_receipts_unavailable=True,next_controller_monotonic_start=end,stagnant_rounds=s['stagnant_rounds'],recorded_at=time.time(),current_turn_classification='Progress: project-only evaluator compatibility fixed and seven fail-closed tests pass. Evaluation46completed under current canonical receipt enforcement; unsigned observations unknown, all prior floors/history retained. Verified wait: both frozen model runs still active.')
    cp['next_safe_actions']=['Poll existing23370and87876; no restart or frozen source changes.','After primary completion inspect original development gates and run prepared moving16,stationary16,journey15and cooperative25native provider checks plus failure/edit-stability diagnostics; after both terminal verify exact reproduction.','Use evaluate_milestone_goal_v2 for current canonical API. Host-signed goal-assessment.v1 producer remains unavailable: do not forge receipts, sign self-assessments, change shared governance, reset floors or mislabel unknown as passing.','Continue original full goal:46of50evaluations used,four remain; deadline2026-09-09T19:24:05Z.']
    write(base+'checkpoint-goalpost-adapter-v2.json',cp)
    live=read(base+'projected-pool-progress-v26.json');live.update(latest_checkpoint=base+'checkpoint-goalpost-adapter-v2.json',round=46,remaining_evaluations=4,pending_evaluation=False,assessment_receipts_unavailable=True,recorded_at=time.time());write(base+'projected-pool-progress-v26.json',live)
    print(dict(round=46,remaining_evaluations=4,decision=result['decision'],all_current_observations_unknown=True,prior_floors_preserved=True,work_seconds=duration,next_controller_monotonic_start=end,active_sessions=[23370,87876],full_goal_complete=False))
if __name__=='__main__':main()
