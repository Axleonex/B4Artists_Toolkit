r"""Real-model quality benchmark for BoneForge BFA (run inside Bforartists).

Scores the rigging pipeline against an artist-made rig: a VRM model's
humanoid map (VRM 0 or VRM 1) supplies ground-truth joints and skin weights.

Stages: import -> unrigged target mesh (artist truth stored per vertex) ->
auto-detection accuracy -> known-marker rig + production skinning vs artist
weights -> weight-bleed pose test -> auto end-to-end -> control rig drives the
mesh (P1) -> game export round-trip.

The model is NOT part of the repo (third-party assets are often paid). Point
at a local copy; without one the benchmark skips:

    set BF_BENCH_MODEL=C:\path\to\model.vrm      (a .vrm is glTF; .glb works too)
    bforartists --background --factory-startup --python tests/bench_real_model.py

Optional: ``BF_BENCH_WORK`` (work folder; default = the model's folder) and
``BF_BENCH_OUT`` (result JSON path), ``BF_BENCH_MAP`` (humanoid bone ->
bone name JSON, for non-VRM glTF skeletons). Gates marked ``enforced`` fail
the run; ``tracked`` gates report progress toward the parity plan.
"""
import sys, os, time, json, math, shutil, tempfile, traceback

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.environ.get("BF_BENCH_MODEL", "")
# work files (model copy, export, results) stay beside the model — never the
# system temp drive — unless BF_BENCH_WORK says otherwise
WORK = os.environ.get("BF_BENCH_WORK") or (os.path.dirname(os.path.abspath(MODEL)) if MODEL else tempfile.gettempdir())
OUT = os.environ.get("BF_BENCH_OUT") or os.path.join(WORK, "bf_bench_result.json")
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import bpy
from mathutils import Vector

R = {"stages": {}}
from mathutils import Matrix
ROT = Matrix.Identity(4)   # set in prepare(): BoneForge expects the -Y front


def stage(name):
    def deco(fn):
        def run(*a, **k):
            t = time.time()
            try:
                v = fn(*a, **k)
                R["stages"][name] = {"ok": True, "sec": round(time.time() - t, 2), **(v or {})}
                return v
            except Exception as e:
                R["stages"][name] = {"ok": False, "sec": round(time.time() - t, 2),
                                     "error": repr(e), "tb": traceback.format_exc()[-1500:]}
                print("STAGE FAIL", name, repr(e))
                return None
        return run
    return deco


# ------------------------------------------------------------------ helpers
REGIONS = ["torso", "head", "upper_arm.L", "forearm.L", "hand.L", "upper_arm.R", "forearm.R",
           "hand.R", "thigh.L", "shin.L", "foot.L", "thigh.R", "shin.R", "foot.R"]
# VRM humanoid bone -> scoring region. Works for VRM 0 (``VRM``) and VRM 1
# (``VRMC_vrm``) models; non-humanoid bones (hair, skirt, accessories) score
# as the region of their nearest humanoid ancestor.
HUMANOID_REGION = {
    "hips": "torso", "spine": "torso", "chest": "torso", "upperChest": "torso",
    "leftShoulder": "torso", "rightShoulder": "torso",
    "neck": "head", "head": "head", "leftEye": "head", "rightEye": "head", "jaw": "head",
    "leftUpperArm": "upper_arm.L", "leftLowerArm": "forearm.L", "leftHand": "hand.L",
    "rightUpperArm": "upper_arm.R", "rightLowerArm": "forearm.R", "rightHand": "hand.R",
    "leftUpperLeg": "thigh.L", "leftLowerLeg": "shin.L", "leftFoot": "foot.L", "leftToes": "foot.L",
    "rightUpperLeg": "thigh.R", "rightLowerLeg": "shin.R", "rightFoot": "foot.R", "rightToes": "foot.R",
}
HB = {}             # humanoid bone -> bone name, filled from the model file
BONE_REGION = {}    # bone name -> region, for humanoid bones


def load_humanoid_map(path):
    """Humanoid bone -> node name from the model's VRM 0 or VRM 1 extension."""
    import struct
    with open(path, "rb") as f:
        b = f.read()
    n = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + n])
    names = [nd.get("name", "") for nd in j.get("nodes", [])]
    ext = j.get("extensions", {})
    out = {}
    if "VRMC_vrm" in ext:
        for k, v in ext["VRMC_vrm"]["humanoid"]["humanBones"].items():
            out[k] = names[v["node"]]
    elif "VRM" in ext:
        for e in ext["VRM"]["humanoid"]["humanBones"]:
            out[e["bone"]] = names[e["node"]]
    return out


def artist_region(bone):
    """Walk up the artist hierarchy until a humanoid-mapped bone is found."""
    b = bone
    while b is not None:
        if b.name in BONE_REGION:
            return BONE_REGION[b.name]
        b = b.parent
    return "torso"


def bfa_region(name):
    n = name.replace("DEF-", "").replace("ORG-", "")
    for side in ("L", "R"):
        if n.startswith(("upper_arm." + side,)): return "upper_arm." + side
        if n.startswith(("forearm." + side,)): return "forearm." + side
        if n.startswith(("hand." + side,)) or (n.endswith("." + side) and any(
                f in n for f in ("thumb", "index", "middle", "ring", "pinky", "finger", "f_"))):
            return "hand." + side
        if n.startswith("thigh." + side): return "thigh." + side
        if n.startswith("shin." + side): return "shin." + side
        if n.startswith(("foot." + side, "toe." + side, "heel." + side)): return "foot." + side
        if n.startswith(("shoulder." + side, "clavicle." + side)): return "torso"
    if n.startswith(("neck", "head", "jaw", "eye", "lid", "brow", "lip")): return "head"
    return "torso"


# ------------------------------------------------------------------ stages
@stage("import")
def do_import():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    glb = os.path.join(WORK, "bf_bench_model.glb")
    shutil.copyfile(MODEL, glb)            # .vrm is glTF binary; importer wants .glb
    bpy.ops.import_scene.gltf(filepath=glb)
    arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    meshes = [o for o in bpy.data.objects if o.type == "MESH"
              and any(m.type == 'ARMATURE' and m.object for m in o.modifiers)]
    arm = arms[0]
    return {"armatures": len(arms), "meshes": [m.name for m in meshes],
            "verts": sum(len(m.data.vertices) for m in meshes), "artist_bones": len(arm.data.bones)}


