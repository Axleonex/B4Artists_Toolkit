"""Research pose observation -> real FK controls roundtrip, no temporal model."""
from pathlib import Path
import sys, json, time, traceback, os
import bpy, numpy as np
from mathutils import Quaternion, Matrix
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'tests'),str(ROOT/'training/b4artists_ml')]
from test_b4artists_ml_rig_observations import ObservationRigTests
from rig_observations import sample
from b4artists_ml import body_solver as bs, rig_state as rs, posing as p
label_out=os.environ.get('B4ML_PROJECTION_LABEL','rig-observation-projection-v1')
if not label_out.replace('-','').isalnum(): raise ValueError('Simple output label required')
ObservationRigTests.setUpClass(); check=ObservationRigTests(); rows=[]
for label,ob in check.rigs.items():
    bpy.context.scene.frame_set(1)
    rs.normalize_fk(ob); binding=bs.mapping(ob)
    names=binding['rotations']
    # Small but nontrivial authored FK changes across pelvis, torso and limbs.
    for i,name in enumerate(names):
        pb=ob.pose.bones[name]; pb.rotation_mode='QUATERNION'
        base=pb.rotation_quaternion.copy()
        pb.keyframe_insert('rotation_quaternion',frame=1)
        pb.rotation_quaternion=base @ Quaternion((1.,.3,.2), .025*((i%3)-1))
        pb.keyframe_insert('rotation_quaternion',frame=11)
    root=ob.pose.bones[binding['root']]
    root.keyframe_insert('location',frame=1)
    root.location.x+=.025;root.location.y+=.015;root.location.z+=.02
    root.keyframe_insert('location',frame=11)
    bpy.context.scene.frame_set(1);p._update(ob)
    before=check.state(ob);tick=time.perf_counter();observation=sample(ob,1,11,context=False)
    sampling_ms=(time.perf_counter()-tick)*1000
    assert check.state(ob)==before
    targets=observation.world_points(observation.positions[1])
    rotation=Matrix(observation.world_rotations(observation.rotations)[1,0]).to_quaternion()
    session=bs.Session(ob);tick=time.perf_counter()
    row=dict(rig=label,sampling_ms=sampling_ms,passed=False)
    try:
        result=session.solve(targets,np.ones(17,dtype=bool),learned_influence=0.,iterations=100,
                             orientations_world={0:tuple(rotation)})
        row.update(passed=True,pin_error=result['pin_error'],length_error=result['length_error'],
                   orientation_error=result['orientation_error_radians'],evaluations=result['evaluations'],
                   world_position_max_error=float(np.max(np.linalg.norm(session.world_points(session.points())-targets,axis=1))))
    except Exception as exc:
        row.update(error=str(exc),trace=session.trace[-3:])
    finally:
        row['projection_ms']=(time.perf_counter()-tick)*1000
        session.cancel()
        row['source_restored']=check.state(ob)==before
    rows.append(row)
    report=dict(scope='Known authored pose roundtrip only. No temporal model, inbetween prediction, skin quality or animator acceptance.',
                host=bpy.app.version_string,rows=rows,completed=len(rows)==len(check.rigs),passed=len(rows)==len(check.rigs) and all(r['passed'] and r['source_restored'] for r in rows))
    (ROOT/f'training/b4artists_ml/results/{label_out}.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(row),flush=True)
