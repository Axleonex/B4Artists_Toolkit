"""Native panel for saved poses and reversible interpolation candidates."""
import bpy
import json
import time
import math
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, FloatProperty, FloatVectorProperty, IntProperty, PointerProperty, StringProperty
from . import bl_info, workflow, posing, body_preview, body_live, quadruped_pose, quadruped_contacts, quadruped_gait, contacts, contact_visualization, support, flight, secondary_motion, cleanup, temporal_preview, rig_diagnostics, rig_mapping
from .rigs import detect_rig


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


def _draw_contact_interval_controls(layout,state):
    jump=layout.row(align=True)
    jump.operator('b4ml.contact',text='Blend In').operation='GO_BLEND_IN'
    jump.operator('b4ml.contact',text='Hold Start').operation='GO_START'
    jump=layout.row(align=True)
    jump.operator('b4ml.contact',text='Hold End').operation='GO_END'
    jump.operator('b4ml.contact',text='Blend Out').operation='GO_BLEND_OUT'
    trim=layout.row(align=True);trim.enabled=bool(state.candidate_action)
    trim.operator('b4ml.contact',text='Set Start').operation='SET_START'
    trim.operator('b4ml.contact',text='Set End').operation='SET_END'

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
    status: StringProperty(default="Capture poses at two or more frames")


def _draw_wrapped(layout,text,icon='NONE',width=30):
    words=str(text).split();lines=[];line=[]
    for word in words:
        if line and len(' '.join(line+[word]))>width:
            lines.append(' '.join(line));line=[word]
        else:line.append(word)
    if line:lines.append(' '.join(line))
    for index,value in enumerate(lines):
        layout.label(text=value,icon=icon if index==0 else 'BLANK1')


def _draw_rig_diagnostics(layout, state, report):
    box=layout.box()
    box.prop(state,'show_rig_diagnostics',icon='TRIA_DOWN' if state.show_rig_diagnostics else 'TRIA_RIGHT',emboss=False)
    if not state.show_rig_diagnostics:return
    if report is None:
        box.label(text='Click Inspect / Refresh above.',icon='INFO');return
    box.label(text='Snapshot; refresh after rig edits',icon='INFO')
    box.label(text=report['profile'],icon='ARMATURE_DATA')
    box.label(text=f"{report['family']} / {report['mapping_schema']}")
    box.label(text=(f"Semantic roles: {report['mapped_required_role_count']}/"
                    f"{report['required_role_count']}"))
    box.label(text=f"Mapped controls: {report['mapped_control_count']}")
    box.label(text=f"Directly writable: {report['writable_control_count']}")
    if report['correction_state']=='active':
        box.label(text=f"Manual corrections: {len(report['manual_corrections'])}",icon='CHECKMARK')
    elif report['correction_state']=='invalid':
        _draw_wrapped(box,report['correction_error'],icon='ERROR')
    excluded=[(key,value) for key,value in report['excluded_bone_counts'].items() if value]
    if excluded:
        box.label(text='Excluded from B4ML controls:')
        for key,value in excluded:box.label(text=f'{key.title()}: {value}')
    for workflow_row in report['workflows']:
        if not workflow_row['applicable']:continue
        row=box.row();row.alert=not workflow_row['ready']
        short_label={'humanoid_whole_body':'Whole-Body Pose',
                     'quadruped_whole_body':'Four-Paw Whole-Body Pose'}.get(
                         workflow_row['id'],workflow_row['label'])
        row.label(text=short_label,
                  icon='CHECKMARK' if workflow_row['ready'] else 'ERROR')
        if not workflow_row['ready']:_draw_wrapped(box,workflow_row['detail'])
    if report['missing_roles']:
        box.label(text='Missing semantic roles:',icon='ERROR')
        for start in range(0,len(report['missing_roles']),4):
            box.label(text=', '.join(report['missing_roles'][start:start+4]))
    if report['blocked_mapped_controls']:
        box.label(text='Blocked mapped controls:',icon='ERROR')
        box.label(text=', '.join(report['blocked_mapped_controls'][:4]))
    if report['unsafe_mapped_controls']:
        box.label(text='Structural bones mapped as controls:',icon='ERROR')
        box.label(text=', '.join(report['unsafe_mapped_controls'][:4]))
    for warning in report['warnings']:_draw_wrapped(box,warning,icon='INFO')
    box.prop(state,'show_rig_role_mappings',icon='TRIA_DOWN' if state.show_rig_role_mappings else 'TRIA_RIGHT',emboss=False)
    if state.show_rig_role_mappings:
        for mapping in report['mapped_roles']:
            box.label(text=mapping['role']+' -> '+mapping['bone'])


def _mapping_busy(state):
    return bool(state.candidate_action or state.posing_payload or state.body_payload
                or state.quadruped_payload or state.temporal_running
                or state.contact_running or state.contact_suggest_running
                or state.flight_running or state.secondary_running
                or state.cleanup_running)


def _draw_rig_mapping_editor(layout,obj,state,profile,correction_rows,correction_error):
    box=layout.box()
    box.prop(state,'show_mapping_corrections',
             icon='TRIA_DOWN' if state.show_mapping_corrections else 'TRIA_RIGHT',
             emboss=False)
    if not state.show_mapping_corrections and not correction_error:return
    if correction_error:
        _draw_wrapped(box,correction_error,icon='ERROR')
        clear=box.row();clear.enabled=not _mapping_busy(state)
        clear.operator('b4ml.mapping_correction',text='Clear Invalid Corrections',icon='X').operation='CLEAR_ALL'
        return
    if profile.family!='humanoid':
        box.label(text='Available on recognized humanoid adapters.',icon='INFO');return
    col=box.column();col.enabled=not _mapping_busy(state)
    col.prop(state,'mapping_role',text='Role')
    col.prop_search(state,'mapping_bone',obj.data,'bones',text='Bone')
    row=col.row(align=True)
    row.operator('b4ml.mapping_correction',text='Apply Role').operation='APPLY'
    clear=row.operator('b4ml.mapping_correction',text='Clear Role').operation='CLEAR_ROLE'
    clear_all=col.row();clear_all.enabled=bool(correction_rows) or bool(correction_error)
    clear_all.operator('b4ml.mapping_correction',text='Clear All Corrections',icon='X').operation='CLEAR_ALL'
    if correction_rows:
        box.label(text='Active corrections:')
        for role,bone in correction_rows:box.label(text=role+' -> '+bone)
    else:box.label(text='No manual corrections.',icon='INFO')

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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
        self.left_frame=values['left'][0]
        self.right_frame=values['right'][0]
        return context.window_manager.invoke_props_dialog(self,width=340)

    def execute(self, context):
        obj=workflow.active_rig(context)
        try:
            workflow.create_inbetween_series(obj,context.scene,self.count)
        except Exception as exc:
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
        self.source_frame=values['source_frame']
        self.destination_frame=values['destination_frame']
        return context.window_manager.invoke_props_dialog(self,width=330)

    def execute(self, context):
        obj=workflow.active_rig(context)
        try:
            workflow.retime_anchor(
                obj,context.scene,self.source_frame,self.destination_frame)
        except Exception as exc:
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
        self.pivot_frame=values['pivot_frame'];self.moved_count=values['moved_count']
        self.source_binding=values['binding']
        return context.window_manager.invoke_props_dialog(self,width=380)

    def execute(self, context):
        obj=workflow.active_rig(context)
        try:
            workflow.scale_pose_spacing(
                obj,self.pivot_frame,self.factor,self.source_binding or None)
        except Exception as exc:
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
        self.pivot_frame=values['pivot_frame'];self.interval=values['interval']
        self.affected_count=values['affected_count'];self.source_binding=values['binding']
        return context.window_manager.invoke_props_dialog(self,width=380)

    def execute(self, context):
        obj=workflow.active_rig(context)
        try:
            workflow.equalize_pose_spacing(
                obj,self.pivot_frame,self.interval,self.source_binding or None)
        except Exception as exc:
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
        return {'FINISHED'}


class B4ML_OT_action(bpy.types.Operator):
    bl_idname = 'b4ml.action'
    bl_label = 'B4Artists ML Action'
    bl_description = 'Inspect the rig, capture or reuse a pose, or manage a separate interpolation candidate'
    bl_options = {'REGISTER', 'UNDO'}
    operation: EnumProperty(items=[(n, n.title(), '') for n in
        ('INSPECT', 'CAPTURE', 'REUSE', 'REMOVE', 'PREVIEW', 'KEEP', 'DISCARD', 'RESTORE_SOURCE')])
    anchor_frame: FloatProperty(options={'HIDDEN'})

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
            else:
                workflow.finish_preview(obj, context.scene, keep=self.operation == 'KEEP')
        except Exception as exc:
            self.report({'ERROR'}, str(exc))
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
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        return {'FINISHED'}

