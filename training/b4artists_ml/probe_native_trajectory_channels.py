"""Compare native polynomial, driver and Bezier evaluation; no add-on imports."""
from pathlib import Path
import sys,os,json,subprocess,time
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve()
OUT=ROOT/'training/b4artists_ml/results/native-trajectory-channels-v1.json'
BLEND=ROOT/'training/b4artists_ml/cache/native-trajectory-channels-v1.blend'
def host():
    import bpy,numpy as np
    scene=bpy.context.scene; frames=np.arange(1.,241.01,.25);u=(frames-1.)/240.; exact=490.5*u*(1-u)
    objects={}
    for kind in ('bezier','generator','driver','dense_linear'):
        ob=bpy.data.objects.new(kind,None);scene.collection.objects.link(ob);objects[kind]=ob
        if kind=='driver':
            fc=ob.driver_add('location',2);fc.driver.type='SCRIPTED';fc.driver.expression='490.5*((frame-1)/240)*(1-(frame-1)/240)'
            continue
        times=frames if kind=='dense_linear' else [1.,241.]
        for f in times:
            v=490.5*((f-1)/240)*(1-(f-1)/240) if kind=='dense_linear' else 0.
            ob.location.z=v;ob.keyframe_insert('location',index=2,frame=float(f))
        ad=ob.animation_data;fc=ad.action.layers[0].strips[0].channelbag(ad.action_slot).fcurves[0]
        if kind=='generator':
            mod=fc.modifiers.new('GENERATOR');mod.mode='POLYNOMIAL';mod.poly_order=2
            # f = frame; 490.5*((f-1)/240) - 490.5*((f-1)/240)**2
            q=490.5/240**2;mod.coefficients=(-490.5/240-q,490.5/240+2*q,-q)
        elif kind=='bezier':
            fc.keyframe_points[0].interpolation='BEZIER'
            fc.keyframe_points[0].handle_right_type='FREE';fc.keyframe_points[1].handle_left_type='FREE'
            fc.keyframe_points[0].handle_right=(81.,163.5);fc.keyframe_points[1].handle_left=(161.,163.5)
        else:
            for k in fc.keyframe_points:k.interpolation='LINEAR'
        fc.update()
    samples={kind:[] for kind in objects}
    for f in frames:
        scene.frame_set(int(f),subframe=float(f-int(f)));bpy.context.view_layer.update()
        for kind,ob in objects.items():samples[kind].append(float(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation.z))
    results={}
    for kind,values in samples.items():
        values=np.array(values);error=np.abs(np.diff(values,n=2)/(.25/24)**2+9.81)
        results[kind]=dict(position_error_max=float(np.max(np.abs(values-exact))),acceleration_error_p95=float(np.percentile(error,95)),passes_existing_acceleration_budget=bool(np.percentile(error,95)<.1),samples=values.tolist())
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    report=dict(addon_loaded='b4artists_ml' in sys.modules,host=bpy.app.version_string,build_hash=bpy.app.build_hash.decode(),frames=frames.tolist(),results=results,scope='Native channel diagnostic only. Dense linear is an evaluation control, not a smooth motion solution; native drivers use simple math expressions only.')
    OUT.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:{a:b for a,b in v.items() if a!='samples'} for k,v in results.items()}),flush=True)
def verify():
    import bpy,numpy as np
    report=json.loads(OUT.read_text());bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    errors={k:0. for k in report['results']}
    for i,f in enumerate(report['frames']):
        bpy.context.scene.frame_set(int(f),subframe=float(f-int(f)));bpy.context.view_layer.update()
        for kind in errors:
            ob=bpy.data.objects[kind];value=float(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation.z)
            errors[kind]=max(errors[kind],abs(value-report['results'][kind]['samples'][i]))
    assert max(errors.values())==0 and 'b4artists_ml' not in sys.modules
    (OUT.parent/'native-trajectory-channels-reload-v1.json').write_text(json.dumps(dict(passed=True,max_reload_difference=errors,addon_loaded=False),indent=2)+'\n')
def main():
    if OUT.exists() or BLEND.exists():raise RuntimeError('Evidence already exists')
    rows=[]
    for mode in ('host','verify'):
        start=time.perf_counter()
        with (ROOT/f'training/b4artists_ml/cache/native-trajectory-channels-{mode}-v1.log').open('w') as log:
            p=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--python',str(HERE),'--','--'+mode],stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4'),timeout=90)
        rows.append(dict(stage=mode,exit_code=p.returncode,elapsed_seconds=time.perf_counter()-start))
        if not OUT.exists():break
    (OUT.parent/'native-trajectory-channels-process-v1.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows))
if __name__=='__main__':
    if '--host' in sys.argv:host()
    elif '--verify' in sys.argv:verify()
    else:main()
