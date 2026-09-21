"""Persistent native motion ownership: source preservation and failure recovery."""
from pathlib import Path
import sys,json,unittest,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import bpy
import numpy as np
from b4artists_ml import motion_layer as m


def fixture(extra_view=False):
    scene=bpy.data.scenes.new('Motion layer test');bpy.context.window.scene=scene
    parts=bpy.data.collections.new('Original character parts');scene.collection.children.link(parts)
    data=bpy.data.armatures.new('Motion source data');owner=bpy.data.objects.new('Motion source',data)
    scene.collection.objects.link(owner);parts.objects.link(owner)
    bpy.context.view_layer.objects.active=owner;owner.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT');bone=data.edit_bones.new('root');bone.head=(0,0,0);bone.tail=(0,0,1);bpy.ops.object.mode_set(mode='OBJECT')
    verts=[(-.5,-.5,0),(.5,-.5,0),(.5,.5,0),(-.5,.5,0),(-.5,-.5,1),(.5,-.5,1),(.5,.5,1),(-.5,.5,1)]
    mesh_data=bpy.data.meshes.new('Character mesh data');mesh_data.from_pydata(verts,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    mesh=bpy.data.objects.new('Character mesh',mesh_data);parts.objects.link(mesh)
    mesh.modifiers.new('Armature','ARMATURE').object=owner;mesh.vertex_groups.new(name='root').add(list(range(8)),1.,'REPLACE')
    for f,x in ((1,0.),(11,.3)):
        owner.pose.bones['root'].location.x=x;owner.pose.bones['root'].keyframe_insert('location',frame=f)
    scene.frame_set(1);bpy.context.view_layer.update()
    other=bpy.data.objects.new('Unrelated object',None);scene.collection.objects.link(other)
    if extra_view:scene.view_layers.new('Second view')
    return owner,mesh,scene,parts,other


def geometry(mesh,instance=None):
    dep=bpy.context.evaluated_depsgraph_get()
    if instance:
        for entry in dep.object_instances:
            if entry.is_instance and entry.parent and entry.parent.original==instance and entry.object.original==mesh:
                return np.array([entry.matrix_world@v.co for v in entry.object.data.vertices])
        raise AssertionError('Instance mesh missing')
    ob=mesh.evaluated_get(dep);return np.array([ob.matrix_world@v.co for v in ob.data.vertices])


def snapshot(owner,mesh):
    return dict(links={ob:tuple(ob.users_collection) for ob in (owner,mesh)},world=owner.matrix_world.copy(),action=owner.animation_data.action,armature=owner.data,mesh=mesh.data,geometry=geometry(mesh),collections=set(bpy.data.collections),objects=set(bpy.data.objects))


class MotionLayerTests(unittest.TestCase):
    def assert_recovered(self,owner,mesh,before):
        bpy.context.view_layer.update()
        self.assertEqual(owner.matrix_world,before['world']);self.assertIs(owner.animation_data.action,before['action'])
        self.assertIs(owner.data,before['armature']);self.assertIs(mesh.data,before['mesh'])
        for ob,links in before['links'].items():self.assertEqual(set(ob.users_collection),set(links));self.assertNotIn(m._OWNER,ob)
        self.assertFalse(any(k.startswith(m._PREFIX) for k in owner.keys()))
        np.testing.assert_allclose(geometry(mesh),before['geometry'],atol=1e-7)

    def test_begin_keep_restore_preserves_originals(self):
        owner,mesh,scene,parts,other=fixture();before=snapshot(owner,mesh)
        instance=m.begin(owner,scene);self.assertIs(m.find(owner),instance);self.assertIs(m.source(instance,scene),owner)
        self.assertNotIn(owner.name,bpy.context.view_layer.objects)
        instance.location=(4,0,0);bpy.context.view_layer.update()
        np.testing.assert_allclose(geometry(mesh,instance),before['geometry']+[4,0,0],atol=1e-6)
        self.assertIs(m.keep(owner),instance);self.assertEqual(m._read(owner)['phase'],'kept')
        m.restore(owner);self.assert_recovered(owner,mesh,before)
        self.assertEqual(set(bpy.data.collections),before['collections']);self.assertEqual(set(bpy.data.objects),before['objects'])
        self.assertIn(other.name,scene.objects)

    def test_rigid_rotation_is_shared_but_scale_and_parent_fail_closed(self):
        from mathutils import Quaternion
        owner,mesh,scene,*_=fixture();before=snapshot(owner,mesh);instance=m.begin(owner,scene)
        instance.location=(2,-1,3);instance.rotation_mode='QUATERNION';instance.rotation_quaternion=Quaternion((0,0,1),.4);bpy.context.view_layer.update()
        self.assertEqual(m.transform(owner),instance.matrix_world);self.assertIs(m.validate(owner),instance)
        with self.assertRaisesRegex(ValueError,'requires restoring'):m.offset(owner)
        instance.scale.x=2;bpy.context.view_layer.update()
        with self.assertRaisesRegex(ValueError,'without scale'):m.validate(owner)
        instance.scale.x=1;bpy.context.view_layer.update();parent=bpy.data.objects.new('Foreign parent',None);scene.collection.objects.link(parent);instance.parent=parent
        with self.assertRaisesRegex(ValueError,'Unparent'):m.validate(owner)
        instance.parent=None;m.restore(owner);bpy.data.objects.remove(parent,do_unlink=True);self.assert_recovered(owner,mesh,before)

    def test_each_partial_move_failure_recovers(self):
        for failing in (0,1):
            owner,mesh,scene,*_=fixture();before=snapshot(owner,mesh)
            def fail(index):
                if index==failing:raise RuntimeError('Injected partial move failure')
            with self.assertRaisesRegex(RuntimeError,'Injected'):m.begin(owner,scene,_after_move=fail)
            self.assert_recovered(owner,mesh,before)
            self.assertEqual(set(bpy.data.collections),before['collections']);self.assertEqual(set(bpy.data.objects),before['objects'])

    def test_renamed_ids_restore(self):
        owner,mesh,scene,parts,_=fixture();before=snapshot(owner,mesh);instance=m.begin(owner,scene)
        owner.name='Renamed rig';mesh.name='Renamed skin';parts.name='Renamed original collection';instance.name='Renamed result';instance.instance_collection.name='Renamed evaluation collection'
        m.validate(owner);m.restore(owner);self.assert_recovered(owner,mesh,before)

    def test_multiple_view_layers_and_new_layer_guard(self):
        owner,mesh,scene,*_=fixture(True);before=snapshot(owner,mesh);instance=m.begin(owner,scene)
        for layer in scene.view_layers:self.assertTrue(layer.layer_collection.children[instance.instance_collection.name].exclude)
        scene.view_layers.new('New user view')
        with self.assertRaisesRegex(ValueError,'every view layer'):m.validate(owner)
        m.restore(owner);self.assert_recovered(owner,mesh,before)

    def test_saved_kept_layer_and_restore(self):
        owner,mesh,scene,parts,_=fixture();instance=m.begin(owner,scene);instance.location.x=4
        instance.keyframe_insert('location',frame=1);instance.location.x=5;instance.keyframe_insert('location',frame=11);m.keep(owner)
        names=dict(owner=owner.name,mesh=mesh.name,scene=scene.name,parts=parts.name);action_name=instance.animation_data.action.name
        scene.frame_set(6);bpy.context.view_layer.update();expected=geometry(mesh,instance)
        with tempfile.TemporaryDirectory() as td:
            path=str(Path(td)/'motion-recovery.blend');bpy.ops.wm.save_as_mainfile(filepath=path);bpy.ops.wm.open_mainfile(filepath=path,use_scripts=False)
            owner=bpy.data.objects[names['owner']];mesh=bpy.data.objects[names['mesh']];scene=bpy.data.scenes[names['scene']];bpy.context.window.scene=scene
            instance=m.validate(owner);self.assertEqual(m._read(owner)['phase'],'kept');np.testing.assert_array_equal(geometry(mesh,instance),expected)
            m.restore(owner);self.assertIn(owner.name,scene.objects);self.assertIn(mesh.name,bpy.data.collections[names['parts']].objects)
            self.assertTrue(bpy.data.actions[action_name].use_fake_user)

    def test_missing_generated_objects_recover(self):
        for missing in ('instance','group'):
            owner,mesh,scene,*_=fixture();before=snapshot(owner,mesh);instance=m.begin(owner,scene)
            if missing=='instance':bpy.data.objects.remove(instance,do_unlink=True)
            else:bpy.data.collections.remove(instance.instance_collection)
            m.restore(owner);self.assert_recovered(owner,mesh,before)

    def test_foreign_generated_members_and_instances_prevent_deletion(self):
        for kind in ('member','instance'):
            owner,mesh,scene,parts,other=fixture();instance=m.begin(owner,scene);group=instance.instance_collection
            if kind=='member':group.objects.link(other)
            else:
                duplicate=bpy.data.objects.new('Another user instance',None);duplicate.instance_type='COLLECTION';duplicate.instance_collection=group;scene.collection.objects.link(duplicate)
            with self.assertRaises(ValueError):m.restore(owner)
            self.assertIs(m.find(owner),instance);self.assertEqual(set(owner.users_collection),{group})
            if kind=='member':group.objects.unlink(other)
            else:duplicate.instance_collection=None
            m.restore(owner);self.assertIn(other.name,scene.objects)

    def test_extra_user_links_are_preserved(self):
        owner,mesh,scene,*_=fixture();instance=m.begin(owner,scene)
        extra=bpy.data.collections.new('Additional user link');scene.collection.children.link(extra);extra.objects.link(mesh)
        with self.assertRaisesRegex(ValueError,'membership'):m.keep(owner)
        m.restore(owner);self.assertIn(mesh.name,extra.objects)

    def test_invalid_or_missing_original_reference_prevents_partial_restore(self):
        owner,mesh,scene,parts,_=fixture();instance=m.begin(owner,scene);old=owner[m._RECORD]
        corrupt=json.loads(old);corrupt['sources'][1]['links']=['invalid'];owner[m._RECORD]=json.dumps(corrupt)
        with self.assertRaisesRegex(ValueError,'original source collection'):m.restore(owner)
        self.assertEqual(set(owner.users_collection),{instance.instance_collection});owner[m._RECORD]=old
        bpy.data.collections.remove(parts)
        with self.assertRaisesRegex(ValueError,'original source collection'):m.restore(owner)
        replacement=bpy.data.collections.new('Explicit recovery destination');scene.collection.children.link(replacement)
        for key in list(owner.keys()):
            if key.startswith(m._PREFIX+'collection_') and owner.get(key) is None:owner[key]=replacement
        m.restore(owner);self.assertIn(mesh.name,replacement.objects)

    def test_invalid_view_record_fails_before_collection_changes(self):
        owner,mesh,scene,*_=fixture();instance=m.begin(owner,scene);old=owner[m._RECORD]
        for replacement in (None, [{'name':'ViewLayer','selected':[True]}], [{'name':'ViewLayer','selected':[True,'yes']}]):
            value=json.loads(old);value['views']=replacement;owner[m._RECORD]=json.dumps(value)
            with self.assertRaisesRegex(ValueError,'view recovery'):m.restore(owner)
            self.assertEqual(set(owner.users_collection),{instance.instance_collection})
            self.assertEqual(set(mesh.users_collection),{instance.instance_collection})
        owner[m._RECORD]=old;m.restore(owner)

    def test_external_collection_reuse_is_not_deleted(self):
        for kind in ('group','instance'):
            owner,mesh,scene,*_=fixture();instance=m.begin(owner,scene);group=instance.instance_collection
            extra=bpy.data.collections.new('User reuse');scene.collection.children.link(extra)
            if kind=='group':extra.children.link(group)
            else:extra.objects.link(instance)
            with self.assertRaisesRegex(ValueError,'collection'):m.restore(owner)
            self.assertIs(m.find(owner),instance)
            if kind=='group':extra.children.unlink(group)
            else:extra.objects.unlink(instance)
            m.restore(owner)

    def test_child_collections_and_parented_objects_are_protected(self):
        for kind in ('collection', 'parented_object'):
            owner,mesh,scene,parts,other=fixture();instance=m.begin(owner,scene);group=instance.instance_collection
            if kind=='collection':
                child=bpy.data.collections.new('User child collection');group.children.link(child);child.objects.link(other)
            else:other.parent=instance
            for operation in (m.keep,m.restore):
                with self.assertRaises(ValueError):operation(owner)
                self.assertEqual(set(owner.users_collection),{group})
                self.assertIn(other.name,scene.objects)
            if kind=='collection':group.children.unlink(child);scene.collection.children.link(child)
            else:other.parent=None
            m.restore(owner);self.assertIn(other.name,scene.objects)

    def test_invalid_active_reference_fails_before_recovery_mutations(self):
        owner,mesh,scene,*_=fixture();instance=m.begin(owner,scene);saved=owner.get(m._active_key(0))
        owner[m._active_key(0)]='invalid'
        with self.assertRaisesRegex(ValueError,'active object'):m.restore(owner)
        self.assertEqual(set(owner.users_collection),{instance.instance_collection})
        if saved is None:del owner[m._active_key(0)]
        else:owner[m._active_key(0)]=saved
        m.restore(owner)

    def test_preflight_rejects_shared_scene_and_existing_layer(self):
        owner,mesh,scene,*_=fixture();before=snapshot(owner,mesh);other_scene=bpy.data.scenes.new('Other scene');other_scene.collection.objects.link(mesh)
        with self.assertRaisesRegex(ValueError,'only the selected scene'):m.begin(owner,scene)
        self.assertNotIn(m._RECORD,owner);other_scene.collection.objects.unlink(mesh)
        instance=m.begin(owner,scene)
        with self.assertRaisesRegex(ValueError,'existing motion layer'):m.begin(owner,scene)
        self.assertIs(m.find(owner),instance);m.restore(owner);self.assert_recovered(owner,mesh,before)


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MotionLayerTests))
    report=dict(passed=result.wasSuccessful(),tests=result.testsRun,failures=[(t.id(),text) for t,text in result.failures],errors=[(t.id(),text) for t,text in result.errors],module=m.__file__)
    (ROOT/'training/b4artists_ml/results/motion-layer-host-v4.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
