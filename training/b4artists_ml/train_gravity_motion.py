"""Controlled gravity-direction learning; no measured acceleration/contact labels assumed."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
import argparse,json,hashlib,time,platform
from pathlib import Path
import numpy as np
from temporal_data import validate_manifests
from temporal_model import selection
from sequence_model import evaluate_windows,acceptance
from train_temporal_motion import restore
from kernel_motion import load_model,save_model
from environment_data import load_environment_windows
from gravity_model import fit,evaluate_model
ROOT=Path(__file__).resolve().parent

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='gravity_motion_v4');args=parser.parse_args()
    if not args.output.replace('_','').isalnum():raise ValueError('Simple unique output name required')
    out=ROOT/'results'/args.output;out.mkdir(exist_ok=False);start=time.perf_counter();p=json.loads((ROOT/'gravity_protocol_v4.json').read_text());manifests=[]
    for row in p['manifests']:
        path=ROOT/row['path']
        if digest(path)!=row['sha256']:raise ValueError('Manifest checksum mismatch')
        manifests.append(json.loads(path.read_text()))
    validate_manifests(manifests)
    names=('environment_context.py','environment_data.py','gravity_model.py','gravity_protocol_v4.json','train_gravity_motion.py','kernel_motion.py','motion_coverage.py','sequence_data.py','sequence_model.py','sequence_kinematics.py','temporal_data.py','temporal_model.py','bvh_data.py','context_data.py','context_network.py','train_temporal_motion.py')
    source={name:digest(ROOT/name) for name in names};(out/'protocol.json').write_text(json.dumps(p,indent=2)+'\n')
    train,skeleton=load_environment_windows(ROOT,manifests[0],'train',p);val,vs=load_environment_windows(ROOT,manifests[0],'validation',p)
    if vs!=skeleton:raise ValueError('Topology mismatch')
    control_path=ROOT/'results/kernel_motion_v3/selected.npz';prior_path=ROOT/'results/kernel_motion_v3/report.json'
    if digest(control_path)!=p['control_sha256'] or digest(prior_path)!=p['control_report_sha256']:raise ValueError('Frozen control changed')
    control=load_model(control_path);prior=json.loads(prior_path.read_text());ridge=restore(ROOT/'results/sequence_motion_v2/ridge.npz')
    reports={name:evaluate_windows(val,skeleton,name,ridge if name=='ridge' else None) for name in p['baselines'] if name!='v3_control'}
    for name,report in reports.items():
        if report!=prior['validation'][name]:raise ValueError('Reference windows changed: '+name)
    reports['v3_control']=evaluate_model(control,val,skeleton)
    if reports['v3_control']!=prior['validation']['mlp']:raise ValueError('V3 control is not reproduced')
    reports['mlp']=reports['v3_control'];best=selection(reports['mlp']);selected='v3_control';history=[];best_gravity=float('inf')
    (out/'selected.npz').write_bytes(control_path.read_bytes())
    print(json.dumps(dict(event='data_ready',train_windows=len(train),validation_windows=len(val),control_score=best,seconds=time.perf_counter()-start)),flush=True)
    for importance in p['gravity_weights']:
        model=fit(train,importance,p['base_width'],p['regularization']);report=evaluate_model(model,val,skeleton);score=selection(report)
        row=dict(importance=importance,score=score,report=report,seconds=time.perf_counter()-start);history.append(row)
        print(json.dumps(dict(event='trial',importance=importance,score=score,position=report['aggregate']['position'],seconds=row['seconds'])),flush=True)
        if score<best_gravity:best_gravity=score;save_model(out/'best_gravity.npz',model)
        if score<best:best=score;selected='gravity_'+str(importance);reports['mlp']=report;save_model(out/'selected.npz',model)
    frozen=dict(selected=selected,selected_sha256=digest(out/'selected.npz'),best_gravity_sha256=digest(out/'best_gravity.npz'),source_sha256=source,selection_split='validation',observed_development_loaded=False,
                skeleton=dict(names=skeleton[0],parents=skeleton[1],semantic=skeleton[2]))
    (out/'selection.json').write_text(json.dumps(frozen,indent=2)+'\n');print(json.dumps(dict(event='selected',selected=selected)),flush=True)
    model=load_model(out/'selected.npz');reloaded=evaluate_model(model,val,skeleton)
    if reloaded!=reports['mlp']:raise ValueError('Selected model reload differs')
    dev,ds=load_environment_windows(ROOT,manifests[1],'confirmation',p)
    if ds!=skeleton:raise ValueError('Development topology mismatch')
    development={name:evaluate_windows(dev,skeleton,name,ridge if name=='ridge' else None) for name in p['baselines'] if name!='v3_control'}
    development['v3_control']=evaluate_model(control,dev,skeleton);development['mlp']=evaluate_model(model,dev,skeleton)
    result=dict(schema=4,status='research_only',goal_status='active_incomplete',protocol=p,selection=frozen,candidates=history,validation=reports,observed_development=development,
                gates=dict(validation=acceptance(reports,p),observed_development=acceptance(development,p)),
                runtime=dict(seconds=time.perf_counter()-start,python=platform.python_version(),numpy=np.__version__,platform=platform.platform(),blas_threads=os.environ['OPENBLAS_NUM_THREADS']),
                limitations=['Source Y-up is an explicit convention assumption, not measured gravity','No learned acceleration magnitude or support-plane/contact behavior','No new blind confirmation data',
                             'Free-flight math is not automatic COM/pelvis or rig correction','No actual learned control-rig/mesh workflow','No animator or Cascadeur comparison'])
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(event='complete',selected=selected,gates=result['gates'],seconds=result['runtime']['seconds'])),flush=True)

if __name__=='__main__':main()
