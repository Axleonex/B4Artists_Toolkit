"""Verify fixed readout reproducibility and summarize all exposed cohorts."""
from pathlib import Path
import copy,json,hashlib
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=ROOT/'results/soft-selector-verification-v27.json';assert not out.exists();a=ROOT/'results/soft_selector_v27';b=ROOT/'results/soft_selector_v27_repeat';reports=[]
    for folder in (a,b):
        complete=read(folder/'complete.json');report=read(folder/'report.json');assert complete['complete'] and complete['report_sha256']==sha(folder/'report.json') and report['selection']['best_learned_sha256']==sha(folder/'best_learned.npz') and not report['confirmation_read'];reports.append(report)
    identical={}
    for name in ('protocol.json','selection_frozen.json','best_learned.npz','probabilities.json'):
        identical[name]=sha(a/name);assert identical[name]==sha(b/name),name
    normalized=[]
    for value in reports:
        value=copy.deepcopy(value);value.pop('runtime');value['model_files']={Path(k).name:v for k,v in value['model_files'].items()};normalized.append(value)
    assert normalized[0]==normalized[1];report=reports[0];parent=read(ROOT/'results/projected_selector_v26/report.json');rows=[]
    assert report['protocol']['gates']==parent['protocol']['gates'] and report['protocol']['projection']==parent['protocol']['projection']
    for part in ('old_validation','new_validation'):
        for name in report['protocol']['baselines']:assert report['partition_reports'][part][name]==parent['partition_reports'][part][name]
        for key,value in report['partition_reports'][part]['mlp']['cohorts'].items():
            den=max(min(report['partition_reports'][part][name]['cohorts'][key]['position'] for name in report['protocol']['baselines']),1e-12);ratio=value['position']/den;old=parent['partition_reports'][part]['mlp']['cohorts'][key]['position']/den
            rows.append(dict(partition=part,cohort=key,ratio=ratio,v26ratio=old,passed=ratio<=1.1,new_failure=ratio>1.1 and old<=1.1,cleared=ratio<=1.1 and old>1.1))
    rows.sort(key=lambda x:-x['ratio']);assert len(rows)==96
    for n,h in report['source_sha256'].items():assert sha(ROOT/n)==h,n
    proof=dict(passed=True,deterministic_reports_equal=True,identical_sha256=identical,cohorts=96,failed=sum(not r['passed'] for r in rows),cleared=[r['cohort'] for r in rows if r['cleared']],new_failures=[r['cohort'] for r in rows if r['new_failure']],rows=rows,development_gates=report['development_gates'],quality_qualified=report['gates']['best_learned']['passed'],new_training=False,refit=False,confirmation_read=False,full_goal_complete=False,model_sha256=report['selection']['best_learned_sha256'],primary_report_sha256=sha(a/'report.json'),repeat_report_sha256=sha(b/'report.json'),source_sha256=sha(Path(__file__)),scope='Complete independent fixed-readout evaluation reproduction, exact original control retention, and exposed cohort comparison. Weights were not retrained; no new quality or usability attestation.')
    out.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:proof[k] for k in ('passed','deterministic_reports_equal','cohorts','failed','cleared','new_failures','quality_qualified')}))
if __name__=='__main__':main()
