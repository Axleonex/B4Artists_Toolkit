"""Known-anchor full-ancestry projection for shared semantic temporal proposals.
SPDX-License-Identifier: GPL-2.0-or-later
No hidden target array is read by projection. Numerical fit is not learned motion.
"""
import numpy as np
from sequence_kinematics import forward,backward
from temporal_data import rotation6,rotation_matrix
from semantic_motion_data import load_windows as semantic_windows
from sequence_data import load_windows as ancestor_windows


def load_windows(root,manifest,split,protocol):
    rows=semantic_windows(root,manifest,split,protocol);old,skeleton=ancestor_windows(root,manifest,split,protocol)
    for a,b in zip(rows,old,strict=True):
        if (a['clip'],a['gap'],a['context'])!=(b['clip'],b['gap'],b['context']) or not np.array_equal(a['frame'],b['frame']):
            raise ValueError('Shared and ancestor window identities differ')
        # This baseline is computed from four KNOWN ancestor poses; target_local
        # and hidden labels never enter the projection initializer.
        a['projection_initial']=b['baseline'].copy();a['offsets']=b['offsets'].copy()
    return rows,skeleton


def project(initial,offsets,parents,semantic,points,rotations,endpoints,*,steps=48,learning_rate=.02,rotation_weight=.5,regularization=1e-5):
    """Batched per-frame geometric fitting, exact root and leaf orientations.

    Semantic positions and rotations use the same normalized world frame as FK.
    Physical offsets are fixed. All priority local transforms use known values.
    """
    initial=np.array(initial,dtype=float,copy=True);points=np.array(points,dtype=float,copy=True);rotations=np.array(rotations,dtype=float,copy=True)
    if initial.ndim!=2 or points.shape!=(len(initial),17,3) or rotations.shape!=(len(initial),17,3,3):raise ValueError('Invalid projection dimensions')
    if not np.isfinite(initial).all() or not np.isfinite(points).all() or not np.isfinite(rotations).all():raise ValueError('Nonfinite projection input')
    if np.max(abs(np.swapaxes(rotations,-1,-2)@rotations-np.eye(3)))>2e-5 or np.min(np.linalg.det(rotations))<.99998:raise ValueError('Invalid proposal orientations')
    if type(steps)!=int or not 1<=steps<=256 or not np.isfinite([learning_rate,rotation_weight,regularization]).all() or not 0<learning_rate<=.1 or min(rotation_weight,regularization)<0:raise ValueError('Invalid projection budget')
    endpoints=np.asarray(endpoints)
    if endpoints.shape!=(len(initial),) or endpoints.dtype.kind!='b':raise ValueError('Explicit endpoint mask required')
    semantic=tuple(semantic);parents=tuple(parents)
    if len(semantic)!=17 or len(set(semantic))!=17 or semantic[0]!=0:raise ValueError('Invalid semantic mapping')
    p0,r0,_=forward(initial,offsets,parents)
    hard=[semantic[j] for j in (4,7,10,13,16)]
    if any(j in parents for j in hard):raise ValueError('Expected actual terminal head/hand/foot joints')
    points[endpoints]=p0[endpoints][:,semantic];rotations[endpoints]=r0[endpoints][:,semantic]
    def fixed(v):
        v=v.copy();v[:,:3]=points[:,0];v[:,3:9]=rotation6(rotations[:,0]);v[endpoints]=initial[endpoints]
        _,world,_=forward(v,offsets,parents)
        for semantic_id,joint in zip((4,7,10,13,16),hard):
            local=np.swapaxes(world[:,parents[joint]],-1,-2)@rotations[:,semantic_id]
            v[:,3+6*joint:9+6*joint]=rotation6(local)
        v[endpoints]=initial[endpoints]
        return v
    def objective(v,gradient=True):
        pos,rot,cache=forward(v,offsets,parents);pe=pos[:,semantic]-points;re=rot[:,semantic]-rotations
        change=v-initial;change[:,:9]=0.
        for j in hard:change[:,3+6*j:9+6*j]=0.
        score=.5*np.sum(pe**2,axis=(1,2))+.5*rotation_weight*np.sum(re**2,axis=(1,2,3))+.5*regularization*np.sum(change**2,axis=1)
        if not gradient:return score
        gp=np.zeros_like(pos);gr=np.zeros_like(rot);gp[:,semantic]=pe;gr[:,semantic]=rotation_weight*re
        grad=backward(gp,gr,cache)+regularization*change;grad[:,:9]=0.
        for j in hard:grad[:,3+6*j:9+6*j]=0.
        grad[endpoints]=0.
        return score,grad
    v=fixed(initial);best=v.copy();best_score,_=objective(v);m=np.zeros_like(v);second=np.zeros_like(v)
    for step in range(1,steps+1):
        score,grad=objective(v);better=score<best_score;best[better]=v[better];best_score=np.minimum(best_score,score)
        m=.9*m+.1*grad;second=.999*second+.001*grad*grad
        update=learning_rate*(m/(1-.9**step))/(np.sqrt(second/(1-.999**step))+1e-8)
        # Projected Adam directions can overshoot tiny animator corrections.
        # Bound backtracking independently per frame and retain only descent.
        wrong=np.sum(grad*update,axis=1)<=0
        update[wrong]=learning_rate*grad[wrong]
        accepted=np.zeros(len(v),dtype=bool);next_v=v.copy()
        for attempt in range(8):
            trial=fixed(v-update*(.25**attempt));candidate=objective(trial,False)
            take=(candidate<=score)&~accepted
            next_v[take]=trial[take];accepted|=take
            if accepted.all():break
        v=next_v
    score,_=objective(v);better=score<best_score;best[better]=v[better];best_score=np.minimum(best_score,score)
    best=fixed(best);pos,rot,_=forward(best,offsets,parents)
    offsets=np.broadcast_to(offsets,pos.shape);edges=np.linalg.norm(pos[:,1:]-pos[:,np.asarray(parents[1:])],axis=-1)
    edge_error=float(np.max(abs(edges-np.linalg.norm(offsets[:,1:],axis=-1))))
    return pos[:,semantic],rot[:,semantic],dict(true_edge_length_max=edge_error,position_fit_error=float(np.mean(np.linalg.norm(pos[:,semantic]-points,axis=-1))),objective=float(np.mean(best_score)),steps=steps)


