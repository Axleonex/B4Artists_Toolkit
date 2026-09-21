"""Preserve canonical training and private-rig evidence; keep quality pending."""
import copy,time,json,argparse
from checkpoint_expanded_goal_v19 import ROOT,read,write,sha,g
from evaluate_milestone_goal_v2 import evaluate

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--evaluation-session',type=int,required=True);args=parser.parse_args()
 base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/'
 cp=read(base+'checkpoint-sequence-feasibility-v2.json');old=read(cp['state_path']);s=copy.deepcopy(old);previous=cp['evidence'];e=read(previous)
 assert cp['round']==58 and s['contract']['max_goalposts']==100 and cp['deadline_unix']==1789053845.
 for n,h in e['artifacts'].items():assert sha(n)==h,n
 processes=read(res+'sequence-corpus-training-v2/processes.json');assert len(processes)==4 and all(v['exit_code']==0 for v in processes)
 assert read(res+'sequence-corpus-training-v2/active-process.json')['all_complete']
 for row in processes:
  report=read(res+'sequence-corpus-training-v2/'+row['kind']+'-'+str(row['seed'])+'/report.json');assert report['complete'] and report['completed_epochs']==60 and report['cpu_export_max_abs_error']<5e-5 and sha(report['weights'])==report['weights_sha256']
 lifecycle=read(res+'private-sequence-lifecycle-v2/report.json');assert lifecycle['complete'] and lifecycle['cases']==15
 runtime={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in (ROOT/'b4artists_ml').glob('*.py')};assert runtime==lifecycle['runtime_sha256']==read(base+'package-test-v0.19.0.json')['runtime_sha256']
 profiles=list((ROOT/res/'private-sequence-projection-v2').glob('*/report.json'));assert len(profiles)==5
 for p in profiles:
  v=read(p);assert v['complete'] and v['equivalence_passed'] and v['cases'][0]['exact_samples'] and v['runtime_sha256']==runtime
 names=['sequence_evaluation_plan_v1.json','evaluate_sequence_corpus_v1.py','private_sequence_job_v1.py','private_sequence_job_v2.py','check_private_sequence_projection_v1.py','check_private_sequence_projection_v2.py','check_private_sequence_lifecycle_v1.py','check_private_sequence_lifecycle_v2.py','checkpoint_sequence_training_v1.py']
 inputs=[tr+n for n in names]+[base+'PRIVATE-SEQUENCE-PROJECTION-v2.md'];added=[n for n in inputs if n not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract']);a=copy.deepcopy(s['contract']);b=copy.deepcopy(old['contract']);a.pop('inputs');b.pop('inputs');assert a==b
 s['explicit_revisions'].append(dict(reason='Four fixed canonical sequence fits complete; five broader exact private-rig comparisons and15lifecycle checks. Same full endpoint, limits and floors; learned quality remains pending.',prior_state=cp['state_path'],prior_sha256=sha(cp['state_path']),added_inputs=added,prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],recorded_at=time.time()))
 paths=set(e['artifacts'])|set(inputs)|{cp['state_path'],previous,gp+'sequence-evaluation-routing-v1.json'}
 for folder in ('sequence-corpus-training-v2','private-sequence-projection-v1','private-sequence-projection-v2','private-sequence-lifecycle-v1','private-sequence-lifecycle-v2'):
  paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res/folder).rglob('*') if p.is_file())
 frozen=res+'sequence-development-v1/frozen-before-validation.json';assert (ROOT/frozen).exists();paths.add(frozen)
 assert all(not (ROOT/tr/'cache'/(n+'.bvh')).exists() for n in read(tr+'temporal_expansion_plan_v19.json')['planned_splits']['confirmation'])
 fp=g.fingerprint(ROOT,s['contract']['inputs']);e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={n:sha(n) for n in sorted(paths)},previous_evidence_recheck=dict(path=previous,sha256=sha(previous),all_prior_artifacts_unchanged=True),sequence_training=dict(fits=4,epochs_each=60,windows=5778,weights_frozen=True,development_pending=True,private_equivalence_cases=6,private_lifecycle_cases=15,independent_review_available=False,full_quality_qualified=False))
 e['qualification'].update(temporal_model_qualification=False,independent_usability='unknown',full_goal_complete=False);ep=gp+'sequence-training-evidence-v1.json';write(ep,e);obs=read(gp+'sequence-feasibility-observations-v2.json')
 for group in obs.values():
  for row in group.values():row.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
 op=gp+'sequence-training-observations-v1.json';write(op,obs);end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];g.record_work(s,'controller-sequence-training-v1',duration);result=evaluate(s,obs,ROOT)
 assert result['round']==59 and result['decision']=='iterate' and s['history'][:-1]==old['history'] and s['floors']==old['floors'];result['evidence_transport_note']='Authenticated assessment and independent review unavailable. Training/export/private-rig results recorded; motion quality and human usability remain unqualified.';s['history'][-1]=result;dest=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-sequence-training-v1.json';assert not (ROOT/dest).exists();write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result)+'\n\n'+result['evidence_transport_note']+'\n',encoding='utf-8')
 cp.update(state_path=dest,last_evaluated_state=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=59,remaining_evaluations=41,evidence=ep,decision='iterate',stagnant_rounds=s['stagnant_rounds'],next_controller_monotonic_start=end,active_jobs=[dict(kind='unified_exec',session_id=args.evaluation_session,task='Frozen sequence development comparison against unchanged projected controls',progress=res+'sequence-development-v1/progress.json')],recorded_at=time.time(),current_turn_classification='Progress:fixed sequence training complete; exact private-rig equivalence and lifecycle evidence. Development comparison running; no runtime promotion.',blocked_audit=dict(consecutive_goal_turns=0,condition=None),work_accounting='Parent active-work interval recorded once; no child runtime added.')
 cp['latest_live_observation']=dict(training=dict(session_id=61813,terminal=True,exit_code=0),private_broad=dict(session_id=52619,terminal=True,exit_code=0),private_lifecycle_v1=dict(session_id=11026,terminal=True,exit_code=1,test_phase_assumption_failed=True),private_lifecycle_v2=dict(session_id=17315,terminal=True,exit_code=0,native_exit=3221225477),development=dict(session_id=args.evaluation_session,live_verified=True))
 cp['next_safe_actions']=['Revalidate the same active development job; do not restart a live evaluation on observation timeout.','Report all four models under unchanged old/new/combined gates; require both seeds for a family pass. No post-validation retraining or seed selection.','Six confirmation clips remain sealed. Actual learned quality, human usability and equivalent Cascadeur comparison remain unqualified.','Private-rig research is promising; production needs explicit dependency injection, source/lifecycle protections and isolated host latency checks.','Retain full goal ID/endpoint,100ceiling,extendeddeadline,paused selector variations and prior deferrals.']
 write(base+'checkpoint-sequence-training-v1.json',cp);print(dict(round=59,remaining_evaluations=41,prior_artifacts_verified=len(read(previous)['artifacts']),artifact_count=len(paths),work_seconds=duration,active_evaluation_session=args.evaluation_session,full_goal_complete=False))
if __name__=='__main__':main()
