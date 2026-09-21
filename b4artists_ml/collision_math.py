"""Host-independent finite-segment clearance against an authored plane.

The first collision model deliberately has a narrow contract: each mass segment
is a solid ellipsoid, the allowed region is the positive side of one plane, and
the response is a whole-character translation along that plane's normal.
"""
import math
import numpy as np


def plane(point, normal):
    point=np.asarray(point,dtype=float);normal=np.asarray(normal,dtype=float)
    if point.shape!=(3,) or normal.shape!=(3,) or not np.isfinite(point).all() or not np.isfinite(normal).all():
        raise ValueError('Collision plane must contain finite 3D vectors')
    length=float(np.linalg.norm(normal))
    if length<1e-8:raise ValueError('Collision plane normal must be nonzero')
    return point,normal/length


def segment_separations(centers,orientations,lengths,radius_ratios,point,normal,inside=None):
    """Return signed ellipsoid-to-plane clearance for one displayed pose.

    ``orientations`` contains proper world-space frames whose columns are the
    local ellipsoid axes. The local Y semi-axis is half the segment length; X/Z
    use the animator's radius ratio.
    """
    centers=np.asarray(centers,dtype=float);orientations=np.asarray(orientations,dtype=float)
    lengths=np.asarray(lengths,dtype=float);radii=np.asarray(radius_ratios,dtype=float)
    point,normal=plane(point,normal)
    count=len(lengths) if lengths.ndim==1 else -1
    if centers.shape!=(count,3) or orientations.shape!=(count,3,3) or radii.shape!=(count,):
        raise ValueError('Collision segment arrays must describe the same one-dimensional segment set')
    if count<1 or not all(np.isfinite(value).all() for value in (centers,orientations,lengths,radii)):
        raise ValueError('Collision segment geometry must be finite and nonempty')
    if np.any(lengths<=1e-8) or np.any(radii<=0):raise ValueError('Collision segment lengths and radii must be positive')
    determinants=np.linalg.det(orientations)
    orthogonality=np.einsum('nji,njk->nik',orientations,orientations)
    if np.max(np.abs(orthogonality-np.eye(3)))>1e-5 or np.max(np.abs(determinants-1.))>1e-5:
        raise ValueError('Collision segment orientations must be proper orthonormal frames')
    local_normal=np.einsum('nji,j->ni',orientations,normal)
    transverse=lengths*radii
    semi_axes=np.column_stack((transverse,.5*lengths,transverse))
    extent=np.sqrt(np.sum((local_normal*semi_axes)**2,axis=1))
    result=(centers-point)@normal-extent
    if inside is not None:
        inside=np.asarray(inside,dtype=bool)
        if inside.shape!=(count,):raise ValueError('Collision surface mask must match the segment count')
        result=np.where(inside,result,np.inf)
    return result


def correction(centers,orientations,lengths,radius_ratios,point,normal,clearance=0.,strength=1.,inside=None):
    """Compute the bounded translational response and inspectable metrics."""
    if not isinstance(clearance,(int,float)) or not math.isfinite(clearance) or clearance<0:
        raise ValueError('Collision clearance must be finite and nonnegative')
    if not isinstance(strength,(int,float)) or not math.isfinite(strength) or not 0<=strength<=1:
        raise ValueError('Collision strength must lie between zero and one')
    _,unit=plane(point,normal)
    separations=segment_separations(centers,orientations,lengths,radius_ratios,point,unit,inside)
    finite=np.isfinite(separations)
    required=float(max(0.,np.max(clearance-separations[finite]))) if finite.any() else 0.
    applied=required*strength
    remaining=max(0.,required-applied)
    return dict(vector=unit*applied,required_lift=required,applied_lift=applied,
        remaining_penetration=remaining,min_separation=float(np.min(separations[finite])) if finite.any() else None,
        participating_segments=int(finite.sum()))


def contact_transition_delta(delta,normal,strength=1.):
    """Apply a bounded frictionless contact impulse to a transition delta.

    The collision normal may change velocity discontinuously at impact; its
    tangent may not. ``strength`` blends between unconstrained and fully
    inelastic normal response without inventing tangential friction.
    """
    delta=np.asarray(delta,dtype=float)
    if delta.shape!=(3,) or not np.isfinite(delta).all():
        raise ValueError('Contact transition delta must be a finite 3D vector')
    if not isinstance(strength,(int,float)) or not math.isfinite(strength) or not 0<=strength<=1:
        raise ValueError('Contact transition strength must lie between zero and one')
    _,unit=plane([0,0,0],normal)
    absorbed=unit*float(np.dot(delta,unit))*strength
    return dict(corrected=delta-absorbed,absorbed=absorbed,normal=unit)
