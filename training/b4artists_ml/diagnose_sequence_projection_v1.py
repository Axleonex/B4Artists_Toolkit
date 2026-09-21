"""Paired raw/projected diagnosis for already-frozen development predictions."""
from pathlib import Path
import os,time,json,hashlib,copy
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
import numpy as np
from sequence_provider_v2 import Provider
from semantic_projection import load_windows
from motion_coverage import evaluate_predictions
from kinematic_trajectory_v20 import predict_packed as control
ROOT=Path(__file__).resolve().parents[2];TR=Path(__file__).resolve().parent;BASE=TR/'results/sequence-projection-diagnosis-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def main():
 report_path=TR/'results/sequence-development-v1/report.json';prior=read(report_path);assert prior['complete'] and not any(prior['family_passes'].values())
 frozen=read(TR/'results/sequence-development-v1/frozen-before-validation.json');protocol=read(TR/'expanded_trajectory_protocol_v19.json');evidence=read(ROOT/'docs/b4artists_ml/goalposts/private-production-evidence-v1.json')
 BASE.mkdir(exist_ok=False);plan=dict(selection='All768original development windows and all4frozen models; three unchanged raw controls. No selection, fitting or projection changes.',prior_report_sha256=sha(report_path),frozen_sha256=sha(TR/'results/sequence-development-v1/frozen-before-validation.json'),script_sha256=sha(Path(__file__)),models=frozen['models'],sources={n:sha(TR/n) for n in ('sequence_provider_v2.py','sequence_numpy_v1.py','semantic_projection.py','motion_coverage.py','kinematic_trajectory_v20.py')},retraining=False,confirmation_read=False,raw_metrics_are_not_qualification=True,max_seconds=1200);write(BASE/'plan.json',plan)
 windows,_=load_windows(TR,read(TR/'temporal_training_manifest_v19.json'),'validation',protocol)
 parts={'old_validation':[w for w in windows if w['clip'] in protocol['old_validation_clips']],'new_validation':[w for w in windows if w['clip'] in protocol['new_validation_clips']]}
 identities={p:[dict(clip=w['clip'],gap=w['gap'],context=w['context'],frames=w['frame'].tolist()) for w in rows] for p,rows in parts.items()};assert identities==read(TR/'results/sequence-development-v1/window-identities.json')
 methods=[dict(name='projected_'+b,baseline=b) for b in ('linear','hermite','shape')]+plan['models'];reports={p:{} for p in (*parts,'combined')};started=time.perf_counter()
 for method in methods:
  name=method['name'];provider=None if 'baseline' in method else Provider(ROOT/method['weights'],method['weights_sha256'],kind=method['kind'],seed=method['seed']);all_rows=[];all_raw=[];all_projected=[]
  for part,rows in parts.items():
   raw=[];projected=[]
   for offset in range(0,len(rows),16):
    assert time.perf_counter()-started<1200 and time.time()<1789053845.
    batch=rows[offset:offset+16]
    raw.extend(control(dict(kind='baseline',baseline=method['baseline']),w['observations'],w['t']) if provider is None else provider.predict_packed(w['observations'],w['t']) for w in batch)
    file=TR/'results/sequence-development-v1'/name/(part+'-'+str(offset)+'.npz');relative=file.relative_to(ROOT).as_posix();assert sha(file)==evidence['artifacts'][relative]
    with np.load(file,allow_pickle=False) as z:projected.extend(z[str(i)] for i in range(len(batch)))
    write(BASE/'progress.json',dict(method=name,partition=part,windows_completed=offset+len(batch),seconds=time.perf_counter()-started))
   raw_metrics=evaluate_predictions(rows,raw);projected_metrics=evaluate_predictions(rows,projected);expected=copy.deepcopy(prior['partition_reports'][part][name]);expected.pop('projection');expected['aggregate'].pop('true_edge_length_max');assert projected_metrics==expected,'Stored projection reproduction mismatch'
   reports[part][name]=dict(raw=raw_metrics,projected=projected_metrics);all_rows+=rows;all_raw+=raw;all_projected+=projected
  reports['combined'][name]=dict(raw=evaluate_predictions(all_rows,all_raw),projected=evaluate_predictions(all_rows,all_projected));write(BASE/(name+'.json'),{p:reports[p][name] for p in reports});print(json.dumps(dict(method=name,raw_position=reports['combined'][name]['raw']['aggregate']['position'],projected_position=reports['combined'][name]['projected']['aggregate']['position'])),flush=True)
 comparisons={}
 for part,methods in reports.items():
  comparisons[part]={}
  for model in plan['models']:
   name=model['name'];comparisons[part][name]={}
   for metric in ('position','rotation','velocity','acceleration'):
    comparisons[part][name][metric]={stage:methods[name][stage]['aggregate'][metric]/max(min(methods['projected_'+b][stage]['aggregate'][metric] for b in ('linear','hermite','shape')),1e-12) for stage in ('raw','projected')}
 assert all(not (TR/'cache'/(n+'.bvh')).exists() for n in read(TR/'temporal_expansion_plan_v19.json')['planned_splits']['confirmation'])
 for name,h in plan['sources'].items():assert sha(TR/name)==h
 result=dict(complete=True,window_count=768,raw_and_projected=reports,ratios_to_stage_best_control=comparisons,stored_projection_metrics_reproduced=True,raw_metrics_are_not_qualification=True,models_unchanged=True,retraining=False,confirmation_read=False,full_goal_complete=False,seconds=time.perf_counter()-started,plan_sha256=sha(BASE/'plan.json'));write(BASE/'report.json',result);print(json.dumps(dict(complete=True,combined=comparisons['combined'])),flush=True)
if __name__=='__main__':main()
