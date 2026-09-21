"""Artist-authored contact timing, independent of the host and learned models."""
import math
from .math_core import finite_vector,unit_quaternion


def blends(row):
    """Return effective entry/exit blend lengths with legacy fallback."""
    shared=row.get('blend',0.)
    return row.get('blend_in',shared),row.get('blend_out',shared)


def validate(rows,first,last):
    if not rows:raise ValueError('Capture at least one enabled contact')
    if len(rows)>32:raise ValueError('Limit a candidate to 32 contacts')
    result=[]
    for row in rows:
        r=dict(row)
        for key in ('start','end','blend','strength'):
            v=r[key]
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):raise ValueError('Contact timing and strength must be finite numbers')
        blend_in,blend_out=blends(r)
        if not all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in (blend_in,blend_out)):
            raise ValueError('Contact timing and strength must be finite numbers')
        if not first<=r['start']<=r['end']<=last or not 0<=r['blend']<=240 or not 0<=blend_in<=240 or not 0<=blend_out<=240 or not 0<r['strength']<=1:raise ValueError('Contact interval must lie inside the candidate, with positive strength')
        r['blend_in']=blend_in;r['blend_out']=blend_out
        if r['limb'] not in ('arm-L','arm-R','leg-L','leg-R','fore-L','fore-R','hind-L','hind-R'):raise ValueError('Unknown contact limb')
        for key in ('point','offset'):r[key]=finite_vector(list(r[key]),3)
        r['rotation']=unit_quaternion(list(r['rotation']))
        for previous in result:
            a=max(first,previous['start']-previous['blend_in'],r['start']-r['blend_in']);b=min(last,previous['end']+previous['blend_out'],r['end']+r['blend_out'])
            if previous['limb']==r['limb'] and (a<b or a==b and weight(previous,a)>0 and weight(r,a)>0):
                raise ValueError('Contact intervals and blends on the same limb must not overlap')
        result.append(r)
    return result


def weight(row,frame):
    if row['start']<=frame<=row['end']:return row['strength']
    blend_in,blend_out=blends(row)
    distance=row['start']-frame if frame<row['start'] else frame-row['end']
    blend=blend_in if frame<row['start'] else blend_out
    if not blend or distance>=blend:return 0.
    t=1-distance/blend
    return row['strength']*t*t*(3-2*t)


def sample_frames(rows,anchors,first,last):
    frames=set(anchors)
    # Quarter-frame fitting is the measured quality/performance knee.  Runtime
    # validation remains denser in contacts.py and adaptively inserts any frame
    # that violates the acceptance gate.
    frames.update(i/4 for i in range(math.ceil(first*4),math.floor(last*4)+1))
    for r in rows:
        blend_in,blend_out=blends(r)
        frames.update((r['start'],r['end'],max(first,r['start']-blend_in),min(last,r['end']+blend_out)))
    return sorted(frames)