def _draw_body_target_reset(row,name,enabled):
    cell=row.row(align=True);cell.enabled=enabled
    operator=cell.operator('b4ml.body',text='Reset')
    operator.operation='RESET_TARGET';operator.target_name=name
    return operator


def _draw_body_pole_align(row,name,enabled):
    cell=row.row(align=True);cell.enabled=enabled
    operator=cell.operator('b4ml.body',text='Align Bend')
    operator.operation='ALIGN_POLE';operator.target_name=name
    return operator


def _draw_body_pole_flip(row,name,enabled):
    cell=row.row(align=True);cell.enabled=enabled
    operator=cell.operator('b4ml.body',text='Flip Side')
    operator.operation='FLIP_POLE';operator.target_name=name
    return operator


def _draw_body_pole_distance(row,item,enabled):
    cell=row.row(align=True);cell.enabled=enabled
    cell.prop(item,'pole_distance',text='')
    operator=cell.operator('b4ml.body',text='Set Distance')
    operator.operation='SET_POLE_DISTANCE';operator.target_name=item.name
    return operator

def _draw_body_pole_status(row,obj,name):
    """Draw a compact read-only relation for a humanoid pole helper."""
    try:
        status=body_preview.pole_bend_status(obj,name)
    except (KeyError,TypeError,ValueError):
        return None
    row.label(text='Current: '+status['relation']+' ('+
              format(math.degrees(status['error_radians']),'.1f')+' deg)')
    return status

def _draw_body_mirror(row,direction,text):
    operator=row.operator('b4ml.body',text=text)
    operator.operation='MIRROR_TARGETS';operator.mirror_direction=direction
    return operator


def _draw_quadruped_mirror(row, direction, text):
    operator = row.operator('b4ml.quadruped_pose', text=text)
    operator.operation = 'MIRROR_TARGETS'
    operator.mirror_direction = direction
    return operator


_QUADRUPED_POLE_UI_LABELS = {
    'Fore Pole L': 'Fore L Pole',
    'Fore Pole R': 'Fore R Pole',
    'Hind Pole L': 'Hind L Pole',
    'Hind Pole R': 'Hind R Pole',
}


def _quadruped_target_ui_label(name):
    return _QUADRUPED_POLE_UI_LABELS.get(name, name)


class B4ML_OT_body(bpy.types.Operator):
    bl_idname='b4ml.body'
    bl_label='Whole-Body Preview'
    bl_options={'REGISTER','UNDO'}
    operation: EnumProperty(items=[(n,n.title(),'') for n in ('BEGIN','KEEP','CANCEL','CALIBRATE_BEND','APPLY_LIMIT_PRESET','RESET_TARGET','MIRROR_TARGETS','ALIGN_POLE','FLIP_POLE','SET_POLE_DISTANCE','SAVE_POSE_ASSET','APPLY_POSE_ASSET')])
    target_name: StringProperty(options={'HIDDEN'})
    mirror_direction: EnumProperty(items=(('LEFT_TO_RIGHT','Left to Right',''),('RIGHT_TO_LEFT','Right to Left','')),options={'HIDDEN'})

    @classmethod
    def description(cls,context,properties):
        descriptions={
            'ALIGN_POLE':'Place this pole helper on the current evaluated elbow or knee bend.',
            'FLIP_POLE':'Place this pole helper opposite the current evaluated bend to request the other side.',
            'SET_POLE_DISTANCE':'Move this pole helper to the selected body-scale distance without changing its direction.',
            'SAVE_POSE_ASSET':'Save the current verified target layout in scene-local semantic body coordinates for another supported humanoid.',
            'APPLY_POSE_ASSET':'Apply the scene semantic target pose to this preview without changing the rig until you solve.',
        }
        return descriptions.get(properties.operation,cls.bl_label)

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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
        return {'FINISHED'}


class B4ML_OT_body_solve(bpy.types.Operator):
    bl_idname='b4ml.body_solve'
    bl_label='Solve Whole Body'
    bl_description='Fit a local learned pose; Escape cancels and restores the previous preview'
    bl_options={'REGISTER','UNDO'}
    _timer=None
    _obj=None

    @classmethod
    def poll(cls,context):
        obj=workflow.active_rig(context)
        return bool(obj and obj.b4ml.body_payload and not obj.b4ml.body_running and not obj.b4ml.body_live and not obj.b4ml.contact_suggest_running and not obj.b4ml.secondary_running and not obj.b4ml.cleanup_running)

    def execute(self,context):
        try:body_preview.solve(workflow.active_rig(context))
        except Exception as exc:
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'}, str(exc))
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
        except Exception as exc:self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
        except Exception as exc:self.report({'ERROR'},str(exc));return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self,context,event):
        if bpy.app.background or context.window is None:return self.execute(context)
        self._obj=workflow.active_rig(context)
        try:
            contacts.suggest_start(self._obj,context.scene)
            self._timer=context.window_manager.event_timer_add(.01,window=context.window);context.window_manager.modal_handler_add(self)
        except Exception as exc:
            contacts.suggest_abort(self._obj);self._remove_timer(context);self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self._remove_timer(context);self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'}, str(exc))
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
        except Exception as exc:self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
        except Exception as exc:self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
        except Exception as exc:self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
        except Exception as exc:self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
        except Exception as exc:self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
        except Exception as exc:self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
        except Exception as exc:self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
        except Exception as exc:self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
        except Exception as exc:self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
            self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
        except Exception as exc:self.report({'ERROR'},str(exc));return {'CANCELLED'}
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
        except Exception as exc:self.report({'ERROR'},str(exc));return {'CANCELLED'}
        visible=workflow.motion_layer.find(obj)
        context.view_layer.objects.active=visible;visible.select_set(True)
        return {'FINISHED'}


