"""Deterministic rigid-segment angular-momentum refinement; no host mutation.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import math
import numpy as np


def _inputs(centers, weights, times):
    points=np.asarray(centers,dtype=float);mass=np.asarray(weights,dtype=float);clock=np.asarray(times,dtype=float)
    if (points.ndim!=3 or points.shape[2]!=3 or points.shape[0]<4 or points.shape[1]<3
            or mass.shape!=(points.shape[1],) or clock.shape!=(points.shape[0],)
            or not all(np.isfinite(v).all() for v in (points,mass,clock))
            or np.any(mass<0) or not np.any(mass>0) or np.any(np.diff(clock)<=0)):
        raise ValueError('Angular momentum needs finite ordered samples and nonnegative segment masses')
    mass=mass/mass.max();mass/=mass.sum()
    return points,mass,clock


def segment_orientations(starts,ends,roll_hints):
    """Build right-handed segment frames with local Y along each segment.

    The evaluated bone X axis is used only as a roll hint. Projecting it onto
    the plane normal to the measured segment keeps the inertia frame attached
    to the actual endpoints while retaining axial twist.
    """
    a=np.asarray(starts,dtype=float);b=np.asarray(ends,dtype=float);h=np.asarray(roll_hints,dtype=float)
    squeezed=a.ndim==2
    if squeezed:a=a[None,:,:];b=b[None,:,:];h=h[None,:,:]
    if (a.ndim!=3 or a.shape[2:]!=(3,) or b.shape!=a.shape or h.shape!=a.shape
            or not all(np.isfinite(v).all() for v in (a,b,h))):
        raise ValueError('Segment frames need matching finite endpoint and roll-hint samples')
    direction=b-a;length=np.linalg.norm(direction,axis=2)
    if np.any(length<1e-8):raise ValueError('Segment endpoints must have nonzero length')
    y=direction/length[:,:,None]
    x=h-y*np.sum(h*y,axis=2)[:,:,None];x_length=np.linalg.norm(x,axis=2)
    if np.any(x_length<1e-8):raise ValueError('Segment roll hint must not be parallel to its endpoints')
    x/=x_length[:,:,None];z=np.cross(x,y)
    frames=np.stack((x,y,z),axis=3)
    if not np.allclose(np.einsum('tnji,tnjk->tnik',frames,frames),np.eye(3),atol=2e-6):
        raise ValueError('Segment frame construction failed')
    return frames[0] if squeezed else frames


def segment_principal_inertia(starts,ends,radius_ratios):
    """Return per-unit-mass principal moments for solid ellipsoid segments.

    Radius is an artist-authored fraction of measured segment length. The
    result is a finite-volume approximation rather than anatomical truth.
    """
    a=np.asarray(starts,dtype=float);b=np.asarray(ends,dtype=float);ratios=np.asarray(radius_ratios,dtype=float)
    squeezed=a.ndim==2
    if squeezed:a=a[None,:,:];b=b[None,:,:]
    if (a.ndim!=3 or a.shape[2:]!=(3,) or b.shape!=a.shape or ratios.shape!=(a.shape[1],)
            or not all(np.isfinite(v).all() for v in (a,b,ratios)) or np.any((ratios<=0)|(ratios>1))):
        raise ValueError('Segment inertia needs finite endpoints and radius ratios in (0, 1]')
    length=np.linalg.norm(b-a,axis=2)
    if np.any(length<1e-8):raise ValueError('Segment endpoints must have nonzero length')
    radius=length*ratios[None,:];half=length*.5
    perpendicular=(half*half+radius*radius)/5
    axial=2*radius*radius/5
    moments=np.stack((perpendicular,axial,perpendicular),axis=2)
    return moments[0] if squeezed else moments


def rotation_matrix(value):
    """Return a proper rotation matrix for a finite exponential-coordinate vector."""
    v=np.asarray(value,dtype=float)
    if v.shape!=(3,) or not np.isfinite(v).all():raise ValueError('Rotation vector must be finite')
    angle=float(np.linalg.norm(v));x=np.array(((0.,-v[2],v[1]),(v[2],0.,-v[0]),(-v[1],v[0],0.)))
    if angle<1e-8:
        # Stable through second order, which also keeps finite-difference Jacobians smooth.
        return np.eye(3)+x+.5*x@x
    x/=angle
    return np.eye(3)+math.sin(angle)*x+(1-math.cos(angle))*(x@x)


def rotation_vector(matrix):
    """Return the principal exponential-coordinate vector of a proper rotation."""
    r=np.asarray(matrix,dtype=float)
    if r.shape!=(3,3) or not np.isfinite(r).all() or not np.allclose(r.T@r,np.eye(3),atol=2e-5) or np.linalg.det(r)<0:
        raise ValueError('Expected a finite proper rotation matrix')
    cosine=float(np.clip((np.trace(r)-1)*.5,-1.,1.));angle=math.acos(cosine)
    vector=np.array((r[2,1]-r[1,2],r[0,2]-r[2,0],r[1,0]-r[0,1]))
    if angle<1e-7:return vector*.5
    if math.pi-angle<1e-5:
        values=np.sqrt(np.maximum((np.diag(r)+1)*.5,0.));axis=values
        index=int(np.argmax(values))
        if values[index]>1e-8:
            for i in range(3):
                if i!=index:axis[i]=math.copysign(axis[i],r[i,index]+r[index,i])
        length=float(np.linalg.norm(axis))
        if length<1e-8:raise ValueError('Rotation axis is numerically undefined')
        if float(np.dot(axis,vector))<0.:axis=-axis
        return axis/length*angle
    return vector*(angle/(2*math.sin(angle)))


def _rotation_vectors(matrices):
    """Vectorized principal logs; the rare pi branch keeps the scalar guard."""
    values=np.asarray(matrices,dtype=float)
    cosine=np.clip((np.trace(values,axis1=-2,axis2=-1)-1)*.5,-1.,1.);angles=np.arccos(cosine)
    vectors=np.stack((values[...,2,1]-values[...,1,2],values[...,0,2]-values[...,2,0],values[...,1,0]-values[...,0,1]),axis=-1)
    scales=np.empty_like(angles);small=angles<1e-7;near_pi=np.pi-angles<1e-5;regular=~(small|near_pi)
    scales[small]=.5;scales[regular]=angles[regular]/(2*np.sin(angles[regular]));scales[near_pi]=0
    result=vectors*scales[...,None]
    for index in np.argwhere(near_pi):
        key=tuple(index);result[key]=rotation_vector(values[key])
    return result


def _angular_velocities(orientations,times):
    count,segments=orientations.shape[:2]
    relative=np.einsum('tnij,tnkj->tnik',orientations[1:],orientations[:-1])
    steps=_rotation_vectors(relative)/np.diff(times)[:,None,None]
    values=np.empty((count,segments,3),dtype=float);values[0]=steps[0];values[-1]=steps[-1]
    for i in range(1,count-1):
        before=times[i]-times[i-1];after=times[i+1]-times[i]
        values[i]=(steps[i-1]*after+steps[i]*before)/(before+after)
    return values


def measure(centers, weights, times, orientations=None, principal_inertia=None):
    """Measure COM-relative orbital and optional finite-segment spin momentum."""
    points,mass,clock=_inputs(centers,weights,times)
    com=np.einsum('n,tnj->tj',mass,points);relative=points-com[:,None,:]
    velocity=np.gradient(relative,clock,axis=0,edge_order=2)
    orbital=np.einsum('n,tnj->tj',mass,np.cross(relative,velocity))
    identity=np.eye(3);inertia=np.empty((len(clock),3,3),dtype=float)
    for i,row in enumerate(relative):
        inertia[i]=sum(weight*((point@point)*identity-np.outer(point,point)) for weight,point in zip(mass,row))
    spin=np.zeros_like(orbital);intrinsic=np.zeros((len(clock),len(mass),3,3),dtype=float)
    if (orientations is None)!=(principal_inertia is None):
        raise ValueError('Segment orientations and principal inertia must be supplied together')
    if orientations is not None:
        frames=np.asarray(orientations,dtype=float);moments=np.asarray(principal_inertia,dtype=float)
        if moments.shape==(len(mass),3):moments=np.broadcast_to(moments,(len(clock),len(mass),3))
        if (frames.shape!=(len(clock),len(mass),3,3) or moments.shape!=(len(clock),len(mass),3)
                or not all(np.isfinite(v).all() for v in (frames,moments)) or np.any(moments<0)
                or not np.allclose(np.einsum('tnji,tnjk->tnik',frames,frames),identity,atol=2e-5)
                or np.any(np.linalg.det(frames)<0)):
            raise ValueError('Segment inertia frames and principal moments must be finite and physical')
        intrinsic=np.einsum('tnik,tnk,tnjk,n->tnij',frames,moments,frames,mass)
        omega=_angular_velocities(frames,clock)
        spin=np.einsum('tnij,tnj->ti',intrinsic,omega)
        inertia+=intrinsic.sum(axis=1)
    else:
        frames=None;moments=None
    momentum=orbital+spin
    if not all(np.isfinite(v).all() for v in (com,relative,orbital,spin,momentum,inertia,intrinsic)):
        raise ValueError('Angular momentum measurement exceeds numeric range')
    return dict(com=com,relative=relative,inertia=inertia,momentum=momentum,orbital_momentum=orbital,
        spin_momentum=spin,intrinsic_inertia=intrinsic,orientations=frames,principal_inertia=moments,
        weights=mass,times=clock,model='rigid_segments' if frames is not None else 'point_masses')


def _integrate(momentum,inertia,times,target):
    rotations=[np.eye(3)]
    for i,duration in enumerate(np.diff(times)):
        source=(momentum[i]+momentum[i+1])*.5;body=(inertia[i]+inertia[i+1])*.5;r=rotations[-1]
        def rate(matrix):
            world_inertia=matrix@body@matrix.T
            return np.linalg.pinv(world_inertia,rcond=1e-9)@(target-matrix@source)
        first=rate(r);middle=rotation_matrix(first*duration*.5)@r;omega=rate(middle)
        rotations.append(rotation_matrix(omega*duration)@r)
    return np.asarray(rotations)


def variation(momentum):
    values=np.asarray(momentum,dtype=float);mean=values.mean(axis=0)
    if values.ndim!=2 or values.shape[1]!=3 or not len(values) or not np.isfinite(values).all():
        raise ValueError('Angular momentum samples must be finite three-dimensional vectors')
    return float(np.sqrt(np.mean(np.sum((values-mean)**2,axis=1)))),mean


def refine(centers, weights, times, strength=1., max_angle=math.radians(35), *, orientations=None, principal_inertia=None):
    """Find a source-safe rigid correction with identity endpoint poses.

    The constant world angular momentum is solved so integration returns to the
    authored landing orientation. A final bounded scale protects animator intent.
    """
    if not isinstance(strength,(int,float)) or not math.isfinite(strength) or not 0<=strength<=1:
        raise ValueError('Angular momentum strength must lie between zero and one')
    if not isinstance(max_angle,(int,float)) or not math.isfinite(max_angle) or not 0<max_angle<math.pi:
        raise ValueError('Maximum angular correction must lie between zero and pi')
    data=measure(centers,weights,times,orientations,principal_inertia);source=data['momentum'];inertia=data['inertia'];clock=data['times']
    before,target=variation(source);target=target.copy();converged=False
    scale=max(float(np.sqrt(np.mean(np.sum(source*source,axis=1)))),1e-9)
    for _ in range(10):
        rotations=_integrate(source,inertia,clock,target);residual=rotation_vector(rotations[-1])
        if np.linalg.norm(residual)<2e-6:converged=True;break
        step=max(scale*2e-5,1e-8);jacobian=np.empty((3,3))
        for axis in range(3):
            shifted=target.copy();shifted[axis]+=step
            jacobian[:,axis]=(rotation_vector(_integrate(source,inertia,clock,shifted)[-1])-residual)/step
        delta=np.linalg.lstsq(jacobian,-residual,rcond=1e-8)[0]
        if not np.isfinite(delta).all():break
        length=float(np.linalg.norm(delta));target+=delta*(min(1.,4*scale/max(length,1e-12)))
    rotations=_integrate(source,inertia,clock,target)
    # Remove the tiny integration/root residual exactly while preserving takeoff.
    end=rotation_vector(rotations[-1])
    for i,u in enumerate((clock-clock[0])/(clock[-1]-clock[0])):
        rotations[i]=rotation_matrix(-end*(u*u*(3-2*u)))@rotations[i]
    vectors=np.asarray([rotation_vector(r) for r in rotations]);peak=float(np.max(np.linalg.norm(vectors,axis=1)))
    limit=min(1.,max_angle/max(peak,1e-12));effective=float(strength)*limit
    rotations=np.asarray([rotation_matrix(v*effective) for v in vectors])
    transformed=np.einsum('tij,tnj->tni',rotations,data['relative'])+data['com'][:,None,:]
    transformed_frames=None if data['orientations'] is None else np.einsum('tij,tnjk->tnik',rotations,data['orientations'])
    after_data=measure(transformed,data['weights'],clock,transformed_frames,data['principal_inertia'])
    after_momentum=after_data['momentum'];after,after_target=variation(after_momentum)
    if before>1e-9 and after>before and strength>0:
        rotations=np.repeat(np.eye(3)[None,:,:],len(clock),axis=0);transformed=np.asarray(centers,dtype=float)
        after_data=data;after_momentum=source.copy();after=before;after_target=source.mean(axis=0);effective=0.;peak=0.
    return dict(rotations=rotations,target=after_target,before_momentum=source,after_momentum=after_momentum,
        before_orbital_momentum=data['orbital_momentum'],after_orbital_momentum=after_data['orbital_momentum'],
        before_spin_momentum=data['spin_momentum'],after_spin_momentum=after_data['spin_momentum'],model=data['model'],
        before_variation=before,after_variation=after,improvement=0. if before<=1e-12 else 1-after/before,
        peak_angle=peak*effective,effective_strength=effective,root_converged=converged,
        endpoint_error=float(np.linalg.norm(rotation_vector(rotations[-1]))))
