"""Build inspectable motion examples from exposed development data only."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import json,hashlib,re,time
import numpy as np
from semantic_projection import load_windows,project_windows
from semantic_motion_data import from_bvh
from bvh_data import parse_bvh
from context_data import PARENTS,ROLES
import shape_trajectory as previous
import kinematic_trajectory_v20 as current
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def main():
    started=time.perf_counter();dest=REPO/'docs/b4artists_ml/motion-review-v1';dest.mkdir(exist_ok=False)
    plan=read(ROOT/'motion_review_plan_v1.json');protocol=read(ROOT/'kinematic_trajectory_protocol_v20.json');manifest=read(ROOT/'temporal_training_manifest_v19.json');old=read(ROOT/'results/expanded_trajectory_v19/report.json');new=read(ROOT/'results/kinematic_trajectory_v20/report.json')
    acquisition=read(ROOT/'temporal_expansion_plan_v19.json');assert all(not (ROOT/'cache'/(c+'.bvh')).exists() for c in acquisition['planned_splits']['confirmation'])
    oldpath=ROOT/'results/expanded_trajectory_v19/best_learned.npz';newpath=ROOT/'results/kinematic_trajectory_v20/best_learned.npz';assert sha(oldpath)==old['selection']['best_learned_sha256'] and sha(newpath)==new['selection']['best_learned_sha256']
    windows,skeleton=load_windows(ROOT,manifest,'validation',protocol);cohorts={}
    for w in windows:cohorts.setdefault(f"{w['clip']}/gap{w['gap']}/context{int(w['context'])}",w)
    assert len(cohorts)==96;rows=list(cohorts.values());keys=list(cohorts);predictions={};edge_errors={}
    for name,provider,model in [('linear',previous,dict(kind='baseline',baseline='linear')),('hermite',previous,dict(kind='baseline',baseline='hermite')),('shape',previous,dict(kind='baseline',baseline='shape')),('previous',previous,previous.load(oldpath)),('current',current,current.load(newpath))]:
        raw=[provider.predict_packed(model,w['observations'],w['t']) for w in rows];projected,metrics=project_windows(rows,raw,skeleton,protocol['projection']);predictions[name]=projected;edge_errors[name]=metrics['true_edge_length_max'];assert edge_errors[name]<1e-6
        print(json.dumps(dict(event='projected',method=name,windows=len(rows),seconds=time.perf_counter()-started)),flush=True)
    descriptions={}
    for line in (ROOT/'cache/cmu-index-v8.txt').read_text(encoding='utf-8').splitlines():
        m=re.match(r'^(\d+_\d+)\s+(.*)',line)
        if m:descriptions[m[1]]=m[2]
    references={}
    for clip in {w['clip'] for w in rows}:
        source=from_bvh(parse_bvh((ROOT/'cache'/(clip+'.bvh')).read_text()),30);rest=source.rest
        left=rest[11]-rest[14];left/=np.linalg.norm(left);up=(rest[5]+rest[8]-rest[11]-rest[14])*.5;up-=left*np.dot(up,left);up/=np.linalg.norm(up)
        references[clip]=np.stack((left,np.cross(up,left),up),axis=1)
    cases=[];priority_max=0.
    for index,(key,w) in enumerate(zip(keys,rows)):
        best=min(protocol['baselines'],key=lambda name:new['baselines'][name]['cohorts'][key]['position']);control=best.removeprefix('projected_');o=w['observations'];basis=references[w['clip']]
        methods={};errors={};values={'reference':w['target'],'control':predictions[control][index],'previous':predictions['previous'][index],'current':predictions['current'][index]}
        for name,value in values.items():
            points=np.asarray(value).reshape(-1,17,9)[...,:3];original=w['target'].reshape(-1,17,9)[...,:3]
            priority_max=max(priority_max,float(np.max(abs(points[[0,-1]]-original[[0,-1]]))))
            display=(o.world_points(points)-o.origin)@basis/o.scale
            methods[name]=np.round(display,7).tolist();errors[name]=float(np.mean(np.linalg.norm(points-original,axis=-1)))
        allpoints=np.concatenate([np.asarray(x).reshape(-1,3) for x in methods.values()]);lo=allpoints.min(axis=0);hi=allpoints.max(axis=0);center=(lo+hi)*.5
        cohort={name:float(new['baselines'][best]['cohorts'][key]['position']) if name=='control' else float(report['best_learned_report']['cohorts'][key]['position']) for name,report in [('control',new),('previous',old),('current',new)]}
        cases.append(dict(id=key,clip=w['clip'],description=descriptions.get(w['clip'],w['clip']),gap=w['gap'],context=bool(w['context']),frames=w['frame'].tolist(),dt=float(w['dt']),methods=methods,control=control,sample_position_errors=errors,cohort_position_errors=cohort,center=center.tolist(),radius=float(np.max(np.linalg.norm(allpoints-center,axis=1))),grid_z=float(np.min(np.asarray(methods['reference'])[:,[13,16],2]))))
    assert priority_max<1e-6
    payload=dict(schema=1,title='B4Artists Machine Learning: motion review',parents=list(PARENTS),roles=list(ROLES),models={'previous':sha(oldpath),'current':sha(newpath)},cases=cases,plan_sha256=sha(ROOT/'motion_review_plan_v1.json'),source_manifest_sha256=sha(ROOT/'temporal_training_manifest_v19.json'),confirmation_read=False,selection=plan['selection'],scope=plan['display'])
    encoded=json.dumps(payload,separators=(',',':'),allow_nan=False);assert len(encoded.encode())<=plan['max_embedded_bytes'];data_hash=hashlib.sha256(encoded.encode()).hexdigest();(dest/'motion-data.json').write_text(encoded,encoding='utf-8')
    template=(ROOT/'motion_review_template_v1.html').read_text(encoding='utf-8');assert template.count('__MOTION_DATA__')==1 and template.count('__DATA_HASH__')==1
    html=template.replace('__MOTION_DATA__',encoded.replace('<','\\u003c')).replace('__DATA_HASH__',data_hash);(dest/'index.html').write_text(html,encoding='utf-8')
    result=dict(passed=True,cases=96,methods=4,displayed_frames=sum(len(x['frames']) for x in cases),max_priority_error=priority_max,true_edge_errors=edge_errors,embedded_data_bytes=len(encoded.encode()),data_sha256=data_hash,html_sha256=sha(dest/'index.html'),model_sha256=payload['models'],confirmation_read=False,human_assessment='not yet supplied',source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in [Path(__file__),ROOT/'motion_review_template_v1.html',ROOT/'motion_review_plan_v1.json',ROOT/'temporal_training_manifest_v19.json',ROOT/'kinematic_trajectory_protocol_v20.json']},artifact=(dest/'index.html').relative_to(REPO).as_posix(),runtime_seconds=time.perf_counter()-started)
    write(ROOT/'results/motion-review-build-v1.json',result);print(json.dumps(result),flush=True)
if __name__=='__main__':main()