class B4ML_PT_main(bpy.types.Panel):
    bl_label = 'B4Artists Machine Learning'
    bl_idname = 'B4ML_PT_main'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'B4Artists ML'

    def draw(self, context):
        layout = self.layout
        layout.label(text='Experimental '+'.'.join(map(str,bl_info['version'])), icon='INFO')
        layout.label(text='Local animation assistance')
        obj = workflow.active_rig(context)
        if obj is None:
            layout.label(text='Select an armature or bound mesh.')
            return
        state = obj.b4ml
        profile, correction_rows, correction_error = rig_mapping.status(obj)
        humanoid = profile.family == 'humanoid'
        if humanoid:
            layout.label(text='Humanoid IK input / FK output')
        if profile.family == 'quadruped':
            layout.label(text='Quadruped: four-paw pose + blending', icon='INFO')
        if state.temporal_running:
            box=layout.box();box.label(text='Generating Whole-body Motion')
            box.label(text=state.temporal_progress)
            box.operator('b4ml.temporal_cancel',text='Cancel',icon='X')
            box.label(text='Escape cancels; source remains visible.')
            return
        alternatives=workflow.motion_layer.results(obj)
        if alternatives:
            saved=layout.box();saved.label(text='Saved Motion Results')
            for result in alternatives:
                saved.operator('b4ml.motion_result',text=result.name).result_name=result.name
        layout.label(text=obj.name, icon='ARMATURE_DATA')
        layout.operator('b4ml.action', text='Inspect / Refresh Rig Mapping').operation = 'INSPECT'
        _draw_rig_diagnostics(layout,state,rig_diagnostics.decode(state.rig_diagnostics_report))
        _draw_rig_mapping_editor(layout,obj,state,profile,correction_rows,correction_error)
        box=layout.box()
        box.prop(state,'show_support',icon='TRIA_DOWN' if state.show_support else 'TRIA_RIGHT',emboss=False)
        if state.show_support:
            col=box.column();col.enabled=not state.body_running and not state.contact_running and not state.contact_suggest_running and not state.flight_running and not state.cleanup_running
            col.label(text='Artist-authored mass estimate')
            if not state.mass_segments:col.operator('b4ml.support',text='Initialize Mass Model').operation='INITIALIZE'
            else:
                col.prop(state,'show_mass_settings',icon='TRIA_DOWN' if state.show_mass_settings else 'TRIA_RIGHT',emboss=False)
                if state.show_mass_settings:
                    col.prop(state,'mass_index')
                    if state.mass_index<len(state.mass_segments):
                        segment=state.mass_segments[state.mass_index]
                        col.label(text=segment.name);col.prop(segment,'weight');col.prop(segment,'fraction');col.prop(segment,'inertia_radius')
                col.prop(state,'show_support_settings',icon='TRIA_DOWN' if state.show_support_settings else 'TRIA_RIGHT',emboss=False)
                if state.show_support_settings:
                    for field in ('support_plane_point','support_plane_normal','support_tolerance','support_rotation_tolerance'):col.prop(state,field)
                col.label(text='Patches: Animation Contacts')
                col.operator('b4ml.support',text='Analyze Current Pose').operation='ANALYZE'
            if state.support_report:
                try:
                    report=json.loads(state.support_report)
                    box.label(text='Snapshot at frame '+format(report['frame'],'.3f'))
                    box.label(text=report['status'].replace('_',' ').title())
                    box.label(text='World COM (internal units):')
                    for axis,value in zip('XYZ',report['com']):box.label(text=axis+': '+format(value,'.5f'))
                    if report['margin'] is not None:box.label(text='Margin: '+format(report['margin'],'.5f'))
                    box.label(text='Contacts: '+str(len(report['contacts']))+' in / '+str(len(report['excluded_contacts']))+' excluded')
                    for item in report['excluded_contacts']:box.label(text=item['limb']+': '+item['reason'])
                except (ValueError,KeyError,TypeError):box.label(text='Reanalyze to replace an unreadable snapshot.')
            box.label(text='Reanalyze after edits.')
            box.label(text='Static support estimate')

        box=layout.box()
        box.prop(state,'show_flights',icon='TRIA_DOWN' if state.show_flights else 'TRIA_RIGHT',emboss=False)
        if state.show_flights:
            box.label(text='Gravity arc for COM')
            box.label(text='Use priority pose frames')
            col=box.column();col.enabled=humanoid and not state.flight_running and not state.contact_running and not state.contact_suggest_running and not state.cleanup_running and bool(state.candidate_action)
            if not state.mass_segments:col.operator('b4ml.support',text='Initialize Mass Model').operation='INITIALIZE'
            col.operator('b4ml.flight',text='Add Airborne Interval').operation='ADD'
            if state.flights:
                col.prop(state,'flight_index')
                if 0<=state.flight_index<len(state.flights):
                    item=state.flights[state.flight_index]
                    col.prop(item,'enabled');col.prop(item,'start',text='Takeoff');col.prop(item,'end',text='Landing')
                    col.prop(item,'strength')
                    if state.flight_backend=='NATIVE':
                        col.label(text='Transition frames')
                        col.prop(item,'takeoff_blend',text='Before takeoff')
                        col.prop(item,'landing_blend',text='After landing')
                        col.prop(item,'match_acceleration')
                        col.label(text='Airborne rotation')
                        col.prop(item,'angular_momentum_strength')
                        col.label(text='Landing support')
                        col.prop(item,'contact_impulse_strength')
                        col.label(text='Static planar collision')
                        col.prop(item,'collision_strength')
                        if item.collision_strength:col.prop(item,'collision_clearance')
                    col.operator('b4ml.flight',text='Remove Interval').operation='REMOVE'
                col.prop(state,'flight_backend')
                col.operator('b4ml.flight_solve',text='Preview COM Flight')
            if state.flight_input and state.flight_output==state.candidate_action:
                col.operator('b4ml.flight',text='Restore Before Flight').operation='RESET'
            if state.flight_running:box.label(text=state.flight_progress)
            if state.flight_metrics:
                try:
                    report=json.loads(state.flight_metrics)
                    box.label(text='COM error (body units)')
                    box.label(text=format(report['max_after'],'.3g'))
                    jumps=[r[key]['corrected']['jump'] for r in report['intervals'] for key in ('takeoff_velocity','landing_velocity') if key in r]
                    jumps.extend(r['after_jump'] for r in report.get('transitions',[]))
                    if jumps:
                        box.label(text='Boundary speed jump')
                        box.label(text=format(max(jumps),'.3g')+' units/s (estimate)')
                    acceleration=[r['after_acceleration_jump'] for r in report.get('transitions',[]) if r.get('match_acceleration')]
                    if acceleration:
                        box.label(text='Boundary acceleration jump')
                        box.label(text=format(max(acceleration),'.3g')+' units/s^2 (estimate)')
                    angular=[r for r in report.get('intervals',[]) if r.get('angular_momentum')]
                    if angular:
                        box.label(text='Angular variation reduction')
                        box.label(text=format(max(r['angular_momentum']['improvement'] for r in angular)*100,'.1f')+'% (rigid-segment estimate)')
                    collision=[r['collision_response'] for r in report.get('intervals',[]) if r.get('collision_response')]
                    if collision:
                        box.label(text='Planar penetration')
                        box.label(text=format(max(r['max_penetration_after'] for r in collision),'.3g')+' world units')
                except (ValueError,KeyError,TypeError):pass
        box=layout.box()
        box.prop(state,'show_contacts',icon='TRIA_DOWN' if state.show_contacts else 'TRIA_RIGHT',emboss=False)
        if state.show_contacts:
            box.label(text='Humanoid geometric contact correction')
            box.label(text='Priority poses stay unchanged.')
            col=box.column();col.enabled=humanoid and not state.contact_running and not state.contact_suggest_running and not state.flight_running and not state.cleanup_running and not state.body_payload and not state.posing_payload
            col.label(text='Provisional foot-contact scan')
            col.prop(state,'contact_surface')
            for field in ('contact_suggest_distance','contact_suggest_speed','contact_suggest_min_frames','contact_suggest_gap_frames'):col.prop(state,field)
            scan=col.row();scan.enabled=bool(state.candidate_action);scan.operator('b4ml.contact_suggest',text='Suggest Foot Contacts',icon='VIEWZOOM')
            if state.contact_surface is None:col.label(text='Uses the authored support plane.')
            col.label(text='Suggestions never change animation.')
            col.prop(state,'show_contact_overlay')
            overlay_options=col.row();overlay_options.enabled=state.show_contact_overlay
            overlay_options.prop(state,'show_all_contact_overlays')
            review_counts = _contact_review_counts(obj)
            col.label(text=(f'{review_counts["PROPOSED"]} proposed | '
                            f'{review_counts["ACCEPTED"]} accepted | '
                            f'{review_counts["REJECTED"]} rejected'))
            if review_counts['PROPOSED']:
                navigate=col.row(align=True);navigate.operator('b4ml.contact',text='Previous Proposed',icon='TRIA_LEFT').operation='PREVIOUS_PROPOSED';navigate.operator('b4ml.contact',text='Next Proposed',icon='TRIA_RIGHT').operation='NEXT_PROPOSED'
                bulk=col.row(align=True);bulk.operator('b4ml.contact',text='Accept All Proposed',icon='CHECKMARK').operation='ACCEPT_ALL';bulk.operator('b4ml.contact',text='Reject All Proposed',icon='X').operation='REJECT_ALL'
            col.prop(state,'contact_limb')
            col.prop(state,'show_contact_details')
            if state.show_contact_details:col.prop(state,'contact_offset')
            col.operator('b4ml.contact',text='Capture Contact Here').operation='CAPTURE'
            if state.contacts:
                col.prop(state,'contact_index')
                if 0<=state.contact_index<len(state.contacts):
                    item=state.contacts[state.contact_index]
                    col.label(text=item.name);col.prop(item,'enabled');col.label(text='Review: '+item.review_state.title())
                    if item.reason:col.label(text=item.reason)
                    if item.review_state=='PROPOSED':
                        col.prop(item,'confidence',slider=True);col.label(text=item.provenance)
                        review=col.row(align=True);review.operator('b4ml.contact',text='Accept',icon='CHECKMARK').operation='ACCEPT';review.operator('b4ml.contact',text='Reject',icon='X').operation='REJECT'
                    elif item.review_state=='REJECTED':col.label(text='Excluded from correction')
                    for field in ('start','end'):col.prop(item,field)
                    col.prop(item,'asymmetric_blend')
                    for field in (('blend_in','blend_out') if item.asymmetric_blend else ('blend',)):
                        col.prop(item,field)
                    for field in ('strength','lock_rotation'):col.prop(item,field)
                    try:
                        timing=contact_visualization.timing(item,posing._frame(context.scene))
                        col.label(text=f"Now: {timing['phase']} | {timing['influence']*100:.0f}% influence")
                    except ValueError:
                        col.label(text='Now: invalid contact timing',icon='ERROR')
                    _draw_contact_interval_controls(col,state)
                    if item.limb in _HUMANOID_CONTACT_LIMBS and item.limb.startswith('arm-'):
                        col.label(text='Hand-to-Prop Hold')
                        col.prop(item,'prop_object')
                        prop_row=col.row(align=True)
                        bind=prop_row.row();bind.enabled=bool(item.prop_object and state.candidate_action)
                        bind.operator('b4ml.contact',text='Bind to Prop',icon='CONSTRAINT').operation='BIND_PROP'
                        clear=prop_row.row();clear.enabled=item.prop_bound
                        clear.operator('b4ml.contact',text='Clear',icon='X').operation='CLEAR_PROP'
                        if item.prop_bound and item.prop_target:
                            col.label(text='Following '+item.prop_target.name)
                    elif item.limb in _HUMANOID_CONTACT_LIMBS and item.limb.startswith('leg-'):
                        col.label(text='Foot-to-Moving-Platform')
                        col.prop(item,'prop_object',text='Surface')
                        surface_row=col.row(align=True)
                        bind=surface_row.row();bind.enabled=bool(item.prop_object and state.candidate_action)
                        bind.operator('b4ml.contact',text='Bind to Platform',icon='CONSTRAINT').operation='BIND_SURFACE'
                        clear=surface_row.row();clear.enabled=item.prop_bound
                        clear.operator('b4ml.contact',text='Clear',icon='X').operation='CLEAR_SURFACE'
                        if item.prop_bound and item.prop_target:
                            col.label(text='Following '+item.prop_target.name)
                    support_controls=col.column();support_controls.enabled=not item.prop_bound
                    support_controls.prop(item,'use_support')
                    if item.use_support:
                        for field in ('support_width','support_length','support_heading'):support_controls.prop(item,field)
                    if state.show_contact_details:
                        for field in ('point','offset'):col.prop(item,field)
                        if item.prop_bound:
                            col.prop(item,'prop_point');col.prop(item,'prop_rotation')
                    col.operator('b4ml.contact',text='Remove Contact').operation='REMOVE'
            row=col.row();row.enabled=bool(state.candidate_action and contacts.rows(obj))
            row.operator('b4ml.contact_solve',text='Preview Contact Correction')
            if state.contact_input and state.contact_output==state.candidate_action:col.operator('b4ml.contact',text='Restore Before Contacts').operation='RESET'
            if state.contact_running:box.label(text=state.contact_progress)
            if state.contact_suggest_running:box.label(text=state.contact_suggest_progress+' (Esc to cancel)')
            box.label(text='No self-collision solve yet.')
        box=layout.box()
        box.prop(state,'show_cleanup',icon='TRIA_DOWN' if state.show_cleanup else 'TRIA_RIGHT',emboss=False)
        if state.show_cleanup:
            box.label(text='Deterministic copied-curve cleanup')
            box.label(text='Priority poses and accepted contacts stay exact.')
            col=box.column();col.enabled=bool(state.candidate_action) and not state.cleanup_running and not state.secondary_running and not state.flight_running and not state.contact_running and not state.contact_suggest_running
            col.prop(state,'cleanup_scope')
            col.prop(state,'cleanup_smooth')
            smooth=col.column();smooth.enabled=state.cleanup_smooth;smooth.prop(state,'cleanup_strength')
            col.prop(state,'cleanup_reduce')
            reduce=col.column();reduce.enabled=state.cleanup_reduce;reduce.prop(state,'cleanup_tolerance')
            col.operator('b4ml.cleanup_solve',text='Preview Cleanup',icon='PLAY')
            if state.cleanup_input and state.cleanup_output==state.candidate_action:
                col.operator('b4ml.cleanup',text='Restore Input').operation='RESET'
            if state.cleanup_running:box.label(text=state.cleanup_progress+' (Esc to cancel)')
            if state.cleanup_metrics:
                try:
                    report=json.loads(state.cleanup_metrics)
                    box.label(text=(str(report['keys_before'])+' to '+str(report['keys_after'])+
                                    ' keys; '+str(report['keys_removed'])+' removed'))
                    box.label(text=str(report['curves_smoothed'])+' curves smoothed; '+str(len(report['cleaned_controls']))+' controls')
                    if report['protected_contact_controls']:
                        box.label(text=str(len(report['protected_contact_controls']))+' contact controls protected')
                    if report.get('accepted_contacts'):
                        box.label(text=(str(report['accepted_contacts'])+' accepted contacts; '+
                                        str(report['contact_samples'])+' validation samples'))
                        box.label(text=('Max contact drift: '+format(report['max_contact_position_drift'],'.3g')+
                                        '; rotation '+format(math.degrees(report['max_contact_rotation_drift_radians']),'.3g')+' deg'))
                    if report.get('reduction'):
                        box.label(text='Max key error: '+format(report['max_reduction_error'],'.3g'))
                    box.label(text='Derivative jump: '+format(report['max_scalar_derivative_jump_before'],'.3g')+' to '+format(report['max_scalar_derivative_jump_after'],'.3g'))
                    if report['skipped_constrained_curves'] or report['skipped_unsupported_curves']:
                        box.label(text=str(report['skipped_constrained_curves']+report['skipped_unsupported_curves'])+' curves safely skipped')
                except (ValueError,KeyError,TypeError):pass
            box.label(text='Procedural cleanup; no learned model used.')
        box=layout.box()
        box.prop(state,'show_secondary',icon='TRIA_DOWN' if state.show_secondary else 'TRIA_RIGHT',emboss=False)
        if state.show_secondary:
            box.label(text='Deterministic control physics')
            box.label(text='Select pose controls.')
            col=box.column();col.enabled=bool(state.candidate_action) and not secondary_motion.busy(state)
            col.prop(state,'secondary_space',text='Space')
            row=col.row(align=True);row.prop(state,'secondary_rotation');row.prop(state,'secondary_location')
            col.prop(state,'secondary_chain')
            chain=col.column();chain.enabled=state.secondary_chain and ((state.secondary_space=='LOCAL' and state.secondary_rotation) or (state.secondary_space=='WORLD' and state.secondary_location))
            if state.secondary_chain and state.secondary_space=='WORLD' and state.secondary_location:
                chain.label(text='World chain: assign a load to every control; no wind/impulse.',icon='INFO')
            chain.prop(state,'secondary_chain_direction',text='Grow From Active')
            chain.prop(state,'secondary_chain_length',text='Maximum Controls')
            selector=chain.operator('b4ml.secondary_select_chain',text='Select Direct Chain',icon='BONE_DATA')
            selector.direction=state.secondary_chain_direction;selector.max_controls=state.secondary_chain_length
            if state.secondary_selection_swap:chain.operator('b4ml.secondary_selection_swap',text='Swap Previous Selection',icon='FILE_REFRESH')
            chain.prop(state,'secondary_chain_propagation',text='Propagation')
            for field in ('secondary_frequency','secondary_damping','secondary_air_friction','secondary_strength','secondary_blend_frames'):col.prop(state,field)
            world=col.column();world.enabled=state.secondary_space=='WORLD' and state.secondary_location
            world.prop(state,'secondary_gravity');world.prop(state,'secondary_external_acceleration')
            world.prop(state,'secondary_self_collision',text='Self-Collision')
            if state.secondary_self_collision:
                world.prop(state,'secondary_self_collision_radius',text='Self Radius')
                world.label(text='Selected controls only; World space and Location required.')
            world.prop(state,'secondary_wind_velocity')
            world.prop(state,'secondary_impulse_velocity')
            impulse_frame=world.column();impulse_frame.enabled=any(value!=0. for value in state.secondary_impulse_velocity)
            impulse_frame.prop(state,'secondary_impulse_frame')
            world.prop(state,'secondary_load_force')
            world.prop(state,'secondary_load_mass')
            world.prop(state,'secondary_load_offset')
            world.prop(state,'secondary_load_inertia')
            recall=world.operator('b4ml.secondary_control_load',text='Load From Active',icon='IMPORT');recall.operation='LOAD_ACTIVE'
            assign=world.operator('b4ml.secondary_control_load',text='Assign Load',icon='ADD');assign.operation='ASSIGN'
            clear=world.operator('b4ml.secondary_control_load',text='Clear Load',icon='X');clear.operation='CLEAR'
            load_count=secondary_motion.control_load_count(obj)
            world.label(text=('Invalid stored control loads' if load_count is None else
                              str(load_count)+' assigned control load'+('s' if load_count!=1 else '')))
            if load_count is None:
                reset=world.operator('b4ml.secondary_control_load',text='Clear Invalid Assignments',icon='TRASH');reset.operation='CLEAR_ALL'
            world.prop(state,'secondary_collision')
            if state.secondary_collision:
                world.prop(state,'secondary_collision_shape',text='Shape')
                if state.secondary_collision_shape in {'SPHERE','COMPOUND'}:
                    if state.secondary_collision_shape=='COMPOUND':
                        world.prop(state,'contact_surface',text='Support Surface')
                        world.label(text='Static support surface is resolved before the static sphere set.')
                        world.prop(state,'secondary_collision_compound_capsule',text='Also Include Capsule')
                        world.prop(state,'secondary_collision_compound_mesh',text='Also Include Static Closed Mesh')
                    world.prop(state,'secondary_sphere_collider',text='Sphere Center / Bounds Source')
                    world.prop(state,'secondary_sphere_radius',text='New Radius')
                    fit=world.operator('b4ml.secondary_sphere',text='Fit New Radius from Bounds',icon='FULLSCREEN_ENTER');fit.operation='FIT';fit.index=-1
                    proxy=world.operator('b4ml.secondary_sphere',text='Create Bounds Proxy',icon='OUTLINER_OB_EMPTY');proxy.operation='PROXY'
                    world.prop(state,'secondary_sphere_moving',text='Follow Center Animation')
                    world.prop(state,'secondary_sphere_scaling',text='Follow Radius Scale')
                    if state.secondary_collision_shape=='SPHERE':
                        world.prop(state,'secondary_collision_continuous',text='Continuous-Time Sweep')
                        world.label(text=('One sphere uses a bounded analytic relative-motion sweep.'
                                          if state.secondary_collision_continuous else
                                          'Sphere sets use bounded projection at solver samples.'))
                    else:
                        world.label(text=('Compound mode permits one moving sphere plus the support surface, optionally after static spheres, '
                                          'two moving spheres plus the support surface, or one moving capsule after static spheres; '
                                          'other moving-collider mixtures remain rejected.'))
                    add=world.operator('b4ml.secondary_sphere',text='Add Sphere to Set',icon='ADD');add.operation='ADD'
                    if state.secondary_spheres:
                        moving_count=sum(bool(item.moving) for item in state.secondary_spheres)
                        world.label(text=str(len(state.secondary_spheres))+' active sphere'+
                                    ('s' if len(state.secondary_spheres)!=1 else ''))
                        if moving_count:
                            world.label(text=str(moving_count)+' following direct location animation')
                        for index,item in enumerate(state.secondary_spheres):
                            sphere=world.box()
                            sphere.prop(item,'collider',text=str(index+1)+' Center')
                            sphere.prop(item,'radius',text='Radius')
                            fit=sphere.operator('b4ml.secondary_sphere',text='Fit Radius from Bounds',icon='FULLSCREEN_ENTER');fit.operation='FIT';fit.index=index
                            sphere.prop(item,'moving',text='Follow Animation')
                            sphere.prop(item,'scaling',text='Follow Radius Scale')
                            remove=sphere.operator('b4ml.secondary_sphere',text='Remove',icon='X')
                            remove.operation='REMOVE';remove.index=index
                        clear=world.operator('b4ml.secondary_sphere',text='Clear Sphere Set',icon='TRASH');clear.operation='CLEAR'
                    else:
                        world.label(text='No set: uses New Sphere directly.')
                    if (state.secondary_collision_shape=='COMPOUND'
                            and state.secondary_collision_compound_capsule):
                        world.prop(state,'secondary_capsule_start',text='Capsule Start Endpoint')
                        world.prop(state,'secondary_capsule_end',text='Capsule End Endpoint')
                        world.prop(state,'secondary_capsule_radius',text='Capsule Radius')
                        world.prop(state,'secondary_capsule_moving',text='Follow Endpoint Animation')
                        world.prop(state,'secondary_capsule_scaling',text='Follow Radius Scale')
                        world.prop(state,'secondary_collision_continuous',text='Continuous-Time Sweep')
                        world.label(text=('One moving capsule plus the support and static sphere set uses bounded relative-motion response; '
                                          'mixed moving colliders and compound meshes are rejected.'
                                          if state.secondary_capsule_moving else
                                          'Static capsule only; enable endpoint animation for the bounded moving-capsule compound slice.'))
                    if (state.secondary_collision_shape=='COMPOUND'
                            and state.secondary_collision_compound_mesh):
                        world.prop(state,'secondary_collision_mesh',text='Closed Mesh')
                        if not state.secondary_collision_compound_capsule:
                            world.prop(state,'secondary_collision_continuous',text='Continuous-Time Sweep (disable for compound mesh)')
                        world.label(text='Static closed mesh only; deformation, object motion, volume mode, and continuous sweep are rejected in this compound.')
                elif state.secondary_collision_shape=='CAPSULE':
                    world.prop(state,'secondary_capsule_start',text='Start Endpoint')
                    world.prop(state,'secondary_capsule_end',text='End Endpoint')
                    world.prop(state,'secondary_capsule_radius',text='Radius')
                    world.prop(state,'secondary_capsule_moving',text='Follow Endpoint Animation')
                    world.prop(state,'secondary_capsule_scaling',text='Follow Radius Scale')
                    world.prop(state,'secondary_collision_continuous',text='Continuous-Time Sweep')
                    world.label(text=('Direct endpoint Actions with bounded interpolated sweep.' if state.secondary_capsule_moving and state.secondary_collision_continuous else
                                      'Direct endpoint Actions sampled at solver frames.' if state.secondary_capsule_moving else
                                      'Static, unparented endpoints; sweep is a bounded static capsule crossing check.' if state.secondary_collision_continuous else
                                      'Static, unparented endpoints only.'))
                elif state.secondary_collision_shape in {'MESH','VOLUME'}:
                    world.prop(state,'secondary_collision_mesh',text='Triangle Mesh')
                    world.prop(state,'secondary_collision_mesh_deforming',text='Follow Shape-Key Deformation')
                    world.prop(state,'secondary_collision_mesh_moving',text='Follow Object Motion')
                    if state.secondary_collision_shape=='VOLUME':
                        world.prop(state,'secondary_collision_volume_radius',text='Control Volume Radius')
                        world.label(text=('Closed mesh; finite spherical control volume; direct shape-key Action sampled per frame.'
                                          if state.secondary_collision_mesh_deforming else
                                          'Closed mesh; finite spherical control volume; static evaluated triangles.'))
                    else:
                        world.label(text=('Unparented mesh; direct shape-key Action sampled per frame.'
                                          if state.secondary_collision_mesh_deforming else
                                          'Static, unparented mesh without modifiers or animation.'))
                    world.prop(state,'secondary_collision_continuous',text='Continuous-Time Sweep')
                    if state.secondary_collision_continuous:
                        world.label(text=('Closed shape-key mesh uses bounded interpolated sweep samples.'
                                          if state.secondary_collision_mesh_deforming else
                                          'Catches segment crossings between solver samples.'))
                else:
                    world.prop(state,'contact_surface',text='Planar Surface')
                    if state.contact_surface is None:world.label(text='Uses the authored support plane.')
                world.prop(state,'secondary_collision_clearance',text='Clearance')
                world.prop(state,'secondary_restitution',text='Bounce')
                world.prop(state,'secondary_surface_friction',text='Friction')
            col.operator('b4ml.secondary_solve',text='Preview Secondary',icon='PLAY')
            if state.secondary_input and state.secondary_output==state.candidate_action:
                col.operator('b4ml.secondary',text='Restore Input').operation='RESET'
            if state.secondary_running:box.label(text=state.secondary_progress+' (Esc to cancel)')
            if state.secondary_metrics:
                try:
                    report=json.loads(state.secondary_metrics)
                    count=len(report['controls']);box.label(text=str(count)+' control'+('s' if count!=1 else '')+'; '+report.get('space','LOCAL').title())
                    if report.get('chain'):box.label(text=str(report.get('chain_links',0))+' coupled chain links')
                    box.label(text=str(report['samples'])+' samples; '+str(report['curves'])+' editable curves')
                    if report['rotation']:box.label(text='Max rotation: '+format(math.degrees(report['max_rotation_correction_radians']),'.2f')+' degrees')
                    if report['location']:box.label(text='Max location: '+format(report['max_location_correction'],'.4g'))
                    if report.get('torque_controls'):box.label(text=str(report['torque_controls'])+' torque control'+('s' if report['torque_controls']!=1 else '')+'; max '+format(report.get('max_control_torque',0.),'.4g'))
                    if report.get('collision'):
                        collider_count=report.get('collision_sphere_count',0)
                        collider_label=('support + '+str(max(0,collider_count-1))+' sphere colliders'
                                        if report.get('collision_compound') else
                                        str(collider_count)+' sphere colliders' if collider_count>1 else
                                        report.get('collision_shape','PLANE').title()+' collider')
                        box.label(text=collider_label+'; '+str(report.get('collision_samples',0))+' contacts')
                        box.label(text='Final penetration '+format(report.get('max_penetration_after',0.),'.3g'))
                except (ValueError,KeyError,TypeError):pass
            box.label(text='Priority poses remain exact; no learned model used.')
        if profile.family == 'quadruped':
            box = layout.box()
            box.label(text='Quadruped Whole-Body Pose')
            box.label(text='Generated Rigify cat, horse, or wolf')
            if state.quadruped_payload:
                quadruped_record = _json_object(state.quadruped_payload)
                schema = quadruped_record.get('schema')
                supports_spine_follow = schema in {3, 4}
                supports_poles = schema == 4
                if state.quadruped_targets.get('Head'):
                    box.label(text=('Move body, paws, and poles; rotate Head.' if supports_poles else
                                    'Move body/paws; rotate the location-locked Head.'))
                else:
                    box.label(text='Move body/paws; recover this legacy preview.')
                for item in state.quadruped_targets:
                    container = box.box() if item.name in quadruped_pose.POLE_TARGETS else box
                    row = container.row(align=True)
                    row.label(text=_quadruped_target_ui_label(item.name),
                              icon='EMPTY_ARROWS' if item.name in {'Body','Head'} else 'EMPTY_DATA')
                    if item.name in quadruped_pose.POLE_TARGETS:
                        reset = row.operator('b4ml.quadruped_pose', text='Reset')
                        reset.operation = 'RESET_TARGET'
                        reset.target_name = item.name
                        pole_actions = container.row(align=True)
                        align = pole_actions.operator('b4ml.quadruped_pose', text='Align Bend')
                        align.operation = 'ALIGN_POLE'
                        align.target_name = item.name
                        flip = pole_actions.operator('b4ml.quadruped_pose', text='Flip Side')
                        flip.operation = 'FLIP_POLE'
                        flip.target_name = item.name
                        pole_distance = container.row(align=True)
                        pole_distance.prop(item, 'pole_distance', text='')
                        distance = pole_distance.operator('b4ml.quadruped_pose', text='Set Distance')
                        distance.operation = 'SET_POLE_DISTANCE'
                        distance.target_name = item.name
                    else:
                        row.prop(item, 'use_orientation', text='Rotation')
                        reset = row.operator('b4ml.quadruped_pose', text='Reset')
                        reset.operation = 'RESET_TARGET'
                        reset.target_name = item.name
                if supports_spine_follow:
                    box.prop(state, 'quadruped_spine_follow')
                    row = box.row()
                    row.enabled = state.quadruped_spine_follow > 0
                    row.prop(state, 'quadruped_neck_share')
                else:
                    box.label(text='Legacy direct recovery; Spine Follow is unavailable.')
                mirror = box.row(align=True)
                _draw_quadruped_mirror(mirror, 'LEFT_TO_RIGHT', 'Mirror L to R')
                _draw_quadruped_mirror(mirror, 'RIGHT_TO_LEFT', 'Mirror R to L')
                box.operator('b4ml.quadruped_pose', text='Solve Quadruped Pose').operation = 'SOLVE'
                assets = box.row(align=True)
                assets.operator('b4ml.quadruped_pose', text='Save Solved Pose').operation = 'SAVE_POSE_ASSET'
                assets.operator('b4ml.quadruped_pose', text='Apply Pose').operation = 'APPLY_POSE_ASSET'
                try:
                    metrics = quadruped_record.get('metrics')
                    if metrics:
                        box.label(text='Max paw error: '+format(metrics['max_paw_error'], '.3g'))
                        if 'max_pole_error' in metrics:
                            box.label(text='Max pole error: '+format(metrics['max_pole_error'], '.3g'))
                        if metrics.get('orientation_errors'):
                            box.label(text='Max rotation error: '+format(math.degrees(metrics['max_orientation_error']), '.3g')+' deg')
                        distribution = metrics.get('spine_distribution')
                        if distribution and distribution.get('active'):
                            box.label(text='Spine follow: '+format(distribution['follow'] * 100, '.0f')+'%; Neck share '+format(distribution['neck_share'] * 100, '.0f')+'%')
                except (ValueError, KeyError, TypeError, AttributeError):
                    pass
                row = box.row(align=True)
                row.operator('b4ml.quadruped_pose', text='Keep as Pose Anchor', icon='CHECKMARK').operation = 'KEEP'
                row.operator('b4ml.quadruped_pose', text='Cancel', icon='X').operation = 'CANCEL'
            else:
                box.prop(state, 'quadruped_spine_follow')
                row = box.row()
                row.enabled = state.quadruped_spine_follow > 0
                row.prop(state, 'quadruped_neck_share')
                box.prop(state, 'quadruped_use_poles')
                if state.quadruped_use_poles:
                    try:
                        pole_modes = quadruped_pose.pole_mode_values(obj)
                        if not all(abs(value - 1.0) <= 1e-7 for value in pole_modes.values()):
                            box.label(text='Pole Vectors need pose-preserving matching.', icon='INFO')
                            row = box.row()
                            row.enabled = (state.candidate_action is None and not state.posing_payload and
                                           not state.body_payload and not state.temporal_running and
                                           not state.flight_running and not state.contact_running and
                                           not state.contact_suggest_running and not state.secondary_running and
                                           not state.cleanup_running and not workflow.motion_layer.find(obj) and
                                           not profile.missing)
                            row.operator('b4ml.quadruped_pose',
                                         text='Match + Enable All Poles',
                                         icon='FORCE_MAGNETIC').operation = 'MATCH_POLES'
                    except (ValueError, KeyError, TypeError) as exc:
                        box.label(text=str(exc), icon='ERROR')
                row = box.row()
                row.enabled = (state.candidate_action is None and not state.posing_payload and
                               not state.body_payload and not profile.missing and
                               profile.name.startswith('Rigify Generated Quadruped'))
                row.operator('b4ml.quadruped_pose', text='Start Quadruped Pose').operation = 'BEGIN'
                if not profile.name.startswith('Rigify Generated Quadruped'):
                    box.label(text='Generate this Rigify metarig to use paw and pole posing.')
            box.label(text='Position, rotation and procedural spine follow; no learned gait model.')
            contact_box = layout.box()
            contact_box.prop(state, 'show_quadruped_contacts',
                             icon='TRIA_DOWN' if state.show_quadruped_contacts else 'TRIA_RIGHT',
                             emboss=False)
            if state.show_quadruped_contacts:
                contact_box.label(text='Review suggestions or capture paw holds.')
                contact_box.label(text='Priority poses stay unchanged.')
                col = contact_box.column()
                col.enabled = (not state.contact_running and not state.contact_suggest_running and not state.flight_running and
                               not state.secondary_running and not state.cleanup_running and not state.quadruped_payload)
                col.prop(state, 'contact_surface')
                if state.contact_surface is None:
                    col.prop(state, 'support_plane_point')
                    col.prop(state, 'support_plane_normal')
                for field in ('contact_suggest_distance', 'contact_suggest_speed',
                              'contact_suggest_min_frames', 'contact_suggest_gap_frames'):
                    col.prop(state, field)
                col.label(text='Thresholds use body-to-paw distance.')
                col.operator('b4ml.contact_suggest', text='Suggest Paw Contacts', icon='VIEWZOOM')
                col.prop(state,'show_contact_overlay')
                overlay_options=col.row();overlay_options.enabled=state.show_contact_overlay
                overlay_options.prop(state,'show_all_contact_overlays')
                review_counts = _contact_review_counts(obj)
                col.label(text=(f'{review_counts["PROPOSED"]} proposed | '
                                f'{review_counts["ACCEPTED"]} accepted | '
                                f'{review_counts["REJECTED"]} rejected'))
                if review_counts['PROPOSED']:
                    navigate = col.row(align=True)
                    navigate.operator('b4ml.contact', text='Previous Proposed', icon='TRIA_LEFT').operation = 'PREVIOUS_PROPOSED'
                    navigate.operator('b4ml.contact', text='Next Proposed', icon='TRIA_RIGHT').operation = 'NEXT_PROPOSED'
                    bulk = col.row(align=True)
                    bulk.operator('b4ml.contact', text='Accept All Proposed', icon='CHECKMARK').operation = 'ACCEPT_ALL'
                    bulk.operator('b4ml.contact', text='Reject All Proposed', icon='X').operation = 'REJECT_ALL'
                col.prop(state, 'quadruped_contact_limb')
                col.prop(state, 'show_contact_details')
                if state.show_contact_details:
                    col.prop(state, 'contact_offset', text='Offset from Paw Tip')
                col.operator('b4ml.contact', text='Capture Paw Contact Here').operation = 'CAPTURE'
                quad_contacts = [item for item in state.contacts if item.limb in quadruped_contacts.LIMBS]
                if quad_contacts:
                    col.prop(state, 'contact_index')
                    if 0 <= state.contact_index < len(state.contacts):
                        item = state.contacts[state.contact_index]
                        if item.limb in quadruped_contacts.LIMBS:
                            col.label(text=item.name)
                            col.prop(item, 'enabled')
                            col.label(text='Review: ' + item.review_state.title())
                            if item.reason:
                                col.label(text=item.reason)
                            if item.review_state == 'PROPOSED':
                                col.label(text='Score: ' + format(item.confidence, '.2f'))
                                col.label(text=item.provenance)
                                review = col.row(align=True)
                                review.operator('b4ml.contact', text='Accept').operation = 'ACCEPT'
                                review.operator('b4ml.contact', text='Reject').operation = 'REJECT'
                            for field in ('start', 'end'):
                                col.prop(item, field)
                            col.prop(item, 'asymmetric_blend')
                            for field in (('blend_in', 'blend_out') if item.asymmetric_blend else ('blend',)):
                                col.prop(item, field)
                            for field in ('strength', 'lock_rotation'):
                                col.prop(item, field)
                            try:
                                timing=contact_visualization.timing(item,posing._frame(context.scene))
                                col.label(text=f"Now: {timing['phase']} | {timing['influence']*100:.0f}% influence")
                            except ValueError:
                                col.label(text='Now: invalid contact timing',icon='ERROR')
                            _draw_contact_interval_controls(col, state)
                            if state.show_contact_details:
                                for field in ('point', 'offset'):
                                    col.prop(item, field)
                            col.operator('b4ml.contact', text='Remove Paw Contact').operation = 'REMOVE'
                row = col.row()
                row.enabled = bool(state.candidate_action and quadruped_contacts.rows(obj))
                row.operator('b4ml.contact_solve', text='Preview Four-Paw Correction')
                if state.contact_input and state.contact_output == state.candidate_action:
                    col.operator('b4ml.contact', text='Restore Before Paw Contacts').operation = 'RESET'
                if state.contact_running:
                    contact_box.label(text=state.contact_progress + ' (Esc to cancel)')
                if state.contact_suggest_running:
                    contact_box.label(text=state.contact_suggest_progress + ' (Esc to cancel)')
                try:
                    metrics = json.loads(state.contact_metrics)
                    if metrics.get('backend') == 'generated_rigify_four_paw_contacts_v1':
                        contact_box.label(text='Paw drift: '+format(metrics['contact_drift_before'], '.3g')+
                                               ' -> '+format(metrics['contact_drift_after'], '.3g'))
                except (ValueError, KeyError, TypeError):
                    pass
                phase_row = col.row()
                phase_row.enabled = bool(state.candidate_action and quadruped_contacts.rows(obj))
                phase_row.operator('b4ml.quadruped_gait', text='Analyze Gait Phases', icon='TIME').operation = 'ANALYZE'
                if state.quadruped_gait_report:
                    try:
                        gait = quadruped_gait.display_report(obj)
                        index = min(max(int(state.quadruped_gait_index), 0), len(gait['phases']) - 1)
                        phase = gait['phases'][index]
                        contact_box.label(text=f"Phase {index + 1}/{len(gait['phases'])}: {phase['label']}")
                        contact_box.label(text=f"Frames {phase['start']:g} to {phase['end']:g}")
                        paws = ', '.join(value.replace('-', ' ') for value in phase['support_limbs'])
                        contact_box.label(text='Support: ' + (paws if paws else 'none'))
                        contact_box.label(text='Navigation revalidates the candidate action.')
                        navigate = col.row(align=True)
                        navigate.operator('b4ml.quadruped_gait', text='Previous Phase', icon='TRIA_LEFT').operation = 'PREVIOUS'
                        navigate.operator('b4ml.quadruped_gait', text='Next Phase', icon='TRIA_RIGHT').operation = 'NEXT'
                        col.operator('b4ml.quadruped_gait', text='Clear Phase Report', icon='X').operation = 'CLEAR'
                    except ValueError as exc:
                        _draw_wrapped(contact_box, str(exc), icon='ERROR')
                        col.operator('b4ml.quadruped_gait', text='Clear Stale Report', icon='X').operation = 'CLEAR'
                contact_box.label(text='Procedural contact-phase review; animation stays unchanged.')
        box = layout.box()
        box.label(text='Humanoid Whole-Body Pose')
        box.label(text='Experimental learned model')
        if state.body_payload:
            box.label(text='Move targets in Object Mode.')
            box.label(text='Use Live Solve or Solve Whole Body.')
            box.label(text='Enable Rotation to use axes.')
            box.label(text='Static balance is optional.')
            col=box.column();col.enabled=not state.body_running or state.body_live
            try:
                controls_version=json.loads(state.body_payload).get('controls_version')
                extra=isinstance(controls_version,int) and controls_version>=1
                chest_orientation=isinstance(controls_version,int) and controls_version>=4
                neck_orientation=isinstance(controls_version,int) and controls_version>=5
            except (ValueError,TypeError):extra=False;chest_orientation=False;neck_orientation=False
            col.prop(state,'show_body_targets',icon='TRIA_DOWN' if state.show_body_targets else 'TRIA_RIGHT')
            if state.show_body_targets:
                mirror=col.row(align=True);mirror.enabled=not state.body_live and not state.body_running
                _draw_body_mirror(mirror,'LEFT_TO_RIGHT','Mirror L to R')
                _draw_body_mirror(mirror,'RIGHT_TO_LEFT','Mirror R to L')
                col.label(text='Semantic Pose Asset')
                asset=col.row(align=True);asset.enabled=not state.body_live and not state.body_running
                save=asset.operator('b4ml.body',text='Save Solved Pose');save.operation='SAVE_POSE_ASSET'
                apply=asset.row(align=True);apply.enabled=isinstance(context.scene.get(body_preview.POSE_ASSET_KEY),str)
                use=apply.operator('b4ml.body',text='Apply Pose');use.operation='APPLY_POSE_ASSET'
                for item in state.body_targets:
                    row=col.row(align=True)
                    position=row.row();position.enabled=item.name!='Pelvis'
                    if item.name=='Pelvis' and state.body_balance and state.body_balance_strength>0 and state.body_balance_free_pelvis:position.label(text='Pelvis position: free')
                    else:position.prop(item,'enabled',text=item.name)
                    if (extra and body_preview.target_supports_orientation(item.name)
                            and (item.name!='Chest' or chest_orientation)
                            and (item.name!='Neck' or neck_orientation)):
                        row.prop(item,'use_orientation',text='Rot')
                    elif item.name in {'Chest','Neck'}:row.label(text='Restart for rotation')
                    _draw_body_target_reset(row,item.name,not state.body_live and not state.body_running)
                    if extra and item.pole and body_preview.target_supports_pole(item.name):
                        pole_row=col.row(align=True)
                        pole_row.prop(item,'use_pole',text='Elbow Direction' if item.name.startswith('Hand') else 'Knee Direction')
                        pole_actions=col.row(align=True)
                        _draw_body_pole_align(pole_actions,item.name,not state.body_live and not state.body_running)
                        _draw_body_pole_flip(pole_actions,item.name,not state.body_live and not state.body_running)
                        pole_distance=col.row(align=True)
                        _draw_body_pole_distance(pole_distance,item,not state.body_live and not state.body_running)
                        _draw_body_pole_status(col,item.id_data,item.name)
            if not extra:box.label(text='Restart for rotation/poles.')
            col.prop(state,'show_body_limits',icon='TRIA_DOWN' if state.show_body_limits else 'TRIA_RIGHT')
            if state.show_body_limits:
                col.label(text='Rotation limits')
                col.label(text='Opt-in animation estimates; tune per character.')
                preset_row=col.row(align=True);preset_row.prop(state,'body_limit_preset',text='')
                preset_row.operator('b4ml.body',text='Apply to Mapped Controls').operation='APPLY_LIMIT_PRESET'
                col.prop_search(state,'body_limit_control',state,'body_limits',text='Control')
                item=state.body_limits.get(state.body_limit_control)
                if item is not None:
                    limits_box=col.box();limits_box.prop(item,'enabled',text='Limit This Control')
                    limits_box.label(text='Source: '+item.preset_provenance)
                    if item.enabled:
                        if item.joint_available:limits_box.prop(item,'space')
                        else:limits_box.label(text='Control space only')
                        limits_box.prop(item,'swing')
                        limits_box.prop(item,'twist_min');limits_box.prop(item,'twist_max')
                        limits_box.prop(item,'use_bend_plane')
                        if item.use_bend_plane:
                            limits_box.prop(item,'bend_axis')
                            limits_box.operator('b4ml.body',text='Use Current Bend as Forward').operation='CALIBRATE_BEND'
                            limits_box.prop(item,'bend_min');limits_box.prop(item,'bend_max');limits_box.prop(item,'bend_sideways')
                col.label(text=f'{sum(i.enabled for i in state.body_limits)} controls limited')
            col.prop(state,'body_balance')
            if state.body_balance:
                for field in ('body_balance_strength','body_balance_inset','body_balance_free_pelvis','body_balance_dynamic'):col.prop(state,field)
                if state.body_balance_dynamic:
                    col.prop(state,'body_balance_velocity')
                    col.label(text='Procedural capture point; no force solve.')
                col.label(text='Authored mass + support')
                col.label(text='Support limbs stay pinned.')
            col.prop(state,'body_strength');col.prop(state,'body_influence')
            manual=col.row();manual.enabled=not state.body_live
            manual.operator('b4ml.body_solve',text='Solve Whole Body')
            live=box.row();live.operator('b4ml.body_live',text='Stop Live Solve' if state.body_live else 'Start Live Solve',icon='PAUSE' if state.body_live else 'PLAY')
            if state.body_balance:
                try:
                    metrics=json.loads(state.body_payload).get('metrics',{}).get('balance')
                    if metrics:
                        col.label(text='Last dynamic balance solve:' if metrics.get('dynamic') else 'Last static balance solve:')
                        col.label(text='COM error: '+format(metrics['com_error'],'.3g'))
                        col.label(text='Margin: '+format(metrics['after_margin'],'.5f'))
                except (ValueError,KeyError,TypeError):pass
            col.operator('b4ml.body',text='Keep as Pose Anchor',icon='CHECKMARK').operation='KEEP'
            col.operator('b4ml.body',text='Cancel Preview',icon='X').operation='CANCEL'
            if state.body_running:box.label(text=state.body_progress+' (Esc to cancel)')
        else:
            row=box.row();row.enabled=humanoid and not state.posing_payload and not state.body_payload and not state.quadruped_payload and state.candidate_action is None
            row.operator('b4ml.body',text='Start Whole-Body Pose').operation='BEGIN'
            if not humanoid:box.label(text='Humanoid solver unavailable for this rig schema.')
        box=layout.box()
        box.label(text='Humanoid Assisted Pose - Geometric Solver')
        if state.posing_payload:
            box.label(text='Move the sphere targets in Object Mode.')
            box.label(text='IK input is matched to an editable FK pose.')
            for item in state.pose_targets:
                row = box.row(align=True)
                row.prop(item, 'enabled', text=item.name)
                if item.pole:
                    row.prop(item, 'learn_bend', text='Learn Bend')
            if state.pose_metrics:
                try:
                    metrics = json.loads(state.pose_metrics)
                except (ValueError, TypeError):
                    metrics = {}
                for limb in metrics.get('limbs', []):
                    reason = limb.get('bend_source', 'authored pole')
                    if reason not in ('learned', 'authored pole'):
                        box.label(text=f"{limb['limb']}: {reason}", icon='INFO')
            box.prop(state, 'pose_offset')
            box.prop(state, 'pose_strength')
            box.prop(state, 'max_bend')
            if any(item.learn_bend for item in state.pose_targets):
                box.prop(state, 'learned_bend_strength')
            box.operator('b4ml.pose', text='Solve Pose').operation = 'SOLVE'
            row = box.row(align=True)
            row.operator('b4ml.pose', text='Keep as Pose Anchor', icon='CHECKMARK').operation = 'KEEP'
            row.operator('b4ml.pose', text='Cancel', icon='X').operation = 'CANCEL'
        else:
            row = box.row()
            row.enabled = humanoid and state.candidate_action is None and not state.body_payload and not state.quadruped_payload
            row.operator('b4ml.pose', text='Start Assisted Pose').operation = 'BEGIN'
        box = layout.box()
        box.label(text='1. Capture Key Poses')
        col = box.column()
        col.enabled = state.candidate_action is None and not state.posing_payload and not state.body_payload and not state.quadruped_payload
        col.prop(state, 'selected_only')
        col.operator('b4ml.action', text='Capture Pose at Current Frame').operation = 'CAPTURE'
        col.operator('b4ml.action', text='Remove Pose at Current Frame').operation = 'REMOVE'
        if state.interpolation_method=='POSES':
            breakdown=col.row();breakdown.enabled=len(state.anchors)>=2
            breakdown.operator('b4ml.breakdown_pose',text='Create Breakdown Pose',icon='KEY_HLT')
            series=col.row();series.enabled=len(state.anchors)>=2
            series.operator('b4ml.inbetween_series',text='Procedural Inbetween Series',icon='KEYFRAME_HLT')
        anchors, anchor_page, anchor_page_count = _anchor_page(state)
        if anchor_page_count > 1:
            row=col.row(align=True)
            previous=row.row(align=True);previous.enabled=anchor_page>1
            operation=previous.operator('b4ml.anchor_page',text='',icon='TRIA_LEFT')
            operation.page=max(1,anchor_page-1)
            row.label(text=_anchor_page_label(anchor_page,anchor_page_count))
            following=row.row(align=True);following.enabled=anchor_page<anchor_page_count
            operation=following.operator('b4ml.anchor_page',text='',icon='TRIA_RIGHT')
            operation.page=min(anchor_page_count,anchor_page+1)
        first_anchor_frame=min((anchor.frame for anchor in state.anchors),default=None)
        last_anchor_frame=max((anchor.frame for anchor in state.anchors),default=None)
        for anchor in anchors:
            row=col.row(align=True);row.label(text=anchor.name,icon='KEY_HLT')
            retime=row.operator('b4ml.retime_anchor',text='',icon='TIME')
            retime.source_frame=anchor.frame
            ripple=row.operator('b4ml.ripple_retime',text='',icon='TRIA_RIGHT')
            ripple.source_frame=anchor.frame
            if last_anchor_frame is not None and abs(anchor.frame-last_anchor_frame)>=1e-5:
                scale=row.operator('b4ml.pose_spacing_scale',text='',icon='FULLSCREEN_ENTER')
                scale.pivot_frame=anchor.frame
                equalize=row.operator('b4ml.pose_spacing_equalize',text='=')
                equalize.pivot_frame=anchor.frame
            if (state.interpolation_method=='POSES' and first_anchor_frame is not None and
                    abs(anchor.frame-first_anchor_frame)>=1e-5):
                edit=row.operator('b4ml.transition_timing',
                    text='Timing*' if workflow.has_transition_timing_override(anchor.payload) else 'Timing')
                edit.frame=anchor.frame
                copy=row.operator('b4ml.transition_timing_transfer',text='',icon='COPYDOWN')
                copy.operation='COPY';copy.frame=anchor.frame
                paste_row=row.row(align=True);paste_row.enabled=bool(state.timing_clipboard)
                paste=paste_row.operator('b4ml.transition_timing_transfer',text='',icon='PASTEDOWN')
                paste.operation='PASTE';paste.frame=anchor.frame
            reuse=row.operator('b4ml.action',text='',icon='DUPLICATE')
            reuse.operation='REUSE';reuse.anchor_frame=anchor.frame
        box = layout.box()
        box.label(text='2. Generate and Review')
        if state.candidate_action:
            box.label(text=state.candidate_action.name, icon='ACTION')
            box.label(text='Scrub the timeline to review.')
            row = box.row(align=True)
            row.operator('b4ml.action', text='Keep Candidate', icon='CHECKMARK').operation = 'KEEP'
            row.operator('b4ml.action', text='Discard', icon='X').operation = 'DISCARD'
        else:
            box.prop(state, 'interpolation_method')
            if state.interpolation_method=='POSES':
                box.prop(state, 'easing')
                box.prop(state, 'timing_bias', slider=True)
                if abs(state.timing_bias) > 1e-6:
                    box.label(text=('Earlier arrival' if state.timing_bias > 0 else 'Later arrival') +
                                   '; pose frames stay fixed.')
            else:
                box.prop(state,'temporal_strength',slider=True)
                box.prop(state,'temporal_smoothing')
                box.label(text='Procedural; strength blends toward endpoint interpolation')
            row = box.row()
            row.enabled = (len(state.anchors) >= 2 and not state.posing_payload and not state.body_payload and not state.quadruped_payload
                           and (state.interpolation_method != 'AUTHORED' or humanoid))
            if state.interpolation_method=='AUTHORED':row.operator('b4ml.temporal_preview',text='Generate Whole-body Preview',icon='PLAY')
            else:row.operator('b4ml.action', text='Generate Interpolation Preview', icon='PLAY').operation = 'PREVIEW'
            if state.interpolation_method=='AUTHORED' and not humanoid:
                box.label(text='Choose Pose Blending for quadrupeds.')
        if state.kept_action and not state.candidate_action and not state.posing_payload and not state.body_payload and not state.quadruped_payload:
            layout.operator('b4ml.action', text='Restore Source Animation').operation = 'RESTORE_SOURCE'
        layout.label(text=state.status)

