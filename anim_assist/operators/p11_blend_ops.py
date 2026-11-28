# --- ANIMATION LAYER BLENDING & MERGING OPERATORS ---
"""Operators for blending between layers, merging layers, flattening
the stack, and layer preset management.
"""

from __future__ import annotations

from ..i18n import T, F

import bpy
from bpy.props import EnumProperty, FloatProperty, IntProperty, StringProperty

from ..core.logging import get_logger
from ..core.p11_properties import get_p11
from ..core import p11_layer_engine as engine
from ..core import p11_blend_math as bm

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Poll helpers
# ---------------------------------------------------------------------------

def _p11_poll(context: bpy.types.Context) -> bool:
    return get_p11(context) is not None


def _has_multiple_layers(context: bpy.types.Context) -> bool:
    p11 = get_p11(context)
    return p11 is not None and len(p11.layers) > 1


def _active_layer_valid(context: bpy.types.Context) -> bool:
    p11 = get_p11(context)
    if p11 is None:
        return False
    return 0 <= p11.active_layer_index < len(p11.layers)


# ---------------------------------------------------------------------------
# Merge Layer Down
# ---------------------------------------------------------------------------

class ANIMASSIST_OT_p11_merge_down(bpy.types.Operator):
    """Merge the active layer into the one below it"""

    bl_idname = "animassist.p11_merge_down"
    bl_label = "Merge Down"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        p11 = get_p11(context)
        if p11 is None:
            return False
        idx = p11.active_layer_index
        if idx <= 0 or idx >= len(p11.layers):
            return False
        layer = p11.layers[idx]
        return not layer.is_base_layer and not layer.protected

    def execute(self, context: bpy.types.Context) -> set[str]:
        p11 = get_p11(context)
        idx = p11.active_layer_index
        name = p11.layers[idx].name
        obj = context.active_object

        if engine.merge_layer_down(p11, idx, obj):
            self.report({'INFO'}, F("Merged '{p0}' into layer below", p0=f'{name}'))
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, T('Merge failed'))
            return {'CANCELLED'}


# ---------------------------------------------------------------------------
# Flatten All
# ---------------------------------------------------------------------------

class ANIMASSIST_OT_p11_flatten_all(bpy.types.Operator):
    """Flatten all layers into the base layer (destructive)"""

    bl_idname = "animassist.p11_flatten_all"
    bl_label = "Flatten All Layers"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return _has_multiple_layers(context)

    def invoke(self, context: bpy.types.Context, event) -> set[str]:
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context: bpy.types.Context) -> set[str]:
        p11 = get_p11(context)
        obj = context.active_object
        count = len(p11.layers)

        if engine.flatten_all(p11, obj):
            self.report({'INFO'}, F('Flattened {p0} layers into base', p0=f'{count}'))
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, T('Flatten failed'))
            return {'CANCELLED'}


# ---------------------------------------------------------------------------
# Interactive Blend Between Layers (Modal)
# ---------------------------------------------------------------------------

class ANIMASSIST_OT_p11_blend_layers(bpy.types.Operator):
    """Interactively blend between two layers with a drag slider"""

    bl_idname = "animassist.p11_blend_layers"
    bl_label = "Blend Between Layers"
    bl_options = {'REGISTER', 'UNDO'}

    source_index: IntProperty(  # type: ignore[valid-type]
        name="Source Layer",
        default=0, min=0,
     translation_context='AnimAssist')

    target_index: IntProperty(  # type: ignore[valid-type]
        name="Target Layer",
        default=1, min=0,
     translation_context='AnimAssist')

    factor: FloatProperty(  # type: ignore[valid-type]
        name="Blend Factor",
        description="0.0 = fully source, 1.0 = fully target",
        default=0.5, min=0.0, max=1.0,
        subtype="FACTOR",
     translation_context='AnimAssist')

    # Internal state for modal.
    _initial_mouse_x: int = 0
    _initial_factor: float = 0.5
    _bone_snapshots: dict = {}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        p11 = get_p11(context)
        if p11 is None or len(p11.layers) < 2:
            return False
        obj = context.active_object
        return obj is not None and obj.type == "ARMATURE" and context.mode == "POSE"

    def invoke(self, context: bpy.types.Context, event) -> set[str]:
        p11 = get_p11(context)
        self.source_index = p11.blend_source_index
        self.target_index = p11.blend_target_index
        self._initial_mouse_x = event.mouse_x
        self._initial_factor = self.factor

        # Snapshot both layers for all bones.
        obj = context.active_object
        frame = context.scene.frame_current
        self._bone_snapshots = {}

        src_action = engine.get_layer_action(p11.layers[self.source_index])
        tgt_action = engine.get_layer_action(p11.layers[self.target_index])

        for bone in obj.pose.bones:
            src_snap = engine.read_bone_from_action(src_action, bone.name, frame, rotation_mode=bone.rotation_mode)
            tgt_snap = engine.read_bone_from_action(tgt_action, bone.name, frame, rotation_mode=bone.rotation_mode)
            self._bone_snapshots[bone.name] = (src_snap, tgt_snap)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context: bpy.types.Context, event) -> set[str]:
        if event.type == 'MOUSEMOVE':
            # Map horizontal mouse delta to blend factor (0..1).
            # 200 px of drag covers the full 0→1 range — feels natural
            # on both standard and high-DPI displays.
            mouse_pixels_for_full_range = 200
            delta = (event.mouse_x - self._initial_mouse_x) / mouse_pixels_for_full_range
            self.factor = max(0.0, min(1.0, self._initial_factor + delta))
            self._apply_blend(context)
            context.area.header_text_set(
                F('Blend: {p0}  (Move mouse, LMB to confirm, RMB/Esc to cancel)', p0=f'{self.factor:.1%}')
            )
            return {'RUNNING_MODAL'}

        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            context.area.header_text_set(None)
            p11 = get_p11(context)
            p11.blend_factor = self.factor
            self.report({'INFO'}, F('Blend applied at {p0}', p0=f'{self.factor:.1%}'))
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.area.header_text_set(None)
            # Restore original values.
            self.factor = 0.0
            self._apply_blend(context)
            self.report({'INFO'}, T('Blend cancelled'))
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def _apply_blend(self, context: bpy.types.Context) -> None:
        obj = context.active_object
        for bone in obj.pose.bones:
            snaps = self._bone_snapshots.get(bone.name)
            if snaps is None:
                continue
            src_snap, tgt_snap = snaps

            result = bm.interpolate_layers(
                source_loc=src_snap.location,
                source_rot=src_snap.rotation,
                source_sca=src_snap.scale,
                target_loc=tgt_snap.location,
                target_rot=tgt_snap.rotation,
                target_sca=tgt_snap.scale,
                factor=self.factor,
            )

            bone.location = result.location
            bone.rotation_euler = result.rotation
            bone.scale = result.scale


