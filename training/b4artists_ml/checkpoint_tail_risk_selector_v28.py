"""Preserve rejected v28 training and complete validation at evaluation49."""
import copy,time,subprocess,zipfile
from checkpoint_expanded_goal_v19 import ROOT,read,write,sha,g
from evaluate_milestone_goal_v2 import evaluate

def main():
    base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/'
    cp=read(base+'checkpoint-soft-selector-v27.json');prior=cp['state_path'];old=read(prior);s=copy.deepcopy(old);previous=cp['evidence'];e=read(previous)
    dest=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-tail-risk-selector-v28.json';assert not (ROOT/dest).exists()
    model=read(res+'tail_risk_selector_v28/report.json');repro=read(res+'tail-risk-selector-verification-v28.json');stability=read(res+'tail-risk-selector-edit-stability-v28.json');diag=read(res+'tail-risk-selector-training-v28.json')
    assert repro['passed'] and repro['deterministic_reports_equal'] and repro['cohorts']==96 and repro['failed']==3
    assert stability['complete'] and stability['cases']==1728 and stability['prior_hard_probes_reproduced_exactly'] and not stability['quality_qualification']
    assert diag['geometry_passed'] and diag['windows']==466 and not diag['validation_loaded']
    for name,h in repro['identical_sha256'].items():assert sha(res+'tail_risk_selector_v28/'+name)==h==sha(res+'tail_risk_selector_v28_repeat/'+name)
    native=[]
    for tag,n in [('tail-risk-selector-host-v28',16),('stationary-tail-risk-selector-host-v28',16),('tail-risk-selector-journey-v28',15),('tail-risk-selector-cooperative-v28',25)]:
        p=res+tag+'.json';d=read(p);process=read(res+tag+'-process.json');assert d['passed'] and d['complete'] and d.get('tests',len(d.get('rows',[])))==n
        assert process['exit_code']==3221225477
        for path,h in d['runtime_sha256'].items():assert sha(path)==h,path
        for path,h in d['research_sha256'].items():assert sha(path if path.startswith(('training/','tests/')) else tr+path)==h,path
        native.append(dict(path=p,sha256=sha(p),cases=n,assertions_passed=True,process_exit=process['exit_code']))
    full=read(res+'projected-selector-reproduction-v26.json');assert full['passed']
    meta=read(base+'package-test-v0.17.5.json');assert sha(cp['artifact']['path'])==meta['sha256']==cp['artifact']['sha256']
    assert {p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in (ROOT/'b4artists_ml').glob('*.py')}==meta['runtime_sha256']
    with zipfile.ZipFile(ROOT/cp['artifact']['path']) as z:assert all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist())
    changed=[n for n,h in e['artifacts'].items() if sha(n)!=h];assert set(changed)=={base+'PROJECT.md',base+'ROADMAP.md'},changed
    versions={}
    for n in changed:
        path=res+'tail-risk-document-baseline-v28/'+n.split('/')[-1];assert sha(path)==e['artifacts'][n];versions[n]=dict(path=path,sha256=sha(path))
    inputs=[tr+'checkpoint_tail_risk_selector_v28.py',base+'TAIL-RISK-SELECTOR-v28.md'];added=[n for n in inputs if n not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract'])
    a=copy.deepcopy(s['contract']);b=copy.deepcopy(old['contract']);a.pop('inputs');b.pop('inputs');assert a==b
    s['explicit_revisions'].append(dict(reason='Fixed training-tail-risk variant reproduced;training objective improves but development worsens with3of96failed cohorts. Raw edit amplification improves and72native assertions pass. Preserve full endpoint, thresholds, sealed confirmation,50goalposts and deadline.',prior_state=prior,prior_sha256=sha(prior),prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],added_inputs=added,preserved_prior_versions=versions,recorded_at=time.time()))
    paths=set(e['artifacts'])|set(inputs)|{prior,previous,res+'projected-selector-reproduction-v26.json',tr+'verify_projected_selector_reproduction_v26.py',gp+'tail-risk-routing-v28.json'}
    for directory in ['tail_risk_selector_v28','tail_risk_selector_v28_repeat','tail-risk-document-baseline-v28','soft-selector-prefit-baseline-v27','projected-selector-checkpoint-path-fix-v26','soft-selector-checkpoint-prefix-fix-v27']:
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res/directory).rglob('*') if p.is_file())
    for directory,pattern in [(tr,'*v28*'),(res,'*tail-risk*v28*.json'),(tr+'cache/','*tail-risk*v28*.log'),('tests/','*tail_risk*v28*'),(gp,'*tail-risk*v28*.json')]:
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/directory).glob(pattern) if p.is_file())
    plan=read(tr+'temporal_expansion_plan_v19.json');assert all(not (ROOT/tr/'cache'/(c+'.bvh')).exists() for c in plan['planned_splits']['confirmation'])
    args=['git','-c','safe.directory=X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github'];assert subprocess.check_output(args+['log','-1','--format=%H %an <%ae> %cn <%ce>'],cwd=ROOT,text=True).strip()==cp['publication']['head']
    assert not subprocess.check_output(args+['diff','--name-only'],cwd=ROOT,text=True).strip();assert not subprocess.check_output(args+['diff','--cached','--name-only'],cwd=ROOT,text=True).strip()
    fp=g.fingerprint(ROOT,s['contract']['inputs']);e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={n:sha(n) for n in sorted(paths)},previous_evidence_recheck=dict(path=previous,sha256=sha(previous),changed_artifacts=changed,preserved_prior_versions=versions,all_other_prior_artifacts_unchanged=True),tail_risk_selector=dict(report=model,reproduction=repro,edit_stability=stability,training_diagnostic=diag,native_checks=native,native_cases=72),projected_selector_full_reproduction=full)
    e['projected_selector_training'].update(repeat_complete_file_present=True,full_reproduction_verified=True,active_sessions=[])
    e['qualification'].update(full_goal_complete=False,temporal_model_qualification=False,temporal_animator_integration=False,full_responsiveness=False,independent_usability='unknown')
    e['limitations']=['v28fails3of96developmentcohorts;worst2.911539vs1.10limit. Both exposed partitions fail; new138_01/gap8/context1regression.', 'Training surrogate scores improve while actual projected quality does not qualify. Raw edit maximum sensitivity improves, but p95 does not consistently improve.','72native assertions pass, hostshutdownstill3221225477. No current GUI or independent animator qualification.','Two full v28training/evaluation runs reproduce exactly; no confirmation loaded or weights promoted.','Signed assessment producer unavailable; canonical observations unknown and historical floors/passed checks preserved.','Full original standalone parity scope remains unmet; one final evaluation remains after this checkpoint.']
    ep=gp+'tail-risk-selector-evidence-v28.json';write(ep,e);obs=read(gp+'soft-selector-observations-v27.json')
    for group in obs.values():
        for row in group.values():row.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
    write(gp+'tail-risk-selector-observations-v28.json',obs);end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];assert duration>0;g.record_work(s,'controller-tail-risk-selector-v28',duration);result=evaluate(s,obs,ROOT)
    assert result['round']==49 and result['decision']=='iterate' and s['history'][:-1]==old['history'];assert s['floors']==old['floors'] and s['passed_checks']==old['passed_checks'] and s['passed_progress_milestones']==old['passed_progress_milestones'];assert cp['deadline_unix']==1788981845. and s['contract']['max_goalposts']==50
    result['evidence_transport_note']='Formal observations unknown because current host-signed assessments cannot be produced. Raw evidence retained, historical floors not reset.';s['history'][-1]=result;write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result)+'\n\n'+result['evidence_transport_note']+'\n')
    cp.update(state_path=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=49,remaining_evaluations=1,evidence=ep,decision=result['decision'],next_controller_monotonic_start=end,pending_document_revisions={},active_jobs=[],stagnant_rounds=s['stagnant_rounds'],recorded_at=time.time(),current_turn_classification='Progress: v28 fully reproduced,72native cases and1728edit probes completed;stronger training objective fails3developmentcohorts. No promotion.')
    cp['next_safe_actions']=['Complete one final requirements, package, evidence and scope audit; checkpoint at50evaluations without silently extending limits.','Preserve all rejected research variants, original50evaluationceiling and2026-09-09T19:24:05Zdeadline. One evaluation remains.','Use evaluate_milestone_goal_v2; never forge assessment signatures or clear floors.','No production promotion,confirmation acquisition,Git publication or parity claim while full-scope requirements remain unmet.'];write(base+'checkpoint-tail-risk-selector-v28.json',cp)
    print(dict(round=49,remaining_evaluations=1,decision=result['decision'],native_cases=72,failed_cohorts=3,work_seconds=duration,next_controller_monotonic_start=end,full_goal_complete=False))
if __name__=='__main__':main()
