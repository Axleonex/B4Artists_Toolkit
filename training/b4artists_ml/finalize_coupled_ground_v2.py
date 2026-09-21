"""Summarize coupled-pose and continuity evidence; preserve all failed gates."""
from pathlib import Path
import json,math,hashlib,time
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def write(p,d):(ROOT/p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def angular_secant(a,b,seconds):
    if len(a)!=4 or len(b)!=4 or not math.isfinite(seconds) or seconds<=0 or not all(math.isfinite(x) for x in list(a)+list(b)):raise ValueError('Finite unit orientation samples and positive seconds required')
    na=math.sqrt(sum(x*x for x in a));nb=math.sqrt(sum(x*x for x in b))
    if min(na,nb)<1e-12:raise ValueError('Degenerate orientation')
    return 2*math.acos(min(1.,abs(sum(x*y for x,y in zip(a,b)))/(na*nb)))/seconds
assert angular_secant([1,0,0,0],[-1,0,0,0],.01)==0
assert abs(angular_secant([1,0,0,0],[math.cos(.05),math.sin(.05),0,0],.1)-1)<1e-10
for a,b,t in [([0]*4,[1,0,0,0],1),([1,0,0,0],[1,0,0,0],0),([float('nan'),0,0,0],[1,0,0,0],1)]:
    try:angular_secant(a,b,t)
    except ValueError:pass
    else:raise AssertionError('Invalid sample accepted')
rows=[]
for profile in ('boneforge','rigify_basic','rigify_default'):
    reports=[read('training/b4artists_ml/results/'+folder+'/'+profile+'/report.json') for folder in ('coupled-ground-feasibility-v1','coupled-ground-continuity-v2')]
    for d,count in zip(reports,(22,134)):
        assert d['complete'] and d['passed_samples']==count and d['all_samples_passed'] and d['source_channels_restored'] and d['actions_and_objects_unchanged'] and not d['qualified']
        assert all(s['passed'] and s['pose_restored'] for s in d['samples'])
        assert all(sha(p)==h for p,h in d['runtime_sha256'].items())
    d=reports[-1];samples={s['frame']:s for s in d['samples']};boundary=[]
    for h in [2**(-n) for n in range(1,9)]:
        a,b=samples[15-h],samples[15];pair={}
        for key in ('input_control_quaternions','control_quaternions'):
            rates={n:angular_secant(a[key][n],b[key][n],h/30) for n in a[key]};name=max(rates,key=rates.get)
            pair[key]=dict(max_radians_per_second=rates[name],control=name)
        boundary.append(dict(interval_frames=h,**pair))
    rows.append(dict(profile=profile,sparse_samples=22,dense_samples=134,max_iterations=max(len(s['trace'])-1 for s in d['samples']),max_errors={key:max(s['final'][key] for s in d['samples']) for key in ('com','contact','orientation','stretch')},takeoff_angular_secants=boundary,temporal_quality_qualified=False))
processes={folder:read('training/b4artists_ml/results/'+folder+'/processes.json') for folder in ('coupled-ground-feasibility-v1','coupled-ground-continuity-v2')}
assert all(len(v)==3 and all(p['complete'] for p in v) for v in processes.values())
summary=dict(complete=True,goal_complete=False,pointwise_samples=468,rows=rows,processes=processes,method_promoted=False,decision='Spatial feasibility demonstrated, temporal quality unqualified. Do not remove production overlap rejection. Investigate boundary feasibility and a joint trajectory solver rather than baking these independent poses.',limitations=['COM/ankle targets and artist-defined mass model only; not contact forces or full-body angular momentum.','Angular secants are evaluated control orientations, not a complete anatomical angular-velocity measurement.','No global infeasibility proof: only this restricted alternating method and frozen authored inputs tested.','No learned model, saved corrected animation, human visual rating or Cascadeur comparison.'],recorded_at=time.time())
write('training/b4artists_ml/results/coupled-ground-continuity-v2/summary.json',summary)
text='\n## Measured outcome\n\nThe66sparse and402dense actual-rig samples all meet the frozen spatial gates. Original channels, actions, objects and input scene bytes are preserved. This is468pointwisechecks, not468independent animations. Maximum dense errors:\n\n| Rig | COM / trunk length | Contact / leg length | Max iterations | Near-takeoff angular secant (rad/s),0.5frame to1/256frame |\n|---|---:|---:|---:|---|\n'
for r in rows:
    q=r['takeoff_angular_secants'];text+=f"| {r['profile']} | {r['max_errors']['com']:.8f} | {r['max_errors']['contact']:.9f} | {r['max_iterations']} | {q[0]['control_quaternions']['max_radians_per_second']:.2f} to {q[-1]['control_quaternions']['max_radians_per_second']:.2f} |\n"
text+='\nBoneForge angular secants grow strongly as the sampling interval shrinks. Rigify settles near39rad/s; its finite value does not establish acceptable animation. The analytic straight-leg limit provides a plausible explanation for BoneForge: for fixed two-link lengths, knee bend near full extension varies with the square root of remaining extension, so nonzero extension speed can produce an unbounded bend rate. This is an inference about the restricted leg/root method, not a proof that every whole-body solution to the user request is impossible.\n\nDecision: retain the production contact/flight overlap rejection. The new alternating projection is useful as a constrained spatial building block, but it must not be baked into a purportedly natural transition. A temporal solver must detect incompatible pose/contact/timing choices, preserve priorities, and test velocity/acceleration/limits across complete motions. Toe roll, contact release and altered authored pose are distinct animator choices; do not silently use them to pass the frozen request. Nearby learned fits remain paused. Full learned-motion and Cascadeur/human qualification remain open.\n\nAll six native processes completed assertions then returned the existing3221225477shutdown fault. No runtime file, model, data split, release, commit or install changed. The dense-script creation initially encountered a shell quoting SyntaxError before any process started; corrected quoting created the intended unchanged algorithm. Source/metric validation is author evidence, not an independent review.\n'
with (ROOT/'docs/b4artists_ml/COUPLED-GROUND-CONTINUITY-v2.md').open('a',encoding='utf-8') as f:f.write(text)
print(json.dumps(summary['rows'],indent=2))
