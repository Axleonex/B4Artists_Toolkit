"""Native panel for saved poses and reversible interpolation candidates."""
import bpy
import json
import time
import math
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, FloatProperty, FloatVectorProperty, IntProperty, PointerProperty, StringProperty
from . import bl_info, workflow, posing, body_preview, body_live, quadruped_pose, quadruped_contacts, quadruped_gait, contacts, contact_visualization, support, flight, secondary_motion, cleanup, temporal_preview, rig_diagnostics, rig_mapping
from .rigs import detect_rig


def _report_error(op, context, exc):
    """Route operator exceptions to the feedback card and op.report.

    Plan §2.3; feedback.py:243 guarded decorator is the async analogue.
    Called from all execute/modal except-exc sites in this file.
    """
    text = str(exc)
    try:
        from .ui_workflow import feedback as _fb
        from . import workflow as _wf
        rig = _wf.active_rig(context)
        if rig is not None:
            key = _fb.classify(text)
            if key:
                _lvl, _tmpl, _fix, _props, _label = _fb.FAILURES[key]
                _fb.set_feedback(rig, _lvl,
                                 _tmpl.format(exc=text) if '{' in _tmpl else _tmpl,
                                 fix=_fix, fix_label=_label, **_props)
            else:
                _fb.error(rig, text)
    except Exception:
        pass
    op.report({'ERROR'}, text)



def _joint_limit_override(self, context):
    self.preset_provenance = 'Custom override'

class B4ML_PG_anchor(bpy.types.PropertyGroup):
    frame: FloatProperty(name="Frame")
    payload: StringProperty(options={'HIDDEN'})

class B4ML_PG_target(bpy.types.PropertyGroup):
    target: PointerProperty(type=bpy.types.Object)
    pole: PointerProperty(type=bpy.types.Object)
    enabled: BoolProperty(name="Pin", default=True)
    use_orientation: BoolProperty(name="Use Target Rotation",default=False,
        description="Rotate this target to set the evaluated pelvis, chest, neck, head, hand or foot orientation")
    use_pole: BoolProperty(name="Use Pole Direction",default=False,
        description="Move this limb's pole helper to choose its elbow or knee direction")
    pole_distance: FloatProperty(name="Requested Distance",default=.4,min=.1,max=4.,precision=2,
        description="Last requested pole distance from the elbow or knee in body-scale units; use Set Distance to move it")
    learn_bend: BoolProperty(name="Learn Bend", default=False,
        description="Suggest this elbow/knee bend from the local trained model; turn off to use your pole unchanged")

class B4ML_PG_joint_limit(bpy.types.PropertyGroup):
    preset_provenance: StringProperty(name='Provenance',default='Manual')
    use_bend_plane: BoolProperty(name='Limit Bend Direction',default=False,update=_joint_limit_override)
    bend_axis: FloatProperty(name='Forward Axis',subtype='ANGLE',default=0.,min=-math.pi,max=math.pi,
        description='Bend rotation axis in the selected rest-local X/Z plane; calibrate from a posed joint',update=_joint_limit_override)
    bend_min: FloatProperty(name='Bend Min',subtype='ANGLE',default=0.,min=-math.pi,max=math.pi,update=_joint_limit_override)
    bend_max: FloatProperty(name='Bend Max',subtype='ANGLE',default=math.radians(160),min=-math.pi,max=math.pi,update=_joint_limit_override)
    bend_sideways: FloatProperty(name='Sideways Swing',subtype='ANGLE',default=math.radians(5),min=0.,max=math.pi,update=_joint_limit_override)
    space: EnumProperty(name="Measure",items=(('CONTROL','Control Rotation','Rest-local animator control rotation'),('JOINT','Skeletal Joint','Evaluated skeletal rotation relative to its actual skeletal parent, corrected for rest pose')),default='CONTROL',update=_joint_limit_override)
    joint_available: BoolProperty(default=False,options={'HIDDEN'})
    enabled: BoolProperty(name="Limit",default=False,update=_joint_limit_override)
    swing: FloatProperty(name="Swing",subtype='ANGLE',default=math.radians(175),min=0.,max=math.pi,
        description="Maximum swing in the selected rest-corrected frame; preset values are editable estimates",update=_joint_limit_override)
    twist_min: FloatProperty(name="Twist Min",subtype='ANGLE',default=-math.pi,min=-math.pi,max=math.pi,update=_joint_limit_override)
    twist_max: FloatProperty(name="Twist Max",subtype='ANGLE',default=math.pi,min=-math.pi,max=math.pi,update=_joint_limit_override)

class B4ML_PG_mass_segment(bpy.types.PropertyGroup):
    weight: FloatProperty(name='Relative Mass',default=1.,min=0.,description='Artist-authored relative mass, not measured anatomy; weights are normalized together')
    fraction: FloatProperty(name='Center Along Segment',default=.5,min=0.,max=1.,description='Zero is segment start and one is segment end; inspect endpoints in the analysis report')
    inertia_radius: FloatProperty(name='Inertia Radius',default=.15,min=.01,max=1.,subtype='FACTOR',description='Solid-ellipsoid radius as a fraction of evaluated segment length; artist estimate, not measured anatomy')


class B4ML_PG_secondary_sphere(bpy.types.PropertyGroup):
    collider: PointerProperty(name='Sphere Center',type=bpy.types.Object,
        description='Unparented object whose world origin defines this sphere center')
    radius: FloatProperty(name='Sphere Radius',default=1.,min=.000001,max=1000.,
        soft_min=.01,soft_max=10.,subtype='DISTANCE',
        description='Explicit radius in world-space scene units; object scale does not change it')
    moving: BoolProperty(name='Follow Animation',default=False,
        description='Sample direct complete object-location animation at every secondary-motion frame')
    scaling: BoolProperty(name='Follow Radius Scale',default=False,
        description='Multiply the explicit radius by direct uniform object-scale animation')

class B4ML_PG_contact(bpy.types.PropertyGroup):
    review_state: EnumProperty(name='Review',items=(('ACCEPTED','Accepted','Available to contact correction'),('PROPOSED','Proposed','Heuristic suggestion requiring animator acceptance'),('REJECTED','Rejected','Excluded from contact correction')),default='ACCEPTED')
    confidence: FloatProperty(name='Suggestion Confidence',default=1.,min=0.,max=1.,subtype='FACTOR')
    provenance: StringProperty(name='Source',default='MANUAL')
    reason: StringProperty(name='Evidence')
    use_support: BoolProperty(name='Use as Support Patch',default=False,description='Explicit rectangular support estimate during full-strength hold only; no automatic floor or sole detection')
    support_width: FloatProperty(name='Patch Width',default=.1,min=0.,subtype='DISTANCE')
    support_length: FloatProperty(name='Patch Length',default=.2,min=0.,subtype='DISTANCE')
    support_heading: FloatProperty(name='Patch Heading',default=0.,subtype='ANGLE',description='Angle in the authored plane: zero width axis follows projected world X, or world Y near an X-facing plane')
    enabled: BoolProperty(name='Enabled',default=True)
    limb: EnumProperty(name='Limb',items=[(key,label,'') for key,label in (
        ('leg-L','Left Foot'),('leg-R','Right Foot'),('arm-L','Left Hand'),('arm-R','Right Hand'),
        ('fore-L','Left Fore Paw'),('fore-R','Right Fore Paw'),('hind-L','Left Hind Paw'),('hind-R','Right Hind Paw'))])
    start: FloatProperty(name='Hold From',default=1.)
    end: FloatProperty(name='Hold To',default=1.)
    blend: FloatProperty(name='Blend Frames',default=2.,min=0.,max=240.)
    asymmetric_blend: BoolProperty(name='Directional Blend',default=False,
        description='Use separate touchdown and release transition lengths')
    blend_in: FloatProperty(name='Blend In',default=2.,min=0.,max=240.,
        description='Frames before the hold used to ease into contact')
    blend_out: FloatProperty(name='Blend Out',default=2.,min=0.,max=240.,
        description='Frames after the hold used to ease out of contact')
    strength: FloatProperty(name='Strength',default=1.,min=0.,max=1.)
    point: FloatVectorProperty(name='World Contact',size=3,subtype='TRANSLATION')
    rotation: FloatVectorProperty(name='Contact Rotation',size=4,subtype='QUATERNION',default=(1.,0.,0.,0.))
    offset: FloatVectorProperty(name='Local Contact Offset',size=3,subtype='TRANSLATION')
    lock_rotation: BoolProperty(name='Hold Rotation',default=True)
    prop_object: PointerProperty(name='Follow Prop',type=bpy.types.Object,
        description='Optional rigid object whose evaluated transform drives this humanoid hand contact')
    prop_target: PointerProperty(type=bpy.types.Object,options={'HIDDEN'})
    prop_bound: BoolProperty(default=False,options={'HIDDEN'})
    prop_name: StringProperty(default='',options={'HIDDEN'})
    prop_point: FloatVectorProperty(name='Prop-local Contact',size=3,subtype='TRANSLATION',options={'HIDDEN'})
    prop_rotation: FloatVectorProperty(name='Prop-local Rotation',size=4,subtype='QUATERNION',
        default=(1.,0.,0.,0.),options={'HIDDEN'})

class B4ML_PG_flight(bpy.types.PropertyGroup):
    enabled: BoolProperty(name='Enabled',default=True)
    start: FloatProperty(name='Takeoff Pose',default=1.,description='Frame of an authored priority pose')
    end: FloatProperty(name='Landing Pose',default=11.,description='Frame of an authored priority pose')
    strength: FloatProperty(name='Gravity Influence',default=1.,min=0.,max=1.,description='Blend from the retained input COM path; one fits scene gravity')
    takeoff_blend: FloatProperty(name='Takeoff Transition',default=0.,min=0.,max=240.,description='Frames before takeoff to match COM velocity; zero disables; Native Motion Layer only')
    landing_blend: FloatProperty(name='Landing Transition',default=0.,min=0.,max=240.,description='Frames after landing to match COM velocity; zero disables; Native Motion Layer only')
    match_acceleration: BoolProperty(name='Match COM Acceleration',default=False,description='Use a source-safe C2 transition to match COM acceleration as well as velocity; Native Motion Layer only')
    angular_momentum_strength: FloatProperty(name='Angular Momentum',default=0.,min=0.,max=1.,subtype='FACTOR',description='Reduce orbital and rigid-segment spin angular-momentum variation during free flight with a bounded motion-layer correction; zero preserves the original orientation')
    contact_impulse_strength: FloatProperty(name='Landing Contact Impulse',default=0.,min=0.,max=1.,subtype='FACTOR',description='Absorb support-normal COM velocity at a landing contact while preserving tangential momentum; requires a held foot contact beginning at the landing frame; Native Motion Layer only')
    collision_strength: FloatProperty(name='Collision Response',default=0.,min=0.,max=1.,subtype='FACTOR',description='Lift the whole displayed character toward the allowed side of the authored support plane or static planar mesh; zero disables; Native Motion Layer only')
    collision_clearance: FloatProperty(name='Collision Clearance',default=.01,min=0.,max=1.,subtype='FACTOR',description='Extra plane clearance as a fraction of evaluated trunk length; mass segments use their editable ellipsoid radii')


_HUMANOID_CONTACT_LIMBS = frozenset(('leg-L', 'leg-R', 'arm-L', 'arm-R'))
_QUADRUPED_CONTACT_LIMBS = frozenset(quadruped_contacts.LIMBS)
_ANCHOR_PAGE_SIZE = 10


def _anchor_page(state):
    anchors = sorted(state.anchors, key=lambda anchor: anchor.frame)
    page_count = max(1, math.ceil(len(anchors) / _ANCHOR_PAGE_SIZE))
    page = min(max(int(state.anchor_page), 1), page_count)
    start = (page - 1) * _ANCHOR_PAGE_SIZE
    return anchors[start:start + _ANCHOR_PAGE_SIZE], page, page_count


def _anchor_page_label(page,page_count):
    return f'Pose Page {page} of {page_count}'


def _json_object(value):
    try:
        record = json.loads(value)
    except (ValueError, TypeError):
        return {}
    return record if isinstance(record, dict) else {}


def _contact_limb_set(obj):
    return (_QUADRUPED_CONTACT_LIMBS if detect_rig(obj.data.bones.keys()).family == 'quadruped'
            else _HUMANOID_CONTACT_LIMBS)


def _contact_review_indices(obj, review_state=None):
    limbs = _contact_limb_set(obj)
    return [index for index, item in enumerate(obj.b4ml.contacts)
            if item.limb in limbs and (review_state is None or item.review_state == review_state)]


def _contact_review_counts(obj):
    result = {name: 0 for name in ('PROPOSED', 'ACCEPTED', 'REJECTED')}
    for index in _contact_review_indices(obj):
        state = obj.b4ml.contacts[index].review_state
        if state in result:
            result[state] += 1
    return result


def _bulk_contact_review(obj, review_state):
    if review_state not in {'ACCEPTED', 'REJECTED'}:
        raise ValueError('Bulk contact review requires an accepted or rejected result')
    proposed = _contact_review_indices(obj, 'PROPOSED')
    if not proposed:
        raise ValueError('No compatible proposed contact suggestions to review')
    enabled = review_state == 'ACCEPTED'
    for index in proposed:
        item = obj.b4ml.contacts[index]
        item.review_state = review_state
        item.enabled = enabled
    counts = _contact_review_counts(obj)
    verb = 'Accepted' if enabled else 'Rejected'
    obj.b4ml.status = (f'{verb} {len(proposed)} contact suggestions; '
                       f'{counts["ACCEPTED"]} accepted, {counts["PROPOSED"]} proposed')
    return len(proposed)


