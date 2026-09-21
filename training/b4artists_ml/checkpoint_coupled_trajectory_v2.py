"""Record the trajectory research milestone, retaining the original endpoint."""
import copy,time
from checkpoint_expanded_goal_v19 import ROOT,read,write,sha,g
from evaluate_milestone_goal_v2 import evaluate
base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/'
cp=read(base+'checkpoint-ground-velocity-v1.json');old=read(cp['state_path']);s=copy.deepcopy(old);e=read(cp['evidence'])
assert cp['round']==67 and cp['max_goalposts']==100 and cp['deadline_unix']==1789053845
summary=read(res+'coupled-trajectory-reconstruction-v2/summary.json');assert summary['complete'] and summary['sampled_spatial_constraints_passed'] and not summary['method_promoted']
protected=dict(e['artifacts']);protected.update(cp['diagnostic_artifacts']);assert all(sha(p)==h for p,h in protected.items())
assert all(p['complete'] for p in summary['processes'])
assert all(not (ROOT/tr/'cache'/(n+'.bvh')).exists() for n in read(tr+'temporal_expansion_plan_v19.json')['planned_splits']['confirmation'])
inputs=[tr+n for n in ('probe_ground_velocity_v1.py','finalize_ground_velocity_v1.py','solve_coupled_trajectory_v1.py','reconstruct_coupled_trajectory_v2.py','finalize_coupled_trajectory_v2.py','checkpoint_coupled_trajectory_v2.py')]+[base+n for n in ('GROUND-VELOCITY-FEASIBILITY-v1.md','COUPLED-TRAJECTORY-v1.md','COUPLED-TRAJECTORY-RECONSTRUCTION-v2.md')]
added=[p for p in inputs if p not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract'])
a=copy.deepcopy(s['contract']);b=copy.deepcopy(old['contract']);a.pop('inputs');b.pop('inputs');assert a==b
s['explicit_revisions'].append(dict(reason='Joint trajectory optimization and adaptive reconstruction pass881sampled spatial constraints on one frozen BoneForge jump, while angular speed/acceleration remain unqualified. Full endpoint, thresholds, limits, floors and prior artifacts preserved.',prior_state=cp['state_path'],prior_sha256=sha(cp['state_path']),artifact_revisions={},added_inputs=added,prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],recorded_at=time.time()))
paths=set(protected)|set(inputs)|{cp['state_path'],cp['evidence'],base+'checkpoint-coupled-ground-v2.json',base+'checkpoint-ground-velocity-v1.json'}
for folder in ('ground-velocity-feasibility-v1','coupled-trajectory-v1','coupled-trajectory-reconstruction-v2'):
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res/folder).rglob('*') if p.is_file())
fp=g.fingerprint(ROOT,s['contract']['inputs']);e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={p:sha(p) for p in sorted(paths)},previous_evidence_recheck=dict(path=cp['evidence'],sha256=sha(cp['evidence']),all_unrevised_artifacts_unchanged=True,explicit_revisions={}),coupled_trajectory_research=summary)
e['qualification'].update(temporal_model_qualification=False,independent_usability='unknown',full_goal_complete=False)
ep=gp+'coupled-trajectory-evidence-v2.json';write(ep,e);obs=read(gp+'coupled-ground-observations-v2.json')
for group in obs.values():
    for row in group.values():row.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
op=gp+'coupled-trajectory-observations-v2.json';write(op,obs)
end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];assert 0<duration<20000
g.record_work(s,'controller-coupled-trajectory-v2',duration);result=evaluate(s,obs,ROOT)
assert result['round']==68 and result['decision']=='iterate' and s['history'][:-1]==old['history'] and s['floors']==old['floors']
result['evidence_transport_note']='Signed assessment transport and independent usability remain unavailable. Spatial research advances, but the full physics, learned-motion and animator/Cascadeur gates remain unmet. Actual progress is not replaced by formal stagnant-round accounting.'
s['history'][-1]=result;dest=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-coupled-trajectory-v2.json';assert not (ROOT/dest).exists();write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result)+'\n\n'+result['evidence_transport_note']+'\n',encoding='utf-8')
cp.update(state_path=dest,last_evaluated_state=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=68,remaining_evaluations=32,evidence=ep,decision='iterate',stagnant_rounds=s['stagnant_rounds'],next_controller_monotonic_start=end,recorded_at=time.time(),current_turn_classification='Progress: implemented joint-frame trajectory optimization and adaptive actual-rig reconstruction;881sampled spatial checks pass, but measured upper-body speed/acceleration prevents promotion.',previous_turn_classification='Progress: actual-rig leg-only/full-body velocity study established need for nonlinear trajectory constraints.',active_jobs=[],blocked_audit=dict(consecutive_goal_turns=0,condition=None),pending_evaluation=False,work_accounting='Parent interval recorded once from checkpoint67; no child runtimes added.',diagnostic_summary=res+'coupled-trajectory-reconstruction-v2/summary.json')
cp['next_safe_actions']=['Preserve both trajectory prototypes and failed motion-quality evidence. Do not release the spatially passing reconstruction: near-takeoff evaluated hand/control rates approach98rad/s and quarter-frame angular acceleration estimates exceed6000rad/s^2.','Next integrate temporal control-rate/acceleration constraints with the contact/COM solve rather than repairing geometry after smoothing. Distinguish solver limitations from the frozen straight-leg/locked-ankle request; do not claim global infeasibility or silently change its pins/timing.','Use realistic authored or existing licensed actor-motion reference cases alongside this retained stress case before broader product qualification. Do not spend unlimited iterations tuning a single artificial jump.','Full original learned posing/motion, physics/refinement, animator usability, quadrupeds and optional connector requirements remain. Nearby learned fits stay paused; sealed confirmation stays unopened.','Preserve goal ID,100evaluation ceiling,deadline1789053845,unchanged experimental0.19.2and publication identity/approval rules.']
cp['accounting_note']='Formal milestone68/100. Same endpoint, deadline and floors; no active processes.'
write(base+'checkpoint-coupled-trajectory-v2.json',cp)
print(dict(round=68,remaining_evaluations=32,protected_artifacts=len(paths),active_parent_seconds=duration,full_goal_complete=False))
