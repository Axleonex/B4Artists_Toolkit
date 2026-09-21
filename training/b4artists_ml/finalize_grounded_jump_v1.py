"""Verify and summarize frozen grounded-jump measurements; no runtime edit."""
from pathlib import Path
import json,hashlib,zipfile,time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'training/b4artists_ml/results/grounded-jump-diagnostic-v1'
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def write(p,d):(ROOT/p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
cp=read('docs/b4artists_ml/checkpoint-visible-state-package-v1.json')
assert cp['round']==66 and cp['max_goalposts']==100 and cp['deadline_unix']==1789053845
old=read(cp['evidence']);changed=[p for p,h in old['artifacts'].items() if sha(p)!=h]
assert not changed,changed
processes=read('training/b4artists_ml/results/grounded-jump-diagnostic-v1/processes.json')
assert len(processes)==3 and all(p['complete'] for p in processes)
rows=[];fig,axes=plt.subplots(3,1,figsize=(10,8),sharex=True,layout='constrained')
for ax,process in zip(axes,processes):
    profile=process['profile'];folder='training/b4artists_ml/results/grounded-jump-diagnostic-v1/'+profile+'/'
    d=read(folder+'report.json');assert d['complete'] and d['source_recovered'] and not d['grounded_workflow_passed'] and d['human_assessment'] is None and d['cascadeur_comparison'] is None
    assert sha(d['blend'])==d['blend_sha256']
    assert sha('training/b4artists_ml/diagnose_grounded_jump_v1.py')==d['script_sha256']
    assert all(sha(p)==h for p,h in d['runtime_sha256'].items())
    t=np.array(d['ground_frames']);scale=d['leg_length_world'];target=np.array(d['before']['points'])[0]
    stats={}
    for phase,color,label in [('before','#2471a3','Authored interpolation'),('after','#c0392b','Ungrounded COM correction')]:
        points=np.array(d[phase]['points']);delta=points-target
        drift=float(np.max(np.linalg.norm(delta,axis=-1))/scale)
        # Host reports used float32 for contact arrays; recomputation is float64.
        assert abs(drift-d[phase]['max_normalized_contact_drift'])<1e-6
        stats[phase]=drift
        z=100*delta[:,:,2].mean(axis=1)/scale
        for mask in (t<=15,t>=33):ax.plot(t[mask],z[mask],color=color,label=label if mask[0] else None)
    ax.axhline(0,color='#555555',linewidth=.8);ax.axvspan(15,33,color='#dddddd',alpha=.6)
    ax.set_title(profile.replace('_',' ').title(),loc='left');ax.set_ylabel('Mean ankle height\n(% leg length)');ax.grid(alpha=.2)
    rows.append(dict(profile=profile,contact_drift_before=stats['before'],contact_drift_after=stats['after'],source_recovered=True,grounded_request_rejected=True,native_exit_code=process['exit_code'],blend=d['blend']))
axes[0].legend(loc='lower center',ncol=2);axes[-1].set_xlabel('Frame (30 fps); shaded interval is airborne and omitted from contact measurements')
fig.suptitle('Grounded jump gap: root-only velocity joins move planted feet\nControlled procedural diagnostic; ankle plane is not a sole/collision test',fontsize=13)
plot='training/b4artists_ml/results/grounded-jump-diagnostic-v1/contact-displacement.png';fig.savefig(ROOT/plot,dpi=150);plt.close(fig)
archive='releases/b4artists_ml_v0.19.2.zip';assert sha(archive)==cp['artifact']['sha256']
with zipfile.ZipFile(ROOT/archive) as z:
    assert all(z.read(n)==(ROOT/n).read_bytes() for n in z.namelist() if not n.endswith('/'))
summary=dict(complete=True,goal_complete=False,goal_id=cp['goal_id'],rows=rows,protected_artifacts_verified=len(old['artifacts']),all_protected_unchanged=True,package_unchanged=True,plot=plot,plot_sha256=sha(plot),native_clean_shutdown=False,review=dict(independent=False,adaptive_review_unavailable='uv trampoline failed to spawn Python child process: entity not found(os error2)',author_checks=['AST parse','Three actual-rig workflows','Recomputed contact metrics','Runtime/archive and prior artifact hashes','Source and rig modes restored']),next_action='Investigate coupled contact and center-of-mass correction on frozen ground-transition samples, including feasibility near straight-leg takeoff. Do not remove the production overlap rejection or accept unconstrained root motion as grounded quality.',recorded_at=time.time())
write('training/b4artists_ml/results/grounded-jump-diagnostic-v1/summary.json',summary)
text='\n## Completed diagnostic\n\nAll three actual-rig runs completed the controlled49-frame request and source recovery. The requested grounded transition is rejected on every rig. Removing contacts permits the separate ungrounded native COM result, but increases foot drift:\n\n| Rig | Before (% leg length) | After (% leg length) | Grounded request |\n|---|---:|---:|---|\n'
for r in rows:text+=f"| {r['profile']} | {100*r['contact_drift_before']:.2f} | {100*r['contact_drift_after']:.2f} | Rejected |\n"
text+='\nThe controlled takeoff/landing poses have extended legs; this is a difficult feasibility case, not an animator-authored exemplar of a natural jump. Contacts here pin ankle frames, not toe roll or sole patches. The next coupled solver must distinguish infeasible pose/timing requests from solver failure. A successful numerical result on these fixtures would still need realistic authored motion and independent visual assessment.\n\nEditable ungrounded scenes and quarter-frame measurements are in training/b4artists_ml/results/grounded-jump-diagnostic-v1. The figure contact-displacement.png shows average left/right vertical ankle displacement; table drift uses the maximum individual 3D displacement. Neither certifies collision penetration. All host assertions completed, followed by the known3221225477shutdown failure. The adaptive review entry point failed before launch with the same uv trampoline error; author checks are not independent review. All4688previously protected artifacts and exact0.19.2archive bytes remain unchanged. No production code, models, data splits or release changed.\n\nDecision: investigate a contact-constrained COM transition solver with actual-rig feedback, while preserving the current rejection until the joint constraints pass. Sequential whole-character translation is insufficient for this planted-foot request. Keep nearby learned fits paused; learned-quality and complete animator/Cascadeur gates remain open.\n'
with (ROOT/'docs/b4artists_ml/GROUNDED-JUMP-DIAGNOSTIC-v1.md').open('a',encoding='utf-8') as f:f.write(text)
cp.update(current_turn_classification='Progress: measured grounded jump incompatibility and ungrounded foot drift on three actual rigs; verified source recovery and preserved all prior evidence.',previous_turn_classification='No progress: architecture assessment mostly restated existing failures.',active_jobs=[],blocked_audit=dict(consecutive_goal_turns=0,condition=None),pending_evaluation=False,diagnostic_summary='training/b4artists_ml/results/grounded-jump-diagnostic-v1/summary.json',next_safe_actions=[summary['next_action'],'Preserve full original goal, checkpoint66,100evaluation cap,deadline1789053845 and sealed confirmation. No nearby model fits.'],recorded_at=time.time())
cp['diagnostic_artifacts']={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT)) for p in BASE.rglob('*') if p.is_file()}
cp['diagnostic_artifacts'].update({p:sha(p) for p in ['training/b4artists_ml/diagnose_grounded_jump_v1.py','training/b4artists_ml/finalize_grounded_jump_v1.py','docs/b4artists_ml/GROUNDED-JUMP-DIAGNOSTIC-v1.md']})
cp['accounting_note']='Diagnostic progress checkpoint; formal goalpost remains66. Parent timer continues from prior checkpoint; no child runtime added and no evaluation or limit reset.'
write('docs/b4artists_ml/checkpoint-grounded-jump-diagnostic-v1.json',cp)
print(json.dumps(dict(complete=True,rows=rows,prior_artifacts_unchanged=len(old['artifacts']),goalpost=66,full_goal_complete=False),indent=2))