def _navigate_contact_proposal(obj, scene, direction):
    if direction not in {-1, 1}:
        raise ValueError('Contact navigation direction must be previous or next')
    proposed = sorted(_contact_review_indices(obj, 'PROPOSED'),
                      key=lambda index: (obj.b4ml.contacts[index].start,
                                         obj.b4ml.contacts[index].end, index))
    if not proposed:
        raise ValueError('No compatible proposed contact suggestions to navigate')
    current = obj.b4ml.contact_index
    if current in proposed:
        target = proposed[(proposed.index(current) + direction) % len(proposed)]
    else:
        frame = scene.frame_current + scene.frame_subframe
        candidates = [index for index in proposed
                      if ((obj.b4ml.contacts[index].start > frame + 1e-6) if direction > 0
                          else (obj.b4ml.contacts[index].start < frame - 1e-6))]
        target = (candidates[0] if direction > 0 and candidates else
                  candidates[-1] if direction < 0 and candidates else
                  proposed[0] if direction > 0 else proposed[-1])
    item = obj.b4ml.contacts[target]
    obj.b4ml.contact_index = target
    frame = float(item.start)
    scene.frame_set(math.floor(frame), subframe=frame - math.floor(frame))
    ordinal = proposed.index(target) + 1
    obj.b4ml.status = f'Reviewing proposed contact {ordinal}/{len(proposed)}: {item.name}'
    return target


def _status_to_feedback(self, context):
    try:
        from .ui_workflow import feedback
        feedback.from_status(self.id_data, self.status)
    except Exception:
        pass


class B4ML_PG_settings(bpy.types.PropertyGroup):
    temporal_running: BoolProperty(default=False,options={'HIDDEN','SKIP_SAVE'})
    temporal_progress: StringProperty(options={'HIDDEN','SKIP_SAVE'})
    temporal_smoothing: BoolProperty(name='Smooth Transitions',default=False,description='Reduce abrupt speed changes while preserving authored poses; contact correction checks the smoothed motion against its limits')
    temporal_strength: FloatProperty(name='Procedural Motion Strength',default=1.,min=0.,max=1.,subtype='FACTOR',description='Blend the procedural whole-body trajectory from endpoint interpolation (0) to the full proposed trajectory (1); this is not learned motion')
    interpolation_method: EnumProperty(name='Method',items=[
        ('POSES','Pose Blending','Blend captured controls independently with the chosen timing'),
        ('AUTHORED','Whole-body Motion','Procedural trajectory through authored poses; requires all humanoid controls')],default='POSES')
    flights: CollectionProperty(type=B4ML_PG_flight)
    flight_index: IntProperty(name='Flight',default=0,min=0)
    flight_backend: EnumProperty(name='Flight Method',items=[('ROOT','Root Curves','Correct the rig master-root animation'),('NATIVE','Native Motion Layer','Apply editable character motion after source rig evaluation')],default='ROOT')
    show_flights: BoolProperty(name='Airborne Motion',default=False)
    flight_running: BoolProperty(default=False,options={'HIDDEN','SKIP_SAVE'})
    flight_progress: StringProperty(options={'HIDDEN','SKIP_SAVE'})
    flight_metrics: StringProperty(options={'HIDDEN'})
    flight_input: PointerProperty(type=bpy.types.Action)
    flight_output: PointerProperty(type=bpy.types.Action)
    show_secondary: BoolProperty(name='Secondary Motion',default=False)
    secondary_space: EnumProperty(name='Simulation Space',items=(('LOCAL','Local','Follow authored local control channels'),('WORLD','World','Follow evaluated world transforms through the rig hierarchy')),default='LOCAL')
    secondary_rotation: BoolProperty(name='Rotation',default=True,description='Apply damped follow-through to complete editable rotation curves on selected pose controls')
    secondary_location: BoolProperty(name='Location',default=False,description='Apply damped follow-through to complete editable location curves on selected pose controls')
    secondary_chain: BoolProperty(name='Couple Selected Chain',default=False,description='Couple one unbranched direct parent-child selection in Local+Rotation or bounded World+Location force/mass mode; deterministic and procedural')
    secondary_chain_direction: EnumProperty(name='Grow From Active',items=(('CHILDREN','Toward Children','Follow one eligible direct child from the active pose control'),('PARENTS','Toward Parents','Follow eligible direct parents from the active pose control')),default='CHILDREN',description='Topology direction for bounded direct-chain selection; no secondary-part meaning is inferred')
    secondary_chain_length: IntProperty(name='Maximum Controls',default=4,min=2,max=32,description='Maximum number of directly parented eligible controls to select from the active pose control')
    secondary_selection_swap: StringProperty(options={'HIDDEN','SKIP_SAVE'})
    secondary_control_loads: StringProperty(options={'HIDDEN'})
    secondary_load_force: FloatVectorProperty(name='Selected Force',size=3,default=(0.,0.,0.),min=-1000000.,max=1000000.,description='World-space force in kg times scene units per second squared, assigned to selected controls')
    secondary_load_mass: FloatProperty(name='Selected Mass',default=1.,min=.001,max=10000.,soft_min=.01,soft_max=100.,description='Mass in kilograms assigned with the selected force')
    secondary_load_offset: FloatVectorProperty(name='Application Offset (Local)',size=3,default=(0.,0.,0.),min=-1000.,max=1000.,description='Force application point relative to each control pivot in that control local space; zero applies no torque')
    secondary_load_inertia: FloatProperty(name='Rotational Inertia',default=1.,min=.001,max=1000000.,soft_min=.01,soft_max=1000.,description='Scalar rotational inertia in kilograms times scene units squared used for force-at-offset torque')
    secondary_chain_propagation: FloatProperty(name='Chain Propagation',default=.65,min=0.,max=1.,subtype='FACTOR',description='How strongly each selected child inherits its parent control lag; zero matches independent followers')
    secondary_frequency: FloatProperty(name='Response Frequency',default=3.,min=.05,max=30.,description='Spring response frequency in cycles per second; lower values create more lag')
    secondary_damping: FloatProperty(name='Damping',default=.45,min=0.,max=4.,description='Damping ratio for selected-control follow-through')
    secondary_air_friction: FloatProperty(name='Air Friction',default=.15,min=0.,max=20.,description='Additional velocity drag per second')
    secondary_wind_velocity: FloatVectorProperty(name='Wind Velocity',size=3,default=(0.,0.,0.),min=-100.,max=100.,description='Uniform world-space air velocity in scene units per second; Air Friction damps selected controls toward it')
    secondary_impulse_velocity: FloatVectorProperty(name='Velocity Impulse',size=3,default=(0.,0.,0.),min=-100.,max=100.,description='One world-space velocity change in scene units per second; zero disables')
    secondary_impulse_frame: FloatProperty(name='Impulse Frame',default=1.,min=-1000000.,max=1000000.,subtype='TIME',description='Frame where the velocity change begins affecting following secondary-motion samples')
    secondary_strength: FloatProperty(name='Influence',default=.65,min=0.,max=1.,subtype='FACTOR',description='Blend from the retained input animation to the deterministic secondary-motion result')
    secondary_blend_frames: FloatProperty(name='Boundary Blend',default=2.,min=0.,max=240.,description='Frames used to blend corrections to exact authored interval endpoints')
    secondary_gravity: FloatProperty(name='Gravity Influence',default=0.,min=0.,max=4.,description='World-space scene gravity applied to selected location controls; zero disables')
    secondary_external_acceleration: FloatVectorProperty(name='External Acceleration',size=3,default=(0.,0.,0.),min=-100.,max=100.,description='Uniform world-space acceleration in scene units per second squared; zero disables')
    secondary_self_collision: BoolProperty(name='Self-Collision',default=False,description='Keep selected world-space control volumes apart with a bounded deterministic pair solver')
    secondary_self_collision_radius: FloatProperty(name='Self Radius',default=.04,min=.000001,max=10.,soft_min=.005,soft_max=1.,subtype='DISTANCE',description='Finite radius assigned to each selected control for self-collision')
    secondary_collision: BoolProperty(name='Collision',default=False,description='Keep selected control pivots or finite control volumes outside an authored collider')
    secondary_collision_shape: EnumProperty(name='Collider Shape',items=(('PLANE','Planar','Use the authored support plane or selected static planar mesh'),('SPHERE','Sphere','Keep selected control pivots outside an explicit sphere'),('COMPOUND','Support + Spheres','Use the authored support surface with static spheres, up to three moving spheres, or one moving capsule in a World coupled chain'),('CAPSULE','Capsule','Keep selected control pivots outside a static endpoint capsule'),('MESH','Mesh','Keep selected control pivots outside a static or direct shape-key triangle mesh'),('VOLUME','Closed Volume','Keep finite selected-control volumes outside a closed static or shape-key triangle mesh')),default='PLANE')
    secondary_collision_compound_capsule: BoolProperty(name='Include Capsule',default=False,description='Add one static endpoint capsule, or one directly animated moving capsule after the support plane and static sphere set in a bounded World coupled compound')
    secondary_collision_compound_mesh: BoolProperty(name='Include Static Closed Mesh',default=False,description='Add one static closed triangle mesh after the support plane and sphere set in a bounded World coupled compound')
    secondary_sphere_collider: PointerProperty(name='Sphere Center',type=bpy.types.Object,description='Unparented object whose world origin defines the sphere center')
    secondary_sphere_radius: FloatProperty(name='Sphere Radius',default=1.,min=.000001,max=1000.,soft_min=.01,soft_max=10.,subtype='DISTANCE',description='Explicit sphere radius in world-space scene units; object scale does not change it')
    secondary_sphere_moving: BoolProperty(name='Follow Animation',default=False,description='Sample direct complete object-location animation for this sphere center')
    secondary_sphere_scaling: BoolProperty(name='Follow Radius Scale',default=False,description='Multiply the explicit radius by direct complete uniform object-scale animation')
    secondary_spheres: CollectionProperty(type=B4ML_PG_secondary_sphere)
    secondary_capsule_start: PointerProperty(name='Capsule Start',type=bpy.types.Object,description='Unparented object whose world origin defines one capsule endpoint')
    secondary_capsule_end: PointerProperty(name='Capsule End',type=bpy.types.Object,description='Unparented object whose world origin defines the other capsule endpoint')
    secondary_capsule_radius: FloatProperty(name='Capsule Radius',default=.1,min=.000001,max=1000.,soft_min=.01,soft_max=10.,subtype='DISTANCE',description='Explicit capsule radius in world-space scene units')
    secondary_capsule_moving: BoolProperty(name='Follow Endpoint Animation',default=False,description='Sample complete direct location Actions on both capsule endpoints')
    secondary_capsule_scaling: BoolProperty(name='Follow Radius Scale',default=False,description='Multiply the capsule radius by matching uniform direct endpoint scales')
    secondary_collision_mesh: PointerProperty(name='Collision Mesh',type=bpy.types.Object,description='Unparented mesh whose evaluated triangles define the sampled exclusion surface')
    secondary_collision_mesh_deforming: BoolProperty(name='Follow Deformation',default=False,description='Sample direct shape-key deformation of the collision mesh at each solve frame')
    secondary_collision_mesh_moving: BoolProperty(name='Follow Object Motion',default=False,description='Sample direct object-transform animation of the collision mesh at each solve frame')
    secondary_collision_volume_radius: FloatProperty(name='Control Volume Radius',default=.05,min=.000001,max=1000.,soft_min=.001,soft_max=10.,subtype='DISTANCE',description='Finite spherical selected-control radius maintained outside the closed collision mesh')
    secondary_collision_continuous: BoolProperty(name='Continuous-Time Sweep',default=False,description='Catch bounded selected-control crossings for a sphere set or capsule, or a closed mesh')
    secondary_collision_clearance: FloatProperty(name='Collision Clearance',default=.01,min=0.,max=10.,subtype='DISTANCE',description='Additional world-space distance maintained from the planar or spherical boundary')
    secondary_restitution: FloatProperty(name='Bounce',default=0.,min=0.,max=1.,subtype='FACTOR',description='Fraction of inward normal velocity reflected at the collision boundary')
    secondary_surface_friction: FloatProperty(name='Surface Friction',default=.35,min=0.,max=1.,subtype='FACTOR',description='Fraction of tangential velocity removed when a selected control contacts the collision boundary')
    secondary_running: BoolProperty(default=False,options={'HIDDEN','SKIP_SAVE'})
    secondary_progress: StringProperty(options={'HIDDEN','SKIP_SAVE'})
    secondary_metrics: StringProperty(options={'HIDDEN'})
    secondary_input: PointerProperty(type=bpy.types.Action)
    secondary_output: PointerProperty(type=bpy.types.Action)
    show_cleanup: BoolProperty(name='Animation Cleanup',default=False)
    cleanup_scope: EnumProperty(name='Apply To',items=(
        ('SELECTED','Selected Controls','Clean only selected captured pose controls'),
        ('CAPTURED','All Captured Controls','Clean all captured controls except accepted-contact controls')),default='SELECTED')
    cleanup_smooth: BoolProperty(name='Smooth Curves',default=True,description='Blend editable curve handles toward bounded harmonic tangents')
    cleanup_strength: FloatProperty(name='Smoothing Strength',default=.65,min=0.,max=1.,subtype='FACTOR',description='Blend from current handles toward the deterministic cleanup result')
    cleanup_reduce: BoolProperty(name='Remove Redundant Linear Keys',default=True,description='Conservatively remove non-priority keys only from fully linear scalar spans')
    cleanup_tolerance: FloatProperty(name='Key Tolerance',default=.001,min=0.,soft_max=.1,precision=5,description='Maximum scalar error at original linear key times; rotation components use radians')
    cleanup_running: BoolProperty(default=False,options={'HIDDEN','SKIP_SAVE'})
    cleanup_progress: StringProperty(options={'HIDDEN','SKIP_SAVE'})
    cleanup_metrics: StringProperty(options={'HIDDEN'})
    cleanup_input: PointerProperty(type=bpy.types.Action)
    cleanup_output: PointerProperty(type=bpy.types.Action)
    body_balance: BoolProperty(name='Assist Balance',default=False,description='Fit the authored COM projection toward the active support region while preserving pins; static by default')
    body_balance_strength: FloatProperty(name='Balance Strength',default=1.,min=0.,max=1.,description='Blend COM correction from the original preview pose, without accumulating repeated solves')
    body_balance_inset: FloatProperty(name='Support Inset',default=.01,min=0.,subtype='DISTANCE',description='Keep the target this far inside the authored support region; oversized insets are rejected')
    body_balance_free_pelvis: BoolProperty(name='Allow Pelvis Translation',default=False,description='Explicitly release the pelvis position pin so balance correction can move it; orientation and supporting contacts remain constrained')
    body_balance_dynamic: BoolProperty(name='Use Capture-Point Estimate',default=False,description='Procedural constant-gravity capture-point estimate from the authored COM velocity; not a force or contact solver')
    body_balance_velocity: FloatVectorProperty(name='COM Velocity',size=3,subtype='VELOCITY',description='Authored world-space COM velocity in scene units per second for the bounded capture-point estimate')
    mass_segments: CollectionProperty(type=B4ML_PG_mass_segment)
    mass_index: IntProperty(name='Segment',default=0,min=0,max=16)
    show_support: BoolProperty(name='Center of Mass / Support',default=False)
    show_mass_settings: BoolProperty(name='Mass Model',default=False)
    show_support_settings: BoolProperty(name='Support Plane / Tolerances',default=False)
    support_plane_point: FloatVectorProperty(name='Support Plane Point',size=3,subtype='TRANSLATION')
    support_plane_normal: FloatVectorProperty(name='Support Plane Normal',size=3,default=(0.,0.,1.))
    support_tolerance: FloatProperty(name='Contact Tolerance',default=.01,min=1e-6,subtype='DISTANCE',description='World-space maximum contact drift and plane distance for this estimate')
    support_rotation_tolerance: FloatProperty(name='Contact Rotation Tolerance',default=math.radians(5),min=1e-6,max=math.pi,subtype='ANGLE',description='Maximum change from captured hand/foot orientation before its patch is excluded')
    support_report: StringProperty(options={'HIDDEN'})
    contacts: CollectionProperty(type=B4ML_PG_contact)
    contact_index: IntProperty(name='Contact',default=0,min=0)
    show_contact_overlay: BoolProperty(name='Show Contact Overlay',default=True,
        description='Draw the selected contact target and its evaluated limb separation in the 3D View')
    show_all_contact_overlays: BoolProperty(name='Show All Contacts',default=False,
        description='Draw every compatible contact instead of only the selected contact')
    contact_limb: EnumProperty(name='Capture Limb',items=[(key,label,'') for key,label in (('leg-L','Left Foot'),('leg-R','Right Foot'),('arm-L','Left Hand'),('arm-R','Right Hand'))])
    quadruped_contact_limb: EnumProperty(name='Capture Paw',items=[(key,label,'') for key,label in (('fore-L','Left Fore Paw'),('fore-R','Right Fore Paw'),('hind-L','Left Hind Paw'),('hind-R','Right Hind Paw'))])
    contact_offset: FloatVectorProperty(name='Capture Local Offset',size=3,subtype='TRANSLATION',description='Point relative to the evaluated foot/hand joint; use an offset for a sole or palm')
    contact_surface: PointerProperty(name='Support Surface',type=bpy.types.Object,description='Optional static planar mesh; empty uses the authored support plane')
    contact_suggest_distance: FloatProperty(name='Maximum Surface Distance',default=.025,min=.0001,max=.25,subtype='FACTOR',description='Maximum surface distance relative to leg length for humanoids or body-to-paw distance for quadrupeds')
    contact_suggest_speed: FloatProperty(name='Maximum Foot Speed',default=.12,min=.001,max=5.,description='Maximum tangential speed per second relative to leg length for humanoids or body-to-paw distance for quadrupeds')
    contact_suggest_min_frames: IntProperty(name='Minimum Hold Frames',default=3,min=2,max=120)
    contact_suggest_gap_frames: IntProperty(name='Bridge Gap Frames',default=1,min=0,max=12,description='Join eligible samples across this many ineligible frames')
    contact_suggest_running: BoolProperty(default=False,options={'HIDDEN','SKIP_SAVE'})
    contact_suggest_progress: StringProperty(options={'HIDDEN','SKIP_SAVE'})
    contact_suggestion_report: StringProperty(options={'HIDDEN'})
    quadruped_gait_report: StringProperty(options={'HIDDEN'})
    quadruped_gait_index: IntProperty(name='Gait Phase',default=0,min=0)
    contact_running: BoolProperty(default=False,options={'HIDDEN','SKIP_SAVE'})
    contact_progress: StringProperty(options={'HIDDEN','SKIP_SAVE'})
    contact_metrics: StringProperty(options={'HIDDEN'})
    contact_input: PointerProperty(type=bpy.types.Action)
    contact_output: PointerProperty(type=bpy.types.Action)
    show_contacts: BoolProperty(name='Animation Contacts',default=False)
    show_quadruped_contacts: BoolProperty(name='Four-Paw Contacts',default=False)
    show_contact_details: BoolProperty(name='Contact Point Settings',default=False)
    body_limits: CollectionProperty(type=B4ML_PG_joint_limit)
    body_limit_preset: EnumProperty(name='Preset',items=(
        ('CONSERVATIVE_HUMANOID_V1','Conservative Humanoid v1','Broad animation-safe estimates for semantically mapped humanoid controls; not clinical anatomy'),),
        default='CONSERVATIVE_HUMANOID_V1')
    body_limit_control: StringProperty(name='Control')
    show_body_targets: BoolProperty(name='Pose Targets',default=True)
    show_body_limits: BoolProperty(name='Joint Limits',default=False)
    body_payload: StringProperty(options={'HIDDEN'})
    body_source: PointerProperty(type=bpy.types.Action)
    body_targets: CollectionProperty(type=B4ML_PG_target)
    quadruped_payload: StringProperty(options={'HIDDEN'})
    quadruped_source: PointerProperty(type=bpy.types.Action)
    quadruped_targets: CollectionProperty(type=B4ML_PG_target)
    quadruped_spine_follow: FloatProperty(name="Spine Follow",default=.5,min=0.,max=1.,subtype='FACTOR',
        description="Share this fraction of the Head target's rotation between the semantic Chest and Neck controls; zero keeps direct Head-only rotation")
    quadruped_neck_share: FloatProperty(name="Neck Share",default=.7,min=0.,max=1.,subtype='FACTOR',
        description="Portion of Spine Follow assigned to Neck; the remainder is assigned to Chest")
    quadruped_use_poles: BoolProperty(name="Pole Targets",default=False,
        description="Add four position-only pole helpers; first enable Rigify Pole Vector on every quadruped limb")
    body_influence: FloatProperty(name="Learned Influence",default=1.,min=0.,max=1.,description="Blend the trained whole-body suggestion; zero uses geometric fitting")
    body_strength: FloatProperty(name="Target Strength",default=1.,min=0.,max=1.)
    body_live: BoolProperty(default=False,options={'HIDDEN','SKIP_SAVE'})
    body_running: BoolProperty(default=False,options={'HIDDEN','SKIP_SAVE'})
    body_progress: StringProperty(options={'HIDDEN','SKIP_SAVE'})
    posing_payload: StringProperty(options={'HIDDEN'})
    posing_source: PointerProperty(type=bpy.types.Action)
    pose_targets: CollectionProperty(type=B4ML_PG_target)
    pose_offset: FloatVectorProperty(name="Pelvis Offset", subtype='TRANSLATION',
        description="World-space displacement; enabled limb targets remain pinned")
    pose_strength: FloatProperty(name="Target Strength", default=1., min=0., max=1.,
        description="Blend requested positions and pelvis displacement from the starting pose")
    max_bend: FloatProperty(name="Maximum Bend", default=175., min=1., max=180.,
        description="Elbow/knee flexion in degrees; zero is straight. This is not a complete anatomical limit model")
    learned_bend_strength: FloatProperty(name="Learned Bend Influence", default=1., min=0., max=1.,
        description="Blend opted-in bend directions from the authored pole toward the learned suggestion")
    pose_metrics: StringProperty(options={'HIDDEN'})
    anchors: CollectionProperty(type=B4ML_PG_anchor)
    anchor_page: IntProperty(name='Pose Page',default=1,min=1,max=13,
        description='Page of stored pose anchors; each page shows up to ten reusable poses')
    source_action: PointerProperty(type=bpy.types.Action)
    candidate_action: PointerProperty(type=bpy.types.Action)
    source_slot: StringProperty(options={'HIDDEN'})
    before_pose: StringProperty(options={'HIDDEN'})
    before_modes: StringProperty(options={'HIDDEN'})
    kept_action: PointerProperty(type=bpy.types.Action)
    kept_source: PointerProperty(type=bpy.types.Action)
    kept_slot: StringProperty(options={'HIDDEN'})
    kept_pose: StringProperty(options={'HIDDEN'})
    kept_modes: StringProperty(options={'HIDDEN'})
    selected_only: BoolProperty(name="Selected Controls Only", default=False,
        description="Capture selected pose controls instead of the detected humanoid controls")
    easing: EnumProperty(name="Timing", items=[
        ('SMOOTH', 'Ease In / Out', 'Smoothstep timing with shortest-path rotation'),
        ('LINEAR', 'Uniform', 'Uniform timing with shortest-path rotation'),
        ('EASE_IN', 'Ease In', 'Leave the first pose slowly, then accelerate'),
        ('EASE_OUT', 'Ease Out', 'Arrive at the next pose gradually after a faster start')])
    timing_bias: FloatProperty(name='Breakdown Bias', default=0.0, min=-1.0, max=1.0,
        subtype='FACTOR', description='Shift every transition midpoint: negative arrives later, positive arrives earlier; authored pose frames stay fixed')
    timing_clipboard: StringProperty(options={'HIDDEN'})
    show_rig_diagnostics: BoolProperty(name='Rig Mapping Diagnostics',default=False)
    show_rig_role_mappings: BoolProperty(name='Semantic Role Mappings',default=False)
    show_mapping_corrections: BoolProperty(name='Humanoid Mapping Corrections',default=False)
    rig_diagnostics_report: StringProperty(options={'HIDDEN','SKIP_SAVE'})
    mapping_role: EnumProperty(name='Semantic Role',items=[
        (role, role, 'Override the detected '+role+' animator control')
        for role in rig_mapping.HUMANOID_ROLES])
    mapping_bone: StringProperty(name='Animator Bone',
        description='Existing animator control to use for the selected semantic role')
    status: StringProperty(default="Capture poses at two or more frames", update=_status_to_feedback)


