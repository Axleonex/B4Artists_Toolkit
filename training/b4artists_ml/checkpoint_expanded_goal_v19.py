"""Record v19 evidence without changing the original endpoint or resumed limits."""
from pathlib import Path
import json,hashlib,sys,time,copy,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[r'\\100.114.2.71\Gdrive\LapArt\hermes-agent-self-evolution',str(Path(__file__).resolve().parent)]
from prime_bridge import goalposts as g
from evaluate_milestone_goal import evaluate

def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def write(p,d):(ROOT/p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def main():
    base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/'
    prior=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-shape-trajectory-v18.json';dest=prior.replace('shape-trajectory-v18','expanded-trajectory-v19');assert not (ROOT/dest).exists()
    old=read(prior);s=copy.deepcopy(old);cp=read(base+'checkpoint-shape-trajectory-v18.json');prev_ev=gp+'shape-trajectory-evidence-v18.json';e=read(prev_ev)
    model=read(res+'expanded_trajectory_v19/report.json');repro=read(res+'expanded-trajectory-reproduction-v19.json');assert repro['passed'] and repro['model_artifacts']==6
    for n,h in repro['identical_sha256'].items():assert sha(res+'expanded_trajectory_v19/'+n)==h==sha(res+'expanded_trajectory_v19_repeat/'+n)
    a=copy.deepcopy(model);b=read(res+'expanded_trajectory_v19_repeat/report.json')
    for report in [a,b]:
        report.pop('runtime');report['model_files']={Path(k).name:v for k,v in report['model_files'].items()}
    assert a==b
    oldmodel=read(res+'shape_trajectory_v18/report.json');assert model['protocol']['gates']==oldmodel['protocol']['gates'];assert model['protocol']['projection']==oldmodel['protocol']['projection'];assert model['protocol']['experiments']==oldmodel['protocol']['experiments']
    for name,row in oldmodel['baselines'].items():assert model['partition_reports']['old_validation'][name]==row
    audit=read(res+'temporal-data-audit-v19.json');acquisition=read(res+'temporal-acquisition-checks-v19.json');live=read(res+'temporal-acquisition-live-verification-v19.json');assert all(x['passed'] for x in [audit,acquisition,live]) and acquisition['cases']==14
    plan=read(tr+'temporal_expansion_plan_v19.json');assert all(not (ROOT/tr/'cache'/(c+'.bvh')).exists() for c in plan['planned_splits']['confirmation']);assert not model['confirmation_read']
    moving=read(res+'expanded-trajectory-host-v19.json');stationary=read(res+'stationary-trajectory-host-v19.json')
    for row in [moving,stationary]:assert row['passed'] and row['complete'] and len(row['rows'])==16 and row['model_sha256']==model['selection']['best_learned_sha256']
    meta=read(base+'package-test-v0.17.2.json');assert meta['ready_for_local_testing'];assert sha('releases/b4artists_ml_v0.17.2.zip')==meta['sha256']
    current={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'b4artists_ml').glob('*.py')};assert current==meta['runtime_sha256']==moving['runtime_sha256']==stationary['runtime_sha256']
    with zipfile.ZipFile(ROOT/'releases/b4artists_ml_v0.17.2.zip') as z:assert all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist())
    changed=[p for p,h in e['artifacts'].items() if sha(p)!=h];assert set(changed)<={base+n+'.md' for n in ['PROJECT','ROADMAP','REQUIREMENTS']},changed
    names=['temporal_expansion_plan_v19.json','temporal_expansion_manifest_v19.json','temporal_training_manifest_v19.json','expanded_trajectory_protocol_v19.json','fetch_cmu_temporal_v19.py','check_temporal_acquisition_v19.py','prepare_temporal_expansion_v19.py','train_expanded_trajectory_v19.py','check_expanded_trajectory_host_v19.py','check_stationary_trajectory_host_v19.py','check_expanded_reproduction_v19.py','checkpoint_expanded_goal_v19.py']
    inputs=[tr+n for n in names]+[base+n+'.md' for n in ['EXPANDED-TRAJECTORY-PLAN-v19','EXPANDED-TRAJECTORY-v19']];added=[p for p in inputs if p not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract'])
    s['explicit_revisions'].append(dict(reason='Fixed data-coverage expansion with pre-fit split freeze and duplicate exclusion; actual learned architecture/gates unchanged and separate old/new/combined validation required. Original endpoint, floors and50-evaluation/15-hour resumed limits unchanged.',prior_state=prior,prior_sha256=sha(prior),prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],added_inputs=added,recorded_at=time.time()))
    fp=g.fingerprint(ROOT,s['contract']['inputs'])
    route_path=gp+'temporal-expansion-routing-v19.json';route=read(route_path);route['validation_results']=dict(acquisition_cases=14,training_coordinate_audit=True,training_clips=78,training_windows=7358,duplicate_excluded=True,confirmation_untouched=True,reproduction_passed=True,identical_artifacts=6,moving_rig_cases=16,stationary_rig_cases=16,development_quality_passed=model['gates']['best_learned']['passed'],full_goal_complete=False);write(route_path,route)
    paths=set(e['artifacts'])|set(inputs)|{prior,prev_ev,route_path,tr+'cache/cmu-tree-v19.json'}
    for pattern in ['temporal-*v19.json','expanded-*v19*.json','stationary-trajectory-host-v19*.json']:
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res).glob(pattern) if p.is_file())
    for folder in ['expanded_trajectory_v19','expanded_trajectory_v19_repeat']:paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res/folder).glob('*') if p.is_file())
    for row in read(tr+'temporal_expansion_manifest_v19.json')['files']:
        if row['status']=='complete':paths.add(tr+'cache/'+row['clip']+'.bvh')
    e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={p:sha(p) for p in sorted(paths)},previous_evidence_recheck=dict(path=prev_ev,sha256=sha(prev_ev),changed_artifacts=changed,all_other_prior_artifacts_unchanged=True),learned_host=moving,stationary_host=stationary,temporal_selection=model['selection'],temporal_gates=model['gates'],development_gates=model['development_gates'],reproduction=repro,expanded_training_audit=audit,acquisition_checks=acquisition,acquisition_live=live,preserved_milestones=old['passed_progress_milestones'],new_passing_milestones=[])
    e['regression']['note']='0.17.2 runtime and package bytes unchanged. Prior317-case coverage,124 offline package cases and six actual-window events remain retained evidence; v19 research/rig checks are not a fresh full-runtime regression.'
    e['qualification'].update(full_goal_complete=False,temporal_model_qualification=False,temporal_animator_integration=False,host_shutdown=False,independent_usability='unknown',full_physics_acceptance=False)
    e['limitations']=['Data expansion is a coverage experiment, not original-goal completion. Separate old/new/combined quality results are recorded without threshold changes or dilution.','Model and all non-runtime diagnostics reproduce, but no temporal weights are promoted. Six fresh confirmation clips remain absent.','A planned training clip duplicated protected validation; exact-byte checking excluded it without replacement before fitting. Catalog prefixes do not imply independent actors.','78 training clips contain17.1minutes of source motion;7358 windows are correlated samples, not independent recordings.','32actual-rig recovery checks remain separate from independent human quality, broad production/quadruped support, responsiveness and Cascadeur comparison. Host shutdown still fails.','All original standalone, learned motion, physics/refinement, rig, distribution, optional connector and independent usability/comparison requirements remain.']
    args=['git','-c','safe.directory=X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github'];assert subprocess.check_output(args+['log','-1','--format=%H %an <%ae> %cn <%ce>'],cwd=ROOT,text=True).strip()==cp['publication']['head'];assert not subprocess.check_output(args+['diff','--name-only'],cwd=ROOT,text=True).strip();assert not subprocess.check_output(args+['diff','--cached','--name-only'],cwd=ROOT,text=True).strip()
    ep=gp+'expanded-trajectory-evidence-v19.json';write(ep,e);obs=read(gp+'shape-trajectory-observations-v18.json')
    for group in obs.values():
        for proof in group.values():proof.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
    write(gp+'expanded-trajectory-observations-v19.json',obs)
    end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];event='controller-expanded-trajectory-v19';assert event not in s['work_events'];g.record_work(s,event,duration);result=evaluate(s,obs,ROOT)
    assert result['round']==32 and result['decision']=='iterate';assert not result['implementation_progress']['new'] and not result['implementation_progress']['lost'];assert all(not c['regression'] for c in result['categories'].values());assert s['history'][:-1]==old['history'];assert cp['max_goalposts']==50 and cp['resumed_run_time_cap_hours']==15
    write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result),encoding='utf-8')
    cp.update(state_path=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=32,remaining_evaluations=18,decision=result['decision'],stagnant_rounds=s['stagnant_rounds'],evidence=ep,active_jobs=[],next_controller_monotonic_start=end,current_turn_classification='Progress: frozen bounded data expansion, live duplicate-leak prevention, training coordinate checks, actual learned model/reproduction and32real-rig checks complete. No temporal weights promoted.',work_accounting='Recorded controller-expanded-trajectory-v19 once from310880.5006178; all acquisition, training, reproduction and host handles terminal.',next_safe_actions=['Read original objective and this checkpoint; preserve50 total evaluations and15-hour resumed deadline.','Inspect separate old/new/combined gates before deciding the next experiment. If development fails, keep confirmation sealed. Diagnose training-only capacity/objective/continuity weaknesses before another prospectively fixed model. Do not retune v19 on validation.','Preserve original protected holdouts and all stricter matched procedural controls; retain excluded83_01 duplicate record.','Continue original physics/refinement, broader humanoid/quadruped, performance, optional connector, distribution and independent animator/equivalent Cascadeur requirements.'],recorded_at=time.time())
    write(base+'checkpoint-expanded-trajectory-v19.json',cp)
    progress=read(base+'expanded-trajectory-progress-v19.json');progress.update(status='evaluated',active_jobs=[],latest_checkpoint=base+'checkpoint-expanded-trajectory-v19.json',remaining_evaluations=18,recorded_at=time.time());write(base+'expanded-trajectory-progress-v19.json',progress)
    print(json.dumps(dict(round=32,remaining=18,decision=result['decision'],stagnant_rounds=s['stagnant_rounds'],work_seconds=duration,full_goal_complete=False)))
if __name__=='__main__':main()
