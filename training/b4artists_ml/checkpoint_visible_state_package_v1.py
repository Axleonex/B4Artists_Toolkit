"""Record exact local patch qualification, preserving the full animation goal."""
import copy,time
from checkpoint_expanded_goal_v19 import ROOT,read,write,sha,g
from evaluate_milestone_goal_v2 import evaluate

def main():
 base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/'
 cp=read(base+'checkpoint-visible-state-integration-v1.json');old=read(cp['state_path']);s=copy.deepcopy(old);previous=cp['evidence'];e=read(previous)
 assert cp['round']==65 and s['contract']['max_goalposts']==100 and cp['deadline_unix']==1789053845.
 final=read(res+'visible-state-package-finalization-v1.json');assert final['complete']
 meta=read(base+'package-test-v0.19.2.json');offline=read(res+'visible-state-package-v1.json');bench=read(res+'visible-state-integrated-workflow-v1/report.json');plan=read(tr+'visible_state_production_regression_plan_v1.json')
 rows=read(res+'visible-state-production-focused-v2-regression.json')+read(res+'visible-state-production-remaining-v1-regression.json')
 runtime={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in (ROOT/'b4artists_ml').glob('*.py')}
 assert len(rows)==43 and sum(r['tests'] for r in rows)==414 and {r['suite'] for r in rows}==set(plan['suites'])
 assert all(r['assertions_passed'] and not r['errors'] and not r['failures'] and not r['skipped'] and r['runtime_sha256']==plan['runtime_sha256'] and sha(r['log'])==r['sha256'] for r in rows)
 assert meta['ready_for_local_testing'] and meta['runtime_sha256']==offline['runtime_sha256']==runtime
 assert meta['regression']['tested_runtime_sha256']==bench['runtime_sha256']==plan['runtime_sha256']
 assert meta['regression']['post_test_version_only_revision']['only_version_literal_changed']
 assert meta['sha256']==offline['package_sha256']==sha('releases/b4artists_ml_v0.19.2.zip') and offline['passed'] and offline['cases']==13 and not offline['denied_runtime_calls']
 assert bench['complete'] and bench['performance_gate_passed'] and bench['ratio']<=.95
 revisions={n:r for n,r in final['document_revisions'].items() if n in e['artifacts']}
 r=read(res+'visible-state-package-baseline-v1/version-revision.json');revisions['b4artists_ml/__init__.py']={k:r[k] for k in ('prior_version','before_sha256','after_sha256')}
 changed={n for n,h in e['artifacts'].items() if sha(n)!=h};assert changed==set(revisions),changed
 for n,r in revisions.items():assert sha(r['prior_version'])==r['before_sha256']==e['artifacts'][n] and sha(n)==r['after_sha256']
 inputs=[tr+n for n in ('check_visible_state_integrated_workflow_v1.py','build_visible_state_package_v1.py','check_visible_state_package_v1.py','finalize_visible_state_package_v1.py','checkpoint_visible_state_package_v1.py')]+[base+'SOURCE-COMPARISON-v0.19.2.md',base+'PUBLISHED-MODEL-SCREEN-v1.md']
 added=[n for n in inputs if n not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract'])
 a=copy.deepcopy(s['contract']);b=copy.deepcopy(old['contract']);a.pop('inputs');b.pop('inputs');assert a==b
 s['explicit_revisions'].append(dict(reason='Integrated source comparison passes414native cases and serial exact-output benchmark; version-only metadata revision and13exact-archive offline workflows qualified. Full goal, thresholds, limits, floors and deferrals unchanged.',prior_state=cp['state_path'],prior_sha256=sha(cp['state_path']),artifact_revisions=revisions,added_inputs=added,prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],recorded_at=time.time()))
 paths=set(e['artifacts'])|set(inputs)|{cp['state_path'],previous,base+'checkpoint-visible-state-integration-v1.json',base+'visible-state-integration-progress-v1.json',gp+'visible-state-package-routing-v1.json',base+'package-test-v0.19.2.json','releases/b4artists_ml_v0.19.2.zip'}
 for folder in ('visible-state-integrated-workflow-v1','visible-state-package-baseline-v1','visible-state-documents-baseline-v1'):
  paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res/folder).rglob('*') if p.is_file())
 paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/tr/'cache/visible-state-package-v1').rglob('*') if p.is_file())
 for prefix in ('visible-state-production-remaining-v1','visible-state-package-v1','visible-state-package-finalization-v1','visible-state-production-regression-completion-v1'):
  paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res).glob(prefix+'*.json'))
  paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/tr/'cache').glob(prefix+'*.log'))
 assert all(not (ROOT/tr/'cache'/(n+'.bvh')).exists() for n in read(tr+'temporal_expansion_plan_v19.json')['planned_splits']['confirmation'])
 fp=g.fingerprint(ROOT,s['contract']['inputs']);e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={n:sha(n) for n in sorted(paths)},previous_evidence_recheck=dict(path=previous,sha256=sha(previous),all_unrevised_artifacts_unchanged=True,explicit_revisions=revisions),visible_state_package=dict(native_cases=414,offline_cases=13,contact_checks=9813,version='0.19.2',metadata_only_revision=meta['regression']['post_test_version_only_revision'],benchmark_ratio=bench['ratio'],new_archive_ready=True,native_shutdown_clean=False))
 e['qualification'].update(temporal_model_qualification=False,independent_usability='unknown',full_goal_complete=False)
 ep=gp+'visible-state-package-evidence-v1.json';write(ep,e);obs=read(gp+'visible-state-integration-observations-v1.json')
 for group in obs.values():
  for row in group.values():row.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
 op=gp+'visible-state-package-observations-v1.json';write(op,obs);end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];g.record_work(s,'controller-visible-state-package-v1',duration);result=evaluate(s,obs,ROOT)
 assert result['round']==66 and result['decision']=='iterate' and s['history'][:-1]==old['history'] and s['floors']==old['floors']
 result['evidence_transport_note']='Signed assessments and independent usability remain unavailable.414native checks, exact output/performance and13offline archive workflows are recorded without substituting for learned-motion or human/Cascadeur qualification.';s['history'][-1]=result
 dest=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-visible-state-package-v1.json';assert not (ROOT/dest).exists();write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result)+'\n\n'+result['evidence_transport_note']+'\n',encoding='utf-8')
 cp.update(state_path=dest,last_evaluated_state=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=66,remaining_evaluations=34,evidence=ep,decision='iterate',stagnant_rounds=s['stagnant_rounds'],next_controller_monotonic_start=end,recorded_at=time.time(),current_turn_classification='Progress: completed414native regression checks, integrated serial benchmark and exact0.19.2offline archive qualification.',previous_turn_classification='Progress: prepared gated archive builder and offline validation; confirmed same regression process continued through interruption.',blocked_audit=dict(consecutive_goal_turns=0,condition=None),active_jobs=[],work_accounting='Parent interval recorded once; no child runtimes added.',pending_source_revisions={},pending_document_revisions={})
 cp['artifact']=dict(path='releases/b4artists_ml_v0.19.2.zip',sha256=meta['sha256'],files=meta['files'],bytes=meta['bytes'],matches_current_source=True,experimental=True,ready_for_local_testing=True,note='414native cases before metadata-only version bump;13exact-archive offline workflows; full goal incomplete.')
 cp['latest_live_observation']=dict(all_jobs_terminal=True,regression_cases=414,offline_cases=13,native_exit_code=read(res+'visible-state-package-v1-process.json')['exit_code'])
 cp['next_safe_actions']=['Source-comparison milestone complete. Do not rerun qualified checks without a relevant change. Archive is local only.','Return priority to full humanoid motion quality and animator workflows. Nearby model fitting remains paused; use a new bounded hypothesis grounded in frozen failures before any new fit.','Read PUBLISHED-MODEL-SCREEN-v1.md: inspected pretrained routes are not verified freely distributable replacements. Do not claim exhaustive rejection or automatically start another nearby fit. Explicit contact/intent, full physics/refinement and human/Cascadeur comparison remain open.','Preserve same goal,100evaluation limit,deadline1789053845,unopened confirmation clips and publication identity/approval rules.']
 write(base+'checkpoint-visible-state-package-v1.json',cp);print(dict(round=66,remaining_evaluations=34,protected_artifacts=len(paths),work_seconds=duration,version='0.19.2',full_goal_complete=False))
if __name__=='__main__':main()