def _mapping_busy(state):
    return bool(state.candidate_action or state.posing_payload or state.body_payload
                or state.quadruped_payload or state.temporal_running
                or state.contact_running or state.contact_suggest_running
                or state.flight_running or state.secondary_running
                or state.cleanup_running)


class B4ML_OT_anchor_page(bpy.types.Operator):
    bl_idname='b4ml.anchor_page'
    bl_label='Browse Stored Poses'
    bl_description='Show another page of reusable pose anchors'
    bl_options={'INTERNAL'}
    page: IntProperty(options={'HIDDEN'},min=1,max=13)

    @classmethod
    def poll(cls,context):
        return workflow.active_rig(context) is not None

    def execute(self,context):
        state=workflow.active_rig(context).b4ml
        page_count=max(1,math.ceil(len(state.anchors)/_ANCHOR_PAGE_SIZE))
        state.anchor_page=min(max(self.page,1),page_count)
        return {'FINISHED'}


class B4ML_OT_mapping_correction(bpy.types.Operator):
    bl_idname='b4ml.mapping_correction'
    bl_label='Edit Humanoid Mapping Correction'
    bl_description='Apply or clear a validated semantic-role correction on this armature'
    bl_options={'REGISTER','UNDO'}
    operation: EnumProperty(items=[(name,name.title().replace('_',' '),'')
                                  for name in ('APPLY','CLEAR_ROLE','CLEAR_ALL')])

    @classmethod
    def poll(cls,context):
        obj=workflow.active_rig(context)
        return bool(obj and not _mapping_busy(obj.b4ml))

    def execute(self,context):
        obj=workflow.active_rig(context);state=obj.b4ml
        try:
            if self.operation=='APPLY':
                rows=rig_mapping.set_correction(obj,state.mapping_role,state.mapping_bone)
                state.status=(f'Mapped {state.mapping_role} to {state.mapping_bone}' if rows
                              else f'{state.mapping_role} uses its detected mapping')
            elif self.operation=='CLEAR_ROLE':
                rig_mapping.clear_correction(obj,state.mapping_role)
                state.status='Cleared manual mapping for '+state.mapping_role
            else:
                rig_mapping.clear_all(obj)
                state.status='Cleared all manual mapping corrections'
            report=rig_diagnostics.analyze(obj)
            state.rig_diagnostics_report=json.dumps(report,allow_nan=False)
            state.show_rig_diagnostics=True
        except Exception as exc:
            _report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}


