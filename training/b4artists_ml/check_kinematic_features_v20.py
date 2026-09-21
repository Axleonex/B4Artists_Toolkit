"""Training-only conditioning audit: invertibility, bounds, units and masks."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import sys,json,hashlib,copy
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tests'))
from test_b4artists_ml_semantic_predictor import windows
from semantic_motion_data import load_windows
from kinematic_features_v20 import features,scales
from shape_trajectory import observation_scale
ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bounds(f):
    result=[]
    for section in [f[153:255],f[255:357],f[357:459]]:
        result.extend([float(np.max(np.linalg.norm(section[:51].reshape(17,3),axis=1))),float(np.max(np.linalg.norm(section[51:].reshape(17,3),axis=1)))])
    return np.array(result)

def check(x):
    before=x.copy();f=features(x);absolute,amp=scales(x);np.testing.assert_array_equal(before,x)
    assert f.shape==(548,) and np.isfinite(f).all();np.testing.assert_array_equal(f[:153],absolute[:153]);np.testing.assert_array_equal(f[459:514],absolute[459:])
    # Reconstruction must use the serialized feature vector alone.
    recovered_amp=np.r_[np.repeat(f[514:531],3),np.repeat(f[531:548],3)]
    np.testing.assert_array_equal(recovered_amp,amp)
    error=0.
    for sl,k in [(slice(153,255),1.),(slice(255,357),x[-2]),(slice(357,459),x[-2])]:error=max(error,float(np.max(abs(f[sl]*recovered_amp-absolute[sl]*k))))
    assert error<1e-8
    stretched=x.copy();stretched[-2:]*=3.7
    unit=float(np.max(abs(features(stretched)[153:459]-f[153:459])));assert unit<1e-9
    limits=np.array([1,np.pi/2,2,np.pi,2,np.pi]);b=bounds(f);assert np.all(b<=limits+1e-6)
    return error,unit,b

def main():
    checks=[];small=windows();x=small[0]['x'].copy();check(x);checks.append('Observed motion is reconstructible from amplitudes and normalized components; original input/start pose/rest/timing remain intact')
    rest=x.copy();p=rest[:612].reshape(4,17,9);p[1:]=p[0];assert not np.any(features(rest)[153:459]);checks.append('Exactly stationary observations have exactly zero kinematic descriptors')
    absent=x.copy();absent[-4:-2]=0.;junk=absent.copy();junk[:612].reshape(4,17,9)[2:]=37.;np.testing.assert_array_equal(features(absent),features(junk));checks.append('Unavailable neighboring poses cannot affect features')
    changed=x.copy();changed[-2:]*=3.7;np.testing.assert_allclose(features(x)[153:459],features(changed)[153:459],rtol=0,atol=1e-9);np.testing.assert_array_equal(features(changed)[512:514],changed[-2:]);checks.append('Normalized path descriptors are independent of uniform time-unit scaling while actual timing remains explicit')
    for invalid in [np.full(667,np.nan),x[:-1],np.r_[x[:-1],0.]]:
        try:features(invalid)
        except ValueError:pass
        else:raise AssertionError('Invalid input accepted')
    checks.append('Malformed, nonfinite and zero-time observations rejected')
    model_scales=observation_scale(small[0]['observations']).reshape(17,9);_,amp=scales(small[0]['x']);np.testing.assert_allclose(amp[:51].reshape(17,3),model_scales[:,:3],atol=1e-12);np.testing.assert_allclose(amp[51:].reshape(17,3),model_scales[:,3:6],atol=1e-12);checks.append('Input amplitudes agree with the existing decoder amplitudes')
    protocol=json.loads((ROOT/'expanded_trajectory_protocol_v19.json').read_text());manifest=json.loads((ROOT/'temporal_training_manifest_v19.json').read_text());rows=load_windows(ROOT,manifest,'train',protocol);assert len(rows)==7358
    reconstruction=0.;units=0.;largest=np.zeros(6);zero_count=0
    for w in rows:
        a,b,c=check(w['x']);reconstruction=max(reconstruction,a);units=max(units,b);largest=np.maximum(largest,c);zero_count+=int(np.any(scales(w['x'])[1]==0))
    checks.append('All7358 training observations satisfy reconstructibility, theoretical norm bounds and time-scaling checks')
    result=dict(passed=True,input_features=548,reconstruction_uses_only_feature_vector=True,checks=checks,training_windows=len(rows),validation_read=False,confirmation_read=False,reconstruction_error_max=reconstruction,time_scaling_descriptor_error_max=units,block_norm_max=largest.tolist(),theoretical_limits=[1,float(np.pi/2),2,float(np.pi),2,float(np.pi)],windows_with_zero_amplitude=zero_count,source_sha256={n:sha(ROOT/n) for n in ['kinematic_features_v20.py','check_kinematic_features_v20.py','temporal_training_manifest_v19.json','expanded_trajectory_protocol_v19.json']},interpretation='This resolves avoidable input/output unit coupling without losing observed motion information. It does not establish improved learned quality; a prospectively fixed training comparison is still required.')
    p=ROOT/'results/kinematic-features-complete-checks-v20.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
