"""In-Bforartists test: the Crescent Rose example files.

* CrescentRose_parts.blend: the 15 part objects, applied transforms, packed 1024 textures, about 2 m long.
* CrescentRose_Mechanisms.blend (Task 4): the rig's parts, joints, links, sequences and forms, a clean
  validator, and every form puts every control where it was saved.
"""
import os

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
EXAMPLES = os.path.join(os.path.dirname(HERE), "examples", "crescent-rose")
PART_NAMES = ("Receiver", "Grip", "Magazine", "Bolt", "Pole", "ButtSpike", "HeadMount",
              "Blade1", "Blade2", "BladeTip", "RearSpike", "PlateL", "PlateR",
              "StrutBase", "StrutRod")


def _open(name):
    path = os.path.join(EXAMPLES, name)
    assert os.path.exists(path), path
    bpy.ops.wm.open_mainfile(filepath=path)


def check_parts_file():
    _open("CrescentRose_parts.blend")
    meshes = {o.name: o for o in bpy.data.objects if o.type == 'MESH'}
    assert set(meshes) == set(PART_NAMES), sorted(meshes)
    for o in meshes.values():
        assert o.parent is None, o.name
        assert tuple(round(s, 4) for s in o.scale) == (1, 1, 1), (o.name, o.scale[:])
        assert all(abs(r) < 1e-6 for r in o.rotation_euler), (o.name, o.rotation_euler[:])
        assert len(o.data.polygons) > 0, o.name
    lo = min(min((o.matrix_world @ v.co).z for v in o.data.vertices) for o in meshes.values())
    hi = max(max((o.matrix_world @ v.co).z for v in o.data.vertices) for o in meshes.values())
    assert 1.8 < hi - lo < 2.4, (lo, hi)          # about 2 m long at scene scale
    images = [i for i in bpy.data.images if i.users]
    assert images, "no textures"
    for img in images:
        assert img.packed_file is not None, img.name
        assert max(img.size) <= 1024, (img.name, img.size[:])
    assert bpy.data.filepath.endswith("CrescentRose_parts.blend")
    print("PASS Crescent Rose parts file")


MECHANISMS = {"HeadMount Hinge": "HINGE", "Blade1 Hinge": "HINGE", "Blade2 Hinge": "HINGE", "BladeTip Hinge": "HINGE",
              "RearSpike Hinge": "HINGE", "PlateL Hinge": "HINGE", "PlateR Hinge": "HINGE", "Grip Hinge": "HINGE",
              "Magazine Slide": "SLIDE", "Bolt Slide": "SLIDE", "Pole Slide": "SLIDE", "Pole Telescope": "TELESCOPE",
              "Head Strut": "PISTON", "PlateR Follow": "FOLLOW"}
SEQUENCES = ("Scythe to Rifle", "Rifle to Compact")
FORMS = ("Scythe", "Rifle", "Compact")


def check_rig_file():
    import boneforge
    try:
        boneforge.register()
    except Exception as exc:
        print("register note:", exc)
    from boneforge.mechanisms import build, records, validate
    _open("CrescentRose_Mechanisms.blend")
    arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE' and records.has_records(o.data))
    rig = records.to_model(arm)
    assert {p.name for p in rig.parts} == set(PART_NAMES), sorted(p.name for p in rig.parts)
    assert {m.name: m.type for m in rig.mechanisms} == MECHANISMS, {m.name: m.type for m in rig.mechanisms}
    assert [s.name for s in rig.sequences] == list(SEQUENCES), [s.name for s in rig.sequences]
    assert [f.name for f in rig.forms] == list(FORMS), [f.name for f in rig.forms]
    assert not rig.missing, rig.missing
    for s in rig.sequences:
        assert s.steps, s.name
    found = validate.rig_checks(arm)
    bad = [(s, m) for s, m, b in found if s != "pass" and "root" not in m]
    assert not bad, bad
    for img in [i for i in bpy.data.images if i.users]:
        assert img.packed_file is not None, img.name
    # the file opens in scythe form: every object part sits where the parts file put it
    for name in PART_NAMES:
        ob = bpy.data.objects[name]
        assert all(abs(a) < 1e-3 for a in ob.matrix_world.to_euler()), (name, ob.matrix_world.to_euler()[:])
    # every form puts every control where it was saved
    ids = rig.ids()
    for form in arm.data.bonecraft_mech.forms:
        bpy.ops.boneforge.mech_go_to_form(name=form.name)
        bpy.context.view_layer.update()
        for v in form.values:
            if v.key in ids:
                got = build.get_value(arm, rig, v.key)
                assert abs(got - v.value) < 1e-3, (form.name, v.key, got, v.value)
    scythe = {v.key: v.value for v in arm.data.bonecraft_mech.forms["Scythe"].values}
    rifle = {v.key: v.value for v in arm.data.bonecraft_mech.forms["Rifle"].values}
    s2r = next(s.id for s in rig.sequences if s.name == "Scythe to Rifle")
    assert abs(scythe[s2r]) < 1e-3 and abs(rifle[s2r] - 1.0) < 1e-3, (scythe[s2r], rifle[s2r])
    bpy.ops.boneforge.mech_go_to_form(name="Rifle")
    bpy.context.view_layer.update()
    pole = bpy.data.objects["Pole"].matrix_world.translation.z
    assert pole > 0.9, ("the pole does not retract in the Rifle form", pole)
    print("PASS Crescent Rose rig file: %d mechanisms, %d sequences, %d forms" % (len(rig.mechanisms), len(rig.sequences), len(rig.forms)))


def run():
    check_parts_file()
    check_rig_file()