class B4ML_OT_transition_timing(bpy.types.Operator):
    bl_idname = 'b4ml.transition_timing'
    bl_label = 'Transition Timing'
    bl_description = 'Override the deterministic timing of the transition arriving at this saved pose'
    bl_options = {'REGISTER', 'UNDO'}
    frame: FloatProperty(options={'HIDDEN'})
    use_override: BoolProperty(name='Override Global Timing', default=True)
    easing: EnumProperty(name='Timing', items=[
        ('SMOOTH', 'Ease In / Out', 'Smoothstep timing with shortest-path rotation'),
        ('LINEAR', 'Uniform', 'Uniform timing with shortest-path rotation'),
        ('EASE_IN', 'Ease In', 'Leave the previous pose slowly, then accelerate'),
        ('EASE_OUT', 'Ease Out', 'Arrive at this pose gradually after a faster start')])
    bias: FloatProperty(name='Breakdown Bias', default=0.0, min=-1.0, max=1.0,
        subtype='FACTOR', description='Negative arrives later; positive arrives earlier')
    departure_hold: FloatProperty(name='Departure Hold', default=0.0, min=0.0, max=.9,
        subtype='FACTOR', description='Fraction of this interval held on the previous pose')
    arrival_hold: FloatProperty(name='Arrival Hold', default=0.0, min=0.0, max=.9,
        subtype='FACTOR', description='Fraction of this interval held on the destination pose')

    @classmethod
    def poll(cls, context):
        return workflow.active_rig(context) is not None

    def draw(self, context):
        layout=self.layout
        layout.prop(self, 'use_override')
        col=layout.column();col.enabled=self.use_override
        col.prop(self, 'easing')
        col.prop(self, 'bias', slider=True)
        col.prop(self, 'departure_hold', slider=True)
        col.prop(self, 'arrival_hold', slider=True)
        if self.departure_hold + self.arrival_hold > .900001:
            col.label(text='Leave at least 10% of the interval for motion.',icon='ERROR')
        layout.label(text=f'Arrives at saved pose frame {self.frame:g}')

    def invoke(self, context, event):
        obj=workflow.active_rig(context)
        try:
            current=workflow.transition_timing(obj,self.frame)
        except Exception as exc:
            _report_error(self, context, exc);return {'CANCELLED'}
        self.use_override=current is not None
        self.easing=current['easing'] if current else obj.b4ml.easing
        self.bias=current['bias'] if current else obj.b4ml.timing_bias
        self.departure_hold=current['departure_hold'] if current else 0.0
        self.arrival_hold=current['arrival_hold'] if current else 0.0
        return context.window_manager.invoke_props_dialog(self,width=320)

    def execute(self, context):
        obj=workflow.active_rig(context)
        try:
            workflow.set_transition_timing(
                obj,self.frame,self.use_override,self.easing,self.bias,
                self.departure_hold,self.arrival_hold)
        except Exception as exc:
            _report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}


class B4ML_OT_breakdown_pose(bpy.types.Operator):
    bl_idname = 'b4ml.breakdown_pose'
    bl_label = 'Create Breakdown Pose'
    bl_description = 'Create an editable priority pose between the neighboring saved poses'
    bl_options = {'REGISTER', 'UNDO'}
    blend: FloatProperty(name='Pose Blend', default=.5, min=0., max=1., subtype='FACTOR',
        description='Zero copies the prior pose; one copies the following pose')
    selected_only: BoolProperty(name='Selected Controls Only', default=False,
        description='Use this blend only for selected captured controls; other controls keep their natural timeline blend')
    left_frame: FloatProperty(options={'HIDDEN'})
    right_frame: FloatProperty(options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        obj=workflow.active_rig(context)
        return bool(obj and obj.b4ml.interpolation_method == 'POSES')

    def draw(self, context):
        layout=self.layout
        layout.prop(self,'blend',slider=True)
        layout.prop(self,'selected_only')
        layout.label(text=f'0%: frame {self.left_frame:g}')
        layout.label(text=f'100%: frame {self.right_frame:g}')
        layout.label(text='Creates a new editable priority pose.',icon='INFO')

    def invoke(self, context, event):
        obj=workflow.active_rig(context)
        try:
            values=workflow.breakdown_context(obj,context.scene)
        except Exception as exc:
            _report_error(self, context, exc);return {'CANCELLED'}
        self.blend=values['natural_blend']
        self.left_frame=values['left'][0]
        self.right_frame=values['right'][0]
        return context.window_manager.invoke_props_dialog(self,width=320)

    def execute(self, context):
        obj=workflow.active_rig(context)
        try:
            workflow.create_breakdown_anchor(
                obj,context.scene,self.blend,self.selected_only)
        except Exception as exc:
            _report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}


class B4ML_OT_inbetween_series(bpy.types.Operator):
    bl_idname = 'b4ml.inbetween_series'
    bl_label = 'Procedural Inbetween Series'
    bl_description = 'Bake evenly spaced editable priority poses from the current transition timing'
    bl_options = {'REGISTER', 'UNDO'}
    count: IntProperty(name='Inbetweens', default=3, min=1, max=8,
        description='Number of editable priority poses to create across this transition')
    left_frame: FloatProperty(options={'HIDDEN'})
    right_frame: FloatProperty(options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        obj=workflow.active_rig(context)
        return bool(obj and obj.b4ml.interpolation_method == 'POSES')

    def draw(self, context):
        layout=self.layout
        layout.prop(self,'count')
        layout.label(text=f'Across frame {self.left_frame:g} to {self.right_frame:g}')
        layout.label(text='Samples current easing, bias, and holds.',icon='INFO')
        layout.label(text='Creates editable procedural priority poses.')

    def invoke(self, context, event):
        obj=workflow.active_rig(context)
        try:
            values=workflow.breakdown_context(obj,context.scene)
        except Exception as exc:
            _report_error(self, context, exc);return {'CANCELLED'}
        self.left_frame=values['left'][0]
        self.right_frame=values['right'][0]
        return context.window_manager.invoke_props_dialog(self,width=340)

    def execute(self, context):
        obj=workflow.active_rig(context)
        try:
            workflow.create_inbetween_series(obj,context.scene,self.count)
        except Exception as exc:
            _report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}


class B4ML_OT_retime_anchor(bpy.types.Operator):
    bl_idname = 'b4ml.retime_anchor'
    bl_label = 'Priority Pose Retime'
    bl_description = 'Move this saved priority pose to the current playhead without recapturing it'
    bl_options = {'REGISTER', 'UNDO'}
    source_frame: FloatProperty(options={'HIDDEN'})
    destination_frame: FloatProperty(options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        obj=workflow.active_rig(context)
        return bool(obj and obj.b4ml.interpolation_method == 'POSES')

    def draw(self, context):
        layout=self.layout
        layout.label(text=f'From frame {self.source_frame:.9g}')
        layout.label(text=f'To playhead frame {self.destination_frame:.9g}')
        layout.label(text='Keeps pose data and incoming timing.',icon='INFO')
        layout.label(text='Saved-pose order cannot change.')

    def invoke(self, context, event):
        obj=workflow.active_rig(context)
        try:
            values=workflow.retime_anchor_context(
                obj,context.scene,self.source_frame)
        except Exception as exc:
            _report_error(self, context, exc);return {'CANCELLED'}
        self.source_frame=values['source_frame']
        self.destination_frame=values['destination_frame']
        return context.window_manager.invoke_props_dialog(self,width=330)

    def execute(self, context):
        obj=workflow.active_rig(context)
        try:
            workflow.retime_anchor(
                obj,context.scene,self.source_frame,self.destination_frame)
        except Exception as exc:
            _report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}


class B4ML_OT_ripple_retime(bpy.types.Operator):
    bl_idname = 'b4ml.ripple_retime'
    bl_label = 'Ripple Pose Retime'
    bl_description = 'Move this saved pose to the playhead and shift every later saved pose with it'
    bl_options = {'REGISTER', 'UNDO'}
    source_frame: FloatProperty(options={'HIDDEN'})
    destination_frame: FloatProperty(options={'HIDDEN'})
    moved_count: IntProperty(options={'HIDDEN'},min=1,max=128)
    source_binding: StringProperty(options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        obj=workflow.active_rig(context)
        return bool(obj and obj.b4ml.interpolation_method == 'POSES')

    def draw(self, context):
        layout=self.layout
        layout.label(text=f'From frame {self.source_frame:.9g}')
        layout.label(text=f'To playhead frame {self.destination_frame:.9g}')
        layout.label(text=f'Moves {self.moved_count} pose' +
                    ('s together.' if self.moved_count != 1 else '.'))
        layout.label(text='Keeps later spacing and all pose timing.',icon='INFO')

    def invoke(self, context, event):
        obj=workflow.active_rig(context)
        try:
            values=workflow.ripple_retime_context(
                obj,context.scene,self.source_frame)
        except Exception as exc:
            _report_error(self, context, exc);return {'CANCELLED'}
        self.source_frame=values['source_frame']
        self.destination_frame=values['destination_frame']
        self.moved_count=values['moved_count']
        self.source_binding=values['binding']
        return context.window_manager.invoke_props_dialog(self,width=340)

    def execute(self, context):
        obj=workflow.active_rig(context)
        try:
            workflow.ripple_retime(
                obj,context.scene,self.source_frame,self.destination_frame,
                self.source_binding)
        except Exception as exc:
            _report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}


class B4ML_OT_pose_spacing_scale(bpy.types.Operator):
    bl_idname = 'b4ml.pose_spacing_scale'
    bl_label = 'Scale Later Pose Spacing'
    bl_description = 'Keep this pose fixed and proportionally scale every later saved-pose frame'
    bl_options = {'REGISTER', 'UNDO'}
    pivot_frame: FloatProperty(options={'HIDDEN'})
    factor: FloatProperty(name='Pose Spacing Scale',default=1.25,min=.25,max=4.,precision=3,
        description='Scale later pose frames around this fixed pivot; easing, bias, holds, and pose data stay exact')
    moved_count: IntProperty(options={'HIDDEN'},min=1,max=127)
    source_binding: StringProperty(options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        obj=workflow.active_rig(context)
        return bool(obj and obj.b4ml.interpolation_method == 'POSES')

    def draw(self, context):
        self.layout.label(text=f'Fixed pivot: frame {self.pivot_frame:.9g}')
        self.layout.prop(self,'factor')
        self.layout.label(text=f'Scales {self.moved_count} later pose' +
                          ('s.' if self.moved_count != 1 else '.'))
        self.layout.label(text='Pose data, easing, bias, and holds stay exact.',icon='INFO')

    def invoke(self, context, event):
        obj=workflow.active_rig(context)
        try:
            values=workflow.pose_spacing_scale_context(obj,self.pivot_frame)
        except Exception as exc:
            _report_error(self, context, exc);return {'CANCELLED'}
        self.pivot_frame=values['pivot_frame'];self.moved_count=values['moved_count']
        self.source_binding=values['binding']
        return context.window_manager.invoke_props_dialog(self,width=380)

    def execute(self, context):
        obj=workflow.active_rig(context)
        try:
            workflow.scale_pose_spacing(
                obj,self.pivot_frame,self.factor,self.source_binding or None)
        except Exception as exc:
            _report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}


class B4ML_OT_pose_spacing_equalize(bpy.types.Operator):
    bl_idname = 'b4ml.pose_spacing_equalize'
    bl_label = 'Equalize Later Pose Spacing'
    bl_description = 'Keep this pose fixed and place every later saved pose at one constant frame interval'
    bl_options = {'REGISTER', 'UNDO'}
    pivot_frame: FloatProperty(options={'HIDDEN'})
    interval: FloatProperty(name='Frame Interval',default=5.,min=.25,max=240.,soft_max=48.,precision=3,
        description='Constant interval between this pivot and every later saved pose')
    affected_count: IntProperty(options={'HIDDEN'},min=1,max=127)
    source_binding: StringProperty(options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        obj=workflow.active_rig(context)
        return bool(obj and obj.b4ml.interpolation_method == 'POSES')

    def draw(self, context):
        self.layout.label(text=f'Fixed pivot: frame {self.pivot_frame:.9g}')
        self.layout.prop(self,'interval')
        self.layout.label(text=f'Affects {self.affected_count} later pose' +
                          ('s.' if self.affected_count != 1 else '.'))
        self.layout.label(text='Pose data, easing, bias, and holds stay exact.',icon='INFO')

    def invoke(self, context, event):
        obj=workflow.active_rig(context)
        try:
            values=workflow.pose_spacing_equalize_context(obj,self.pivot_frame)
        except Exception as exc:
            _report_error(self, context, exc);return {'CANCELLED'}
        self.pivot_frame=values['pivot_frame'];self.interval=values['interval']
        self.affected_count=values['affected_count'];self.source_binding=values['binding']
        return context.window_manager.invoke_props_dialog(self,width=380)

    def execute(self, context):
        obj=workflow.active_rig(context)
        try:
            workflow.equalize_pose_spacing(
                obj,self.pivot_frame,self.interval,self.source_binding or None)
        except Exception as exc:
            _report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}


class B4ML_OT_transition_timing_transfer(bpy.types.Operator):
    bl_idname = 'b4ml.transition_timing_transfer'
    bl_label = 'Transfer Transition Timing'
    bl_description = 'Copy or paste easing, bias, and transition holds between saved pose intervals'
    bl_options = {'REGISTER', 'UNDO'}
    operation: EnumProperty(items=(
        ('COPY', 'Copy', 'Copy this interval timing'),
        ('PASTE', 'Paste', 'Paste copied timing into this interval')))
    frame: FloatProperty(options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        obj=workflow.active_rig(context)
        return bool(obj and obj.b4ml.interpolation_method == 'POSES')

    def execute(self, context):
        obj=workflow.active_rig(context)
        try:
            if self.operation == 'COPY':
                workflow.copy_transition_timing(obj,self.frame)
            else:
                workflow.paste_transition_timing(obj,self.frame)
        except Exception as exc:
            _report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}