@stage("prepare_target")
def prepare():
    global ROT
    arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
    bones = arm.data.bones
    # the character's left arm must sit on +X for a -Y facing character
    map_path = os.environ.get("BF_BENCH_MAP")
    if map_path:
        # any glTF skeleton: humanoid bone -> bone name from a JSON file; the
        # model is scored in its rest (bind) pose, not an animation frame
        with open(map_path, encoding="utf-8") as f:
            HB.update(json.load(f))
        if arm.animation_data:
            arm.animation_data.action = None
        for pb in arm.pose.bones:
            pb.matrix_basis = Matrix.Identity(4)
        bpy.context.view_layer.update()
        R["humanoid_map"] = os.path.basename(map_path)
    else:
        HB.update(load_humanoid_map(MODEL))
    if not HB:
        raise RuntimeError("no humanoid map: a VRM 0/1 model, or BF_BENCH_MAP=<bone map JSON>")
    missing = [b for b in HB.values() if b not in bones]
    if missing:
        raise RuntimeError("humanoid map names bones the model lacks: %s" % missing)
    for hb_name, bone_name in HB.items():
        for key, region in HUMANOID_REGION.items():
            if hb_name == key:
                BONE_REGION[bone_name] = region
        if "Thumb" in hb_name or "Index" in hb_name or "Middle" in hb_name                 or "Ring" in hb_name or "Little" in hb_name:
            BONE_REGION[bone_name] = "hand.L" if hb_name.startswith("left") else "hand.R"
    left_x = (arm.matrix_world @ arm.pose.bones[HB["leftUpperArm"]].head).x
    ROT = Matrix.Rotation(math.pi, 4, 'Z') if left_x < 0 else Matrix.Identity(4)
    R["rotated_180"] = left_x < 0
    dg = bpy.context.evaluated_depsgraph_get()
    parts = []
    # only meshes skinned to the character: the glTF importer also adds a
    # helper "Icosphere" bone-shape mesh that is not part of the model
    skinned = [o for o in bpy.data.objects if o.type == "MESH"
               and any(m.type == 'ARMATURE' and m.object for m in o.modifiers)]
    for src in skinned:
        # rest-pose evaluated copy, world space, no rig
        mod_states = [(m, m.show_viewport) for m in src.modifiers]
        me = bpy.data.meshes.new_from_object(src.evaluated_get(dg))
        me.transform(ROT @ src.matrix_world)
        dst = bpy.data.objects.new("PART_" + src.name, me)
        bpy.context.scene.collection.objects.link(dst)
        # ground truth region per vertex from artist weights
        gid = {g.index: g.name for g in src.vertex_groups}
        att = me.attributes.new("gt_region", 'INT', 'POINT')
        for v in src.data.vertices:
            best, bw = None, 0.0
            for ge in v.groups:
                if ge.weight > bw and gid.get(ge.group) in bones:
                    best, bw = gid[ge.group], ge.weight
            att.data[v.index].value = REGIONS.index(artist_region(bones[best])) if best else -1
        dst.vertex_groups.clear()
        parts.append(dst)
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts: p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    tgt = bpy.context.view_layer.objects.active
    tgt.name = "BENCH_MESH"
    # hide originals from view so they don't interfere
    for o in list(bpy.data.objects):
        if o is not tgt and o.type in ("MESH", "ARMATURE"):
            o.hide_set(True); o.hide_render = True
    # ground-truth joints (world)
    # posed joint heads: they match the evaluated mesh (glTF rest may differ)
    def head(n): return ROT @ arm.matrix_world @ arm.pose.bones[n].head
    marker_bones = {
        "PELVIS": "hips", "NECK_BASE": "neck",
        "SHOULDER_LEFT": "leftUpperArm", "SHOULDER_RIGHT": "rightUpperArm",
        "ELBOW_LEFT": "leftLowerArm", "ELBOW_RIGHT": "rightLowerArm",
        "WRIST_LEFT": "leftHand", "WRIST_RIGHT": "rightHand",
        "HIP_LEFT": "leftUpperLeg", "HIP_RIGHT": "rightUpperLeg",
        "KNEE_LEFT": "leftLowerLeg", "KNEE_RIGHT": "rightLowerLeg",
        "ANKLE_LEFT": "leftFoot", "ANKLE_RIGHT": "rightFoot",
        "TOE_LEFT": "leftToes", "TOE_RIGHT": "rightToes",
    }
    gt = {m: head(HB[hb]) for m, hb in marker_bones.items() if hb in HB}
    # head top = highest vertex whose ground truth is head, near head bone column
    reg = tgt.data.attributes["gt_region"].data
    hb = head(HB["head"])
    hz = [ (tgt.matrix_world @ v.co) for v in tgt.data.vertices
           if reg[v.index].value == REGIONS.index("head")]
    top = max(hz, key=lambda p: p.z)
    gt["HEAD_TOP"] = Vector((hb.x, hb.y, top.z))
    for s, a in (("LEFT", "L"), ("RIGHT", "R")):
        f = gt["ANKLE_" + s]; gt["HEEL_" + s] = Vector((f.x, f.y + 0.06, 0.0))
    fz = [v.co.z for v in tgt.data.vertices if reg[v.index].value in (REGIONS.index("foot.L"), REGIONS.index("foot.R"))]
    R["height"] = gt["HEAD_TOP"].z - min(fz)
    R["gt"] = {k: list(v) for k, v in gt.items()}
    nreg = sum(1 for d in reg if d.value >= 0)
    return {"target_verts": len(tgt.data.vertices), "height_m": round(R["height"], 3),
            "gt_labeled_verts": nreg, "left_arm_x_sign": "+" if gt["WRIST_LEFT"].x > 0 else "-"}


def register_bf():
    import boneforge
    try:
        boneforge.register()
    except Exception as e:
        print("register note:", e)
    return boneforge


