"""Validate the completed velocity study without claiming motion qualification."""
from pathlib import Path
import json,hashlib,time
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'training/b4artists_ml/results/ground-velocity-feasibility-v1'
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def write(p,d):(ROOT/p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
cp=read('docs/b4artists_ml/checkpoint-coupled-ground-v2.json');e=read(cp['evidence'])
assert cp['round']==67 and cp['max_goalposts']==100 and cp['deadline_unix']==1789053845
changed=[p for p,h in e['artifacts'].items() if sha(p)!=h];assert not changed,changed
processes=read('training/b4artists_ml/results/ground-velocity-feasibility-v1/processes.json');assert len(processes)==3 and all(p['complete'] for p in processes)
rows=[]
for process in processes:
    profile=process['profile'];path='training/b4artists_ml/results/ground-velocity-feasibility-v1/'+profile+'/report.json';d=read(path)
    assert d['complete'] and d['source_channels_restored'] and d['actions_and_objects_unchanged'] and not d['qualified'] and len(d['rows'])==4
    assert d['script_sha256']==sha('training/b4artists_ml/probe_ground_velocity_v1.py') and all(sha(p)==h for p,h in d['runtime_sha256'].items())
    assert sha('training/b4artists_ml/results/ground-velocity-feasibility-v1/'+profile+'.log')==process['log_sha256']
    for row in d['rows']:
        assert len(row['epsilon_results'])==3 and row['source_restored']
        assert [x['epsilon'] for x in row['epsilon_results']]==[.001,.0005,.00025]
        for x in row['epsilon_results']:
            assert len(x['solution'])==3+3*len(row['controls']) and len(x['finite_step_checks'])==3
    variants={r['variant']:r for r in d['rows'] if r['frame']==15}
    v={k:r['epsilon_results'][-1] for k,r in variants.items()}
    rows.append(dict(profile=profile,leg_peak_local_rate=v['legs']['max_local_rotation_rate'],body_peak_local_rate=v['whole_body']['max_local_rotation_rate'],body_max_rate_control=v['whole_body']['max_rate_control'],body_linear_residual=v['whole_body']['residual_norm'],body_full_frame_check=v['whole_body']['finite_step_checks'][0],body_small_step_check=v['whole_body']['finite_step_checks'][-1],native_exit_code=process['exit_code']))
summary=dict(complete=True,full_goal_complete=False,qualified=False,rows=rows,point='Allowing upper-body motion improves the local linear solve but does not produce a usable full-frame trajectory.',decision='Use whole-body constrained endpoint velocities as a diagnostic/possible trajectory initialization, never as direct animation increments. A nonlinear trajectory solve must preserve contacts, authored poses and COM while measuring angular velocity and acceleration.',all_prior_artifacts_unchanged=len(e['artifacts']),source_preserved=True,production_unchanged=True,known_host_shutdown_fault=True,recorded_at=time.time())
write('training/b4artists_ml/results/ground-velocity-feasibility-v1/summary.json',summary)
text='\n## Completed comparison\n\nAll three actual-rig runs completed both boundary poses and both control sets across all three finite-difference sizes. Every temporary pose was restored; source channels, actions, drivers, objects and input scene bytes remain unchanged. At epsilon0.00025, takeoff results are:\n\n| Rig | Leg-only peak local control rate (rad/s) | Whole-body peak local control rate (rad/s) | Whole-body largest-rate control |\n|---|---:|---:|---|\n'
for r in rows:text+=f"| {r['profile']} | {r['leg_peak_local_rate']:.2f} | {r['body_peak_local_rate']:.2f} | {r['body_max_rate_control']} |\n"
text+='\nThe whole-body rates are stable across the tested finite-difference sizes. The leg-only BoneForge result is highly sensitive and has a very small singular value; numerical rank15 and a tiny linear residual must not be interpreted as a physically useful solution. These are minimum-norm solutions under the declared coordinate metric, not minimum-maximum-speed or force-optimal solutions. They do not prove global infeasibility.\n\nThe whole-body finite updates still produce material COM/contact errors over1/30second. Errors shrink with shorter steps, demonstrating that the local derivative is useful but its direct increments are insufficient as animation. COM velocity residuals are normalized by trunk length; the reported contact residual combines normalized ankle linear velocity and angular velocity terms and is not a distance or collision measurement. The source stand pose is repeated at takeoff/landing, so symmetric results are not independent motion diversity.\n\nDecision: retain the coupled spatial projection and whole-body derivative model as research building blocks. The next candidate must solve a continuous sequence with endpoint velocities, contacts, priority poses and temporal regularization together; a pose-by-pose bake or direct Jacobian increments are not qualified. Do not silently replace fixed ankle contacts with toe pivots, change authored poses or retime the frozen request to create a pass. Alternative contact geometry may be evaluated only as a separately declared request. No model is promoted and nearby training remains paused.\n\nThe current host again exits3221225477after completed assertions. All4731previously protected artifacts remain unchanged. This is author research evidence, not independent usability or Cascadeur comparison.\n'
with (ROOT/'docs/b4artists_ml/GROUND-VELOCITY-FEASIBILITY-v1.md').open('a',encoding='utf-8') as f:f.write(text)
cp.update(current_turn_classification='Progress: compared actual-rig leg-only/full-body velocity constraints and nonlinear increments; whole-body directions improve conditioning but full-frame increments fail trajectory requirements.',previous_turn_classification='Progress: coupled ground spatial feasibility and dense angular-rate diagnosis completed.',active_jobs=[],blocked_audit=dict(consecutive_goal_turns=0,condition=None),diagnostic_summary='training/b4artists_ml/results/ground-velocity-feasibility-v1/summary.json',recorded_at=time.time(),pending_evaluation=False)
cp['next_safe_actions']=[summary['decision'],'Retain the frozen contact/timing request and failure evidence. A continuous candidate must be validated over full frames and between authored poses, with angular-speed/acceleration checks and meaningful physical/animator limits.','Preserve original goal, checkpoint67,100evaluation ceiling,deadline1789053845,release0.19.2and sealed confirmation. No new nearby model fit.']
cp['diagnostic_artifacts']={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in BASE.rglob('*') if p.is_file()}
for p in ['training/b4artists_ml/probe_ground_velocity_v1.py','training/b4artists_ml/finalize_ground_velocity_v1.py','docs/b4artists_ml/GROUND-VELOCITY-FEASIBILITY-v1.md']:cp['diagnostic_artifacts'][p]=sha(p)
cp['accounting_note']='Research progress checkpoint. Formal goalpost remains67 and parent timer continues from385859.4766528; no work-duration or evaluation reset and no child runtimes added.'
write('docs/b4artists_ml/checkpoint-ground-velocity-v1.json',cp)
print(json.dumps(dict(complete=True,rows=rows,previous_artifacts_unchanged=len(e['artifacts']),goalpost=67,full_goal_complete=False),indent=2))