class B4ML_OT_action(bpy.types.Operator):
    bl_idname = 'b4ml.action'
    bl_label = 'B4Artists ML Action'
    bl_description = 'Inspect the rig, capture or reuse a pose, or manage a separate interpolation candidate'
    bl_options = {'REGISTER', 'UNDO'}
    operation: EnumProperty(items=[(n, n.replace('_', ' ').title(), '') for n in
        ('INSPECT', 'CAPTURE', 'REUSE', 'REMOVE', 'PREVIEW', 'KEEP', 'DISCARD',
         'RESTORE_SOURCE', 'SELECT_KEPT')])
    anchor_frame: FloatProperty(options={'HIDDEN'})

    @classmethod
    def description(cls, context, properties):
        _STAGE_KEYS = {
            'PREVIEW': 'motion.preview',
            'KEEP': 'review.keep',
            'DISCARD': 'review.discard',
            'RESTORE_SOURCE': 'review.restore',
        }
        stage_key = _STAGE_KEYS.get(properties.operation)
        if stage_key:
            try:
                from .ui_workflow import stage as _stage
                st = _stage.evaluate(_stage.snapshot(context))
                reason = _stage.locked(st, stage_key)
                if reason:
                    return reason
            except Exception:
                pass
        return cls.bl_description

    @classmethod
    def poll(cls, context):
        obj=workflow.active_rig(context)
        return bool(obj and not obj.b4ml.temporal_running and not obj.b4ml.contact_suggest_running and not obj.b4ml.secondary_running and not obj.b4ml.cleanup_running)

    def execute(self, context):
        obj = workflow.active_rig(context)
        state = obj.b4ml
        try:
            if self.operation == 'INSPECT':
                report=rig_diagnostics.analyze(obj);state.show_rig_diagnostics=True
                state.rig_diagnostics_report=json.dumps(report,allow_nan=False)
                blocked=sum(row['applicable'] and not row['ready'] for row in report['workflows'])
                state.status=(f"{report['profile']} [{report['family']}]: "
                              f"{report['mapped_required_role_count']}/{report['required_role_count']} roles; "
                              f"{blocked} blocked preflights")
                if report['warnings']:
                    self.report({'WARNING'}, '; '.join(report['warnings']))
            elif self.operation == 'CAPTURE':
                workflow.capture_anchor(obj, context.scene, state.selected_only)
            elif self.operation == 'REUSE':
                workflow.reuse_anchor(obj,context.scene,self.anchor_frame)
            elif self.operation == 'REMOVE':
                frame = context.scene.frame_current + context.scene.frame_subframe
                workflow.remove_anchor(obj, frame)
            elif self.operation == 'RESTORE_SOURCE':
                workflow.restore_kept_source(obj, context.scene)
            elif self.operation == 'PREVIEW':
                workflow.preview(obj, context.scene, state.easing,
                                 timing_bias=state.timing_bias)
            elif self.operation == 'SELECT_KEPT':
                if not state.kept_action:
                    raise ValueError('No kept result to select')
                if obj.animation_data is None:
                    obj.animation_data_create()
                obj.animation_data.action = state.kept_action
            else:
                workflow.finish_preview(obj, context.scene, keep=self.operation == 'KEEP')
        except Exception as exc:
            _report_error(self, context, exc)
            return {'CANCELLED'}
        return {'FINISHED'}

class B4ML_OT_pose(bpy.types.Operator):
    bl_idname = 'b4ml.pose'
    bl_label = 'B4Artists Assisted Pose'
    bl_options = {'REGISTER', 'UNDO'}
    operation: EnumProperty(items=[(n, n.title(), '') for n in ('BEGIN', 'SOLVE', 'KEEP', 'CANCEL')])

    @classmethod
    def poll(cls, context):
        obj=workflow.active_rig(context)
        return bool(obj and not obj.b4ml.contact_suggest_running and not obj.b4ml.secondary_running and not obj.b4ml.cleanup_running)

    def execute(self, context):
        obj = workflow.active_rig(context)
        try:
            if self.operation == 'BEGIN':
                posing.begin(obj, context.scene)
            elif self.operation == 'SOLVE':
                posing.solve(obj, context.scene)
            else:
                posing.finish(obj, context.scene, self.operation == 'KEEP')
        except Exception as exc:
            _report_error(self, context, exc)
            return {'CANCELLED'}
        return {'FINISHED'}

class B4ML_OT_body(bpy.types.Operator):
    bl_idname='b4ml.body'
    bl_label='Whole-Body Preview'
    bl_options={'REGISTER','UNDO'}
    operation: EnumProperty(items=[(n,n.title(),'') for n in ('BEGIN','KEEP','CANCEL','CALIBRATE_BEND','APPLY_LIMIT_PRESET','RESET_TARGET','MIRROR_TARGETS','ALIGN_POLE','FLIP_POLE','SET_POLE_DISTANCE','SAVE_POSE_ASSET','APPLY_POSE_ASSET')])
    target_name: StringProperty(options={'HIDDEN'})
    mirror_direction: EnumProperty(items=(('LEFT_TO_RIGHT','Left to Right',''),('RIGHT_TO_LEFT','Right to Left','')),options={'HIDDEN'})

    @classmethod
    def description(cls, context, properties):
        descriptions = {
            'ALIGN_POLE': 'Place this pole helper on the current evaluated elbow or knee bend.',
            'FLIP_POLE': 'Place this pole helper opposite the current evaluated bend to request the other side.',
            'SET_POLE_DISTANCE': 'Move this pole helper to the selected body-scale distance without changing its direction.',
            'SAVE_POSE_ASSET': 'Save the current verified target layout in scene-local semantic body coordinates for another supported humanoid.',
            'APPLY_POSE_ASSET': 'Apply the scene semantic target pose to this preview without changing the rig until you solve.',
        }
        _STAGE_KEYS = {'BEGIN': 'pose.begin', 'KEEP': 'pose.keep', 'CANCEL': 'pose.cancel'}
        stage_key = _STAGE_KEYS.get(properties.operation)
        if stage_key:
            try:
                from .ui_workflow import stage as _stage
                st = _stage.evaluate(_stage.snapshot(context))
                reason = _stage.locked(st, stage_key)
                if reason:
                    return reason
            except Exception:
                pass
        return descriptions.get(properties.operation, cls.bl_label)

    @classmethod
    def poll(cls,context):
        obj=workflow.active_rig(context)
        return bool(obj and not obj.b4ml.contact_suggest_running and not obj.b4ml.secondary_running and not obj.b4ml.cleanup_running)

    def execute(self,context):
        obj=workflow.active_rig(context)
        try:
            if self.operation=='BEGIN':body_preview.begin(obj,context.scene)
            elif self.operation=='CALIBRATE_BEND':body_preview.calibrate_bend_axis(obj)
            elif self.operation=='APPLY_LIMIT_PRESET':body_preview.apply_limit_preset(obj,obj.b4ml.body_limit_preset)
            elif self.operation=='RESET_TARGET':body_preview.reset_target(obj,self.target_name)
            elif self.operation=='MIRROR_TARGETS':body_preview.mirror_targets(obj,self.mirror_direction)
            elif self.operation=='ALIGN_POLE':body_preview.align_pole_to_current_bend(obj,self.target_name)
            elif self.operation=='FLIP_POLE':body_preview.flip_pole_to_opposite_bend(obj,self.target_name)
            elif self.operation=='SET_POLE_DISTANCE':
                item=obj.b4ml.body_targets.get(self.target_name)
                body_preview.set_pole_distance(obj,self.target_name,item.pole_distance if item else None)
            elif self.operation=='SAVE_POSE_ASSET':body_preview.capture_pose_asset(obj,context.scene)
            elif self.operation=='APPLY_POSE_ASSET':body_preview.apply_pose_asset(obj,context.scene)
            else:body_preview.finish(obj,context.scene,self.operation=='KEEP')
        except Exception as exc:
            _report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}


class B4ML_OT_body_solve(bpy.types.Operator):
    bl_idname='b4ml.body_solve'
    bl_label='Solve Whole Body'
    bl_description='Fit a local learned pose; Escape cancels and restores the previous preview'
    bl_options={'REGISTER','UNDO'}
    _timer=None
    _obj=None

    @classmethod
    def description(cls, context, properties):
        try:
            from .ui_workflow import stage as _stage
            st = _stage.evaluate(_stage.snapshot(context))
            reason = _stage.locked(st, 'pose.solve')
            if reason:
                return reason
        except Exception:
            pass
        return cls.bl_description

    @classmethod
    def poll(cls,context):
        obj=workflow.active_rig(context)
        return bool(obj and obj.b4ml.body_payload and not obj.b4ml.body_running and not obj.b4ml.body_live and not obj.b4ml.contact_suggest_running and not obj.b4ml.secondary_running and not obj.b4ml.cleanup_running)

    def execute(self,context):
        try:body_preview.solve(workflow.active_rig(context))
        except Exception as exc:
            _report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self,context,event):
        if bpy.app.background or context.window is None:return self.execute(context)
        self._obj=workflow.active_rig(context)
        try:
            body_preview.start(self._obj)
            self._timer=context.window_manager.event_timer_add(.01,window=context.window)
            context.window_manager.modal_handler_add(self)
        except Exception as exc:
            body_preview.abort(self._obj);self._remove_timer(context)
            _report_error(self, context, exc);return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def _remove_timer(self,context):
        if self._timer is not None:
            try:context.window_manager.event_timer_remove(self._timer)
            except (ReferenceError,RuntimeError):pass
            self._timer=None

    def modal(self,context,event):
        try:
            if not self._obj.b4ml.body_running:
                self._remove_timer(context);return {'CANCELLED'}
            if event.type in ('ESC','RIGHTMOUSE'):
                body_preview.abort(self._obj);self._remove_timer(context);return {'CANCELLED'}
            if event.type=='TIMER' and time.monotonic()>=getattr(self,'_next_tick',0.):
                self._next_tick=time.monotonic()+.01
                if body_preview.step(self._obj):
                    self._remove_timer(context);return {'FINISHED'}
                if context.area:context.area.tag_redraw()
        except Exception as exc:
            try:body_preview.abort(self._obj)
            except (ReferenceError,RuntimeError):pass
            self._remove_timer(context)
            try:self._obj.b4ml.status='Whole-body solve failed: '+str(exc)
            except ReferenceError:pass
            _report_error(self, context, exc);return {'CANCELLED'}
        if event.type in ('MIDDLEMOUSE','WHEELUPMOUSE','WHEELDOWNMOUSE','MOUSEMOVE'):
            return {'PASS_THROUGH'}
        return {'RUNNING_MODAL'}

    def cancel(self,context):
        try:
            if self._obj:body_preview.abort(self._obj)
        finally:self._remove_timer(context)


class B4ML_OT_quadruped_pose(bpy.types.Operator):
    bl_idname = 'b4ml.quadruped_pose'
    bl_label = 'Quadruped Whole-Body Pose'
    bl_description = 'Move a generated Rigify torso, four paw IK targets, and four limb poles; rotate Head and optionally distribute its turn through Chest and Neck'
    bl_options = {'REGISTER', 'UNDO'}
    operation: EnumProperty(items=[(name, name.title(), '') for name in
                                   ('MATCH_POLES', 'BEGIN', 'RESET_TARGET', 'MIRROR_TARGETS',
                                    'ALIGN_POLE', 'FLIP_POLE', 'SET_POLE_DISTANCE',
                                    'SAVE_POSE_ASSET', 'APPLY_POSE_ASSET',
                                    'SOLVE', 'KEEP', 'CANCEL')])
    target_name: StringProperty(options={'HIDDEN'})
    mirror_direction: EnumProperty(
        items=(('LEFT_TO_RIGHT', 'Left to Right', ''),
               ('RIGHT_TO_LEFT', 'Right to Left', '')), options={'HIDDEN'})

    @classmethod
    def description(cls, context, properties):
        return {
            'ALIGN_POLE': 'Place this Pole Target on the current evaluated limb bend ray.',
            'FLIP_POLE': 'Place this Pole Target opposite the current evaluated limb bend.',
            'SET_POLE_DISTANCE': ('Move this Pole Target to the selected body-scale distance '
                                  'without changing its current direction.'),
        }.get(properties.operation, cls.bl_description)

    @classmethod
    def poll(cls, context):
        obj = workflow.active_rig(context)
        return bool(obj and not obj.b4ml.candidate_action and
                    not obj.b4ml.posing_payload and not obj.b4ml.body_payload and
                    not obj.b4ml.contact_suggest_running and
                    not obj.b4ml.temporal_running and not obj.b4ml.flight_running and
                    not obj.b4ml.body_running and not obj.b4ml.body_live and
                    not obj.b4ml.contact_running and not obj.b4ml.secondary_running and
                    not obj.b4ml.cleanup_running and not workflow.motion_layer.find(obj))

    def execute(self, context):
        obj = workflow.active_rig(context)
        try:
            if self.operation == 'MATCH_POLES':
                quadruped_pose.match_pole_vectors(obj, context.scene)
            elif self.operation == 'BEGIN':
                quadruped_pose.begin(obj, context.scene)
            elif self.operation == 'RESET_TARGET':
                quadruped_pose.reset_target(obj, context.scene, self.target_name)
            elif self.operation == 'MIRROR_TARGETS':
                quadruped_pose.mirror_targets(obj, context.scene, self.mirror_direction)
            elif self.operation == 'ALIGN_POLE':
                quadruped_pose.align_pole_to_current_bend(
                    obj, context.scene, self.target_name)
            elif self.operation == 'FLIP_POLE':
                quadruped_pose.flip_pole_to_opposite_bend(
                    obj, context.scene, self.target_name)
            elif self.operation == 'SET_POLE_DISTANCE':
                item = obj.b4ml.quadruped_targets.get(self.target_name)
                quadruped_pose.set_pole_distance(
                    obj, context.scene, self.target_name,
                    item.pole_distance if item else None)
            elif self.operation == 'SAVE_POSE_ASSET':
                quadruped_pose.capture_pose_asset(obj, context.scene)
            elif self.operation == 'APPLY_POSE_ASSET':
                quadruped_pose.apply_pose_asset(obj, context.scene)
            elif self.operation == 'SOLVE':
                quadruped_pose.solve(obj, context.scene)
            else:
                quadruped_pose.finish(obj, context.scene, self.operation == 'KEEP')
        except Exception as exc:
            _report_error(self, context, exc)
            return {'CANCELLED'}
        return {'FINISHED'}


