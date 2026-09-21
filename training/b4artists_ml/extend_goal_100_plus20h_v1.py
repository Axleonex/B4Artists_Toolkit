"""Apply the user's explicit total-evaluation and deadline extension in place."""
import copy,time,datetime
from checkpoint_expanded_goal_v19 import ROOT,read,write,sha,g

def main():
 base='docs/b4artists_ml/';gp=base+'goalposts/';cp=read(base+'checkpoint-broader-shape-v1.json');prior=cp['state_path'];old=read(prior);s=copy.deepcopy(old);prior_evidence=cp['evidence'];e=read(prior_evidence);receipt=read('training/b4artists_ml/results/shape-runtime-baseline-v1/receipt.json')
 dest=gp+'01a073fe-c240-70c0-b5cd-fe9653aac60e-limit100-plus20h-v1.json';assert not (ROOT/dest).exists();assert cp['round']==56 and len(s['history'])==56 and cp['max_goalposts']==s['contract']['max_goalposts']==75
 changed=[n for n,h in e['artifacts'].items() if sha(n)!=h];expected={'b4artists_ml/'+n for n in ('__init__.py','ui.py','temporal_preview.py','contacts.py')};assert set(changed)==expected,changed;pending={}
 for n in changed:
  r=receipt[n];assert sha(r['prior_version'])==r['before_sha256']==e['artifacts'][n];pending[n]=dict(**r,after_sha256=sha(n))
 old_deadline=cp['deadline_unix'];new_deadline=old_deadline+20*3600;s['contract']['max_goalposts']=100;s['contract']['max_wall_seconds']+=20*3600;s['contract_hash']=g.digest(s['contract'])
 a=copy.deepcopy(s['contract']);b=copy.deepcopy(old['contract'])
 for k in ('max_goalposts','max_wall_seconds'):a.pop(k);b.pop(k)
 assert a==b
 revision=dict(reason='Explicit user extension:100total evaluations and20additional hours beyond the existing deadline. Same goal, endpoint, history, floors, evidence, cadence and stagnation policy; no evaluation consumed.',authorization='Set evaluation limit to 100, add 20 more hours.',prior_state=prior,prior_sha256=sha(prior),prior_contract_hash=old['contract_hash'],new_contract_hash=s['contract_hash'],before_max_goalposts=75,after_max_goalposts=100,before_deadline_unix=old_deadline,after_deadline_unix=new_deadline,added_hours=20,before_max_wall_seconds=old['contract']['max_wall_seconds'],after_max_wall_seconds=s['contract']['max_wall_seconds'],recorded_at=time.time())
 s['explicit_revisions'].append(revision)
 for k in ('history','floors','passed_checks','passed_progress_milestones','active_seconds','evaluated_seconds','work_events','stagnant_rounds'):assert s[k]==old[k]
 write(dest,s)
 # Preserve last evaluated artifact hashes, with explicit pending source versions.
 # This limit revision does not certify a still-unpackaged changed worktree.
 e.update(contract_hash=s['contract_hash'],limit_revision=revision,pending_source_revisions=pending,last_evaluated_input_fingerprint=e['input_fingerprint'])
 e['qualification'].update(current_source_full_regression=False,current_package_matches_worktree=False,full_goal_complete=False)
 e['artifacts'].update({prior:sha(prior),prior_evidence:sha(prior_evidence),'training/b4artists_ml/extend_goal_100_plus20h_v1.py':sha('training/b4artists_ml/extend_goal_100_plus20h_v1.py')})
 ep=gp+'limit100-plus20h-evidence-v1.json';write(ep,e)
 cp.update(state_path=dest,contract_hash=s['contract_hash'],max_goalposts=100,remaining_evaluations=44,deadline_unix=new_deadline,evidence=ep,pending_source_revisions=pending,recorded_at=time.time(),current_turn_classification='Progress: explicit100total evaluation ceiling and20additional hours recorded during runtime integration;56evaluations remain consumed.398native checks now pass; exact package validation follows.',last_evaluated_state=prior)
 cp['artifact']['matches_current_source']=False;cp['artifact']['note']='Previous0.18.0archive remains preserved;0.19.0source has passed398native checks and awaits exact package validation.'
 cp.setdefault('limit_extensions',[]).append(revision);cp['prior_deadline_unix']=old_deadline;cp['latest_extension_hours']=20;cp['deadline_utc']=datetime.datetime.fromtimestamp(new_deadline,datetime.timezone.utc).isoformat();cp['next_safe_actions']=['Finish the already-authorized0.19.0localpackage and offline validation under the same full goal.','Preserve100total evaluations and extended deadline; continue performance and motion-quality work without resetting evidence or weakening requirements.']
 cp['latest_live_observation']={'native_regression':dict(session_id=7570,terminal=True,exit_code=0),'runtime_references':dict(session_id=4714,terminal=True,exit_code=0),'runtime_crouch':dict(session_id=68763,terminal=True,exit_code=0)}
 write(base+'checkpoint-limit100-plus20h-v1.json',cp)
 verification=read(dest);assert verification['contract']['max_goalposts']==100 and verification['contract']['max_wall_seconds']==old['contract']['max_wall_seconds']+72000 and verification['history']==old['history'];assert read(base+'checkpoint-limit100-plus20h-v1.json')['deadline_unix']==1789053845.
 print(dict(goal_id=cp['goal_id'],evaluations_used=56,max_evaluations=100,remaining=44,deadline_utc=cp['deadline_utc'],deadline_eastern='2026-09-10 11:24:05 EDT',history_preserved=True,pending_source_versions=len(pending)))
if __name__=='__main__':main()
