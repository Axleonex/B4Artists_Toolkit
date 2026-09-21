"""Direction-conditioned temporal learner; trained capabilities stay explicit."""
import numpy as np
from environment_data import gravity_features
from motion_coverage import fit_feature_normalization
from sequence_model import statistics
from kernel_motion import training_targets,infer_coefficients as infer_base,kernel_trials
from sequence_data import semantic_output
from sequence_kinematics import forward
from motion_coverage import evaluate_predictions

SCHEMA='raw_pose_gravity_direction_v1'


def prepare(windows,importance):
    if not np.isfinite(importance) or importance<=0:raise ValueError('Positive gravity feature importance required')
    x=gravity_features(windows);_,weight,_,_=statistics(windows);mean,std=fit_feature_normalization(x,weight)
    std[-4:]/=importance
    return (x-mean)/std,weight,mean,std,training_targets(windows)


def fit(windows,importance,base_width,regularization):
    z,weight,mean,std,target=prepare(windows,importance);width=base_width*np.sqrt(637/z.shape[1])
    _,alpha=next(kernel_trials(z,weight,target,width,[regularization]))
    return dict(kind='kernel',variant='raw_pose',feature_schema=SCHEMA,gravity_importance=importance,mean=mean,std=std,centers=z,width=width,alpha=alpha)


def infer_coefficients(model,windows):
    schema=str(model.get('feature_schema',''))
    if not schema:return infer_base(model,windows)
    if schema!=SCHEMA:raise ValueError('Unsupported environmental model schema')
    x=gravity_features(windows)
    return infer_base(model,[dict(x=row) for row in x])


def evaluate_model(model,windows,skeleton):
    coefficients=infer_coefficients(model,windows);predictions=[];edge=0.
    for w,c in zip(windows,coefficients,strict=True):
        local=w['baseline']+w['basis_functions']@c;p,_,_=forward(local,w['offsets'],skeleton[1])
        lengths=np.linalg.norm(p[:,1:]-p[:,np.asarray(skeleton[1][1:])],axis=-1)
        edge=max(edge,float(abs(lengths-np.linalg.norm(w['offsets'][1:],axis=-1)).max()))
        predictions.append(semantic_output(local,w['offsets'],skeleton))
    report=evaluate_predictions(windows,predictions);report['aggregate']['true_edge_length_max']=edge
    return report
