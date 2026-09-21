"""Constant-gravity COM targets and editable cubic curve interpolation."""
import math
import numpy as np
from .support_math import vector


def _contact_blends(row):
    shared=row.get('blend',0.)
    return row.get('blend_in',shared),row.get('blend_out',shared)


def _landing_contact_covers(row,contact,end=None):
    boundary=row['end'];required_end=boundary if end is None else end
    return (max(row.get('collision_strength',0.),row.get('contact_impulse_strength',0.))>0 and contact.get('strength',0.)>0
        and abs(contact['start']-boundary)<=1e-8 and contact['end']>=required_end-1e-8)


def trajectory(start,end,u,duration,gravity):
    a=vector(start);b=vector(end);g=vector(gravity);t=np.asarray(u,dtype=float)
    if t.ndim!=1 or not np.isfinite(t).all() or np.any((t<0)|(t>1)) or not math.isfinite(duration) or duration<=0:
        raise ValueError('Flight needs finite times in [0,1] and a positive duration')
    result=a*(1-t[:,None])+b*t[:,None]+.5*g*duration**2*(t*t-t)[:,None]
    if not np.isfinite(result).all():raise ValueError('Flight trajectory exceeds numeric range')
    return result


def endpoint_velocities(start,end,duration,gravity):
    if not math.isfinite(duration) or duration<=0:raise ValueError('Flight duration must be positive')
    average=(vector(end)-vector(start))/duration;g=vector(gravity)
    return average-.5*g*duration,average+.5*g*duration


def cubic_controls(values):
    """Bezier y handles interpolating values at u=0,1/3,2/3,1; x is linear in time."""
    v=np.asarray(values,dtype=float)
    if v.ndim<1 or v.shape[0]!=4 or not np.isfinite(v).all():raise ValueError('Expected four finite cubic samples')
    a=27*v[1]-8*v[0]-v[3];b=27*v[2]-v[0]-8*v[3]
    return (2*a-b)/18.,(2*b-a)/18.


def validate(rows,anchors,contacts):
    if not rows or len(rows)>16:raise ValueError('Author between one and sixteen flight intervals')
    result=[];known=set(anchors)
    for row in sorted(rows,key=lambda r:r['start']):
        r=dict(row)
        if not all(isinstance(r.get(k),(int,float)) and math.isfinite(r[k]) for k in ('start','end','strength')):
            raise ValueError('Flight times and strength must be finite')
        if r['start'] not in known or r['end'] not in known or r['start']>=r['end']:
            raise ValueError('Flight endpoints must be two distinct authored priority poses')
        if not 0<=r['strength']<=1:raise ValueError('Flight strength must lie between zero and one')
        angular=r.get('angular_momentum_strength',0.)
        if not isinstance(angular,(int,float)) or not math.isfinite(angular) or not 0<=angular<=1:
            raise ValueError('Angular momentum strength must lie between zero and one')
        collision=r.get('collision_strength',0.)
        impulse=r.get('contact_impulse_strength',0.)
        clearance=r.get('collision_clearance',0.)
        if not isinstance(collision,(int,float)) or not math.isfinite(collision) or not 0<=collision<=1:
            raise ValueError('Collision strength must lie between zero and one')
        if not isinstance(impulse,(int,float)) or not math.isfinite(impulse) or not 0<=impulse<=1:
            raise ValueError('Landing contact impulse strength must lie between zero and one')
        if not isinstance(clearance,(int,float)) or not math.isfinite(clearance) or clearance<0 or clearance>1:
            raise ValueError('Collision clearance must lie between zero and one body lengths')
        if result and result[-1]['end']>r['start']:raise ValueError('Flight intervals must not overlap')
        for c in contacts:
            if not all(isinstance(c.get(k),(int,float)) and math.isfinite(c[k]) for k in ('start','end','blend','strength')) or c['start']>c['end'] or c['blend']<0 or not 0<=c['strength']<=1:
                raise ValueError('Invalid contact timing or strength')
            blend_in,blend_out=_contact_blends(c)
            if not all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and 0<=v<=240 for v in (blend_in,blend_out)):
                raise ValueError('Invalid contact timing or strength')
            if (c['strength']>0 and max(r['start'],c['start']-blend_in)<min(r['end'],c['end']+blend_out)
                    and not _landing_contact_covers(r,c)):
                raise ValueError('A held/blended contact overlaps the flight interior; edit its interval first')
        result.append(r)
    return result


def transition_offset(u,duration,velocity,landing=False):
    """Zero endpoint cubic displacement; velocity is in world units/second.

    Takeoff corrects the final derivative; landing corrects the initial one.
    Neither acceleration continuity nor angular momentum is implied.
    """
    t=np.asarray(u,dtype=float);v=vector(velocity)
    if t.ndim!=1 or not np.isfinite(t).all() or np.any((t<0)|(t>1)) or not math.isfinite(duration) or duration<=0:
        raise ValueError('Transition needs finite times in [0,1] and a positive duration')
    basis=t*(1-t)**2 if landing else t*t*(t-1)
    result=basis[:,None]*duration*v
    if not np.isfinite(result).all():raise ValueError('Transition exceeds numeric range')
    return result


