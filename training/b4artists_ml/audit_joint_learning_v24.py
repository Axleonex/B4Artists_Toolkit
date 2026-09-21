"""Check that both learned readouts and input-conditioned joint weights are active."""
from pathlib import Path
import json,hashlib
import numpy as np
import joint_mixture_v24 as predictor
ROOT=Path(__file__).resolve().parent

def main():
 folder=ROOT/'results/joint_mixture_v24';model=predictor.load(folder/'best_learned.npz');report=json.loads((folder/'report.json').read_text());rows=json.loads((folder/'expert_strengths.json').read_text())['rows'];readout=model['w1'].reshape(model['w1'].shape[0],17,7)
 position=np.array([r['position_strengths'] for r in rows]);rotation=np.array([r['rotation_strengths'] for r in rows]);pchange=np.linalg.norm(readout[...,:4],axis=(0,2));rchange=np.linalg.norm(readout[...,4:],axis=(0,2))
 assert np.all(pchange>0) and np.all(rchange>0)
 # Readout started exactly zero; L2 shrinkage alone cannot produce these nonzero weights.
 pvariation=np.std(position,axis=0).max(axis=-1);rvariation=np.std(rotation,axis=0).max(axis=-1)
 assert np.all(pvariation>0) and np.all(rvariation>0)
 assert report['training_diagnostic']['hidden_feature_change']>0
 result=dict(passed=True,scope='Evidence of supervised nonzero position/rotation readouts and observation-dependent strengths, not generalization or quality qualification',position_readout_norm_by_joint=pchange.tolist(),rotation_readout_norm_by_joint=rchange.tolist(),position_strength_std_by_joint=pvariation.tolist(),rotation_strength_std_by_joint=rvariation.tolist(),hidden_feature_change=report['training_diagnostic']['hidden_feature_change'],model_sha256=hashlib.sha256((folder/'best_learned.npz').read_bytes()).hexdigest(),report_sha256=hashlib.sha256((folder/'report.json').read_bytes()).hexdigest(),source_sha256={Path(__file__).name:hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
 out=ROOT/'results/joint-learning-audit-v24.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,joints=17,position_readout_min=float(pchange.min()),rotation_readout_min=float(rchange.min()),position_variation_min=float(pvariation.min()),rotation_variation_min=float(rvariation.min()))))
if __name__=='__main__':main()
