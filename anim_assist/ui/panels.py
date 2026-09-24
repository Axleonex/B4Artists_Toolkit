"""Sidebar panels for Graph Editor, Dope Sheet, Timeline, and 3D View."""

from __future__ import annotations

import bpy
from bpy.types import Panel


class _GraphEditorMixin:
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "UI"
    bl_category = "Keys"


def _draw_key_manager(layout: bpy.types.UILayout) -> None:
    box = layout.box()
    box.label(text="Batch Interpolation", icon="IPO_BEZIER")
    row = box.row(align=True)
    for itype, label in (("CONSTANT", "Constant"), ("LINEAR", "Linear"), ("BEZIER", "Bezier")):
        op = row.operator("animassist.batch_interpolation", text=label)
        op.interp_type = itype

    box = layout.box()
    box.label(text="Handle Selection", icon="HANDLE_ALIGNED")
    row = box.row(align=True)
    for side, label in (("LEFT", "Left"), ("RIGHT", "Right"), ("BOTH", "Both")):
        op = row.operator("animassist.select_handles", text=label)
        op.side = side

    box = layout.box()
    box.label(text="Key Types", icon="KEYTYPE_KEYFRAME_VEC")
    col = box.column(align=True)
    for kt_id, kt_name in (
        ("KEYFRAME", "Keyframe"),
        ("BREAKDOWN", "Breakdown"),
        ("MOVING_HOLD", "Moving Hold"),
        ("EXTREME", "Extreme"),
        ("JITTER", "Jitter"),
    ):
        row = col.row(align=True)
        row.label(text=kt_name)
        op = row.operator("animassist.set_key_type", text="", icon="KEYTYPE_KEYFRAME_VEC")
        op.key_type = kt_id
        op = row.operator("animassist.select_by_key_type", text="", icon="RESTRICT_SELECT_OFF")
        op.key_type = kt_id
        op.deselect = False
        op = row.operator("animassist.select_by_key_type", text="", icon="RESTRICT_SELECT_ON")
        op.key_type = kt_id
        op.deselect = True
        op = row.operator("animassist.delete_by_key_type", text="", icon="TRASH")
        op.key_type = kt_id

    box = layout.box()
    box.label(text="Set Handle Type", icon="HANDLE_AUTO")
    row = box.row(align=True)
    for ht, label in (
        ("AUTO_CLAMPED", "Clamp"),
        ("AUTO", "Auto"),
        ("VECTOR", "Vec"),
        ("ALIGNED", "Align"),
        ("FREE", "Free"),
    ):
        op = row.operator("animassist.set_handle_type", text=label)
        op.handle_type = ht

    box = layout.box()
    box.label(text="Key Operations", icon="NLA_PUSHDOWN")
    box.operator("animassist.insert_frames", text="Insert Frames…")
    box.operator("animassist.move_keys", text="Move Keys…")


class ANIMASSIST_PT_curve_tools(_GraphEditorMixin, Panel):
    bl_idname = "ANIMASSIST_PT_curve_tools"
    bl_label = "Curve Tools"
    bl_order = 30

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        settings = context.scene.anim_assist

        # A plain checkbox: the old triangle + "Curve Tools" label repeated the
        # panel title and looked like a collapse control.
        layout.prop(settings, "panel_compact", text="Compact buttons")

        if settings.panel_compact:
            col = layout.column(align=True)
            col.operator("animassist.blend_neighbor", text="Blend to Neighbor")
            col.operator("animassist.blend_frame", text="Blend Frame")
            col.operator("animassist.blend_offset", text="Blend Offset")
            col.operator("animassist.push_pull", text="Push / Pull")
            col.operator("animassist.ease_to_ease", text="Ease To Ease")
            col.operator("animassist.smooth_keys", text="Smooth Keys")


class ANIMASSIST_PT_blend_neighbor(_GraphEditorMixin, Panel):
    bl_idname = "ANIMASSIST_PT_blend_neighbor"
    bl_label = "Blend to Neighbor"
    bl_parent_id = "ANIMASSIST_PT_curve_tools"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return not context.scene.anim_assist.panel_compact

    def draw(self, context: bpy.types.Context) -> None:
        self.layout.operator(
            "animassist.blend_neighbor",
            text="Blend to Neighbor",
            icon="TRACKING_FORWARDS_SINGLE",
        )


class ANIMASSIST_PT_blend_frame(_GraphEditorMixin, Panel):
    bl_idname = "ANIMASSIST_PT_blend_frame"
    bl_label = "Blend Frame"
    bl_parent_id = "ANIMASSIST_PT_curve_tools"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return not context.scene.anim_assist.panel_compact

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        s = context.scene.anim_assist

        row = layout.row(align=True)
        row.prop(s, "reference_frame", text="Ref")
        row.operator("animassist.set_reference_frame", text="", icon="EYEDROPPER")
        layout.operator("animassist.blend_frame", text="Blend Frame", icon="IPO_BEZIER")


class ANIMASSIST_PT_bookmarks(_GraphEditorMixin, Panel):
    bl_idname = "ANIMASSIST_PT_bookmarks"
    bl_label = "Frame Bookmarks"
    bl_parent_id = "ANIMASSIST_PT_blend_frame"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        s = context.scene.anim_assist

        for i, bm in enumerate(s.bookmarks):
            row = layout.row(align=True)
            icon = "BOOKMARKS" if i == s.active_bookmark_index else "DOT"
            op = row.operator("animassist.recall_bookmark", text=f"{bm.name} (F{bm.frame})", icon=icon)
            op.index = i

        row = layout.row(align=True)
        row.operator("animassist.add_bookmark", text="Add", icon="ADD")
        row.operator("animassist.remove_bookmark", text="Remove", icon="REMOVE")


