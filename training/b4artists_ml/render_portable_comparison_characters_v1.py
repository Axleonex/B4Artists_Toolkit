"""Render a side-by-side author inspection of the frozen neutral characters."""
from pathlib import Path
import json
import math

import addon_utils
import bpy
from mathutils import Vector


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
MANIFEST = HERE.parent / "reference-assets-v1/manifest.json"
OUTPUT = HERE.parent / "results/portable-comparison-characters-v1.png"


def point_at(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat("-Z", "Y").to_euler()


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = "Portable Comparison Characters v1"
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 700
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(OUTPUT)
    scene.render.film_transparent = False
    scene.world = bpy.data.worlds.new("Preview World")
    scene.world.color = (0.035, 0.045, 0.065)
    addon_utils.enable("io_scene_fbx", default_set=False)
    data = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    positions = (-2.5, 0.0, 2.5)
    colors = ((0.22, 0.48, 0.75, 1.0), (0.30, 0.68, 0.50, 1.0), (0.76, 0.42, 0.26, 1.0))
    for expected, x, color in zip(data["assets"], positions, colors):
        before = set(bpy.context.scene.objects)
        bpy.ops.import_scene.fbx(filepath=str(ROOT / expected["fbx"]), use_anim=False,
                                 automatic_bone_orientation=False)
        added = [obj for obj in bpy.context.scene.objects if obj not in before]
        armature = next(obj for obj in added if obj.type == "ARMATURE")
        mesh = next(obj for obj in added if obj.type == "MESH")
        armature.location.x = x
        armature.show_in_front = True
        armature.display_type = "WIRE"
        material = bpy.data.materials.new(expected["id"] + " preview")
        material.diffuse_color = color
        material.use_nodes = True
        shader = material.node_tree.nodes.get("Principled BSDF")
        shader.inputs["Base Color"].default_value = color
        shader.inputs["Roughness"].default_value = 0.72
        mesh.data.materials.clear()
        mesh.data.materials.append(material)
        font_curve = bpy.data.curves.new(expected["id"] + " label", "FONT")
        font_curve.body = expected["label"] + "\n" + f"{expected['skeleton_height_m']:.2f} m"
        font_curve.align_x = "CENTER"
        font_curve.align_y = "CENTER"
        font_curve.size = 0.20
        text = bpy.data.objects.new(expected["id"] + " label", font_curve)
        scene.collection.objects.link(text)
        text.location = (x, 0.10, expected["skeleton_height_m"] + 0.28)
        text.rotation_euler = (math.radians(90.0), 0.0, 0.0)

    bpy.ops.mesh.primitive_plane_add(size=12.0, location=(0.0, 0.0, 0.0))
    floor = bpy.context.object
    floor.name = "Ground"
    floor_material = bpy.data.materials.new("Ground")
    floor_material.diffuse_color = (0.07, 0.08, 0.10, 1.0)
    floor_material.use_nodes = True
    floor_shader = floor_material.node_tree.nodes.get("Principled BSDF")
    floor_shader.inputs["Base Color"].default_value = (0.07, 0.08, 0.10, 1.0)
    floor_shader.inputs["Roughness"].default_value = 0.88
    floor.data.materials.append(floor_material)

    camera_data = bpy.data.cameras.new("Camera")
    camera = bpy.data.objects.new("Camera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = (0.0, -12.5, 3.2)
    camera.data.lens = 50
    point_at(camera, (0.0, 0.0, 1.05))
    scene.camera = camera
    key_data = bpy.data.lights.new("Key", "AREA")
    key_data.energy = 1250
    key_data.shape = "RECTANGLE"
    key_data.size = 5.0
    key = bpy.data.objects.new("Key", key_data)
    scene.collection.objects.link(key)
    key.location = (-3.0, -4.0, 6.0)
    point_at(key, (0.0, 0.0, 1.0))
    fill_data = bpy.data.lights.new("Fill", "AREA")
    fill_data.energy = 700
    fill_data.size = 4.0
    fill = bpy.data.objects.new("Fill", fill_data)
    scene.collection.objects.link(fill)
    fill.location = (4.0, -1.0, 3.0)
    point_at(fill, (0.0, 0.0, 1.0))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(write_still=True)
    print(json.dumps({"render": OUTPUT.relative_to(ROOT).as_posix(), "assets": 3}, indent=2))


if __name__ == "__main__":
    main()
