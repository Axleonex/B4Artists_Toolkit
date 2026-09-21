"""Describe every exposed development cohort; no fitting or new holdout reads."""
from pathlib import Path
import json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parent

def main():
 paths=[ROOT/'results'/n/'report.json' for n in ['joint_mixture_v24','curve_mixture_v23']]
 new,old=[json.loads(p.read_text()) for p in paths];strengths=json.loads((paths[0].parent/'expert_strengths.json').read_text());groups={}
 for row in strengths['rows']:groups.setdefault(f"{row['clip']}/gap{row['gap']}/context{int(row['context'])}",[]).append(dict(position=row['position_strengths'],rotation=row['rotation_strengths']))
 rows=[]
 for part in ['old_validation','new_validation']:
  v=new['partition_reports'][part];prior=old['partition_reports'][part]
  for key,value in v['mlp']['cohorts'].items():
   controls={k:v[k]['cohorts'][key]['position'] for k in ['projected_linear','projected_hermite','projected_shape']};best=min(controls,key=controls.get);den=controls[best]
   ratio=value['position']/den;before=prior['mlp']['cohorts'][key]['position']/den
   rows.append(dict(partition=part,cohort=key,ratio=ratio,prior_ratio=before,passed=ratio<=1.1,prior_passed=before<=1.1,new_failure=ratio>1.1 and before<=1.1,best_procedural=best,position=value['position'],controls=controls,mean_position_strengths=np.mean([g['position'] for g in groups[key]],axis=0).tolist(),mean_rotation_strengths=np.mean([g['rotation'] for g in groups[key]],axis=0).tolist()))
 rows.sort(key=lambda x:-x['ratio'])
 result=dict(scope='Exposed development diagnosis, no model fitting, threshold changes or confirmation reads',cohorts=len(rows),failed=sum(not x['passed'] for x in rows),prior_failed=sum(not x['prior_passed'] for x in rows),newly_failed=[x['cohort'] for x in rows if x['new_failure']],improved_cohorts=sum(x['ratio']<x['prior_ratio'] for x in rows),worsened_cohorts=sum(x['ratio']>x['prior_ratio'] for x in rows),position_expert_order=strengths['position_expert_order'],rotation_expert_order=strengths['rotation_expert_order'],rows=rows,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__)]},report_sha256={p.parent.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
 out=ROOT/'results/joint-failure-attribution-v24.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('rows','source_sha256','report_sha256')}))
if __name__=='__main__':main()
