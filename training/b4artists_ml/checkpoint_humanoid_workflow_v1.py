"""First resumed humanoid milestone; preserve original full goal and75ceiling."""
import copy,time,ast
from checkpoint_expanded_goal_v19 import ROOT,read,write,sha,g
from evaluate_milestone_goal_v2 import evaluate

def main():
    base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/'
    cp=read(base+'checkpoint-resume75-v1.json');prior=cp['state_path'];old=read(prior);s=copy.deepcopy(old);previous=cp['evidence'];e=read(previous);dest=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-humanoid-workflow-v1.json';assert not (ROOT/dest).exists()
    assert cp['round']==50 and s['contract']['max_goalposts']==75 and cp['deadline_unix']==1788981845.
    summary=read(res+'humanoid-workflow-review-v4/summary.json');processes=read(res+'humanoid-workflow-review-v4/processes.json');assert summary['complete'] and len(summary['rows'])==3 and len(processes)==3 and all(x['complete'] for x in processes) and not summary['full_workflow_qualified']
    for row in summary['rows']:assert sha(row['review_scene'])==row['sha256'] and row['source_restored'] and not row['contact_passed']
    rows=read(res+'contact-exact-keys-v1-regression.json');assert len(rows)==2 and sum(r['tests'] for r in rows)==20
    runtime={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in (ROOT/'b4artists_ml').glob('*.py')}
    for row in rows:assert row['assertions_passed'] and not row['errors'] and not row['failures'] and not row['skipped'] and row['runtime_sha256']==runtime and sha(row['log'])==row['sha256']
    probe=read(res+'contact-key-api-probe-v1.json');assert [len(x['after']) for x in probe]==[1,1,2] and probe[2]['evaluated']==[1.,1.5,2.]
    changed=[n for n,h in e['artifacts'].items() if sha(n)!=h];assert changed==['b4artists_ml/contacts.py'],changed
    versions={}
    for n in changed:
        item=cp['pending_source_revisions'][n];assert sha(item['prior_version'])==item['before_sha256']==e['artifacts'][n] and sha(n)==item['after_sha256'];versions[n]=dict(path=item['prior_version'],sha256=item['before_sha256'])
    def funcs(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse((ROOT/p).read_bytes()).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    a=funcs('b4artists_ml/contacts.py');b=funcs(versions['b4artists_ml/contacts.py']['path']);assert set(a)==set(b) and {k for k in a if a[k]!=b[k]}=={'correction_steps'}
    def nums(p):return [n.value for n in ast.walk(ast.parse((ROOT/p).read_bytes())) if isinstance(n,ast.Constant) and type(n.value) in (int,float)]
    assert nums('b4artists_ml/contacts.py')==nums(versions['b4artists_ml/contacts.py']['path'])
    inputs=[tr+'checkpoint_humanoid_workflow_v1.py',base+'HUMANOID-WORKFLOW-MILESTONE.md',base+'HUMANOID-WORKFLOW-REVIEW-v1.md',tr+'build_humanoid_workflow_review_v4.py'];added=[n for n in inputs if n not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract']);a=copy.deepcopy(s['contract']);b=copy.deepcopy(old['contract']);a.pop('inputs');b.pop('inputs');assert a==b
    s['explicit_revisions'].append(dict(reason='Humanoid authored/context/contact workflow review yields3native editable scenes and exposes tangent/limb discontinuities. Exact adaptive contact keys fixed;20native regression cases pass with unchanged numeric constants. No learned or full-workflow qualification. Preserve full endpoint,75ceiling, deadline and floors.',prior_state=prior,prior_sha256=sha(prior),prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],added_inputs=added,preserved_prior_versions=versions,recorded_at=time.time()))
    paths=set(e['artifacts'])|set(inputs)|{prior,previous,gp+'humanoid-workflow-review-routing-v1.json',res+'contact-key-insertion-diagnosis-v1.json',res+'contact-key-insertion-diagnosis-v1.log',res+'contact-key-api-probe-v1.json',res+'contact-key-api-probe-v1.log',res+'humanoid-review-v4-preflight.json',tr+'diagnose_contact_keys_v1.py',tr+'probe_contact_key_api_v1.py'}
    for version in range(1,5):
        paths.add(tr+f'build_humanoid_workflow_review_v{version}.py');paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res/f'humanoid-workflow-review-v{version}').rglob('*') if p.is_file())
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res/'contact-exact-keys-baseline-v1').rglob('*') if p.is_file())
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res).glob('contact-exact-keys-v1*.json'))
    paths.update(row['log'].replace('\\','/') for row in rows)
    assert sha(cp['artifact']['path'])==cp['artifact']['sha256'];plan=read(tr+'temporal_expansion_plan_v19.json');assert all(not (ROOT/tr/'cache'/(n+'.bvh')).exists() for n in plan['planned_splits']['confirmation'])
    fp=g.fingerprint(ROOT,s['contract']['inputs']);e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={n:sha(n) for n in sorted(paths)},previous_evidence_recheck=dict(path=previous,sha256=sha(previous),changed_artifacts=changed,preserved_prior_versions=versions,all_other_prior_artifacts_unchanged=True),humanoid_workflow_review=summary,exact_contact_key_fix=dict(native_regression_cases=20,rows=rows,api_probe=probe,only_changed_function='contacts.correction_steps',all_numeric_constants_unchanged=True,new_package_created=False))
    e['qualification'].update(full_goal_complete=False,full_humanoid_workflow=False,contact_key_regression=True,current_source_full_regression=False,current_package_matches_worktree=False,temporal_model_qualification=False,temporal_animator_integration=False,independent_usability='unknown')
    ep=gp+'humanoid-workflow-evidence-v1.json';write(ep,e);obs=read(gp+'evaluation-limit-observations-v1.json')
    for group in obs.values():
        for row in group.values():row.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
    write(gp+'humanoid-workflow-observations-v1.json',obs);end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];g.record_work(s,'controller-humanoid-workflow-v1',duration);result=evaluate(s,obs,ROOT)
    assert result['round']==51 and result['decision']=='iterate' and s['history'][:-1]==old['history'] and s['floors']==old['floors'] and s['passed_checks']==old['passed_checks'] and s['passed_progress_milestones']==old['passed_progress_milestones']
    result['evidence_transport_note']='Formal signed assessments remain unavailable. Raw20case regression and3actual-rig failures retained; no original threshold/floor was lowered.';s['history'][-1]=result;write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result)+'\n\n'+result['evidence_transport_note']+'\n')
    cp.update(state_path=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=51,remaining_evaluations=24,evidence=ep,decision='iterate',next_controller_monotonic_start=end,active_jobs=[],pending_source_revisions={},pending_document_revisions={},current_turn_classification='Progress: exact contact sample retention fixed and20native cases pass;3editable humanoid review scenes expose remaining contextual tangent and limb-rotation failure. No model or workflow promoted.',recorded_at=time.time())
    cp['next_safe_actions']=['Compare authored-neighbor context/tangents against source-action neighbor context on the same3saved scenes; preserve priorities, contact limits and source recovery.','Trace the remaining limb branch discontinuity rather than increasing refinement limits or loosening tolerances.','Exact-key worktree fix passes20contact integration cases; complete suitable release regression and packaging before replacing0.17.5.','Continue the humanoid milestone within75total evaluations and existing deadline; deferred full-goal requirements remain.','Native goal status was blocked at last tool read; available lifecycle tools cannot resume it. Do not create a replacement goal or alter runtime stores.']
    write(base+'checkpoint-humanoid-workflow-v1.json',cp);print(dict(round=51,max_goalposts=75,remaining_evaluations=24,native_regression_cases=20,review_scenes=3,full_workflow_qualified=False,full_goal_complete=False,work_seconds=duration,all_jobs_terminal=True))
if __name__=='__main__':main()
