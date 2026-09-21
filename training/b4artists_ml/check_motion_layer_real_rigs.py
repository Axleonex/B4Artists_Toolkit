"""Actual-rig ownership, native playback, direct editing and fresh recovery checks."""
from pathlib import Path
import sys, os, json, time, subprocess, hashlib
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
PREFIX = "motion-layer-real-v4"
RIGS = ("boneforge", "rigify_basic", "rigify_default", "metarig_basic", "metarig_default")

def path(label, suffix):
    return ROOT / "training/b4artists_ml" / ("cache" if suffix.endswith((".blend", ".log")) else "results") / f"{PREFIX}-{label}{suffix}"

def sample(ob, mesh, instance=None):
    import bpy, numpy as np
    graph = bpy.context.evaluated_depsgraph_get()
    if instance:
        points = bones = None
        # Depsgraph instance wrappers are transient: copy values during iteration.
        for entry in graph.object_instances:
            if not entry.is_instance or not entry.parent or entry.parent.original != instance:
                continue
            if entry.object.original == mesh:
                points = np.array([entry.matrix_world @ v.co for v in entry.object.data.vertices])
            elif entry.object.original == ob:
                bones = np.array([entry.matrix_world @ b.head for b in entry.object.pose.bones])
        assert points is not None and bones is not None
    else:
        skin = mesh.evaluated_get(graph); rig = ob.evaluated_get(graph)
        points = np.array([skin.matrix_world @ v.co for v in skin.data.vertices])
        bones = np.array([rig.matrix_world @ b.head for b in rig.pose.bones])
    return dict(mesh=points.tolist(), bones=bones.tolist())

def difference(a, b, offset=(0,0,0)):
    import numpy as np
    return max(float(np.max(np.abs(np.array(a[k]) - np.array(b[k]) - offset))) for k in a)

def memberships(ob, mesh):
    return {o.name:sorted(c.name for c in o.users_collection) for o in (ob, mesh)}

