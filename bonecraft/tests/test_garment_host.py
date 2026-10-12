"""In-Bforartists behavioural test: garments bend with the joint they cover.

An arm (upper_arm -> forearm, parented under a torso bone) with a body skin,
a separate sleeve island over the elbow, a small button island on the upper
arm and a yoke island over the shoulder. After segment weights and the
island pass with ``base_method='SEGMENT'``:
- the sleeve keeps weights on exactly the elbow's two bones (not rigid), and
  its two ends follow their own bones;
- the button is pinned rigid to one bone;
- the yoke over the shoulder (a limb root) is pinned rigid, as artists
  weight clothing there to the torso side;
- negative control: without ``base_method`` the sleeve is pinned rigid (the
  old behaviour).
"""
import bmesh
import bpy
from mathutils import Matrix, Vector

from boneforge.autorig import skin_gen


def _cyl(bm, x0, x1, r, segs=16, rings=12):
    res = bmesh.ops.create_cone(bm, cap_ends=False, segments=segs, radius1=r, radius2=r,
                                depth=x1 - x0)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(1.5708, 3, 'Y'), verts=res["verts"])
    bmesh.ops.translate(bm, vec=((x0 + x1) / 2, 0, 1.4), verts=res["verts"])
    edges = [e for e in bm.edges if all(v in res["verts"] for v in e.verts)
             and abs(e.verts[0].co.x - e.verts[1].co.x) > 1e-6]
    bmesh.ops.subdivide_edges(bm, edges=edges, cuts=rings, use_grid_fill=False)


def _scene():
    bm = bmesh.new()
    _cyl(bm, 0.0, 0.62, 0.04)                  # body skin: shoulder to wrist
    _cyl(bm, 0.22, 0.42, 0.05)                 # sleeve over the elbow (x=0.32)
    r = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.008)
    bmesh.ops.translate(bm, vec=(0.15, 0, 1.445), verts=r["verts"])   # button
    _cyl(bm, -0.06, 0.06, 0.055)               # yoke over the shoulder (x=0)
    me = bpy.data.meshes.new("BF_GARMENT")
    bm.to_mesh(me)
    bm.free()
    mesh = bpy.data.objects.new("BF_GARMENT", me)
    bpy.context.scene.collection.objects.link(mesh)
    arm = bpy.data.objects.new("BF_GARMENT_RIG", bpy.data.armatures.new("BF_GARMENT_RIG"))
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    ebs = arm.data.edit_bones
    chest = ebs.new("spine.chest"); chest.head, chest.tail = (-0.2, 0, 1.2), (-0.2, 0, 1.5)
    up = ebs.new("upper_arm.L"); up.head, up.tail = (0.0, 0, 1.4), (0.32, 0, 1.4)
    up.parent = chest
    fo = ebs.new("forearm.L"); fo.head, fo.tail = (0.32, 0, 1.4), (0.62, 0, 1.4)
    fo.parent = up
    fo.use_connect = True
    bpy.ops.object.mode_set(mode='OBJECT')
    return mesh, arm


def _islands(mesh):
    isl = skin_gen._find_mesh_islands(mesh)
    V = mesh.data.vertices

    def pick(fn):
        return next(i for i in isl if fn([V[k].co for k in i]))
    sleeve = pick(lambda c: min(p.x for p in c) > 0.21 and max(p.x for p in c) < 0.43
                  and max(abs(p.y) for p in c) > 0.045)
    button = pick(lambda c: len(c) < 50)
    yoke = pick(lambda c: min(p.x for p in c) < -0.05)
    return sleeve, button, yoke


def _groups(mesh, idx):
    names = {g.index: g.name for g in mesh.vertex_groups}
    return {names[ge.group] for i in idx for ge in mesh.data.vertices[i].groups if ge.weight > 1e-4}


def _dominant(mesh, i):
    names = {g.index: g.name for g in mesh.vertex_groups}
    v = mesh.data.vertices[i]
    return names[max(v.groups, key=lambda ge: ge.weight).group]


def run():
    mesh, arm = _scene()
    skin_gen._apply_segment_weights(mesh, arm)
    skin_gen.rigidify_small_islands(mesh, arm, 'SEGMENT')
    sleeve, button, yoke = _islands(mesh)
    g = _groups(mesh, sleeve)
    assert g == {"upper_arm.L", "forearm.L"}, ("sleeve not on the elbow's bones", g)
    V = mesh.data.vertices
    near_end = min(sleeve, key=lambda i: V[i].co.x)
    far_end = max(sleeve, key=lambda i: V[i].co.x)
    assert _dominant(mesh, near_end) == "upper_arm.L" and _dominant(mesh, far_end) == "forearm.L"
    assert len(_groups(mesh, button)) == 1, ("button not rigid", _groups(mesh, button))
    assert len(_groups(mesh, yoke)) == 1, ("shoulder yoke not rigid", _groups(mesh, yoke))
    for ob in (mesh, arm):
        bpy.data.objects.remove(ob, do_unlink=True)
    # negative control: the old pass pins the sleeve rigid
    mesh, arm = _scene()
    skin_gen._apply_segment_weights(mesh, arm)
    skin_gen.rigidify_small_islands(mesh, arm)
    sleeve, _b, _y = _islands(mesh)
    assert len(_groups(mesh, sleeve)) == 1, "negative control: sleeve should be rigid without SEGMENT"
    for ob in (mesh, arm):
        bpy.data.objects.remove(ob, do_unlink=True)
    print("garments verified (sleeve bends on upper_arm/forearm, ends follow their bones; "
          "button and shoulder yoke rigid; old pass rigid = control)")
    print("ALL GARMENT TESTS PASS")


if __name__ == "__main__":
    run()
