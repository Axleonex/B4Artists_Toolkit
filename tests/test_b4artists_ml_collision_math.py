"""Static planar collision response for finite rigid mass segments."""
from pathlib import Path
import os,sys,unittest,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]
import numpy as np
from b4artists_ml import collision_math as cm


class CollisionMathTests(unittest.TestCase):
    def geometry(self):
        centers=np.array([[0.,0.,.4],[2.,0.,1.]])
        orientations=np.repeat(np.eye(3)[None,:,:],2,axis=0)
        lengths=np.array([1.,2.]);radii=np.array([.2,.1])
        return centers,orientations,lengths,radii

    def test_ellipsoid_extent_uses_orientation_and_artist_radius(self):
        centers,orientations,lengths,radii=self.geometry()
        separation=cm.segment_separations(centers,orientations,lengths,radii,[0,0,0],[0,0,4])
        np.testing.assert_allclose(separation,[.2,.8])
        rotation=np.array([[1.,0.,0.],[0.,0.,-1.],[0.,1.,0.]])
        orientations[0]=rotation
        self.assertAlmostEqual(cm.segment_separations(centers,orientations,lengths,radii,[0,0,0],[0,0,1])[0],-.1)

    def test_full_and_partial_response_with_bounded_surface_mask(self):
        centers,orientations,lengths,radii=self.geometry();centers[0,2]=.1
        full=cm.correction(centers,orientations,lengths,radii,[0,0,0],[0,0,1],clearance=.05,strength=1.)
        self.assertAlmostEqual(full['required_lift'],.15);self.assertAlmostEqual(full['remaining_penetration'],0.)
        np.testing.assert_allclose(full['vector'],[0,0,.15])
        partial=cm.correction(centers,orientations,lengths,radii,[0,0,0],[0,0,1],clearance=.05,strength=.25)
        self.assertAlmostEqual(partial['applied_lift'],.0375);self.assertAlmostEqual(partial['remaining_penetration'],.1125)
        excluded=cm.correction(centers,orientations,lengths,radii,[0,0,0],[0,0,1],clearance=.05,inside=[False,True])
        self.assertEqual(excluded['participating_segments'],1);self.assertEqual(excluded['required_lift'],0.)

    def test_plane_normal_is_normalized_and_invalid_inputs_fail_closed(self):
        centers,orientations,lengths,radii=self.geometry()
        a=cm.correction(centers,orientations,lengths,radii,[0,0,0],[0,0,1],clearance=.25)
        b=cm.correction(centers,orientations,lengths,radii,[0,0,0],[0,0,8],clearance=.25)
        np.testing.assert_allclose(a['vector'],b['vector'])
        bad=[
            lambda:cm.plane([0,0,0],[0,0,0]),
            lambda:cm.correction(centers,orientations,lengths,radii,[0,0,0],[0,0,1],strength=1.1),
            lambda:cm.correction(centers,orientations,[1,0],radii,[0,0,0],[0,0,1]),
            lambda:cm.segment_separations(centers,orientations,lengths,radii,[0,0,0],[0,0,1],[True]),
        ]
        for call in bad:
            with self.assertRaises(ValueError):call()

    def test_contact_impulse_absorbs_only_the_plane_normal_component(self):
        full=cm.contact_transition_delta([1.,2.,-3.],[0,0,4],1.)
        np.testing.assert_allclose(full['corrected'],[1.,2.,0.])
        np.testing.assert_allclose(full['absorbed'],[0.,0.,-3.])
        partial=cm.contact_transition_delta([1.,2.,-3.],[0,0,1],.25)
        np.testing.assert_allclose(partial['corrected'],[1.,2.,-2.25])
        np.testing.assert_allclose(partial['absorbed'],[0.,0.,-.75])
        with self.assertRaises(ValueError):cm.contact_transition_delta([1,2],[0,0,1],1.)
        with self.assertRaises(ValueError):cm.contact_transition_delta([1,2,3],[0,0,1],-1.)

try:import bpy
except ImportError:bpy=None


