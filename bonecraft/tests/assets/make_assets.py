"""Generate small ORIGINAL sample meshes for the test harness, in-host.

Run inside Bforartists:
    bforartists --background --python tests/assets/make_assets.py
Produces simple primitive-based stand-ins saved as .blend files. All
geometry is generated here — no imported assets.
"""
import bpy
import os

OUT = os.path.dirname(os.path.abspath(__file__))


def _save(name):
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, name + ".blend"))


def tpose_box():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.mesh.primitive_cube_add(size=0.4, location=(0, 0, 1.2))
    _save("tpose_box")


if __name__ == "__main__":
    tpose_box()
    print("sample assets written to", OUT)