def transition_c2_spline(duration,velocity,acceleration,landing=False):
    """Three cubic spans with position, velocity and acceleration endpoint constraints.

    Velocity and acceleration use world units/second and world units/second squared.
    The returned Bezier handles reproduce the piecewise polynomial exactly.
    """
    if not math.isfinite(duration) or duration<=0:raise ValueError('Transition duration must be positive')
    velocity=vector(velocity);acceleration=vector(acceleration)
    knots=np.linspace(0.,1.,4);matrix=np.zeros((12,12),dtype=float);rhs=np.zeros((12,3),dtype=float);row=0
    def terms(piece,u,order):
        result=np.zeros(12,dtype=float);x=u-knots[piece]
        for power in range(order,4):
            factor=math.factorial(power)/math.factorial(power-order)
            result[piece*4+power]=factor*x**(power-order)
        return result
    for join in range(1,3):
        for order in range(3):
            matrix[row]=terms(join-1,knots[join],order)-terms(join,knots[join],order);row+=1
    start=(np.zeros(3),velocity*duration,acceleration*duration**2) if landing else (np.zeros(3),)*3
    end=(np.zeros(3),)*3 if landing else (np.zeros(3),velocity*duration,acceleration*duration**2)
    for order,value in enumerate(start):matrix[row]=terms(0,0.,order);rhs[row]=value;row+=1
    for order,value in enumerate(end):matrix[row]=terms(2,1.,order);rhs[row]=value;row+=1
    coefficients=np.linalg.solve(matrix,rhs).reshape(3,4,3)
    def evaluate(piece,u,order=0):return terms(piece,u,order).reshape(3,4)[piece]@coefficients[piece]
    values=np.array([evaluate(min(index,2),u) for index,u in enumerate(knots)])
    right=[];left=[]
    for piece in range(3):
        width=knots[piece+1]-knots[piece]
        right.append(values[piece]+evaluate(piece,knots[piece],1)*width/3)
        left.append(values[piece+1]-evaluate(piece,knots[piece+1],1)*width/3)
    if not all(np.isfinite(value).all() for value in (coefficients,values,right,left)):
        raise ValueError('Transition exceeds numeric range')
    return dict(knots=knots,values=values,right=np.asarray(right),left=np.asarray(left),coefficients=coefficients)


def transition_c2_values(spline,u):
    times=np.asarray(u,dtype=float)
    if times.ndim!=1 or not np.isfinite(times).all() or np.any((times<0)|(times>1)):
        raise ValueError('Transition needs finite times in [0,1]')
    knots=np.asarray(spline['knots'],dtype=float);coefficients=np.asarray(spline['coefficients'],dtype=float)
    if knots.shape!=(4,) or coefficients.shape!=(3,4,3) or not np.isfinite(coefficients).all():
        raise ValueError('Invalid transition spline')
    result=[]
    for value in times:
        piece=min(int(value*3),2);x=value-knots[piece]
        result.append(np.array([1.,x,x*x,x*x*x])@coefficients[piece])
    return np.asarray(result)


def transition_spans(intervals,anchors,contacts):
    """Validate explicitly requested free-motion spans before host mutation."""
    spans=[];occupied=[(r['start'],r['end']) for r in intervals]
    for index,row in enumerate(intervals):
        for key,landing in (('takeoff_blend',False),('landing_blend',True)):
            frames=row.get(key,0.)
            if not isinstance(frames,(int,float)) or not math.isfinite(frames) or frames<0:
                raise ValueError('Transition frames must be finite and nonnegative')
            if frames==0:continue
            if frames<1:raise ValueError('Use at least one transition frame')
            start=row['end'] if landing else row['start']-frames
            end=row['end']+frames if landing else row['start']
            if start<min(anchors) or end>max(anchors):raise ValueError('Transition must stay within authored pose range')
            if any(start<a<end for a in anchors):raise ValueError('Transition crosses an authored priority pose')
            if any(max(start,a)<min(end,b) for a,b in occupied):raise ValueError('Transition overlaps another flight or transition')
            if any(c['strength']>0 and max(start,c['start']-_contact_blends(c)[0])<min(end,c['end']+_contact_blends(c)[1])
                    and not (landing and _landing_contact_covers(row,c,end)) for c in contacts):
                raise ValueError('A held/blended contact overlaps the transition; edit its interval first')
            occupied.append((start,end));spans.append(dict(start=start,end=end,landing=landing,flight_index=index))
    return spans
