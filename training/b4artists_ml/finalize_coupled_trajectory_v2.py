"""Validate the two-stage trajectory result and retain separate motion gates."""
from pathlib import Path
import json,hashlib,math,time
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def write(p,d):(ROOT/p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def normalize(q):
    n=math.sqrt(sum(v*v for v in q));assert n>1e-12;return [v/n for v in q]
def product(a,b):
    w,x,y,z=a;v,i,j,k=b
    return [w*v-x*i-y*j-z*k,w*i+x*v+y*k-z*j,w*j-x*k+y*v+z*i,w*k+x*j-y*i+z*v]
def velocity(a,b,dt):
    a=normalize(a);b=normalize(b);q=product(b,[a[0],-a[1],-a[2],-a[3]])
    if q[0]<0:q=[-v for v in q]
    n=math.sqrt(sum(v*v for v in q[1:]));factor=(2*math.atan2(n,q[0])/n if n>1e-12 else 2)/dt
    return [v*factor for v in q[1:]]
def norm(v):return math.sqrt(sum(x*x for x in v))
assert norm(velocity([1,0,0,0],[-1,0,0,0],.1))==0
assert abs(norm(velocity([1,0,0,0],[math.cos(.05),math.sin(.05),0,0],.1))-1)<1e-10
cp=read('docs/b4artists_ml/checkpoint-ground-velocity-v1.json');prior=read(cp['evidence']);protected=dict(prior['artifacts']);protected.update(cp['diagnostic_artifacts'])
assert all(sha(p)==h for p,h in protected.items())
reports=[];processes=[]
for folder,script in [('coupled-trajectory-v1','solve_coupled_trajectory_v1.py'),('coupled-trajectory-reconstruction-v2','reconstruct_coupled_trajectory_v2.py')]:
    base='training/b4artists_ml/results/'+folder+'/';d=read(base+'report.json');p=read(base+'process.json')
    assert d['complete'] and d['source_preserved'] and d['priorities_unchanged'] and not d['qualified'] and p['complete']
    assert d['script_sha256']==sha('training/b4artists_ml/'+script) and all(sha(n)==h for n,h in d['runtime_sha256'].items()) and sha(base+'host.log')==p['log_sha256']
    reports.append(d);processes.append(p)
first,second=reports;assert len(first['iterations'])==16 and second['sampled_constraints_passed']
assert second['input_trajectory_sha256']==sha('training/b4artists_ml/results/coupled-trajectory-v1/latest-trajectory.npz')
assert all(second['dense_max'][k]<=v for k,v in [('com',2e-4),('contact',2e-4),('orientation',.001)])
assert read('training/b4artists_ml/results/coupled-trajectory-v1/algebra-check.json')['max_error']<1e-10
quarter=[]
for d in reports:
    samples={r['frame']:r for r in d['dense']};times=[i/4 for i in range(4,197)];names=set(samples[1]['control_quaternions']);peak_v=(0.,None,None);peak_a=(0.,None,None)
    for name in names:
        velocities=[velocity(samples[a]['control_quaternions'][name],samples[b]['control_quaternions'][name],(b-a)/30) for a,b in zip(times,times[1:])]
        for t,v in zip(times[1:],velocities):
            if norm(v)>peak_v[0]:peak_v=(norm(v),name,t)
        for t,a,b in zip(times[2:],velocities,velocities[1:]):
            value=norm([(v-u)*120 for u,v in zip(a,b)])
            if value>peak_a[0]:peak_a=(value,name,t)
    quarter.append(dict(peak_evaluated_control_rate_rad_s=peak_v,peak_sampled_angular_acceleration_rad_s2=peak_a,spacing_frames=.25))
near=[];samples={r['frame']:r for r in second['dense']}
leg_names=set(read('training/b4artists_ml/results/coupled-ground-continuity-v2/boneforge/report.json')['samples'][0]['control_quaternions'])
for h in [.5,.25,.125,.0625,.03125,.015625,.0078125]:
    a=samples[15-h]['control_quaternions'];b=samples[15]['control_quaternions'];rates={n:norm(velocity(a[n],b[n],h/30)) for n in a};name=max(rates,key=rates.get)
    near.append(dict(interval_frames=h,max_leg_rate=max(rates[n] for n in leg_names),max_all_rate=rates[name],control=name))
summary=dict(complete=True,full_goal_complete=False,method_promoted=False,profile='boneforge',optimizer_iterations=16,reconstruction_knots=second['passes'][-1]['knots'],validation_samples=len(second['dense']),sampled_spatial_constraints_passed=True,initial_dense_errors=first['dense_max'],reconstructed_dense_errors=second['dense_max'],quarter_frame_motion_estimates=quarter,near_takeoff=near,source_preserved=True,processes=processes,previous_artifacts_unchanged=len(protected),decision='Retain joint optimization plus adaptive reconstruction as research. Spatial checks pass, but upper-body angular speed/acceleration remain excessive for claiming successful animation. Enforce temporal constraints during optimization and evaluate complete actor-based reference motion before production integration.',scope='One controlled jump on BoneForge; no broad rig, motion, human, physical force or Cascadeur qualification.',recorded_at=time.time())
write('training/b4artists_ml/results/coupled-trajectory-reconstruction-v2/summary.json',summary)
text='\n## Completed two-stage result\n\nThe16-iteration coupled solve passes whole-frame position constraints but initially fails dense checks: COM0.02244trunk lengths, ankle0.01157leg lengths. Adaptive reconstruction adds28samples to its193initial knots. The resulting221-knot trajectory passes881dense sampled checks with unchanged priorities and source data: COM0.00019436trunk lengths, ankle0.00010126leg lengths and orientation0.00000293rad. The original optimizer and failure remain frozen. No corrected result is installed or released.\n\nThis is spatial progress, not successful animation qualification. Near takeoff, reconstructed leg rates remain bounded around12rad/s, while an upper-body control approaches98rad/s. The quarter-frame angular speed/acceleration estimates and control names are recorded in summary.json. They use normalized quaternion differences in evaluated pose orientations; finite sampling does not certify continuous bounds or force/torque plausibility. Numerical control rates are separate from anatomical joint-limit measurements.\n\nDecision: the temporal guide plus adaptive constraint projection can preserve geometry, but the projection can redistribute fast motion into other controls. A production trajectory solver needs joint temporal limits and regularization integrated with the contacts/COM solve. Do not declare the request globally impossible from these candidates, weaken the spatial gates, release a fast shoulder correction as natural motion, or discard the frozen stress case. Full learned-motion, broader rig/motion tests, independent animator assessment and Cascadeur comparison remain outstanding.\n\nThe two runs took approximately155.6and52.5seconds including host startup/shutdown; these are single research runs, not responsive-UI qualification. Both completed assertions followed by the known3221225477shutdown failure. Block update algebra agrees with an independent direct KKT solve to3.6e-15on a small linear system; this is a numerical unit check, not independent code or visual review. The canonical adaptive-review entry point again failed before launch with the uv trampoline error.\n'
with (ROOT/'docs/b4artists_ml/COUPLED-TRAJECTORY-RECONSTRUCTION-v2.md').open('a',encoding='utf-8') as f:f.write(text)
print(json.dumps({k:summary[k] for k in ['reconstruction_knots','validation_samples','reconstructed_dense_errors','quarter_frame_motion_estimates','previous_artifacts_unchanged','method_promoted']},indent=2))
