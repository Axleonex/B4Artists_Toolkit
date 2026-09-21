"""Describe every exposed cohort and selected proposal without further fitting."""
from pathlib import Path
import json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parent

def main():
    out=ROOT/'results/projected-selector-failure-attribution-v26.json';assert not out.exists()
    a=ROOT/'results/projected_selector_v26';b=ROOT/'results/curve_mixture_v23'
    complete=json.loads((a/'complete.json').read_text());assert complete['complete'] and complete['report_sha256']==hashlib.sha256((a/'report.json').read_bytes()).hexdigest()
    new=json.loads((a/'report.json').read_text());old=json.loads((b/'report.json').read_text());choices=json.loads((a/'choices.json').read_text());grouped={}
    for row in choices:grouped.setdefault(f"{row['clip']}/gap{row['gap']}/context{int(row['context'])}",[]).append(row)
    rows=[]
    for part in ('old_validation','new_validation'):
        report=new['partition_reports'][part];prior=old['partition_reports'][part]
        for key,value in report['mlp']['cohorts'].items():
            controls={n:report[n]['cohorts'][key]['position'] for n in new['protocol']['baselines']};best=min(controls,key=controls.get);den=controls[best]
            ratio=value['position']/max(den,1e-12);before=prior['mlp']['cohorts'][key]['position']/max(den,1e-12);selected=grouped[key]
            rows.append(dict(partition=part,cohort=key,ratio=ratio,prior_ratio=before,passed=ratio<=1.1,prior_passed=before<=1.1,new_failure=ratio>1.1 and before<=1.1,cleared_failure=ratio<=1.1 and before>1.1,best_procedural=best,position=value['position'],controls=controls,choice_histogram=np.bincount([r['choice'] for r in selected],minlength=12).tolist(),learned_expert_windows=sum(r['uses_frozen_learned_expert'] for r in selected),windows=len(selected)))
    rows.sort(key=lambda r:-r['ratio'])
    result=dict(scope='Exposed development diagnosis only; no refitting, threshold changes or confirmation reads',cohorts=len(rows),failed=sum(not r['passed'] for r in rows),prior_failed=sum(not r['prior_passed'] for r in rows),newly_failed=[r['cohort'] for r in rows if r['new_failure']],cleared=[r['cohort'] for r in rows if r['cleared_failure']],improved_cohorts=sum(r['ratio']<r['prior_ratio'] for r in rows),worsened_cohorts=sum(r['ratio']>r['prior_ratio'] for r in rows),rows=rows,model_sha256=new['selection']['best_learned_sha256'],development_gates=new['development_gates'],report_sha256={p.parent.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [a/'report.json',b/'report.json']},source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),full_goal_complete=False)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ('cohorts','failed','prior_failed','newly_failed','cleared','improved_cohorts','worsened_cohorts')}),flush=True)
if __name__=='__main__':main()