# ---------------------------------------------------------------------------
# Set Blend Factor (non-modal, for UI slider)
# ---------------------------------------------------------------------------

class ANIMASSIST_OT_p11_set_blend_factor(bpy.types.Operator):
    """Apply a specific blend factor between source and target layers"""

    bl_idname = "animassist.p11_set_blend_factor"
    bl_label = "Set Blend Factor"
    bl_options = {'REGISTER', 'UNDO'}

    factor: FloatProperty(  # type: ignore[valid-type]
        name="Factor",
        description="Blend amount between the source and target animation layers",
        default=0.5, min=0.0, max=1.0,
        subtype="FACTOR",
     translation_context='AnimAssist')

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        p11 = get_p11(context)
        if p11 is None or len(p11.layers) < 2:
            return False
        obj = context.active_object
        return obj is not None and obj.type == "ARMATURE"

    def execute(self, context: bpy.types.Context) -> set[str]:
        p11 = get_p11(context)
        obj = context.active_object
        frame = context.scene.frame_current

        src_idx = p11.blend_source_index
        tgt_idx = p11.blend_target_index

        if src_idx >= len(p11.layers) or tgt_idx >= len(p11.layers):
            self.report({'WARNING'}, T('Invalid source/target layer indices'))
            return {'CANCELLED'}

        src_action = engine.get_layer_action(p11.layers[src_idx])
        tgt_action = engine.get_layer_action(p11.layers[tgt_idx])

        updated = 0
        for bone in obj.pose.bones:
            src_snap = engine.read_bone_from_action(src_action, bone.name, frame, rotation_mode=bone.rotation_mode)
            tgt_snap = engine.read_bone_from_action(tgt_action, bone.name, frame, rotation_mode=bone.rotation_mode)

            result = bm.interpolate_layers(
                source_loc=src_snap.location,
                source_rot=src_snap.rotation,
                source_sca=src_snap.scale,
                target_loc=tgt_snap.location,
                target_rot=tgt_snap.rotation,
                target_sca=tgt_snap.scale,
                factor=self.factor,
            )

            bone.location = result.location
            bone.rotation_euler = result.rotation
            bone.scale = result.scale
            updated += 1

        p11.blend_factor = self.factor
        self.report({'INFO'}, F('Blend factor {p0} applied to {p1} bones', p0=f'{self.factor:.1%}', p1=f'{updated}'))
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Save / Load Preset
# ---------------------------------------------------------------------------

class ANIMASSIST_OT_p11_save_preset(bpy.types.Operator):
    """Save the current layer stack as a preset"""

    bl_idname = "animassist.p11_save_preset"
    bl_label = "Save Layer Preset"
    bl_options = {'REGISTER', 'UNDO'}

    preset_name: StringProperty(  # type: ignore[valid-type]
        name="Preset Name",
        default="My Preset",
     translation_context='AnimAssist')

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return _p11_poll(context)

    def invoke(self, context: bpy.types.Context, event) -> set[str]:
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context: bpy.types.Context) -> set[str]:
        p11 = get_p11(context)
        json_str = engine.serialize_layer_stack(p11)

        preset = p11.user_presets.add()
        preset.name = self.preset_name
        preset.preset_json = json_str

        self.report({'INFO'}, F("Saved preset '{p0}'", p0=f'{self.preset_name}'))
        return {'FINISHED'}


