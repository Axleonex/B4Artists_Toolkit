"""Record rejected v26 quality, native behavior and pending full reproduction."""
import copy,time,subprocess,zipfile
from checkpoint_expanded_goal_v19 import ROOT,read,write,sha,g
from evaluate_milestone_goal_v2 import evaluate

def main():
    base='docs/b4artists_ml/';gp=base+'goalposts/';tr='training/b4artists_ml/';res=tr+'results/'
    cp=read(base+'checkpoint-goalpost-adapter-v2.json');prior=cp['state_path'];old=read(prior);s=copy.deepcopy(old);previous=cp['evidence'];e=read(previous)
    dest=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-projected-selector-v26.json';assert not (ROOT/dest).exists()
    model=read(res+'projected_selector_v26/report.json');complete=read(res+'projected_selector_v26/complete.json');proof=read(res+'projected-selector-host-verification-v26.json');digest=model['selection']['best_learned_sha256']
    assert complete['complete'] and complete['report_sha256']==sha(res+'projected_selector_v26/report.json') and sha(res+'projected_selector_v26/best_learned.npz')==digest
    assert model['training_windows']==7358 and model['validation_windows']==768 and not model['gates']['best_learned']['passed'] and not model['confirmation_read']
    assert not (ROOT/res/'projected_selector_v26/confirmation_selection.json').exists()
    assert proof['complete'] and proof['native_cases']==72 and proof['model_sha256']==digest and not proof['development_qualified']
    for item in proof['checks']:assert item['passed'] and sha(item['path'])==item['sha256']
    for name,h in model['source_sha256'].items():assert sha(tr+name)==h,name
    parent=read(res+'kinematic_trajectory_v20/report.json');assert model['protocol']['gates']==parent['protocol']['gates'] and model['protocol']['projection']==parent['protocol']['projection']
    for part in ('old_validation','new_validation'):
        for name in model['protocol']['baselines']:assert model['partition_reports'][part][name]==parent['partition_reports'][part][name]
    diagnosis=read(res+'projected-selector-failure-attribution-v26.json');assert diagnosis['failed']==3 and diagnosis['cohorts']==96
    stability=read(res+'projected-selector-edit-stability-v26.json');assert stability['complete'] and stability['cases']==1728 and not stability['qualification'] and not stability['confirmation_read']
    repeat=res+'projected_selector_v26_repeat/';frozen=read(repeat+'selection_frozen.json');assert frozen['sha256']==digest==sha(repeat+'best_learned.npz') and not frozen['validation_loaded']
    # A frozen weights file does not establish complete reproduction.
    repeat_complete=(ROOT/repeat/'complete.json').exists()
    meta=read(base+'package-test-v0.17.5.json');runtime={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in (ROOT/'b4artists_ml').glob('*.py')};assert runtime==meta['runtime_sha256'] and sha(cp['artifact']['path'])==meta['sha256']==cp['artifact']['sha256']
    with zipfile.ZipFile(ROOT/cp['artifact']['path']) as z:assert all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist())
    changed=[n for n,h in e['artifacts'].items() if sha(n)!=h];assert set(changed)=={base+'PROJECT.md',base+'ROADMAP.md'},changed
    versions={}
    for n in changed:
        v=cp['pending_document_revisions'][n];assert sha(v['prior_version'])==v['before_sha256']==e['artifacts'][n] and sha(n)==v['after_sha256'];versions[n]=dict(path=v['prior_version'],sha256=v['before_sha256'])
    inputs=[tr+'checkpoint_projected_selector_v26.py',base+'PROJECTED-SELECTOR-v26.md'];added=[n for n in inputs if n not in s['contract']['inputs']];s['contract']['inputs']+=added;s['contract_hash']=g.digest(s['contract'])
    a=copy.deepcopy(s['contract']);b=copy.deepcopy(old['contract']);a.pop('inputs');b.pop('inputs');assert a==b
    s['explicit_revisions'].append(dict(reason='Frozen v26candidate and original matched controls complete;3of96cohorts fail and1728raw-edit probes expose hard-selection jumps.72native rig/action/cooperative cases pass; repeated frozen weights match, full reproduction pending. No qualification or confirmation. Preserve full endpoint,50evaluations,extended deadline and historical floors.',prior_state=prior,prior_sha256=sha(prior),prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],added_inputs=added,preserved_prior_versions=versions,recorded_at=time.time()))
    fp=g.fingerprint(ROOT,s['contract']['inputs']);paths=set(e['artifacts'])|set(inputs)|{prior,previous,res+'projected-selector-failure-attribution-v26.json',res+'projected-selector-edit-stability-v26.json',res+'projected-selector-primary-verification-v26.json',res+'projected-selector-host-verification-v26.json'}
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res/'projected_selector_v26').rglob('*') if p.is_file())
    paths.update(v['path'] for v in versions.values())
    for name in ('projected-selector-host-v26','stationary-projected-selector-host-v26','projected-selector-journey-v26','projected-selector-cooperative-v26'):
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/res).glob(name+'*.json') if p.is_file())
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/tr/'cache').glob(name+'*') if p.is_file())
    # Include only immutable already-frozen reproduction artifacts, no live log.
    paths.update(repeat+n for n in ('best_learned.npz','selection_frozen.json','label_manifest.json','labels.npz','cost_normalizers.json'))
    plan=read(tr+'temporal_expansion_plan_v19.json');assert all(not (ROOT/tr/'cache'/(c+'.bvh')).exists() for c in plan['planned_splits']['confirmation'])
    args=['git','-c','safe.directory=X:/Scripting Attempts/B4Artists_Tools/B4Artists_Anim_Tools_github'];assert subprocess.check_output(args+['log','-1','--format=%H %an <%ae> %cn <%ce>'],cwd=ROOT,text=True).strip()==cp['publication']['head'];assert not subprocess.check_output(args+['diff','--name-only'],cwd=ROOT,text=True).strip();assert not subprocess.check_output(args+['diff','--cached','--name-only'],cwd=ROOT,text=True).strip()
    e.update(contract_hash=s['contract_hash'],input_fingerprint=fp,artifacts={n:sha(n) for n in sorted(paths)},previous_evidence_recheck=dict(path=previous,sha256=sha(previous),changed_artifacts=changed,preserved_prior_versions=versions,all_other_prior_artifacts_unchanged=True),projected_selector_primary=model,projected_selector_diagnosis=diagnosis,projected_selector_edit_stability=stability,projected_selector_native=proof,projected_selector_training=dict(primary_complete=True,primary_session=23370,primary_exit=0,repeat_session=87876,repeat_weights_identical=True,repeat_complete_file_present=repeat_complete,full_reproduction_verified=False,active_sessions=[87876]))
    e['qualification'].update(full_goal_complete=False,temporal_model_qualification=False,temporal_animator_integration=False,trained_temporal_backend_native=True,full_responsiveness=False,independent_usability='unknown')
    e['limitations']=['v26average P improves5.16/7.39/6.59percent but fails3of96cohorts with2.90worst ratio; threshold1.10unchanged.','13of576small1e-3endpoint probes switch candidate; raw jumps reach1.624body-reference units and2.997radians.','72native cases pass through synchronous/cooperative research paths, not full product/animator qualification. Host shutdown crash persists.','Frozen repeated weights match; complete corpus/label/report reproduction still requires the prepared verifier after the repeat process finishes.','Current canonical signed-assessment envelopes remain unavailable; formal observations unknown and all original floors/history preserved.','Original physics/refinement, learned generalization, automatic contacts/intent/style, broader rigs/quadrupeds, connector, independent animator and equivalent Cascadeur comparison remain incomplete.']
    ep=gp+'projected-selector-evidence-v26.json';write(ep,e);obs=read(gp+'goalpost-adapter-observations-v2.json')
    for group in obs.values():
        for row in group.values():row.update(artifact=ep,sha256=sha(ep),input_fingerprint=fp)
    write(gp+'projected-selector-observations-v26.json',obs);end=time.perf_counter();duration=end-cp['next_controller_monotonic_start'];event='controller-projected-selector-v26';assert event not in s['work_events'];g.record_work(s,event,duration);result=evaluate(s,obs,ROOT)
    assert result['round']==47 and result['decision']=='iterate' and s['history'][:-1]==old['history'];assert s['floors']==old['floors'] and s['passed_checks']==old['passed_checks'] and s['passed_progress_milestones']==old['passed_progress_milestones'];assert cp['deadline_unix']==1788981845. and s['contract']['max_goalposts']==50
    result['evidence_transport_note']='Formal unknown evidence reflects unavailable current host-signed assessment envelopes. Raw motion-quality failures and passing native checks are retained; earlier floors and history are not reset.';s['history'][-1]=result
    write(dest,s);(ROOT/dest).with_suffix('.md').write_text(g.markdown(result)+'\n\n'+result['evidence_transport_note']+'\n')
    cp.update(state_path=dest,contract_hash=s['contract_hash'],input_fingerprint=fp,round=47,remaining_evaluations=3,evidence=ep,decision=result['decision'],next_controller_monotonic_start=end,pending_document_revisions={},active_jobs=[dict(session_id=87876,kind='independent_reproduction',command='train_projected_selector_v26.py --output projected_selector_v26_repeat',stage='weights frozen; development evaluation')],stagnant_rounds=s['stagnant_rounds'],recorded_at=time.time(),current_turn_classification='Progress: actual trained v26candidate, development rejection,1728edit probes and72native provider checks completed. Verified wait: repeated weights match and same87876handle remains live for development evaluation.')
    cp['latest_live_observation']=dict(primary=dict(session_id=23370,terminal=True,exit_code=0),reproduction=dict(session_id=87876,live=True,weights_frozen=True,model_sha256=digest),native_validation_chain=dict(session_id=45704,terminal=True,exit_code=0),recorded_at=time.time())
    cp['cooperative_research']=dict(evidence=res+'projected-selector-host-verification-v26.json',native_cases=72,trained_provider_tested=True,ui_integrated=False,full_responsiveness=False)
    cp['next_safe_actions']=['Poll existing87876until terminal, then run verify_projected_selector_reproduction_v26.py once. Primary23370and validation45704are terminal; do not restart.','v26is unqualified: preserve weights/protocol/data/results and sealed confirmation.72native cases do not override3failed development groups or editing discontinuities.','Inspect training-only proposal/selector evidence for a fixed continuous alternative; freeze any new experiment before evaluation. Do not tune the rejected v26weights or relax original gates.','Use current evaluate_milestone_goal_v2; authenticated assessment receipts remain unavailable, so formal unknown checks do not erase earlier evidence/floors.','Full original goal remains active:47of50evaluations used,three remain; deadline2026-09-09T19:24:05Z.']
    write(base+'checkpoint-projected-selector-v26.json',cp)
    live=read(base+'projected-pool-progress-v26.json');live.update(latest_checkpoint=base+'checkpoint-projected-selector-v26.json',round=47,remaining_evaluations=3,active_jobs=cp['active_jobs'],primary_complete=True,quality_qualified=False,repeat_weights_identical=True,recorded_at=time.time());write(base+'projected-pool-progress-v26.json',live)
    print(dict(round=47,remaining_evaluations=3,decision=result['decision'],primary_qualified=False,native_cases=72,repeat_weights_identical=True,active_sessions=[87876],work_seconds=duration,next_controller_monotonic_start=end,full_goal_complete=False))
if __name__=='__main__':main()
