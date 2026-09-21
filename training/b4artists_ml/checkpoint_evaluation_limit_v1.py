"""Record the final authorized evaluation; never redefine completion or limits."""
import copy,time,subprocess
from checkpoint_expanded_goal_v19 import ROOT,read,write,sha,g
from evaluate_milestone_goal_v2 import evaluate

def main():
    base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/'
    cp=read(base+'checkpoint-tail-risk-selector-v28.json');prior=cp['state_path'];old=read(prior);s=copy.deepcopy(old);previous=cp['evidence'];e=read(previous)
    dest=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-evaluation-limit-v1.json';assert not (ROOT/dest).exists()
    assert cp['round']==49 and cp['remaining_evaluations']==1 and cp['deadline_unix']==1788981845. and s['contract']['max_goalposts']==50 and not cp['active_jobs']
    ap=res+'goal-limit-delivery-audit-v1.json';audit=read(ap);assert audit['audit_completed'] and not audit['full_goal_complete'] and audit['prior_state']['path']==prior and audit['prior_state']['sha256']==sha(prior) and audit['prior_evidence']['sha256']==sha(previous)
    assert audit['prior_evidence']['verified_artifact_count']==2750 and audit['all_tracked_validation_jobs_terminal'] and len(audit['endpoint_rows'])==10
    changed=[n for n,h in e['artifacts'].items() if sha(n)!=h];assert set(changed)=={base+'PROJECT.md',base+'ROADMAP.md',base+'REQUIREMENTS.md'},changed
    versions={}
    for n in changed:
        p=res+'goal-limit-document-baseline-v1/'+n.split('/')[-1];assert sha(p)==e['artifacts'][n];versions[n]=dict(path=p,sha256=sha(p))
    for row in audit['endpoint_rows']:
        for n,h in row['evidence'].items():assert sha(versions[n]['path'] if n in versions else n)==h,n
    assert sha(audit['package']['path'])==audit['package']['sha256']==cp['artifact']['sha256']
    for n,h in audit['protected_addons_sha256'].items():assert sha(n)==h,n
    plan=read(tr+'temporal_expansion_plan_v19.json');assert all(not (ROOT/tr/'cache'/(n+'.bvh')).exists() for n in plan['planned_splits']['confirmation'])
    args=['git','-c','safe.directory=X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github'];assert subprocess.check_output(args+['log','-1','--format=%H %an <%ae> %cn <%ce>'],cwd=ROOT,text=True).strip()==cp['publication']['head'];assert not subprocess.check_output(args+['diff','--name-only'],cwd=ROOT,text=True).strip();assert not subprocess.check_output(args+['diff','--cached','--name-only'],cwd=ROOT,text=True).strip()
    inputs=[tr+'checkpoint_evaluation_limit_v1.py',tr+'audit_goal_limit_v1.py',base+'EVALUATION-LIMIT-HANDOFF.md'];added=[n for n in inputs if n not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract'])
    a=copy.deepcopy(s['contract']);b=copy.deepcopy(old['contract']);a.pop('inputs');b.pop('inputs');assert a==b
    s['explicit_revisions'].append(dict(reason='Final full-endpoint/delivery/evidence audit at user50evaluationceiling. Endpoint remains unmet; preserve original thresholds, historical floors and existing extended deadline. No new model or release promotion.',prior_state=prior,prior_sha256=sha(prior),prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],added_inputs=added,preserved_prior_versions=versions,recorded_at=time.time()))
    paths=set(e['artifacts'])|set(inputs)|{ap,prior,previous,base+'checkpoint-tail-risk-selector-v28.json',base+'tail-risk-progress-v28.json'}|{v['path'] for v in versions.values()}
    fp=g.fingerprint(ROOT,s['contract']['inputs']);e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={n:sha(n) for n in sorted(paths)},previous_evidence_recheck=dict(path=previous,sha256=sha(previous),changed_artifacts=changed,preserved_prior_versions=versions,all_other_prior_artifacts_unchanged=True),full_endpoint_delivery_audit=audit)
    e['qualification'].update(full_goal_complete=False,temporal_model_qualification=False,temporal_animator_integration=False,current_package_ui='unverified',full_responsiveness=False,independent_usability='unknown')
    e['limits']=dict(max_goalposts=50,final_authorized_round=50,deadline_unix=1788981845.,reason='Evaluation ceiling reached before time ceiling; user decision needed to extend evaluations.',endpoint_unchanged=True,thresholds_unchanged=True)
    ep=gp+'evaluation-limit-evidence-v1.json';write(ep,e);obs=read(gp+'tail-risk-selector-observations-v28.json')
    for group in obs.values():
        for row in group.values():row.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
    op=gp+'evaluation-limit-observations-v1.json';write(op,obs);end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];assert duration>0;g.record_work(s,'controller-evaluation-limit-v1',duration);result=evaluate(s,obs,ROOT)
    assert result['round']==50 and result['decision']=='checkpoint' and result['reason']=='goalpost limit reached' and s['status']=='checkpoint'
    assert s['history'][:-1]==old['history'] and s['floors']==old['floors'] and s['passed_checks']==old['passed_checks'] and s['passed_progress_milestones']==old['passed_progress_milestones']
    result['evidence_transport_note']='Canonical signed-assessment envelopes remain unavailable; unknown formal observations do not erase earlier evidence/floors. Actual scope and quality also remain incomplete. Stop at user50evaluationceiling, not completion.';s['history'][-1]=result
    write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result)+'\n\n'+result['evidence_transport_note']+'\n')
    cp.update(state_path=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=50,remaining_evaluations=0,evidence=ep,decision='checkpoint',reason='goalpost limit reached',shared_state_status='checkpoint',native_goal_status='active',next_controller_monotonic_start=end,pending_document_revisions={},pending_source_revisions={},pending_evaluation=False,active_jobs=[],stagnant_rounds=s['stagnant_rounds'],recorded_at=time.time(),current_turn_classification='Progress: final full-endpoint audit rehashed2750prior artifacts, exact36file experimental package and retained345native plus4offlinecases. All tracked jobs terminal; original full goal incomplete. Checkpoint at authorized50evaluationlimit.',blocked_audit=dict(consecutive_goal_turns=1,condition='Authorized50evaluationceiling reached; requires explicit extension before new evaluated development.'))
    cp['next_safe_actions']=['Do not launch new development or evaluate round51 without explicit extension of the evaluation allowance. The time extension does not raise the50ceiling.','Resume from this goal ID/state/evidence and retain original endpoint, thresholds, floors, data splits and deadline unless explicitly revised.','Use EVALUATION-LIMIT-HANDOFF.md for the full requirements audit and next research/workflow priorities. Fresh confirmation remains sealed; no temporal model is qualified.','No independent animator or equivalent Cascadeur comparison has been supplied. No parity claim, production promotion, installation or publication.','Native goal remains incomplete; no complete lifecycle call was issued. Shared state is checkpointed at the declared limit.']
    cp['final_delivery_audit']=dict(path=ap,sha256=sha(ap),handoff=base+'EVALUATION-LIMIT-HANDOFF.md',handoff_sha256=sha(base+'EVALUATION-LIMIT-HANDOFF.md'),artifact_count=len(e['artifacts']),all_tracked_jobs_terminal=True)
    write(base+'checkpoint-evaluation-limit-v1.json',cp)
    print(dict(round=50,remaining_evaluations=0,decision=result['decision'],reason=result['reason'],full_goal_complete=False,verified_prior_artifacts=2750,final_artifacts=len(e['artifacts']),historical_floors_preserved=True,work_seconds=duration,next_controller_monotonic_start=end,state=dest,checkpoint=base+'checkpoint-evaluation-limit-v1.json'))
if __name__=='__main__':main()