class B4ML_OT_body_live(bpy.types.Operator):
    bl_idname='b4ml.body_live'
    bl_label='Live Whole-Body Solve'
    bl_description='Update the pose after target edits settle; Escape stops automatic solving'
    _timer=None
    _obj=None
    _watcher=None

    @classmethod
    def poll(cls,context):
        obj=workflow.active_rig(context)
        return bool(obj and obj.b4ml.body_payload and not obj.b4ml.contact_suggest_running and not obj.b4ml.secondary_running and not obj.b4ml.cleanup_running)

    def execute(self,context):
        obj=workflow.active_rig(context)
        if obj.b4ml.body_live:
            body_live.stop(obj);obj.b4ml.status='Live Solve stopped; preview retained'
            return {'FINISHED'}
        self.report({'ERROR'},'Start Live Solve from an interactive viewport')
        return {'CANCELLED'}

    def invoke(self,context,event):
        obj=workflow.active_rig(context)
        if obj.b4ml.body_live or bpy.app.background or context.window is None:
            return self.execute(context)
        self._obj=obj
        try:
            body_live.start(obj)
            self._watcher=body_live._WATCHERS[obj.as_pointer()]
            self._timer=context.window_manager.event_timer_add(.02,window=context.window)
            context.window_manager.modal_handler_add(self)
        except Exception as exc:
            body_live.stop(obj);self._remove_timer(context)
            _report_error(self, context, exc);return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def _remove_timer(self,context):
        if self._timer is not None:
            try:context.window_manager.event_timer_remove(self._timer)
            except (ReferenceError,RuntimeError,AttributeError):pass
            self._timer=None

    def _owns_session(self):
        try:return self._watcher is not None and body_live._WATCHERS.get(self._obj.as_pointer()) is self._watcher
        except (ReferenceError,AttributeError):return False

    def modal(self,context,event):
        try:
            if not self._owns_session():
                self._remove_timer(context);return {'CANCELLED'}
            if event.type=='ESC' and event.value=='PRESS':
                body_live.stop(self._obj);self._remove_timer(context)
                self._obj.b4ml.status='Live Solve stopped; preview retained'
                return {'CANCELLED','PASS_THROUGH'}
            if event.type=='TIMER' and time.monotonic()>=getattr(self,'_next_tick',0.):
                self._next_tick=time.monotonic()+.02
                if body_live.tick(self._obj)=='stopped':
                    self._remove_timer(context);return {'CANCELLED'}
                if context.area:context.area.tag_redraw()
                return {'RUNNING_MODAL'}
        except Exception as exc:
            self._remove_timer(context)
            try:
                if self._owns_session():body_live.stop(self._obj)
                self._obj.b4ml.status='Live Solve stopped: '+str(exc)
            except (ReferenceError,RuntimeError,AttributeError):pass
            self._remove_timer(context);self.report({'WARNING'},str(exc));return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def cancel(self,context):
        try:
            if self._owns_session():body_live.stop(self._obj)
        finally:self._remove_timer(context)


class B4ML_OT_contact(bpy.types.Operator):
    bl_idname='b4ml.contact'
    bl_label='Animation Contact'
    bl_options={'REGISTER','UNDO'}
    operation: EnumProperty(items=[
        ('CAPTURE','Capture','Capture the current evaluated point and orientation'),
        ('ACCEPT','Accept','Accept the selected provisional suggestion'),
        ('REJECT','Reject','Reject and disable the selected provisional suggestion'),
        ('ACCEPT_ALL','Accept All Proposed','Accept every compatible provisional suggestion'),
        ('REJECT_ALL','Reject All Proposed','Reject every compatible provisional suggestion'),
        ('PREVIOUS_PROPOSED','Previous Proposed','Select the previous compatible provisional interval and show its start frame'),
        ('NEXT_PROPOSED','Next Proposed','Select the next compatible provisional interval and show its start frame'),
        ('GO_BLEND_IN','Go Blend In','Move the playhead to the beginning of the selected contact blend-in'),
        ('GO_START','Go Start','Move the playhead to the selected contact start without changing animation'),
        ('GO_END','Go End','Move the playhead to the selected contact end without changing animation'),
        ('GO_BLEND_OUT','Go Blend Out','Move the playhead to the end of the selected contact blend-out'),
        ('SET_START','Set Start','Set the selected contact start from the playhead after validating all enabled intervals'),
        ('SET_END','Set End','Set the selected contact end from the playhead after validating all enabled intervals'),
        ('BIND_PROP','Bind Hand to Prop','Capture the selected hand contact in the chosen rigid object local space'),
        ('CLEAR_PROP','Clear Prop Hold','Return the selected hand contact to its captured world-space target'),
        ('BIND_SURFACE','Bind Foot to Platform','Capture the selected foot contact in the chosen rigid planar mesh local space'),
        ('CLEAR_SURFACE','Clear Platform Hold','Fix the selected foot contact at its current world-space target'),
        ('REMOVE','Remove','Remove the selected contact'),
        ('RESET','Restore Before Contacts','Restore the retained input interpolation candidate')])
    @classmethod
    def poll(cls,context):
        obj=workflow.active_rig(context)
        return bool(obj and not obj.b4ml.contact_running and not obj.b4ml.contact_suggest_running and not obj.b4ml.flight_running and not obj.b4ml.secondary_running and not obj.b4ml.cleanup_running and not obj.b4ml.temporal_running and not obj.b4ml.body_payload and not obj.b4ml.posing_payload and not obj.b4ml.quadruped_payload)
    def execute(self,context):
        obj=workflow.active_rig(context)
        try:
            if self.operation in {'ACCEPT_ALL', 'REJECT_ALL'}:
                _bulk_contact_review(obj, 'ACCEPTED' if self.operation == 'ACCEPT_ALL' else 'REJECTED')
            elif self.operation in {'PREVIOUS_PROPOSED', 'NEXT_PROPOSED'}:
                _navigate_contact_proposal(obj, context.scene,
                                           -1 if self.operation == 'PREVIOUS_PROPOSED' else 1)
            elif self.operation in {'GO_BLEND_IN','GO_START','GO_END','GO_BLEND_OUT','SET_START','SET_END'}:
                contacts.edit_interval(obj,context.scene,self.operation)
            elif self.operation in {'BIND_PROP','CLEAR_PROP','BIND_SURFACE','CLEAR_SURFACE'}:
                contacts.edit_prop_binding(obj,context.scene,self.operation,context.view_layer)
            else:
                backend=quadruped_contacts if detect_rig(obj.data.bones.keys()).family=='quadruped' else contacts
                if self.operation=='CAPTURE':backend.capture(obj,context.scene);return {'FINISHED'}
                if self.operation=='RESET':backend.restore_before_contacts(obj,context.scene);return {'FINISHED'}
                state=obj.b4ml
                if not 0<=state.contact_index<len(state.contacts):raise ValueError('Choose a contact')
                if self.operation=='ACCEPT':
                    state.contacts[state.contact_index].review_state='ACCEPTED';state.contacts[state.contact_index].enabled=True;state.status='Contact suggestion accepted; edit it before correction if needed'
                elif self.operation=='REJECT':
                    state.contacts[state.contact_index].review_state='REJECTED';state.contacts[state.contact_index].enabled=False;state.status='Contact suggestion rejected and excluded from correction'
                else:
                    state.contacts.remove(state.contact_index);state.contact_index=max(0,min(state.contact_index,len(state.contacts)-1))
        except Exception as exc:_report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}


class B4ML_OT_contact_suggest(bpy.types.Operator):
    bl_idname='b4ml.contact_suggest'
    bl_label='Suggest Foot Contacts'
    bl_description='Scan evaluated animation against the chosen static surface and create provisional intervals; no animation is changed'
    bl_options={'REGISTER','UNDO'}
    _timer=None
    _obj=None

    @classmethod
    def poll(cls,context):
        obj=workflow.active_rig(context)
        return bool(obj and obj.b4ml.candidate_action and not obj.b4ml.contact_suggest_running and not obj.b4ml.contact_running and not obj.b4ml.flight_running and not obj.b4ml.secondary_running and not obj.b4ml.cleanup_running and not obj.b4ml.body_payload and not obj.b4ml.posing_payload and not obj.b4ml.quadruped_payload)

    def execute(self,context):
        try:contacts.suggest(workflow.active_rig(context),context.scene)
        except Exception as exc:_report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self,context,event):
        if bpy.app.background or context.window is None:return self.execute(context)
        self._obj=workflow.active_rig(context)
        try:
            contacts.suggest_start(self._obj,context.scene)
            self._timer=context.window_manager.event_timer_add(.01,window=context.window);context.window_manager.modal_handler_add(self)
        except Exception as exc:
            contacts.suggest_abort(self._obj);self._remove_timer(context);_report_error(self, context, exc);return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def _remove_timer(self,context):
        if self._timer is not None:
            try:context.window_manager.event_timer_remove(self._timer)
            except (ReferenceError,RuntimeError):pass
            self._timer=None

    def modal(self,context,event):
        try:
            if not self._obj.b4ml.contact_suggest_running:self._remove_timer(context);return {'CANCELLED'}
            if event.type in ('ESC','RIGHTMOUSE'):
                contacts.suggest_abort(self._obj);self._remove_timer(context);return {'CANCELLED'}
            if event.type=='TIMER':
                if contacts.suggest_step(self._obj):self._remove_timer(context);return {'FINISHED'}
                if context.area:context.area.tag_redraw()
        except Exception as exc:
            try:contacts.suggest_abort(self._obj)
            except (ReferenceError,RuntimeError):pass
            self._remove_timer(context);_report_error(self, context, exc);return {'CANCELLED'}
        if event.type in ('MIDDLEMOUSE','WHEELUPMOUSE','WHEELDOWNMOUSE','MOUSEMOVE'):return {'PASS_THROUGH'}
        return {'RUNNING_MODAL'}

    def cancel(self,context):
        try:
            if self._obj:contacts.suggest_abort(self._obj)
        finally:self._remove_timer(context)


class B4ML_OT_quadruped_gait(bpy.types.Operator):
    bl_idname = 'b4ml.quadruped_gait'
    bl_label = 'Procedural Gait Phases'
    bl_description = 'Review support phases from accepted paw contacts without changing animation'
    bl_options = {'REGISTER', 'UNDO'}
    operation: EnumProperty(items=[
        ('ANALYZE', 'Analyze Gait Phases', 'Classify exact support intervals from accepted paw contacts'),
        ('PREVIOUS', 'Previous Phase', 'Move the playhead to the previous support phase'),
        ('NEXT', 'Next Phase', 'Move the playhead to the next support phase'),
        ('CLEAR', 'Clear Phase Report', 'Remove the saved procedural phase report')])

    @classmethod
    def poll(cls, context):
        obj = workflow.active_rig(context)
        state = obj.b4ml if obj else None
        playing = bool(context.screen and context.screen.is_animation_playing)
        return bool(obj and not playing and not state.contact_running and
                    not state.contact_suggest_running and not state.flight_running and
                    not state.secondary_running and not state.cleanup_running and
                    not state.temporal_running and not state.body_running and not state.body_live and
                    not state.body_payload and not state.posing_payload and not state.quadruped_payload)

    def execute(self, context):
        obj = workflow.active_rig(context)
        try:
            if self.operation == 'ANALYZE':
                quadruped_gait.analyze(obj, context.scene)
            elif self.operation == 'PREVIOUS':
                quadruped_gait.navigate(obj, context.scene, -1)
            elif self.operation == 'NEXT':
                quadruped_gait.navigate(obj, context.scene, 1)
            else:
                quadruped_gait.clear(obj)
        except Exception as exc:
            _report_error(self, context, exc)
            return {'CANCELLED'}
        return {'FINISHED'}


