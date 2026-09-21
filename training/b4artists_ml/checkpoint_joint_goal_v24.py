"""Record fixed per-joint mixture evidence under the same full active endpoint."""
import copy,time,subprocess,zipfile
from pathlib import Path
from checkpoint_expanded_goal_v19 import ROOT,read,sha,write,g,evaluate

def main():
 base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/';prefix='01a073fe-c240-70c0-b5cd-fe9653aac60e-'
 prior=gp+prefix+'curve-confidence-v23.json';dest=gp+prefix+'joint-mixture-v24.json';assert not (ROOT/dest).exists()
 old=read(prior);s=copy.deepcopy(old);cp=read(base+'checkpoint-curve-confidence-v23.json');prev_ev=gp+'curve-confidence-evidence-v23.json';e=read(prev_ev)
 model=read(res+'joint_mixture_v24/report.json');repro=read(res+'joint-mixture-reproduction-v24.json');verification=read(res+'joint-experiment-verification-v24.json');attribution=read(res+'joint-failure-attribution-v24.json');assert verification['passed'] and verification['pre_fit_checks']==18 and repro['passed']
 for n,h in repro['identical_sha256'].items():assert sha(res+'joint_mixture_v24/'+n)==h==sha(res+'joint_mixture_v24_repeat/'+n)
 a=copy.deepcopy(model);b=read(res+'joint_mixture_v24_repeat/report.json')
 for report in [a,b]:report.pop('runtime');report['model_files']={Path(k).name:v for k,v in report['model_files'].items()}
 assert a==b
 previous=read(res+'curve_mixture_v23/report.json');assert model['protocol']['gates']==previous['protocol']['gates'] and model['protocol']['projection']==previous['protocol']['projection']
 for part in ['old_validation','new_validation','combined']:
  for name in model['protocol']['baselines']:assert model['partition_reports'][part][name]==previous['partition_reports'][part][name]
 for name,h in model['source_sha256'].items():assert sha(tr+name)==h
 plan=read(tr+'temporal_expansion_plan_v19.json');assert all(not (ROOT/tr/'cache'/(c+'.bvh')).exists() for c in plan['planned_splits']['confirmation']);assert not model['confirmation_read']
 moving=read(res+'joint-mixture-host-v24.json');stationary=read(res+'stationary-joint-host-v24.json');meta=read(base+'package-test-v0.17.4.json')
 current={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in (ROOT/'b4artists_ml').glob('*.py')};assert current==meta['runtime_sha256']==moving['runtime_sha256']==stationary['runtime_sha256']
 for host in [moving,stationary]:assert host['complete'] and host['passed'] and len(host['rows'])==16 and host['model_sha256']==model['selection']['best_learned_sha256']
 assert sha('releases/b4artists_ml_v0.17.4.zip')==meta['sha256']
 with zipfile.ZipFile(ROOT/'releases/b4artists_ml_v0.17.4.zip') as z:assert all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist())
 changed=[p for p,h in e['artifacts'].items() if sha(p)!=h];assert set(changed)=={base+n+'.md' for n in ['PROJECT','ROADMAP','REQUIREMENTS']},changed
 versions={}
 for p in changed:
  snapshot=res+'joint-document-baseline-v24/'+Path(p).name;assert sha(snapshot)==e['artifacts'][p];versions[p]=dict(path=snapshot,sha256=sha(snapshot))
 names=['rotation_diagnosis_plan_v24.json','ablate_fixed_positions_v24.py','joint_mixture_plan_v24.json','joint_mixture_protocol_v24.json','joint_mixture_v24.py','check_joint_mixture_v24.py','train_joint_mixture_v24.py','check_joint_mixture_host_v24.py','check_stationary_joint_host_v24.py','check_joint_reproduction_v24.py','analyze_joint_result_v24.py','audit_joint_learning_v24.py','verify_joint_experiment_v24.py','checkpoint_joint_goal_v24.py']
 inputs=[tr+n for n in names]+[base+'JOINT-MIXTURE-PLAN-v24.md',base+'JOINT-MIXTURE-v24.md'];added=[p for p in inputs if p not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract'])
 s['explicit_revisions'].append(dict(reason='Add controlled rotation substitutions and one prospectively fixed learned per-joint position/proper-rotation mixture with exact reproduction and actual-rig checks. Original full endpoint, floors/milestones,50total evaluations and15-hour resumed deadline unchanged.',prior_state=prior,prior_sha256=sha(prior),prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],added_inputs=added,recorded_at=time.time()))
 fp=g.fingerprint(ROOT,s['contract']['inputs']);route=gp+'rotation-selection-routing-v24.json';paths=set(e['artifacts'])|set(inputs)|{prior,prev_ev,route}
 for pattern in ['joint-*v24*.json','stationary-joint-host-v24*.json','fixed-position-rotation-ablation-v24.json']:paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res).glob(pattern) if p.is_file())
 for folder in ['joint_mixture_v24','joint_mixture_v24_repeat','joint-document-baseline-v24']:paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res/folder).glob('*') if p.is_file())
 for name in ['joint-mixture-host-v24.log','stationary-joint-host-v24.log']:paths.add(tr+'cache/'+name)
 feature=read(res+'joint_mixture_v24/feature_audit.json');assert feature['rows']==7358 and feature['columns']==596 and feature['finite']
 e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={p:sha(p) for p in sorted(paths)},previous_evidence_recheck=dict(path=prev_ev,sha256=sha(prev_ev),changed_artifacts=changed,preserved_prior_versions=versions,all_other_prior_artifacts_unchanged=True),learned_host=moving,stationary_host=stationary,temporal_selection=model['selection'],temporal_gates=model['gates'],development_gates=model['development_gates'],reproduction=repro,joint_verification=verification,joint_learning_audit=read(res+'joint-learning-audit-v24.json'),joint_failure_attribution=attribution,joint_feature_audit=feature,joint_rotation_ablation=read(res+'fixed-position-rotation-ablation-v24.json'),preserved_milestones=old['passed_progress_milestones'],new_passing_milestones=[])
 e['regression'].update(rerun_this_iteration=False,retained_from=prev_ev,note='Runtime/package0.17.4 unchanged. Prior330-case/31-suite and four offline package checks retained, not rerun.18pre-fit checks and32actual-rig cases cover this research candidate.')
 e['qualification'].update(full_goal_complete=False,temporal_model_qualification=False,temporal_animator_integration=False,host_shutdown=False,independent_usability='unknown',full_physics_acceptance=False,full_responsiveness=False)
 e['limitations']=['Development gates remain independent and unchanged; all new and lost cohort passes are recorded. No model promotion or full-goal qualification.','Separate position and normalized-quaternion rotation weights are learned for17joints from known observations. Valid rotations and bounded positions do not guarantee perceptual quality or C1 continuity at hemisphere ambiguity.','18math/data-boundary checks, exact model/diagnostic reproduction and32actual-rig recovery cases establish bounded correctness, not naturalness or broad production coverage.','Host shutdown remains failed after completed assertions. Runtime/package0.17.4 and historical UI evidence remain unchanged; no browser-policy workaround.','Six fresh confirmation clips remain absent; no data downloads, installs or publication.','All original full learned workflow/intent/style/partial-body, physics/refinement, humanoid/quadruped, connector, distribution, responsiveness, supported-host, independent animator and equivalent Cascadeur requirements remain.']
 args=['git','-c','safe.directory=X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github'];assert subprocess.check_output(args+['log','-1','--format=%H %an <%ae> %cn <%ce>'],cwd=ROOT,text=True).strip()==cp['publication']['head'];assert not subprocess.check_output(args+['diff','--name-only'],cwd=ROOT,text=True).strip();assert not subprocess.check_output(args+['diff','--cached','--name-only'],cwd=ROOT,text=True).strip()
 ep=gp+'joint-mixture-evidence-v24.json';write(ep,e);obs=read(gp+'curve-confidence-observations-v23.json')
 for group in obs.values():
  for proof in group.values():proof.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
 write(gp+'joint-mixture-observations-v24.json',obs)
 end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];event='controller-joint-mixture-v24';assert event not in s['work_events'];g.record_work(s,event,duration);result=evaluate(s,obs,ROOT)
 assert result['round']==39 and result['decision']=='iterate';assert not result['implementation_progress']['new'] and not result['implementation_progress']['lost'];assert all(not c['regression'] for c in result['categories'].values());assert s['history'][:-1]==old['history'];assert cp['max_goalposts']==50 and cp['resumed_run_time_cap_hours']==15 and cp['deadline_unix']==1788902277.2365775
 write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result),encoding='utf-8')
 summary=f"Progress: completed controlled rotation substitutions and fixed per-joint mixture; {attribution['failed']}/96cohorts fail versus{attribution['prior_failed']}previously, with{len(attribution['newly_failed'])}new failures.18pre-fit checks, exact reproduction and32real-rig recovery cases pass. Full original goal remains incomplete."
 cp.update(state_path=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=39,remaining_evaluations=11,decision=result['decision'],stagnant_rounds=s['stagnant_rounds'],evidence=ep,active_jobs=[],next_controller_monotonic_start=end,current_turn_classification=summary,work_accounting='Recorded controller-joint-mixture-v24 once from327817.1025334; all recorded training/host processes terminal.',next_safe_actions=['Read original objective and this checkpoint; preserve50total evaluations and fixed15-hour resumed deadline21:17:57UTC.','Keep all candidates frozen and confirmation sealed; prioritize worst-cohort and newly introduced failures without weakening gates or overfitting exposed development data.','Continue original full learned workflow, physics/refinement, rig/quadruped, connector, distribution and responsiveness requirements.','Independent animator and equivalent Cascadeur comparison remain unknown; do not repeat pending question or fabricate evidence.'],recorded_at=time.time())
 write(base+'checkpoint-joint-mixture-v24.json',cp);progress=read(base+'joint-mixture-progress-v24.json');progress.update(status='evaluated',active_jobs=[],latest_checkpoint=base+'checkpoint-joint-mixture-v24.json',remaining_evaluations=11,rounds_completed=39,recorded_at=time.time());write(base+'joint-mixture-progress-v24.json',progress)
 print(dict(round=39,remaining=11,decision=result['decision'],stagnant_rounds=s['stagnant_rounds'],work_seconds=duration,full_goal_complete=False))
if __name__=='__main__':main()
