"""Independently authored FBX humanoids; no BoneForge/Rigify builder dependency.
Fixture geometry is authored here under GPL-2.0-or-later, not a production asset.
"""
from pathlib import Path
from importlib import resources
import sys,os,json,unittest,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]
import bpy,addon_utils,numpy as np
from mathutils import Vector,Quaternion
import b4artists_ml
from b4artists_ml import rigs,posing as p,workflow as w,body_solver as solver,body_preview as body,body_live as live
RECORDS=[]
PROFILES=('mocap_humanoid','unity_humanoid','unreal_mannequin')


def _runtime_source_sha256(module):
    """Hash a runtime module whether B4ML_PACKAGE is a directory or ZIP."""
    package_name, _, module_name = module.__name__.rpartition('.')
    if not package_name:
        package_name = module.__package__ or module.__name__
    source = resources.files(package_name).joinpath(module_name + '.py')
    return hashlib.sha256(source.read_bytes()).hexdigest()


def authored(key,variant=0):
    """Construct FK bones directly from body dimensions, then roundtrip through FBX."""
    scene=bpy.data.scenes.new('Imported '+key);bpy.context.window.scene=scene
    roles={v:k for k,v in rigs.source_maps()[key]['bones'].items()}
    leg=1.+.17*variant;arm=.65-.07*variant;torso=.6+.08*variant
    z=leg;h={'hips':(0,0,z),'spine.01':(0,0,z+.14),'spine.02':(0,0,z+.28),
        'chest':(0,0,z+torso*.7),'neck':(0,0,z+torso),'head':(0,0,z+torso+.16)}
    parents={'hips':'FixtureRoot','spine.01':'hips','spine.02':'spine.01','chest':'spine.02','neck':'chest','head':'neck'}
    for side,sign in (('L',1),('R',-1)):
        for role,pt,parent in (
            ('clavicle',(.07,0,z+torso*.72),'chest'),
            ('upperarm',(.23,0,z+torso*.72),'clavicle.fk-'+side),
            ('forearm',(.23+arm*.52,-.07,z+torso*.61),'upperarm.fk-'+side),
            ('hand',(.23+arm,-.015,z+torso*.49),'forearm.fk-'+side),
            ('thigh',(.13,0,z),'hips'),('shin',(.13,-.065,leg*.51),'thigh.fk-'+side),
            ('foot',(.13,0,.12),'shin.fk-'+side)):
            name=role+'.fk-'+side;h[name]=(sign*pt[0],pt[1],pt[2]);parents[name]=parent
    data=bpy.data.armatures.new('AuthoredFK');ob=bpy.data.objects.new('ImportedHumanoid',data);scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
    root=data.edit_bones.new('FixtureRoot');root.head=(0,0,0);root.tail=(0,0,.15);root.use_deform=False
    for i,(role,point) in enumerate(h.items()):
        bone=data.edit_bones.new(roles[role]);bone.head=point
        children=[n for n in h if parents[n]==role]
        if children:bone.tail=h[children[0]]
        elif role=='head':bone.tail=Vector(point)+Vector((0,0,.18))
        elif role.startswith('hand'):bone.tail=Vector(point)+Vector((.13 if role.endswith('L') else -.13,0,0))
        else:bone.tail=Vector(point)+Vector((0,-.19,-.03))
        bone.roll=(i%5-2)*(.13+.06*variant)
    for role,parent in parents.items():
        bone=data.edit_bones[roles[role]];bone.parent=data.edit_bones[roles.get(parent,parent)]
        bone.use_connect=False
    extra=data.edit_bones.new('Accessory');extra.head=(0,.08,z+torso);extra.tail=(0,.2,z+torso);extra.parent=data.edit_bones[roles['chest']]
    bpy.ops.object.mode_set(mode='OBJECT')
    verts=[];faces=[];weights=[]
    for bone in data.bones:
        if not bone.use_deform:continue
        i=len(verts);point=bone.head_local;verts.extend([point,point+Vector((.017,0,0)),point+Vector((0,.019,0))]);faces.append((i,i+1,i+2));weights.append((bone.name,[i,i+1,i+2]))
    md=bpy.data.meshes.new('AuthoredSurface');md.from_pydata(verts,[],faces);mesh=bpy.data.objects.new('BoundSurface',md);scene.collection.objects.link(mesh)
    for name,indices in weights:mesh.vertex_groups.new(name=name).add(indices,1.,'REPLACE')
    for side in ('L','R'):
        name=roles['forearm.fk-'+side];indices=next(v for n,v in weights if n==name)
        mesh.vertex_groups[name].add(indices,.6,'REPLACE')
        mesh.vertex_groups[roles['upperarm.fk-'+side]].add(indices,.4,'REPLACE')
    mesh.modifiers.new('Deformation','ARMATURE').object=ob;mesh.parent=ob
    mesh.select_set(True);p._update(ob)
    before={n:tuple(ob.matrix_world@ob.pose.bones[n].head) for n in roles.values()}
    folder=ROOT/'training/b4artists_ml/cache';path=folder/(os.environ.get('B4ML_RUN_LABEL','imported-development')+'-authored-'+key+'-'+str(variant)+'-'+str(len(RECORDS))+'.fbx')
    addon_utils.enable('io_scene_fbx',default_set=False)
    bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False)
    imported_scene=bpy.data.scenes.new('FBX '+key);bpy.context.window.scene=imported_scene
    bpy.ops.import_scene.fbx(filepath=str(path),use_anim=False,automatic_bone_orientation=False)
    ob=next(o for o in imported_scene.objects if o.type=='ARMATURE');mesh=next(o for o in imported_scene.objects if o.type=='MESH')
    assert mesh.find_armature()==ob
    import_error=max((ob.matrix_world@ob.pose.bones[n].head-Vector(v)).length for n,v in before.items())
    assert import_error<1e-4
    for role,parent in parents.items():assert ob.pose.bones[roles[role]].parent.name==roles.get(parent,parent)
    bpy.context.view_layer.objects.active=ob
    if variant:
        ob.location=(.4,-.3,.2);ob.rotation_euler=(.1,-.13,.24);ob.scale=(1.+variant*.15,)*3
    for bone in ob.pose.bones:bone.rotation_mode='QUATERNION'
    # Authored root motion and an independently animated unowned accessory.
    for frame in (1,9,17):
        ob.pose.bones['FixtureRoot'].location=(frame*.012,0,0)
        ob.pose.bones['FixtureRoot'].rotation_quaternion=Quaternion((0,0,1),frame*.007)
        ob.pose.bones['FixtureRoot'].keyframe_insert('location',frame=frame)
        ob.pose.bones['FixtureRoot'].keyframe_insert('rotation_quaternion',frame=frame)
        ob.pose.bones['Accessory'].rotation_quaternion=Quaternion((1,0,0),frame*.005)
        ob.pose.bones['Accessory'].keyframe_insert('rotation_quaternion',frame=frame)
    imported_scene.frame_set(1);p._update(ob)
    RECORDS.append(dict(package_root=os.environ.get('B4ML_PACKAGE',str(ROOT)),loaded_runtime_sha256={Path(m.__file__).name:_runtime_source_sha256(m) for m in (p,w,solver)},fixture=key,variant=variant,format='FBX',file=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bones=len(ob.data.bones),vertices=len(mesh.data.vertices),max_import_head_error=import_error))
    return ob,mesh,roles


