"""Native read-only RNA batch compatibility probe for source guard research."""
from pathlib import Path
import sys,json,hashlib,subprocess,os,time
HERE=Path(__file__).resolve();TR=HERE.parent;ROOT=TR.parents[1];OUT=TR/'results/visible-state-bulk-probe-v1'
def host():
 import bpy,numpy as np
 sys.path.insert(0,str(ROOT));from b4artists_ml import workflow as w
 # Registration supplies properties required by the retained reference file.
 import b4artists_ml;b4artists_ml.register();ref=TR/'results/broader-shape-runtime-v1/rigify_default/reach_hold-smooth_both.blend';bpy.ops.wm.open_mainfile(filepath=str(ref),load_ui=False,use_scripts=False);obj=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE' and o.b4ml.candidate_action);bones=obj.pose.bones;n=len(bones);rows=[]
 for prop,width in [('location',3),('scale',3),('rotation_euler',3),('rotation_quaternion',4),('rotation_axis_angle',4),('lock_location',3),('lock_scale',3),('lock_rotation',3),('lock_rotations_4d',1),('lock_rotation_w',1)]:
  actual=np.array([tuple(getattr(b,prop)) if width>1 else getattr(b,prop) for b in bones]);types=[np.bool_] if prop.startswith('lock_') else [np.float32,np.float64]
  for dtype in types:
   value=np.empty(actual.shape,dtype=dtype)
   try:bones.foreach_get(prop,value.ravel());row=dict(property=prop,dtype=str(np.dtype(dtype)),supported=True,exact=np.array_equal(value,actual),max_difference=float(np.max(abs(value.astype(float)-actual.astype(float)))))
   except Exception as exc:row=dict(property=prop,dtype=str(np.dtype(dtype)),supported=False,error=repr(exc))
   rows.append(row)
 bone=bones[0];before_mode=bone.rotation_mode;bone.rotation_mode='XYZ';bone.rotation_euler=(.1,.2,.3);before=w.raw_pose(obj,{bone.name})[bone.name];bone.rotation_euler.order='ZYX';after=w.raw_pose(obj,{bone.name})[bone.name]
 report=dict(complete=True,bones=n,fields=rows,euler_order_probe=dict(mode_before=before['mode'],mode_after=after['mode'],raw_before=before['raw_rotation'],raw_after=after['raw_rotation'],rotation_before=before['rotation'],rotation_after=after['rotation']),host=bpy.app.version_string,production_changed=False)
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
def main():
 OUT.mkdir(exist_ok=False)
 with (OUT/'host.log').open('w') as log:p=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--','host'],stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,OPENBLAS_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1'),timeout=120)
 (OUT/'process.json').write_text(json.dumps(dict(exit_code=p.returncode))+'\n');print((OUT/'report.json').read_text() if (OUT/'report.json').exists() else (OUT/'host.log').read_text());print('Native exit',p.returncode)
if __name__=='__main__':
 if 'host' in sys.argv:host()
 else:main()
