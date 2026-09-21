"""Evaluate the coupled-ground research milestone without changing the goal."""
import copy,time
from checkpoint_expanded_goal_v19 import ROOT,read,write,sha,g
from evaluate_milestone_goal_v2 import evaluate
base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/'
cp=read(base+'checkpoint-grounded-jump-diagnostic-v1.json');old=read(cp['state_path']);s=copy.deepcopy(old);e=read(cp['evidence'])
assert cp['round']==66 and cp['max_goalposts']==100 and cp['deadline_unix']==1789053845
summary=read(res+'coupled-ground-continuity-v2/summary.json');assert summary['complete'] and summary['pointwise_samples']==468 and not summary['method_promoted']
protected=dict(e['artifacts']);protected.update(cp['diagnostic_artifacts'])
changed=[p for p,h in protected.items() if sha(p)!=h];assert not changed,changed
for group in summary['processes'].values():assert len(group)==3 and all(p['complete'] for p in group)
assert all(not (ROOT/tr/'cache'/(n+'.bvh')).exists() for n in read(tr+'temporal_expansion_plan_v19.json')['planned_splits']['confirmation'])
inputs=[tr+n for n in ('probe_coupled_ground_v1.py','probe_coupled_ground_continuity_v2.py','finalize_coupled_ground_v2.py','checkpoint_coupled_ground_v2.py','diagnose_grounded_jump_v1.py','finalize_grounded_jump_v1.py')]+[base+n for n in ('GROUNDED-JUMP-DIAGNOSTIC-v1.md','COUPLED-GROUND-FEASIBILITY-v1.md','COUPLED-GROUND-CONTINUITY-v2.md')]
added=[p for p in inputs if p not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract'])
a=copy.deepcopy(s['contract']);b=copy.deepcopy(old['contract']);a.pop('inputs');b.pop('inputs');assert a==b
s['explicit_revisions'].append(dict(reason='Three actual-rig grounded-jump failures measured;468coupled spatial samples pass but dense angular secants expose unqualified temporal behavior. Preserve full endpoint, thresholds, limits, floors, sealed confirmation and production.',prior_state=cp['state_path'],prior_sha256=sha(cp['state_path']),artifact_revisions={},added_inputs=added,prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],recorded_at=time.time()))
paths=set(protected)|set(inputs)|{cp['state_path'],cp['evidence'],base+'checkpoint-visible-state-package-v1.json',base+'checkpoint-grounded-jump-diagnostic-v1.json'}
for folder in ('coupled-ground-feasibility-v1','coupled-ground-continuity-v2'):
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res/folder).rglob('*') if p.is_file())
fp=g.fingerprint(ROOT,s['contract']['inputs']);e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={p:sha(p) for p in sorted(paths)},previous_evidence_recheck=dict(path=cp['evidence'],sha256=sha(cp['evidence']),all_unrevised_artifacts_unchanged=True,explicit_revisions={}),coupled_ground_research=summary)
e['qualification'].update(temporal_model_qualification=False,independent_usability='unknown',full_goal_complete=False)
ep=gp+'coupled-ground-evidence-v2.json';write(ep,e);obs=read(gp+'visible-state-package-observations-v1.json')
for group in obs.values():
    for row in group.values():row.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
op=gp+'coupled-ground-observations-v2.json';write(op,obs)
end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];assert 0<duration<20000
g.record_work(s,'controller-coupled-ground-v2',duration);result=evaluate(s,obs,ROOT)
assert result['round']==67 and result['decision']=='iterate' and s['history'][:-1]==old['history'] and s['floors']==old['floors']
result['evidence_transport_note']='Signed assessment transport and independent usability remain unavailable. Grounded workflow remains rejected; spatial feasibility does not pass temporal physics or learned motion. Actual research progress is recorded separately from formal stagnant rounds.'
s['history'][-1]=result;dest=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-coupled-ground-v2.json';assert not (ROOT/dest).exists();write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result)+'\n\n'+result['evidence_transport_note']+'\n',encoding='utf-8')
cp.update(state_path=dest,last_evaluated_state=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=67,remaining_evaluations=33,evidence=ep,decision='iterate',stagnant_rounds=s['stagnant_rounds'],next_controller_monotonic_start=end,recorded_at=time.time(),current_turn_classification='Progress: research solver meets468spatial pose checks; dense boundary analysis exposes angular-speed growth and prevents incorrect temporal promotion.',previous_turn_classification='Progress: completed three-rig grounded-jump diagnostic, measured foot drift and preserved source.',active_jobs=[],blocked_audit=dict(consecutive_goal_turns=0,condition=None),pending_evaluation=False,work_accounting='Parent interval recorded once from checkpoint66; no child runtimes added.',diagnostic_summary=res+'coupled-ground-continuity-v2/summary.json')
cp['next_safe_actions']=['Retain the successful alternating contact/COM projection as a research building block; do not bake it or remove the production overlap rejection.','Investigate temporally constrained ground-transition feasibility. BoneForge near-straight endpoint angular secants increase sharply; Rigify remains near39rad/s. Distinguish restricted-solver failure from incompatible authored contact/timing, without silently moving pins or contact boundaries.','Frozen whole-goal requirements remain: genuine learned posing/motion improvement, contacts/physics/refinement, full animator workflows, quadrupeds and optional connector. Nearby learned fits remain paused; use diagnosed hypotheses and preserve sealed confirmation.','Preserve full goal ID,100evaluation cap,deadline1789053845,production0.19.2archive and publication identity/approval rules.']
cp['accounting_note']='Formal milestone67/100 recorded; same endpoint and deadline. No active processes.'
write(base+'checkpoint-coupled-ground-v2.json',cp)
print(dict(round=67,remaining_evaluations=33,protected_artifacts=len(paths),active_parent_seconds=duration,full_goal_complete=False))
