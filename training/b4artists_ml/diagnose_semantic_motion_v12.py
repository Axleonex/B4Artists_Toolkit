"""Post-selection diagnostics; no fitting, tuning, or confirmation access."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import hashlib,json,time
import numpy as np
import semantic_predictor as predictor
from semantic_projection import load_windows
from motion_coverage import evaluate_predictions,squared_distance
from sequence_data import coefficients_basis
ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def main():
    start=time.perf_counter();a=ROOT/'results/semantic_motion_v12';b=ROOT/'results/semantic_motion_v12_repeat'
    ra=json.loads((a/'report.json').read_text());rb=json.loads((b/'report.json').read_text())
    aa={k:v for k,v in ra.items() if k!='runtime'};bb={k:v for k,v in rb.items() if k!='runtime'}
    assert aa==bb,'Independent reports differ beyond runtime metadata'
    names=['protocol.json','manifest.json','trials.json','selection.json','selected.npz','best_learned.npz']+['trial_'+str(i)+'.npz' for i in range(8)]
    files={name:dict(first=sha(a/name),repeat=sha(b/name)) for name in names}
    assert all(v['first']==v['repeat'] for v in files.values())
    assert all(sha(ROOT/name)==h for name,h in ra['source_sha256'].items())
    reproduction=dict(passed=True,scope='Independent complete fit and identical projection/evaluation; runtime timings excluded from report equality.',files=files,report_metrics_exact=True,source_unchanged=True,confirmation_read=False)
    write(ROOT/'results/semantic-model-reproduction-v12.json',reproduction)
    protocol=ra['protocol'];manifest=json.loads((a/'manifest.json').read_text());model=predictor.load(a/'best_learned.npz')
    result=dict(scope='Post-selection explanatory analysis only. Models, selected weights, gates and frozen validation scores are unchanged.',model_sha256=sha(a/'best_learned.npz'),splits={},confirmation_read=False)
    for split in ['train','validation']:
        windows,skeleton=load_windows(ROOT,manifest,split,protocol)
        report={}
        for name,which in [('linear',dict(kind='baseline',baseline='linear')),('hermite',dict(kind='baseline',baseline='hermite')),('learned',model)]:
            pred=[predictor.predict_packed(which,w['observations'],w['t']) for w in windows]
            report[name]=evaluate_predictions(windows,pred)
        z=np.stack([(predictor.features(w['x'],model['variant'])-model['mean'])/model['std'] for w in windows])
        learned=predictor.design(model,z)@model['coef'];targets=[];oracle=[]
        for w in windows:
            basis=coefficients_basis(w['t'],w['observations'].duration)
            c=np.linalg.solve(basis.T@basis+np.eye(4)*1e-6,basis.T@(w['target']-w['linear']))
            targets.append(c.ravel());oracle.append(w['linear']+basis@c)
        targets=np.asarray(targets)
        report['label_fit_oracle']=evaluate_predictions(windows,oracle)
        report['oracle_warning']='Uses hidden labels: capacity diagnostic only, never a predictor, initializer, score for selection, or runtime fallback.'
        report['coefficient_mse_unweighted']=dict(learned=float(np.mean((learned-targets)**2)),zero=float(np.mean(targets**2)))
        distance=np.sqrt(np.maximum(0,squared_distance(z,model['centers'])))
        report['nearest_center_distance_quantiles']=np.quantile(distance.min(axis=1),[0,.25,.5,.75,.95,1]).tolist()
        report['max_rbf_activation_quantiles']=np.quantile(np.exp(-distance.min(axis=1)**2/(2*model['width']**2)),[0,.25,.5,.75,.95,1]).tolist()
        result['splits'][split]=report
        print(json.dumps(dict(split=split,raw={k:v['aggregate'] for k,v in report.items() if isinstance(v,dict) and 'aggregate' in v},coefficient_mse=report['coefficient_mse_unweighted'],nearest_center=report['nearest_center_distance_quantiles'])),flush=True)
    result['projected_validation']=dict(linear=ra['baselines']['projected_linear'],hermite=ra['baselines']['projected_hermite'],learned=ra['best_learned_report'])
    result['source_sha256']=sha(Path(__file__));result['seconds']=time.perf_counter()-start
    write(ROOT/'results/semantic-model-diagnostic-v12.json',result)
if __name__=='__main__':main()
