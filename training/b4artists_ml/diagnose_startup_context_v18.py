"""Training-only check for duplicated calibration/startup speed anomalies."""
from pathlib import Path
import json,hashlib
import numpy as np
from bvh_data import parse_bvh
from semantic_motion_data import from_bvh
ROOT=Path(__file__).resolve().parent

def main():
    manifest=ROOT/'results/boundary_trajectory_v16/manifest.json';rows=json.loads(manifest.read_text())['files'];out=[]
    for row in rows:
        if row['split']!='train':continue
        path=ROOT/'cache'/(row['clip']+'.bvh');assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
        motion=parse_bvh(path.read_text());p,r=motion.transforms();seq=from_bvh(motion);scale=np.linalg.norm((seq.rest[5]+seq.rest[8]-seq.rest[11]-seq.rest[14])*.5)
        speed=np.linalg.norm(np.diff(seq.positions,axis=0),axis=-1).mean(axis=1)/scale/seq.dt
        out.append(dict(clip=row['clip'],source_sha256=row['sha256'],first_valid_rest_position_delta=float(np.max(np.linalg.norm(p[1]-p[0],axis=-1))/scale),first_valid_rest_rotation_delta=float(np.max(abs(r[1]-r[0]))),first_decimated_speed=float(speed[0]),speed_median=float(np.median(speed)),speed_p95=float(np.percentile(speed,95)),first_speed_over_p95=float(speed[0]/max(np.percentile(speed,95),1e-12))))
    duplicates=[r['clip'] for r in out if r['first_valid_rest_position_delta']<1e-9 and r['first_valid_rest_rotation_delta']<1e-9]
    result=dict(scope='Training-only startup hypothesis check; no exclusion, resampling, validation motion or training protocol change.',clips=len(out),duplicate_calibration_at_first_motion_frame=duplicates,max_first_speed_over_clip_p95=max(r['first_speed_over_p95'] for r in out),rows=out,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),manifest]})
    p=ROOT/'results/startup-context-diagnostic-v18.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['rows','source_sha256']}))
if __name__=='__main__':main()
