"""Minimal host-only constraint translation reproduction; no add-on imports."""
from pathlib import Path
import os,sys,json,subprocess,time
ROOT=Path(__file__).resolve().parents[2]

def host():
    import bpy,numpy as np
    from mathutils import Vector
    report=dict(host=bpy.app.version_string,build_hash=bpy.app.build_hash.decode(),addon_loaded='b4artists_ml' in sys.modules,cases=[])
    for kind in ('DAMPED_TRACK','STRETCH_TO'):
        data=bpy.data.armatures.new(kind);obj=bpy.data.objects.new(kind,data);bpy.context.scene.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj;obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        root=data.edit_bones.new('root');root.head=(0,0,0);root.tail=(0,0,.2)
        owner=data.edit_bones.new('owner');owner.head=(0,0,1.7);owner.tail=(0,.02,1.7);owner.parent=root
        target=data.edit_bones.new('target');target.head=(.003,.018,1.702);target.tail=(.003,.018,1.722);target.parent=root
        bpy.ops.object.mode_set(mode='OBJECT');con=obj.pose.bones['owner'].constraints.new(kind);con.target=obj;con.subtarget='target'
        if kind=='DAMPED_TRACK':con.track_axis='TRACK_Y'
        bpy.context.view_layer.update();root=obj.pose.bones['root'];base=root.matrix.copy();reference=np.array(obj.pose.bones['owner'].matrix,dtype=float)
        for distance in (0.,.2,2.,7.,30.,120.):
            matrix=base.copy();matrix.translation+=Vector((0,0,distance));root.matrix=matrix;obj.update_tag();bpy.context.view_layer.update()
            actual=np.array(obj.pose.bones['owner'].matrix,dtype=float)
            error=float(np.max(np.linalg.norm(actual[:3,:3]-reference[:3,:3],axis=0)/np.linalg.norm(reference[:3,:3],axis=0)))
            report['cases'].append(dict(constraint=kind,translation=distance,max_relative_basis=error,passes_existing_basis_budget=error<=2e-4,owner_space=con.owner_space,target_space=con.target_space))
        root.matrix=base;obj.update_tag();bpy.context.view_layer.update();np.testing.assert_allclose(np.array(obj.pose.bones['owner'].matrix),reference,atol=1e-7)
    assert not report['addon_loaded'];report['restored']=True
    (ROOT/'training/b4artists_ml/results/minimal-constraint-precision-v1.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

def main():
    started=time.perf_counter()
    with (ROOT/'training/b4artists_ml/cache/minimal-constraint-precision-v1.log').open('w',encoding='utf-8') as log:
        result=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--python',str(Path(__file__).resolve()),'--','--host'],cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4'),stdout=log,stderr=subprocess.STDOUT,timeout=90)
    report=dict(exit_code=result.returncode,elapsed_seconds=time.perf_counter()-started)
    (ROOT/'training/b4artists_ml/results/minimal-constraint-precision-v1-process.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':
    if '--host' in sys.argv:host()
    else:main()