class ANIMASSIST_OT_p11_load_preset(bpy.types.Operator):
    """Load a saved layer stack preset"""

    bl_idname = "animassist.p11_load_preset"
    bl_label = "Load Layer Preset"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        p11 = get_p11(context)
        return (
            p11 is not None
            and len(p11.user_presets) > 0
            and 0 <= p11.user_presets_index < len(p11.user_presets)
        )

    def invoke(self, context: bpy.types.Context, event) -> set[str]:
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context: bpy.types.Context) -> set[str]:
        p11 = get_p11(context)
        preset = p11.user_presets[p11.user_presets_index]

        if engine.deserialize_layer_stack(p11, preset.preset_json):
            self.report({'INFO'}, F("Loaded preset '{p0}'", p0=f'{preset.name}'))
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, T('Could not load the preset. Pick a preset from the list or save a new one'))
            return {'CANCELLED'}


class ANIMASSIST_OT_p11_remove_preset(bpy.types.Operator):
    """Remove a saved layer preset"""

    bl_idname = "animassist.p11_remove_preset"
    bl_label = "Remove Preset"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        p11 = get_p11(context)
        return (
            p11 is not None
            and len(p11.user_presets) > 0
            and 0 <= p11.user_presets_index < len(p11.user_presets)
        )

    def execute(self, context: bpy.types.Context) -> set[str]:
        p11 = get_p11(context)
        idx = p11.user_presets_index
        name = p11.user_presets[idx].name
        p11.user_presets.remove(idx)
        if p11.user_presets_index >= len(p11.user_presets):
            p11.user_presets_index = max(0, len(p11.user_presets) - 1)
        self.report({'INFO'}, F("Removed preset '{p0}'", p0=f'{name}'))
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Set Layer Weight (for quick slider access)
# ---------------------------------------------------------------------------

class ANIMASSIST_OT_p11_set_weight(bpy.types.Operator):
    """Set the weight of the active layer"""

    bl_idname = "animassist.p11_set_weight"
    bl_label = "Set Layer Weight"
    bl_options = {'REGISTER', 'UNDO'}

    weight: FloatProperty(  # type: ignore[valid-type]
        name="Weight",
        description="Influence of the active animation layer",
        default=1.0, min=0.0, max=1.0,
        subtype="FACTOR",
     translation_context='AnimAssist')

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return _active_layer_valid(context)

    def execute(self, context: bpy.types.Context) -> set[str]:
        p11 = get_p11(context)
        layer = p11.layers[p11.active_layer_index]
        layer.weight = self.weight
        p11.eval_generation += 1
        self.report({'INFO'}, F("'{p0}' weight: {p1}", p0=f'{layer.name}', p1=f'{self.weight:.0%}'))
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Set Blend Mode
# ---------------------------------------------------------------------------

class ANIMASSIST_OT_p11_set_blend_mode(bpy.types.Operator):
    """Set the blend mode of the active layer"""

    bl_idname = "animassist.p11_set_blend_mode"
    bl_label = "Set Blend Mode"
    bl_options = {'REGISTER', 'UNDO'}

    mode: EnumProperty(  # type: ignore[valid-type]
        name="Mode",
        description="How the active animation layer combines with layers below it",
        items=[
            ("OVERRIDE", "Override", ""),
            ("ADDITIVE", "Additive", ""),
            ("MULTIPLY", "Multiply", ""),
            ("COMBINE", "Combine", ""),
        ],
        default="OVERRIDE",
     translation_context='AnimAssist')

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        p11 = get_p11(context)
        if not _active_layer_valid(context):
            return False
        return not p11.layers[p11.active_layer_index].is_base_layer

    def execute(self, context: bpy.types.Context) -> set[str]:
        p11 = get_p11(context)
        layer = p11.layers[p11.active_layer_index]
        layer.blend_mode = self.mode
        p11.eval_generation += 1
        self.report({'INFO'}, F("'{p0}' mode: {p1}", p0=f'{layer.name}', p1=f'{self.mode}'))
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Class collection
# ---------------------------------------------------------------------------

CLASSES: tuple[type, ...] = (
    ANIMASSIST_OT_p11_merge_down,
    ANIMASSIST_OT_p11_flatten_all,
    ANIMASSIST_OT_p11_blend_layers,
    ANIMASSIST_OT_p11_set_blend_factor,
    ANIMASSIST_OT_p11_save_preset,
    ANIMASSIST_OT_p11_load_preset,
    ANIMASSIST_OT_p11_remove_preset,
    ANIMASSIST_OT_p11_set_weight,
    ANIMASSIST_OT_p11_set_blend_mode,
)