CLASSES = (B4ML_PG_anchor, B4ML_PG_target, B4ML_PG_joint_limit, B4ML_PG_mass_segment, B4ML_PG_secondary_sphere, B4ML_PG_contact, B4ML_PG_flight, B4ML_PG_settings, B4ML_OT_anchor_page, B4ML_OT_mapping_correction, B4ML_OT_transition_timing, B4ML_OT_breakdown_pose, B4ML_OT_inbetween_series, B4ML_OT_retime_anchor, B4ML_OT_ripple_retime, B4ML_OT_pose_spacing_scale, B4ML_OT_pose_spacing_equalize, B4ML_OT_transition_timing_transfer, B4ML_OT_action, B4ML_OT_pose, B4ML_OT_body, B4ML_OT_body_solve, B4ML_OT_body_live, B4ML_OT_quadruped_pose, B4ML_OT_contact, B4ML_OT_contact_suggest, B4ML_OT_quadruped_gait, B4ML_OT_contact_solve, B4ML_OT_temporal_preview, B4ML_OT_temporal_cancel, B4ML_OT_flight, B4ML_OT_flight_solve, B4ML_OT_cleanup, B4ML_OT_cleanup_solve, B4ML_OT_secondary, B4ML_OT_secondary_select_chain, B4ML_OT_secondary_selection_swap, B4ML_OT_secondary_control_load, B4ML_OT_secondary_sphere, B4ML_OT_secondary_solve, B4ML_OT_support, B4ML_OT_motion_result, B4ML_PT_main)

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
    except Exception:
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
