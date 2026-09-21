"""Native collection-instance motion feasibility; disposable scene, no runtime edits."""
from pathlib import Path
import sys,os,json,time,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve()
BLEND=ROOT/'training/b4artists_ml/cache/instance-motion-feasibility-v1.blend'
META=ROOT/'training/b4artists_ml/results/instance-motion-feasibility-v1.json'

def sample(bpy,np,obj,mesh,inst,names):
    dep=bpy.context.evaluated_depsgraph_get();result={}
    for entry in dep.object_instances:
        if not entry.is_instance or not entry.parent or entry.parent.original!=inst:continue
        if entry.object.original==obj:
            result['bones']=np.einsum('ij,bjk->bik',np.array(entry.matrix_world,dtype=float),np.array([entry.object.pose.bones[n].matrix for n in names],dtype=float))
        elif entry.object.original==mesh:
            result['mesh']=np.array([entry.matrix_world@v.co for v in entry.object.data.vertices],dtype=float)
    assert set(result)=={'bones','mesh'},list(result)
    return result

def setup():
    import bpy,numpy as np
    from mathutils import Vector
    sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
    import test_b4artists_ml_flight as t
    t.FlightTests.setUpClass();ob,source,source_sig,modes=t.fixture('rigify_default',True);scene=bpy.context.scene
    w,p,c=t.w,t.p,t.c
    w.finish_preview(ob,scene,False);max(ob.b4ml.anchors,key=lambda a:a.frame).frame=61
    w.preview(ob,scene);w.finish_preview(ob,scene,True)
    names=sorted(b.name for b in ob.data.bones if b.use_deform);verts=[]
    for name in names:
        bone=ob.data.bones[name];point=bone.head_local;size=max(float(bone.length)*.25,1e-5)
        verts.extend([tuple(point),tuple(point+Vector((size,0,0))),tuple(point+Vector((0,size,0)))])
    data=bpy.data.meshes.new('Instance precision mesh');data.from_pydata(verts,[],[tuple(range(i,i+3)) for i in range(0,len(verts),3)])
    mesh=bpy.data.objects.new('Instance precision mesh',data);scene.collection.objects.link(mesh);mesh.matrix_world=ob.matrix_world
    mesh.modifiers.new('Armature','ARMATURE').object=ob
    for index,name in enumerate(names):mesh.vertex_groups.new(name=name).add(list(range(index*3,index*3+3)),1.,'REPLACE')
    group=bpy.data.collections.new('Character evaluation collection');group.objects.link(ob);group.objects.link(mesh)
    inst=bpy.data.objects.new('Character motion instance',None);inst.instance_type='COLLECTION';inst.instance_collection=group;scene.collection.objects.link(inst)
    world=ob.matrix_world.copy();pose_token=t.f._curve_token(ob)
    report=dict(host=bpy.app.version_string,build_hash=bpy.app.build_hash.decode(),source_rig=ob.name,mesh=mesh.name,instance=inst.name,scene=scene.name,bones=names,cases=[],scope='Feasibility on one transformed default Rigify with synthetic bound triangles. Source and instance both remain visible; no production preview/hide/keep/export integration is implemented.',script_sha256=hashlib.sha256(HERE.read_bytes()).hexdigest(),passed=False)
    for frame in (6.,20.+1/3,31.):
        scene.frame_set(int(frame),subframe=frame-int(frame));p._update(ob)
        before=np.array([ob.matrix_world@ob.pose.bones[n].matrix for n in names]);evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh_before=np.array([evaluated.matrix_world@v.co for v in evaluated.data.vertices])
        for distance in (0.,.2,2.,7.,30.,120.):
            inst.location=(0,0,distance);bpy.context.view_layer.update();got=sample(bpy,np,ob,mesh,inst,names);delta=np.array([0,0,distance])
            error=float(np.max(np.linalg.norm(got['bones'][:,:3,:3]-before[:,:3,:3],axis=1)/np.linalg.norm(before[:,:3,:3],axis=1)))
            heads=float(np.max(np.linalg.norm(got['bones'][:,:3,3]-before[:,:3,3]-delta,axis=1)))
            vertices=float(np.max(np.linalg.norm(got['mesh']-mesh_before-delta,axis=1)))
            assert error<=2e-4 and heads<=2e-4 and vertices<=2e-4
            report['cases'].append(dict(frame=frame,translation=distance,basis=error,head_error=heads,mesh_error=vertices))
    assert t.f._curve_token(ob)==pose_token and ob.matrix_world==world
    # Standard editable object F-curves, deliberately labelled procedural keys.
    for frame,z in ((1.,0.),(16.,30.),(31.,120.),(46.,30.),(61.,0.)):
        inst.location=(0,0,z);inst.keyframe_insert('location',frame=frame)
    for fc in w.action_curves(inst.animation_data.action,getattr(inst.animation_data,'action_slot',None)):
        for k in fc.keyframe_points:k.interpolation='LINEAR'
    report['playback']=[]
    for frame in (1.,7.5,20.+1/3,31.,44.25,61.):
        scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update();got=sample(bpy,np,ob,mesh,inst,names)
        report['playback'].append(dict(frame=frame,translation=list(inst.location),bones=got['bones'].tolist(),mesh=got['mesh'].tolist()))
    report.update(passed=True,source_curve_unchanged=True,source_world_unchanged=True,mesh_vertices=len(verts),editable_action=inst.animation_data.action.name)
    META.write_text(json.dumps(report,indent=2)+'\n');bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    print('INSTANCE_SETUP '+json.dumps({k:v for k,v in report.items() if k not in ('cases','playback','bones')}),flush=True)