def start_session(mesh):
    bpy.context.view_layer.objects.active = mesh
    mesh.select_set(True)
    bpy.ops.boneforge.autorig_wizard_start()
    s = bpy.context.scene.boneforge_autorig_session
    s.mesh_object_name = mesh.name
    return s


@stage("detection_accuracy")
def detection():
    from boneforge.autorig.constants import BODY_MARKERS
    register_bf()
    mesh = bpy.data.objects["BENCH_MESH"]
    s = start_session(mesh)
    bpy.ops.boneforge.autorig_run_detection()
    H = R["height"]; errs = {}
    for i, name in enumerate(BODY_MARKERS):
        m = s.body_markers[i]
        if m.confidence > 0 and name in R["gt"]:
            errs[name] = round((Vector(m.position) - Vector(R["gt"][name])).length / H * 100, 1)
    vals = sorted(errs.values())
    med = vals[len(vals) // 2] if vals else None
    R["detected"] = {BODY_MARKERS[i]: list(s.body_markers[i].position) for i in range(len(BODY_MARKERS))}
    bad = {k: v for k, v in errs.items() if v > 5.0}
    bpy.ops.boneforge.autorig_wizard_cancel()
    return {"markers_scored": len(errs), "median_err_pct_height": med,
            "max_err_pct_height": max(vals) if vals else None,
            "markers_over_5pct": bad, "per_marker_pct": errs}


def set_markers(s, positions):
    from boneforge.autorig.constants import BODY_MARKERS
    from boneforge.autorig.session import recalculate_derived_joints
    for i, name in enumerate(BODY_MARKERS):
        if name in positions:
            m = s.body_markers[i]
            m.position = positions[name]; m.confidence = 1.0; m.confirmed = True
    recalculate_derived_joints(s, bpy.context)


def generate(s, rig_type="BODY_ONLY"):
    s.rig_type = rig_type
    try:
        s.finger_count = 0
    except Exception:
        pass
    from boneforge.autorig import wizard
    s.wizard_step = wizard.STEP_REVIEW
    return bpy.ops.boneforge.autorig_generate()


def score_weights(mesh, label):
    reg = mesh.data.attributes["gt_region"].data
    gid = {g.index: g.name for g in mesh.vertex_groups}
    agree = total = zero = 0
    conf = {}
    for v in mesh.data.vertices:
        gtr = reg[v.index].value
        best, bw = None, 0.0
        for ge in v.groups:
            if ge.weight > bw:
                best, bw = gid[ge.group], ge.weight
        if best is None:
            zero += 1; continue
        if gtr < 0: continue
        total += 1
        br = bfa_region(best)
        if br == REGIONS[gtr]:
            agree += 1
        else:
            key = REGIONS[gtr] + "->" + br
            conf[key] = conf.get(key, 0) + 1
    top = dict(sorted(conf.items(), key=lambda kv: -kv[1])[:8])
    return {"region_agreement_pct": round(agree / max(total, 1) * 100, 1),
            "unweighted_verts": zero, "top_confusions": top}


def bleed_test(mesh, arm):
    """Bend left elbow & left knee 90deg; measure how many far-away verts move."""
    reg = mesh.data.attributes["gt_region"].data
    dg = bpy.context.evaluated_depsgraph_get()
    rest = [mesh.matrix_world @ v.co for v in mesh.evaluated_get(dg).data.vertices]
    pb = arm.pose.bones
    moved_bones = []
    for n in ("forearm.L", "shin.L"):
        b = pb.get(n) or pb.get("DEF-" + n)
        if b:
            b.rotation_mode = 'XYZ'; b.rotation_euler = (math.radians(90), 0, 0); moved_bones.append(b.name)
    # force FK so IK does not fight the pose
    for b in pb:
        for c in b.constraints:
            if c.type == 'IK': c.influence = 0.0
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    posed = [mesh.matrix_world @ v.co for v in mesh.evaluated_get(dg).data.vertices]
    H = R["height"]; thr = 0.005 * H
    far = {"torso", "head", "upper_arm.R", "forearm.R", "hand.R", "thigh.R", "shin.R", "foot.R"}
    far_n = far_moved = 0; near_n = near_moved = 0; maxfar = 0.0
    gid_all = {gg.index: gg.name for gg in mesh.vertex_groups}
    for i, v in enumerate(mesh.data.vertices):
        g = reg[v.index].value
        if g < 0: continue
        d = (posed[i] - rest[i]).length
        if REGIONS[g] in far:
            far_n += 1
            if d > thr:
                far_moved += 1
                R.setdefault("_bleed_regions", {}).setdefault(REGIONS[g], 0)
                R["_bleed_regions"][REGIONS[g]] += 1
                # which bone drags it (dominant weight) — for diagnosis
                best, bw = None, 0.0
                for ge in v.groups:
                    if ge.weight > bw:
                        best, bw = gid_all[ge.group], ge.weight
                key = "%s<-%s" % (REGIONS[g], best)
                R.setdefault("_bleed_bones", {}).setdefault(key, 0)
                R["_bleed_bones"][key] += 1
            maxfar = max(maxfar, d)
        elif REGIONS[g] in ("hand.L", "foot.L"):
            near_n += 1
            if d > thr: near_moved += 1
    for b in pb:
        b.rotation_euler = (0, 0, 0)
    br = R.pop("_bleed_regions", {})
    bb = dict(sorted(R.pop("_bleed_bones", {}).items(), key=lambda kv: -kv[1])[:8])
    return {"bleeding_far_regions": br, "bleeding_by_bone": bb, "posed_bones": moved_bones,
            "far_region_bleed_pct": round(far_moved / max(far_n, 1) * 100, 2),
            "max_far_move_pct_height": round(maxfar / H * 100, 2),
            "hand_foot_follow_pct": round(near_moved / max(near_n, 1) * 100, 1)}


@stage("oracle_rig_and_skin")
def oracle():
    register_bf()
    mesh = bpy.data.objects["BENCH_MESH"]
    s = start_session(mesh)
    set_markers(s, {k: tuple(v) for k, v in R["gt"].items()})
    t = time.time(); res = generate(s); gen_sec = time.time() - t
    arm = bpy.data.objects.get("BoneForge_Rig")
    out = {"operator": list(res), "gen_sec": round(gen_sec, 1)}
    if arm is None:
        return {**out, "armature": None}
    out["bones"] = len(arm.data.bones)
    out["skin_method"] = getattr(s, "skinning_method", None) if hasattr(s, "skinning_method") else None
    for attr in ("skinning_quality_score", "skinning_method", "skinning_warnings"):
        if hasattr(s, attr):
            out[attr] = getattr(s, attr) if not hasattr(getattr(s, attr), "__len__") or isinstance(getattr(s, attr), str) else str(getattr(s, attr))[:400]
    out["weights"] = score_weights(mesh, "oracle")
    out["bleed"] = bleed_test(mesh, arm)
    arm.name = "ORACLE_RIG"
    return out


@stage("auto_end_to_end")
def auto():
    register_bf()
    src = bpy.data.objects["BENCH_MESH"]
    mesh = src.copy(); mesh.data = src.data.copy(); mesh.name = "AUTO_MESH"
    bpy.context.scene.collection.objects.link(mesh)
    for m in list(mesh.modifiers): mesh.modifiers.remove(m)
    mesh.vertex_groups.clear(); mesh.parent = None
    src.hide_set(True)
    s = start_session(mesh)
    bpy.ops.boneforge.autorig_run_detection()
    try:
        bpy.ops.boneforge.autorig_accept_high()
    except Exception as e:
        print("accept_high", e)
    from boneforge.autorig.constants import BODY_MARKERS, REQUIRED_BODY_MARKERS
    unconfirmed = [BODY_MARKERS[i] for i in range(len(BODY_MARKERS))
                   if BODY_MARKERS[i] in REQUIRED_BODY_MARKERS and not s.body_markers[i].confirmed]
    # user would click confirm-all-green; mimic by confirming everything detected
    for i in range(len(BODY_MARKERS)):
        if s.body_markers[i].confidence > 0: s.body_markers[i].confirmed = True
    from boneforge.autorig.session import recalculate_derived_joints
    recalculate_derived_joints(s, bpy.context)
    res = generate(s)
    arm = bpy.data.objects.get("BoneForge_Rig")
    out = {"required_needing_manual_confirm": unconfirmed, "operator": list(res)}
    if arm:
        out["weights"] = score_weights(mesh, "auto")
        out["bleed"] = bleed_test(mesh, arm)
        arm.name = "AUTO_RIG"
    return out


@stage("control_rig")
def control():
    """P1: the control rig must drive the skinned mesh, with one deform skeleton."""
    from boneforge.autorig.rig_build import build_control_rig
    arm = bpy.data.objects.get("ORACLE_RIG")
    mesh = bpy.data.objects["BENCH_MESH"]
    if arm is None:
        raise RuntimeError("no oracle rig")
    arm.hide_set(False)
    dg = bpy.context.evaluated_depsgraph_get()
    rest = [mesh.matrix_world @ v.co for v in mesh.evaluated_get(dg).data.vertices]
    bpy.context.view_layer.objects.active = arm
    build_control_rig(arm, context=bpy.context)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    now = [mesh.matrix_world @ v.co for v in mesh.evaluated_get(dg).data.vertices]
    shift = max((p - q).length for p, q in zip(rest, now)) / R["height"] * 100
    deform = {b.name for b in arm.data.bones if b.use_deform}
    gid = {g.index: g.name for g in mesh.vertex_groups}
    weighted = {gid[ge.group] for v in mesh.data.vertices for ge in v.groups if ge.weight > 0}
    reg = mesh.data.attributes["gt_region"].data

    def centre(region):
        idx = [v.index for v in mesh.data.vertices
               if reg[v.index].value == REGIONS.index(region)]
        ev = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
        c = Vector()
        for i in idx:
            c += mesh.matrix_world @ ev[i].co
        return c / max(len(idx), 1)

    pb = arm.pose.bones
    bpy.ops.object.mode_set(mode='POSE')
    moves = {}
    for ctrl, region, other, axis, deg in (
            ("upperarm.fk-L", "hand.L", "hand.R", 2, 60),
            ("thigh.fk-R", "foot.R", "foot.L", 0, 45),
            ("chest", "head", "foot.L", 0, 30)):
        for side in ("L", "R"):
            for limb in ("arm", "leg"):
                pb["properties"]["IK_FK-%s-%s" % (limb, side)] = 0.0
        arm.update_tag()      # a bare ID-property write does not re-evaluate
        c0, o0 = centre(region), centre(other)
        b = pb[ctrl]
        b.rotation_mode = 'XYZ'
        e = [0.0, 0.0, 0.0]
        e[axis] = math.radians(deg)
        b.rotation_euler = e
        bpy.context.view_layer.update()
        moves[ctrl] = {
            "moves_" + region: round((centre(region) - c0).length / R["height"] * 100, 2),
            "moves_" + other: round((centre(other) - o0).length / R["height"] * 100, 2)}
        b.rotation_euler = (0, 0, 0)
        bpy.context.view_layer.update()
    bpy.ops.object.mode_set(mode='OBJECT')
    try:
        out_picker = list(bpy.ops.boneforge.picker_regenerate())
        lay = arm.get("bf_picker_layout") or arm.data.get("bf_picker_layout")
        lay = json.loads(lay) if isinstance(lay, str) else lay
        picker = len(lay["controls"]) if lay else 0
    except Exception as e:
        out_picker, picker = "ERR " + str(e)[:160], 0
    return {"bind_rest_shift_pct_height": round(shift, 4), "deform_bones": len(deform),
            "weighted_bones": len(weighted),
            "weights_on_non_deform": sorted(weighted - deform),
            "leftover_wizard_bones": [n for n in (b.name for b in arm.data.bones)
                                      if n.startswith("WIZ-")],
            "control_moves_pct_height": moves, "picker": out_picker,
            "picker_controls": picker}


@stage("finger_markers")
def fingers():
    """P7: finger markers from the hand's own shape vs the artist's finger joints."""
    from boneforge.autorig import wizard
    arm = [o for o in bpy.data.objects if o.type == "ARMATURE" and o.name not in
           ("ORACLE_RIG", "AUTO_RIG")][0]
    mesh = bpy.data.objects["BENCH_MESH"]

    def ph(n):
        return ROT @ (arm.matrix_world @ arm.pose.bones[HB[n]].head)

    def pt(n):
        return ROT @ (arm.matrix_world @ arm.pose.bones[HB[n]].tail)

    needed = ["leftIndexProximal", "leftMiddleProximal", "leftRingProximal",
              "leftLittleProximal", "leftIndexDistal", "leftMiddleDistal",
              "leftRingDistal", "leftLittleDistal", "leftThumbDistal"]
    if any(n not in HB for n in needed):
        return {"skipped": "model has no finger bones in its humanoid map"}
    gt = {"FINGER_PALM_L": (ph("leftHand") + ph("leftMiddleProximal")) * 0.5}
    for f, hb in (("INDEX", "leftIndex"), ("MIDDLE", "leftMiddle"), ("RING", "leftRing"),
                  ("PINKY", "leftLittle")):
        gt["FINGER_%s_BASE_L" % f] = ph(hb + "Proximal")
        gt["FINGER_%s_TIP_L" % f] = pt(hb + "Distal")
    gt["FINGER_THUMB_BASE_L"] = ph("leftThumbMetacarpal" if "leftThumbMetacarpal" in HB
                                   else "leftThumbProximal")
    gt["FINGER_THUMB_TIP_L"] = pt("leftThumbDistal")
    wrist, elbow = Vector(R["gt"]["WRIST_LEFT"]), Vector(R["gt"]["ELBOW_LEFT"])
    hand_len = (gt["FINGER_MIDDLE_TIP_L"] - wrist).length
    guess = wizard._guess_finger_markers_from_mesh(mesh, wrist, True, elbow)
    errs = {k: round((Vector(guess[k]) - v).length / hand_len * 100, 1)
            for k, v in gt.items() if k in guess}
    vals = sorted(errs.values())
    return {"hand_len": round(hand_len, 3), "median_pct_hand": vals[len(vals) // 2],
            "max_pct_hand": vals[-1], "per_marker": errs}


@stage("joint_correctives")
def correctives():
    """P7: elbow corrective on the real (open, multi-piece) mesh: how much of the
    rest cross-section survives a 110 degree bend, without and with the key."""
    from boneforge.autorig import joint_correctives as jc
    arm = bpy.data.objects.get("ORACLE_RIG")
    mesh = bpy.data.objects["BENCH_MESH"]
    reg = mesh.data.attributes["gt_region"].data
    idx = [v.index for v in mesh.data.vertices
           if reg[v.index].value in (REGIONS.index("forearm.L"), REGIONS.index("upper_arm.L"))]
    pb = arm.pose.bones
    pb["properties"]["IK_FK-arm-L"] = 0.0
    arm.update_tag(); bpy.context.view_layer.update()
    name, info = jc.generate_joint_corrective(mesh, arm, "elbow", "L")
    if name is None:
        return info
    key = mesh.data.shape_keys.key_blocks[name]
    joint = arm.matrix_world @ pb["forearm.def-L"].head
    radius = info["band_radius"]

    def own_dist(i, p):
        segs = [(arm.matrix_world @ pb[n].head, arm.matrix_world @ pb[n].tail)
                for n in ("upperarm.def-L", "forearm.def-L")]
        best = 1e9
        for h, t in segs:
            d = t - h; dd = max(d.dot(d), 1e-12)
            u = max(0.0, min(1.0, (p - h).dot(d) / dd))
            best = min(best, (p - (h + d * u)).length)
        return best

    def band_radii():
        ev = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
        pts = [(i, mesh.matrix_world @ ev[i].co) for i in idx]
        return {i: own_dist(i, p) for i, p in pts
                if (p - arm.matrix_world @ pb["forearm.def-L"].head).length < radius}

    fore = pb["forearm.fk-L"]; fore.rotation_mode = 'XYZ'
    rest = band_radii()
    fore.rotation_euler = (info["bend_sign"] * math.radians(110), 0, 0)
    key.mute = True; bpy.context.view_layer.update()
    plain = band_radii()
    key.mute = False; bpy.context.view_layer.update()
    fixed = band_radii()
    fore.rotation_euler = (0, 0, 0); bpy.context.view_layer.update()
    common = [i for i in rest if i in plain and i in fixed and rest[i] > 1e-6]
    kept = lambda d: sum(min(d[i] / rest[i], 1.5) for i in common) / max(len(common), 1) * 100
    return {"band_vertices": len(common), "cross_section_kept_plain_pct": round(kept(plain), 1),
            "cross_section_kept_corrected_pct": round(kept(fixed), 1),
            "vertices_moved": info.get("vertices_moved")}


@stage("twist_bones")
def twist():
    """P7: forearm twist bones stop the wrist pinch on the real character."""
    from boneforge.autorig import rig_integrate as ri
    arm = bpy.data.objects.get("ORACLE_RIG")
    mesh = bpy.data.objects["BENCH_MESH"]
    reg = mesh.data.attributes["gt_region"].data
    fore = [v.index for v in mesh.data.vertices if reg[v.index].value == REGIONS.index("forearm.L")]
    hand = [v.index for v in mesh.data.vertices if reg[v.index].value == REGIONS.index("hand.L")]
    base = twist_profile(mesh, arm, fore, hand)
    added = ri.add_twist_bones(arm, segments=2)
    fixed = twist_profile(mesh, arm, fore, hand)
    return {"twist_bones_added": len(added), "max_twist_jump_before_deg": round(base, 1),
            "max_twist_jump_after_deg": round(fixed, 1)}


def twist_profile(mesh, arm, fore_idx, hand_idx, side="L", deg=90.0):
    """Largest twist jump (degrees) between neighbouring forearm/hand rings.

    Turns the FK hand ``deg`` about its own axis and measures how far each
    ring of the forearm (10% bins from elbow to wrist) plus the hand turns
    about the forearm axis. Without twist bones the forearm stays at 0 while
    the hand turns fully: one ``deg``-sized tear at the wrist.
    """
    import math as _m
    import bpy as _bpy
    fb = arm.data.bones["forearm.def-" + side]
    h, t = arm.matrix_world @ fb.head_local, arm.matrix_world @ fb.tail_local
    d, length = (t - h).normalized(), (t - h).length

    def radial(p):
        v = p - h
        return v - d * v.dot(d)

    def positions():
        ev = mesh.evaluated_get(_bpy.context.evaluated_depsgraph_get()).data.vertices
        return {i: mesh.matrix_world @ ev[i].co for i in list(fore_idx) + list(hand_idx)}

    pb = arm.pose.bones
    pb["properties"]["IK_FK-arm-" + side] = 0.0
    arm.update_tag(); _bpy.context.view_layer.update()
    p0 = positions()
    hand = pb["hand.fk-" + side]; hand.rotation_mode = 'XYZ'
    hand.rotation_euler = (0.0, _m.radians(deg), 0.0)
    _bpy.context.view_layer.update()
    p1 = positions()
    hand.rotation_euler = (0.0, 0.0, 0.0); _bpy.context.view_layer.update()

    def angle(i):
        a, b = radial(p0[i]), radial(p1[i])
        if a.length < 1e-6 or b.length < 1e-6:
            return None
        ang = _m.degrees(a.angle(b))
        return ang if a.cross(b).dot(d) >= 0 else -ang

    rings = {}
    for i in fore_idx:
        u = (p0[i] - h).dot(d) / length
        if 0.0 <= u <= 1.0:
            ang = angle(i)
            if ang is not None:
                rings.setdefault(min(int(u * 10), 9), []).append(ang)
    hand_angles = [a for a in (angle(i) for i in hand_idx) if a is not None]
    means = [sum(v) / len(v) for k, v in sorted(rings.items()) if len(v) >= 3]
    if hand_angles:
        means.append(sum(hand_angles) / len(hand_angles))
    return max((abs(b - a) for a, b in zip(means, means[1:])), default=0.0)


@stage("game_export_roundtrip")
def export():
    """P5: deform-only game profiles export exactly the skinned skeleton."""
    arm = bpy.data.objects.get("ORACLE_RIG")
    mesh = bpy.data.objects["BENCH_MESH"]
    deform = {b.name for b in arm.data.bones if b.use_deform}
    weighted = {g.name for g in mesh.vertex_groups}
    core = ("hips", "chest", "neck", "head", "upperarm.def-L", "forearm.def-L",
            "hand.def-L", "thigh.def-R", "shin.def-R", "foot.def-R")
    # FBX deform-only keeps the ancestors of deform bones (one rooted
    # hierarchy: root -> COG -> hips); anything else extra is a leak
    ancestors = set()
    for b in arm.data.bones:
        if b.use_deform:
            p = b.parent
            while p is not None:
                if not p.use_deform:
                    ancestors.add(p.name)
                p = p.parent
    out = {"source_deform_bones": len(deform), "allowed_ancestors": sorted(ancestors),
           "profiles": {}}
    for pid in ("unity_humanoid", "unreal_humanoid", "vrchat"):
        path = os.path.join(WORK, "bf_bench_export_%s.fbx" % pid)
        bpy.ops.object.select_all(action='DESELECT')
        arm.hide_set(False); mesh.hide_set(False)
        arm.select_set(True); mesh.select_set(True)
        bpy.context.view_layer.objects.active = arm
        res = list(bpy.ops.boneforge.profile_export(filepath=path, profile_id=pid,
                                                    action_mode='NONE'))
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=path)
        new = [o for o in bpy.data.objects if o not in before]
        na = [o for o in new if o.type == "ARMATURE"]
        nm = [o for o in new if o.type == "MESH"]
        bones = {b.name for b in na[0].data.bones} if na else set()
        groups = {g.name for g in nm[0].vertex_groups} if nm else set()
        roots = [b.name for b in na[0].data.bones if b.parent is None] if na else []
        out["profiles"][pid] = {
            "result": res, "armatures": len(na), "bones": len(bones),
            "extra_bones": sorted(bones - deform - ancestors)[:8],
            "hierarchy_ancestors": sorted((bones - deform) & ancestors),
            "missing_deform": sorted(deform - bones)[:8],
            "weights_lost": sorted((weighted & deform) - groups)[:8],
            "missing_core": [c for c in core if c not in bones], "roots": roots}
        for o in new:
            bpy.data.objects.remove(o, do_unlink=True)
    return out


def _clip_path():
    clip = os.environ.get("BF_BENCH_CLIP", "")
    if clip and os.path.isfile(clip):
        return clip
    guess = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(MODEL))), "motion")
    if os.path.isdir(guess):
        for f in sorted(os.listdir(guess)):
            if f.lower().endswith(".bvh") and "walk" in f.lower():
                return os.path.join(guess, f)
    return ""