def setup(label):
    import bpy, numpy as np
    from mathutils import Vector, Quaternion
    sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
    import b4artists_ml
    from b4artists_ml import motion_layer as m, posing as p, contacts as c, rig_state as rs
    from test_b4artists_ml_contacts import fixture
    b4artists_ml.register()
    ob, source, source_signature, modes = fixture(label, True)
    scene = bpy.context.scene
    names=[b.name for b in ob.data.bones if b.use_deform]
    assert names
    verts=[]
    for name in names:
        point=ob.data.bones[name].head_local
        verts.extend([point,point+Vector((.01,0,0)),point+Vector((0,.01,0))])
    data=bpy.data.meshes.new('Motion test skin');data.from_pydata(verts,[],[tuple(range(i,i+3)) for i in range(0,len(verts),3)])
    mesh=bpy.data.objects.new('Motion test skin',data);scene.collection.objects.link(mesh);mesh.matrix_world=ob.matrix_world.copy()
    for i,name in enumerate(names):mesh.vertex_groups.new(name=name).add(list(range(i*3,i*3+3)),1.,'REPLACE')
    mesh.modifiers.new('Armature','ARMATURE').object=ob
    p._update(ob)
    before = sample(ob,mesh); links=memberships(ob,mesh); world=[list(r) for r in ob.matrix_world]
    action=ob.animation_data.action; signature=c._action_signature(ob); candidate_modes=rs.mode_values(ob)
    started=time.perf_counter(); instance=m.begin(ob,scene); begin_ms=(time.perf_counter()-started)*1000
    p._update(ob); identity_error=difference(sample(ob,mesh,instance),before); assert identity_error < 2e-5, identity_error
    instance.location=(4,-2,3);p._update(ob)
    translated=sample(ob,mesh,instance); translation_error=difference(translated,before,(4,-2,3));assert translation_error < 2e-5,translation_error
    assert not any(o.name in bpy.context.view_layer.objects for o in (ob,mesh))
    control=ob.pose.bones[p.bindings(ob)[2][0]['fk'][0]]
    old_basis=control.matrix_basis.copy();control.matrix_basis=old_basis @ Quaternion((1,0,0),.1).to_matrix().to_4x4();p._update(ob)
    edit_delta=difference(sample(ob,mesh,instance),translated);assert edit_delta > 1e-5,edit_delta
    control.matrix_basis=old_basis;p._update(ob);edit_restore_error=difference(sample(ob,mesh,instance),translated);assert edit_restore_error < 2e-5
    m.keep(ob)
    expected={}
    for frame in (1.,2.137,6.,8.713,11.):
        scene.frame_set(int(frame),subframe=frame%1);p._update(ob);expected[str(frame)]=sample(ob,mesh,instance)
    assert ob.animation_data.action==action, "Action changed"
    assert c._action_signature(ob)==signature, "Curves changed"
    assert rs.mode_values(ob)==candidate_modes, "Candidate rig modes changed"
    assert [list(r) for r in ob.matrix_world]==world
    scene.frame_set(6);p._update(ob)
    report=dict(passed=True,label=label,scene=scene.name,owner=ob.name,mesh=mesh.name,instance=instance.name,original_links=links,original_world=world,action=action.name,source_action=source.name,source_bones=len(ob.data.bones),weighted_deform_bones=len(names),identity_error=identity_error,translation_error=translation_error,control_edit_delta=edit_delta,control_restore_error=edit_restore_error,begin_ms=begin_ms,expected_samples=expected,expected_recovered=before,module_sha256=hashlib.sha256((ROOT/'b4artists_ml/motion_layer.py').read_bytes()).hexdigest())
    bpy.ops.wm.save_as_mainfile(filepath=str(path(label,'.blend')))
    path(label,'-setup.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('expected_samples','expected_recovered')}),flush=True)

def verify(label):
    import bpy
    meta=json.loads(path(label,'-setup.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(path(label,'.blend')),use_scripts=False)
    scene=bpy.data.scenes[meta['scene']];bpy.context.window.scene=scene
    ob=bpy.data.objects[meta['owner']];mesh=bpy.data.objects[meta['mesh']];instance=bpy.data.objects[meta['instance']]
    assert 'b4artists_ml' not in sys.modules
    errors=[]
    for frame,expected in reversed(list(meta['expected_samples'].items())):
        frame=float(frame);scene.frame_set(int(frame),subframe=frame%1);bpy.context.view_layer.update();errors.append(difference(sample(ob,mesh,instance),expected))
    assert max(errors) < 2e-5,errors
    # Only the ownership module is imported for explicit recovery; playback above was addon-free.
    sys.path.insert(0,str(ROOT));from b4artists_ml import motion_layer as m
    assert m.source(instance,scene)==ob and m.validate(ob)==instance
    scene.frame_set(6);bpy.context.view_layer.update();started=time.perf_counter();m.restore(ob);bpy.context.view_layer.update();restore_ms=(time.perf_counter()-started)*1000
    assert memberships(ob,mesh)==meta['original_links']
    assert [list(r) for r in ob.matrix_world]==meta['original_world']
    assert ob.animation_data.action.name==meta['action'] and bpy.data.actions.get(meta['source_action']) is not None
    recovery_error=difference(sample(ob,mesh),meta['expected_recovered']);assert recovery_error<2e-5,recovery_error
    result=dict(passed=True,label=label,addon_free_playback=True,max_reload_error=max(errors),fresh_recovery_error=recovery_error,restore_ms=restore_ms,original_memberships_restored=True,original_actions_retained=True,blend_sha256=hashlib.sha256(path(label,'.blend').read_bytes()).hexdigest(),scope='Generated rigs and synthetic deform-bound triangles; no animator UI or production character coverage claimed.')
    path(label,'-verify.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)

def main():
    rows=[]
    for label in RIGS:
        for mode in ('setup','verify'):
            if path(label,'-'+mode+'.json').exists():raise RuntimeError('Evidence already exists')
            started=time.perf_counter()
            with path(label,'-'+mode+'.log').open('w') as log:
                process=subprocess.run(['X:/5.1.0/bforartists.exe','--background','--factory-startup','--disable-autoexec','--python',str(HERE),'--',mode,label],stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4'),timeout=240)
            result=path(label,'-'+mode+'.json')
            rows.append(dict(label=label,stage=mode,exit_code=process.returncode,seconds=time.perf_counter()-started,assertions_passed=result.exists() and json.loads(result.read_text()).get('passed') is True))
            path('all','-process.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows[-1]),flush=True)
            if not rows[-1]['assertions_passed']:return
if __name__=='__main__':
    if '--' in sys.argv:
        mode,label=sys.argv[sys.argv.index('--')+1:];(setup if mode=='setup' else verify)(label)
    else:main()
