"""In-Bforartists test: Fit Dropped Rig.

* no mesh picked -> CANCELLED, rig and marker untouched (Review Focus 5);
* picked mesh deleted -> CANCELLED;
* mesh picked, fit + auto-weight on -> rig sized/placed on the mesh,
  mesh parented with an Armature modifier, marker removed.
"""
import bpy

import boneforge


def _refused(message="Pick the mesh to fit the rig to", **options):
    """True when Fit Dropped Rig refuses (background mode raises on ERROR reports)."""
    try:
        return bpy.ops.boneforge.fit_dropped_rig(**options) == {'CANCELLED'}
    except RuntimeError as exc:
        return message in str(exc)


def run():
    boneforge.register()
    from boneforge.autorig import quick_human as qh     # after register: modules may be reloaded
    try:
        ctx = bpy.context
        scene = ctx.scene
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(2.0, 0.0, 0.5))
        mesh = ctx.active_object
        arm = qh._build_fallback_skeleton(ctx)
        arm[qh.DROPPED_RIG_PROP] = "fallback"
        start_scale = tuple(arm.scale)

        scene.boneforge_drop_target_mesh = None
        ctx.view_layer.objects.active = arm
        assert _refused()
        assert qh.DROPPED_RIG_PROP in arm and tuple(arm.scale) == start_scale

        bpy.ops.mesh.primitive_plane_add()
        gone = ctx.active_object
        scene.boneforge_drop_target_mesh = gone
        bpy.data.objects.remove(gone)
        ctx.view_layer.objects.active = arm
        assert _refused()
        assert qh.DROPPED_RIG_PROP in arm

        # its options are the operator's own (tuned after the click in Adjust Last Operation)
        scene.boneforge_drop_target_mesh = mesh
        ctx.view_layer.objects.active = arm
        assert _refused("Turn on Fit Rig to Mesh or Auto-Weight", fit_to_mesh=False, auto_weight=False), \
            "both options off must refuse"
        assert qh.DROPPED_RIG_PROP in arm and tuple(arm.scale) == start_scale

        ctx.view_layer.objects.active = arm
        assert bpy.ops.boneforge.fit_dropped_rig(fit_to_mesh=True, auto_weight=True) == {'FINISHED'}
        assert abs(arm.location.x - 2.0) < 1e-3 and abs(arm.location.z) < 1e-3, tuple(arm.location)
        assert 0.6 < arm.dimensions.z < 1.2, arm.dimensions.z
        assert mesh.parent == arm, mesh.parent
        assert any(m.type == 'ARMATURE' and m.object == arm for m in mesh.modifiers)
        bone_names = {b.name for b in arm.data.bones}
        weighted = {mesh.vertex_groups[g.group].name
                    for v in mesh.data.vertices for g in v.groups if g.weight > 0.0}
        assert weighted & bone_names, ("automatic weights were not assigned", sorted(weighted)[:5])
        assert qh.DROPPED_RIG_PROP not in arm, "marker must be cleared after fitting"
        # still adjustable afterwards: Adjust Last Operation re-runs it on the restored rig
        assert bpy.ops.boneforge.fit_dropped_rig.poll(), "the finished fit must stay adjustable"
        # but run fresh on a rig that was not dropped in, it refuses and leaves the rig alone
        fitted = tuple(arm.location)
        assert _refused("BoneCraft Rigs shelf", fit_to_mesh=True, auto_weight=False)
        assert tuple(arm.location) == fitted
    finally:
        boneforge.unregister()
    print("PASS fit dropped rig: errors leave rig untouched; fit + auto-weight works")
