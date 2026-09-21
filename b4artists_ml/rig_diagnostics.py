"""Read-only, evidence-bounded rig mapping diagnostics.

The report probes the same structural adapters used by animator workflows. It
does not create sessions, normalize modes, write controls, or claim that an
unrecognized hierarchy is compatible.
"""
import json
import math
import bpy

from .rigs import QUADRUPED_REQUIRED, REQUIRED, detect_rig
from . import rig_mapping


_REPORT_KEYS = frozenset({
    'schema', 'profile', 'family', 'mapping_schema', 'bone_count',
    'required_role_count', 'mapped_required_role_count', 'mapped_roles',
    'missing_roles', 'mapped_control_count', 'writable_control_count',
    'blocked_mapped_controls', 'unsafe_mapped_controls',
    'excluded_bone_counts', 'workflows', 'warnings', 'correction_state',
    'manual_corrections', 'correction_error',
})
_EXCLUDED_CATEGORIES = ('deform', 'mechanism', 'organization', 'widget', 'tweak')
_WORKFLOW_LABELS = {
    'automatic_capture': 'Automatic Pose Capture',
    'pose_blending': 'Pose Blending',
    'humanoid_whole_body': 'Humanoid Whole-Body Pose',
    'quadruped_whole_body': 'Quadruped Whole-Body Pose',
}
_FAMILY_SCHEMAS = {'humanoid': 'humanoid_v1', 'quadruped': 'quadruped_v1', 'unknown': 'unmapped'}
_MAX_TEXT = 512
_MAX_BONES = 100000
_MAX_REPORT_CHARS = 262144


def _excluded_category(name):
    return rig_mapping.structural_category(name)


def _probe(identifier, label, applicable, operation):
    if not applicable:
        return {'id': identifier, 'label': label, 'applicable': False,
                'ready': False, 'detail': 'Not applicable to this rig family'}
    try:
        operation()
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        detail = (str(exc).strip() or type(exc).__name__)[:_MAX_TEXT]
        return {'id': identifier, 'label': label, 'applicable': True,
                'ready': False, 'detail': detail}
    return {'id': identifier, 'label': label, 'applicable': True,
            'ready': True, 'detail': 'Read-only preflight passed'}


def _reject_active_preview(obj, label):
    state = obj.b4ml
    if (state.candidate_action or state.posing_payload or state.body_payload
            or state.quadruped_payload):
        raise ValueError('Keep or cancel the active preview before ' + label)


def _body_geometry(obj, binding):
    names = binding['names']
    if len(names) != 17:
        raise ValueError('Whole-body adapter requires 17 ordered semantic joints')
    points = [obj.matrix_world @ obj.data.bones[name].head_local for name in names]
    if any(not all(math.isfinite(value) for value in point) for point in points):
        raise ValueError('Rig produced nonfinite rest-joint positions')
    left = points[11] - points[14]
    up = (points[5] + points[8] - points[11] - points[14]) * .5
    scale = up.length
    if left.length < 1e-8 or scale < 1e-8:
        raise ValueError('Degenerate body frame')
    left.normalize()
    up -= left * up.dot(left)
    if up.length < 1e-8:
        raise ValueError('Degenerate body frame')


def _blocked_control(obj, name, workflow):
    bone = obj.pose.bones.get(name)
    if bone is None:
        return True
    channels = workflow._channels(bone)
    if not any(channels[key] for key in ('location', 'rotation', 'scale')):
        return True
    if any(not constraint.mute and constraint.influence > 0 for constraint in bone.constraints):
        return True
    paths = {bone.path_from_id(key) for key in (
        'location', 'scale', 'rotation_euler', 'rotation_quaternion', 'rotation_axis_angle')}
    animation = obj.animation_data
    if animation and any(curve.data_path in paths for curve in animation.drivers):
        return True
    return any(not math.isfinite(value) or value <= 0 for value in bone.scale)


