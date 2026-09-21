"""Independent derivative, collision, actual-rig and recovery checks."""
from pathlib import Path
import sys,os,json,math,unittest,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[os.environ.get('B4ML_PACKAGE',str(ROOT)),str(ROOT/'tests')]
import numpy as np
from b4artists_ml import flight_math as fm

class MomentumMathTests(unittest.TestCase):
    def test_endpoint_velocity_units_and_cubic_handles(self):
        v=np.array([2.,-3.,.5]);duration=2.3;eps=1e-5
        for landing in (False,True):
            f=lambda t:fm.transition_offset(t,duration,v,landing)
            np.testing.assert_array_equal(f([0,1]),np.zeros((2,3)))
            derivative0=(-3*f([0])[0]+4*f([eps])[0]-f([2*eps])[0])/(2*eps*duration)
            derivative1=(3*f([1])[0]-4*f([1-eps])[0]+f([1-2*eps])[0])/(2*eps*duration)
            np.testing.assert_allclose(derivative0,v if landing else 0,atol=1e-8)
            np.testing.assert_allclose(derivative1,0 if landing else v,atol=1e-8)
            a,b=fm.cubic_controls(f([0,1/3,2/3,1]));t=np.linspace(0,1,51)[:,None]
            np.testing.assert_allclose(3*(1-t)**2*t*a+3*(1-t)*t*t*b,f(t[:,0]),atol=1e-14)
    def test_span_validation_contact_priority_and_overlap(self):
        row=dict(start=4.,end=8.,strength=1.,takeoff_blend=3.,landing_blend=3.)
        self.assertEqual(len(fm.transition_spans([row],[1,4,8,11],[])),2)
        for bad in (-1,float('nan'),.5,4):
            with self.assertRaises(ValueError):fm.transition_spans([dict(row,takeoff_blend=bad)],[1,4,8,11],[])
        with self.assertRaisesRegex(ValueError,'priority'):fm.transition_spans([row],[1,2,4,8,11],[])
        with self.assertRaisesRegex(ValueError,'contact'):fm.transition_spans([row],[1,4,8,11],[dict(start=1,end=2,blend=0,strength=1)])
        with self.assertRaisesRegex(ValueError,'overlap'):fm.transition_spans([dict(start=4,end=5,landing_blend=4),dict(start=9,end=10,takeoff_blend=4)],[1,4,5,9,10,14],[])

    def test_collision_landing_allows_only_endpoint_contact_through_transition(self):
        row=dict(start=4,end=8,strength=1,angular_momentum_strength=0,
                 contact_impulse_strength=1,collision_strength=0,collision_clearance=0,
                 takeoff_blend=0,landing_blend=3)
        contact=dict(start=8,end=11,blend=2,strength=1)
        self.assertEqual(len(fm.validate([row],[1,4,8,11],[contact])),1)
        spans=fm.transition_spans([row],[1,4,8,11],[contact])
        self.assertEqual([(item['start'],item['end'],item['landing']) for item in spans],[(8,11,True)])
        for bad in (dict(contact,start=7),dict(contact,start=9),dict(contact,end=10)):
            with self.assertRaisesRegex(ValueError,'contact'):
                fm.transition_spans([row],[1,4,8,11],[bad])
    def test_invalid_offsets(self):
        for u,d in [([-.1],1),([1.1],1),([float('nan')],1),([.5],0)]:
            with self.assertRaises(ValueError):fm.transition_offset(u,d,[1,2,3])
    def test_c2_transition_matches_boundary_velocity_and_acceleration(self):
        velocity=np.array([2.,-3.,.5]);acceleration=np.array([4.,1.,-2.]);duration=2.3;eps=1e-4
        for landing in (False,True):
            spline=fm.transition_c2_spline(duration,velocity,acceleration,landing)
            value=lambda u:fm.transition_c2_values(spline,[u])[0]
            boundary=0. if landing else 1.;outer=1. if landing else 0.;side=1. if landing else -1.
            derivative=side*(-3*value(boundary)+4*value(boundary+side*eps)-value(boundary+side*2*eps))/(2*eps*duration)
            second=(2*value(boundary)-5*value(boundary+side*eps)+4*value(boundary+side*2*eps)-value(boundary+side*3*eps))/(eps*duration)**2
            np.testing.assert_allclose(value(boundary),0,atol=1e-12);np.testing.assert_allclose(value(outer),0,atol=1e-12)
            np.testing.assert_allclose(derivative,velocity,atol=1e-7);np.testing.assert_allclose(second,acceleration,atol=1e-6)
            outer_side=-side
            outer_velocity=outer_side*(-3*value(outer)+4*value(outer+outer_side*eps)-value(outer+outer_side*2*eps))/(2*eps*duration)
            outer_acceleration=(2*value(outer)-5*value(outer+outer_side*eps)+4*value(outer+outer_side*2*eps)-value(outer+outer_side*3*eps))/(eps*duration)**2
            np.testing.assert_allclose(outer_velocity,0,atol=1e-7);np.testing.assert_allclose(outer_acceleration,0,atol=1e-6)
            coefficients=spline['coefficients'];width=1/3
            def endpoint(piece,x,order):
                terms=np.array([0 if power<order else math.factorial(power)/math.factorial(power-order)*x**(power-order) for power in range(4)])
                return terms@coefficients[piece]
            for piece in (0,1):
                for order in range(3):np.testing.assert_allclose(endpoint(piece,width,order),endpoint(piece+1,0,order),atol=1e-12)
        with self.assertRaises(ValueError):fm.transition_c2_spline(0,velocity,acceleration)
        with self.assertRaises(ValueError):fm.transition_c2_values(fm.transition_c2_spline(1,velocity,acceleration),[1.1])

