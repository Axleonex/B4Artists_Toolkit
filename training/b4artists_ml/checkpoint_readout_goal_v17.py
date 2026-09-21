"""Preserve the full goal and record the completed readout research evaluation."""
from pathlib import Path
import json,hashlib,sys,time,copy,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[r'\\100.114.2.71\Gdrive\LapArt\hermes-agent-self-evolution',str(Path(__file__).resolve().parent)]
from prime_bridge import goalposts as g
from evaluate_milestone_goal import evaluate

def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def write(p,d):(ROOT/p).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def main():
    base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/'
    prior=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-momentum-transitions-v1.json';dest=prior.replace('momentum-transitions-v1','readout-trajectory-v17')
    assert not (ROOT/dest).exists();old=read(prior);s=copy.deepcopy(old);cp=read(base+'checkpoint-momentum-transitions-v1.json')
    model=read(res+'readout_trajectory_v17/report.json');repeat=read(res+'readout-trajectory-reproduction-v17.json');assert repeat['passed'] and repeat['model_artifacts']==14
    a=copy.deepcopy(model);b=read(res+'readout_trajectory_v17_repeat/report.json');a.pop('runtime');b.pop('runtime');assert a==b
    assert all(sha(res+'readout_trajectory_v17/'+n)==h==sha(res+'readout_trajectory_v17_repeat/'+n) for n,h in repeat['identical_sha256'].items())
    assert not model['gates']['best_learned']['passed']
    moving=read(res+'readout-trajectory-host-v17.json');stationary=read(res+'stationary-trajectory-host-v17.json')
    for result in [moving,stationary]:assert result['passed'] and result['complete'] and len(result['rows'])==16 and result['model_sha256']==model['selection']['best_learned_sha256']
    native=read(res+'readout-preflight-v17-corrected-regression.json');assert len(native)==1 and native[0]['assertions_passed'] and native[0]['tests']==3
    meta=read(base+'package-test-v0.17.2.json');assert meta['ready_for_local_testing'] and meta['visual_inspection']['passed'] and meta['packaged_ui_qualification']=='passed'
    current={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'b4artists_ml').glob('*.py')};assert current==meta['runtime_sha256']==moving['runtime_sha256']==stationary['runtime_sha256']
    assert sha('releases/b4artists_ml_v0.17.2.zip')==meta['sha256']
    with zipfile.ZipFile(ROOT/'releases/b4artists_ml_v0.17.2.zip') as z,zipfile.ZipFile(ROOT/'releases/b4artists_ml_v0.17.1.zip') as oldzip:
        assert all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist())
        assert z.namelist()==oldzip.namelist();assert {n for n in z.namelist() if z.read(n)!=oldzip.read(n)}=={'b4artists_ml/ui.py','b4artists_ml/__init__.py'}
    prev_ev=gp+'momentum-transitions-evidence-v1.json';e=read(prev_ev);changed=[p for p,h in e['artifacts'].items() if sha(p)!=h]
    allowed={base+n+'.md' for n in ['PROJECT','ROADMAP','REQUIREMENTS','USER_GUIDE']}|{'b4artists_ml/ui.py','b4artists_ml/__init__.py'};assert set(changed)<=allowed,changed
    names=['build_transition_label_package.py','audit_temporal_coverage_v1.py','readout_trajectory.py','readout_trajectory_protocol_v17.json','train_readout_trajectory_v17.py','check_readout_trajectory_host_v17.py','check_stationary_trajectory_host_v17.py','checkpoint_readout_goal_v17.py']
    new_inputs=[tr+n for n in names]+['tests/test_b4artists_ml_readout.py']+[base+n+'.md' for n in ['TEMPORAL-COVERAGE-AUDIT-v1','TEMPORAL-DATA-OPTIONS-v17','READOUT-TRAJECTORY-PLAN-v17','READOUT-TRAJECTORY-v17','DISTRIBUTION-RECHECK-v17']]
    added=[p for p in new_inputs if p not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract'])
    s['explicit_revisions'].append(dict(reason='Declare presentation-only patch verification, training-only coverage audit and frozen exact learned readout experiment; retain every original endpoint, quality threshold, milestone, regression floor and authorized limit.',prior_state=prior,prior_sha256=sha(prior),prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],added_inputs=added,recorded_at=time.time()))
    fp=g.fingerprint(ROOT,s['contract']['inputs'])
    for path in [gp+'temporal-audit-routing-v1.json',gp+'readout-trajectory-routing-v17.json']:
        rr=read(path);rr['validation_results']=dict(coverage_audit=res+'temporal-coverage-audit-v1.json',native_readout_tests=3,readout_reproduction=repeat['passed'],identical_model_artifacts=14,moving_actual_rig_cases=16,stationary_actual_rig_cases=16,temporal_quality_passed=False,full_goal_complete=False);write(path,rr)
    paths=set(e['artifacts'])|set(new_inputs)|{prior,prev_ev,'releases/b4artists_ml_v0.17.2.zip',base+'package-test-v0.17.2.json',base+'native-ui-transition-label-package-v1.json',res+'native-ui-process-transition-label-package-v1.json',res+'temporal-coverage-audit-v1.json',res+'cmu-publisher-recheck-v17.json'}
    for folder,patterns in [(res,['readout*.json','stationary-trajectory-host-v17*.json']),(gp,['transition-label-routing-v1.json','temporal-audit-routing-v1.json','readout-trajectory-routing-v17.json'])]:
        for pattern in patterns:paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/folder).glob(pattern))
    for folder in ['readout_trajectory_v17','readout_trajectory_v17_repeat']:
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res/folder).glob('*') if p.is_file())
    publisher=read(res+'cmu-publisher-recheck-v17.json')
    for row in publisher:
        p=Path(row['Path']);assert row['Status']==200 and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA256'];paths.add(p.relative_to(ROOT).as_posix())
    e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={p:sha(p) for p in sorted(paths)},package=dict(path='releases/b4artists_ml_v0.17.2.zip',sha256=meta['sha256'],files=meta['files'],bytes=meta['bytes'],matches_current_source=True,experimental=True),previous_evidence_recheck=dict(path=prev_ev,sha256=sha(prev_ev),changed_artifacts=changed,all_other_prior_artifacts_unchanged=True),packaged_ui=meta['packaged_ui'],focused_native=dict(cases=3,suites=1,assertions_passed=True,host_shutdown_passed=False),learned_host=moving,stationary_host=stationary,temporal_selection=model['selection'],temporal_gates=model['gates'],reproduction=repeat,coverage_audit=read(res+'temporal-coverage-audit-v1.json'),preserved_milestones=old['passed_progress_milestones'],new_passing_milestones=[],publisher_recheck=dict(current_cmu_publisher_retrieved=True,scope='CMU source usage terms only; no blanket licensing qualification',artifact=res+'cmu-publisher-recheck-v17.json'))
    e['regression']['presentation_patch_evidence']=base+'package-test-v0.17.2.json';e['regression']['note']='Prior317-case coverage retained with exact two-file presentation audit; six actual-window events rerun on0.17.2. Three new research solver cases are a separate focused check. No fresh full-regression claim.'
    e['qualification'].update(full_goal_complete=False,temporal_model_qualification=False,temporal_animator_integration=False,host_shutdown=False,independent_usability='unknown',full_physics_acceptance=False)
    e['limitations']=['Learned v17 improves position2.6%, but required5%, acceleration and worst-cohort protection fail. No temporal weights promoted.','Only465.865 seconds of training motion across31clips/13catalog groups; group IDs are not independent actors.','Worst contextual long transition is a substantial reference overshoot: linear0.074618, Hermite1.000332, learned0.875952 body units. Future diagnosis must preserve old held-out evidence.','Actual-rig integration and stationary source recovery pass32cases; these do not prove learned-motion visual quality, broad production/quadruped support, or Cascadeur parity.','Host shutdown crash persists. Human usability and direct comparative assessments remain unknown.','Fresh CMU publisher retrieval gap is resolved; unrelated code/weights/data and optional Cascadeur entitlement remain separate checks.','0.17.2 fixes labels only, inheriting explicitly audited behavioral/offline coverage. All original physics/refinement, standalone, rig, learned animation, connector and comparison requirements remain.']
    args=['git','-c','safe.directory=X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github'];head=subprocess.check_output(args+['log','-1','--format=%H %an <%ae> %cn <%ce>'],cwd=ROOT,text=True).strip();assert head==cp['publication']['head'];assert not subprocess.check_output(args+['diff','--name-only'],cwd=ROOT,text=True).strip();assert not subprocess.check_output(args+['diff','--cached','--name-only'],cwd=ROOT,text=True).strip()
    ep=gp+'readout-trajectory-evidence-v17.json';write(ep,e);obs=read(gp+'momentum-transitions-observations-v1.json')
    for group in obs.values():
        for proof in group.values():proof.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
    write(gp+'readout-trajectory-observations-v17.json',obs)
    end=time.perf_counter();event='controller-readout-trajectory-v17';assert event not in s['work_events'];g.record_work(s,event,end-cp['next_controller_monotonic_start']);out=evaluate(s,obs,ROOT)
    assert out['round']==30 and out['decision']=='iterate';assert not out['implementation_progress']['new'] and not out['implementation_progress']['lost'];assert all(not c['regression'] for c in out['categories'].values());assert s['history'][:-1]==old['history']
    write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(out),encoding='utf-8')
    cp.update(state_path=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=30,remaining_evaluations=20,decision=out['decision'],stagnant_rounds=s['stagnant_rounds'],evidence=ep,artifact=e['package'],active_jobs=[],next_controller_monotonic_start=end,current_turn_classification='Progress: exact learned readout implementation/reproduction and32actual-rig diagnostics complete; current CMU publisher source recovered. Quality still fails; no temporal promotion.',work_accounting='Recorded controller-readout-trajectory-v17 once from307467.7241804 across label package, coverage audit, mathematical verification, original/reproduction training, host checks and publisher verification. All known jobs terminal.',next_safe_actions=['Read the original objective and this same state, preserving50 total evaluations and the15-hour resumed deadline.','Diagnose contextual-reference overshoot on training clips and known observations. Do not retune v17 against its already observed validation or change gates.','Prospectively freeze a coherent next learned experiment or bounded rights-checked data expansion only after diagnosis. Preserve all held-out splits, artifacts and failures.','Complete all original physics/refinement, wider humanoid/quadruped, responsiveness, optional connector, distribution and independent animator/equivalent Cascadeur requirements.'],recorded_at=time.time())
    write(base+'checkpoint-readout-trajectory-v17.json',cp)
    print(json.dumps(dict(round=30,remaining=20,decision=out['decision'],stagnant_rounds=s['stagnant_rounds'],scores={k:v['score'] for k,v in out['categories'].items()},work_seconds=end-cp['next_controller_monotonic_start'],full_goal_complete=False)))
if __name__=='__main__':main()