class B4ML_OT_temporal_preview(bpy.types.Operator):
    bl_idname='b4ml.temporal_preview'
    bl_label='Generate Whole-body Preview'
    bl_description='Generate a procedural motion trajectory through authored poses; Escape preserves the source'
    bl_options={'REGISTER','UNDO'}
    _timer=None
    _obj=None

    @classmethod
    def poll(cls,context):
        obj=workflow.active_rig(context)
        return bool(obj and len(obj.b4ml.anchors)>=2 and not obj.b4ml.candidate_action and not obj.b4ml.posing_payload and not obj.b4ml.body_payload and not obj.b4ml.quadruped_payload and not obj.b4ml.temporal_running and not obj.b4ml.body_running and not obj.b4ml.body_live and not obj.b4ml.contact_running and not obj.b4ml.contact_suggest_running and not obj.b4ml.flight_running and not obj.b4ml.secondary_running and not obj.b4ml.cleanup_running and not workflow.motion_layer.find(obj))

    def execute(self,context):
        try:temporal_preview.run(workflow.active_rig(context),context.scene)
        except Exception as exc:
            _report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self,context,event):
        if bpy.app.background or context.window is None:return self.execute(context)
        self._obj=workflow.active_rig(context)
        try:
            temporal_preview.start(self._obj,context.scene)
            self._timer=context.window_manager.event_timer_add(.01,window=context.window)
            context.window_manager.modal_handler_add(self)
        except Exception as exc:
            temporal_preview.abort(self._obj);self._remove_timer(context)
            _report_error(self, context, exc);return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def _remove_timer(self,context):
        if self._timer is not None:
            try:context.window_manager.event_timer_remove(self._timer)
            except (ReferenceError,RuntimeError):pass
            self._timer=None

    def modal(self,context,event):
        try:
            if not self._obj.b4ml.temporal_running:
                self._remove_timer(context);return {'CANCELLED'}
            if event.type in ('ESC','RIGHTMOUSE'):
                temporal_preview.abort(self._obj);self._remove_timer(context);return {'CANCELLED'}
            if event.type=='TIMER' and time.monotonic()>=getattr(self,'_next_tick',0.):
                self._next_tick=time.monotonic()+.01
                if temporal_preview.step(self._obj):
                    self._remove_timer(context);return {'FINISHED'}
                if context.area:context.area.tag_redraw()
        except Exception as exc:
            try:temporal_preview.abort(self._obj)
            except (ReferenceError,RuntimeError):pass
            self._remove_timer(context)
            try:self._obj.b4ml.status='Motion generation failed: '+str(exc)
            except ReferenceError:pass
            _report_error(self, context, exc);return {'CANCELLED'}
        if event.type in ('MIDDLEMOUSE','WHEELUPMOUSE','WHEELDOWNMOUSE','MOUSEMOVE'):
            return {'PASS_THROUGH'}
        return {'RUNNING_MODAL'}

    def cancel(self,context):
        try:
            if self._obj:temporal_preview.abort(self._obj)
        finally:self._remove_timer(context)


class B4ML_OT_temporal_cancel(bpy.types.Operator):
    bl_idname='b4ml.temporal_cancel'
    bl_label='Cancel Motion Generation'
    def execute(self,context):
        obj=workflow.active_rig(context)
        if obj is not None:temporal_preview.abort(obj)
        return {'FINISHED'}

class B4ML_OT_contact_solve(bpy.types.Operator):
    bl_idname='b4ml.contact_solve'
    bl_label='Correct Contacts'
    bl_description='Correct explicit contacts on a copied animation candidate; Escape restores the input'
    bl_options={'REGISTER','UNDO'}
    _timer=None
    _obj=None

    @classmethod
    def poll(cls,context):
        obj=workflow.active_rig(context)
        return bool(obj and obj.b4ml.candidate_action and not obj.b4ml.contact_running and not obj.b4ml.contact_suggest_running and not obj.b4ml.flight_running and not obj.b4ml.secondary_running and not obj.b4ml.cleanup_running)

    def execute(self,context):
        obj=workflow.active_rig(context)
        backend=quadruped_contacts if detect_rig(obj.data.bones.keys()).family=='quadruped' else contacts
        try:backend.solve(obj,context.scene)
        except Exception as exc:
            _report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self,context,event):
        if bpy.app.background or context.window is None:return self.execute(context)
        self._obj=workflow.active_rig(context)
        self._backend=quadruped_contacts if detect_rig(self._obj.data.bones.keys()).family=='quadruped' else contacts
        try:
            self._backend.start(self._obj,context.scene)
            self._timer=context.window_manager.event_timer_add(.01,window=context.window)
            context.window_manager.modal_handler_add(self)
        except Exception as exc:
            self._backend.abort(self._obj);self._remove_timer(context)
            _report_error(self, context, exc);return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def _remove_timer(self,context):
        if self._timer is not None:
            try:context.window_manager.event_timer_remove(self._timer)
            except (ReferenceError,RuntimeError):pass
            self._timer=None

    def modal(self,context,event):
        try:
            if not self._obj.b4ml.contact_running:
                self._remove_timer(context);return {'CANCELLED'}
            if event.type in ('ESC','RIGHTMOUSE'):
                self._backend.abort(self._obj);self._remove_timer(context);return {'CANCELLED'}
            if event.type=='TIMER' and time.monotonic()>=getattr(self,'_next_tick',0.):
                self._next_tick=time.monotonic()+.01
                if self._backend.step(self._obj):
                    self._remove_timer(context);return {'FINISHED'}
                if context.area:context.area.tag_redraw()
        except Exception as exc:
            try:self._backend.abort(self._obj)
            except (ReferenceError,RuntimeError):pass
            self._remove_timer(context)
            try:self._obj.b4ml.status='Contact correction failed: '+str(exc)
            except ReferenceError:pass
            _report_error(self, context, exc);return {'CANCELLED'}
        if event.type in ('MIDDLEMOUSE','WHEELUPMOUSE','WHEELDOWNMOUSE','MOUSEMOVE'):
            return {'PASS_THROUGH'}
        return {'RUNNING_MODAL'}

    def cancel(self,context):
        try:
            if self._obj and self._backend:self._backend.abort(self._obj)
        finally:self._remove_timer(context)


class B4ML_OT_flight(bpy.types.Operator):
    bl_idname='b4ml.flight'
    bl_label='Airborne Interval'
    bl_options={'REGISTER','UNDO'}
    operation: EnumProperty(items=[('ADD','Add','Use adjacent priority poses'),('REMOVE','Remove','Remove the selected flight interval'),('RESET','Restore Before Flight','Restore the retained input candidate')])
    @classmethod
    def poll(cls,context):
        obj=workflow.active_rig(context)
        return bool(obj and obj.b4ml.candidate_action and not obj.b4ml.flight_running and not obj.b4ml.contact_running and not obj.b4ml.contact_suggest_running and not obj.b4ml.secondary_running and not obj.b4ml.cleanup_running)
    def execute(self,context):
        obj=workflow.active_rig(context)
        try:
            if self.operation=='ADD':flight.add(obj,context.scene)
            elif self.operation=='RESET':flight.restore(obj,context.scene)
            else:
                state=obj.b4ml
                if not 0<=state.flight_index<len(state.flights):raise ValueError('Choose a flight interval to remove')
                state.flights.remove(state.flight_index);state.flight_index=max(0,min(state.flight_index,len(state.flights)-1))
        except Exception as exc:_report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}

class B4ML_OT_flight_solve(bpy.types.Operator):
    bl_idname='b4ml.flight_solve'
    bl_label='Correct COM Flight'
    bl_description='Fit scene-gravity COM motion on a copied animation candidate; Escape restores the input'
    bl_options={'REGISTER','UNDO'}
    _timer=None
    _obj=None

    @classmethod
    def poll(cls,context):
        obj=workflow.active_rig(context)
        return bool(obj and obj.b4ml.candidate_action and not obj.b4ml.flight_running and not obj.b4ml.contact_running and not obj.b4ml.contact_suggest_running and not obj.b4ml.secondary_running and not obj.b4ml.cleanup_running)

    def execute(self,context):
        try:flight.solve(workflow.active_rig(context),context.scene)
        except Exception as exc:
            _report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self,context,event):
        if bpy.app.background or context.window is None:return self.execute(context)
        self._obj=workflow.active_rig(context)
        try:
            flight.start(self._obj,context.scene)
            self._timer=context.window_manager.event_timer_add(.01,window=context.window)
            context.window_manager.modal_handler_add(self)
        except Exception as exc:
            flight.abort(self._obj);self._remove_timer(context)
            _report_error(self, context, exc);return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def _remove_timer(self,context):
        if self._timer is not None:
            try:context.window_manager.event_timer_remove(self._timer)
            except (ReferenceError,RuntimeError):pass
            self._timer=None

    def modal(self,context,event):
        try:
            if not self._obj.b4ml.flight_running:
                self._remove_timer(context);return {'CANCELLED'}
            if event.type in ('ESC','RIGHTMOUSE'):
                flight.abort(self._obj);self._remove_timer(context);return {'CANCELLED'}
            if event.type=='TIMER' and time.monotonic()>=getattr(self,'_next_tick',0.):
                self._next_tick=time.monotonic()+.01
                if flight.step(self._obj):
                    self._remove_timer(context);return {'FINISHED'}
                if context.area:context.area.tag_redraw()
        except Exception as exc:
            try:flight.abort(self._obj)
            except (ReferenceError,RuntimeError):pass
            self._remove_timer(context)
            try:self._obj.b4ml.status='Flight correction failed: '+str(exc)
            except ReferenceError:pass
            _report_error(self, context, exc);return {'CANCELLED'}
        if event.type in ('MIDDLEMOUSE','WHEELUPMOUSE','WHEELDOWNMOUSE','MOUSEMOVE'):
            return {'PASS_THROUGH'}
        return {'RUNNING_MODAL'}

    def cancel(self,context):
        try:
            if self._obj:flight.abort(self._obj)
        finally:self._remove_timer(context)


class B4ML_OT_cleanup(bpy.types.Operator):
    bl_idname='b4ml.cleanup'
    bl_label='Animation Cleanup'
    bl_options={'REGISTER','UNDO'}
    operation: EnumProperty(items=[('RESET','Restore Before Cleanup','Restore the retained input candidate')])

    @classmethod
    def poll(cls,context):
        obj=workflow.active_rig(context)
        return bool(obj and obj.b4ml.candidate_action and not obj.b4ml.cleanup_running and
                    not obj.b4ml.secondary_running and not obj.b4ml.flight_running and
                    not obj.b4ml.contact_running and not obj.b4ml.contact_suggest_running)

    def execute(self,context):
        try:cleanup.restore(workflow.active_rig(context),context.scene)
        except Exception as exc:_report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}


class B4ML_OT_cleanup_solve(bpy.types.Operator):
    bl_idname='b4ml.cleanup_solve'
    bl_label='Preview Animation Cleanup'
    bl_description='Smooth and simplify selected copied animation curves while preserving priority poses and accepted contacts'
    bl_options={'REGISTER','UNDO'}
    _timer=None
    _obj=None

    @classmethod
    def poll(cls,context):
        obj=workflow.active_rig(context)
        return bool(obj and obj.b4ml.candidate_action and not obj.b4ml.cleanup_running and
                    not obj.b4ml.secondary_running and not obj.b4ml.flight_running and
                    not obj.b4ml.contact_running and not obj.b4ml.contact_suggest_running)

    def execute(self,context):
        try:cleanup.solve(workflow.active_rig(context),context.scene)
        except Exception as exc:_report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self,context,event):
        if bpy.app.background or context.window is None:return self.execute(context)
        self._obj=workflow.active_rig(context)
        try:
            cleanup.start(self._obj,context.scene)
            self._timer=context.window_manager.event_timer_add(.01,window=context.window)
            context.window_manager.modal_handler_add(self)
        except Exception as exc:
            cleanup.abort(self._obj);self._remove_timer(context)
            _report_error(self, context, exc);return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def _remove_timer(self,context):
        if self._timer is not None:
            try:context.window_manager.event_timer_remove(self._timer)
            except (ReferenceError,RuntimeError):pass
            self._timer=None

    def modal(self,context,event):
        try:
            if not self._obj.b4ml.cleanup_running:
                self._remove_timer(context);return {'CANCELLED'}
            if event.type in ('ESC','RIGHTMOUSE'):
                cleanup.abort(self._obj);self._remove_timer(context);return {'CANCELLED'}
            if event.type=='TIMER' and time.monotonic()>=getattr(self,'_next_tick',0.):
                self._next_tick=time.monotonic()+.01
                if cleanup.step(self._obj):
                    self._remove_timer(context);return {'FINISHED'}
                if context.area:context.area.tag_redraw()
        except Exception as exc:
            try:cleanup.abort(self._obj)
            except (ReferenceError,RuntimeError):pass
            self._remove_timer(context)
            try:self._obj.b4ml.status='Animation cleanup failed: '+str(exc)
            except ReferenceError:pass
            _report_error(self, context, exc);return {'CANCELLED'}
        if event.type in ('MIDDLEMOUSE','WHEELUPMOUSE','WHEELDOWNMOUSE','MOUSEMOVE'):
            return {'PASS_THROUGH'}
        return {'RUNNING_MODAL'}

    def cancel(self,context):
        try:
            if self._obj and self._timer is not None:cleanup.abort(self._obj)
        finally:self._remove_timer(context)


class B4ML_OT_secondary(bpy.types.Operator):
    bl_idname='b4ml.secondary'
    bl_label='Secondary Motion'
    bl_options={'REGISTER','UNDO'}
    operation: EnumProperty(items=[('RESET','Restore Before Secondary Motion','Restore the retained input candidate')])

    @classmethod
    def poll(cls,context):
        obj=workflow.active_rig(context)
        return bool(obj and obj.b4ml.candidate_action and
                    not secondary_motion.busy(obj.b4ml))

    def execute(self,context):
        try:secondary_motion.restore(workflow.active_rig(context),context.scene)
        except Exception as exc:_report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}


class B4ML_OT_secondary_select_chain(bpy.types.Operator):
    bl_idname='b4ml.secondary_select_chain'
    bl_label='Select Direct Chain'
    bl_description='Select a bounded direct control hierarchy from the active pose control; does not infer hair, cloth, flesh, or other secondary-part meaning'
    bl_options={'REGISTER','UNDO'}
    direction: EnumProperty(items=(('CHILDREN','Toward Children',''),('PARENTS','Toward Parents','')),default='CHILDREN',options={'HIDDEN'})
    max_controls: IntProperty(default=4,min=2,max=32,options={'HIDDEN'})

    @classmethod
    def poll(cls,context):
        obj=workflow.active_rig(context)
        return bool(obj and context.active_pose_bone and obj.b4ml.candidate_action and
                    ((obj.b4ml.secondary_space == 'LOCAL' and obj.b4ml.secondary_rotation) or
                     (obj.b4ml.secondary_space == 'WORLD' and obj.b4ml.secondary_location)) and
                    not obj.b4ml.temporal_running and not obj.b4ml.body_running and
                    not obj.b4ml.body_live and not obj.b4ml.body_payload and
                    not obj.b4ml.posing_payload and not obj.b4ml.quadruped_payload and
                    not obj.b4ml.secondary_running and not obj.b4ml.flight_running and
                    not obj.b4ml.contact_running and not obj.b4ml.contact_suggest_running and
                    not obj.b4ml.cleanup_running)

    def execute(self,context):
        obj=workflow.active_rig(context)
        try:
            secondary_motion.select_chain(obj,context.active_pose_bone.name,
                                          self.direction,self.max_controls)
        except Exception as exc:_report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}


