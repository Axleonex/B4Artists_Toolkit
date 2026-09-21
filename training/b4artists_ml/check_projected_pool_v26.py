"""Arithmetic and isolation checks for fitted proposal diagnostics."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import sys,json,hashlib,copy
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'tests'))
from test_b4artists_ml_semantic_predictor import windows
from motion_coverage import evaluate_predictions
import kinematic_trajectory_v20 as parent
import projected_pool_v26 as pool

def main():
    out=ROOT/'results/projected-pool-checks-v26.json';assert not out.exists()
    rows=windows();spec=dict(hidden=8,epochs=10,batch_size=4,learning_rate=.001,regularization=0.,velocity_weight=.01,acceleration_weight=.0001,baseline_kind='shape',continuity='C0')
    model,_=parent.fit(rows,spec,7);checks=[]
    predictions=[pool.expert_predictions(model,w['observations'],w['t']) for w in rows]
    for w,values in zip(rows,predictions):
        before=np.asarray(values).copy();v=before.reshape(4,-1,17,9)
        for i,(p,r) in enumerate(pool.CANDIDATES):
            combined=pool.combine(values,i).reshape(-1,17,9)
            np.testing.assert_array_equal(combined[...,:3],v[p,...,:3])
            np.testing.assert_array_equal(combined[...,3:],v[pool.ROTATION_INDEX[r],...,3:])
            np.testing.assert_array_equal(combined[[0,-1]],v[0,[0,-1]])
            combined[:]=99;np.testing.assert_array_equal(values,before)
        for original,index in enumerate(pool.BASELINE_INDEX):np.testing.assert_array_equal(pool.combine(values,index),values[original])
    checks+=['All12candidates use the declared positions and rotations without blending or aliasing','All original projected controls are exact members of the pool','Authored endpoints remain exact']
    values=predictions[0]
    for index in (-1,12,True,1.5):
        try:pool.combine(values,index)
        except ValueError:pass
        else:raise AssertionError('Invalid index accepted')
    for bad in (np.asarray(values)[:3],np.full_like(values,np.nan)):
        try:pool.combine(bad,0)
        except ValueError:pass
        else:raise AssertionError('Invalid proposal accepted')
    bad=np.asarray(values).copy().reshape(4,-1,17,9);bad[2,1,0,3]+=.001
    try:pool.combine(bad.reshape(4,-1,153),0)
    except ValueError:pass
    else:raise AssertionError('Changed shape/Hermite rotation equivalence accepted')
    checks.append('Invalid index, nonfinite/malformed proposals and changed baseline equivalence fail closed')
    groups=[[pool.metrics(w,pool.combine(p,i)) for i in range(12)] for w,p in zip(rows,predictions)]
    for i in range(12):
        direct=evaluate_predictions(rows,[pool.combine(p,i) for p in predictions]);composed=pool.report(rows,groups,np.full(len(rows),i),0.)
        assert composed['cohorts']==direct['cohorts']
        assert {k:v for k,v in composed['aggregate'].items() if k!='true_edge_length_max'}==direct['aggregate']
    checks.append('Stored window metrics aggregate exactly like the original evaluator')
    before=pool.combine(values,11);rows[0]['target'][:]=np.nan
    np.testing.assert_array_equal(pool.combine(pool.expert_predictions(model,rows[0]['observations'],rows[0]['t']),11),before)
    checks.append('Proposal construction reads observations only; hidden label mutation cannot change it')
    sources={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['projected_pool_v26.py','check_projected_pool_v26.py','curve_mixture_v23.py','kinematic_trajectory_v20.py','temporal_model.py','motion_coverage.py']}
    result=dict(passed=True,checks=checks,source_sha256=sources,scope='Tiny independent arithmetic/observation fixtures; no corpus validation or inference quality claim')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=len(checks))),flush=True)
if __name__=='__main__':main()