def verify():
    import bpy,numpy as np
    assert 'b4artists_ml' not in sys.modules
    report=json.loads(META.read_text());bpy.ops.wm.open_mainfile(filepath=str(BLEND));scene=bpy.data.scenes[report['scene']];bpy.context.window.scene=scene
    ob=bpy.data.objects[report['source_rig']];mesh=bpy.data.objects[report['mesh']];inst=bpy.data.objects[report['instance']]
    errors=[]
    for row in report['playback']:
        frame=row['frame'];scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update();got=sample(bpy,np,ob,mesh,inst,report['bones'])
        error=max(float(np.max(np.abs(got[key]-np.array(row[key])))) for key in ('bones','mesh'));assert error<2e-5;errors.append(error)
    assert 'b4artists_ml' not in sys.modules
    result=dict(passed=True,addon_loaded=False,frames=len(errors),max_reload_difference=max(errors),editable_action=inst.animation_data.action.name,blend_sha256=hashlib.sha256(BLEND.read_bytes()).hexdigest(),scope='Native playback only; not end-user workflow, clean host exit, source/instance visibility, contact composition or export acceptance')
    (ROOT/'training/b4artists_ml/results/instance-motion-native-playback-v1.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)

def main():
    if META.exists() or BLEND.exists():raise RuntimeError('Refusing to overwrite evidence')
    rows=[]
    for stage in ('setup','verify'):
        started=time.perf_counter()
        with (ROOT/f'training/b4artists_ml/cache/instance-motion-{stage}-v1.log').open('w',encoding='utf-8') as log:
            result=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--python',str(HERE),'--','--'+stage],cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4'),stdout=log,stderr=subprocess.STDOUT,timeout=180)
        rows.append(dict(stage=stage,exit_code=result.returncode,elapsed_seconds=time.perf_counter()-started));print(json.dumps(rows[-1]),flush=True)
        (ROOT/'training/b4artists_ml/results/instance-motion-process-v1.json').write_text(json.dumps(rows,indent=2)+'\n')
        if stage=='setup' and (not META.exists() or not BLEND.exists()):break

if __name__=='__main__':
    if '--setup' in sys.argv:setup()
    elif '--verify' in sys.argv:verify()
    else:main()
