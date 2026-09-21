"""Reproduce shipped pose weights in an isolated directory from hash-verified local inputs."""
from pathlib import Path
import sys,os,json,hashlib,shutil,time,platform,traceback
ROOT=Path(__file__).resolve().parent;TAG=os.environ.get('B4ML_REPRO_TAG','shipped-model-reproduction-v1');STAGE=ROOT/'cache'/TAG;OUT=ROOT/'results'/(TAG+'.json')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    import numpy as np
    assert not STAGE.exists() and not OUT.exists()
    manifests=['data_manifest.json','confirmation_manifest.json','expansion_manifest.json','context_confirmation_manifest.json','results/training_manifest_v4.json']
    clips={};inputs={}
    for name in manifests:
        path=ROOT/name;inputs[name]=sha(path)
        for row in json.loads(path.read_text())['files']:
            if row['clip'] in clips:assert clips[row['clip']]['sha256']==row['sha256']
            clips[row['clip']]=row
    for clip,row in clips.items():assert sha(ROOT/'cache'/(clip+'.bvh'))==row['sha256'],clip
    STAGE.mkdir();(STAGE/'cache').mkdir();(STAGE/'results').mkdir()
    for name in manifests:shutil.copy2(ROOT/name,STAGE/name)
    for clip in clips:shutil.copy2(ROOT/'cache'/(clip+'.bvh'),STAGE/'cache'/(clip+'.bvh'))
    for name in ['context_projection.py','results/limb_prior_rff_v1.npz']:
        inputs[name]=sha(ROOT/name);shutil.copy2(ROOT/name,STAGE/name)
    for name in ['train_limb_prior.py','train_limb_prior_v2.py','train_context_pose.py','context_data.py','context_network.py','bvh_data.py','confirm_limb_prior_v2.py','confirm_context_pose.py','evaluate_context_projection.py']:
        inputs[name]=sha(ROOT/name)
    denied=[]
    def audit(event,args):
        if event in ('socket.connect','socket.getaddrinfo','socket.sendto','subprocess.Popen','os.system'):
            denied.append(event);raise RuntimeError('Reproduction is offline: '+event)
    sys.addaudithook(audit)
    sys.path.insert(0,str(ROOT))
    import train_limb_prior as base
    base.ROOT=STAGE
    import train_limb_prior_v2 as limb,train_context_pose as body
    report=dict(schema=1,started_at=time.time(),python=platform.python_version(),numpy=np.__version__,threads=os.environ.get('OPENBLAS_NUM_THREADS'),inputs=inputs,clips={k:v['sha256'] for k,v in clips.items()},raw_bytes=sum((ROOT/'cache'/(k+'.bvh')).stat().st_size for k in clips),stages=[],passed=False,blind_confirmation=False,scope='Reproduction of the two currently shipped single-frame pose models and existing observed confirmation. No new temporal model, data download, holdout or quality claim.')
    try:
        for label,mod in [('limb',limb),('body',body)]:
            t=time.perf_counter();mod.main();report['stages'].append(dict(stage=label,seconds=time.perf_counter()-t))
        pairs=[('limb_prior_rff_v2.npz','limb_prior_v1.npz'),('context_pose_mlp_v1.npz','context_pose_mlp_v1.npz')]
        report['weights']={}
        for built,shipped in pairs:
            actual=sha(STAGE/'results'/built);expected=sha(ROOT.parents[1]/'b4artists_ml/models'/shipped)
            report['weights'][shipped]=dict(reproduced_sha256=actual,shipped_sha256=expected,byte_identical=actual==expected)
        if not all(x['byte_identical'] for x in report['weights'].values()):raise ValueError('Training did not reproduce the shipped weights byte for byte')
        import confirm_limb_prior_v2 as lc,confirm_context_pose as bc
        for label,mod in [('limb_confirmation',lc),('body_confirmation',bc)]:
            t=time.perf_counter();mod.main();report['stages'].append(dict(stage=label,seconds=time.perf_counter()-t))
        l=json.loads((STAGE/'results/limb_prior_confirmation_v2.json').read_text());b=json.loads((STAGE/'results/context_pose_confirmation_v1.json').read_text())
        report['confirmation_gates']=dict(limb={k:v['quality_gate_passed'] for k,v in l['limbs'].items()},body={k:v['passed'] for k,v in b['modes'].items()})
        report['passed']=all(report['confirmation_gates']['limb'].values()) and all(report['confirmation_gates']['body'].values()) and not denied
    except BaseException as exc:report['error']=str(exc);report['traceback']=traceback.format_exc()
    report['denied_calls']=denied;report['outputs']={p.relative_to(STAGE).as_posix():sha(p) for p in (STAGE/'results').glob('*')};OUT.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':main()
