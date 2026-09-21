"""Host-independent contact interval detection.

Inputs are normalized observations produced by the Bforartists scene adapter.
This module classifies provisional intervals only; it never edits animation.
"""
import math


def _finite(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(label + ' must be a finite number')
    return float(value)


def detect_intervals(samples, max_distance, max_speed, min_frames, gap_frames):
    """Return provisional spans from ordered per-frame observations.

    ``distance`` is absolute surface distance divided by evaluated limb length;
    ``speed`` is tangential speed divided by limb length per second. ``inside``
    states whether the projected point belongs to a bounded support surface.
    """
    max_distance=_finite(max_distance,'Maximum contact distance')
    max_speed=_finite(max_speed,'Maximum contact speed')
    if max_distance<=0 or max_speed<=0:raise ValueError('Contact thresholds must be positive')
    if isinstance(min_frames,bool) or not isinstance(min_frames,int) or min_frames<2:raise ValueError('Minimum contact frames must be at least two')
    if isinstance(gap_frames,bool) or not isinstance(gap_frames,int) or not 0<=gap_frames<=12:raise ValueError('Contact gap frames must be between zero and twelve')
    checked=[]
    for sample in samples:
        if not isinstance(sample,dict):raise ValueError('Contact samples must be records')
        frame=_finite(sample.get('frame'),'Contact frame')
        distance=_finite(sample.get('distance'),'Contact distance')
        speed=_finite(sample.get('speed'),'Contact speed')
        if distance<0 or speed<0:raise ValueError('Contact distance and speed cannot be negative')
        checked.append(dict(sample,frame=frame,distance=distance,speed=speed,
            eligible=bool(sample.get('inside')) and distance<=max_distance and speed<=max_speed))
    if any(b['frame']<=a['frame'] for a,b in zip(checked,checked[1:])):raise ValueError('Contact samples must have increasing frames')
    runs=[];current=[];last_eligible=None
    for sample in checked:
        if sample['eligible']:
            if current and sample['frame']-last_eligible>1+gap_frames+1e-6:
                runs.append(current);current=[]
            current.append(sample);last_eligible=sample['frame']
        elif current and sample['frame']-last_eligible>1+gap_frames+1e-6:
            runs.append(current);current=[];last_eligible=None
    if current:runs.append(current)
    result=[]
    for run in runs:
        if (len(run)<min_frames
                or run[-1]['frame']-run[0]['frame'] < min_frames-1-1e-6):continue
        distance_ratio=max(s['distance']/max_distance for s in run)
        speed_ratio=max(s['speed']/max_speed for s in run)
        confidence=max(0.,min(.95,1.-.5*distance_ratio-.5*speed_ratio))
        result.append(dict(start=run[0]['frame'],end=run[-1]['frame'],samples=run,
            sample_count=len(run),max_distance=max(s['distance'] for s in run),
            max_speed=max(s['speed'] for s in run),confidence=confidence))
    return result
