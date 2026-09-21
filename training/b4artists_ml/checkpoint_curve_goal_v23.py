"""Record curve-descriptor progress without changing the full active endpoint."""
import copy,time,subprocess,zipfile
from pathlib import Path
from checkpoint_expanded_goal_v19 import ROOT,read,sha,write,g,evaluate

def main():
 base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/'
 prior_tag='relative-mixture-v22';tag='curve-confidence-v23';prefix='01a073fe-c240-70c0-b5cd-fe9653aac60e-'
 prior=gp+prefix+prior_tag+'.json';dest=gp+prefix+tag+'.json';assert not (ROOT/dest).exists()
 old=read(prior);s=copy.deepcopy(old);cp=read(base+'checkpoint-'+prior_tag+'.json');prev_ev=gp+prior_tag+'-evidence.json'
 # Existing evidence names put their version at the end.
 prev_ev=gp+'relative-mixture-evidence-v22.json';e=read(prev_ev)
 model=read(res+'curve_mixture_v23/report.json');repro=read(res+'curve-mixture-reproduction-v23.json');verification=read(res+'curve-experiment-verification-v23.json');assert verification['passed'] and verification['pre_fit_checks']==18 and repro['passed']
 for n,h in repro['identical_sha256'].items():assert sha(res+'curve_mixture_v23/'+n)==h==sha(res+'curve_mixture_v23_repeat/'+n)
 a=copy.deepcopy(model);b=read(res+'curve_mixture_v23_repeat/report.json')
 for report in [a,b]:report.pop('runtime');report['model_files']={Path(k).name:v for k,v in report['model_files'].items()}
 assert a==b
 previous=read(res+'mixture_trajectory_v21/report.json');assert model['protocol']['gates']==previous['protocol']['gates'] and model['protocol']['projection']==previous['protocol']['projection']
 for part in ['old_validation','new_validation','combined']:
  for name in model['protocol']['baselines']:assert model['partition_reports'][part][name]==previous['partition_reports'][part][name]
 assert all(v['checks']['position'] and not v['checks']['cohorts'] for v in model['development_gates'].values())
 for name,h in model['source_sha256'].items():assert sha(tr+name)==h
 plan=read(tr+'temporal_expansion_plan_v19.json');assert all(not (ROOT/tr/'cache'/(c+'.bvh')).exists() for c in plan['planned_splits']['confirmation']);assert not model['confirmation_read']
 moving=read(res+'curve-mixture-host-v23.json');stationary=read(res+'stationary-curve-host-v23.json');meta=read(base+'package-test-v0.17.4.json')
 current={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in (ROOT/'b4artists_ml').glob('*.py')};assert current==meta['runtime_sha256']==moving['runtime_sha256']==stationary['runtime_sha256']
 for host in [moving,stationary]:assert host['complete'] and host['passed'] and len(host['rows'])==16 and host['model_sha256']==model['selection']['best_learned_sha256']
 assert sha('releases/b4artists_ml_v0.17.4.zip')==meta['sha256']
 with zipfile.ZipFile(ROOT/'releases/b4artists_ml_v0.17.4.zip') as z:assert all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist())
 changed=[p for p,h in e['artifacts'].items() if sha(p)!=h];assert set(changed)=={base+n+'.md' for n in ['PROJECT','ROADMAP','REQUIREMENTS']},changed
 versions={}
 for p in changed:
  snapshot=res+'curve-document-baseline-v23/'+Path(p).name;assert sha(snapshot)==e['artifacts'][p];versions[p]=dict(path=snapshot,sha256=sha(snapshot))
 names=['curve_confidence_plan_v23.json','curve_mixture_protocol_v23.json','curve_features_v23.py','curve_mixture_v23.py','check_curve_mixture_v23.py','check_curve_compatibility_v23.py','train_curve_mixture_v23.py','check_curve_mixture_host_v23.py','check_stationary_curve_host_v23.py','check_curve_reproduction_v23.py','analyze_curve_result_v23.py','verify_curve_experiment_v23.py','checkpoint_curve_goal_v23.py']
 inputs=[tr+n for n in names]+[base+'CURVE-CONFIDENCE-PLAN-v23.md',base+'CURVE-CONFIDENCE-v23.md'];added=[p for p in inputs if p not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract'])
 s['explicit_revisions'].append(dict(reason='Add one fixed observed-curve descriptor experiment, exact group-excluded parent features, unchanged gates, compatibility/reproduction and actual-rig recovery. Full original endpoint, floors/milestones,50 evaluations and15-hour resumed deadline unchanged.',prior_state=prior,prior_sha256=sha(prior),prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],added_inputs=added,recorded_at=time.time()))
 fp=g.fingerprint(ROOT,s['contract']['inputs']);route=gp+'curve-confidence-routing-v23.json';paths=set(e['artifacts'])|set(inputs)|{prior,prev_ev,route}
 for pattern in ['curve-*v23*.json','stationary-curve-host-v23*.json']:paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res).glob(pattern) if p.is_file())
 for folder in ['curve_mixture_v23','curve_mixture_v23_repeat','curve-document-baseline-v23']:paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res/folder).glob('*') if p.is_file())
 for name in ['curve-mixture-host-v23.log','stationary-curve-host-v23.log']:paths.add(tr+'cache/'+name)
 attribution=read(res+'curve-failure-attribution-v23.json');cross=read(res+'curve-v22-comparison-v23.json');assert attribution['failed']==7 and attribution['prior_failed']==11 and not attribution['newly_failed'];assert len(cross['newly_failed'])==1
 feature=read(res+'curve_mixture_v23/feature_audit.json');compat=read(res+'curve-compatibility-v23.json');assert feature['rows']==7358 and feature['columns']==596 and feature['finite'] and compat['passed']
 e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={p:sha(p) for p in sorted(paths)},previous_evidence_recheck=dict(path=prev_ev,sha256=sha(prev_ev),changed_artifacts=changed,preserved_prior_versions=versions,all_other_prior_artifacts_unchanged=True),learned_host=moving,stationary_host=stationary,temporal_selection=model['selection'],temporal_gates=model['gates'],development_gates=model['development_gates'],reproduction=repro,curve_verification=verification,curve_failure_attribution=attribution,curve_feature_audit=feature,curve_compatibility=compat,curve_v22_comparison=cross,curve_rotation_crosscheck=read(res+'curve-rotation-crosscheck-v23.json'),preserved_milestones=old['passed_progress_milestones'],new_passing_milestones=[])
 e['regression'].update(rerun_this_iteration=False,retained_from=prev_ev,note='Runtime/package0.17.4 unchanged. Prior330-case/31-suite and four offline package checks retained, not rerun.18pre-fit checks, compatibility and32actual-rig cases cover this research candidate.')
 e['qualification'].update(full_goal_complete=False,temporal_model_qualification=False,temporal_animator_integration=False,host_shutdown=False,independent_usability='unknown',full_physics_acceptance=False,full_responsiveness=False)
 e['limitations']=['All average-position gates pass, but all worst-cohort gates fail. Seven of96cohorts fail versus11with v21; one previously passing v22cohort fails. No promotion.','48descriptors are computed from known observations and group-excluded parent proposals. They are not calibrated uncertainty probabilities or physical guarantees.','Model, feature audit and non-runtime results reproduce exactly; six fresh confirmation clips remain absent. No new data downloaded.','Rotation cross-reference motivates controlled substitutions with fixed v23 positions; failure of individual fixed-rotation controls is not a proof that every positional mixture fails.','32actual-rig checks establish editable results and recovery, not naturalness or broad production coverage. Host shutdown remains failed.','v0.17.4 runtime/package and historical UI proof are unchanged; no browser-policy workaround was used.','All original full learned workflow/intent/style/partial-body, physics/refinement, humanoid/quadruped, connector, distribution, responsiveness, supported-host, independent animator and Cascadeur requirements remain.']
 args=['git','-c','safe.directory=X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github'];assert subprocess.check_output(args+['log','-1','--format=%H %an <%ae> %cn <%ce>'],cwd=ROOT,text=True).strip()==cp['publication']['head'];assert not subprocess.check_output(args+['diff','--name-only'],cwd=ROOT,text=True).strip();assert not subprocess.check_output(args+['diff','--cached','--name-only'],cwd=ROOT,text=True).strip()
 ep=gp+'curve-confidence-evidence-v23.json';write(ep,e);obs=read(gp+'relative-mixture-observations-v22.json')
 for group in obs.values():
  for proof in group.values():proof.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
 write(gp+'curve-confidence-observations-v23.json',obs)
 end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];event='controller-curve-confidence-v23';assert event not in s['work_events'];g.record_work(s,event,duration);result=evaluate(s,obs,ROOT)
 assert result['round']==38 and result['decision']=='iterate';assert not result['implementation_progress']['new'] and not result['implementation_progress']['lost'];assert all(not c['regression'] for c in result['categories'].values());assert s['history'][:-1]==old['history'];assert cp['max_goalposts']==50 and cp['resumed_run_time_cap_hours']==15 and cp['deadline_unix']==1788902277.2365775
 write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result),encoding='utf-8')
 cp.update(state_path=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=38,remaining_evaluations=12,decision=result['decision'],stagnant_rounds=s['stagnant_rounds'],evidence=ep,active_jobs=[],next_controller_monotonic_start=end,current_turn_classification='Progress: observed curve descriptors reduce failed cohorts11to7and worst ratios to1.587/1.207; exact reproduction,18checks, compatibility and32real-rig cases pass. Quality remains unqualified and full original goal incomplete.',work_accounting='Recorded controller-curve-confidence-v23 once from326161.027492; sessions85457,24647,90912,20440terminal.',next_safe_actions=['Read original objective/checkpoint; preserve50total evaluations and unchanged15-hour deadline21:17:57UTC.','Keep all candidates frozen and six fresh confirmation clips sealed. Run controlled substitutions of procedural rotations while holding v23positions fixed to isolate remaining rotation effects before a new architecture.','Consider learned rotation selectivity or per-joint mixture capacity only after diagnostic/training evidence. Any parent-dependent features must use group-excluded training parents and the identical inference calculation.','Continue every original full learned workflow, physics/refinement, rig/quadruped, optional connector, distribution and responsiveness requirement.','Independent animator and equivalent Cascadeur comparison remain unknown; do not fabricate or bypass browser policy.'],recorded_at=time.time())
 write(base+'checkpoint-curve-confidence-v23.json',cp);progress=read(base+'curve-confidence-progress-v23.json');progress.update(status='evaluated',active_jobs=[],latest_checkpoint=base+'checkpoint-curve-confidence-v23.json',remaining_evaluations=12,rounds_completed=38,recorded_at=time.time());write(base+'curve-confidence-progress-v23.json',progress)
 print(dict(round=38,remaining=12,decision=result['decision'],stagnant_rounds=s['stagnant_rounds'],work_seconds=duration,full_goal_complete=False))
if __name__=='__main__':main()
