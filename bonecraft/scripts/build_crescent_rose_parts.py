"""Build examples/crescent-rose/CrescentRose_parts.blend from amandangm's Crescent Rose FBX (CC BY 4.0).

Usage (from bonecraft/):
    bforartists --background --factory-startup --python scripts/build_crescent_rose_parts.py -- <CrescentRose.fbx>

Imports the FBX, applies its 1/100 scale (the weapon is then about 2 m long), separates every loose piece,
joins the pieces of each part into one object named after the part (PIECES), sets each origin to its bounds
centre, downscales the textures to 1024 and packs them, and saves the .blend into examples/crescent-rose/.
"""
import os
import sys
import tempfile

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from boneforge.mechanisms.parts import islands   # noqa: E402

OUT = os.path.join(ROOT, "examples", "crescent-rose", "CrescentRose_parts.blend")
TEXTURE_MAX = 1024
SCALE = 6.25                      # 32 cm as imported -> 2.0 m
PART_NAMES = ("Receiver", "Grip", "Magazine", "Bolt", "Pole", "ButtSpike", "HeadMount",
              "Blade1", "Blade2", "BladeTip", "RearSpike", "PlateL", "PlateR", "StrutBase", "StrutRod")
# (mesh name in the FBX, loose-piece index in islands() order) -> part object name.
# Decided from each piece's centre: z along the weapon (0 = butt, 32 = head), y < 0 blade side, y > 4 back.
PIECES = {
    ("Black01", 0): "BladeTip",     # the knob joining the tip spike
    ("Black01", 1): "HeadMount",    # the rear block of the head
    ("Black01", 2): "HeadMount",    # the top cap
    ("Black01", 3): "HeadMount",    # the head core
    ("Black01", 4): "Receiver",     # small knob on the body
    ("Black01", 5): "Receiver",     # the body
    ("Black01", 6): "Magazine",     # the tube under the body
    ("Black01", 7): "StrutRod",     # the notched sleeve of the strut (head side)
    ("Blades01", 0): "Blade1",      # first blade plates, L and R
    ("Blades01", 1): "Blade1",
    ("Blades01", 2): "Blade2",      # second blade plates
    ("Blades01", 3): "Blade2",
    ("Blades01", 4): "Pole",        # the pole
    ("Blades01", 5): "BladeTip",    # the tip spike
    ("Blades01", 6): "RearSpike",   # the rear spike blades
    ("Blades01", 7): "RearSpike",
    ("Blades01", 8): "Receiver",    # the ring above the bolt
    ("Blades01", 9): "ButtSpike",   # the butt spike
    ("Red01", 0): "HeadMount",      # inner head plates
    ("Red01", 11): "HeadMount",
    ("Red01", 1): "Blade2",         # second segment covers
    ("Red01", 2): "Blade2",
    ("Red01", 3): "PlateL",         # outer head plate, x < 0
    ("Red01", 4): "PlateR",         # outer head plate, x > 0
    ("Red01", 5): "HeadMount",      # thin top covers
    ("Red01", 6): "HeadMount",
    ("Red01", 7): "RearSpike",      # spike pivot caps
    ("Red01", 8): "RearSpike",
    ("Red01", 9): "RearSpike",      # spike mount plates
    ("Red01", 10): "RearSpike",
    ("Red01", 12): "Grip",          # the grip block
    ("Red01", 13): "Receiver",      # the long red housing
    ("Red01", 14): "StrutBase",     # the thin strut rod (receiver side)
    ("Red01", 15): "Bolt",          # the bolt cylinder
    ("Red01", 16): "Pole",          # the collar
    ("Red01", 17): "Bolt",          # bolt knob bits
    ("Red01", 18): "Bolt",
}


