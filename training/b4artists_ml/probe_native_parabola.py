"""Check existing finite-difference acceleration metric on an exact native parabola."""
from pathlib import Path
import sys,os,json,subprocess,time
ROOT=Path(__file__).resolve().parents[2]

def host():
    import bpy,numpy as np
    ob=bpy.data.objects.new('Exact parabola',None);bpy.context.scene.collection.objects.link(ob)
    for frame in (1.,241.):ob.location=(0,0,0);ob.keyframe_insert('location',frame=frame)
    ad=ob.animation_data;curves=ad.action.layers[0].strips[0].channelbag(ad.action_slot).fcurves;fc=curves.find('location',index=2)
    a,b=fc.keyframe_points;a.interpolation='BEZIER';a.handle_right_type=b.handle_left_type='FREE';a.handle_right=(81.,163.5);b.handle_left=(161.,163.5);fc.update()
    frames=np.arange(1.,241.01,.25);u=(frames-1.)/240;exact=4*122.625*u*(1-u);native=[];curve=[]
    for frame in frames:
        bpy.context.scene.frame_set(int(frame),subframe=float(frame-int(frame)));bpy.context.view_layer.update();native.append(float(ob.location.z));curve.append(float(fc.evaluate(float(frame))))
    dt=.25/24;rows={}
    for name,values in (('float64_formula',exact),('float32_formula',exact.astype(np.float32).astype(float)),('native_curve',np.array(curve)),('native_object',np.array(native))):
        error=np.abs(np.diff(values,n=2)/dt**2+9.81)
        rows[name]=dict(position_error_max=float(np.max(np.abs(values-exact))),acceleration_error_p95=float(np.percentile(error,95)),acceleration_error_max=float(np.max(error)),passes_existing_acceleration_budget=bool(np.percentile(error,95)<.1))
    report=dict(host=bpy.app.version_string,build_hash=bpy.app.build_hash.decode(),addon_loaded='b4artists_ml' in sys.modules,frames=240,samples=len(frames),sample_spacing_frames=.25,fps=24,keys=[list(a.co),list(b.co)],handles=[list(a.handle_right),list(b.handle_left)],expected_acceleration=-9.81,results=rows,scope='Native two-key parabola diagnostic; acceptance threshold and sampling unchanged. Not a relaxation or a product pass.')
    (ROOT/'training/b4artists_ml/results/native-parabola-precision-v1.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

def main():
    started=time.perf_counter()
    with (ROOT/'training/b4artists_ml/cache/native-parabola-precision-v1.log').open('w',encoding='utf-8') as log:
        result=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--python',str(Path(__file__).resolve()),'--','--host'],cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4'),stdout=log,stderr=subprocess.STDOUT,timeout=90)
    report=dict(exit_code=result.returncode,elapsed_seconds=time.perf_counter()-started)
    (ROOT/'training/b4artists_ml/results/native-parabola-precision-v1-process.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':
    if '--host' in sys.argv:host()
    else:main()
