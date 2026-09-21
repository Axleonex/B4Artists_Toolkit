"""Record completed shape-reference research without narrowing the original goal."""
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
    prior=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-readout-trajectory-v17.json';dest=prior.replace('readout-trajectory-v17','shape-trajectory-v18');assert not (ROOT/dest).exists()
    old=read(prior);s=copy.deepcopy(old);cp=read(base+'checkpoint-readout-trajectory-v17.json');prev_ev=gp+'readout-trajectory-evidence-v17.json';e=read(prev_ev)
    model=read(res+'shape_trajectory_v18/report.json');repro=read(res+'shape-trajectory-reproduction-v18.json');assert repro['passed'] and repro['model_artifacts']==6
    a=copy.deepcopy(model);b=read(res+'shape_trajectory_v18_repeat/report.json');a.pop('runtime');b.pop('runtime');assert a==b
    assert all(sha(res+'shape_trajectory_v18/'+n)==h==sha(res+'shape_trajectory_v18_repeat/'+n) for n,h in repro['identical_sha256'].items())
    oldmodel=read(res+'readout_trajectory_v17/report.json');assert model['protocol']['gates']==oldmodel['protocol']['gates'];assert model['protocol']['projection']==oldmodel['protocol']['projection'];assert set(model['baselines'])==set(oldmodel['baselines'])|{'projected_shape'}
    for k in oldmodel['baselines']:assert oldmodel['baselines'][k]==model['baselines'][k]
    assert not model['gates']['best_learned']['passed']
    moving=read(res+'shape-trajectory-host-v18.json');stationary=read(res+'stationary-trajectory-host-v18.json')
    for row in [moving,stationary]:assert row['passed'] and row['complete'] and len(row['rows'])==16 and row['model_sha256']==model['selection']['best_learned_sha256']
    checks=[read(res+'shape-reference-checks-v18.json'),read(res+'shape-trajectory-checks-v18.json')];assert all(c['passed'] for c in checks)
    meta=read(base+'package-test-v0.17.2.json');assert meta['ready_for_local_testing'];assert sha('releases/b4artists_ml_v0.17.2.zip')==meta['sha256']
    current={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'b4artists_ml').glob('*.py')};assert current==meta['runtime_sha256']==moving['runtime_sha256']==stationary['runtime_sha256']
    with zipfile.ZipFile(ROOT/'releases/b4artists_ml_v0.17.2.zip') as z:assert all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist())
    changed=[p for p,h in e['artifacts'].items() if sha(p)!=h];assert set(changed)<={base+n+'.md' for n in ['PROJECT','ROADMAP','REQUIREMENTS']},changed
    names=['shape_reference.py','check_shape_reference_v18.py','diagnose_shape_reference_v18.py','diagnose_startup_context_v18.py','shape_trajectory.py','shape_readout.py','shape_trajectory_protocol_v18.json','check_shape_trajectory_v18.py','train_shape_trajectory_v18.py','check_shape_trajectory_host_v18.py','check_stationary_trajectory_host_v18.py','checkpoint_shape_goal_v18.py']
    inputs=[tr+n for n in names]+[base+n+'.md' for n in ['SHAPE-REFERENCE-DIAGNOSIS-v18','SHAPE-TRAJECTORY-PLAN-v18','SHAPE-TRAJECTORY-v18']];added=[p for p in inputs if p not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract'])
    s['explicit_revisions'].append(dict(reason='Declare training-only overshoot/startup diagnoses, independently checked procedural reference and frozen actual learned residual experiment. Original endpoint, thresholds, regression floors and limits unchanged. Add a stricter matched procedural control so its gains cannot qualify ML.',prior_state=prior,prior_sha256=sha(prior),prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],added_inputs=added,recorded_at=time.time()))
    fp=g.fingerprint(ROOT,s['contract']['inputs'])
    for path in [gp+'shape-reference-routing-v18.json',gp+'shape-trajectory-routing-v18.json']:
        r=read(path);r['validation_results']=dict(reference_checks=6,learned_math_checks=7,reproduction_passed=True,identical_artifacts=6,moving_rig_cases=16,stationary_rig_cases=16,temporal_quality_passed=False,host_shutdown=False,full_goal_complete=False);write(path,r)
    paths=set(e['artifacts'])|set(inputs)|{prior,prev_ev,res+'startup-context-diagnostic-v18.json',base+'readout-work-accounting-v17.json'}
    for folder,patterns in [(res,['shape*.json','stationary-trajectory-host-v18*.json']),(gp,['shape-reference-routing-v18.json','shape-trajectory-routing-v18.json'])]:
        for pattern in patterns:paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/folder).glob(pattern) if p.is_file())
    for folder in ['shape_trajectory_v18','shape_trajectory_v18_repeat']:paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res/folder).glob('*') if p.is_file())
    e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={p:sha(p) for p in sorted(paths)},previous_evidence_recheck=dict(path=prev_ev,sha256=sha(prev_ev),changed_artifacts=changed,all_other_prior_artifacts_unchanged=True),learned_host=moving,stationary_host=stationary,temporal_selection=model['selection'],temporal_gates=model['gates'],reproduction=repro,shape_reference_diagnostic=read(res+'shape-reference-diagnostic-v18.json'),startup_context_diagnostic=read(res+'startup-context-diagnostic-v18.json'),focused_research_checks=checks,preserved_milestones=old['passed_progress_milestones'],new_passing_milestones=[])
    e['regression']['note']='0.17.2 runtime and package bytes unchanged since the prior evaluated state. Prior317-case coverage,124 offline package cases and six actual-window events remain explicitly retained evidence. v18 research/rig checks do not imply a fresh full-runtime regression.'
    e['qualification'].update(full_goal_complete=False,temporal_model_qualification=False,temporal_animator_integration=False,host_shutdown=False,independent_usability='unknown',full_physics_acceptance=False)
    e['limitations']=['Shape-only reference improves position; actual learned correction adds only0.75%, failing the5% requirement. Acceleration and worst-cohort protection also fail. No temporal model promoted.','Worst cohort falls to2.742 times the best control but remains unacceptable; reference bounds alone suppress real motion arcs.','All original baselines/gates and held-out windows retained; additional shape-only baseline makes comparison stricter. Previously exposed validation is not blind confirmation.','Only7.8 minutes of distinct training motion; no new data acquired. Startup diagnostic found no reason to exclude first-motion windows.','Actual-rig32-case recovery passes; this is separate from human quality, broad production/quadruped support, responsiveness and Cascadeur comparison. Host shutdown still fails.','All original standalone, learned motion, physics/refinement, rig, distribution, optional connector and independent usability/comparison requirements remain.']
    args=['git','-c','safe.directory=X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github'];assert subprocess.check_output(args+['log','-1','--format=%H %an <%ae> %cn <%ce>'],cwd=ROOT,text=True).strip()==cp['publication']['head'];assert not subprocess.check_output(args+['diff','--name-only'],cwd=ROOT,text=True).strip();assert not subprocess.check_output(args+['diff','--cached','--name-only'],cwd=ROOT,text=True).strip()
    ep=gp+'shape-trajectory-evidence-v18.json';write(ep,e);obs=read(gp+'readout-trajectory-observations-v17.json')
    for group in obs.values():
        for proof in group.values():proof.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
    write(gp+'shape-trajectory-observations-v18.json',obs)
    end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];event='controller-shape-trajectory-v18';assert event not in s['work_events'];g.record_work(s,event,duration);result=evaluate(s,obs,ROOT)
    assert result['round']==31 and result['decision']=='iterate';assert not result['implementation_progress']['new'] and not result['implementation_progress']['lost'];assert all(not c['regression'] for c in result['categories'].values());assert s['history'][:-1]==old['history']
    write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result),encoding='utf-8')
    cp.update(state_path=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=31,remaining_evaluations=19,decision=result['decision'],stagnant_rounds=s['stagnant_rounds'],evidence=ep,active_jobs=[],next_controller_monotonic_start=end,current_turn_classification='Progress: training-only reference/startup diagnosis, new supervised trajectory model, complete deterministic reproduction and32actual-rig checks complete. Quality fails; no temporal model promoted.',work_accounting='Recorded controller-shape-trajectory-v18 once from309531.1006512; all original/reproduction/host handles terminal.',next_safe_actions=['Read original objective and this state; preserve50 total evaluations and15-hour resumed deadline.','Prioritize a bounded, prospectively specified expansion of distinct motion coverage using verified publisher terms. Preserve every old holdout and define any new confirmation set before fitting; never call catalog prefixes independent actors.','Keep the stricter shape-only control and unchanged quality thresholds. The learned model must supply improvement beyond procedural baselines. No post-validation retuning of v18.','Complete original physics/refinement, broader humanoid/quadruped, performance, optional connector, distribution and independent animator/equivalent Cascadeur requirements.'],recorded_at=time.time())
    write(base+'checkpoint-shape-trajectory-v18.json',cp)
    print(json.dumps(dict(round=31,remaining=19,decision=result['decision'],stagnant_rounds=s['stagnant_rounds'],work_seconds=duration,full_goal_complete=False)))
if __name__=='__main__':main()