class ANIMASSIST_PT_blend_offset(_GraphEditorMixin, Panel):
    bl_idname = "ANIMASSIST_PT_blend_offset"
    bl_label = "Blend Offset"
    bl_parent_id = "ANIMASSIST_PT_curve_tools"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return not context.scene.anim_assist.panel_compact

    def draw(self, context: bpy.types.Context) -> None:
        self.layout.operator("animassist.blend_offset", text="Blend Offset", icon="ARROW_LEFTRIGHT")


class ANIMASSIST_PT_push_pull(_GraphEditorMixin, Panel):
    bl_idname = "ANIMASSIST_PT_push_pull"
    bl_label = "Push / Pull"
    bl_parent_id = "ANIMASSIST_PT_curve_tools"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return not context.scene.anim_assist.panel_compact

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        s = context.scene.anim_assist

        row = layout.row(align=True)
        row.prop(s, "reference_frame", text="Ref")
        row.operator("animassist.set_reference_frame", text="", icon="EYEDROPPER")
        layout.operator("animassist.push_pull", text="Push / Pull", icon="FULLSCREEN_EXIT")


class ANIMASSIST_PT_ease_to_ease(_GraphEditorMixin, Panel):
    bl_idname = "ANIMASSIST_PT_ease_to_ease"
    bl_label = "Ease To Ease"
    bl_parent_id = "ANIMASSIST_PT_curve_tools"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return not context.scene.anim_assist.panel_compact

    def draw(self, context: bpy.types.Context) -> None:
        self.layout.operator("animassist.ease_to_ease", text="Ease To Ease", icon="IPO_EASE_IN_OUT")


class ANIMASSIST_PT_smooth_keys(_GraphEditorMixin, Panel):
    bl_idname = "ANIMASSIST_PT_smooth_keys"
    bl_label = "Smooth Keys"
    bl_parent_id = "ANIMASSIST_PT_curve_tools"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return not context.scene.anim_assist.panel_compact

    def draw(self, context: bpy.types.Context) -> None:
        self.layout.operator("animassist.smooth_keys", text="Smooth Keys", icon="SMOOTHCURVE")


class ANIMASSIST_PT_anim_offset(_GraphEditorMixin, Panel):
    bl_idname = "ANIMASSIST_PT_anim_offset"
    bl_label = "Anim Offset"
    bl_category = "Motion"
    bl_order = 10

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        s = context.scene.anim_assist
        m = s.mask
        active = s.anim_offset_active

        layout.operator(
            "animassist.anim_offset",
            text="Deactivate" if active else "Activate",
            icon="PAUSE" if active else "PLAY",
            depress=active,
        )

        box = layout.box()
        box.label(text="Mask", icon="MOD_MASK")
        box.prop(m, "enabled", text="Use Mask")
        row = box.row(align=True)
        row.prop(m, "start_frame", text="Start")
        row.prop(m, "end_frame", text="End")
        col = box.column(align=True)
        col.prop(m, "blend_left", text="Blend In")
        col.prop(m, "blend_right", text="Blend Out")
        box.operator("animassist.anim_offset_range_from_scene", text="Range from Scene", icon="SCENE_DATA")


class ANIMASSIST_PT_key_manager(_GraphEditorMixin, Panel):
    bl_idname = "ANIMASSIST_PT_key_manager"
    bl_label = "Key Manager"
    bl_order = 60

    def draw(self, context: bpy.types.Context) -> None:
        _draw_key_manager(self.layout)


class ANIMASSIST_PT_anim_offset_dope(Panel):
    bl_idname = "ANIMASSIST_PT_anim_offset_dope"
    bl_label = "Anim Offset"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"
    bl_category = "Motion"
    bl_order = 10

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return getattr(context.space_data, "mode", "") != "TIMELINE"

    def draw(self, context: bpy.types.Context) -> None:
        ANIMASSIST_PT_anim_offset.draw(self, context)


class ANIMASSIST_PT_key_manager_dope(Panel):
    bl_idname = "ANIMASSIST_PT_key_manager_dope"
    bl_label = "Key Manager"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"
    bl_category = "Keys"
    bl_order = 60

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return getattr(context.space_data, "mode", "") != "TIMELINE"

    def draw(self, context: bpy.types.Context) -> None:
        _draw_key_manager(self.layout)


class ANIMASSIST_PT_key_manager_timeline(Panel):
    bl_idname = "ANIMASSIST_PT_key_manager_timeline"
    bl_label = "Key Manager"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"
    bl_category = "Keys"
    bl_order = 60

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return getattr(context.space_data, "mode", "") == "TIMELINE"

    def draw(self, context: bpy.types.Context) -> None:
        _draw_key_manager(self.layout)


class ANIMASSIST_PT_anim_offset_3d(Panel):
    bl_idname = "ANIMASSIST_PT_anim_offset_3d"
    bl_label = "Anim Offset"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Motion"
    bl_order = 10

    def draw(self, context: bpy.types.Context) -> None:
        ANIMASSIST_PT_anim_offset.draw(self, context)


classes: list[type] = [
    ANIMASSIST_PT_curve_tools,
    ANIMASSIST_PT_blend_neighbor,
    ANIMASSIST_PT_blend_frame,
    ANIMASSIST_PT_bookmarks,
    ANIMASSIST_PT_blend_offset,
    ANIMASSIST_PT_push_pull,
    ANIMASSIST_PT_ease_to_ease,
    ANIMASSIST_PT_smooth_keys,
    ANIMASSIST_PT_anim_offset,
    ANIMASSIST_PT_key_manager,
    ANIMASSIST_PT_anim_offset_dope,
    ANIMASSIST_PT_key_manager_dope,
    ANIMASSIST_PT_key_manager_timeline,
    ANIMASSIST_PT_anim_offset_3d,
]