def _separate(obj):
    """One object per loose piece; returns the new objects (obj itself keeps one piece)."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.object.mode_set(mode='OBJECT')
    return [o for o in bpy.context.selected_objects if o.type == 'MESH']


def _build_materials(textures_dir):
    """The FBX names its materials (Black_1, Blade_1, Red_1) but links no textures: wire each one's
    BaseColor, Normal, Roughness and Metallic maps from the textures folder into a Principled BSDF."""
    for mat in bpy.data.materials:
        stem = mat.name.partition("_")[0]            # Black, Blade, Red
        maps = {m: os.path.join(textures_dir, f"CrescentRose_Low_{stem}_1_{m}.jpg")
                for m in ("BaseColor", "Normal", "Roughness", "Metallic")}
        if not all(os.path.exists(p) for p in maps.values()):
            continue
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
        for i, (kind, path) in enumerate(maps.items()):
            tex = nodes.new("ShaderNodeTexImage")
            tex.image = bpy.data.images.load(path)
            tex.location = (-700, 300 - 300 * i)
            if kind == "BaseColor":
                links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
            elif kind == "Normal":
                tex.image.colorspace_settings.name = "Non-Color"
                nm = nodes.new("ShaderNodeNormalMap")
                nm.location = (-350, -600)
                links.new(tex.outputs["Color"], nm.inputs["Color"])
                links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
            else:
                tex.image.colorspace_settings.name = "Non-Color"
                links.new(tex.outputs["Color"], bsdf.inputs[kind])


def main():
    fbx = sys.argv[sys.argv.index("--") + 1]
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    bpy.ops.import_scene.fbx(filepath=fbx)
    root = bpy.data.objects["Crescent_Rose_Low"]
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    # the FBX root carries a 0.01 scale that leaves the weapon 32 cm long; Crescent Rose is about 2 m,
    # so scale by SCALE on top of it, keep each mesh's world matrix and drop the empty
    for o in meshes:
        mw = Matrix.Scale(SCALE, 4) @ o.matrix_world
        o.parent = None
        o.matrix_world = mw
    bpy.data.objects.remove(root)
    groups = {}
    for o in meshes:
        # island index -> piece object: separate() renumbers vertices per piece but keeps each piece's
        # first vertex, so match by that vertex's coordinates
        first = {i: tuple(round(c, 4) for c in o.data.vertices[idx[0]].co) for i, idx in enumerate(islands(o.data))}
        name = o.name
        for p in _separate(o):
            key = tuple(round(c, 4) for c in p.data.vertices[0].co)
            i = next(i for i, co in first.items() if co == key)
            groups.setdefault(PIECES[(name, i)], []).append(p)
    assert set(groups) == set(PART_NAMES), sorted(groups)
    for part_name, objs in groups.items():
        bpy.ops.object.select_all(action='DESELECT')
        for p in objs:
            p.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        if len(objs) > 1:
            bpy.ops.object.join()
        part = bpy.context.view_layer.objects.active
        part.name = part_name
        part.data.name = part_name
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    _build_materials(os.path.join(os.path.dirname(fbx), "CrescentRoseTextures"))
    # downscale, write as JPEG (packing a scaled buffer would store lossless PNG pixels, 10 MB for 12 maps),
    # then pack the JPEG bytes
    tmp = tempfile.mkdtemp(prefix="crescent-rose-tex-")
    bpy.context.scene.render.image_settings.file_format = 'JPEG'
    bpy.context.scene.render.image_settings.quality = 85
    for img in bpy.data.images:
        if img.size[0] > TEXTURE_MAX or img.size[1] > TEXTURE_MAX:
            img.scale(min(img.size[0], TEXTURE_MAX), min(img.size[1], TEXTURE_MAX))
        out = os.path.join(tmp, os.path.splitext(img.name)[0] + ".jpg")
        img.save_render(out)
        img.filepath = out
        img.reload()
        img.pack()
        img.filepath = ""
    bpy.ops.outliner.orphans_purge(do_recursive=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True, relative_remap=False)
    print("wrote", OUT, len(groups), "parts")


if __name__ == "__main__":
    main()
