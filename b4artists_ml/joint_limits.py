"""Rest-local swing/twist limits, independent of bpy and rig naming.
SPDX-License-Identifier: GPL-2.0-or-later

Quaternion order is wxyz. Local Y is the bone's longitudinal rest axis.
These are artist-defined control limits, not a clinical anatomical model.
"""
import math
import numpy as np


PRESET_ID = 'CONSERVATIVE_HUMANOID_V1'
PRESET_LABEL = 'Conservative Humanoid v1'
PRESET_PROVENANCE = 'B4ML preset v1'

# Broad animation-safe starting ranges in degrees. They are deliberately
# conservative defaults for supported semantic roles, not clinical anatomy.
_PRESET_DEGREES = {
    'hips': (90, -45, 45),
    'spine': (90, -35, 35),
    'chest': (90, -40, 40),
    'neck': (90, -55, 55),
    'head': (100, -70, 70),
    'clavicle': (90, -30, 30),
    'upperarm': (125, -95, 95),
    'forearm': (155, -25, 25),
    'hand': (80, -65, 65),
    'thigh': (110, -55, 55),
    'shin': (155, -25, 25),
    'foot': (65, -45, 45),
}


def semantic_group(role):
    """Map one canonical adapter role to a preset group, or return None."""
    if not isinstance(role, str):
        return None
    base = role.split('.', 1)[0]
    if base == 'spine':
        return 'spine'
    return base if base in _PRESET_DEGREES else None


def preset_values(role, joint_available, preset=PRESET_ID):
    """Return an opt-in preset row for a canonical role.

    The caller owns rig semantics. Unknown roles remain untouched rather than
    being guessed from a control name.
    """
    if preset != PRESET_ID:
        raise ValueError('Unknown joint-limit preset: ' + str(preset))
    group = semantic_group(role)
    if group is None:
        return None
    swing, twist_min, twist_max = _PRESET_DEGREES[group]
    return {
        'enabled': True,
        'space': 'JOINT' if joint_available else 'CONTROL',
        'swing': math.radians(swing),
        'twist_min': math.radians(twist_min),
        'twist_max': math.radians(twist_max),
        'use_bend_plane': False,
        'provenance': PRESET_PROVENANCE,
        'preset': PRESET_ID,
        'semantic_role': role,
    }


def validate(request, writable):
    if request is None:return {}
    if not isinstance(request,dict):raise ValueError('Expected joint limit dictionary')
    result={}
    for name,values in request.items():
        if name not in writable:raise ValueError(f'Joint limit is not on a writable body control: {name}')
        if not isinstance(values,dict) or set(values)-{'space','bend'}!={'swing','twist_min','twist_max'}:
            raise ValueError(f'Invalid joint limit fields: {name}')
        space=values.get('space','CONTROL')
        if space not in ('CONTROL','JOINT'):raise ValueError(f'Unknown limit measurement space: {name}')
        a=np.array([values[k] for k in ('swing','twist_min','twist_max')],dtype=float)
        # RNA FloatProperty stores float32, including its +/-pi endpoints.
        epsilon=2e-7
        if not np.isfinite(a).all() or not (-epsilon<=a[0]<=math.pi+epsilon and -math.pi-epsilon<=a[1]<=a[2]<=math.pi+epsilon):
            raise ValueError(f'Invalid joint limit range: {name}')
        a[0]=np.clip(a[0],0.,math.pi);a[1:]=np.clip(a[1:],-math.pi,math.pi)
        if a[0]>math.pi-1e-5 and (a[1]>-math.pi or a[2]<math.pi):
            raise ValueError(f'Swing must be below 180 degrees when twist is limited: {name}')
        result[name]=dict(zip(('swing','twist_min','twist_max'),map(float,a)))
        if 'bend' in values:
            bend=values['bend']
            if not isinstance(bend,dict) or set(bend)!={'axis','minimum','maximum','sideways'}:
                raise ValueError(f'Invalid bend-plane fields: {name}')
            b=np.array([bend[k] for k in ('axis','minimum','maximum','sideways')],dtype=float)
            if b.shape!=(4,) or not np.isfinite(b).all() or not (-math.pi-epsilon<=b[0]<=math.pi+epsilon and -math.pi-epsilon<=b[1]<=b[2]<=math.pi+epsilon and -epsilon<=b[3]<=math.pi+epsilon):
                raise ValueError(f'Invalid bend-plane range: {name}')
            if a[0]>math.pi-1e-5:raise ValueError(f'Swing must be below 180 degrees for a bend plane: {name}')
            b[:3]=np.clip(b[:3],-math.pi,math.pi);b[3]=np.clip(b[3],0.,math.pi)
            result[name]['bend']=dict(zip(('axis','minimum','maximum','sideways'),map(float,b)))
        if space=='JOINT':result[name]['space']=space
    return result


def angles(quaternion):
    q=np.asarray(quaternion,dtype=float)
    if q.shape!=(4,) or not np.isfinite(q).all() or abs(float(np.linalg.norm(q))-1)>1e-4:
        raise ValueError('Expected finite unit joint quaternion')
    w,x,y,z=q
    longitudinal=math.hypot(w,y)
    swing=2*math.atan2(math.hypot(x,z),longitudinal)
    # Twist is undefined at a 180-degree swing. Such a pose is outside every
    # validated request that restricts twist, regardless of this chosen zero.
    twist=0. if longitudinal<1e-12 else (2*math.atan2(y,w)+math.pi)%(2*math.pi)-math.pi
    return swing,twist


def swing_vector(quaternion):
    """Log of the Y-twist-free swing, expressed along rest-local X and Z.

    At a reversed Y axis the twist/swing split is ambiguous, so calibration
    rejects that case. Residual evaluation supplies a finite rejection penalty.
    """
    angle,_=angles(quaternion)
    w,x,y,z=map(float,quaternion);longitudinal=math.hypot(w,y)
    if longitudinal<1e-7:raise ValueError('Bend direction is undefined at a reversed joint axis')
    transverse=math.hypot(x,z)
    if transverse<1e-12:return np.zeros(2)
    return np.array((x*w+z*y,z*w-x*y))*(angle/(longitudinal*transverse))


def bend_coordinates(quaternion,axis):
    v=swing_vector(quaternion);c=math.cos(axis);s=math.sin(axis)
    return np.array((v[0]*c+v[1]*s,-v[0]*s+v[1]*c))


def residual(quaternion,limit):
    swing,twist=angles(quaternion)
    correction=0.
    if not limit['twist_min']<=twist<=limit['twist_max']:
        # Signed shortest rotation to the allowed interval on the circle.
        # -pi and +pi denote the same rotation, including asymmetric intervals.
        candidates=[(twist-edge+math.pi)%(2*math.pi)-math.pi for edge in (limit['twist_min'],limit['twist_max'])]
        correction=min(candidates,key=abs)
    excess=max(0.,swing-limit['swing'])
    constrained_twist=limit['twist_min']>-math.pi or limit['twist_max']<math.pi
    singular=math.hypot(float(quaternion[0]),float(quaternion[2]))<1e-7
    if singular and (constrained_twist or 'bend' in limit):excess=max(excess,.01)
    result=[excess,correction]
    if 'bend' in limit:
        bend=limit['bend']
        if singular:result.extend((0.,0.))
        else:
            forward,side=bend_coordinates(quaternion,bend['axis'])
            result.extend((forward-float(np.clip(forward,bend['minimum'],bend['maximum'])),math.copysign(max(0.,abs(side)-bend['sideways']),side)))
    return np.asarray(result)
