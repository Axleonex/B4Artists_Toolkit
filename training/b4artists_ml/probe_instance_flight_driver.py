"""Evaluate split residual curves and analytic native trajectory drivers; disposable scene."""
from pathlib import Path
import sys,os,json,time,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve()
BLEND=ROOT/'training/b4artists_ml/cache/instance-flight-driver-feasibility-v1.blend'
META=ROOT/'training/b4artists_ml/results/instance-flight-driver-feasibility-v1.json'

def sample(bpy,np,obj,mesh,inst,names):
    dep=bpy.context.evaluated_depsgraph_get();result={}
    for entry in dep.object_instances:
        if not entry.is_instance or not entry.parent or entry.parent.original!=inst:continue
        if entry.object.original==obj:
            result['heads']=np.array([entry.matrix_world@entry.object.pose.bones[n].head for n in names],dtype=float)
            result['tails']=np.array([entry.matrix_world@entry.object.pose.bones[n].tail for n in names],dtype=float)
            result['bones']=np.einsum('ij,bjk->bik',np.array(entry.matrix_world,dtype=float),np.array([entry.object.pose.bones[n].matrix for n in names],dtype=float))
        elif entry.object.original==mesh:
            result['mesh']=np.array([entry.matrix_world@v.co for v in entry.object.data.vertices],dtype=float)
    assert set(result)=={'bones','mesh','heads','tails'},list(result)
    return result