def analyze(obj):
    """Return a JSON-safe report without mutating *obj* or global runtime state."""
    from . import body_solver, motion_layer, posing, quadruped_pose, workflow

    profile, correction_rows, correction_error = rig_mapping.status(obj)
    required = QUADRUPED_REQUIRED if profile.family == 'quadruped' else REQUIRED
    display_roles = (QUADRUPED_REQUIRED if profile.family == 'quadruped' else
                     rig_mapping.HUMANOID_ROLES if profile.family == 'humanoid' else REQUIRED)
    mapped = tuple((role, profile.roles[role]) for role in display_roles if role in profile.roles)
    mapped_required_count = sum(role in profile.roles for role in required)
    missing = tuple(role for role in required if role not in profile.roles)
    excluded = {key: [] for key in _EXCLUDED_CATEGORIES}
    for name in sorted(obj.data.bones.keys()):
        category = _excluded_category(name)
        if category:
            excluded[category].append(name)
    unsafe_controls = tuple(sorted(name for name in profile.controls
                                   if _excluded_category(name) is not None))
    blocked_controls = tuple(sorted(name for name in profile.controls
                                    if _blocked_control(obj, name, workflow)
                                    or name in unsafe_controls))

    def automatic_capture():
        _reject_active_preview(obj, 'capturing a pose')
        workflow._reject_nla(obj)
        if correction_error:
            raise ValueError(correction_error)
        if not profile.controls:
            raise ValueError('No automatically mapped animator controls; use Selected Controls Only for manual capture')
        if unsafe_controls:
            raise ValueError('Generated structural bones entered the editable-control set: ' + ', '.join(unsafe_controls[:3]))
        if not any(any(workflow._channels(obj.pose.bones[name])[key]
                       for key in ('location', 'rotation', 'scale')) for name in profile.controls):
            raise ValueError('All automatically mapped control channels are locked')

    def pose_blending():
        _reject_active_preview(obj, 'interpolating poses')
        if motion_layer.find(obj):
            raise ValueError('Restore the kept motion source before generating another candidate')
        workflow._reject_nla(obj)
        workflow.read_anchors(obj)

    def humanoid_whole_body():
        _reject_active_preview(obj, 'whole-body posing')
        if body_solver._SESSIONS.get(obj.as_pointer()) is not None:
            raise ValueError('Another contextual session owns this rig')
        if getattr(getattr(bpy.context, 'screen', None), 'is_animation_playing', False):
            raise ValueError('Stop playback before posing')
        workflow._reject_nla(obj)
        posing._check_space(obj)
        binding = body_solver.mapping(obj, writable=True)
        _body_geometry(obj, binding)

    def quadruped_whole_body():
        _reject_active_preview(obj, 'quadruped posing')
        if getattr(getattr(bpy.context, 'screen', None), 'is_animation_playing', False):
            raise ValueError('Stop playback before quadruped posing')
        workflow._reject_nla(obj)
        posing._check_space(obj)
        profile, body, limbs = quadruped_pose.binding(obj)
        quadruped_pose._require_ik(obj, limbs)
        head = quadruped_pose._head_control(profile, obj)
        spine = quadruped_pose._spine_controls(profile, obj)
        follow = float(obj.b4ml.quadruped_spine_follow)
        neck_share = float(obj.b4ml.quadruped_neck_share)
        if not all(math.isfinite(value) and 0.0 <= value <= 1.0
                   for value in (follow, neck_share)):
            raise ValueError('Quadruped spine settings must be finite values from zero to one')
        rotate = [head]
        rotate.extend(spine[role] for role, amount in
                      quadruped_pose._spine_weights(follow, neck_share).items() if amount > 0.0)
        use_poles = bool(obj.b4ml.quadruped_use_poles)
        if use_poles:
            quadruped_pose._require_pole_vectors(obj, limbs)
        quadruped_pose._check_writable(obj, body, limbs, rotate,
                                       (row['pole'] for row in limbs) if use_poles else ())

    workflows = (
        _probe('automatic_capture', 'Automatic Pose Capture', True, automatic_capture),
        _probe('pose_blending', 'Pose Blending', True, pose_blending),
        _probe('humanoid_whole_body', 'Humanoid Whole-Body Pose',
               profile.family == 'humanoid', humanoid_whole_body),
        _probe('quadruped_whole_body', 'Quadruped Whole-Body Pose',
               profile.family == 'quadruped', quadruped_whole_body),
    )
    return {
        'schema': 2,
        'profile': profile.name,
        'family': profile.family,
        'mapping_schema': profile.schema,
        'bone_count': len(obj.data.bones),
        'required_role_count': len(required),
        'mapped_required_role_count': mapped_required_count,
        'mapped_roles': [{'role': role, 'bone': bone} for role, bone in mapped],
        'missing_roles': list(missing),
        'mapped_control_count': len(profile.controls),
        'writable_control_count': len(profile.controls) - len(blocked_controls),
        'blocked_mapped_controls': list(blocked_controls),
        'unsafe_mapped_controls': list(unsafe_controls),
        'excluded_bone_counts': {key: len(value) for key, value in excluded.items()},
        'workflows': list(workflows),
        'warnings': list(profile.warnings),
        'correction_state': ('invalid' if correction_error else
                             'active' if correction_rows else 'none'),
        'manual_corrections': [{'role': role, 'bone': bone}
                               for role, bone in correction_rows],
        'correction_error': correction_error[:_MAX_TEXT],
    }