try:import bpy
except ImportError:bpy=None

@unittest.skipIf(bpy is None,'Requires actual Bforartists')
class MomentumHostTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import b4artists_ml;b4artists_ml.register()
    def fixture(self,label='boneforge',strength=1.,shift=0.,match_acceleration=False,angular=0.):
        from test_b4artists_ml_flight import fixture
        from b4artists_ml import workflow as w,flight as f
        ob,source,sig,modes=fixture(label,True);scene=bpy.context.scene
        w.finish_preview(ob,scene,False);first,last=[i.payload for i in ob.b4ml.anchors];ob.b4ml.anchors.clear()
        for frame,payload in [(1,first),(4,first),(8,last),(11,last)]:
            item=ob.b4ml.anchors.add();item.frame=frame+shift;item.payload=payload
        w.preview(ob,scene);ob.b4ml.flights.clear();row=ob.b4ml.flights.add();row.start=4+shift;row.end=8+shift;row.takeoff_blend=row.landing_blend=2.7 if shift==.137 else 3;row.strength=strength;row.match_acceleration=match_acceleration;row.angular_momentum_strength=angular;ob.b4ml.flight_backend='NATIVE'
        return ob,source,sig,modes
    def test_actual_rigs_continuity_and_editable_recovery(self):
        from b4artists_ml import flight as f,workflow as w,motion_layer as m,contacts as c
        from test_b4artists_ml_flight import com
        records=[]
        for label,strength,shift,match_acceleration in [('boneforge',1.,0.,False),('rigify_default',1.,0.,False),('boneforge',.5,.25,False),('boneforge',0.,0.,False),('boneforge',1.,.137,False)]:
            ob,source,sig,modes=self.fixture(label,strength,shift,match_acceleration);scene=bpy.context.scene;candidate=ob.b4ml.candidate_action;token=f._curve_token(ob)
            times=[.5+shift,1+shift,4+shift,8+shift,11+shift,11.5+shift];before={t:com(ob,t) for t in times}
            report=f.solve(ob,scene);instance=m.validate(ob)
            self.assertEqual(len(report['transitions']),2)
            for row in report['transitions']:
                self.assertLessEqual(row['normalized_jump'],.02)
                if row['before_jump']>.02:self.assertLessEqual(row['after_jump'],row['before_jump']*.1)
                if match_acceleration:
                    self.assertTrue(row['match_acceleration']);self.assertLessEqual(row['normalized_acceleration_jump'],.05)
                    if row['before_acceleration_jump']>.05:self.assertLessEqual(row['after_acceleration_jump'],row['before_acceleration_jump']*.1)
            for t,point in before.items():np.testing.assert_allclose(com(ob,t)+np.array(instance.location),point,atol=2e-5)
            self.assertEqual(f._curve_token(ob),token);self.assertIs(ob.animation_data.action,candidate)
            self.assertGreater(len(w.action_curves(instance.animation_data.action,getattr(instance.animation_data,'action_slot',None))),0)
            records.append(dict(profile=label,strength=strength,shift=shift,match_acceleration=match_acceleration,report=report))
            f.restore(ob,scene);self.assertIsNone(m.find(ob));w.finish_preview(ob,scene,False);self.assertEqual(c._action_signature(ob),sig)
        path=ROOT/('training/b4artists_ml/results/'+os.environ.get('B4ML_RUN_LABEL','momentum')+'-host.json');path.write_text(json.dumps(dict(passed=True,rows=records),indent=2))
    def test_acceleration_continuity_and_source_recovery(self):
        from b4artists_ml import flight as f,workflow as w,motion_layer as m,contacts as c,posing as p
        from test_b4artists_ml_flight import com
        ob,source,sig,*_=self.fixture(match_acceleration=True);scene=bpy.context.scene;candidate=ob.b4ml.candidate_action;token=f._curve_token(ob)
        before={t:com(ob,t) for t in (.5,1,4,8,11,11.5)};report=f.solve(ob,scene);instance=m.validate(ob)
        for row in report['transitions']:
            self.assertTrue(row['match_acceleration']);self.assertLessEqual(row['normalized_jump'],.02);self.assertLessEqual(row['normalized_acceleration_jump'],.1)
            if row['before_jump']>.02:self.assertLessEqual(row['after_jump'],row['before_jump']*.1)
            if row['before_acceleration_jump']>.1:self.assertLessEqual(row['after_acceleration_jump'],row['before_acceleration_jump']*.1)
        for frame,point in before.items():np.testing.assert_allclose(com(ob,frame)+np.array(instance.location),point,atol=2e-5)
        self.assertEqual(f._curve_token(ob),token);self.assertIs(ob.animation_data.action,candidate)
        path=ROOT/('training/b4artists_ml/results/'+os.environ.get('B4ML_RUN_LABEL','momentum')+'-acceleration-host.json')
        path.write_text(json.dumps(dict(passed=True,profile='boneforge',report=report),indent=2))
        f.restore(ob,scene);self.assertIsNone(m.find(ob));w.finish_preview(ob,scene,False);self.assertEqual(c._action_signature(ob),sig)

    def test_landing_contact_impulse_preserves_tangent_and_held_feet(self):
        from b4artists_ml import flight as f,workflow as w,motion_layer as m,contacts as c,posing as p
        from mathutils import Vector
        ob,source,sig,*_=self.fixture(match_acceleration=True);scene=bpy.context.scene
        scene.frame_set(8);p._update(ob);points=[]
        for limb in ('leg-L','leg-R'):
            ob.b4ml.contact_limb=limb;item=c.capture(ob,scene);item.start=8;item.end=11;item.blend=0;points.append(Vector(item.point))
        plane=sum(points,Vector())/len(points);plane.z=min(point.z for point in points)
        ob.b4ml.support_plane_point=plane;ob.b4ml.support_plane_normal=(0,0,1)
        row=ob.b4ml.flights[0];row.contact_impulse_strength=1.;row.collision_strength=0.
        report=f.solve(ob,scene);instance=m.validate(ob);landing=next(item for item in report['transitions'] if item['landing'])
        self.assertEqual(report['backend'],'native_instance_com_contact_impulse_v4')
        self.assertIn('collision_impulse',landing);self.assertLessEqual(landing['normalized_jump'],.02)
        self.assertGreaterEqual(landing['normalized_full_jump'],landing['normalized_jump'])
        self.assertIn('pre_contact_max_penetration_body_fraction',landing['collision_impulse'])
        self.assertTrue(landing['collision_impulse']['contact_stage_required'])
        self.assertEqual(landing['collision_impulse']['participating_contacts'],2)
        f.restore(ob,scene);self.assertIsNone(m.find(ob));w.finish_preview(ob,scene,False);self.assertEqual(c._action_signature(ob),sig)
    def test_angular_momentum_real_rigs_preserve_com_boundaries_and_source(self):
        from b4artists_ml import flight as f,workflow as w,motion_layer as m,contacts as c,posing as p
        records=[]
        for label,c2 in (('boneforge',False),('rigify_default',False),('rigify_default',True)):
            ob,source,sig,*_=self.fixture(label,match_acceleration=c2,angular=1.);scene=bpy.context.scene;candidate=ob.b4ml.candidate_action;token=f._curve_token(ob)
            report=f.solve(ob,scene);instance=m.validate(ob);metric=report['intervals'][0]['angular_momentum']
            self.assertEqual(report['backend'],'native_instance_com_angular_v2');self.assertLess(report['max_after'],2e-4)
            self.assertLess(report['relative_basis_error'],2e-4);self.assertLess(report['rigid_translation_error'],2e-4)
            self.assertLess(metric['endpoint_rotation_error'],2e-5);self.assertLessEqual(metric['peak_correction_radians'],math.radians(35)+1e-6)
            self.assertLessEqual(metric['after_variation'],metric['before_variation']*1.001+1e-10)
            self.assertIn('intrinsic spin',metric['model']);self.assertIn('before_spin_variation',metric);self.assertIn('after_spin_variation',metric)
            if c2:self.assertTrue(all(row['match_acceleration'] and row['normalized_acceleration_jump']<=.1 for row in report['transitions']))
            for frame in (4.,8.):
                scene.frame_set(int(frame));p._update(ob);self.assertLess(np.linalg.norm(instance.location),2e-5)
                self.assertLess(2*math.acos(min(1.,abs(instance.matrix_world.to_quaternion().w))),2e-5)
            self.assertEqual(f._curve_token(ob),token);self.assertIs(ob.animation_data.action,candidate)
            records.append(dict(profile=label,match_acceleration=c2,report=report))
            f.restore(ob,scene);self.assertIsNone(m.find(ob));w.finish_preview(ob,scene,False);self.assertEqual(c._action_signature(ob),sig)
        path=ROOT/('training/b4artists_ml/results/'+os.environ.get('B4ML_RUN_LABEL','angular-momentum')+'-angular-host.json')
        path.write_text(json.dumps(dict(passed=True,rows=records),indent=2))
    def test_cancel_settings_and_root_rejection(self):
        from b4artists_ml import flight as f,motion_layer as m
        ob,*_=self.fixture();scene=bpy.context.scene;token=f._curve_token(ob);objects=set(bpy.data.objects.keys())
        f.start(ob,scene)
        while m.find(ob) is None:self.assertFalse(f.step(ob))
        f.abort(ob);self.assertIsNone(m.find(ob));self.assertEqual(set(bpy.data.objects.keys()),objects);self.assertEqual(f._curve_token(ob),token)
        f.start(ob,scene);f.step(ob);ob.b4ml.flights[0].takeoff_blend=2
        with self.assertRaisesRegex(ValueError,'changed'):f.step(ob)
        self.assertIsNone(m.find(ob));ob.b4ml.flights[0].takeoff_blend=3
        f.start(ob,scene);f.step(ob);ob.b4ml.mass_segments[0].inertia_radius=.41
        with self.assertRaisesRegex(ValueError,'changed'):f.step(ob)
        self.assertIsNone(m.find(ob));ob.b4ml.flight_backend='ROOT'
        with self.assertRaisesRegex(ValueError,'Native Motion Layer'):f.solve(ob,scene)
        ob.b4ml.flights[0].takeoff_blend=ob.b4ml.flights[0].landing_blend=0;ob.b4ml.flights[0].angular_momentum_strength=1
        with self.assertRaisesRegex(ValueError,'Angular momentum correction requires Native Motion Layer'):f.solve(ob,scene)
    def test_contact_and_priority_rejection_preserve_candidate(self):
        from b4artists_ml import flight as f,motion_layer as m
        ob,*_=self.fixture();scene=bpy.context.scene;token=f._curve_token(ob)
        contact=ob.b4ml.contacts.add();contact.start=1;contact.end=2;contact.blend=0;contact.strength=1;contact.enabled=True
        with self.assertRaisesRegex(ValueError,'contact'):f.solve(ob,scene)
        self.assertIsNone(m.find(ob));self.assertEqual(f._curve_token(ob),token)
        ob.b4ml.contacts.clear();anchor=ob.b4ml.anchors.add();anchor.frame=2;anchor.payload=ob.b4ml.anchors[0].payload
        with self.assertRaisesRegex(ValueError,'priority'):f.solve(ob,scene)
        self.assertIsNone(m.find(ob));self.assertEqual(f._curve_token(ob),token)
    def test_sixteen_flights_with_thirty_two_transitions(self):
        from b4artists_ml import flight as f,workflow as w,motion_layer as m
        from test_b4artists_ml_native_flight import values
        ob,*_=self.fixture();scene=bpy.context.scene;w.finish_preview(ob,scene,False);payload=ob.b4ml.anchors[0].payload;ob.b4ml.anchors.clear();ob.b4ml.flights.clear()
        for index in range(16):
            for frame in (1+5*index,2+5*index,4+5*index,5+5*index):
                anchor=ob.b4ml.anchors.add();anchor.frame=frame;anchor.payload=payload
            row=ob.b4ml.flights.add();row.start=2+5*index;row.end=4+5*index;row.takeoff_blend=row.landing_blend=1
        w.preview(ob,scene);before=f._curve_token(ob);report=f.solve(ob,scene);instance=m.validate(ob)
        self.assertEqual(len(report['transitions']),32);self.assertEqual(len(instance.animation_data.drivers),147)
        self.assertEqual(f._curve_token(ob),before)
        for fc in instance.animation_data.drivers:
            self.assertTrue(fc.driver.is_valid)
            for variable in fc.driver.variables:self.assertIs(variable.targets[0].id,instance)
        expected=values(ob);w.finish_preview(ob,scene,True);w.restore_kept_source(ob,scene);result=m.results(ob)[-1]
        w.preview_motion_result(ob,scene,result);np.testing.assert_allclose(values(ob),expected,atol=2e-5);w.finish_preview(ob,scene,False)
    def test_keep_archive_reload_reopen_discard(self):
        from b4artists_ml import flight as f,workflow as w,motion_layer as m,contacts as c
        from test_b4artists_ml_native_flight import values
        ob,source,sig,*_=self.fixture();scene=bpy.context.scene;name=ob.name;f.solve(ob,scene);expected=values(ob)
        w.finish_preview(ob,scene,True);w.restore_kept_source(ob,scene);result=m.results(ob)[-1];result_name=result.name
        with tempfile.TemporaryDirectory() as td:
            path=str(Path(td)/'momentum.blend');bpy.ops.wm.save_as_mainfile(filepath=path);bpy.ops.wm.open_mainfile(filepath=path,use_scripts=False)
            ob=bpy.data.objects[name];scene=bpy.context.scene;result=bpy.data.objects[result_name];w.preview_motion_result(ob,scene,result)
            np.testing.assert_allclose(values(ob),expected,atol=2e-5);w.finish_preview(ob,scene,False);self.assertEqual(c._action_signature(ob),sig)

if __name__=='__main__':unittest.main()
