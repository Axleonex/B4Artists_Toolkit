"""In-Bforartists behavioural test: skinning dense meshes (Q1).

A two-bone arm (upper_arm -> forearm) around a finely subdivided tube.
- With the proxy threshold lowered below the tube's size, bone heat runs on a
  decimated copy: the method is AUTO_PROXY, every vertex is weighted, and each
  end of the tube follows its own bone.
- Honest failure: when heat leaves the body unweighted (simulated by a heat
  step that writes nothing), the result is NOT reported as AUTO — the
  segment method takes over and every vertex is weighted.
- Negative control: below the threshold the plain AUTO path runs.
"""
import bmesh
import bpy
from mathutils import Matrix

from boneforge.autorig import skin_gen


class _Validation:
    can_auto_weight = True


def _scene(cuts=40):
    bm = bmesh.new()
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=0.05, radius2=0.05, depth=0.6)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(1.5708, 3, 'Y'), verts=res["verts"])
    bmesh.ops.translate(bm, vec=(0.3, 0, 1.4), verts=res["verts"])
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=cuts // 10, use_grid_fill=True)
    me = bpy.data.meshes.new("BF_DENSE")
    bm.to_mesh(me)
    bm.free()
    mesh = bpy.data.objects.new("BF_DENSE", me)
    bpy.context.scene.collection.objects.link(mesh)
    arm = bpy.data.objects.new("BF_DENSE_RIG", bpy.data.armatures.new("BF_DENSE_RIG"))
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    up = arm.data.edit_bones.new("upper_arm.L")
    up.head, up.tail = (0.0, 0, 1.4), (0.3, 0, 1.4)
    fo = arm.data.edit_bones.new("forearm.L")
    fo.head, fo.tail = (0.3, 0, 1.4), (0.6, 0, 1.4)
    fo.parent, fo.use_connect = up, True
    bpy.ops.object.mode_set(mode='OBJECT')
    return mesh, arm


def _dominant(mesh, i):
    names = {g.index: g.name for g in mesh.vertex_groups}
    groups = mesh.data.vertices[i].groups
    return names[max(groups, key=lambda ge: ge.weight).group] if len(groups) else None


def _ends_follow(mesh):
    V = mesh.data.vertices
    near = min(range(len(V)), key=lambda i: V[i].co.x)
    far = max(range(len(V)), key=lambda i: V[i].co.x)
    return _dominant(mesh, near) == "upper_arm.L" and _dominant(mesh, far) == "forearm.L"


def _cleanup(*obs):
    for ob in obs:
        bpy.data.objects.remove(ob, do_unlink=True)


def run():
    saved = skin_gen._HEAT_PROXY_VERTS, skin_gen._HEAT_PROXY_TARGET
    try:
        # proxy path
        mesh, arm = _scene()
        n = len(mesh.data.vertices)
        skin_gen._HEAT_PROXY_VERTS, skin_gen._HEAT_PROXY_TARGET = n // 2, max(500, n // 4)
        method, warnings = skin_gen.apply_base_weights(bpy.context, mesh, arm, _Validation())
        missing = skin_gen._count_unweighted(mesh)
        assert method == 'AUTO_PROXY', (method, warnings)
        assert missing == 0, ("proxy heat left vertices unweighted", missing, n)
        assert _ends_follow(mesh), "proxy weights: tube ends do not follow their bones"
        assert "BF_DENSE_BFheat" not in bpy.data.objects, "proxy object left behind"
        _cleanup(mesh, arm)

        # honest failure: a heat step that weights nothing is not AUTO
        mesh, arm = _scene()
        skin_gen._HEAT_PROXY_VERTS = 10 ** 9
        real_ops = bpy.ops.object.parent_set

        def failing_parent_set(type='OBJECT', **kw):
            if type == 'ARMATURE_AUTO':
                return real_ops(type='ARMATURE_NAME')      # groups, no weights
            return real_ops(type=type, **kw)
        orig = skin_gen.bpy.ops.object
        class _Ops:
            def __getattr__(self, name):
                return failing_parent_set if name == "parent_set" else getattr(orig, name)
        class _BpyOps:
            object = _Ops()
        real_bpy_ops = skin_gen.bpy.ops
        skin_gen.bpy.ops = _BpyOps()
        try:
            method, warnings = skin_gen.apply_base_weights(bpy.context, mesh, arm, _Validation())
        finally:
            skin_gen.bpy.ops = real_bpy_ops
        assert method == 'SEGMENT', ("failed heat reported as", method, warnings)
        assert any("unweighted" in w for w in warnings), warnings
        assert skin_gen._count_unweighted(mesh) == 0
        assert _ends_follow(mesh)
        _cleanup(mesh, arm)

        # negative control: small mesh -> plain AUTO
        mesh, arm = _scene(cuts=10)
        skin_gen._HEAT_PROXY_VERTS = 10 ** 9
        method, _w = skin_gen.apply_base_weights(bpy.context, mesh, arm, _Validation())
        assert method == 'AUTO', method
        _cleanup(mesh, arm)
    finally:
        skin_gen._HEAT_PROXY_VERTS, skin_gen._HEAT_PROXY_TARGET = saved
    print("dense skinning verified (proxy heat: AUTO_PROXY, %d verts all weighted, ends follow; "
          "failed heat -> SEGMENT with a warning; small mesh -> AUTO)" % n)
    print("ALL DENSE-SKIN TESTS PASS")


if __name__ == "__main__":
    run()
