"""Real BoneForge/Rigify selected-control secondary-motion workflows."""
from pathlib import Path
import json
import math
import os
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get('B4ML_PACKAGE', str(ROOT)), str(ROOT/'tests')]

import bpy
from mathutils import Euler, Quaternion, Vector
import b4artists_ml
from b4artists_ml import secondary_motion as secondary, workflow as w, flight, support
from b4artists_ml.rigs import detect_rig
from test_b4artists_ml_contacts import fixture as base_fixture

RECORDS = []


def fixture(label='boneforge'):
    obj, source, source_signature, modes = base_fixture(label, transformed=True)
    state = obj.b4ml
    state.contacts.clear()
    profile = detect_rig(obj.data.bones.keys())
    name = profile.roles['chest']
    bone = obj.pose.bones[name]
    prop, count = secondary._rotation_spec(bone)
    path = bone.path_from_id(prop)
    curves = w.action_curves(state.candidate_action, getattr(obj.animation_data, 'action_slot', None))
    group = [curves.find(path, index=index) for index in range(count)]
    if any(curve is None for curve in group):
        raise AssertionError('Fixture candidate lacks complete chest rotation curves')
    for frame in range(1, 12):
        angle = .65 * math.sin((frame-1) * math.pi / 5)
        if bone.rotation_mode == 'QUATERNION':
            values = tuple(Quaternion((0, 0, 1), angle))
        elif bone.rotation_mode == 'AXIS_ANGLE':
            values = (angle, 0., 0., 1.)
        else:
            values = tuple(Euler((0., 0., angle), bone.rotation_mode))
        for index, curve in enumerate(group):
            key = min(curve.keyframe_points, key=lambda item: abs(float(item.co.x)-frame))
            key.co.y = values[index]
            key.interpolation = 'LINEAR'
            curve.update()
    for pose_bone in obj.pose.bones:
        if hasattr(pose_bone, 'select'):
            pose_bone.select = False
        else:
            pose_bone.bone.select = False
    if hasattr(bone, 'select'):
        bone.select = True
    else:
        bone.bone.select = True
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.context.scene.frame_set(6)
    return obj, source, source_signature, modes, name, path


def curve_values(action, obj, path):
    curves = w.action_curves(action, next((slot for slot in action.slots if slot.identifier == w._slot(obj.animation_data)), None))
    result = []
    for curve in curves:
        if curve.data_path == path:
            result.append((curve.array_index, [(float(key.co.x), float(key.co.y), key.interpolation) for key in curve.keyframe_points]))
    return sorted(result)


def location_chain_key_values(action, obj, chain, frames=None):
    """Return exact selected-chain location key coordinates for comparison."""
    wanted = None if frames is None else {float(frame) for frame in frames}
    rows = []
    for _, path, _ in chain:
        for index, keys in curve_values(action, obj, path):
            rows.append((path, index, tuple(
                (frame, value) for frame, value, _interpolation in keys
                if wanted is None or frame in wanted)))
    return tuple(sorted(rows))


def rotation_chain(obj):
    """Find a two-control direct hierarchy with complete candidate curves."""
    captured = set(json.loads(obj.b4ml.anchors[0].payload)['pose'])
    curves = w.action_curves(obj.b4ml.candidate_action,
                             getattr(obj.animation_data, 'action_slot', None))
    eligible = {}
    for bone in obj.pose.bones:
        if bone.name not in captured or not w._channels(bone)['rotation']:
            continue
        prop, count = secondary._rotation_spec(bone)
        path = bone.path_from_id(prop)
        if all(curves.find(path, index=index) is not None for index in range(count)):
            eligible[bone.name] = (bone, path, count)
    for child_name, (child, _, _) in eligible.items():
        if child.parent and child.parent.name in eligible:
            return [eligible[child.parent.name], eligible[child_name]]
    raise AssertionError('Fixture has no direct two-control rotation chain')


def location_chain(obj):
    """Find a two-control direct hierarchy with complete location curves."""
    captured = set(json.loads(obj.b4ml.anchors[0].payload)['pose'])
    curves = w.action_curves(obj.b4ml.candidate_action,
                             getattr(obj.animation_data, 'action_slot', None))
    eligible = {}
    for bone in obj.pose.bones:
        if (bone.name not in captured
                or w._channels(bone)['location'] != [0, 1, 2]):
            continue
        path = bone.path_from_id('location')
        if all(curves.find(path, index=index) is not None for index in range(3)):
            eligible[bone.name] = (bone, path, 3)
    for child_name, (child, _, _) in eligible.items():
        if child.parent and child.parent.name in eligible:
            return [eligible[child.parent.name], eligible[child_name]]
    raise AssertionError('Fixture has no direct two-control location chain')


def animate_rotation_group(action, obj, definition, amplitude):
    bone, path, count = definition
    curves = w.action_curves(action, getattr(obj.animation_data, 'action_slot', None))
    group = [curves.find(path, index=index) for index in range(count)]
    for frame in range(1, 12):
        angle = amplitude*math.sin((frame-1)*math.pi/5)
        if bone.rotation_mode == 'QUATERNION':
            values = tuple(Quaternion((0, 0, 1), angle))
        elif bone.rotation_mode == 'AXIS_ANGLE':
            values = (angle, 0., 0., 1.)
        else:
            values = tuple(Euler((0., 0., angle), bone.rotation_mode))
        for index, curve in enumerate(group):
            key = min(curve.keyframe_points,
                      key=lambda item: abs(float(item.co.x)-frame))
            key.co.y = values[index]
            key.interpolation = 'LINEAR'
            curve.update()


def animate_location_group(action, obj, definition, amplitude):
    _, path, _ = definition
    curves = w.action_curves(action, getattr(obj.animation_data, 'action_slot', None))
    curve = curves.find(path, index=0)
    for frame in range(1, 12):
        key = min(curve.keyframe_points,
                  key=lambda item: abs(float(item.co.x)-frame))
        key.co.y += amplitude*math.sin((frame-1)*math.pi/5)
        key.interpolation = 'LINEAR'
        curve.update()


def make_static_sphere(name, center):
    collider = bpy.data.objects.new(name, None)
    collider.empty_display_type = 'SPHERE'
    collider.empty_display_size = 1.0
    collider.location = center
    bpy.context.scene.collection.objects.link(collider)
    bpy.context.view_layer.update()
    return collider


def make_static_endpoint(name, center):
    endpoint = bpy.data.objects.new(name, None)
    endpoint.empty_display_type = 'SPHERE'
    endpoint.empty_display_size = .1
    endpoint.location = center
    bpy.context.scene.collection.objects.link(endpoint)
    bpy.context.view_layer.update()
    return endpoint


def make_static_mesh(name, center, depth=2.0):
    vertices = (
        (-4., -4., -depth), (-4., 4., -depth),
        (-4., 4., 0.), (-4., -4., 0.),
        (4., -4., -depth), (4., -4., 0.),
        (4., 4., 0.), (4., 4., -depth))
    faces = (
        (0, 1, 2, 3), (4, 5, 6, 7), (0, 4, 7, 1),
        (3, 2, 6, 5), (0, 3, 5, 4), (1, 7, 6, 2))
    data = bpy.data.meshes.new(name + ' Data')
    data.from_pydata(vertices, [], faces)
    data.update()
    collider = bpy.data.objects.new(name, data)
    collider.location = center
    bpy.context.scene.collection.objects.link(collider)
    bpy.context.view_layer.update()
    return collider


class SecondaryMotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()

    def test_boneforge_and_rigify_selected_rotation_workflow(self):
        for label in ('boneforge', 'rigify_default'):
            with self.subTest(rig=label):
                obj, source, source_signature, modes, name, path = fixture(label)
                scene = bpy.context.scene
                original = obj.b4ml.candidate_action
                priority = obj.b4ml.anchors.add()
                priority.frame = 6.
                priority.payload = obj.b4ml.anchors[0].payload
                input_token = flight._curve_token(obj, original)
                before = curve_values(original, obj, path)
                steps = []
                secondary.start(obj, scene)
                while True:
                    began = time.perf_counter()
                    done = secondary.step(obj)
                    steps.append((time.perf_counter()-began)*1000)
                    if done:
                        break
                report = json.loads(obj.b4ml.secondary_metrics)
                output = obj.b4ml.candidate_action
                self.assertEqual(report['backend'], 'implicit_selected_control_secondary_v2')
                self.assertEqual(report['controls'], [name])
                self.assertEqual(report['priority_poses'], 3)
                self.assertTrue(report['priority_poses_preserved'])
                self.assertFalse(report['learned'])
                self.assertGreater(report['max_rotation_correction_radians'], .01)
                self.assertIs(obj.b4ml.secondary_input, original)
                self.assertIs(obj.b4ml.secondary_output, output)
                self.assertEqual(flight._curve_token(obj, original), input_token)
                after = curve_values(output, obj, path)
                self.assertNotEqual(after, before)
                for axis_before, axis_after in zip(before, after):
                    self.assertEqual(axis_before[1][0][1], axis_after[1][0][1])
                    self.assertEqual(axis_before[1][5][1], axis_after[1][5][1])
                    self.assertEqual(axis_before[1][-1][1], axis_after[1][-1][1])
                self.assertTrue(all(key[2] == 'LINEAR' for _, values in after for key in values[:-1]))
                RECORDS.append(dict(fixture=label, step_p95_ms=float(max(steps)), **report))
                secondary.restore(obj, scene)
                self.assertIs(obj.b4ml.candidate_action, original)
                self.assertEqual(curve_values(original, obj, path), before)
                w.finish_preview(obj, scene, False)
                self.assertIs(obj.animation_data.action, source)

    def test_selected_location_curves(self):
        obj, _, _, _, chest, _ = fixture('boneforge')
        scene = bpy.context.scene
        curves = w.action_curves(obj.b4ml.candidate_action, getattr(obj.animation_data, 'action_slot', None))
        chosen = None
        for bone in obj.pose.bones:
            path = bone.path_from_id('location')
            group = [curves.find(path, index=index) for index in range(3)]
            if w._channels(bone)['location'] == [0, 1, 2] and all(group):
                chosen = bone, path, group
                break
        self.assertIsNotNone(chosen)
        bone, path, group = chosen
        for pose_bone in obj.pose.bones:
            if hasattr(pose_bone, 'select'):pose_bone.select = False
            else:pose_bone.bone.select = False
        if hasattr(bone, 'select'):bone.select = True
        else:bone.bone.select = True
        for frame in range(1, 12):
            key = min(group[0].keyframe_points, key=lambda item: abs(float(item.co.x)-frame))
            key.co.y = .2*math.sin((frame-1)*math.pi/5)
            key.interpolation = 'LINEAR';group[0].update()
        before = curve_values(obj.b4ml.candidate_action, obj, path)
        obj.b4ml.secondary_rotation = False
        obj.b4ml.secondary_location = True
        report = secondary.solve(obj, scene)
        self.assertEqual(report['controls'], [bone.name])
        self.assertGreater(report['max_location_correction'], .005)
        after = curve_values(obj.b4ml.candidate_action, obj, path)
        self.assertNotEqual(after, before)
        secondary.restore(obj, scene)
        self.assertEqual(curve_values(obj.b4ml.candidate_action, obj, path), before)

    def test_coupled_local_rotation_chain_is_editable_and_length_preserving(self):
        obj, _, _, _, _, _ = fixture('boneforge')
        scene = bpy.context.scene
        state = obj.b4ml
        chain = rotation_chain(obj)
        for index, definition in enumerate(chain):
            animate_rotation_group(state.candidate_action, obj, definition, .5/(index+1))
        for bone in obj.pose.bones:
            if hasattr(bone, 'select'):
                bone.select = False
            else:
                bone.bone.select = False
        for bone, _, _ in chain:
            if hasattr(bone, 'select'):
                bone.select = True
            else:
                bone.bone.select = True
        priority = state.anchors.add()
        priority.frame = 6.
        priority.payload = state.anchors[0].payload
        source = state.candidate_action
        before = {path: curve_values(source, obj, path) for _, path, _ in chain}
        source_lengths = []
        for frame in range(1, 12):
            scene.frame_set(frame)
            source_lengths.append((chain[1][0].head-chain[0][0].head).length)
        scene.frame_set(6)
        state.secondary_space = 'LOCAL'
        state.secondary_rotation = True
        state.secondary_location = False
        state.secondary_chain = True
        state.secondary_chain_propagation = .8
        report = secondary.solve(obj, scene)
        self.assertEqual(report['backend'], 'implicit_selected_control_chain_v1')
        self.assertTrue(report['chain'])
        self.assertEqual(report['chain_controls'], [item[0].name for item in chain])
        self.assertEqual(report['chain_links'], 1)
        self.assertAlmostEqual(report['chain_propagation'], .8, places=6)
        self.assertTrue(report['priority_poses_preserved'])
        self.assertGreater(report['max_rotation_correction_radians'], .01)
        for _, path, _ in chain:
            after = curve_values(state.candidate_action, obj, path)
            self.assertNotEqual(before[path], after)
            for axis_before, axis_after in zip(before[path], after):
                for priority_index in (0, 5, -1):
                    self.assertEqual(axis_before[1][priority_index][1],
                                     axis_after[1][priority_index][1])
                self.assertTrue(all(key[2] == 'LINEAR' for key in axis_after[1][:-1]))
        maximum_length_error = 0.
        for frame, expected in zip(range(1, 12), source_lengths):
            scene.frame_set(frame)
            actual = (chain[1][0].head-chain[0][0].head).length
            maximum_length_error = max(maximum_length_error, abs(actual-expected))
        self.assertLessEqual(maximum_length_error, 1e-6)
        RECORDS.append(dict(fixture='boneforge', case='local_rotation_chain',
                            maximum_link_length_error=maximum_length_error, **report))
        secondary.restore(obj, scene)
        self.assertIs(state.candidate_action, source)
        for _, path, _ in chain:
            self.assertEqual(curve_values(source, obj, path), before[path])

    def test_coupled_chain_rejects_disconnected_selection_and_world_space(self):
        obj, _, _, _, _, _ = fixture('boneforge')
        state = obj.b4ml
        chain = rotation_chain(obj)
        for bone in obj.pose.bones:
            if hasattr(bone, 'select'):
                bone.select = False
            else:
                bone.bone.select = False
        for bone, _, _ in chain:
            if hasattr(bone, 'select'):
                bone.select = True
            else:
                bone.bone.select = True
        state.secondary_chain = True
        state.secondary_space = 'WORLD'
        with self.assertRaisesRegex(ValueError, r'Local\+Rotation or World\+Location'):
            secondary.solve(obj, bpy.context.scene)
        state.secondary_space = 'LOCAL'
        extra = next(bone for bone in obj.pose.bones
                     if bone.name not in {item[0].name for item in chain}
                     and bone.parent not in {item[0] for item in chain})
        if hasattr(extra, 'select'):
            extra.select = True
        else:
            extra.bone.select = True
        with self.assertRaisesRegex(ValueError, 'unbranched direct parent-child'):
            secondary.solve(obj, bpy.context.scene)

    def test_coupled_world_location_chain_transfers_authored_load_momentum(self):
        self._run_world_location_chain_case('boneforge')

    def _run_world_location_chain_case(self, label, collision=False):
        obj, _, _, _, _, _ = fixture(label)
        scene = bpy.context.scene
        state = obj.b4ml
        chain = location_chain(obj)
        for index, definition in enumerate(chain):
            animate_location_group(state.candidate_action, obj, definition, .12/(index+1))
        for bone in obj.pose.bones:
            if hasattr(bone, 'select'):
                bone.select = False
            else:
                bone.bone.select = False
        for bone, _, _ in chain:
            if hasattr(bone, 'select'):
                bone.select = True
            else:
                bone.bone.select = True
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        if obj.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
        secondary.assign_control_loads(obj, (0., 0., -4.), 2.)
        if collision:
            heights = []
            positions = []
            for frame in (1., 6., 11.):
                scene.frame_set(int(frame))
                for bone, _, _ in chain:
                    position = (w.display_world(obj) @ bone.matrix).translation.copy()
                    heights.append(float(position.z))
                    positions.append(position)
            scene.frame_set(1)
            state.secondary_collision = True
            if collision in {
                    'SPHERE', 'SPHERE_SET', 'MOVING_SPHERE',
                    'MOVING_SPHERE_CONTINUOUS', 'COMPOUND',
                    'COMPOUND_MOVING_SPHERE',
                    'COMPOUND_MIXED_SPHERES',
                    'COMPOUND_MOVING_SPHERE_SET',
                    'COMPOUND_MOVING_SPHERE_STATIC_SET',
                    'COMPOUND_MOVING_SPHERE_TRIPLE',
                    'COMPOUND_MOVING_SPHERE_TRIPLE_STATIC_SET',
                    'COMPOUND_MOVING_SPHERE_QUAD',
                    'COMPOUND_MOVING_CAPSULE',
                    'COMPOUND_CAPSULE', 'COMPOUND_MESH',
                    'COMPOUND_CAPSULE_MESH'}:
                lowest = min(positions, key=lambda value: value.z)
                collider = make_static_sphere(
                    'B4ML Chain Sphere ' + label,
                    lowest-Vector((0., 0., 1.03)))
                state.secondary_collision_shape = 'SPHERE'
                state.secondary_sphere_collider = collider
                state.secondary_sphere_radius = 1.0
                if collision == 'MOVING_SPHERE':
                    base = collider.location.copy()
                    for frame, offset, scale in (
                            (1.0, -.04, 1.0), (6.0, 0.0, 1.08),
                            (11.0, .04, 1.0)):
                        collider.location = base+Vector((offset, 0., 0.))
                        collider.scale = (scale, scale, scale)
                        collider.keyframe_insert(data_path='location', frame=frame)
                        collider.keyframe_insert(data_path='scale', frame=frame)
                    for curve in w.action_curves(
                            collider.animation_data.action,
                            getattr(collider.animation_data, 'action_slot', None)):
                        for key in curve.keyframe_points:
                            key.interpolation = 'LINEAR'
                    state.secondary_sphere_moving = True
                    state.secondary_sphere_scaling = True
                elif collision == 'MOVING_SPHERE_CONTINUOUS':
                    base = collider.location.copy()
                    for frame, offset, scale in (
                            (1.0, -.04, 1.0), (6.0, 0.0, 1.08),
                            (11.0, .04, 1.0)):
                        collider.location = base+Vector((offset, 0., 0.))
                        collider.scale = (scale, scale, scale)
                        collider.keyframe_insert(data_path='location', frame=frame)
                        collider.keyframe_insert(data_path='scale', frame=frame)
                    for curve in w.action_curves(
                            collider.animation_data.action,
                            getattr(collider.animation_data, 'action_slot', None)):
                        for key in curve.keyframe_points:
                            key.interpolation = 'LINEAR'
                    state.secondary_sphere_moving = True
                    state.secondary_sphere_scaling = True
                    state.secondary_collision_continuous = True
                    secondary.add_sphere_collider(obj, scene)
                    second = make_static_sphere(
                        'B4ML Chain Continuous Sphere B ' + label,
                        base + Vector((.75, 0., 0.)))
                    state.secondary_sphere_collider = second
                    state.secondary_sphere_radius = 1.0
                    state.secondary_sphere_moving = True
                    state.secondary_sphere_scaling = True
                    for frame, offset, scale in (
                            (1.0, -.04, 1.0), (6.0, 0.0, 1.08),
                            (11.0, .04, 1.0)):
                        second.location = (base + Vector((.75 + offset, 0., 0.)))
                        second.scale = (scale, scale, scale)
                        second.keyframe_insert(data_path='location', frame=frame)
                        second.keyframe_insert(data_path='scale', frame=frame)
                    for curve in w.action_curves(
                            second.animation_data.action,
                            getattr(second.animation_data, 'action_slot', None)):
                        for key in curve.keyframe_points:
                            key.interpolation = 'LINEAR'
                    secondary.add_sphere_collider(obj, scene)
                elif collision == 'SPHERE_SET':
                    state.secondary_sphere_collider = collider
                    state.secondary_sphere_radius = 1.0
                    secondary.add_sphere_collider(obj, scene)
                    second = make_static_sphere(
                        'B4ML Chain Sphere B ' + label,
                        collider.location + Vector((.65, 0., 0.)))
                    state.secondary_sphere_collider = second
                    state.secondary_sphere_radius = 1.0
                    state.secondary_sphere_moving = False
                    state.secondary_sphere_scaling = False
                    secondary.add_sphere_collider(obj, scene)
                elif collision in {
                        'COMPOUND_MOVING_SPHERE',
                        'COMPOUND_MIXED_SPHERES',
                        'COMPOUND_MOVING_SPHERE_SET',
                        'COMPOUND_MOVING_SPHERE_STATIC_SET',
                        'COMPOUND_MOVING_SPHERE_TRIPLE',
                        'COMPOUND_MOVING_SPHERE_TRIPLE_STATIC_SET',
                        'COMPOUND_MOVING_SPHERE_QUAD',
                        'COMPOUND_MOVING_CAPSULE',
                        'COMPOUND', 'COMPOUND_CAPSULE', 'COMPOUND_MESH',
                        'COMPOUND_CAPSULE_MESH'}:
                    state.secondary_collision_shape = 'COMPOUND'
                    state.contact_surface = None
                    state.secondary_sphere_collider = collider
                    state.secondary_sphere_radius = 1.0
                    if collision == 'COMPOUND_MOVING_SPHERE':
                        base = collider.location.copy()
                        for frame, offset, scale in (
                                (1.0, -.04, 1.0), (6.0, 0.0, 1.08),
                                (11.0, .04, 1.0)):
                            collider.location = base + Vector((offset, 0., 0.))
                            collider.scale = (scale, scale, scale)
                            collider.keyframe_insert(data_path='location', frame=frame)
                            collider.keyframe_insert(data_path='scale', frame=frame)
                        for curve in w.action_curves(
                                collider.animation_data.action,
                                getattr(collider.animation_data, 'action_slot', None)):
                            for key in curve.keyframe_points:
                                key.interpolation = 'LINEAR'
                        state.secondary_sphere_moving = True
                        state.secondary_sphere_scaling = True
                    elif collision in {
                            'COMPOUND_MOVING_SPHERE_SET',
                            'COMPOUND_MOVING_SPHERE_STATIC_SET',
                            'COMPOUND_MOVING_SPHERE_TRIPLE',
                            'COMPOUND_MOVING_SPHERE_TRIPLE_STATIC_SET',
                            'COMPOUND_MOVING_SPHERE_QUAD'}:
                        base = collider.location.copy()
                        for frame, offset, scale in (
                                (1.0, -.04, 1.0), (6.0, 0.0, 1.08),
                                (11.0, .04, 1.0)):
                            collider.location = base + Vector((offset, 0., 0.))
                            collider.scale = (scale, scale, scale)
                            collider.keyframe_insert(data_path='location', frame=frame)
                            collider.keyframe_insert(data_path='scale', frame=frame)
                        for curve in w.action_curves(
                                collider.animation_data.action,
                                getattr(collider.animation_data, 'action_slot', None)):
                            for key in curve.keyframe_points:
                                key.interpolation = 'LINEAR'
                        state.secondary_sphere_radius = 1.0
                        state.secondary_sphere_moving = True
                        state.secondary_sphere_scaling = True
                        state.secondary_collision_continuous = True
                        secondary.add_sphere_collider(obj, scene)
                        second = make_static_sphere(
                            'B4ML Chain Moving Sphere Set B ' + label,
                            collider.location + Vector((1.65, 0., 0.)))
                        base = second.location.copy()
                        for frame, offset, scale in (
                                (1.0, .22, 1.0), (6.0, 0.0, 1.06),
                                (11.0, -.22, 1.0)):
                            second.location = base + Vector((offset, 0., 0.))
                            second.scale = (scale, scale, scale)
                            second.keyframe_insert(data_path='location', frame=frame)
                            second.keyframe_insert(data_path='scale', frame=frame)
                        for curve in w.action_curves(
                                second.animation_data.action,
                                getattr(second.animation_data, 'action_slot', None)):
                            for key in curve.keyframe_points:
                                key.interpolation = 'LINEAR'
                        state.secondary_sphere_collider = second
                        state.secondary_sphere_radius = .65
                        state.secondary_sphere_moving = True
                        state.secondary_sphere_scaling = True
                        secondary.add_sphere_collider(obj, scene)
                        if collision in {
                                'COMPOUND_MOVING_SPHERE_TRIPLE',
                                'COMPOUND_MOVING_SPHERE_TRIPLE_STATIC_SET',
                                'COMPOUND_MOVING_SPHERE_QUAD'}:
                            third = make_static_sphere(
                                'B4ML Chain Moving Sphere Set C ' + label,
                                base + Vector((1.65, 0., 0.)))
                            third_base = third.location.copy()
                            for frame, offset, scale in (
                                    (1.0, -.16, 1.0), (6.0, 0.0, 1.05),
                                    (11.0, .16, 1.0)):
                                third.location = third_base + Vector((offset, 0., 0.))
                                third.scale = (scale, scale, scale)
                                third.keyframe_insert(data_path='location', frame=frame)
                                third.keyframe_insert(data_path='scale', frame=frame)
                            for curve in w.action_curves(
                                    third.animation_data.action,
                                    getattr(third.animation_data, 'action_slot', None)):
                                for key in curve.keyframe_points:
                                    key.interpolation = 'LINEAR'
                            state.secondary_sphere_collider = third
                            state.secondary_sphere_radius = .45
                            state.secondary_sphere_moving = True
                            state.secondary_sphere_scaling = True
                            secondary.add_sphere_collider(obj, scene)
                            if collision == 'COMPOUND_MOVING_SPHERE_QUAD':
                                fourth = make_static_sphere(
                                    'B4ML Chain Moving Sphere Set D ' + label,
                                    third_base + Vector((1.65, 0., 0.)))
                                fourth_base = fourth.location.copy()
                                for frame, offset, scale in (
                                        (1.0, .12, 1.0), (6.0, 0.0, 1.04),
                                        (11.0, -.12, 1.0)):
                                    fourth.location = fourth_base + Vector((offset, 0., 0.))
                                    fourth.scale = (scale, scale, scale)
                                    fourth.keyframe_insert(data_path='location', frame=frame)
                                    fourth.keyframe_insert(data_path='scale', frame=frame)
                                for curve in w.action_curves(
                                        fourth.animation_data.action,
                                        getattr(fourth.animation_data, 'action_slot', None)):
                                    for key in curve.keyframe_points:
                                        key.interpolation = 'LINEAR'
                                state.secondary_sphere_collider = fourth
                                state.secondary_sphere_radius = .35
                                state.secondary_sphere_moving = True
                                state.secondary_sphere_scaling = True
                                secondary.add_sphere_collider(obj, scene)
                        if collision in {
                                'COMPOUND_MOVING_SPHERE_STATIC_SET',
                                'COMPOUND_MOVING_SPHERE_TRIPLE_STATIC_SET'}:
                            static = make_static_sphere(
                                'B4ML Chain Moving Sphere Static Set C ' + label,
                                base + Vector((.75, 0., 1.0)))
                            state.secondary_sphere_collider = static
                            state.secondary_sphere_radius = .18
                            state.secondary_sphere_moving = False
                            state.secondary_sphere_scaling = False
                            secondary.add_sphere_collider(obj, scene)
                    elif collision == 'COMPOUND_MIXED_SPHERES':
                        state.secondary_sphere_moving = False
                        state.secondary_sphere_scaling = False
                        secondary.add_sphere_collider(obj, scene)
                        moving = make_static_sphere(
                            'B4ML Chain Moving Sphere B ' + label,
                            collider.location + Vector((1.2, 0., 0.)))
                        base = moving.location.copy()
                        for frame, offset, scale in (
                                (1.0, -.22, 1.0), (6.0, .22, 1.08),
                                (11.0, .62, 1.0)):
                            moving.location = base + Vector((offset, 0., 0.))
                            moving.scale = (scale, scale, scale)
                            moving.keyframe_insert(data_path='location', frame=frame)
                            moving.keyframe_insert(data_path='scale', frame=frame)
                        for curve in w.action_curves(
                                moving.animation_data.action,
                                getattr(moving.animation_data, 'action_slot', None)):
                            for key in curve.keyframe_points:
                                key.interpolation = 'LINEAR'
                        state.secondary_sphere_collider = moving
                        state.secondary_sphere_radius = .65
                        state.secondary_sphere_moving = True
                        state.secondary_sphere_scaling = True
                        state.secondary_collision_continuous = True
                        secondary.add_sphere_collider(obj, scene)
                    else:
                        state.secondary_sphere_moving = False
                        state.secondary_sphere_scaling = False
                        state.secondary_collision_continuous = False
                        secondary.add_sphere_collider(obj, scene)
                    if collision in {
                            'COMPOUND_MOVING_CAPSULE',
                            'COMPOUND_CAPSULE', 'COMPOUND_CAPSULE_MESH'}:
                        start = make_static_endpoint(
                            'B4ML Chain Compound Capsule Start ' + label,
                            collider.location + Vector((-.5, 0., .55)))
                        end = make_static_endpoint(
                            'B4ML Chain Compound Capsule End ' + label,
                            collider.location + Vector((.5, 0., .55)))
                        state.secondary_collision_compound_capsule = True
                        state.secondary_capsule_start = start
                        state.secondary_capsule_end = end
                        state.secondary_capsule_radius = .22
                        state.secondary_capsule_moving = False
                        state.secondary_capsule_scaling = False
                        state.secondary_collision_continuous = False
                        if collision == 'COMPOUND_MOVING_CAPSULE':
                            for endpoint, direction in ((start, -1.), (end, 1.)):
                                base = endpoint.location.copy()
                                for frame, offset, scale, z_offset in (
                                        (1.0, -.04, 1.0, -.6),
                                        (3.0, -.02, 1.0, -.6),
                                        (4.0, -.01, 1.08, .6),
                                        (5.0, .01, 1.08, .6),
                                        (6.0, 0.0, 1.0, -.6),
                                        (11.0, .04, 1.0, -.6)):
                                    endpoint.location = base + Vector((direction * offset, 0., z_offset))
                                    endpoint.scale = (scale, scale, scale)
                                    endpoint.keyframe_insert(data_path='location', frame=frame)
                                    endpoint.keyframe_insert(data_path='scale', frame=frame)
                                for curve in w.action_curves(
                                        endpoint.animation_data.action,
                                        getattr(endpoint.animation_data, 'action_slot', None)):
                                    for key in curve.keyframe_points:
                                        key.interpolation = 'LINEAR'
                            state.secondary_capsule_moving = True
                            state.secondary_capsule_scaling = True
                            state.secondary_collision_continuous = True
                    if collision in {'COMPOUND_MESH', 'COMPOUND_CAPSULE_MESH'}:
                        mesh = make_static_mesh(
                            'B4ML Chain Compound Mesh ' + label,
                            positions[-2] - Vector((0., 0., .02)), depth=2.0)
                        mesh.scale = (.05, .05, .05)
                        bpy.context.view_layer.update()
                        state.secondary_collision_compound_mesh = True
                        state.secondary_collision_mesh = mesh
                        state.secondary_collision_mesh_deforming = False
                        state.secondary_collision_mesh_moving = False
                        state.secondary_collision_volume_radius = 0.0
                    if collision not in {
                            'COMPOUND_MOVING_SPHERE',
                            'COMPOUND_MIXED_SPHERES',
                            'COMPOUND_MOVING_SPHERE_SET',
                            'COMPOUND_MOVING_SPHERE_STATIC_SET',
                            'COMPOUND_MOVING_SPHERE_TRIPLE',
                            'COMPOUND_MOVING_SPHERE_TRIPLE_STATIC_SET',
                            'COMPOUND_MOVING_SPHERE_QUAD'}:
                        second = make_static_sphere(
                            'B4ML Chain Sphere B ' + label,
                            collider.location + Vector((.65, 0., 0.)))
                        state.secondary_sphere_collider = second
                        state.secondary_sphere_radius = 1.0
                        secondary.add_sphere_collider(obj, scene)
            elif collision in {
                    'CAPSULE', 'MOVING_CAPSULE', 'MOVING_CAPSULE_ZERO',
                    'MOVING_CAPSULE_CONTINUOUS', 'SCALING_CAPSULE'}:
                lowest = min(positions, key=lambda value: value.z)
                start = make_static_endpoint(
                    'B4ML Chain Capsule Start ' + label,
                    lowest-Vector((0., 0., 2.03)))
                end = make_static_endpoint(
                    'B4ML Chain Capsule End ' + label,
                    lowest-Vector((0., 0., 1.03)))
                state.secondary_collision_shape = 'CAPSULE'
                state.secondary_capsule_start = start
                state.secondary_capsule_end = end
                state.secondary_capsule_radius = 1.0
                state.secondary_capsule_moving = False
                state.secondary_capsule_scaling = False
                state.secondary_collision_continuous = False
                if collision in {
                        'MOVING_CAPSULE', 'MOVING_CAPSULE_ZERO',
                        'MOVING_CAPSULE_CONTINUOUS'}:
                    start_base = start.location.copy()
                    end_base = end.location.copy()
                    for endpoint, base, direction in (
                            (start, start_base, -1.), (end, end_base, 1.)):
                        for frame, offset, scale in (
                                (1., -.04, 1.), (6., 0., 1.08), (11., .04, 1.)):
                            endpoint.location = base+Vector((offset, .02*direction, 0.))
                            endpoint.scale = (scale, scale, scale)
                            endpoint.keyframe_insert(data_path='location', frame=frame)
                            endpoint.keyframe_insert(data_path='scale', frame=frame)
                        for curve in w.action_curves(
                                endpoint.animation_data.action,
                                getattr(endpoint.animation_data, 'action_slot', None)):
                            for key in curve.keyframe_points:
                                key.interpolation = 'LINEAR'
                    state.secondary_capsule_moving = True
                    state.secondary_capsule_scaling = True
                    state.secondary_collision_continuous = (
                        collision == 'MOVING_CAPSULE_CONTINUOUS')
                elif collision == 'SCALING_CAPSULE':
                    for endpoint in (start, end):
                        for frame, scale in ((1., 1.), (6., 1.08), (11., 1.)):
                            endpoint.scale = (scale, scale, scale)
                            endpoint.keyframe_insert(data_path='scale', frame=frame)
                        for curve in w.action_curves(
                                endpoint.animation_data.action,
                                getattr(endpoint.animation_data, 'action_slot', None)):
                            for key in curve.keyframe_points:
                                key.interpolation = 'LINEAR'
                    state.secondary_capsule_scaling = True
            elif collision == 'MESH':
                lowest = min(positions, key=lambda value: value.z)
                collider = make_static_mesh(
                    'B4ML Chain Mesh ' + label,
                    lowest-Vector((0., 0., .012)))
                state.secondary_collision_shape = 'MESH'
                state.secondary_collision_mesh = collider
                state.secondary_collision_mesh_deforming = False
                state.secondary_collision_mesh_moving = False
                state.secondary_collision_continuous = False
            elif collision == 'MESH_CONTINUOUS':
                lowest = min(positions, key=lambda value: value.z)
                collider = make_static_mesh(
                    'B4ML Chain Continuous Mesh ' + label,
                    lowest-Vector((0., 0., .002)), depth=.001)
                state.secondary_collision_shape = 'MESH'
                state.secondary_collision_mesh = collider
                state.secondary_collision_mesh_deforming = False
                state.secondary_collision_mesh_moving = False
                state.secondary_collision_continuous = True
            elif collision == 'MESH_VOLUME_CONTINUOUS':
                lowest = min(positions, key=lambda value: value.z)
                collider = make_static_mesh(
                    'B4ML Chain Volume Mesh ' + label,
                    lowest-Vector((0., 0., .003)), depth=.001)
                state.secondary_collision_shape = 'VOLUME'
                state.secondary_collision_mesh = collider
                state.secondary_collision_mesh_deforming = False
                state.secondary_collision_mesh_moving = False
                state.secondary_collision_volume_radius = .001
                state.secondary_collision_continuous = True
            elif collision == 'MOVING_DEFORMING_MESH_CONTINUOUS':
                lowest = min(positions, key=lambda value: value.z)
                collider = make_static_mesh(
                    'B4ML Chain Moving Deforming Mesh ' + label,
                    lowest-Vector((0., 0., .012)), depth=.02)
                base_location = collider.location.copy()
                for frame, offset in ((1., -.04), (6., 0.), (11., .04)):
                    collider.location = base_location + Vector((offset, 0., 0.))
                    collider.keyframe_insert(data_path='location', frame=frame)
                for curve in w.action_curves(
                        collider.animation_data.action,
                        getattr(collider.animation_data, 'action_slot', None)):
                    for key in curve.keyframe_points:
                        key.interpolation = 'LINEAR'
                basis = collider.shape_key_add(name='Basis')
                deform = collider.shape_key_add(name='Deform')
                for index, point in enumerate(deform.data):
                    point.co = basis.data[index].co
                deform.data[6].co.x += .25
                for frame, value in ((1., 0.), (6., 1.), (11., 0.)):
                    deform.value = value
                    deform.keyframe_insert(data_path='value', frame=frame)
                for curve in w.action_curves(
                        collider.data.shape_keys.animation_data.action,
                        getattr(collider.data.shape_keys.animation_data, 'action_slot', None)):
                    for key in curve.keyframe_points:
                        key.interpolation = 'LINEAR'
                state.secondary_collision_shape = 'MESH'
                state.secondary_collision_mesh = collider
                state.secondary_collision_mesh_deforming = True
                state.secondary_collision_mesh_moving = True
                state.secondary_collision_continuous = True
            else:
                state.secondary_collision_shape = 'PLANE'
                state.support_plane_point = (0., 0., min(heights)-.04)
                state.support_plane_normal = (0., 0., 1.)
            if collision in {
                    'COMPOUND', 'COMPOUND_MOVING_SPHERE',
                    'COMPOUND_MOVING_SPHERE_TRIPLE',
                    'COMPOUND_MOVING_SPHERE_TRIPLE_STATIC_SET',
                    'COMPOUND_MOVING_SPHERE_QUAD',
                    'COMPOUND_MOVING_SPHERE_STATIC_SET',
                    'COMPOUND_MOVING_CAPSULE',
                    'COMPOUND_CAPSULE', 'COMPOUND_MESH',
                    'COMPOUND_CAPSULE_MESH'}:
                state.support_plane_point = (0., 0., min(heights)-.04)
                state.support_plane_normal = (0., 0., 1.)
            state.secondary_gravity = 4.0
            state.secondary_collision_clearance = .01
            state.secondary_restitution = .2
            state.secondary_surface_friction = .4
            if collision == 'MESH_CONTINUOUS':
                state.secondary_collision_clearance = .001
            elif collision == 'MESH_VOLUME_CONTINUOUS':
                state.secondary_collision_clearance = .001
        priority = state.anchors.add()
        priority.frame = 6.
        priority.payload = state.anchors[0].payload
        state.secondary_space = 'WORLD'
        state.secondary_rotation = False
        state.secondary_location = True
        state.secondary_chain = True
        state.secondary_chain_propagation = .85
        zero_strength = collision == 'MOVING_CAPSULE_ZERO'
        input_action = state.candidate_action
        input_location_keys = location_chain_key_values(input_action, obj, chain)
        input_priority_keys = location_chain_key_values(
            input_action, obj, chain, (1., 6., 11.))
        if collision == 'COMPOUND_MOVING_SPHERE_QUAD':
            records, _, _ = secondary._sphere_colliders(state, scene, obj)
            self.assertEqual(sum(bool(item['moving']) for item in records), 4)
            with self.assertRaisesRegex(ValueError, 'one to three moving spheres'):
                secondary.solve(obj, scene)
            self.assertEqual(
                location_chain_key_values(state.candidate_action, obj, chain),
                input_location_keys)
            return
        if zero_strength:
            state.secondary_strength = 0.0
        if collision == 'SCALING_CAPSULE':
            with self.assertRaisesRegex(ValueError, 'scaling-only capsule'):
                secondary.solve(obj, scene)
            return
        report = secondary.solve(obj, scene)
        moving_sphere = collision in {
            'MOVING_SPHERE', 'MOVING_SPHERE_CONTINUOUS',
            'COMPOUND_MOVING_SPHERE', 'COMPOUND_MIXED_SPHERES',
            'COMPOUND_MOVING_SPHERE_SET',
            'COMPOUND_MOVING_SPHERE_STATIC_SET',
            'COMPOUND_MOVING_SPHERE_TRIPLE',
            'COMPOUND_MOVING_SPHERE_TRIPLE_STATIC_SET'}
        moving_sphere_compound = collision == 'COMPOUND_MOVING_SPHERE'
        mixed_moving_sphere_compound = collision == 'COMPOUND_MIXED_SPHERES'
        moving_sphere_set_compound = collision == 'COMPOUND_MOVING_SPHERE_SET'
        mixed_moving_sphere_set_compound = collision == 'COMPOUND_MOVING_SPHERE_STATIC_SET'
        moving_sphere_triple_compound = collision == 'COMPOUND_MOVING_SPHERE_TRIPLE'
        mixed_moving_sphere_triple_compound = (
            collision == 'COMPOUND_MOVING_SPHERE_TRIPLE_STATIC_SET')
        moving_capsule = collision in {
            'MOVING_CAPSULE', 'MOVING_CAPSULE_ZERO',
            'COMPOUND_MOVING_CAPSULE'}
        moving_capsule_compound = collision == 'COMPOUND_MOVING_CAPSULE'
        self.assertEqual(
            report['backend'],
            'implicit_selected_control_chain_location_compound_support_spheres_capsule_mesh_v1'
            if collision == 'COMPOUND_CAPSULE_MESH' else
            'implicit_selected_control_chain_location_compound_support_spheres_capsule_v1'
            if collision == 'COMPOUND_CAPSULE' else
            'implicit_selected_control_chain_location_compound_support_spheres_mesh_v1'
            if collision == 'COMPOUND_MESH' else
            'implicit_selected_control_chain_location_compound_support_spheres_v1'
            if collision == 'COMPOUND' else
            'implicit_selected_control_chain_location_mixed_moving_sphere_triple_set_compound_support_spheres_v1'
            if mixed_moving_sphere_triple_compound else
            'implicit_selected_control_chain_location_moving_sphere_triple_set_compound_support_v1'
            if moving_sphere_triple_compound else
            'implicit_selected_control_chain_location_mixed_moving_sphere_compound_support_spheres_v1'
            if mixed_moving_sphere_compound else
            'implicit_selected_control_chain_location_moving_sphere_set_compound_support_v1'
            if moving_sphere_set_compound else
            'implicit_selected_control_chain_location_mixed_moving_sphere_set_compound_support_spheres_v1'
            if mixed_moving_sphere_set_compound else
            'implicit_selected_control_chain_location_moving_capsule_compound_support_spheres_v1'
            if moving_capsule_compound else
            'implicit_selected_control_chain_location_moving_sphere_compound_support_v1'
            if moving_sphere_compound else
            'implicit_selected_control_chain_location_moving_deforming_mesh_v1'
            if collision == 'MOVING_DEFORMING_MESH_CONTINUOUS' else
            'implicit_selected_control_chain_location_continuous_moving_capsule_v1'
            if collision == 'MOVING_CAPSULE_CONTINUOUS' else
            'implicit_selected_control_chain_location_continuous_sphere_v1'
            if collision == 'MOVING_SPHERE_CONTINUOUS' else
            'implicit_selected_control_chain_location_moving_capsule_v1'
            if moving_capsule else
            'implicit_selected_control_chain_location_moving_sphere_v1'
            if moving_sphere else 'implicit_selected_control_chain_location_v1')
        self.assertEqual(
            report['schema'],
            40 if mixed_moving_sphere_triple_compound else
            39 if moving_sphere_triple_compound else
            38 if mixed_moving_sphere_set_compound else
            37 if moving_sphere_set_compound else
            36 if mixed_moving_sphere_compound else
            35 if moving_capsule_compound else
            32 if collision in {'COMPOUND_MESH', 'COMPOUND_CAPSULE_MESH'} else
            31 if collision in {'COMPOUND', 'COMPOUND_CAPSULE'} else
            34 if moving_sphere_compound else
            28 if collision == 'MOVING_DEFORMING_MESH_CONTINUOUS' else
            30 if collision == 'MOVING_SPHERE_CONTINUOUS' else
            29 if collision == 'MOVING_CAPSULE_CONTINUOUS' else
            27 if moving_capsule else 26 if moving_sphere else 25)
        self.assertEqual(report['chain_mode'], 'WORLD_LOCATION')
        self.assertEqual(report['momentum_transfer'], not zero_strength)
        self.assertLessEqual(report['momentum_conservation_error'], 1e-10)
        self.assertEqual(report['loaded_controls'], 2)
        if collision == 'SPHERE_SET':
            self.assertEqual(report['collision_sphere_count'], 2)
            self.assertEqual(report['collision_collider_count'], 2)
        if collision == 'MOVING_SPHERE_CONTINUOUS':
            self.assertEqual(report['collision_sphere_count'], 2)
            self.assertEqual(report['collision_collider_count'], 2)
        if collision == 'COMPOUND_MOVING_SPHERE':
            self.assertEqual(report['collision_sphere_count'], 1)
            self.assertEqual(report['collision_collider_count'], 2)
            self.assertTrue(report['collision_plane'])
            self.assertTrue(report['collision_compound'])
            self.assertFalse(report['collision_compound_capsule'])
            self.assertFalse(report['collision_compound_mesh'])
            self.assertEqual(
                report['collision_target_space'],
                'static support plane plus one evaluated direct moving sphere and uniform scale')
        if mixed_moving_sphere_compound:
            self.assertEqual(report['collision_sphere_count'], 2)
            self.assertEqual(report['collision_collider_count'], 3)
            self.assertTrue(report['collision_plane'])
            self.assertTrue(report['collision_compound'])
            self.assertFalse(report['collision_compound_capsule'])
            self.assertFalse(report['collision_compound_mesh'])
            self.assertEqual(report['moving_collision_spheres'], 1)
            self.assertEqual(report['scaling_collision_spheres'], 1)
            self.assertEqual(
                report['collision_target_space'],
                'static support plane plus static sphere set plus one evaluated direct moving sphere and uniform scale')
            self.assertGreater(report['continuous_collision_samples'], 0)
            self.assertEqual(
                report['continuous_collision_target_space'],
                'bounded analytic relative-motion moving sphere sweep with support-plane projection')
        if moving_sphere_set_compound:
            self.assertEqual(report['collision_sphere_count'], 2)
            self.assertEqual(report['collision_collider_count'], 3)
            self.assertTrue(report['collision_plane'])
            self.assertTrue(report['collision_compound'])
            self.assertFalse(report['collision_compound_capsule'])
            self.assertFalse(report['collision_compound_mesh'])
            self.assertEqual(report['moving_collision_spheres'], 2)
            self.assertEqual(report['scaling_collision_spheres'], 2)
            self.assertEqual(
                report['collision_target_space'],
                'static support plane plus two evaluated direct moving spheres and uniform scale')
            self.assertGreater(report['continuous_collision_samples'], 0)
            self.assertEqual(
                report['continuous_collision_target_space'],
                'bounded analytic relative-motion moving sphere sweep with support-plane projection')
        if mixed_moving_sphere_set_compound:
            self.assertEqual(report['collision_sphere_count'], 3)
            self.assertEqual(report['collision_collider_count'], 4)
            self.assertTrue(report['collision_plane'])
            self.assertTrue(report['collision_compound'])
            self.assertFalse(report['collision_compound_capsule'])
            self.assertFalse(report['collision_compound_mesh'])
            self.assertEqual(report['moving_collision_spheres'], 2)
            self.assertEqual(report['scaling_collision_spheres'], 2)
            self.assertEqual(
                report['collision_target_space'],
                'static support plane plus static sphere set plus two evaluated direct moving spheres and uniform scale')
            self.assertGreater(report['continuous_collision_samples'], 0)
            self.assertEqual(
                report['continuous_collision_target_space'],
                'bounded analytic relative-motion moving sphere sweep with support-plane projection')
        if moving_sphere_triple_compound:
            self.assertEqual(report['collision_sphere_count'], 3)
            self.assertEqual(report['collision_collider_count'], 4)
            self.assertTrue(report['collision_plane'])
            self.assertTrue(report['collision_compound'])
            self.assertFalse(report['collision_compound_capsule'])
            self.assertFalse(report['collision_compound_mesh'])
            self.assertEqual(report['moving_collision_spheres'], 3)
            self.assertEqual(report['scaling_collision_spheres'], 3)
            self.assertEqual(
                report['collision_target_space'],
                'static support plane plus three evaluated direct moving spheres and uniform scale')
            self.assertGreater(report['continuous_collision_samples'], 0)
            self.assertEqual(
                report['continuous_collision_target_space'],
                'bounded analytic relative-motion moving sphere sweep with support-plane projection')
        if mixed_moving_sphere_triple_compound:
            self.assertEqual(report['collision_sphere_count'], 4)
            self.assertEqual(report['collision_collider_count'], 5)
            self.assertTrue(report['collision_plane'])
            self.assertTrue(report['collision_compound'])
            self.assertFalse(report['collision_compound_capsule'])
            self.assertFalse(report['collision_compound_mesh'])
            self.assertEqual(report['moving_collision_spheres'], 3)
            self.assertEqual(report['scaling_collision_spheres'], 3)
            self.assertEqual(
                report['collision_target_space'],
                'static support plane plus static sphere set plus three evaluated direct moving spheres and uniform scale')
            self.assertGreater(report['continuous_collision_samples'], 0)
            self.assertEqual(
                report['continuous_collision_target_space'],
                'bounded analytic relative-motion moving sphere sweep with support-plane projection')
        if collision in {
                'COMPOUND', 'COMPOUND_MOVING_CAPSULE',
                'COMPOUND_CAPSULE', 'COMPOUND_MESH',
                'COMPOUND_CAPSULE_MESH'}:
            self.assertEqual(report['collision_sphere_count'], 2)
            self.assertEqual(report['collision_collider_count'],
                             5 if collision == 'COMPOUND_CAPSULE_MESH' else
                             4 if collision in {'COMPOUND_MOVING_CAPSULE',
                                                'COMPOUND_CAPSULE',
                                                'COMPOUND_MESH'} else 3)
            self.assertTrue(report['collision_plane'])
            self.assertTrue(report['collision_compound'])
            self.assertEqual(report['collision_compound_capsule'],
                             collision in {'COMPOUND_MOVING_CAPSULE',
                                           'COMPOUND_CAPSULE',
                                           'COMPOUND_CAPSULE_MESH'})
            self.assertEqual(report['collision_compound_mesh'],
                             collision in {'COMPOUND_MESH', 'COMPOUND_CAPSULE_MESH'})
            self.assertEqual(
                report['collision_target_space'],
                'static support plane plus static sphere set plus static capsule plus static closed mesh'
                if collision == 'COMPOUND_CAPSULE_MESH' else
                'static support plane plus static sphere set plus static closed mesh'
                if collision == 'COMPOUND_MESH' else
                'static support plane plus static sphere set plus static capsule'
                if collision == 'COMPOUND_CAPSULE' else
                'static support plane plus static sphere set plus one evaluated moving capsule'
                if moving_capsule_compound else
                'static support plane plus static sphere set')
            if collision in {'COMPOUND_CAPSULE', 'COMPOUND_CAPSULE_MESH'}:
                self.assertIsNotNone(report['collision_capsule_start'])
                self.assertAlmostEqual(report['collision_capsule_radius'], .22, places=6)
            if moving_capsule_compound:
                self.assertEqual(report['collision_collider_count'], 4)
                self.assertTrue(report['collision_capsule_moving'])
                self.assertTrue(report['collision_capsule_scaling'])
                self.assertTrue(report['collision_capsule_continuous'])
                self.assertGreater(report['continuous_collision_samples'], 0)
                self.assertEqual(
                    report['continuous_collision_target_space'],
                    'bounded moving capsule sweep with support-plane and static-sphere projection')
        self.assertTrue(report['priority_poses_preserved'])
        if zero_strength:
            self.assertEqual(report['max_location_correction'], 0.0)
            self.assertEqual(report['collision_samples'], 0)
            self.assertEqual(report['coupled_samples'], 0)
            self.assertEqual(report['max_raw_penetration'], 0.0)
            self.assertEqual(report['max_penetration_after'], 0.0)
            self.assertEqual(
                location_chain_key_values(state.candidate_action, obj, chain),
                input_location_keys)
        else:
            self.assertGreater(report['max_location_correction'], .001)
        self.assertEqual(
            location_chain_key_values(
                state.candidate_action, obj, chain, (1., 6., 11.)),
            input_priority_keys)
        if collision:
            self.assertTrue(report['collision'])
            if not zero_strength:
                self.assertGreater(report['collision_samples'], 0)
            if (not zero_strength
                     and collision not in {'MESH_CONTINUOUS', 'MESH_VOLUME_CONTINUOUS',
                                           'COMPOUND_MIXED_SPHERES',
                                           'COMPOUND_MOVING_SPHERE_SET',
                                          'COMPOUND_MOVING_SPHERE_STATIC_SET',
                                          'COMPOUND_MOVING_SPHERE_TRIPLE',
                                          'COMPOUND_MOVING_SPHERE_TRIPLE_STATIC_SET'}):
                self.assertGreater(report['max_raw_penetration'], 0., report)
            penetration_limit = 1e-6 if moving_capsule_compound else 1e-8
            self.assertLessEqual(
                report['max_penetration_after'], penetration_limit,
                {key: report[key] for key in (
                    'max_penetration_after', 'max_raw_penetration',
                    'collision_samples', 'continuous_collision_samples',
                    'collision_sphere_count', 'collision_collider_count')})
            if collision == 'MESH_CONTINUOUS':
                self.assertGreater(report['continuous_collision_samples'], 0, report)
            if collision == 'MESH_VOLUME_CONTINUOUS':
                self.assertTrue(report['collision_mesh_exact_swept_volume'])
                self.assertGreater(report['continuous_collision_samples'], 0, report)
                self.assertEqual(
                    report['collision_target_space'],
                    'exact swept-sphere closed evaluated triangle volume')
            if collision == 'MOVING_DEFORMING_MESH_CONTINUOUS':
                self.assertGreater(report['continuous_collision_samples'], 0, report)
                self.assertEqual(
                    report['collision_target_space'],
                    'continuous-time closed moving deforming triangle mesh')
            if collision == 'MOVING_CAPSULE_CONTINUOUS':
                self.assertGreater(report['continuous_collision_samples'], 0, report)
                self.assertEqual(
                    report['collision_target_space'],
                    'bounded continuous-time moving/deforming capsule')
            if collision == 'MOVING_SPHERE_CONTINUOUS':
                self.assertGreater(report['continuous_collision_samples'], 0, report)
                self.assertEqual(
                    report['continuous_collision_target_space'],
                    'bounded analytic relative-motion sphere sweep')
            if (moving_sphere or moving_capsule) and not zero_strength:
                self.assertTrue(report['relative_velocity_response'])
                self.assertTrue(report['relative_radius_velocity_response'])
            if zero_strength:
                self.assertFalse(report['collision_influence_active'])
                self.assertFalse(report['relative_velocity_response'])
                self.assertFalse(report['relative_radius_velocity_response'])
        RECORDS.append(dict(fixture=label, case='world_location_chain', **report))
        if zero_strength:
            self.assertIs(state.candidate_action, input_action)
            self.assertIs(obj.animation_data.action, input_action)
            return
        secondary.restore(obj, scene)

    def test_coupled_world_location_chain_on_rigify_profiles(self):
        for label in ('rigify_default', 'rigify_basic'):
            with self.subTest(fixture=label):
                self._run_world_location_chain_case(label)

    def test_coupled_world_location_chain_plane_collision(self):
        self._run_world_location_chain_case('boneforge', collision=True)

    def test_coupled_world_location_chain_static_sphere_collision(self):
        self._run_world_location_chain_case('boneforge', collision='SPHERE')

    def test_coupled_world_location_chain_static_sphere_set_collision(self):
        self._run_world_location_chain_case('boneforge', collision='SPHERE_SET')

    def test_coupled_world_location_chain_compound_support_sphere_collision(self):
        self._run_world_location_chain_case('boneforge', collision='COMPOUND')

    def test_coupled_world_location_chain_compound_support_moving_sphere_collision(self):
        self._run_world_location_chain_case(
            'boneforge', collision='COMPOUND_MOVING_SPHERE')

    def test_coupled_world_location_chain_compound_support_mixed_spheres_collision(self):
        self._run_world_location_chain_case(
            'boneforge', collision='COMPOUND_MIXED_SPHERES')

    def test_coupled_world_location_chain_compound_support_moving_sphere_set_collision(self):
        self._run_world_location_chain_case(
            'boneforge', collision='COMPOUND_MOVING_SPHERE_SET')

    def test_coupled_world_location_chain_compound_support_moving_sphere_static_set_collision(self):
        self._run_world_location_chain_case(
            'boneforge', collision='COMPOUND_MOVING_SPHERE_STATIC_SET')

    def test_coupled_world_location_chain_compound_support_three_moving_spheres_collision(self):
        self._run_world_location_chain_case(
            'boneforge', collision='COMPOUND_MOVING_SPHERE_TRIPLE')

    def test_coupled_world_location_chain_compound_support_three_moving_spheres_static_set_collision(self):
        self._run_world_location_chain_case(
            'boneforge', collision='COMPOUND_MOVING_SPHERE_TRIPLE_STATIC_SET')

    def test_coupled_world_location_chain_compound_support_rejects_four_moving_spheres(self):
        self._run_world_location_chain_case(
            'boneforge', collision='COMPOUND_MOVING_SPHERE_QUAD')

    def test_coupled_world_location_chain_compound_support_moving_capsule_collision(self):
        self._run_world_location_chain_case(
            'boneforge', collision='COMPOUND_MOVING_CAPSULE')

    def test_coupled_world_location_chain_compound_support_sphere_capsule_collision(self):
        self._run_world_location_chain_case('boneforge', collision='COMPOUND_CAPSULE')

    def test_coupled_world_location_chain_compound_support_sphere_mesh_collision(self):
        self._run_world_location_chain_case('boneforge', collision='COMPOUND_MESH')

    def test_coupled_world_location_chain_compound_support_sphere_capsule_mesh_collision(self):
        self._run_world_location_chain_case(
            'boneforge', collision='COMPOUND_CAPSULE_MESH')

    def test_coupled_world_location_chain_moving_sphere_collision(self):
        self._run_world_location_chain_case('boneforge', collision='MOVING_SPHERE')

    def test_coupled_world_location_chain_continuous_moving_sphere(self):
        self._run_world_location_chain_case(
            'boneforge', collision='MOVING_SPHERE_CONTINUOUS')

    def test_coupled_world_location_chain_static_capsule_collision(self):
        self._run_world_location_chain_case('boneforge', collision='CAPSULE')

    def test_coupled_world_location_chain_moving_capsule_collision(self):
        self._run_world_location_chain_case('boneforge', collision='MOVING_CAPSULE')

    def test_coupled_world_location_chain_zero_strength_is_exact_noop(self):
        self._run_world_location_chain_case('boneforge', collision='MOVING_CAPSULE_ZERO')

    def test_coupled_world_location_chain_resolves_continuous_moving_capsule(self):
        self._run_world_location_chain_case(
            'boneforge', collision='MOVING_CAPSULE_CONTINUOUS')

    def test_coupled_world_location_chain_rejects_scaling_only_capsule(self):
        self._run_world_location_chain_case('boneforge', collision='SCALING_CAPSULE')

    def test_coupled_world_location_chain_static_mesh_collision(self):
        self._run_world_location_chain_case('boneforge', collision='MESH')

    def test_coupled_world_location_chain_static_continuous_mesh_collision(self):
        self._run_world_location_chain_case('boneforge', collision='MESH_CONTINUOUS')

    def test_coupled_world_location_chain_static_exact_swept_volume(self):
        self._run_world_location_chain_case('boneforge', collision='MESH_VOLUME_CONTINUOUS')

    def test_coupled_world_location_chain_moving_deforming_mesh_collision(self):
        self._run_world_location_chain_case(
            'boneforge', collision='MOVING_DEFORMING_MESH_CONTINUOUS')

    def test_coupled_local_rotation_chain_on_rigify_default(self):
        obj, source_action, _, _, _, _ = fixture('rigify_default')
        scene = bpy.context.scene
        state = obj.b4ml
        chain = rotation_chain(obj)
        for index, definition in enumerate(chain):
            animate_rotation_group(state.candidate_action, obj, definition, .45/(index+1))
        for bone in obj.pose.bones:
            if hasattr(bone, 'select'):
                bone.select = False
            else:
                bone.bone.select = False
        for bone, _, _ in chain:
            if hasattr(bone, 'select'):
                bone.select = True
            else:
                bone.bone.select = True
        priority = state.anchors.add()
        priority.frame = 6.
        priority.payload = state.anchors[0].payload
        source = state.candidate_action
        state.secondary_space = 'LOCAL'
        state.secondary_rotation = True
        state.secondary_location = False
        state.secondary_chain = True
        state.secondary_chain_propagation = .7
        report = secondary.solve(obj, scene)
        self.assertEqual(report['backend'], 'implicit_selected_control_chain_v1')
        self.assertEqual(report['chain_links'], 1)
        self.assertTrue(report['priority_poses_preserved'])
        self.assertGreater(report['max_rotation_correction_radians'], .01)
        RECORDS.append(dict(fixture='rigify_default', case='local_rotation_chain', **report))
        object_name = obj.name
        source_name = source_action.name
        w.finish_preview(obj, scene, True)
        path_file = ROOT/'training/b4artists_ml/cache/secondary-chain-kept.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(path_file))
        bpy.ops.wm.open_mainfile(filepath=str(path_file))
        obj = bpy.data.objects[object_name]
        self.assertNotEqual(obj.animation_data.action.name, source_name)
        saved_report = json.loads(obj.animation_data.action['b4ml_secondary_metrics'])
        self.assertTrue(saved_report['chain'])
        self.assertEqual(saved_report['chain_links'], 1)
        w.restore_kept_source(obj, bpy.context.scene)
        self.assertEqual(obj.animation_data.action.name, source_name)

    def test_coupled_local_rotation_chain_transfers_offset_torque(self):
        obj, source_action, _, _, _, _ = fixture('rigify_default')
        scene = bpy.context.scene
        state = obj.b4ml
        chain = rotation_chain(obj)
        for bone in obj.pose.bones:
            if hasattr(bone, 'select'):
                bone.select = False
            else:
                bone.bone.select = False
        for bone, _, _ in chain:
            if hasattr(bone, 'select'):
                bone.select = True
            else:
                bone.bone.select = True
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        if obj.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
        secondary.assign_control_loads(
            obj, (0., 4., 0.), 2., (0.5, 0., 0.), 1.)
        priority = state.anchors.add()
        priority.frame = 6.
        priority.payload = state.anchors[0].payload
        state.secondary_space = 'LOCAL'
        state.secondary_rotation = True
        state.secondary_location = False
        state.secondary_chain = True
        state.secondary_chain_propagation = .7
        source = state.candidate_action
        report = secondary.solve(obj, scene)
        self.assertEqual(report['schema'], 33)
        self.assertEqual(report['backend'],
                         'implicit_selected_control_chain_angular_momentum_v1')
        self.assertEqual(report['chain_mode'], 'LOCAL_ROTATION')
        self.assertEqual(report['chain_links'], 1)
        self.assertEqual(report['torque_controls'], 2)
        self.assertTrue(report['angular_momentum_transfer'])
        self.assertLessEqual(report['angular_momentum_conservation_error'], 1e-10)
        self.assertGreater(report['maximum_internal_angular_impulse'], 0.)
        self.assertGreater(report['max_control_torque'], 0.)
        self.assertGreater(report['max_control_angular_acceleration'], 0.)
        self.assertGreater(report['max_rotation_correction_radians'], 1e-5)
        RECORDS.append(dict(fixture='rigify_default',
                            case='local_rotation_chain_offset_torque', **report))
        secondary.restore(obj, scene)
        self.assertIs(state.candidate_action, source)
        w.finish_preview(obj, scene, False)
        self.assertIs(obj.animation_data.action, source_action)

    def test_cancellation_stale_settings_and_selected_only(self):
        obj, _, _, _, name, path = fixture('boneforge')
        scene = bpy.context.scene
        original = obj.b4ml.candidate_action
        token = flight._curve_token(obj, original)
        actions = set(bpy.data.actions.keys())
        secondary.start(obj, scene)
        self.assertFalse(secondary.step(obj))
        secondary.abort(obj)
        self.assertFalse(obj.b4ml.secondary_running)
        self.assertIs(obj.animation_data.action, original)
        self.assertEqual(flight._curve_token(obj, original), token)
        self.assertEqual(set(bpy.data.actions.keys()), actions)
        secondary.start(obj, scene)
        self.assertFalse(secondary.step(obj))
        obj.b4ml.secondary_frequency += .1
        with self.assertRaisesRegex(ValueError, 'changed'):
            secondary.step(obj)
        self.assertFalse(obj.b4ml.secondary_running)
        self.assertIs(obj.animation_data.action, original)
        self.assertEqual(flight._curve_token(obj, original), token)
        obj.b4ml.secondary_frequency -= .1
        bone = obj.pose.bones[name]
        if hasattr(bone, 'select'):
            bone.select = False
        else:
            bone.bone.select = False
        with self.assertRaisesRegex(ValueError, 'Select one or more'):
            secondary.solve(obj, scene)

    def test_repeated_preview_keep_reload_and_restore_source(self):
        obj, source, source_signature, modes, name, path = fixture('boneforge')
        scene = bpy.context.scene
        original = obj.b4ml.candidate_action
        secondary.solve(obj, scene)
        first = obj.b4ml.candidate_action
        first_name = first.name
        secondary.solve(obj, scene)
        self.assertNotIn(first_name, bpy.data.actions)
        result = obj.b4ml.candidate_action
        source_name = source.name
        w.finish_preview(obj, scene, True)
        self.assertIs(obj.b4ml.kept_action, result)
        self.assertIsNone(obj.b4ml.secondary_input)
        path_file = ROOT/'training/b4artists_ml/cache/secondary-motion-kept.blend'
        name_obj = obj.name
        bpy.ops.wm.save_as_mainfile(filepath=str(path_file))
        bpy.ops.wm.open_mainfile(filepath=str(path_file))
        obj = bpy.data.objects[name_obj]
        bpy.context.view_layer.objects.active = obj
        self.assertIs(obj.animation_data.action, obj.b4ml.kept_action)
        self.assertIn('b4ml_secondary_metrics', obj.b4ml.kept_action)
        w.restore_kept_source(obj, bpy.context.scene)
        self.assertEqual(obj.animation_data.action.name, source_name)

    def test_composes_after_flight_and_restores_in_order(self):
        obj, source, _, _, _, _ = fixture('boneforge')
        scene = bpy.context.scene
        interpolation = obj.b4ml.candidate_action
        support.initialize(obj)
        flight.add(obj, scene)
        flight.solve(obj, scene)
        flight_output = obj.b4ml.candidate_action
        secondary.solve(obj, scene)
        self.assertIs(obj.b4ml.secondary_input, flight_output)
        secondary.restore(obj, scene)
        self.assertIs(obj.b4ml.candidate_action, flight_output)
        flight.restore(obj, scene)
        self.assertIs(obj.b4ml.candidate_action, interpolation)
        w.finish_preview(obj, scene, False)
        self.assertIs(obj.animation_data.action, source)

    def test_world_space_gravity_on_boneforge_and_rigify(self):
        for label in ('boneforge', 'rigify_default'):
            with self.subTest(rig=label):
                obj, _, _, _, name, _ = fixture(label)
                scene = bpy.context.scene
                state = obj.b4ml
                bone = obj.pose.bones[name]
                path = bone.path_from_id('location')
                curves = w.action_curves(state.candidate_action, getattr(obj.animation_data, 'action_slot', None))
                group = [curves.find(path, index=index) for index in range(3)]
                self.assertTrue(all(group))
                for frame in range(1, 12):
                    key = min(group[0].keyframe_points, key=lambda item: abs(float(item.co.x)-frame))
                    key.co.y = .12*math.sin((frame-1)*math.pi/5)
                    key.interpolation = 'LINEAR'
                    group[0].update()
                parent = bone.parent
                self.assertIsNotNone(parent)
                parent_prop, parent_count = secondary._rotation_spec(parent)
                parent_path = parent.path_from_id(parent_prop)
                parent_group = [curves.find(parent_path, index=index) for index in range(parent_count)]
                self.assertTrue(all(parent_group))
                for frame in range(1, 12):
                    angle = .3*math.sin((frame-1)*math.pi/5)
                    if parent.rotation_mode == 'QUATERNION':
                        values = tuple(Quaternion((0, 1, 0), angle))
                    elif parent.rotation_mode == 'AXIS_ANGLE':
                        values = (angle, 0., 1., 0.)
                    else:
                        values = tuple(Euler((0., angle, 0.), parent.rotation_mode))
                    for index, curve in enumerate(parent_group):
                        key = min(curve.keyframe_points, key=lambda item: abs(float(item.co.x)-frame))
                        key.co.y = values[index]
                        key.interpolation = 'LINEAR'
                        curve.update()
                priority = state.anchors.add()
                priority.frame = 6.
                priority.payload = state.anchors[0].payload
                before = curve_values(state.candidate_action, obj, path)
                state.secondary_space = 'WORLD'
                state.secondary_rotation = True
                state.secondary_location = True
                state.secondary_gravity = .75
                report = secondary.solve(obj, scene)
                self.assertEqual(report['backend'], 'implicit_selected_control_secondary_v2')
                self.assertEqual(report['space'], 'WORLD')
                self.assertGreater(report['max_location_correction'], .001)
                self.assertLessEqual(report['max_world_location_error'], 2e-4)
                self.assertLessEqual(report['max_world_rotation_error_radians'], 2e-3)
                RECORDS.append(dict(fixture=label, case='world_gravity', **report))
                after = curve_values(state.candidate_action, obj, path)
                self.assertNotEqual(before, after)
                for axis_before, axis_after in zip(before, after):
                    self.assertEqual(axis_before[1][0][1], axis_after[1][0][1])
                    self.assertEqual(axis_before[1][5][1], axis_after[1][5][1])
                    self.assertEqual(axis_before[1][-1][1], axis_after[1][-1][1])
                secondary.restore(obj, scene)

    def test_world_space_gravity_respects_planar_collision(self):
        obj, _, _, _, name, _ = fixture('boneforge')
        scene = bpy.context.scene
        state = obj.b4ml
        bone = obj.pose.bones[name]
        path = bone.path_from_id('location')
        curves = w.action_curves(state.candidate_action, getattr(obj.animation_data, 'action_slot', None))
        group = [curves.find(path, index=index) for index in range(3)]
        self.assertTrue(all(group))
        priority = state.anchors.add()
        priority.frame = 6.
        priority.payload = state.anchors[0].payload
        heights = []
        for frame in (1., 6., 11.):
            scene.frame_set(int(frame))
            heights.append(float((w.display_world(obj)@obj.pose.bones[name].matrix).translation.z))
        scene.frame_set(6)
        state.support_plane_point = (0., 0., min(heights)-.04)
        state.support_plane_normal = (0., 0., 1.)
        state.secondary_space = 'WORLD'
        state.secondary_rotation = False
        state.secondary_location = True
        state.secondary_frequency = .5
        state.secondary_strength = 1.
        state.secondary_gravity = 4.
        state.secondary_collision = True
        state.secondary_collision_clearance = .01
        state.secondary_restitution = .2
        state.secondary_surface_friction = .4
        report = secondary.solve(obj, scene)
        self.assertTrue(report['collision'])
        self.assertEqual(report['collision_surface'], 'AUTHORED_PLANE')
        self.assertGreater(report['collision_samples'], 0)
        self.assertGreater(report['max_raw_penetration'], 0.)
        self.assertEqual(report['max_penetration_before'], 0.)
        self.assertLessEqual(report['max_penetration_after'], 1e-8)
        self.assertLessEqual(report['max_world_location_error'], 2e-4)
        RECORDS.append(dict(fixture='boneforge', case='world_gravity_collision', **report))
        secondary.restore(obj, scene)

    def test_world_collision_rejects_priority_pose_conflict(self):
        obj, _, _, _, name, _ = fixture('boneforge')
        scene = bpy.context.scene
        state = obj.b4ml
        state.secondary_space = 'WORLD'
        state.secondary_rotation = False
        state.secondary_location = True
        state.secondary_collision = True
        state.secondary_strength = 1.
        matrix = w.display_world(obj)@obj.pose.bones[name].matrix
        state.support_plane_point = matrix.translation+Vector((0., 0., 1.))
        state.support_plane_normal = (0., 0., 1.)
        with self.assertRaisesRegex(ValueError, 'priority pose'):
            secondary.solve(obj, scene)


if __name__ == '__main__':
    filter_name = os.environ.get('B4ML_TEST_FILTER')
    suite = (unittest.defaultTestLoader.loadTestsFromName(
        filter_name, module=sys.modules[__name__])
        if filter_name else
        unittest.defaultTestLoader.loadTestsFromTestCase(SecondaryMotionTests))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print('B4ML_SECONDARY_RECORDS', json.dumps(RECORDS, allow_nan=False))
    print('B4ML_SECONDARY_RESULT:', 'PASS' if result.wasSuccessful() else 'FAIL')
    if not result.wasSuccessful():
        raise SystemExit(1)
