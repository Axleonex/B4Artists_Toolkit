"""In-Bforartists behavioural test: face markers from the head's shape.

A synthetic head facing -Y (Blender's front): skull sphere, a nose, a chin
and two separate eyeball spheres, above a neck. The guessed face markers
must be on the FRONT (-Y) — they used to land on the back of the head — the
eye markers must snap to the eyeball centres, and the nose marker must sit on
the nose tip. Negative control: facing +Y moves the face to +Y.
"""
import bmesh
import bpy
from mathutils import Vector

from boneforge.autorig import wizard

EYES = {"L": Vector((0.032, -0.075, 1.62)), "R": Vector((-0.032, -0.075, 1.62))}
NOSE_TIP = Vector((0.0, -0.125, 1.575))


def _head(flip=False):
    bm = bmesh.new()
    def sphere(centre, radius, segs=24):
        r = bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=segs // 2, radius=radius)
        bmesh.ops.translate(bm, vec=centre, verts=r["verts"])
    sphere(Vector((0, 0, 1.60)), 0.10)                      # skull
    sphere(Vector((0, -0.055, 1.50)), 0.045)                # jaw / chin mass
    r = bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.02, radius2=0.002, depth=0.04)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(1.5708, 3, 'X'),
                     verts=r["verts"])
    bmesh.ops.translate(bm, vec=NOSE_TIP + Vector((0, 0.02, 0)), verts=r["verts"])
    r = bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.05, radius2=0.05, depth=0.2)
    bmesh.ops.translate(bm, vec=(0, 0, 1.40), verts=r["verts"])  # neck
    for c in EYES.values():
        sphere(c, 0.012, 12)                                # separate eyeballs
    if flip:
        for v in bm.verts:
            v.co.y = -v.co.y
    me = bpy.data.meshes.new("BF_HEAD")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("BF_HEAD", me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def run():
    head = _head()
    got = wizard._guess_face_markers_from_mesh(head, Vector((0, 0, 1.46)), -1.0)
    assert got, "no face markers"
    front = [k for k, v in got.items() if not k.startswith("JAW")]
    assert all(got[k].y < 0 for k in front), ("face markers not on the -Y front", {k: got[k].y for k in front})
    for side, key in (("L", "EYE_LEFT"), ("R", "EYE_RIGHT")):
        err = (got[key] - EYES[side]).length
        assert err < 0.005, ("eye marker not on the eyeball", key, err)
    nose_err = (got["NOSE_TIP"] - NOSE_TIP).length
    assert nose_err < 0.02, ("nose marker off the nose tip", nose_err)
    assert got["CHIN"].z < got["LOWER_LIP"].z < got["UPPER_LIP"].z < got["NOSE_TIP"].z
    bpy.data.objects.remove(head, do_unlink=True)
    # negative control: the same head facing +Y puts the face on +Y
    flipped = _head(flip=True)
    got2 = wizard._guess_face_markers_from_mesh(flipped, Vector((0, 0, 1.46)), 1.0)
    assert got2["NOSE_TIP"].y > 0, got2["NOSE_TIP"]
    bpy.data.objects.remove(flipped, do_unlink=True)
    print("face markers verified (front side, eyes snapped %.4f m, nose %.4f m, ordered chin<lips<nose)"
          % (max((got["EYE_LEFT"] - EYES["L"]).length, (got["EYE_RIGHT"] - EYES["R"]).length), nose_err))
    print("ALL FACE-MARKER TESTS PASS")


if __name__ == "__main__":
    run()
