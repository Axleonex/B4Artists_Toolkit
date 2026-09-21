"""Training-only explanatory diagnostics after v13 selection; no retuning."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import json,hashlib,time
import numpy as np
import trajectory_predictor as predictor
from semantic_projection import load_windows
from sequence_model import statistics
from motion_coverage import evaluate_predictions
ROOT=Path(__file__).resolve().parent

def main():
    start=time.perf_counter();out=ROOT/'results/trajectory_motion_v13';frozen=json.loads((out/'selection_frozen.json').read_text());protocol=json.loads((out/'protocol.json').read_text());manifest=json.loads((out/'manifest.json').read_text())
    path=out/'best_learned.npz';assert hashlib.sha256(path.read_bytes()).hexdigest()==frozen['sha256'];m=predictor.load(path)
    train,_=load_windows(ROOT,manifest,'train',protocol);_,weights,_,_=statistics(train)
    z=np.stack([(predictor.features(w['x'],'motion')-m['mean'])/m['std'] for w in train]);phi=predictor.design(m,z)
    s=np.linalg.svd(phi*np.sqrt(weights[:,None]),compute_uv=False)
    h,_=predictor.normal_system(phi,train,weights,frozen['experiment']);reg=frozen['experiment']['regularization'];e=np.maximum(np.linalg.eigvalsh(h)-reg,0)
    report=dict(scope='Post-selection training-only conditioning and raw-trajectory diagnostic; no new fit, validation, confirmation or altered weights.',model_sha256=frozen['sha256'],feature_singular_values=s.tolist(),trajectory_data_eigenvalues=e.tolist(),effective_degrees_of_freedom_per_output=float(np.sum(e/(e+reg))),possible_coefficients_per_output=len(e),activation_quantiles=np.quantile(phi[:,1:],[0,.25,.5,.75,.95,1]).tolist(),raw={})
    for name,model in [('linear',dict(kind='baseline',baseline='linear')),('hermite',dict(kind='baseline',baseline='hermite')),('learned',m)]:
        report['raw'][name]=evaluate_predictions(train,[predictor.predict_packed(model,w['observations'],w['t']) for w in train])
    report['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();report['seconds']=time.perf_counter()-start
    (ROOT/'results/trajectory-fit-diagnostic-v13.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(effective_dof=report['effective_degrees_of_freedom_per_output'],possible=report['possible_coefficients_per_output'],activations=report['activation_quantiles'],training_raw={k:v['aggregate']['position'] for k,v in report['raw'].items()})),flush=True)
if __name__=='__main__':main()
