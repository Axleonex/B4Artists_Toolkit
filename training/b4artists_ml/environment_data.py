"""Known environmental context for existing temporal windows; never infer hidden contacts."""
import hashlib
import numpy as np
from bvh_data import parse_bvh
from sequence_data import full_motion,known_window,load_windows
from environment_context import Environment,encode_environment


def environment_window(motion,start,end,t,context,environment):
    window=known_window(motion,start,end,t,context)
    window['environment']=encode_environment(environment,window['origin'],window['basis'],motion.semantic_motion.scale,(end-start)*motion.semantic_motion.dt)
    return window


def load_environment_windows(root,manifest,split,protocol):
    windows,skeleton=load_windows(root,manifest,split,protocol);motions={}
    # This assumption is explicit protocol metadata, not an estimated floor or measured acceleration.
    if protocol['source_environment']!='assumed_Y_up_direction_only':raise ValueError('Unknown source environment convention')
    environment=Environment(direction_hint=(0.,-1.,0.))
    rows={row['clip']:row for row in manifest['files'] if row['split']==split}
    for w in windows:
        clip=w['clip']
        if clip not in motions:
            path=root/'cache'/(clip+'.bvh')
            if hashlib.sha256(path.read_bytes()).hexdigest()!=rows[clip]['sha256']:raise ValueError('Source checksum changed')
            motion=full_motion(parse_bvh(path.read_text()),protocol['target_fps'])
            if np.dot(motion.semantic_motion.reference[:,2],[0,1,0])<.9:raise ValueError('Rest convention does not support the declared up-axis assumption')
            motions[clip]=motion
        motion=motions[clip];start=int(np.searchsorted(motion.semantic_motion.frames,w['frame'][0]));end=start+w['gap']
        if not np.array_equal(motion.semantic_motion.frames[start:end+1],w['frame']):raise ValueError('Window frame identity mismatch')
        known=environment_window(motion,start,end,w['t'],w['context'],environment)
        w['environment']=known['environment']
    return windows,skeleton


def gravity_features(windows):
    result=[]
    for w in windows:
        e=np.asarray(w['environment'],dtype=float)
        if e.shape!=(11,) or not np.isfinite(e).all() or e[4]!=1 or not np.isclose(np.linalg.norm(e[:3]),1,atol=1e-7):raise ValueError('This learned model requires a known gravity direction')
        # The learned experiment consumes direction only, never claims magnitude/support learning.
        result.append(np.r_[w['x'],e[:3],e[4]])
    return np.stack(result)
