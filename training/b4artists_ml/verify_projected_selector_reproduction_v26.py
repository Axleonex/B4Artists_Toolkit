"""Complete fitted-label and learned-selector reproduction; timings stay separate."""
from pathlib import Path
import json,hashlib,copy
import numpy as np
ROOT=Path(__file__).resolve().parent

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=ROOT/'results/projected-selector-reproduction-v26.json';assert not out.exists()
    a=ROOT/'results/projected_selector_v26';b=ROOT/'results/projected_selector_v26_repeat'
    for directory in (a,b):
        complete=read(directory/'complete.json');assert complete['complete'] and complete['report_sha256']==sha(directory/'report.json')
    deterministic=['protocol.json','manifest.json','parent_membership.json','window_identity.json','labels.npz','label_manifest.json','cost_normalizers.json','best_learned.npz','selection_frozen.json','choices.json']
    identical={}
    for name in deterministic:
        assert sha(a/name)==sha(b/name),name;identical[name]=sha(a/name)
    ma=read(a/'label_manifest.json');mb=read(b/'label_manifest.json');assert ma==mb
    assert ma['training_windows']==7358 and ma['features']==596 and ma['candidates']==12
    for chunk in ma['chunks']:
        name=chunk['path'];assert sha(a/name)==sha(b/name)==chunk['sha256'];identical[name]=chunk['sha256']
    with np.load(a/'labels.npz',allow_pickle=False) as archive:
        x=archive['features'];values=archive['metrics'];assert x.shape==(7358,596) and values.shape==(7358,12,9)
        assert np.isfinite(x).all() and np.isfinite(values).all()
        for chunk in ma['chunks']:
            with np.load(a/chunk['path'],allow_pickle=False) as c:
                sl=slice(chunk['start'],chunk['end']);np.testing.assert_array_equal(c['indices'],np.arange(chunk['start'],chunk['end']));np.testing.assert_array_equal(c['features'],x[sl]);np.testing.assert_array_equal(c['metrics'],values[sl])
    ra=read(a/'report.json');rb=read(b/'report.json');original_reports=[sha(a/'report.json'),sha(b/'report.json')]
    runtimes=[r.pop('runtime') for r in (ra,rb)]
    for report in (ra,rb):report['model_files']={Path(k).name:v for k,v in report['model_files'].items()}
    assert ra==rb,'Deterministic report mismatch'
    assert not ra['confirmation_read'] and ra['source_sha256']==ma['source_sha256']
    for n,h in ra['source_sha256'].items():assert sha(ROOT/n)==h,n
    for n,h in {**ra['protocol']['source_manifests'],**ra['protocol']['parent_files'],**ra['protocol']['diagnostic_files']}.items():assert sha(ROOT/n)==h,n
    result=dict(passed=True,scope='Complete independent label regeneration, feature/ownership cache, fit, model and deployed old/new/combined metrics. Only runtime, event/progress timing and directory-qualified model paths differ.',model_artifacts=1,training_windows=7358,projected_candidate_windows=7358*12,identical_sha256=identical,model_sha256=identical['best_learned.npz'],report_sha256=original_reports,deterministic_reports_equal=True,runtimes=runtimes,development_gates=ra['development_gates'],full_goal_complete=False,confirmation_read=False)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ('passed','training_windows','projected_candidate_windows','model_sha256','deterministic_reports_equal')}),flush=True)
if __name__=='__main__':main()
