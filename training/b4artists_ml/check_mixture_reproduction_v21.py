"""Verify independent fixed-mixture fits and every non-runtime result."""
from pathlib import Path
import json
from fetch_cmu_temporal_v19 import sha,read,write,require
ROOT=Path(__file__).resolve().parent

def main():
 folders=[ROOT/'results'/n for n in ['mixture_trajectory_v21','mixture_trajectory_v21_repeat']]
 reports=[read(p/'report.json') for p in folders]
 require(sha(folders[0]/'best_learned.npz')==sha(folders[1]/'best_learned.npz'),'Model reproduction failed')
 docs=['protocol.json','manifest.json','parent_membership.json','selection_frozen.json','expert_strengths.json']
 for n in docs:require((folders[0]/n).read_bytes()==(folders[1]/n).read_bytes(),'Diagnostic reproduction failed: '+n)
 for report in reports:
  report.pop('runtime')
  for rel,h in report['model_files'].items():require(sha(ROOT/rel)==h,'Reported model hash differs')
  report['model_files']={Path(rel).name:h for rel,h in report['model_files'].items()}
 require(reports[0]==reports[1],'Non-runtime reports differ')
 out=ROOT/'results/mixture-trajectory-reproduction-v21.json';require(not out.exists(),'Evidence already exists')
 result=dict(passed=True,model_artifacts_per_run=1,identical_sha256={'best_learned.npz':sha(folders[0]/'best_learned.npz')},identical_diagnostic_files=docs,non_runtime_reports_identical=True,allowed_difference='Output path normalized after actual path/hash verification; runtime fields omitted. Parent weights are verified existing artifacts, not retrained in this experiment.',confirmation_accessed=False,source_sha256={Path(__file__).name:sha(Path(__file__))},report_sha256={p.name:sha(p/'report.json') for p in folders})
 write(out,result);print(json.dumps(result),flush=True)
if __name__=='__main__':main()
