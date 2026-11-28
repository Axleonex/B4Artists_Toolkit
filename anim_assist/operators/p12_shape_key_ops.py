# --- LIPSYNC SHAPE KEY OPERATORS (Phase 12 / v12.0.0) ---
"""Shape key wiring operators - parallel to the bone wiring operators.

- AA_OT_p12_autofill_shape_key_wiring: heuristic match of viseme names to shape keys
  on the active mesh.
- AA_OT_p12_capture_viseme_shape: snapshot the current shape-key state as the
  named viseme (overrides built-in).
- AA_OT_p12_pick_mesh: set link.mesh_name from the active mesh in the viewport.
"""

from __future__ import annotations

from ..i18n import T, F

import bpy
from bpy.props import StringProperty
from bpy.types import Operator

from ..core import p12_properties as p12_props
from ..core import p12_shape_key_wiring as skw
from ..core.logging import get_logger

_log = get_logger(__name__)


# ---------------------------------------------------------------------------
# Autofill shape key wiring
# ---------------------------------------------------------------------------

class AA_OT_p12_autofill_shape_key_wiring(Operator):
    """Auto-fill the shape_key_wiring rows by name-matching viseme names to shape keys."""

    bl_idname = "animassist.p12_autofill_shape_key_wiring"
    bl_label = "Autofill Shape Key Wiring"
    bl_options = {"REGISTER", "UNDO"}

    library_id: StringProperty(  # type: ignore[valid-type]
        name="Library",
        default="CARTOON_5",
     translation_context='AnimAssist')

    @classmethod
    def poll(cls, context):
        return p12_props.get_p12(context) is not None

    def execute(self, context):
        p12 = p12_props.get_p12(context)
        link = None
        if p12.layer_links and 0 <= p12.active_link_index < len(p12.layer_links):
            link = p12.layer_links[p12.active_link_index]

        # Prefer link.mesh_name; fall back to active mesh in viewport.
        mesh_obj = None
        if link is not None and link.mesh_name:
            mesh_obj = bpy.data.objects.get(link.mesh_name)
        if mesh_obj is None and context.active_object is not None and context.active_object.type == "MESH":
            mesh_obj = context.active_object
        if mesh_obj is None:
            self.report({"ERROR"}, T('No mesh selected and no link.mesh_name set'))
            return {"CANCELLED"}

        added = skw.autofill_shape_key_wiring(p12, mesh_obj, self.library_id)
        if added == 0:
            self.report({"INFO"}, F('All {p0} visemes already wired', p0=self.library_id))
        else:
            missing = skw.missing_shape_keys(p12, mesh_obj)
            msg = F('Autofilled {p0} row(s)', p0=str(added))
            if missing:
                msg = F('{p0} - {p1} viseme(s) need a shape key: {p2}',
                        p0=msg, p1=str(len(missing)), p2=', '.join(missing[:5]))
            self.report({"INFO"}, msg)
        return {"FINISHED"}


# ---------------------------------------------------------------------------
# Pick mesh from viewport
# ---------------------------------------------------------------------------

class AA_OT_p12_pick_mesh(Operator):
    """Set the active lipsync link's mesh_name from the currently selected mesh."""

    bl_idname = "animassist.p12_pick_mesh"
    bl_label = "Use Active Mesh"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if p12_props.get_p12(context) is None:
            return False
        return context.active_object is not None and context.active_object.type == "MESH"

    def execute(self, context):
        p12 = p12_props.get_p12(context)
        if not p12.layer_links or p12.active_link_index < 0 or p12.active_link_index >= len(p12.layer_links):
            self.report({"ERROR"}, T('No lipsync layer link selected. Select one in the Lipsync panel list first'))
            return {"CANCELLED"}
        link = p12.layer_links[p12.active_link_index]
        link.mesh_name = context.active_object.name
        sk = context.active_object.data.shape_keys
        if sk is None:
            self.report({"WARNING"}, F("Mesh '{p0}' has no shape keys", p0=link.mesh_name))
        else:
            count = len([kb for kb in sk.key_blocks if kb.name != "Basis"])
            self.report({"INFO"}, F("Mesh set to '{p0}' ({p1} shape keys)", p0=link.mesh_name, p1=str(count)))
        return {"FINISHED"}


# ---------------------------------------------------------------------------
# Capture current shape key state as a viseme
# ---------------------------------------------------------------------------

class AA_OT_p12_capture_viseme_shape(Operator):
    """Capture the current shape key values as the named viseme.

    For shape-key-driven faces, this is how you teach the rig what each
    viseme looks like on this character. Pose the face with shape key
    sliders, run this op, name the viseme.
    """

    bl_idname = "animassist.p12_capture_viseme_shape"
    bl_label = "Capture Viseme (Shape Keys)"
    bl_options = {"REGISTER", "UNDO"}

    viseme_name: StringProperty(  # type: ignore[valid-type]
        name="Viseme",
        default="A",
     translation_context='AnimAssist')

    @classmethod
    def poll(cls, context):
        if p12_props.get_p12(context) is None:
            return False
        return context.active_object is not None and context.active_object.type == "MESH"

    def execute(self, context):
        # For shape keys the "capture" is implicit - the wiring already maps
        # viseme -> shape_key, and the bake writes 1.0 to that key at the
        # cue frame. So this op's job is simply: confirm the shape_key for
        # this viseme is wired, and report which key it is.
        p12 = p12_props.get_p12(context)
        for entry in p12.shape_key_wiring:
            if entry.viseme_name == self.viseme_name:
                if entry.shape_key_name:
                    self.report(
                        {"INFO"},
                        F("Viseme '{p0}' wired to shape key '{p1}'", p0=self.viseme_name, p1=entry.shape_key_name),
                    )
                else:
                    self.report(
                        {"WARNING"},
                        F("Viseme '{p0}' has no shape key wired - fill in the wiring row", p0=self.viseme_name),
                    )
                return {"FINISHED"}
        # Not yet in wiring - add it.
        entry = p12.shape_key_wiring.add()
        entry.viseme_name = self.viseme_name
        entry.shape_key_name = ""
        self.report(
            {"INFO"},
            F("Added wiring row for viseme '{p0}' - fill in the shape key name", p0=self.viseme_name),
        )
        return {"FINISHED"}


CLASSES: tuple[type, ...] = (
    AA_OT_p12_autofill_shape_key_wiring,
    AA_OT_p12_pick_mesh,
    AA_OT_p12_capture_viseme_shape,
)
