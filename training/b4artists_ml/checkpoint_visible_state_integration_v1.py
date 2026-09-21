"""Checkpoint exact source comparison integration; preserve full goal and evidence."""
import copy,time,argparse
from checkpoint_expanded_goal_v19 import ROOT,read,write,sha,g
from evaluate_milestone_goal_v2 import evaluate

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--regression-session',type=int,required=True);args=parser.parse_args()
 base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/'
 cp=read(base+'checkpoint-tangent-development-v1.json');old=read(cp['state_path']);s=copy.deepcopy(old);previous=cp['evidence'];e=read(previous)
 assert cp['round']==64 and s['contract']['max_goalposts']==100 and cp['deadline_unix']==1789053845.
 replacements={'b4artists_ml/temporal_generation.py':res+'visible-state-production-baseline-v1/temporal_generation.py'}
 changed={n for n,h in e['artifacts'].items() if sha(n)!=h};assert changed==set(replacements),changed
 revisions={}
 for n,b in replacements.items():
  assert sha(b)==e['artifacts'][n]
  revisions[n]=dict(prior_version=b,before_sha256=sha(b),after_sha256=sha(n))
 focused=read(res+'visible-state-production-focused-v2-regression.json');plan=read(tr+'visible_state_production_regression_plan_v1.json')
 assert len(focused)==4 and sum(r['tests'] for r in focused)==24
 assert all(r['assertions_passed'] and not r['errors'] and not r['failures'] and not r['skipped'] and r['runtime_sha256']==plan['runtime_sha256'] for r in focused)
 bench=read(res+'visible-state-workflow-v1/report.json');assert bench['complete'] and bench['performance_gate_passed'] and bench['exact_output'] and bench['source_preserved'] and not bench['production_changed']
 inputs=[tr+n for n in ('visible_state_candidates_v1.py','probe_visible_state_bulk_v1.py','check_visible_state_candidates_v1.py','check_visible_state_candidates_v2.py','check_visible_state_workflow_v1.py','visible_state_production_regression_plan_v1.json','checkpoint_visible_state_integration_v1.py')]+['tests/test_b4artists_ml_visible_state_v1.py',base+'VISIBLE-STATE-INTEGRATION-v1.md']
 added=[n for n in inputs if n not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract'])
 a=copy.deepcopy(s['contract']);b=copy.deepcopy(old['contract']);a.pop('inputs');b.pop('inputs');assert a==b
 s['explicit_revisions'].append(dict(reason='Exact batched pose comparison passed fixed research and24integrated checks; remaining native regression active. Original endpoint, thresholds, floors, limits and deferrals unchanged.',prior_state=cp['state_path'],prior_sha256=sha(cp['state_path']),source_revisions=revisions,added_inputs=added,prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],recorded_at=time.time()))
 paths=set(e['artifacts'])|set(inputs)|set(replacements.values())|{cp['state_path'],previous,gp+'visible-state-routing-v1.json',base+'checkpoint-tangent-development-v1.json'}
 for folder in ('visible-state-bulk-probe-v1','visible-state-candidates-v1','visible-state-candidates-v2','visible-state-workflow-v1','visible-state-production-baseline-v1'):
  paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res/folder).rglob('*') if p.is_file())
 for prefix in ('visible-state-production-focused-v1','visible-state-production-focused-v2'):
  paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res).glob(prefix+'*.json'))
  paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/tr/'cache').glob(prefix+'*.log'))
 assert all(not (ROOT/tr/'cache'/(n+'.bvh')).exists() for n in read(tr+'temporal_expansion_plan_v19.json')['planned_splits']['confirmation'])
 fp=g.fingerprint(ROOT,s['contract']['inputs'])
 e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={n:sha(n) for n in sorted(paths)},previous_evidence_recheck=dict(path=previous,sha256=sha(previous),all_unrevised_artifacts_unchanged=True,source_revisions=revisions),visible_state_integration=dict(focused_native_cases=24,remaining_regression_pending=True,research_benchmark_ratio=bench['ratio'],native_shutdown_clean=False,new_archive_ready=False))
 e['qualification'].update(temporal_model_qualification=False,independent_usability='unknown',full_goal_complete=False)
 ep=gp+'visible-state-integration-evidence-v1.json';write(ep,e);obs=read(gp+'tangent-development-observations-v1.json')
 for group in obs.values():
  for row in group.values():row.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
 op=gp+'visible-state-integration-observations-v1.json';write(op,obs)
 end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];g.record_work(s,'controller-visible-state-integration-v1',duration);result=evaluate(s,obs,ROOT)
 assert result['round']==65 and result['decision']=='iterate' and s['history'][:-1]==old['history'] and s['floors']==old['floors']
 result['evidence_transport_note']='Signed assessments and independent usability unavailable. Native focused checks and measured candidate performance retained; full regression, exact new package and full goal qualification remain incomplete.'
 s['history'][-1]=result;dest=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-visible-state-integration-v1.json';assert not (ROOT/dest).exists();write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result)+'\n\n'+result['evidence_transport_note']+'\n',encoding='utf-8')
 cp.update(state_path=dest,last_evaluated_state=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=65,remaining_evaluations=35,evidence=ep,decision='iterate',stagnant_rounds=s['stagnant_rounds'],next_controller_monotonic_start=end,recorded_at=time.time(),current_turn_classification='Progress: benchmark selected exact batched comparison, integrated it, and24native checks pass; wider regression running.',previous_turn_classification='Progress: recovered completed full-workflow benchmark and revised architecture assessment from failed learned-model evidence.',blocked_audit=dict(consecutive_goal_turns=0,condition=None),work_accounting='Parent interval recorded once; no child runtimes added.',pending_source_revisions={},pending_document_revisions={})
 cp['active_jobs']=[dict(kind='unified_exec',session_id=args.regression_session,task='39remaining native suites on unchanged source',report=res+'visible-state-production-remaining-v1-regression.json')]
 cp['latest_live_observation']=dict(regression=dict(session_id=args.regression_session,live_verified=True),focused=dict(session_id=49326,terminal=True,exit_code=0,cases=24))
 cp['artifact']['matches_current_source']=False;cp['artifact']['note']='Previously tested0.19.1archive unchanged; current source comparison optimization not included. New archive pending.'
 cp['next_safe_actions']=['Revalidate same remaining-regression session; inspect all39suite results plus24focused cases against frozen runtime hashes. Do not restart on observation timeout.','Run a serial actual-integration full-workflow comparison, then package and verify only after all414cases pass.','Source baseline and first failed test fixture are preserved. Do not weaken exact source checks or guard frequency.','Nearby learned fits remain paused; full human animation tasks, intent/contact/physics and comparative validation remain required.','Keep same goal,100evaluation limit,deadline1789053845,unopened confirmation clips and publication identity/approval rules.']
 write(base+'checkpoint-visible-state-integration-v1.json',cp)
 print(dict(round=65,remaining_evaluations=35,protected_artifacts=len(paths),source_revisions=len(revisions),work_seconds=duration,active_regression_session=args.regression_session,full_goal_complete=False))
if __name__=='__main__':main()
