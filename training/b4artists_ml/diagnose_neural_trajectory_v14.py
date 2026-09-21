"""Training-only generalization diagnostic after immutable v14 selection."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import json,hashlib
import numpy as np
import neural_trajectory as model
from semantic_projection import load_windows
from motion_coverage import evaluate_predictions
ROOT=Path(__file__).resolve().parent

def main():
    folder=ROOT/'results/neural_trajectory_v14';frozen=json.loads((folder/'selection_frozen.json').read_text());protocol=json.loads((folder/'protocol.json').read_text());manifest=json.loads((folder/'manifest.json').read_text());path=folder/'best_learned.npz';assert hashlib.sha256(path.read_bytes()).hexdigest()==frozen['sha256']
    m=model.load(path);train,_=load_windows(ROOT,manifest,'train',protocol);reports={}
    for name,which in [('linear',dict(kind='baseline',baseline='linear')),('hermite',dict(kind='baseline',baseline='hermite')),('learned_fit',m)]:
        reports[name]=evaluate_predictions(train,[model.predict_packed(which,w['observations'],w['t']) for w in train])
    trials=json.loads((folder/'internal_trials.json').read_text());reports['learned_excluded_group']=next(r['report'] for r in trials if r['id']==frozen['id'])
    summary={}
    for name,r in reports.items():
        summary[name]={}
        for gap in protocol['gaps']:
            for context in [0,1]:
                rows=[v for k,v in r['cohorts'].items() if k.endswith('/gap'+str(gap)+'/context'+str(context))]
                summary[name]['gap'+str(gap)+'/context'+str(context)]={k:float(np.mean([v[k] for v in rows])) for k in ['position','root','rotation','velocity','acceleration']}
    contrasts=[]
    for cohort,row in reports['learned_excluded_group']['cohorts'].items():
        baseline=min(reports[name]['cohorts'][cohort]['position'] for name in ['linear','hermite']);contrasts.append(dict(cohort=cohort,baseline=baseline,learned=row['position'],ratio=row['position']/max(baseline,1e-12),absolute_delta=row['position']-baseline))
    contrasts.sort(key=lambda r:r['absolute_delta'],reverse=True)
    report=dict(scope='Post-selection training-only diagnostic; fit and excluded-group metrics on the same training windows distinguish fitting from catalog-group transfer. Not blind evaluation or tuning.',model_sha256=frozen['sha256'],reports=reports,gap_context_summary=summary,worst_absolute_regressions=contrasts[:20],source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (ROOT/'results/neural-trajectory-diagnostic-v14.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(aggregate={k:v['aggregate'] for k,v in reports.items()},worst=contrasts[:3])),flush=True)
if __name__=='__main__':main()
