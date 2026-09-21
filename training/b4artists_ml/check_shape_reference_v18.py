"""Independent closed-form/invariant checks, no training or host mutation."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tests'))
import numpy as np
from dataclasses import replace
from test_b4artists_ml_semantic_predictor import windows
from shape_reference import harmonic_tangent,reference
from semantic_motion_data import baseline
ROOT=Path(__file__).resolve().parent

def main():
    checks=[]
    np.testing.assert_allclose(harmonic_tangent(np.array([1.,0.,-1.]),np.array([4.,2.,1.]),1.,2.),[1.5,0.,0.],rtol=0,atol=1e-14);checks.append('closed-form weighted slope, zero and reversal')
    base=windows()[0]['observations'];rng=np.random.default_rng(18);t=np.linspace(0,1,257)
    for i in range(50):
        p=rng.normal(size=(4,17,3));o=replace(base,positions=p,duration=float(rng.uniform(1,40)*base.dt));v=reference(o,t).reshape(-1,17,9)[...,:3]
        assert np.all(v>=np.minimum(p[0],p[1])-1e-12) and np.all(v<=np.maximum(p[0],p[1])+1e-12)
        sign=np.sign(p[1]-p[0]);assert np.min(np.diff(v,axis=0)*sign)>-1e-12
        np.testing.assert_array_equal(v[0],p[0]);np.testing.assert_array_equal(v[-1],p[1])
    checks.append('50 randomized contextual curves remain monotone within endpoint component bounds')
    p=np.repeat(base.positions[:1],4,axis=0);p[0,:,0]=0.;p[1,:,0]=1.;p[2,:,0]=-100.;p[3,:,0]=101.;o=replace(base,positions=p,duration=32*base.dt)
    old=baseline(o,t,contextual=True).reshape(-1,17,9)[...,:3];new=reference(o,t).reshape(-1,17,9)[...,:3];assert np.max(abs(old[...,0]))>100 and new[...,0].min()>=0 and new[...,0].max()<=1;checks.append('extreme known-context overshoot is bounded')
    masked=replace(o,context=False);np.testing.assert_array_equal(reference(masked,t),baseline(masked,t));checks.append('no-context reference is unchanged linear/SLERP')
    p=np.repeat(base.positions[:1],4,axis=0);o=replace(base,positions=p);v=reference(o,t).reshape(-1,17,9)[...,:3];np.testing.assert_allclose(v,np.broadcast_to(p[0],v.shape),atol=1e-14,rtol=0);checks.append('stationary positions preserved')
    for bad in [-1.,0.,float('nan')]:
        try:harmonic_tangent(np.ones(3),np.ones(3),bad,1.)
        except ValueError:pass
        else:raise AssertionError('Invalid timing accepted')
    checks.append('invalid timing rejected')
    result=dict(passed=True,checks=checks,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'shape_reference.py']},scope='Procedural reference math only; not trained animation, physical projection, multi-window C1 or human-quality acceptance.')
    out=ROOT/'results/shape-reference-checks-v18.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
