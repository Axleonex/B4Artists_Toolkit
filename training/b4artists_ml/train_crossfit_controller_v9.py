"""Frozen, grouped cross-fit experiment; no data acquisition or promotion."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
from pathlib import Path
import argparse,json,time,hashlib,copy
import numpy as np
from sequence_data import load_windows
from temporal_data import validate_manifests
from sequence_model import acceptance
from temporal_model import selection
from kernel_motion import prepare as prepare_base,kernel_trials,save_model,load_model
from context_gate import base_locals,evaluate_gate
from crossfit_controller import grouped_folds,prepare,evaluate_controller
ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='crossfit_controller_v9');args=parser.parse_args()
    if not args.output.replace('_','').isalnum():raise ValueError('Simple unique output label required')
    out=ROOT/'results'/args.output;out.mkdir(exist_ok=False);tick=time.perf_counter()
    protocol=json.loads((ROOT/'crossfit_controller_protocol_v9.json').read_text())
    for name,h in protocol['source_manifests'].items():assert sha(ROOT/name)==h
    save(out/'protocol.json',protocol)
    prior=json.loads((ROOT/'results/training_manifest_v4.json').read_text())
    extra=json.loads((ROOT/'temporal_expansion_manifest_v8.json').read_text())
    manifest=dict(files=prior['files']+[r for r in extra['files'] if r['split']!='confirmation'])
    validate_manifests([manifest]);save(out/'manifest.json',manifest)
    train,sk=load_windows(ROOT,manifest,'train',protocol);val,vsk=load_windows(ROOT,manifest,'validation',protocol);assert sk==vsk
    oldids={r['clip'] for r in prior['files'] if r['split']=='validation'}
    oldidx=[i for i,w in enumerate(val) if w['clip'] in oldids];oldval=[val[i] for i in oldidx]
    oldreport=json.loads((ROOT/'results/motion_expansion_v8/report.json').read_text())
    base_path=ROOT/'results/motion_expansion_v8/expanded_base.npz';base=load_model(base_path)
    gate8=load_model(ROOT/'results/motion_expansion_v8/expanded_gate.npz')
    valbase=base_locals(base,val);oldvalbase=[valbase[i] for i in oldidx]
    reference=evaluate_gate(gate8,val,valbase,sk)
    assert reference==oldreport['validation']['mlp'],'Incumbent evidence changed'
    old_reference=oldreport['expanded_candidate_old_validation']['v6_reference']
    oof=[None]*len(train);folds=[]
    for fold,(fitidx,heldidx) in enumerate(grouped_folds(train,protocol['crossfit_folds'])):
        fit=[train[i] for i in fitidx];held=[train[i] for i in heldidx]
        fitgroups={w['clip'].split('_')[0] for w in fit};heldgroups={w['clip'].split('_')[0] for w in held}
        assert not fitgroups&heldgroups
        z,weight,mean,std,target=prepare_base(fit,'raw_pose')
        _,alpha=next(kernel_trials(z,weight,target,.25,[10.]))
        model=dict(kind='kernel',variant='raw_pose',mean=mean,std=std,centers=z,width=.25,alpha=alpha)
        predictions=base_locals(model,held)
        for i,pred in zip(heldidx,predictions,strict=True):
            assert oof[i] is None;oof[i]=pred
        record=dict(fold=fold,fit_clips=sorted({w['clip'] for w in fit}),held_clips=sorted({w['clip'] for w in held}),fit_groups=sorted(fitgroups),held_groups=sorted(heldgroups),training_windows=len(fit),held_windows=len(held),prediction_sha256=hashlib.sha256(b''.join(v.astype('<f8').tobytes() for v in predictions)).hexdigest())
        folds.append(record);save(out/'folds.json',folds)
        print(json.dumps(dict(event='fold_complete',fold=fold,training=len(fit),held=len(held),seconds=time.perf_counter()-tick)),flush=True)
    assert all(p is not None for p in oof)
    # These predictions carry training labels only through each excluded-fold fit.
    # The deployed base remains V8 trained on all and only training clips.
    best_score=selection(reference);selected=None;best_candidate=float('inf');trials=[];chosen=reference
    for variant in protocol['feature_variants']:
        z,weight,mean,std,target=prepare(train,oof,variant)
        for width in protocol['kernel_widths']:
            for reg,alpha in kernel_trials(z,weight,target,width,protocol['kernel_regularization']):
                model=dict(kind='simplex_controller_v1',variant=variant,mean=mean,std=std,centers=z,width=width,alpha=alpha,control_sha256=sha(base_path))
                report=evaluate_controller(model,val,valbase,sk);old=evaluate_controller(model,oldval,oldvalbase,sk)
                score=selection(report);protect=all(old['aggregate'][k]<=old_reference['aggregate'][k]*1.02 for k in ('position','rotation'))
                identifier=f'{variant}_{width}_{reg}';record=dict(id=identifier,score=score,old_validation_protection=protect,aggregate=report['aggregate']);trials.append(record)
                if score<best_candidate:
                    best_candidate=score;save_model(out/'best_candidate.npz',model);save(out/'best_candidate_validation.json',report)
                if score<best_score and protect:
                    best_score=score;selected=identifier;chosen=report;save_model(out/'selected_gate.npz',model)
                print(json.dumps(dict(event='trial',id=identifier,score=score,protect=protect)),flush=True)
    frozen=dict(selected=selected or 'v8_control',new_model_selected=selected is not None,base_sha256=sha(base_path),gate_sha256=sha(out/'selected_gate.npz') if selected else sha(ROOT/'results/motion_expansion_v8/expanded_gate.npz'),folds_sha256=sha(out/'folds.json'),protocol_sha256=sha(ROOT/'crossfit_controller_protocol_v9.json'),source_sha256={p.name:sha(p) for p in ROOT.glob('*.py')},confirmation_is_fresh=False)
    save(out/'selection.json',frozen)
    # V8 confirmation is now observed diagnostic data; never use it for selection.
    validation=copy.deepcopy(oldreport['validation']);validation['mlp']=chosen
    confirmation_rows=[r for r in extra['files'] if r['split']=='confirmation']
    validate_manifests([manifest,dict(files=confirmation_rows)])
    dev,dsk=load_windows(ROOT,dict(files=confirmation_rows),'confirmation',protocol);assert dsk==sk
    development=copy.deepcopy(oldreport['confirmation'])
    if selected:
        model=load_model(out/'selected_gate.npz');assert evaluate_controller(model,val,valbase,sk)==chosen
        development['mlp']=evaluate_controller(model,dev,base_locals(base,dev),sk)
    gates=dict(validation=acceptance(validation,protocol),observed_v8_confirmation=acceptance(development,protocol))
    result=dict(status='research_only',selection=frozen,validation=validation,observed_v8_confirmation=development,gates=gates,candidates=trials,folds=folds,windows=dict(train=len(train),validation=len(val),observed_confirmation=len(dev)),seconds=time.perf_counter()-tick,full_goal_complete=False,limits=['No fresh confirmation in this experiment','No actual-rig temporal application','Catalog groups do not prove actor independence','Model is never auto-promoted into the add-on'])
    save(out/'report.json',result)
    print(json.dumps(dict(event='complete',selected=frozen['selected'],gates=gates,seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
