"""Controlled temporal-input/learner comparisons; no new data or runtime promotion."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
import argparse,json,hashlib,time,platform
from pathlib import Path
import numpy as np
from temporal_data import validate_manifests
from temporal_model import selection
from sequence_data import load_windows
from sequence_model import evaluate_windows,acceptance
from train_temporal_motion import restore
from kernel_motion import prepare,kernel_trials,linear_fit,evaluate_model,save_model,load_model
ROOT=Path(__file__).resolve().parent

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='kernel_motion_v3');args=parser.parse_args()
    if not args.output.replace('_','').isalnum():raise ValueError('Simple unique output name required')
    output=ROOT/'results'/args.output;output.mkdir(exist_ok=False);start=time.perf_counter()
    p=json.loads((ROOT/'kernel_protocol_v3.json').read_text());manifests=[]
    for row in p['manifests']:
        path=ROOT/row['path']
        if digest(path)!=row['sha256']:raise ValueError('Manifest checksum mismatch')
        manifests.append(json.loads(path.read_text()))
    validate_manifests(manifests)
    source_names=('kernel_protocol_v3.json','kernel_motion.py','motion_coverage.py','train_kernel_motion.py','sequence_data.py','sequence_kinematics.py','sequence_model.py','temporal_data.py','temporal_model.py','bvh_data.py','context_data.py','context_network.py','train_temporal_motion.py')
    source={name:digest(ROOT/name) for name in source_names};(output/'protocol.json').write_text(json.dumps(p,indent=2)+'\n')
    train,skeleton=load_windows(ROOT,manifests[0],'train',p);val,vs=load_windows(ROOT,manifests[0],'validation',p)
    if skeleton!=vs:raise ValueError('Validation topology mismatch')
    prior=json.loads((ROOT/'results/sequence_motion_v2/report.json').read_text());prior_ridge=ROOT/'results/sequence_motion_v2/ridge.npz'
    if digest(prior_ridge)!=prior['selection']['ridge_sha256']:raise ValueError('Reference ridge changed')
    ridge=restore(prior_ridge)
    reports={name:evaluate_windows(val,skeleton,name,ridge if name=='ridge' else None) for name in p['baselines']}
    for name,report in reports.items():
        if report!=prior['validation'][name]:raise ValueError('Baseline windows/evaluation differ from frozen V2: '+name)
    z,weight,mean,std,target=prepare(train,'motion_relative')
    zero=dict(kind='zero',variant='motion_relative',mean=mean,std=std)
    best_score=selection(reports['fk_linear']);best_id='zero_fk';reports['mlp']=reports['fk_linear'];save_model(output/'selected.npz',zero)
    history=[];families={}
    print(json.dumps(dict(event='data_ready',train_windows=len(train),validation_windows=len(val),zero_score=best_score)),flush=True)
    def consider(model,identifier,family,parameters):
        nonlocal best_score,best_id
        report=evaluate_model(model,val,skeleton);score=selection(report)
        row=dict(id=identifier,family=family,parameters=parameters,score=score,aggregate=report['aggregate'],seconds=time.perf_counter()-start)
        history.append(row);print(json.dumps(dict(event='trial',id=identifier,score=score,position=report['aggregate']['position'],seconds=row['seconds'])),flush=True)
        if family not in families or score<families[family]['score']:
            families[family]=dict(id=identifier,score=score,report=report,parameters=parameters);save_model(output/(family+'.npz'),model)
        if score<best_score:
            best_score=score;best_id=identifier;reports['mlp']=report;save_model(output/'selected.npz',model)
    for variant in p['feature_variants']:
        z,weight,mean,std,target=prepare(train,variant)
        for reg in p['linear_regularization']:
            model=dict(kind='linear',variant=variant,mean=mean,std=std,coef=linear_fit(z,weight,target,reg))
            consider(model,f'{variant}_linear_{reg}',variant+'_linear',dict(regularization=reg))
        for width in p['kernel_widths']:
            for reg,alpha in kernel_trials(z,weight,target,width,p['kernel_regularization']):
                model=dict(kind='kernel',variant=variant,mean=mean,std=std,centers=z,width=width,alpha=alpha)
                consider(model,f'{variant}_kernel_{width}_{reg}',variant+'_kernel',dict(width=width,regularization=reg))
    frozen=dict(selected=best_id,selected_sha256=digest(output/'selected.npz'),source_sha256=source,selection_split='validation',observed_development_loaded=False,
                skeleton=dict(names=skeleton[0],parents=skeleton[1],semantic=skeleton[2]),v2_report_sha256=digest(ROOT/'results/sequence_motion_v2/report.json'))
    (output/'selection.json').write_text(json.dumps(frozen,indent=2)+'\n');print(json.dumps(dict(event='selected',selected=best_id,score=best_score)),flush=True)
    model=load_model(output/'selected.npz');reloaded=evaluate_model(model,val,skeleton)
    if reloaded!=reports['mlp']:raise ValueError('Selected saved model does not reproduce validation')
    dev,ds=load_windows(ROOT,manifests[1],'confirmation',p)
    if ds!=skeleton:raise ValueError('Development topology mismatch')
    development={name:evaluate_windows(dev,skeleton,name,ridge if name=='ridge' else None) for name in p['baselines']}
    development['mlp']=evaluate_model(model,dev,skeleton)
    result=dict(schema=3,status='research_only',goal_status='active_incomplete',protocol=p,selection=frozen,candidates=history,families=families,validation=reports,observed_development=development,
                gates=dict(validation=acceptance(reports,p),observed_development=acceptance(development,p)),
                runtime=dict(seconds=time.perf_counter()-start,python=platform.python_version(),numpy=np.__version__,platform=platform.platform(),blas_threads=os.environ['OPENBLAS_NUM_THREADS']),
                limitations=['Oracle audit is not deployable inference','Kernel coefficient regression is supervised statistical learning, not a neural network',
                             'No fresh blind confirmation data','No contacts/style/partial-body/multiple-interior-anchor conditioning','No Bforartists rig/mesh workflow integration','No animator/Cascadeur comparison'])
    (output/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(event='complete',selected=best_id,gates=result['gates'],seconds=result['runtime']['seconds'])),flush=True)

if __name__=='__main__':main()
