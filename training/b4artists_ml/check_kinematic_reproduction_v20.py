"""Compare independent v19 runs, allowing only their model path prefix to differ."""
from pathlib import Path
import copy,json,hashlib
from fetch_cmu_temporal_v19 import sha,read,write,require
ROOT=Path(__file__).resolve().parent

def main():
    folders=[ROOT/'results'/n for n in ['kinematic_trajectory_v20','kinematic_trajectory_v20_repeat']]
    reports=[read(p/'report.json') for p in folders]
    identical={}
    files=sorted(p.name for p in folders[0].glob('*.npz'));require(len(files)==6,'Six model artifacts required')
    for n in files:
        require(sha(folders[0]/n)==sha(folders[1]/n),'Model reproduction failed: '+n);identical[n]=sha(folders[0]/n)
    docs=['protocol.json','manifest.json','folds.json','internal_diagnostic.json','selection_frozen.json']
    for n in docs:require((folders[0]/n).read_bytes()==(folders[1]/n).read_bytes(),'Diagnostic reproduction failed: '+n)
    for report in reports:
        report.pop('runtime')
        for rel,h in report['model_files'].items():require(sha(ROOT/rel)==h,'Reported model hash does not match bytes')
        report['model_files']={Path(rel).name:h for rel,h in report['model_files'].items()}
    require(reports[0]==reports[1],'Non-runtime research report differs')
    result=dict(passed=True,model_artifacts=6,identical_sha256=identical,identical_diagnostic_files=docs,non_runtime_reports_identical=True,allowed_difference='The output directory prefix in model_files is normalized only after each actual path and hash is verified. Runtime timings/platform fields omitted as in prior reproduction.',runtime_performance_claim=False,confirmation_accessed=False,source_sha256={Path(__file__).name:sha(Path(__file__))},report_sha256={p.name:sha(p/'report.json') for p in folders})
    write(ROOT/'results/kinematic-trajectory-reproduction-v20.json',result);print(json.dumps(result),flush=True)
if __name__=='__main__':main()