def decode(value):
    """Return a bounded, internally consistent report, or ``None`` for corrupt data."""
    if not isinstance(value, str) or not value or len(value) > _MAX_REPORT_CHARS:
        return None
    try:
        report = json.loads(value)
    except (TypeError, ValueError, RecursionError):
        return None
    if not isinstance(report, dict) or report.get('schema') != 2 or set(report) != _REPORT_KEYS:
        return None
    if (not isinstance(report['mapped_roles'], list)
            or not isinstance(report['missing_roles'], list)
            or not isinstance(report['blocked_mapped_controls'], list)
            or not isinstance(report['unsafe_mapped_controls'], list)
            or not isinstance(report['excluded_bone_counts'], dict)
            or not isinstance(report['workflows'], list)
            or not isinstance(report['warnings'], list)
            or not isinstance(report['manual_corrections'], list)):
        return None
    if any(not isinstance(report[key], str) or not report[key] or len(report[key]) > _MAX_TEXT
           for key in ('profile', 'family', 'mapping_schema')):
        return None
    if report['family'] not in _FAMILY_SCHEMAS or report['mapping_schema'] != _FAMILY_SCHEMAS[report['family']]:
        return None
    if (not isinstance(report['correction_state'], str)
            or report['correction_state'] not in {'none', 'active', 'invalid'}
            or not isinstance(report['correction_error'], str)
            or len(report['correction_error']) > _MAX_TEXT
            or len(report['manual_corrections']) > len(rig_mapping.HUMANOID_ROLES)):
        return None
    count_keys = ('bone_count', 'required_role_count', 'mapped_required_role_count',
                  'mapped_control_count', 'writable_control_count')
    if any(type(report[key]) is not int or not 0 <= report[key] <= _MAX_BONES for key in count_keys):
        return None
    if (report['mapped_required_role_count'] > report['required_role_count']
            or report['mapped_control_count'] > report['bone_count']
            or report['writable_control_count'] > report['mapped_control_count']):
        return None
    required_roles = set(QUADRUPED_REQUIRED if report['family'] == 'quadruped' else REQUIRED)
    allowed_roles = set(QUADRUPED_REQUIRED if report['family'] == 'quadruped' else
                        rig_mapping.HUMANOID_ROLES if report['family'] == 'humanoid' else REQUIRED)
    if report['required_role_count'] != len(required_roles):
        return None
    text_lists = ('missing_roles', 'blocked_mapped_controls', 'unsafe_mapped_controls', 'warnings')
    list_limits = {'missing_roles': len(required_roles),
                   'blocked_mapped_controls': report['mapped_control_count'],
                   'unsafe_mapped_controls': report['mapped_control_count'],
                   'warnings': 64}
    if any(len(report[key]) > list_limits[key] or any(
            not isinstance(item, str) or not item or len(item) > _MAX_TEXT for item in report[key])
            for key in text_lists):
        return None
    if any(len(report[key]) != len(set(report[key])) for key in text_lists[:-1]):
        return None
    if (len(report['blocked_mapped_controls'])
            != report['mapped_control_count'] - report['writable_control_count']
            or not set(report['unsafe_mapped_controls']) <= set(report['blocked_mapped_controls'])):
        return None
    if set(report['excluded_bone_counts']) != set(_EXCLUDED_CATEGORIES):
        return None
    if any(type(item) is not int or not 0 <= item <= report['bone_count']
           for item in report['excluded_bone_counts'].values()):
        return None
    if sum(report['excluded_bone_counts'].values()) > report['bone_count']:
        return None
    if len(report['workflows']) != len(_WORKFLOW_LABELS):
        return None
    for row in report['workflows']:
        if (not isinstance(row, dict)
                or set(row) != {'id', 'label', 'applicable', 'ready', 'detail'}
                or not isinstance(row.get('id'), str)
                or row.get('id') not in _WORKFLOW_LABELS
                or row.get('label') != _WORKFLOW_LABELS.get(row.get('id'))
                or not isinstance(row.get('detail'), str) or not row['detail']
                or len(row['detail']) > _MAX_TEXT
                or type(row.get('applicable')) is not bool or type(row.get('ready')) is not bool
                or row['ready'] and not row['applicable']):
            return None
    if {row['id'] for row in report['workflows']} != set(_WORKFLOW_LABELS):
        return None
    applicability = {'automatic_capture': True, 'pose_blending': True,
                     'humanoid_whole_body': report['family'] == 'humanoid',
                     'quadruped_whole_body': report['family'] == 'quadruped'}
    if any(row['applicable'] != applicability[row['id']] for row in report['workflows']):
        return None
    if len(report['mapped_roles']) > len(allowed_roles):
        return None
    for row in report['mapped_roles']:
        if (not isinstance(row, dict) or set(row) != {'role', 'bone'}
                or any(not isinstance(row[key], str) or not row[key] or len(row[key]) > _MAX_TEXT
                       for key in ('role', 'bone'))):
            return None
    mapped_roles = [row['role'] for row in report['mapped_roles']]
    if (len(mapped_roles) != len(set(mapped_roles))
            or not set(mapped_roles) <= allowed_roles
            or report['mapped_required_role_count'] != len(set(mapped_roles) & required_roles)
            or set(report['missing_roles']) != required_roles - set(mapped_roles)
            or len(report['missing_roles']) != report['required_role_count'] - report['mapped_required_role_count']):
        return None
    corrections = report['manual_corrections']
    for row in corrections:
        if (not isinstance(row, dict) or set(row) != {'role', 'bone'}
                or not isinstance(row.get('role'), str)
                or row.get('role') not in rig_mapping.HUMANOID_ROLES
                or not isinstance(row.get('bone'), str) or not row['bone']
                or len(row['bone']) > _MAX_TEXT):
            return None
    correction_roles = [row['role'] for row in corrections]
    correction_bones = [row['bone'] for row in corrections]
    if (len(correction_roles) != len(set(correction_roles))
            or len(correction_bones) != len(set(correction_bones))):
        return None
    if report['correction_state'] == 'none' and (corrections or report['correction_error']):
        return None
    if report['correction_state'] == 'active':
        mapped_lookup = {row['role']: row['bone'] for row in report['mapped_roles']}
        if (report['family'] != 'humanoid' or not corrections or report['correction_error']
                or any(mapped_lookup.get(row['role']) != row['bone'] for row in corrections)):
            return None
    if report['correction_state'] == 'invalid' and (corrections or not report['correction_error']):
        return None
    return report
