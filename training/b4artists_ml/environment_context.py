"""Explicit world physics context, normalized only by known anchor frames.
SPDX-License-Identifier: GPL-2.0-or-later
"""
from dataclasses import dataclass
import numpy as np


def vector(value,name):
    a=np.asarray(value,dtype=float)
    if a.shape!=(3,) or not np.isfinite(a).all():raise ValueError(name+' must be a finite 3-vector')
    return a


def unit(value,name):
    a=vector(value,name);length=np.linalg.norm(a)
    if length<1e-12:raise ValueError(name+' must have a direction')
    return a/length


@dataclass(frozen=True)
class SupportPlane:
    point: tuple
    normal: tuple

    def __post_init__(self):
        object.__setattr__(self,'point',tuple(vector(self.point,'Plane point')))
        object.__setattr__(self,'normal',tuple(unit(self.normal,'Plane normal')))


@dataclass(frozen=True)
class Environment:
    # Acceleration is in the same internal world length units / second squared as poses.
    acceleration: tuple | None = None
    direction_hint: tuple | None = None
    support: SupportPlane | None = None

    def __post_init__(self):
        if self.acceleration is not None and self.direction_hint is not None:raise ValueError('Supply acceleration or direction-only gravity, not both')
        if self.acceleration is not None:object.__setattr__(self,'acceleration',tuple(vector(self.acceleration,'Gravity acceleration')))
        if self.direction_hint is not None:object.__setattr__(self,'direction_hint',tuple(unit(self.direction_hint,'Gravity hint')))
        if self.support is not None and not isinstance(self.support,SupportPlane):raise ValueError('Explicit SupportPlane required')


def encode_environment(environment,origin,basis,length_scale,duration):
    """11 values: down3, g*T^2/L, direction-known, acceleration-known, plane-normal3, signed-height/L, plane-known."""
    if not isinstance(environment,Environment):raise ValueError('Explicit Environment required')
    origin=vector(origin,'Anchor origin');basis=np.asarray(basis,dtype=float)
    if basis.shape!=(3,3) or not np.isfinite(basis).all() or not np.allclose(basis.T@basis,np.eye(3),atol=1e-7,rtol=0) or np.linalg.det(basis)<0:raise ValueError('Anchor basis must be a proper orthonormal rotation')
    if not np.isfinite([length_scale,duration]).all() or min(length_scale,duration)<=0:raise ValueError('Positive finite scale and duration required')
    result=np.zeros(11)
    if environment.acceleration is not None:
        acceleration=np.asarray(environment.acceleration);strength=np.linalg.norm(acceleration);result[5]=1
        if strength>1e-12:result[:3]=basis.T@(acceleration/strength);result[4]=1
        result[3]=strength*duration**2/length_scale
    elif environment.direction_hint is not None:
        result[:3]=basis.T@environment.direction_hint;result[4]=1
    if environment.support is not None:
        normal=np.asarray(environment.support.normal);result[6:9]=basis.T@normal
        result[9]=np.dot(origin-environment.support.point,normal)/length_scale;result[10]=1
    if not np.isfinite(result).all():raise ValueError('Physical context overflows normalized units')
    return result


def from_scene(scene,support=None):
    """Read raw scene acceleration; display unit scale is not a second physical conversion."""
    acceleration=tuple(scene.gravity) if scene.use_gravity else (0.,0.,0.)
    return Environment(acceleration=acceleration,support=support)


def timeline_seconds(scene,start,end):
    fps=float(scene.render.fps);base=float(scene.render.fps_base)
    if not np.isfinite([fps,base,start,end]).all() or min(fps,base)<=0 or end<=start:raise ValueError('Positive frame interval and frame rate required')
    return (end-start)*base/fps


def free_flight_points(start,end,t,duration,environment):
    """Constant-acceleration free point/COM path; not automatically a pelvis trajectory or collision solver."""
    start=vector(start,'Flight start');end=vector(end,'Flight end');t=np.asarray(t,dtype=float)
    if t.ndim!=1 or not np.isfinite(t).all() or np.any((t<0)|(t>1)) or not np.isfinite(duration) or duration<=0:raise ValueError('Valid flight times required')
    if not isinstance(environment,Environment) or environment.acceleration is None:raise ValueError('Flight requires known acceleration magnitude, including explicit zero')
    g=np.asarray(environment.acceleration);u=t[:,None]
    result=start*(1-u)+end*u+.5*g*duration**2*(u*u-u)
    if not np.isfinite(result).all():raise ValueError('Flight output overflows')
    return result