def setup():
    import bpy,numpy as np
    from mathutils import Vector
    sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
    import test_b4artists_ml_flight as t
    t.FlightTests.setUpClass();ob,source,source_sig,modes=t.fixture('rigify_default',True);scene=bpy.context.scene
    w,p,c=t.w,t.p,t.c
    w.finish_preview(ob,scene,False);max(ob.b4ml.anchors,key=lambda a:a.frame).frame=241
    w.preview(ob,scene);w.finish_preview(ob,scene,True)
    names=sorted({b.name for b in ob.data.bones if b.use_deform}|set(t.support.body_solver.mapping(ob,writable=False)['names']));verts=[]
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
    report=dict(host=bpy.app.version_string,build_hash=bpy.app.build_hash.decode(),source_rig=ob.name,mesh=mesh.name,instance=inst.name,scene=scene.name,bones=names,cases=[],scope='Procedural 240-frame COM flight feasibility on one transformed default Rigify with synthetic bound triangles. Source and instance both remain visible; no production preview/hide/keep/export/contact integration is implemented. Not learned temporal motion.',script_sha256=hashlib.sha256(HERE.read_bytes()).hexdigest(),passed=False)
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
    # Procedural COM flight written to native instance-object F-curves.
    # This is not a learned-motion model or a production output adapter.
    from b4artists_ml import flight_math as fm
    inst.location=(0,0,0);binding=t.support.body_solver.mapping(ob,writable=False)
    masses=[i.weight for i in ob.b4ml.mass_segments];fractions=[i.fraction for i in ob.b4ml.mass_segments]
    def at(frame):
        scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update()
        _,_,starts,ends=t.support.sample(ob,bpy.context.evaluated_depsgraph_get())
        return t.f.center_of_mass(starts,ends,masses,fractions)[0],starts,ends
    start,starts,ends=at(1.);end,_,_=at(241.)
    scale=sum(float(np.linalg.norm(ends[i]-starts[i])) for i in range(3));duration=240*scene.render.fps_base/scene.render.fps;gravity=list(scene.gravity)
    values={};times=[1+i*4. for i in range(61)];segments=list(zip(times,times[1:]));began=time.perf_counter()
    def target(frame):return fm.trajectory(start,end,[(frame-1)/240],duration,gravity)[0]
    for left,right in segments:
        for frame in (left,left+(right-left)/3,left+2*(right-left)/3,right):
            if frame not in values:
                u=(frame-1)/240
                values[frame]=start*(1-u)+end*u-at(frame)[0]
    for frame in times:
        for axis in range(3):
            prop='b4ml_residual_'+str(axis);inst[prop]=float(values[frame][axis]);inst.keyframe_insert(data_path='[\"'+prop+'\"]',frame=frame)
    curves=w.action_curves(inst.animation_data.action,getattr(inst.animation_data,'action_slot',None))
    for axis in range(3):
        fc=curves.find('[\"b4ml_residual_'+str(axis)+'\"]');keys={float(k.co.x):k for k in fc.keyframe_points}
        for left,right in segments:
            a,b=fm.cubic_controls([values[left],values[left+(right-left)/3],values[left+2*(right-left)/3],values[right]])
            ka,kb=keys[left],keys[right];ka.handle_right_type=kb.handle_left_type='FREE';ka.interpolation='BEZIER'
            ka.handle_right=(left+(right-left)/3,float(a[axis]));kb.handle_left=(left+2*(right-left)/3,float(b[axis]))
        fc.update()
    for axis in range(3):
        driver=inst.driver_add('location',axis).driver;driver.type='SCRIPTED'
        variable=driver.variables.new();variable.name='residual';variable.type='SINGLE_PROP'
        variable.targets[0].id=inst;variable.targets[0].data_path='["b4ml_residual_'+str(axis)+'"]'
        u='min(max((frame-1)/240,0),1)'
        driver.expression='residual+('+repr(.5*gravity[axis]*duration**2)+')*(('+u+')**2-('+u+'))'
    report['flight_fit_seconds']=time.perf_counter()-began
    lookup={name:i for i,name in enumerate(names)};mapped=[lookup[n] for n in binding['names']]
    positions=[];checks=[]
    for frame in np.arange(1.,241.01,.25):
        at(float(frame));got=sample(bpy,np,ob,mesh,inst,names)
        heads=got['heads'][mapped];tails=got['tails'][mapped]
        a=np.array([heads[i] for _,i,j,weight in t.support.SEGMENTS]);b=np.array([heads[j] if j is not None else tails[i] for _,i,j,weight in t.support.SEGMENTS])
        actual=t.f.center_of_mass(a,b,masses,fractions)[0];positions.append(actual)
        before=np.array([ob.matrix_world@ob.pose.bones[n].matrix for n in names]);delta=np.array(inst.location)
        expected=before.copy();expected[:,:3,3]+=delta
        basis=float(np.max(np.linalg.norm(got['bones'][:,:3,:3]-before[:,:3,:3],axis=1)/np.linalg.norm(before[:,:3,:3],axis=1)))
        com_error=float(np.linalg.norm(actual-target(frame)))/scale
        evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh_before=np.array([evaluated.matrix_world@v.co for v in evaluated.data.vertices])
        mesh_error=float(np.max(np.linalg.norm(got['mesh']-mesh_before-delta,axis=1)))/scale
        assert basis<=2e-4 and com_error<=2e-4 and mesh_error<=2e-4
        if frame in (1.,241.):assert np.linalg.norm(inst.location)<2e-5
        checks.append(dict(frame=float(frame),basis=basis,com_error=com_error,mesh_error=mesh_error))
    dt=.25*scene.render.fps_base/scene.render.fps;acc=np.diff(np.array(positions),n=2,axis=0)/dt**2;error=np.linalg.norm(acc-np.array(gravity),axis=1)
    report['native_driver_expressions']=[fc.driver.expression for fc in inst.animation_data.drivers]
    report['flight']=dict(fit_interval_frames=4.,frames=240,seconds=duration,samples=len(checks),keys_per_axis=len(times),max_com_error=max(v['com_error'] for v in checks),max_basis=max(v['basis'] for v in checks),max_mesh_error=max(v['mesh_error'] for v in checks),acceleration_sample_frames=.25,acceleration_error_p95=float(np.percentile(error,95)),acceleration_budget_pass=bool(np.percentile(error,95)<.1),priority_offset_zero=True,checks=checks)
    assert t.f._curve_token(ob)==pose_token and ob.matrix_world==world
    report['playback']=[]
    for frame in (1.,7.5,20.+1/3,121.,200.25,241.):
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
    (ROOT/'training/b4artists_ml/results/instance-flight-driver-native-playback-v1.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)

def main():
    if META.exists() or BLEND.exists():raise RuntimeError('Refusing to overwrite evidence')
    rows=[]
    for stage in ('setup','verify'):
        started=time.perf_counter()
        with (ROOT/f'training/b4artists_ml/cache/instance-flight-driver-{stage}-v1.log').open('w',encoding='utf-8') as log:
            result=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--python',str(HERE),'--','--'+stage],cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4'),stdout=log,stderr=subprocess.STDOUT,timeout=180)
        rows.append(dict(stage=stage,exit_code=result.returncode,elapsed_seconds=time.perf_counter()-started));print(json.dumps(rows[-1]),flush=True)
        (ROOT/'training/b4artists_ml/results/instance-flight-driver-process-v1.json').write_text(json.dumps(rows,indent=2)+'\n')
        if stage=='setup' and (not META.exists() or not BLEND.exists()):break

if __name__=='__main__':
    if '--setup' in sys.argv:setup()
    elif '--verify' in sys.argv:verify()
    else:main()