class B4ML_OT_secondary_selection_swap(bpy.types.Operator):
    bl_idname='b4ml.secondary_selection_swap'
    bl_label='Swap Previous Selection'
    bl_description='Exchange the current pose-control selection, active control, and chain mode with the last selection replaced by Select Direct Chain'
    bl_options={'REGISTER','UNDO'}

    @classmethod
    def poll(cls,context):
        obj=workflow.active_rig(context)
        return bool(obj and obj.mode == 'POSE' and obj.b4ml.candidate_action and
                    obj.b4ml.secondary_selection_swap and
                    not obj.b4ml.temporal_running and not obj.b4ml.body_running and
                    not obj.b4ml.body_live and not obj.b4ml.body_payload and
                    not obj.b4ml.posing_payload and not obj.b4ml.quadruped_payload and
                    not obj.b4ml.secondary_running and not obj.b4ml.flight_running and
                    not obj.b4ml.contact_running and not obj.b4ml.contact_suggest_running and
                    not obj.b4ml.cleanup_running)

    def execute(self,context):
        try:secondary_motion.swap_selection(workflow.active_rig(context))
        except Exception as exc:_report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}


class B4ML_OT_secondary_control_load(bpy.types.Operator):
    bl_idname='b4ml.secondary_control_load'
    bl_label='Secondary Control Load'
    bl_description='Assign or clear a persistent world force, mass, local application offset, and rotational inertia on selected pose controls'
    bl_options={'REGISTER','UNDO'}
    operation: EnumProperty(items=(
        ('ASSIGN','Assign to Selected','Store the displayed force, mass, local offset, and rotational inertia on every selected pose control'),
        ('LOAD_ACTIVE','Load From Active','Recall the active selected control assignment into the displayed settings'),
        ('CLEAR','Clear Selected','Remove the stored load and torque settings from every selected pose control'),
        ('CLEAR_ALL','Clear All','Remove all stored control loads, including an invalid record')),
                            default='ASSIGN',options={'HIDDEN'})

    @classmethod
    def description(cls,context,properties):
        return {
            'ASSIGN':'Store the displayed world force, mass, local application offset, and rotational inertia on every selected pose control',
            'LOAD_ACTIVE':'Recall the active selected control assignment into the displayed force, mass, local offset, and inertia settings',
            'CLEAR':'Remove the stored load and torque settings from every selected pose control',
            'CLEAR_ALL':'Remove all stored control loads, including an invalid record',
        }.get(properties.operation,cls.bl_description)

    @classmethod
    def poll(cls,context):
        obj=workflow.active_rig(context)
        return bool(obj and obj.mode=='POSE' and obj.b4ml.candidate_action and
                    not secondary_motion.busy(obj.b4ml))

    def execute(self,context):
        obj=workflow.active_rig(context)
        try:
            if self.operation=='ASSIGN':
                secondary_motion.assign_control_loads(
                    obj,obj.b4ml.secondary_load_force,obj.b4ml.secondary_load_mass,
                    obj.b4ml.secondary_load_offset,obj.b4ml.secondary_load_inertia)
            elif self.operation=='LOAD_ACTIVE':secondary_motion.load_active_control_load(obj)
            elif self.operation=='CLEAR':secondary_motion.clear_control_loads(obj)
            elif self.operation=='CLEAR_ALL':secondary_motion.clear_all_control_loads(obj)
            else:raise ValueError('Unknown secondary control-load operation')
        except Exception as exc:_report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}


class B4ML_OT_secondary_sphere(bpy.types.Operator):
    bl_idname='b4ml.secondary_sphere'
    bl_label='Secondary Sphere Set'
    bl_description='Create, add, fit, or remove explicit static or directly animated spherical colliders'
    bl_options={'REGISTER','UNDO'}
    operation: EnumProperty(items=(
        ('ADD','Add Sphere','Copy the displayed center and radius into the collider set'),
        ('PROXY','Create Proxy','Create and add an unparented sphere proxy from the staged geometric object bounds'),
        ('FIT','Fit Radius','Set the explicit radius from the collider geometric bounds'),
        ('REMOVE','Remove Sphere','Remove one sphere from the collider set'),
        ('CLEAR','Clear Spheres','Remove every listed sphere collider')),
        default='ADD',options={'HIDDEN'})
    index: IntProperty(default=-1,options={'HIDDEN'})

    @classmethod
    def poll(cls,context):
        obj=workflow.active_rig(context)
        return bool(obj and obj.b4ml.candidate_action and
                    not secondary_motion.busy(obj.b4ml))

    def execute(self,context):
        obj=workflow.active_rig(context)
        try:
            if self.operation=='ADD':
                secondary_motion.add_sphere_collider(obj,context.scene)
            elif self.operation=='PROXY':
                secondary_motion.create_sphere_proxy_from_bounds(obj,context.scene)
            elif self.operation=='FIT':
                secondary_motion.fit_sphere_collider_radius(obj,context.scene,self.index)
            elif self.operation=='REMOVE':
                secondary_motion.remove_sphere_collider(obj,self.index)
            elif self.operation=='CLEAR':
                secondary_motion.clear_sphere_colliders(obj)
            else:
                raise ValueError('Unknown sphere-set operation')
        except Exception as exc:_report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}


class B4ML_OT_secondary_solve(bpy.types.Operator):
    bl_idname='b4ml.secondary_solve'
    bl_label='Preview Secondary Motion'
    bl_description='Add deterministic damped follow-through to selected controls on a copied animation candidate; Escape restores the input'
    bl_options={'REGISTER','UNDO'}
    _timer=None
    _obj=None
    _backend=None

    @classmethod
    def poll(cls,context):
        obj=workflow.active_rig(context)
        return bool(obj and obj.b4ml.candidate_action and
                    not secondary_motion.busy(obj.b4ml))

    def execute(self,context):
        try:secondary_motion.solve(workflow.active_rig(context),context.scene)
        except Exception as exc:_report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self,context,event):
        if bpy.app.background or context.window is None:return self.execute(context)
        self._obj=workflow.active_rig(context)
        try:
            secondary_motion.start(self._obj,context.scene)
            self._timer=context.window_manager.event_timer_add(.01,window=context.window)
            context.window_manager.modal_handler_add(self)
        except Exception as exc:
            secondary_motion.abort(self._obj);self._remove_timer(context)
            _report_error(self, context, exc);return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def _remove_timer(self,context):
        if self._timer is not None:
            try:context.window_manager.event_timer_remove(self._timer)
            except (ReferenceError,RuntimeError):pass
            self._timer=None

    def modal(self,context,event):
        try:
            if not self._obj.b4ml.secondary_running:
                self._remove_timer(context);return {'CANCELLED'}
            if event.type in ('ESC','RIGHTMOUSE'):
                secondary_motion.abort(self._obj);self._remove_timer(context);return {'CANCELLED'}
            if event.type=='TIMER' and time.monotonic()>=getattr(self,'_next_tick',0.):
                self._next_tick=time.monotonic()+.01
                if secondary_motion.step(self._obj):
                    self._remove_timer(context);return {'FINISHED'}
                if context.area:context.area.tag_redraw()
        except Exception as exc:
            try:secondary_motion.abort(self._obj)
            except (ReferenceError,RuntimeError):pass
            self._remove_timer(context)
            try:self._obj.b4ml.status='Secondary motion failed: '+str(exc)
            except ReferenceError:pass
            _report_error(self, context, exc);return {'CANCELLED'}
        if event.type in ('MIDDLEMOUSE','WHEELUPMOUSE','WHEELDOWNMOUSE','MOUSEMOVE'):
            return {'PASS_THROUGH'}
        return {'RUNNING_MODAL'}

    def cancel(self,context):
        try:
            # A completed/cancelled modal has already released its timer. Do
            # not let Blender's delayed cancel callback abort a newer job.
            if self._obj and self._timer is not None:secondary_motion.abort(self._obj)
        finally:self._remove_timer(context)


class B4ML_OT_support(bpy.types.Operator):
    bl_idname='b4ml.support'
    bl_label='Analyze Center of Mass / Support'
    bl_options={'REGISTER','UNDO'}
    operation: EnumProperty(items=[('INITIALIZE','Initialize Mass Model','Create an editable approximation without changing the rig'),('ANALYZE','Analyze Current Pose','Save a static COM/support snapshot; does not modify animation')])
    @classmethod
    def poll(cls,context):
        obj=workflow.active_rig(context)
        return bool(obj and not obj.b4ml.body_running and not obj.b4ml.contact_running and not obj.b4ml.contact_suggest_running and not obj.b4ml.flight_running and not obj.b4ml.secondary_running and not obj.b4ml.cleanup_running)
    def execute(self,context):
        obj=workflow.active_rig(context)
        try:
            if self.operation=='INITIALIZE':support.initialize(obj)
            else:support.snapshot(obj,context.scene,context.evaluated_depsgraph_get())
        except Exception as exc:_report_error(self, context, exc);return {'CANCELLED'}
        return {'FINISHED'}


class B4ML_OT_motion_result(bpy.types.Operator):
    bl_idname='b4ml.motion_result'
    bl_label='Preview Saved Motion'
    bl_description='Restore the complete editable pose and native trajectory as a reversible preview'
    bl_options={'REGISTER','UNDO'}
    result_name: StringProperty()
    @classmethod
    def poll(cls,context):
        obj=workflow.active_rig(context)
        return bool(obj and not obj.b4ml.candidate_action and not obj.b4ml.body_payload and not obj.b4ml.posing_payload and not obj.b4ml.quadruped_payload and not obj.b4ml.contact_suggest_running and not obj.b4ml.secondary_running and not obj.b4ml.cleanup_running)
    def execute(self,context):
        obj=workflow.active_rig(context)
        try:workflow.preview_motion_result(obj,context.scene,bpy.data.objects.get(self.result_name))
        except Exception as exc:_report_error(self, context, exc);return {'CANCELLED'}
        visible=workflow.motion_layer.find(obj)
        context.view_layer.objects.active=visible;visible.select_set(True)
        return {'FINISHED'}


CLASSES = (B4ML_PG_anchor, B4ML_PG_target, B4ML_PG_joint_limit, B4ML_PG_mass_segment, B4ML_PG_secondary_sphere, B4ML_PG_contact, B4ML_PG_flight, B4ML_PG_settings, B4ML_OT_anchor_page, B4ML_OT_mapping_correction, B4ML_OT_transition_timing, B4ML_OT_breakdown_pose, B4ML_OT_inbetween_series, B4ML_OT_retime_anchor, B4ML_OT_ripple_retime, B4ML_OT_pose_spacing_scale, B4ML_OT_pose_spacing_equalize, B4ML_OT_transition_timing_transfer, B4ML_OT_action, B4ML_OT_pose, B4ML_OT_body, B4ML_OT_body_solve, B4ML_OT_body_live, B4ML_OT_quadruped_pose, B4ML_OT_contact, B4ML_OT_contact_suggest, B4ML_OT_quadruped_gait, B4ML_OT_contact_solve, B4ML_OT_temporal_preview, B4ML_OT_temporal_cancel, B4ML_OT_flight, B4ML_OT_flight_solve, B4ML_OT_cleanup, B4ML_OT_cleanup_solve, B4ML_OT_secondary, B4ML_OT_secondary_select_chain, B4ML_OT_secondary_selection_swap, B4ML_OT_secondary_control_load, B4ML_OT_secondary_sphere, B4ML_OT_secondary_solve, B4ML_OT_support, B4ML_OT_motion_result)

def register():
    registered = []
    try:
        for cls in CLASSES:
            bpy.utils.register_class(cls)
            registered.append(cls)
        bpy.types.Object.b4ml = PointerProperty(type=B4ML_PG_settings)
        quadruped_pose.register()
        quadruped_contacts.register()
        body_preview.register()
        contacts.register()
        contact_visualization.register()
        flight.register()
        cleanup.register()
        secondary_motion.register()
        temporal_preview.register()
        from . import ui_workflow
        ui_workflow.register()
    except Exception:
        try:
            from . import ui_workflow as _uw; _uw.unregister()
        except Exception:
            pass
        temporal_preview.unregister()
        secondary_motion.unregister()
        cleanup.unregister()
        flight.unregister()
        contact_visualization.unregister()
        contacts.unregister()
        quadruped_contacts.unregister()
        body_preview.unregister()
        quadruped_pose.unregister()
        if hasattr(bpy.types.Object, 'b4ml'):
            del bpy.types.Object.b4ml
        for cls in reversed(registered):
            bpy.utils.unregister_class(cls)
        raise

def unregister():
    try:
        from . import ui_workflow
        ui_workflow.unregister()
    except Exception as exc:
        print('[b4ml] ui_workflow.unregister failed:', exc)
    temporal_preview.unregister()
    secondary_motion.unregister()
    cleanup.unregister()
    flight.unregister()
    contact_visualization.unregister()
    contacts.unregister()
    quadruped_contacts.unregister()
    body_preview.unregister()
    quadruped_pose.unregister()
    if hasattr(bpy.types.Object, 'b4ml'):
        del bpy.types.Object.b4ml
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