@stage("retarget_real_clip")
def retarget_clip():
    """P6: a real motion-capture clip drives the rig with the same motion.

    Fidelity = per mapped bone, per frame, the angle between where the source
    bone points and where the target bone points (after aligning the two
    figures' facing).
    """
    clip = _clip_path()
    if not clip:
        return {"skipped": "no clip (set BF_BENCH_CLIP)"}
    from mathutils import Quaternion
    from boneforge.autorig import maps as bf_maps, retarget as rt, retarget_core as rc
    arm = bpy.data.objects.get("ORACLE_RIG")
    before = set(bpy.data.objects)
    bpy.ops.import_anim.bvh(filepath=clip, global_scale=0.01, rotate_mode='NATIVE',
                            update_scene_fps=False, update_scene_duration=True)
    src = [o for o in bpy.data.objects if o not in before and o.type == "ARMATURE"][0]
    best = None
    for mid in bf_maps.available_maps():
        res = rc.build_mappings(bf_maps.load_map(mid), [b.name for b in src.data.bones],
                                [b.name for b in arm.data.bones])
        nmatch = sum(1 for m in res["mappings"] if m["matched"])
        if best is None or nmatch > best[1]:
            best = (mid, nmatch, res)
    mid, nmatch, res = best
    name_map = rc.matched_name_map(res)
    for side in ("L", "R"):
        for limb in ("arm", "leg"):
            arm.pose.bones["properties"]["IK_FK-%s-%s" % (limb, side)] = 0.0
    arm.update_tag()
    act = src.animation_data.action
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
    frames = rt.retarget_clip_corrected(src, arm, name_map, f0, f1)

    # facing alignment: the same whole-body turn the retarget applies
    align = rt.facing_alignment(src, arm, name_map)

    def dirs(ob, names):
        out = {}
        dg = bpy.context.evaluated_depsgraph_get()
        ev = ob.evaluated_get(dg)
        for n in names:
            pb = ev.pose.bones[n]
            out[n] = ((ob.matrix_world @ pb.tail) - (ob.matrix_world @ pb.head)).normalized()
        return out

    scene = bpy.context.scene
    scene.frame_set(f0 - 1 if f0 > 0 else 0)
    pairs = [(s, t) for s, t in name_map.items() if t not in ("hips",)]
    # rest directions (no animation influence): use data bones
    def rest_dir(ob, n):
        b = ob.data.bones[n]
        return ((ob.matrix_world @ b.tail_local) - (ob.matrix_world @ b.head_local)).normalized()
    errs = {t: [] for _s, t in pairs}
    for f in range(f0, f1 + 1, max(1, (f1 - f0) // 60)):
        scene.frame_set(f)
        sd = dirs(src, [s for s, _t in pairs])
        td = dirs(arm, [t for _s, t in pairs])
        for s, t in pairs:
            # pose fidelity: does the target bone point where the source bone
            # points (after the whole-body facing alignment)? Rest poses of
            # mocap skeletons are arbitrary, so nothing is measured vs rest.
            want = align @ sd[s]
            ang = math.degrees(want.angle(td[t])) if want.length and td[t].length else 0.0
            errs[t].append(ang)
    # root motion + foot skate: while the source foot is planted (near its
    # lowest and barely moving), the target foot should barely move too
    src_foot = [s for s, t in name_map.items() if t == "foot.fk-L"]
    skate, travel = None, None
    if src_foot and "foot.def-L" in arm.pose.bones:
        H = R["height"]
        sp, tp, hs, ht = [], [], [], []
        hips_src = [s for s, t in name_map.items() if t == "hips"]
        for f in range(f0, f1 + 1):
            scene.frame_set(f)
            dg = bpy.context.evaluated_depsgraph_get()
            se, te = src.evaluated_get(dg), arm.evaluated_get(dg)
            sp.append(src.matrix_world @ se.pose.bones[src_foot[0]].head)
            tp.append(arm.matrix_world @ te.pose.bones["foot.def-L"].head)
            if hips_src:
                hs.append(src.matrix_world @ se.pose.bones[hips_src[0]].head)
                ht.append(arm.matrix_world @ te.pose.bones["hips"].head)
        zmin = min(p.z for p in sp)
        s_leg = sum(src.data.bones[s].length for s, t in name_map.items()
                    if t in ("thigh.fk-L", "shin.fk-L")) * src.matrix_world.to_scale()[0]
        planted = [i for i in range(1, len(sp))
                   if sp[i].z - zmin < 0.04 * s_leg and (sp[i] - sp[i - 1]).length < 0.01 * s_leg]
        if planted:
            moves = sorted(((tp[i] - tp[i - 1]).to_2d().length) for i in planted)
            skate = round(moves[len(moves) // 2] / H * 100, 3)
        if hs:
            s_tr = (hs[-1] - hs[0]).to_2d().length
            t_tr = (ht[-1] - ht[0]).to_2d().length
            t_leg = arm.data.bones["thigh.fk-L"].length + arm.data.bones["shin.fk-L"].length
            travel = round((t_tr / t_leg) / (s_tr / s_leg), 3) if s_tr > 1e-6 else None
    # Collarbones deliberately keep the character's own angle (a mocap
    # collarbone tilted up shrugged a flat VRoid one) and follow only the
    # clip's collarbone motion, so they are reported, not direction-scored.
    clav = {t: round(sorted(v)[len(v) // 2], 1) for t, v in errs.items() if v and "clavicle" in t}
    errs = {t: v for t, v in errs.items() if "clavicle" not in t}
    per_bone = {t: round(sorted(v)[len(v) // 2], 1) for t, v in errs.items() if v}
    allv = sorted(a for v in errs.values() for a in v)
    return {"clip": os.path.basename(clip), "map": mid, "mapped": nmatch,
            "frames": frames, "median_deg": round(allv[len(allv) // 2], 1),
            "p90_deg": round(allv[int(len(allv) * 0.9)], 1),
            "worst_bones": dict(sorted(per_bone.items(), key=lambda kv: -kv[1])[:6]),
            "collarbone_offset_deg": clav,
            "planted_foot_skate_pct_height_per_frame": skate,
            "travel_ratio_leg_normalised": travel}


def _get(path, default=None):
    cur = R["stages"]
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def gates():
    """Parity-plan gates. ``enforced`` gates fail the run."""
    g = []

    def gate(name, kind, ok, value):
        g.append({"gate": name, "kind": kind, "pass": bool(ok), "value": value})

    moves = _get(("control_rig", "control_moves_pct_height"), {}) or {}
    arm_m = moves.get("upperarm.fk-L", {})
    leg_m = moves.get("thigh.fk-R", {})
    gate("P1 FK arm moves its hand >=10% height", "enforced",
         arm_m.get("moves_hand.L", 0) >= 10, arm_m)
    gate("P1 FK arm leaves the other hand still", "enforced",
         arm_m.get("moves_hand.R", 99) <= 0.2, arm_m)
    gate("P1 FK leg moves its foot >=10% height", "enforced",
         leg_m.get("moves_foot.R", 0) >= 10, leg_m)
    gate("P1 spine control moves the head", "enforced",
         (moves.get("chest") or {}).get("moves_head", 0) >= 3, moves.get("chest"))
    gate("P1 bind does not move the rest pose", "enforced",
         _get(("control_rig", "bind_rest_shift_pct_height"), 99) <= 0.01,   # 0.0 is a pass, not "missing"
         _get(("control_rig", "bind_rest_shift_pct_height")))
    gate("P1 one deform skeleton (no leftovers, weights only on deform)", "enforced",
         _get(("control_rig", "leftover_wizard_bones"), ["?"]) == []
         and _get(("control_rig", "weights_on_non_deform"), ["?"]) == [],
         {"leftover": _get(("control_rig", "leftover_wizard_bones")),
          "non_deform": _get(("control_rig", "weights_on_non_deform"))})
    gate("P2 detection median <=3% height", "enforced",
         _get(("detection_accuracy", "median_err_pct_height"), 99) <= 3,
         _get(("detection_accuracy", "median_err_pct_height")))
    gate("P2 detection max <=6% height", "enforced",
         _get(("detection_accuracy", "max_err_pct_height"), 99) <= 6,
         _get(("detection_accuracy", "max_err_pct_height")))
    gate("P3 skin agreement >=95% vs artist", "enforced",
         _get(("oracle_rig_and_skin", "weights", "region_agreement_pct"), 0) >= 95,
         _get(("oracle_rig_and_skin", "weights", "region_agreement_pct")))
    gate("P3 skin agreement >=92% vs artist (regression floor)", "enforced",
         _get(("oracle_rig_and_skin", "weights", "region_agreement_pct"), 0) >= 92,
         _get(("oracle_rig_and_skin", "weights", "region_agreement_pct")))
    gate("P3 cross-side bleed <=0.1% of far vertices", "enforced",
         _get(("oracle_rig_and_skin", "bleed", "far_region_bleed_pct"), 99) <= 0.1,
         {"pct": _get(("oracle_rig_and_skin", "bleed", "far_region_bleed_pct")),
          "regions": _get(("oracle_rig_and_skin", "bleed", "bleeding_far_regions"))})
    gate("P3 zero cross-side bleed (target)", "tracked",
         _get(("oracle_rig_and_skin", "bleed", "bleeding_far_regions"), {"?": 1}) == {},
         _get(("oracle_rig_and_skin", "bleed", "bleeding_far_regions")))
    ceiling = {"AUTO": 1.0, "SEGMENT": 0.8, "ENVELOPE": 0.7, "FALLBACK": 0.5}
    method = _get(("oracle_rig_and_skin", "skinning_method"))
    score = _get(("oracle_rig_and_skin", "skinning_quality_score"))
    gate("P4 quality score is honest (<= its method's ceiling, not 'perfect')", "enforced",
         score is not None and method in ceiling and float(score) <= ceiling[method] + 1e-6,
         {"method": method, "score": score})
    for pid, info in (_get(("game_export_roundtrip", "profiles"), {}) or {}).items():
        gate("P5 %s export = the skinned deform skeleton (no leaked control bones, "
             "none missing, no lost weights, core chain, one root)" % pid, "enforced",
             info["armatures"] == 1 and not info["extra_bones"] and not info["missing_deform"]
             and not info["weights_lost"] and not info["missing_core"] and len(info["roots"]) == 1,
             info)
    fm = _get(("finger_markers",), {}) or {}
    if "median_pct_hand" in fm:
        gate("P7 finger markers: median <=20% of hand length", "enforced",
             fm["median_pct_hand"] <= 20, {k: fm[k] for k in ("median_pct_hand", "max_pct_hand")})
    jc_info = _get(("joint_correctives",), {}) or {}
    if "cross_section_kept_corrected_pct" in jc_info:
        gate("P7 elbow corrective keeps more of the cross-section at 110 deg", "enforced",
             jc_info["cross_section_kept_corrected_pct"] > jc_info["cross_section_kept_plain_pct"] + 2
             and jc_info["cross_section_kept_corrected_pct"] >= 90, jc_info)
    tw = _get(("twist_bones",), {}) or {}
    if "max_twist_jump_after_deg" in tw:
        gate("P7 twist bones: largest forearm twist jump <=50 deg for a 90 deg wrist turn", "enforced",
             tw["max_twist_jump_after_deg"] <= 50
             and tw["max_twist_jump_after_deg"] < tw["max_twist_jump_before_deg"], tw)
    rt_info = _get(("retarget_real_clip",), {}) or {}
    if "median_deg" in rt_info:
        gate("P6 real clip: median bone-direction error <=3 deg", "enforced",
             rt_info["median_deg"] <= 3.0, {k: rt_info.get(k) for k in ("clip", "map", "median_deg", "p90_deg")})
        skate = rt_info.get("planted_foot_skate_pct_height_per_frame")
        gate("P6 real clip: planted foot skate <=0.25% height/frame", "enforced",
             skate is not None and skate <= 0.25, skate)
        travel = rt_info.get("travel_ratio_leg_normalised")
        gate("P6 real clip: root travel matches (leg-normalised ratio 0.9-1.1)", "enforced",
             travel is not None and 0.9 <= travel <= 1.1, travel)
    return g


def main():
    if not MODEL or not os.path.isfile(MODEL):
        print("BENCH SKIPPED: set BF_BENCH_MODEL to a local VRoid/VRM model")
        return 0
    do_import(); prepare(); detection(); fingers(); oracle(); auto(); control(); twist(); correctives(); export(); retarget_clip()
    st = R["stages"]
    R["timing"] = {   # Q1: pipeline speed on this model
        "target_verts": st.get("prepare_target", {}).get("target_verts"),
        "generate_sec": st.get("oracle_rig_and_skin", {}).get("gen_sec"),
        "auto_end_to_end_sec": st.get("auto_end_to_end", {}).get("sec"),
        "control_rig_sec": st.get("control_rig", {}).get("sec"),
    }
    print("BENCH TIMING", json.dumps(R["timing"]))
    R["gates"] = gates()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)
    for g in R["gates"]:
        print("%-5s %-9s %s  -> %s" % ("PASS" if g["pass"] else "FAIL", g["kind"],
                                      g["gate"], json.dumps(g["value"], default=str)[:120]))
    broken = [name for name, v in R["stages"].items() if not v.get("ok")]
    failed = [g for g in R["gates"] if g["kind"] == "enforced" and not g["pass"]]
    print("BENCH DONE -> %s  (stage errors: %s)" % (OUT, broken or "none"))
    if broken or failed:
        print("BENCH ENFORCED GATES FAILED")
        return 1
    print("BENCH ENFORCED GATES PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
