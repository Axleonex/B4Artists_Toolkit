"""Preserve v27 results and full-goal history at evaluation48."""
import copy,time,subprocess,zipfile
from checkpoint_expanded_goal_v19 import ROOT,read,write,sha,g
from evaluate_milestone_goal_v2 import evaluate

def main():
    base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/'
    cp=read(base+'checkpoint-projected-selector-v26.json');prior=cp['state_path'];old=read(prior);s=copy.deepcopy(old);previous=cp['evidence'];e=read(previous)
    dest=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-soft-selector-v27.json';assert not (ROOT/dest).exists()
    model=read(res+'soft_selector_v27/report.json');repro=read(res+'soft-selector-verification-v27.json');stability=read(res+'soft-selector-edit-stability-v27.json');diag=read(res+'soft-selector-training-v27.json')
    assert repro['passed'] and repro['deterministic_reports_equal'] and repro['cohorts']==96 and repro['failed']==2
    assert stability['complete'] and stability['cases']==1728 and stability['prior_hard_probes_reproduced_exactly'] and not stability['quality_qualification']
    assert diag['geometry_passed'] and diag['windows']==466 and not diag['validation_loaded']
    for name,h in repro['identical_sha256'].items():assert sha(res+'soft_selector_v27/'+name)==h==sha(res+'soft_selector_v27_repeat/'+name)
    native=[]
    for tag,n in [('soft-selector-host-v27',16),('stationary-soft-selector-host-v27',16),('soft-selector-journey-v27',15),('soft-selector-cooperative-v27',25)]:
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
        path=res+'soft-selector-document-baseline-v27/'+n.split('/')[-1];assert sha(path)==e['artifacts'][n];versions[n]=dict(path=path,sha256=sha(path))
    inputs=[tr+'checkpoint_soft_selector_v27.py',base+'SOFT-SELECTOR-v27.md'];added=[n for n in inputs if n not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract'])
    a=copy.deepcopy(s['contract']);b=copy.deepcopy(old['contract']);a.pop('inputs');b.pop('inputs');assert a==b
    s['explicit_revisions'].append(dict(reason='Fixed soft readout reproduced,72native checks pass;two of96cohorts still fail and tiny-edit amplification worsens. Preserve full endpoint and thresholds, sealed confirmation,50goalposts and deadline.',prior_state=prior,prior_sha256=sha(prior),prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],added_inputs=added,preserved_prior_versions=versions,recorded_at=time.time()))
    paths=set(e['artifacts'])|set(inputs)|{prior,previous,res+'projected-selector-reproduction-v26.json',tr+'verify_projected_selector_reproduction_v26.py',gp+'tail-risk-routing-v28.json'}
    for directory in ['soft_selector_v27','soft_selector_v27_repeat','soft-selector-document-baseline-v27','soft-selector-prefit-baseline-v27','projected-selector-checkpoint-path-fix-v26','soft-selector-checkpoint-prefix-fix-v27']:
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res/directory).rglob('*') if p.is_file())
    for directory,pattern in [(tr,'*v27*'),(res,'*soft-selector*v27*.json'),(tr+'cache/','*soft-selector*v27*.log'),('tests/','*soft_selector*v27*'),(gp,'*soft-selector*v27*.json')]:
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/directory).glob(pattern) if p.is_file())
    plan=read(tr+'temporal_expansion_plan_v19.json');assert all(not (ROOT/tr/'cache'/(c+'.bvh')).exists() for c in plan['planned_splits']['confirmation'])
    args=['git','-c','safe.directory=X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github'];assert subprocess.check_output(args+['log','-1','--format=%H %an <%ae> %cn <%ce>'],cwd=ROOT,text=True).strip()==cp['publication']['head']
    assert not subprocess.check_output(args+['diff','--name-only'],cwd=ROOT,text=True).strip();assert not subprocess.check_output(args+['diff','--cached','--name-only'],cwd=ROOT,text=True).strip()
    fp=g.fingerprint(ROOT,s['contract']['inputs']);e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={n:sha(n) for n in sorted(paths)},previous_evidence_recheck=dict(path=previous,sha256=sha(previous),changed_artifacts=changed,preserved_prior_versions=versions,all_other_prior_artifacts_unchanged=True),soft_selector=dict(report=model,reproduction=repro,edit_stability=stability,training_diagnostic=diag,native_checks=native,native_cases=72),projected_selector_full_reproduction=full)
    e['projected_selector_training'].update(repeat_complete_file_present=True,full_reproduction_verified=True,active_sessions=[])
    e['qualification'].update(full_goal_complete=False,temporal_model_qualification=False,temporal_animator_integration=False,full_responsiveness=False,independent_usability='unknown')
    e['limitations']=['v27fails2of96developmentcohorts;worst2.901379vs1.10limit. Newpartition passes, aggregate quality still unqualified.','Raw large-edit jumps improve but maximum tiny-edit position amplification worsens2.4to2.5fold. Quaternion readout has hemisphere-boundary limitations.','72native cases pass assertions, hostshutdownstill3221225477. No current GUI or independent animator qualification.','Full v26 training and v27 readout evaluation reproduce; no confirmation loaded or weights promoted.','Signed assessment producer unavailable; canonical observations unknown; historical floors and passed checks preserved.','Original complete standalone parity scope remains unmet, including learned generalization, physics, intent/style/contacts, quadrupeds, connector and equivalent comparison.']
    ep=gp+'soft-selector-evidence-v27.json';write(ep,e);obs=read(gp+'projected-selector-observations-v26.json')
    for group in obs.values():
        for row in group.values():row.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
    write(gp+'soft-selector-observations-v27.json',obs);end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];assert duration>0;g.record_work(s,'controller-soft-selector-v27',duration);result=evaluate(s,obs,ROOT)
    assert result['round']==48 and result['decision']=='iterate' and s['history'][:-1]==old['history'];assert s['floors']==old['floors'] and s['passed_checks']==old['passed_checks'] and s['passed_progress_milestones']==old['passed_progress_milestones'];assert cp['deadline_unix']==1788981845. and s['contract']['max_goalposts']==50
    result['evidence_transport_note']='Formal observations unknown because current host-signed assessments cannot be produced. Raw evidence retained, historical floors not reset.';s['history'][-1]=result;write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result)+'\n\n'+result['evidence_transport_note']+'\n')
    cp.update(state_path=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=48,remaining_evaluations=2,evidence=ep,decision=result['decision'],next_controller_monotonic_start=end,pending_document_revisions={},active_jobs=[],stagnant_rounds=s['stagnant_rounds'],recorded_at=time.time(),current_turn_classification='Progress: v27 fixed readout fully reproduced,72native cases and1728edit probes completed;two quality cohorts fail. No promotion.')
    cp['next_safe_actions']=['Freeze one training-only tail-risk objective on immutable v26labels; meaningful gradient/provenance checks before training and development evaluation. Do not retune v27 or relax gates.','Preserve full original endpoint,50evaluationceiling and2026-09-09T19:24:05Zdeadline. Two evaluations remain.','Use evaluate_milestone_goal_v2; never forge assessment signatures or clear floors.','No production promotion,confirmation acquisition,Git publication or parity claim while quality and full-scope requirements remain unmet.'];write(base+'checkpoint-soft-selector-v27.json',cp)
    print(dict(round=48,remaining_evaluations=2,decision=result['decision'],native_cases=72,failed_cohorts=2,work_seconds=duration,next_controller_monotonic_start=end,full_goal_complete=False))
if __name__=='__main__':main()
