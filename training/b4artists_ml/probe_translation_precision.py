"""Controlled root/object translation precision; diagnostic only, no addon edits.
SPDX-License-Identifier: GPL-2.0-or-later
"""
from pathlib import Path
import os,sys,json,time,subprocess,hashlib,traceback,platform
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve()
TAG='rigify-translation-precision-v1'

def host():
    sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
    import numpy as np,bpy
    from mathutils import Vector
    import test_b4artists_ml_flight as t
    f,w,p,c,rs=t.f,t.w,t.p,t.c,t.rs
    report=dict(schema=1,protocol='Same evaluated pose, displacement and mesh weights; vary only root/object share. Fresh restore before each branch. No runtime or tolerance changes.',host=bpy.app.version_string,build_hash=bpy.app.build_hash.decode(),python=platform.python_version(),numpy=np.__version__,script_sha256=hashlib.sha256(HERE.read_bytes()).hexdigest(),cases=[],constraints={},recovery=[],passed=False)
    dest=ROOT/f'training/b4artists_ml/results/{TAG}.json'
    def persist():dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    try:
        t.FlightTests.setUpClass()
        for label in ('boneforge','rigify_basic','rigify_default'):
            ob,source,source_sig,modes=t.fixture(label);scene=bpy.context.scene
            w.finish_preview(ob,scene,False);max(ob.b4ml.anchors,key=lambda a:a.frame).frame=61
            w.preview(ob,scene);scene.frame_set(31);p._update(ob)
            original=ob.b4ml.candidate_action;pose_before=w.raw_pose(ob);world=ob.matrix_world.copy();root=ob.pose.bones['root']
            names=sorted(b.name for b in ob.data.bones if b.use_deform)
            # Small triangles weighted independently to every deform bone. They
            # measure the actual armature modifier, not a matrix-only surrogate.
            verts=[]
            for name in names:
                bone=ob.data.bones[name];point=bone.head_local.copy();size=max(float(bone.length)*.25,1e-5)
                verts.extend([tuple(point),tuple(point+Vector((size,0,0))),tuple(point+Vector((0,size,0)))])
            mesh_data=bpy.data.meshes.new(label+' precision mesh');mesh_data.from_pydata(verts,[],[tuple(range(i,i+3)) for i in range(0,len(verts),3)])
            mesh=bpy.data.objects.new(label+' precision mesh',mesh_data);scene.collection.objects.link(mesh)
            mesh.matrix_world=world;mesh.modifiers.new('Armature','ARMATURE').object=ob
            for index,name in enumerate(names):mesh.vertex_groups.new(name=name).add(list(range(index*3,index*3+3)),1.,'REPLACE')
            def snapshot():
                dep=bpy.context.evaluated_depsgraph_get();evaluated=ob.evaluated_get(dep)
                local=np.array([evaluated.pose.bones[n].matrix for n in names],dtype=np.float64)
                matrices=np.einsum('ij,bjk->bik',np.array(evaluated.matrix_world,dtype=np.float64),local)
                evaluated_mesh=mesh.evaluated_get(dep)
                points=np.array([evaluated_mesh.matrix_world@v.co for v in evaluated_mesh.data.vertices],dtype=np.float64)
                return matrices,points,local
            def restore(frame):
                ob.matrix_world=world;scene.frame_set(int(frame),subframe=frame-int(frame));p._update(ob)
            for frame in (6.,20.+1/3,31.):
                restore(frame);before,mesh_before,local_before=snapshot();baseline_root=root.location.copy()
                for distance in (0.,.2,2.,7.,30.,120.):
                    delta=np.array([0.,0.,distance])
                    for share in (1.,.5,0.):
                        for convert in (('host','direct') if share==1. else ('host',)):
                            restore(frame)
                            if share:
                                local_delta=world.inverted().to_3x3()@Vector(delta*share)
                                if convert=='host':p._translate(ob,'root',local_delta)
                                else:
                                    assert root.parent is None
                                    root.location=np.array(baseline_root)+np.linalg.solve(np.array(root.bone.matrix_local)[:3,:3],np.array(local_delta));p._update(ob)
                            if share<1:
                                matrix=world.copy();matrix.translation+=Vector(delta*(1-share));ob.matrix_world=matrix;p._update(ob)
                            after,mesh_after,local_after=snapshot()
                            lengths=np.linalg.norm(before[:,:3,:3],axis=1)
                            basis_by_bone=np.max(np.linalg.norm(after[:,:3,:3]-before[:,:3,:3],axis=1)/lengths,axis=1)
                            i=int(np.argmax(basis_by_bone));head_error=np.linalg.norm(after[:,:3,3]-before[:,:3,3]-delta,axis=1)
                            mesh_error=np.linalg.norm(mesh_after-mesh_before-delta,axis=1)
                            row=dict(rig=label,frame=frame,translation=delta.tolist(),root_share=share,conversion=convert,max_relative_basis=float(basis_by_bone[i]),worst_bone=names[i],max_head_error=float(max(head_error)),max_mesh_error=float(max(mesh_error)),mesh_vertices=len(mesh_after),basis_budget_pass=bool(max(basis_by_bone)<=2e-4))
                            report['cases'].append(row)
                            if row['max_relative_basis']>2e-4:
                                name=names[i]
                                if label+':'+name not in report['constraints']:
                                    chain=[];bone=ob.pose.bones[name]
                                    while bone:
                                        chain.append(dict(name=bone.name,rest_length=float(bone.bone.length),constraints=[dict(type=con.type,name=con.name,influence=con.influence,owner_space=con.owner_space,target_space=con.target_space,target=getattr(getattr(con,'target',None),'name',None),subtarget=getattr(con,'subtarget',None)) for con in bone.constraints]));bone=bone.parent
                                    report['constraints'][label+':'+name]=chain
                persist()
            restore(31.);assert ob.animation_data.action==original and w.raw_pose(ob)==pose_before
            w.finish_preview(ob,scene,False)
            assert ob.animation_data.action==source and c._action_signature(ob)==source_sig and rs.mode_values(ob)==modes
            assert ob.matrix_world==world
            report['recovery'].append(dict(rig=label,source=True,modes=True,world=True,pose=True))
            print('PRECISION_RIG '+json.dumps(dict(rig=label,cases=sum(ca['rig']==label for ca in report['cases']),recovery=True)),flush=True);persist()
        report['passed']=True
    except BaseException as exc:report.update(error=str(exc),traceback=traceback.format_exc())
    finally:persist();print('PRECISION_RESULT '+json.dumps({k:v for k,v in report.items() if k not in ('cases','constraints')}),flush=True)

def main():
    dest=ROOT/f'training/b4artists_ml/results/{TAG}.json'
    if dest.exists():raise RuntimeError('Refusing to overwrite existing diagnostic evidence')
    started=time.perf_counter()
    with (ROOT/f'training/b4artists_ml/cache/{TAG}.log').open('w',encoding='utf-8') as log:
        result=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--python',str(HERE),'--','--host'],cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4'),stdout=log,stderr=subprocess.STDOUT,timeout=300)
    process=dict(exit_code=result.returncode,elapsed_seconds=time.perf_counter()-started,result_sha256=hashlib.sha256(dest.read_bytes()).hexdigest() if dest.exists() else None)
    (ROOT/f'training/b4artists_ml/results/{TAG}-process.json').write_text(json.dumps(process,indent=2)+'\n');print(json.dumps(process))

if __name__=='__main__':
    if '--host' in sys.argv:host()
    else:main()