def keys(ob,action=None):
    return [(c.data_path,c.array_index,[(tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.interpolation) for k in c.keyframe_points]) for c in w.action_curves(action or ob.animation_data.action,ob.animation_data.action_slot)]


class ImportedHumanoidTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):b4artists_ml.register()
    @classmethod
    def tearDownClass(cls):
        label=os.environ.get('B4ML_RUN_LABEL','imported-development')
        (ROOT/f'training/b4artists_ml/results/{label}-fixtures.json').write_text(json.dumps(RECORDS,indent=2)+'\n')
    def tearDown(self):
        body.reset_runtime()
        for ob in list(bpy.data.objects):
            if ob.type=='ARMATURE' and ob.b4ml.body_payload:body.finish(ob,bpy.context.scene,False)
    def test_imported_whole_body_and_source_recovery(self):
        for i,key in enumerate(PROFILES):
            with self.subTest(profile=key):
                ob,mesh,roles=authored(key,i);source=w.raw_pose(ob);action=ob.animation_data.action;signature=keys(ob)
                self.assertFalse(rigs.detect_rig(ob.data.bones.keys()).missing)
                if os.environ.get('B4ML_EXPECT_IMPORTED_UNSUPPORTED')=='1':
                    with self.assertRaisesRegex(ValueError,'Contextual adapter'):body.begin(ob,bpy.context.scene)
                    self.assertEqual(source,w.raw_pose(ob));self.assertEqual(signature,keys(ob));continue
                s=solver.Session(ob)
                pb=ob.pose.bones[roles['spine.01']];pb.rotation_quaternion=Quaternion((1,0,0),.09)
                pb=ob.pose.bones[roles['forearm.fk-L']];pb.rotation_quaternion=Quaternion((1,0,0),.1)
                p._update(ob);targets=s.world_points(s.points());s.cancel()
                body.begin(ob,bpy.context.scene)
                for index,label in body.TARGETS:ob.b4ml.body_targets[label].target.location=targets[index]
                ob.b4ml.body_influence=0.
                body.solve(ob);record=body._read(ob);self.assertLess(record['metrics']['pin_error'],2e-4)
                self.assertLess(record['metrics']['length_error'],.002)
                self.assertTrue(any(len(v.groups)>1 for v in mesh.data.vertices))
                actual=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
                for vertex in mesh.data.vertices:
                    expected=Vector((0,0,0))
                    for group in vertex.groups:
                        name=mesh.vertex_groups[group.group].name
                        expected+=group.weight*(ob.matrix_world@ob.pose.bones[name].matrix@ob.data.bones[name].matrix_local.inverted()@vertex.co)
                    self.assertLess((actual.matrix_world@actual.data.vertices[vertex.index].co-expected).length,2e-4)
                solved=w.raw_pose(ob);priority_points={1:[tuple(ob.matrix_world@ob.pose.bones[n].head) for n in roles.values()]}
                body.finish(ob,bpy.context.scene,True)
                self.assertEqual(source,w.raw_pose(ob));self.assertEqual(action,ob.animation_data.action);self.assertEqual(signature,keys(ob))
                self.assertEqual(solved['FixtureRoot']['rotation'],source['FixtureRoot']['rotation']);self.assertEqual(solved['Accessory'],source['Accessory'])
                for frame in (9,17):
                    bpy.context.scene.frame_set(frame);w.capture_anchor(ob,bpy.context.scene)
                    priority_points[frame]=[tuple(ob.matrix_world@ob.pose.bones[n].head) for n in roles.values()]
                w.preview(ob,bpy.context.scene)
                for frame in (1,9,17):
                    bpy.context.scene.frame_set(frame)
                    actual_points=np.array([ob.matrix_world@ob.pose.bones[n].head for n in roles.values()])
                    self.assertLess(float(np.max(np.linalg.norm(actual_points-np.array(priority_points[frame]),axis=1))),2e-4)
                    payload=json.loads(next(a for a in ob.b4ml.anchors if a.frame==frame).payload)
                    self.assertIn('FixtureRoot',payload['pose'])
                    for name,row in payload['pose'].items():
                        self.assertLess(solver._angle(Quaternion(w.raw_pose(ob,[name])[name]['rotation']),Quaternion(row['rotation'])),1e-4)
                self.assertEqual(signature,keys(ob,action));w.finish_preview(ob,bpy.context.scene,False)
                self.assertEqual(action,ob.animation_data.action);self.assertEqual(signature,keys(ob))
                RECORDS[-1]['whole_body_metrics']=record['metrics'];RECORDS[-1]['candidate_source_preserved']=True

    def test_dependency_constraints_drivers_and_scale_rejected_before_mutation(self):
        for issue in ('constraint','driver','scale','locked'):
            with self.subTest(issue=issue):
                ob,mesh,roles=authored('unity_humanoid',0);root=ob.pose.bones['FixtureRoot']
                if issue=='constraint':root.constraints.new('LIMIT_LOCATION')
                elif issue=='driver':root.driver_add('location',0).driver.expression='0'
                elif issue=='scale':root.scale=(1,2,1)
                else:root.lock_location=(True,False,False)
                p._update(ob);before=w.raw_pose(ob);objects=set(bpy.data.objects)
                with self.assertRaises(ValueError):body.begin(ob,bpy.context.scene)
                self.assertEqual(before,w.raw_pose(ob));self.assertEqual(objects,set(bpy.data.objects));self.assertFalse(ob.b4ml.body_payload)

    def test_wrong_spine_topology_fails_before_helpers(self):
        ob,mesh,roles=authored('unreal_mannequin',1)
        bpy.ops.object.mode_set(mode='EDIT');ob.data.edit_bones[roles['neck']].parent=ob.data.edit_bones[roles['hips']];bpy.ops.object.mode_set(mode='OBJECT')
        before=w.raw_pose(ob);objects=set(bpy.data.objects)
        with self.assertRaisesRegex(ValueError,'hierarchy'):body.begin(ob,bpy.context.scene)
        self.assertEqual(before,w.raw_pose(ob));self.assertEqual(objects,set(bpy.data.objects))

    def test_changed_dependency_rejected_during_session(self):
        ob,mesh,roles=authored('mocap_humanoid',0);s=solver.Session(ob)
        try:
            before=w.raw_pose(ob);c=ob.pose.bones['FixtureRoot'].constraints.new('LIMIT_LOCATION')
            with self.assertRaisesRegex(ValueError,'constrained'):s._validate()
            ob.pose.bones['FixtureRoot'].constraints.remove(c)
            self.assertEqual(before,w.raw_pose(ob));s._validate()
        finally:s.cancel()

    def test_live_partial_pins_orientation_and_source(self):
        ob,mesh,roles=authored('unity_humanoid',2);before=w.raw_pose(ob);signature=keys(ob)
        body.begin(ob,bpy.context.scene);ob.b4ml.body_influence=0.
        head=ob.b4ml.body_targets['Head'];head.enabled=False;head.use_orientation=True
        goal=head.target.rotation_quaternion.copy()@Quaternion((0,0,1),.12);head.target.rotation_quaternion=goal
        ob.b4ml.body_targets['Hand L'].enabled=False
        ob.b4ml.body_targets['Foot L'].use_pole=True
        live.start(ob,now=0.)
        for i in range(3000):
            result=live.tick(ob,now=.2+i*.03)
            if result in ('ready','idle'):break
        else:self.fail('Imported live fit did not finish')
        self.assertLess(solver._angle(goal,ob.matrix_world.to_quaternion()@ob.pose.bones[roles['head']].matrix.to_quaternion()),.001)
        body.finish(ob,bpy.context.scene,True)
        self.assertEqual(w.raw_pose(ob),before);self.assertEqual(keys(ob),signature);self.assertFalse(live._WATCHERS)

    def test_pending_preview_save_reload_keep_and_restore(self):
        ob,mesh,roles=authored('unreal_mannequin',1);name=ob.name;source=w.raw_pose(ob);signature=keys(ob)
        body.begin(ob,bpy.context.scene);ob.b4ml.body_influence=0.;body.solve(ob)
        path=ROOT/('training/b4artists_ml/cache/'+os.environ.get('B4ML_RUN_LABEL','imported-development')+'-pending.blend')
        bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.wm.open_mainfile(filepath=str(path))
        ob=bpy.data.objects[name];body.finish(ob,bpy.context.scene,True)
        self.assertEqual(w.raw_pose(ob),source);self.assertEqual(keys(ob),signature);self.assertEqual(len(ob.b4ml.anchors),1)

    def test_support_native_motion_and_editable_source_recovery(self):
        from b4artists_ml import support,contacts,flight,motion_layer
        for i,key in enumerate(PROFILES):
            with self.subTest(profile=key):
                ob,mesh,roles=authored(key,i);scene=bpy.context.scene;action=ob.animation_data.action;signature=keys(ob)
                for frame in (1,9,17):scene.frame_set(frame);w.capture_anchor(ob,scene)
                w.preview(ob,scene);scene.frame_set(1);support.initialize(ob)
                contact=contacts.capture(ob,scene);self.assertEqual(contact.start,1.)
                analysis=support.analyze(ob,scene,bpy.context.evaluated_depsgraph_get())
                self.assertEqual(len(analysis['segments']),17);self.assertTrue(np.isfinite(analysis['com']).all())
                ob.b4ml.contacts.clear();item=flight.add(ob,scene);item.start=1;item.end=9;ob.b4ml.flight_backend='NATIVE'
                flight.start(ob,scene)
                for _ in range(3000):
                    if flight.step(ob):break
                else:self.fail('Imported native flight did not finish')
                self.assertIsNotNone(motion_layer.find(ob));self.assertEqual(signature,keys(ob,action))
                metrics=json.loads(ob.b4ml.flight_metrics)
                self.assertLess(max(row['acceleration_error_p95'] for row in metrics['intervals']),.1)
                instance=motion_layer.validate(ob);dep=bpy.context.evaluated_depsgraph_get()
                self.assertTrue(any(e.is_instance and e.parent and e.parent.original==instance and e.object.original==mesh for e in dep.object_instances))
                w.finish_preview(ob,scene,True);w.restore_kept_source(ob,scene)
                self.assertEqual(action,ob.animation_data.action);self.assertEqual(signature,keys(ob));self.assertIsNone(motion_layer.find(ob))
                self.assertTrue(motion_layer.results(ob));self.assertIn(mesh,bpy.context.scene.objects.values())
                RECORDS[-1]['native_flight_metrics']=metrics

    def test_learned_completion_with_active_joint_limits(self):
        from b4artists_ml import joint_limits as limits
        for i,key in enumerate(PROFILES):
            with self.subTest(profile=key):
                ob,mesh,roles=authored(key,i);s=solver.Session(ob);before=w.raw_pose(ob)
                try:
                    targets=s.world_points(s.baseline);mask=np.zeros(17,bool);mask[0]=True
                    names=[roles['forearm.fk-'+side] for side in ('L','R')]
                    request={n:dict(swing=.03,twist_min=-.5,twist_max=.5) for n in names}
                    result=s.solve(targets,mask,learned_influence=1.,rotation_limits=request,iterations=80)
                    self.assertGreater(result['neural_residual_norm'],1e-5)
                    self.assertLess(result['pin_error'],2e-4);self.assertLess(result['joint_limit_error_radians'],.001)
                    for n,limit in request.items():self.assertLess(max(abs(limits.residual(solver._quat(ob.pose.bones[n]),limit))),.001)
                    RECORDS[-1]['limited_learned_metrics']={k:v for k,v in result.items() if k!='points'}
                finally:s.cancel()
                self.assertEqual(before,w.raw_pose(ob))

    def test_contact_correction_preserves_unowned_animation(self):
        from b4artists_ml import contacts
        for i,key in enumerate(PROFILES):
            with self.subTest(profile=key):
                ob,mesh,roles=authored(key,i);scene=bpy.context.scene;source=ob.animation_data.action;signature=keys(ob)
                for frame in (1,9,17):scene.frame_set(frame);w.capture_anchor(ob,scene)
                w.preview(ob,scene);scene.frame_set(5)
                ob.b4ml.contact_limb='leg-L';item=contacts.capture(ob,scene);item.start=4;item.end=7;item.blend=1.;item.lock_rotation=False
                original=ob.animation_data.action;unowned=[row for row in keys(ob) if 'Accessory' in row[0]]
                report=contacts.solve(ob,scene);self.assertLess(report['max_after'],2e-4)
                self.assertEqual(unowned,[row for row in keys(ob) if 'Accessory' in row[0]])
                self.assertEqual(signature,keys(ob,source));self.assertNotEqual(original,ob.animation_data.action)
                w.finish_preview(ob,scene,True);w.restore_kept_source(ob,scene)
                self.assertEqual(source,ob.animation_data.action);self.assertEqual(signature,keys(ob))
                RECORDS[-1]['contact_metrics']=report

    def test_ordinary_anchor_capture_retains_unsupported_limb_topology(self):
        ob,mesh,roles=authored('unity_humanoid',0)
        bpy.ops.object.mode_set(mode='EDIT');ob.data.edit_bones[roles['forearm.fk-L']].parent=ob.data.edit_bones[roles['hips']];bpy.ops.object.mode_set(mode='OBJECT')
        before=w.raw_pose(ob);signature=keys(ob)
        self.assertGreater(w.capture_anchor(ob,bpy.context.scene),0)
        self.assertEqual(before,w.raw_pose(ob));self.assertEqual(signature,keys(ob))
        with self.assertRaises(ValueError):body.begin(ob,bpy.context.scene)

    def test_ordinary_anchor_capture_retains_partial_imported_profile(self):
        ob,mesh,roles=authored('unity_humanoid',0);ob.data.bones[roles['hips']].name='UnmappedHips'
        before=w.raw_pose(ob);signature=keys(ob)
        self.assertGreater(w.capture_anchor(ob,bpy.context.scene),0)
        self.assertEqual(before,w.raw_pose(ob));self.assertEqual(signature,keys(ob))
        with self.assertRaises(ValueError):body.begin(ob,bpy.context.scene)

    def test_legacy_limb_pose_uses_connected_pelvis_ancestor(self):
        for i,key in enumerate(PROFILES):
            with self.subTest(profile=key):
                ob,mesh,roles=authored(key,i);source=w.raw_pose(ob);signature=keys(ob)
                p.begin(ob,bpy.context.scene);ob.b4ml.pose_offset=(.005,0,0)
                rows=p.solve(ob,bpy.context.scene)
                self.assertTrue(rows);self.assertLess(max(r['residual'] for r in rows),2e-4)
                p.finish(ob,bpy.context.scene,True)
                # Legacy direct-FK Keep intentionally leaves the solved pose visible.
                self.assertEqual(signature,keys(ob))
                anchor=json.loads(ob.b4ml.anchors[0].payload)['pose'];self.assertIn('FixtureRoot',anchor)
                self.assertEqual(anchor,json.loads(json.dumps(w.raw_pose(ob,anchor))))
                w.restore_pose(ob,source);p._update(ob)
                p.begin(ob,bpy.context.scene);ob.b4ml.pose_offset=(.006,0,0);p.solve(ob,bpy.context.scene);p.finish(ob,bpy.context.scene,False)
                self.assertEqual(source,w.raw_pose(ob));self.assertEqual(signature,keys(ob))