def project_windows(windows,predictions,skeleton,protocol):
    """Only static offsets, known initializers and calibration enter projection."""
    if len(windows)!=len(predictions) or not windows:raise ValueError('Matching nonempty predictions required')
    output=[];edge=0.;fitting=[]
    for start in range(0,len(windows),16):
        rows=windows[start:start+16];preds=predictions[start:start+16];counts=[len(w['t']) for w in rows]
        values=np.concatenate(preds).reshape(-1,17,9);rot,bad=rotation_matrix(values[...,3:])
        if bad.any():raise ValueError('Degenerate predicted orientation')
        alignment=np.concatenate([np.broadcast_to(w['observations'].rest_alignment,(n,17,3,3)) for w,n in zip(rows,counts)])
        ends=np.concatenate([(w['t']==0)|(w['t']==1) for w in rows])
        offsets=np.concatenate([np.broadcast_to(w['offsets'],(n,)+w['offsets'].shape) for w,n in zip(rows,counts)])
        pos,world,metrics=project(np.concatenate([w['projection_initial'] for w in rows]),offsets,skeleton[1],skeleton[2],values[...,:3],rot@alignment,ends,**protocol)
        calibrated=world@np.swapaxes(alignment,-1,-2)
        packed=np.concatenate((pos,rotation6(calibrated)),axis=-1).reshape(-1,153)
        output.extend(np.split(packed,np.cumsum(counts)[:-1]));edge=max(edge,metrics['true_edge_length_max']);fitting.append(metrics['position_fit_error'])
    return output,dict(true_edge_length_max=edge,position_fit_error=float(np.mean(fitting)))