@unittest.skipIf(bpy is None,'Requires actual Bforartists')
class CollisionHostTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import b4artists_ml;b4artists_ml.register()

    def fixture(self,label='boneforge'):
        from test_b4artists_ml_flight import fixture
        return fixture(label,True)

    def minimum_and_com(self,obj,frame,normal):
        from b4artists_ml import native_flight as native,support,contacts,posing,angular_math as am
        from b4artists_ml.support_math import center_of_mass
        scene=bpy.context.scene;contacts._frame(scene,frame);posing._update(obj)
        binding=support.body_solver.mapping(obj,writable=False);evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        a,b,hints=native._segment_geometry(evaluated,binding['names']);weights=[i.weight for i in obj.b4ml.mass_segments];fractions=[i.fraction for i in obj.b4ml.mass_segments]
        com,centers,_=center_of_mass(a,b,weights,fractions);orientations=am.segment_orientations(a,b,hints);lengths=np.linalg.norm(b-a,axis=1);radii=[i.inertia_radius for i in obj.b4ml.mass_segments]
        separations=cm.segment_separations(centers,orientations,lengths,radii,[0,0,0],normal)
        scale=max(float(sum(lengths[:3])),1e-8)
        return float(min(separations)),com,scale

    def configure_ceiling(self,obj):
        from b4artists_ml import flight_math as fm
        scene=bpy.context.scene;row=obj.b4ml.flights[0];duration=(row.end-row.start)*scene.render.fps_base/scene.render.fps;gravity=scene.gravity if scene.use_gravity else [0,0,0]
        candidates=[]
        for normal in (np.array(v,dtype=float) for v in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))):
            start,a,scale=self.minimum_and_com(obj,row.start,normal);end,b,_=self.minimum_and_com(obj,row.end,normal);endpoint=min(start,end);interior=[]
            for frame in np.linspace(row.start,row.end,max(5,int((row.end-row.start)*4)+1))[1:-1]:
                minimum,source,_=self.minimum_and_com(obj,float(frame),normal);u=(frame-row.start)/(row.end-row.start)
                wanted=fm.trajectory(a,b,[u],duration,gravity)[0];interior.append(minimum+float(np.dot(wanted-source,normal)))
            candidates.append((endpoint-min(interior),normal,endpoint,min(interior),scale))
        excursion,normal,endpoint,interior,scale=max(candidates,key=lambda value:value[0])
        self.assertGreater(excursion,scale*.002)
        threshold=(endpoint+interior)*.5;point=normal*threshold
        obj.b4ml.support_plane_point=point;obj.b4ml.support_plane_normal=normal
        row.collision_clearance=0.;row.collision_strength=1.;obj.b4ml.flight_backend='NATIVE'
        return scale

    def test_real_rig_ceiling_response_is_editable_reversible_and_clear(self):
        from b4artists_ml import flight as f,motion_layer as m,workflow as w,contacts as contacts
        obj,source,signature,*_=self.fixture();scene=bpy.context.scene;candidate=obj.b4ml.candidate_action;scale=self.configure_ceiling(obj)
        report=f.solve(obj,scene);instance=m.validate(obj);metric=report['intervals'][0]['collision_response']
        self.assertEqual(report['backend'],'native_instance_com_collision_v1');self.assertGreater(metric['max_penetration_before'],scale*.005)
        self.assertLessEqual(metric['max_penetration_after'],scale*2e-4);self.assertTrue(metric['priority_poses_preserved'])
        curves=w.action_curves(instance.animation_data.action,getattr(instance.animation_data,'action_slot',None))
        self.assertTrue(any(fc.data_path.startswith('["b4ml_residual_') and all(key.interpolation=='LINEAR' for key in fc.keyframe_points) for fc in curves))
        for frame in (obj.b4ml.flights[0].start,obj.b4ml.flights[0].end):
            contacts._frame(scene,frame);self.assertLess(np.linalg.norm(instance.location),2e-5)
        self.assertIs(obj.animation_data.action,candidate);f.restore(obj,scene);w.finish_preview(obj,scene,False);self.assertEqual(contacts._action_signature(obj),signature)

    def test_settings_cancel_and_root_backend_fail_closed(self):
        from b4artists_ml import flight as f,motion_layer as m
        obj,*_=self.fixture();scene=bpy.context.scene;self.configure_ceiling(obj);token=f._curve_token(obj)
        f.start(obj,scene);self.assertFalse(f.step(obj));obj.b4ml.support_plane_point.z+=.01
        with self.assertRaisesRegex(ValueError,'changed'):f.step(obj)
        self.assertIsNone(m.find(obj));self.assertEqual(f._curve_token(obj),token)
        obj.b4ml.flight_backend='ROOT'
        with self.assertRaisesRegex(ValueError,'collision response requires Native Motion Layer'):f.solve(obj,scene)

    def test_collision_result_keep_reload_preview_and_discard(self):
        from b4artists_ml import flight as f,motion_layer as m,workflow as w,contacts
        obj,source,signature,*_=self.fixture();scene=bpy.context.scene;self.configure_ceiling(obj);f.solve(obj,scene);instance=m.validate(obj)
        frames=np.linspace(obj.b4ml.flights[0].start,obj.b4ml.flights[0].end,9);expected=[]
        for frame in frames:
            contacts._frame(scene,float(frame));expected.append(np.array(instance.location))
        name=obj.name;w.finish_preview(obj,scene,True);w.restore_kept_source(obj,scene);result=m.results(obj)[-1];result_name=result.name
        with tempfile.TemporaryDirectory() as directory:
            path=str(Path(directory)/'collision-result.blend');bpy.ops.wm.save_as_mainfile(filepath=path);bpy.ops.wm.open_mainfile(filepath=path,use_scripts=False)
            obj=bpy.data.objects[name];scene=bpy.context.scene;bpy.context.window.scene=scene;result=bpy.data.objects[result_name];w.preview_motion_result(obj,scene,result);instance=m.validate(obj)
            for frame,wanted in zip(frames,expected):contacts._frame(scene,float(frame));np.testing.assert_allclose(instance.location,wanted,atol=2e-5)
            w.finish_preview(obj,scene,False);self.assertEqual(contacts._action_signature(obj),signature)

    def test_rigify_and_combined_angular_c2_collision(self):
        from b4artists_ml import flight as f,workflow as w,motion_layer as m,contacts
        records=[]
        for label,combined in (('rigify_default',False),('boneforge',True)):
            obj,source,signature,*_=self.fixture(label);scene=bpy.context.scene
            if combined:
                w.finish_preview(obj,scene,False);first,last=[item.payload for item in obj.b4ml.anchors];obj.b4ml.anchors.clear()
                for frame,payload in ((1,first),(4,first),(8,last),(11,last)):
                    item=obj.b4ml.anchors.add();item.frame=frame;item.payload=payload
                w.preview(obj,scene);obj.b4ml.flights.clear();row=obj.b4ml.flights.add();row.start=4;row.end=8
                row.takeoff_blend=row.landing_blend=3;row.match_acceleration=True;row.angular_momentum_strength=1.
            scale=self.configure_ceiling(obj);report=f.solve(obj,scene);instance=m.validate(obj);metric=report['intervals'][0]
            self.assertIn('collision_response',metric);self.assertLessEqual(metric['collision_response']['max_penetration_after'],scale*2e-4)
            if combined:
                self.assertEqual(report['backend'],'native_instance_com_angular_collision_v3');self.assertIn('angular_momentum',metric)
                self.assertTrue(all(row['match_acceleration'] and row['normalized_acceleration_jump']<=.1 for row in report['transitions']))
            records.append((label,combined,report['backend']))
            f.restore(obj,scene);w.finish_preview(obj,scene,False);self.assertEqual(contacts._action_signature(obj),signature)
        self.assertEqual(len(records),2)


if __name__=='__main__':unittest.main()
