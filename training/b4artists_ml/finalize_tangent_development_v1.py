"""Summarize frozen development results without changing their acceptance."""
from pathlib import Path
import json,hashlib
TR=Path(__file__).resolve().parent;ROOT=TR.parents[1];BASE=TR/'results/sequence-tangent-development-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 r=read(BASE/'report.json');old=read(TR/'results/sequence-development-v1/report.json');assert r['complete'] and r['protected_baselines_match'] and not r['confirmation_read'];analysis={};table=['| Seed | Position ratio | Velocity ratio | Acceleration ratio | Worst cohort ratio | All partitions pass |','|---|---:|---:|---:|---:|---|']
 for m in r['models']:
  name=m['name'];prior=name.removeprefix('tangent-');gate=r['development_gates'][name]['combined'];passed=all(v['passed'] for v in r['development_gates'][name].values());ratio=gate.get('ratios',{});table.append(f"| {m['seed']} | {ratio.get('position',float('nan')):.3f} | {ratio.get('velocity',float('nan')):.3f} | {ratio.get('acceleration',float('nan')):.3f} | {gate.get('max_cohort_position_ratio',float('nan')):.3f} | {passed} |")
  if name in r['failed_candidates']:analysis[name]=dict(error=r['failed_candidates'][name],passed=False);continue
  groups={}
  for context in (0,1):
   selected=[k for k in r['partition_reports']['combined'][name]['cohorts'] if k.endswith('/context'+str(context))];values={}
   for label,report,key in [('new',r,name),('previous',old,prior),('shape',r,'projected_shape')]:
    cohorts=report['partition_reports']['combined'][key]['cohorts'];values[label]={metric:sum(cohorts[k][metric] for k in selected)/len(selected) for metric in ('position','rotation','velocity','acceleration')}
   groups['context'+str(context)]=dict(cohorts=len(selected),equally_weighted_cohort_mean=values)
  analysis[name]=dict(passed_all_partitions=passed,original_gates=r['development_gates'][name],context_groups=groups)
 output=dict(complete=True,report_sha256=sha(BASE/'report.json'),prior_report_sha256=sha(TR/'results/sequence-development-v1/report.json'),models=analysis,context_grouping_is_diagnostic_only=True,acceptance_changed=False,models_changed=False,confirmation_read=False,full_goal_complete=False);p=BASE/'comparison-to-previous.json';assert not p.exists();p.write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
 allpass=all(r['family_passes'].values());judgment='Both fixed seeds pass the original development gates. This is not full tool qualification; native learned workflows, sealed confirmation, human usability and equivalent Cascadeur comparison remain required.' if allpass else 'The tested tangent-conditioning configuration does not pass the original development requirements. No model is promoted or bundled. A completed fit and stronger context response cannot substitute for the failed gates.'
 lines=['# Tangent-conditioned sequence development','',judgment,'','Both60-epochfits and the protocol were frozen before evaluation. All768original development windows were evaluated; the three projected procedural controls reproduced the original references exactly. Old, new and combined partitions retain their original gates.','']+table+['','Ratios below1mean lower error. Original requirements include position at most0.95, velocity/acceleration at most1.05, and each cohort at most1.10. Endpoints and physical edge checks remain separate.','', '## Context diagnostic','']
 for name,a in analysis.items():
  if 'context_groups' not in a:continue
  lines.append(name)
  for group,v in a['context_groups'].items():
   q=v['equally_weighted_cohort_mean'];lines.append(f"- {group}: position error {q['new']['position']:.6f}, previous model {q['previous']['position']:.6f}, shape control {q['shape']['position']:.6f}.")
  lines.append('')
 lines+=['These context summaries are equally weighted cohort means and do not replace acceptance aggregation. Development data has been repeatedly exposed; it is not an unbiased confirmation set. All six confirmation clips remain unopened.','', 'No new fit follows automatically from this result. Preserve both seeds and failure evidence. A further learned-motion experiment requires a new bounded hypothesis rather than adjacent tuning. Continue the independent responsiveness and full physics/intent/workflow requirements.','', 'Evidence: training/b4artists_ml/results/sequence-tangent-development-v1/report.json and comparison-to-previous.json. The original goal, deadline, evaluation ceiling and qualification requirements remain unchanged.']
 text='\n'.join(lines)+'\n'
 for a,b in {'Both60-epochfits':'Both 60-epoch fits','All768original':'All 768 original','below1mean':'below 1 mean','most0.95':'most 0.95','most1.05':'most 1.05','most1.10':'most 1.10'}.items():text=text.replace(a,b)
 doc=ROOT/'docs/b4artists_ml/TANGENT-SEQUENCE-DEVELOPMENT-v1.md';assert not doc.exists();doc.write_text(text,encoding='utf-8');print(json.dumps(dict(complete=True,family_passes=r['family_passes'],models={n:a.get('original_gates',{}).get('combined',{}) for n,a in analysis.items()})),flush=True)
if __name__=='__main__':main()
