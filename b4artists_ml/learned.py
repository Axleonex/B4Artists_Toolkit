"""Local trained limb bend prior; constraint projection remains deterministic.

SPDX-License-Identifier: GPL-2.0-or-later
No network, downloads or inference service. NumPy is provided by Bforartists.
"""
import hashlib
import io
from importlib import resources
import numpy as np

MODEL_SHA256='59704e21ce7185697d48a62df60455aefaee8b7580f65496877d6bb39c8f073d'
_MODEL=None


def decode_model(data):
    if len(data)>100000 or hashlib.sha256(data).hexdigest()!=MODEL_SHA256:
        raise ValueError('The bundled bend model is missing or has an invalid checksum')
    shapes={'mean':(4,),'scale':(4,),'omega':(4,256),'phase':(256,),
            'coefficients':(261,3),'input_min':(4,),'input_max':(4,)}
    result={}
    with np.load(io.BytesIO(data),allow_pickle=False) as archive:
        expected={kind+'_'+key for kind in ('arm','leg') for key in shapes}
        if set(archive.files)!=expected:
            raise ValueError('Unsupported bend model contents')
        for kind in ('arm','leg'):
            row={}
            for key,shape in shapes.items():
                value=archive[kind+'_'+key]
                if value.shape!=shape or value.dtype.kind!='f' or not np.isfinite(value).all():
                    raise ValueError('Invalid bend model array: '+key)
                value.setflags(write=False);row[key]=value
            if np.any(row['scale']<=0) or np.any(row['input_min']>row['input_max']):
                raise ValueError('Invalid bend model normalization')
            result[kind]=row
    return result


def model():
    global _MODEL
    if _MODEL is None:
        try:
            data=resources.files(__package__).joinpath('models/limb_prior_v1.npz').read_bytes()
        except OSError as exc:
            raise ValueError('Reinstall the add-on to restore its bundled bend model') from exc
        _MODEL=decode_model(data)
    return _MODEL


def anatomical_basis(left_hip,right_hip,left_shoulder,right_shoulder):
    points=np.asarray([left_hip,right_hip,left_shoulder,right_shoulder],dtype=float)
    if points.shape!=(4,3) or not np.isfinite(points).all():
        raise ValueError('Invalid body landmarks for learned bending')
    origin=(points[0]+points[1])*0.5
    left=points[0]-points[1];up=(points[2]+points[3])*0.5-origin
    extent=max(np.linalg.norm(left),np.linalg.norm(up))
    if extent<1e-10 or np.linalg.norm(left)<extent*1e-5:
        raise ValueError('Hip landmarks cannot define the body frame')
    left/=np.linalg.norm(left)
    up-=left*np.dot(up,left)
    if np.linalg.norm(up)<extent*1e-5:
        raise ValueError('Shoulder landmarks cannot define the body frame')
    up/=np.linalg.norm(up)
    return np.stack((left,np.cross(up,left),up),axis=1)


def infer_features(kind,x):
    """Return raw learned plane prediction for one normalized, canonical-left limb."""
    if kind not in ('arm','leg'):
        raise ValueError('Unsupported learned limb type')
    x=np.asarray(x,dtype=float)
    if x.shape!=(4,) or not np.isfinite(x).all():
        raise ValueError('Invalid learned limb features')
    row=model()[kind]
    # A conservative range guard, not a calibrated confidence or plausibility score.
    margin=np.array([.1,.1,.1,.05])
    if np.any(x<row['input_min']-margin) or np.any(x>row['input_max']+margin):
        return None,'outside training range'
    z=(x-row['mean'])/row['scale']
    phi=np.concatenate(([1.],z,np.cos(z@row['omega']+row['phase'])*np.sqrt(2/256)))
    return phi@row['coefficients'],'learned'


def direction(kind,root,target,lengths,basis,side):
    """Return a unit bend direction in the input coordinate system, or a fallback reason."""
    root=np.asarray(root,dtype=float);target=np.asarray(target,dtype=float)
    lengths=np.asarray(lengths,dtype=float);basis=np.asarray(basis,dtype=float)
    if (root.shape!=(3,) or target.shape!=(3,) or lengths.shape!=(2,) or basis.shape!=(3,3)
            or not all(np.isfinite(v).all() for v in (root,target,lengths,basis))
            or np.any(lengths<=0) or side not in ('L','R')):
        raise ValueError('Invalid learned bend request')
    if not np.allclose(basis.T@basis,np.eye(3),atol=1e-6) or np.linalg.det(basis)<0:
        raise ValueError('Body frame must be a proper orthonormal basis')
    delta=basis.T@(target-root)/sum(lengths)
    distance=np.linalg.norm(delta)
    if distance<1e-5 or distance>1+1e-6:
        return None,'degenerate or unreachable target'
    if side=='R':
        delta[0]*=-1
    raw,reason=infer_features(kind,np.r_[delta,lengths[0]/sum(lengths)])
    if raw is None:
        return None,reason
    axis=delta/distance
    plane=raw-axis*np.dot(raw,axis)
    norm=np.linalg.norm(plane)
    if norm<1e-5:
        return None,'ambiguous bend direction'
    plane/=norm
    if side=='R':
        plane[0]*=-1
    return tuple(basis@plane),'learned'
