"""Pre-fit loss weighting checks, with exact zero-strength v21 compatibility."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import sys,json,copy,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT.parents[1]/'tests'))
from test_b4artists_ml_semantic_predictor import windows
import relative_mixture_v22 as m
import mixture_trajectory_v21 as old
import kinematic_trajectory_v20 as parent

def main():
 out=ROOT/'results/relative-mixture-checks-v22.json';assert not out.exists();checks=[]
 rows=windows()
 for i,w in enumerate(rows):w['clip']='synthetic_'+str(i%3)
 errors=np.array([[1,2,3],[.001,.002,.003],[.1,.2,.3],[1,2,3]],dtype=float)
 weight,d=m.cohort_weights(rows,errors,.5,.01);assert abs(weight.sum()-1)<1e-14 and np.all(weight>0)
 mass={r['clip']:r['mass'] for r in d['cohorts']};assert mass['synthetic_1']>mass['synthetic_2']>mass['synthetic_0'];checks.append('normalized positive weights favor low-error cohorts')
 zero,zd=m.cohort_weights(rows,errors,0,.01);np.testing.assert_array_equal(zero,old.statistics(rows)[1]);checks.append('zero relative strength exactly restores original sample weights')
 duplicate=copy.deepcopy(rows)+[copy.deepcopy(rows[0])];dw,dd=m.cohort_weights(duplicate,np.concatenate([errors,errors[:1]]),.5,.01)
 np.testing.assert_allclose([r['mass'] for r in dd['cohorts']],[r['mass'] for r in d['cohorts']],rtol=0,atol=1e-15);checks.append('duplicating an identical row does not change cohort mass')
 order=[3,1,0,2];sw,sd=m.cohort_weights([rows[i] for i in order],errors[order],.5,.01);np.testing.assert_array_equal(sw,weight[order]);checks.append('sample reordering preserves corresponding weights')
 zw,zz=m.cohort_weights(rows,np.zeros_like(errors),.5,.01);np.testing.assert_allclose(zw,zero,rtol=0,atol=1e-15)
 tiny=errors.copy();tiny[1]=0;tw,td=m.cohort_weights(rows,tiny,1,.01);assert np.isfinite(tw).all() and td['error_floor']>0;checks.append('zero and mixed-zero errors have finite bounded normalization')
 for bad,alpha,floor in [(errors[:-1],.5,.01),(-errors,.5,.01),(errors*np.nan,.5,.01),(errors,-1,.01),(errors,2,.01),(errors,.5,0),(errors,.5,np.nan)]:
  try:m.cohort_weights(rows,bad,alpha,floor)
  except ValueError:pass
  else:raise AssertionError('Invalid weighting inputs accepted')
 checks.append('invalid labels and weighting fractions rejected')
 ps=dict(hidden=8,epochs=10,batch_size=4,learning_rate=.001,regularization=0.,velocity_weight=.01,acceleration_weight=.0001,baseline_kind='shape',continuity='C0');pm,_=parent.fit(rows,ps,7)
 spec=dict(hidden=8,epochs=10,batch_size=4,learning_rate=.001,regularization=0.,velocity_weight=.01,acceleration_weight=.0001,initial_probabilities=[.025,.025,.05,.9],relative_fraction=0.,relative_floor_fraction=.01)
 terms=tuple(np.asarray(a) for a in zip(*(old.training_terms(w,old.expert_predictions(pm,w['observations'],w['t']),spec) for w in rows)))
 a,ad=old.fit(rows,terms,pm,spec,7);b,bd=m.fit(rows,terms,pm,spec,7,errors)
 for k in a:np.testing.assert_array_equal(a[k],b[k])
 checks.append('zero-strength complete fit is byte-equivalent at every parameter to v21')
 spec['relative_fraction']=.5;c,cd=m.fit(rows,terms,pm,spec,7,errors);np.testing.assert_array_equal(c['mean'],a['mean']);np.testing.assert_array_equal(c['std'],a['std']);assert cd['training_objective']<cd['initial_objective'];assert any(not np.array_equal(c[k],a[k]) for k in ('w0','w1','b0','b1'))
 checks.append('relative weighting changes supervised fit while preserving feature normalization')
 w=rows[0];p=m.predict_packed(c,w['observations'],w['t']);w['target'][:]=np.nan;errors[:]=np.nan;np.testing.assert_array_equal(p,m.predict_packed(c,w['observations'],w['t']));checks.append('inference does not access training errors or labels')
 result=dict(passed=True,checks=checks,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'relative_mixture_v22.py',ROOT/'mixture_trajectory_v21.py']},scope='Pre-fit weighting correctness; original predictor invariants retained under pinned source')
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
