"""BoneForge-compatible semantic roles, with separate writable controls.

The bundled source maps retain BoneForge's GPL-2.0-or-later data unchanged.
No dependency on an installed BoneForge or Rigify add-on.
"""
from dataclasses import dataclass
import json
from importlib.resources import files


@dataclass(frozen=True)
class RigProfile:
    name: str
    roles: dict
    controls: tuple
    missing: tuple
    warnings: tuple = ()
    family: str = "humanoid"
    schema: str = "humanoid_v1"


REQUIRED = ("hips", "head", "upperarm.fk-L", "forearm.fk-L", "hand.fk-L",
            "upperarm.fk-R", "forearm.fk-R", "hand.fk-R", "thigh.fk-L",
            "shin.fk-L", "foot.fk-L", "thigh.fk-R", "shin.fk-R", "foot.fk-R")

QUADRUPED_REQUIRED = (
    "pelvis", "chest", "head",
    "fore.upper-L", "fore.lower-L", "fore.foot-L", "fore.toe-L",
    "fore.upper-R", "fore.lower-R", "fore.foot-R", "fore.toe-R",
    "hind.upper-L", "hind.lower-L", "hind.foot-L", "hind.toe-L",
    "hind.upper-R", "hind.lower-R", "hind.foot-R", "hind.toe-R",
)


def source_maps():
    return {p.name[:-5]: json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(files(__package__).joinpath("maps").iterdir(), key=lambda p: p.name)
            if p.name.endswith(".json")}


def _plain_map():
    result = {"hips": ("spine", "hips"), "spine.01": ("spine.001",),
              "spine.02": ("spine.002",), "chest": ("spine.003", "chest"),
              "neck": ("neck", "spine.004"), "head": ("head", "spine.006", "spine.005")}
    for side in ("L", "R"):
        for role, bone in (("clavicle", "shoulder"), ("upperarm", "upper_arm"),
                           ("forearm", "forearm"), ("hand", "hand"),
                           ("thigh", "thigh"), ("shin", "shin"), ("foot", "foot")):
            result[f"{role}.fk-{side}"] = (f"{bone}.{side}",)
    return result


def _resolve(names, aliases):
    # Exact matches only. Never confuse shoulder with arm or left with right.
    return {role: next(name for name in options if name in names)
            for role, options in aliases.items() if any(name in names for name in options)}


def _quadruped_profile(names):
    """Return an explicit Rigify quadruped profile, or None.

    The signatures are deliberately structural and precede humanoid Rigify
    detection. Generated horse controls overlap humanoid control names, so a
    humanoid-first check can silently select the wrong anatomy.
    """
    generated_wolf = {"torso", "front_thigh_fk.L", "front_thigh_fk.R",
                      "thigh_fk.L", "thigh_fk.R"} <= names
    generated_horse = {"torso", "upper_arm_fk.L", "upper_arm_fk.R",
                       "lower_leg_fk.L", "lower_leg_fk.R",
                       "hind_foot_fk.L", "hind_foot_fk.R"} <= names
    # The current cat template shares the horse forelimb convention and the
    # wolf hindlimb convention. Keep it distinct when its generated hand/foot
    # controls are present.
    generated_cat = {"torso", "upper_arm_fk.L", "upper_arm_fk.R",
                     "hand_fk.L", "hand_fk.R", "f_toe.L", "f_toe.R",
                     "shin_fk.L", "shin_fk.R", "foot_fk.L", "foot_fk.R",
                     "r_toe.L", "r_toe.R"} <= names
    metarig_wolf = {"front_thigh.L", "front_thigh.R", "front_shin.L",
                    "front_shin.R", "thigh.L", "thigh.R", "shin.L", "shin.R"} <= names
    metarig_horse = {"upper_arm.L", "upper_arm.R", "forefoot.L", "forefoot.R",
                     "lower_leg.L", "lower_leg.R", "hind_foot.L", "hind_foot.R"} <= names
    metarig_cat = {"upper_arm.L", "upper_arm.R", "hand.L", "hand.R",
                   "f_toe.L", "f_toe.R", "shin.L", "shin.R",
                   "foot.L", "foot.R", "r_toe.L", "r_toe.R",
                   "face", "tail.001", "pelvis.C"} <= names
    if not any((generated_wolf, generated_horse, generated_cat,
                metarig_wolf, metarig_horse, metarig_cat)):
        return None

    generated = generated_wolf or generated_horse or generated_cat
    if generated_wolf:
        label = "Rigify Generated Quadruped (Wolf)"
        fore = ("front_thigh_fk", "front_shin_fk", "front_foot_fk", "front_toe")
        hind = ("thigh_fk", "shin_fk", "foot_fk", "toe")
    elif generated_horse:
        label = "Rigify Generated Quadruped (Horse)"
        fore = ("upper_arm_fk", "forearm_fk", "forefoot_fk", "f_toe_fk")
        hind = ("thigh_fk", "lower_leg_fk", "hind_foot_fk", "r_toe_fk")
    elif generated_cat:
        label = "Rigify Generated Quadruped (Cat)"
        fore = ("upper_arm_fk", "forearm_fk", "hand_fk", "f_toe")
        hind = ("thigh_fk", "shin_fk", "foot_fk", "r_toe")
    elif metarig_wolf:
        label = "Rigify Quadruped Metarig (Wolf)"
        fore = ("front_thigh", "front_shin", "front_foot", "front_toe")
        hind = ("thigh", "shin", "foot", "toe")
    elif metarig_horse:
        label = "Rigify Quadruped Metarig (Horse)"
        fore = ("upper_arm", "forearm", "forefoot", "f_toe")
        hind = ("thigh", "lower_leg", "hind_foot", "r_toe")
    else:
        label = "Rigify Quadruped Metarig (Cat)"
        fore = ("upper_arm", "forearm", "hand", "f_toe")
        hind = ("thigh", "shin", "foot", "r_toe")

    aliases = {
        "pelvis": ("hips", "torso", "spine", "spine.001", "spine.004"),
        "chest": ("chest", "spine.006", "spine.005", "spine.008"),
        "neck": ("neck", "neck.001", "spine.009"),
        "head": ("head", "face", "spine.011", "spine.006"),
    }
    for side in ("L", "R"):
        for role, bone in zip(("upper", "lower", "foot", "toe"), fore):
            aliases[f"fore.{role}-{side}"] = (f"{bone}.{side}",)
        for role, bone in zip(("upper", "lower", "foot", "toe"), hind):
            aliases[f"hind.{role}-{side}"] = (f"{bone}.{side}",)
    roles = _resolve(names, aliases)
    controls = set(roles.values())
    controls |= names & {"root", "torso", "hips", "chest", "neck", "head"}
    controls |= {name for name in names
                 if (name.startswith(("spine_fk", "tail.")) or name.startswith("tail_master"))
                 and not name.startswith(("DEF-", "MCH-", "ORG-"))}
    if generated:
        # Add recognized animator-facing IK controls while excluding generated
        # mechanisms, visual widgets and tweak/deform chains.
        for side in ("L", "R"):
            if generated_wolf:
                stems = ("front_foot_ik", "front_foot_heel_ik", "front_thigh_ik_target",
                         "foot_ik", "foot_heel_ik", "thigh_ik_target")
            elif generated_cat:
                stems = ("hand_ik", "hand_heel_ik", "upper_arm_ik_target",
                         "foot_ik", "foot_heel_ik", "thigh_ik_target")
            else:
                stems = ("forefoot_ik", "forefoot_heel_ik", "upper_arm_ik_target",
                         "hind_foot_ik", "hind_foot_heel_ik", "thigh_ik_target")
            controls |= names & {f"{stem}.{side}" for stem in stems}
    missing = tuple(role for role in QUADRUPED_REQUIRED if role not in roles)
    warning = ("Quadruped capture, interpolation, bounded whole-body posing and authored "
               "four-paw contacts are available; flight and learned gait remain unavailable.",)
    return RigProfile(label, roles, tuple(sorted(controls)), missing, warning,
                      family="quadruped", schema="quadruped_v1")


def detect_rig(bone_names):
    names = set(bone_names)
    warnings = []
    maps = source_maps()
    target_names = {v for data in maps.values() for v in data["bones"].values()}
    quadruped = _quadruped_profile(names)
    if quadruped is not None:
        return quadruped
    if {"hips", "upperarm.fk-L", "thigh.fk-R"} <= names:
        label = "BoneForge Control Rig"
        roles = {n: n for n in target_names if n in names}
        controls = {n for n in names if n in target_names or
                    (n.endswith(("-L", "-R")) and any(t in n for t in (".fk-", ".ik-", ".pole-", ".roll-")))}
        controls |= names & {"root"}
    elif {"torso", "upper_arm_fk.L", "thigh_fk.R"} <= names:
        label = "Rigify Generated"
        aliases = {"hips": ("hips", "torso"), "head": ("head",), "neck": ("neck",),
                   "chest": ("chest",), "spine.01": ("spine_fk",),
                   "spine.02": ("spine_fk.001",)}
        for side in ("L", "R"):
            for role, bone in (("clavicle", "shoulder"), ("upperarm", "upper_arm_fk"),
                               ("forearm", "forearm_fk"), ("hand", "hand_fk"),
                               ("thigh", "thigh_fk"), ("shin", "shin_fk"), ("foot", "foot_fk")):
                aliases[f"{role}.fk-{side}"] = (f"{bone}.{side}",)
        roles = _resolve(names, aliases)
        controls = set(roles.values()) | (names & {"root", "torso", "spine_fk.002", "spine_fk.003"})
        for side in ("L", "R"):
            controls |= names & {f"{part}.{side}" for part in
                                 ("hand_ik", "foot_ik", "upper_arm_ik_target", "thigh_ik_target", "foot_heel_ik")}
        warnings.append("IK/FK switches and parent spaces must stay constant between anchors.")
    else:
        candidates = []
        for key, data in maps.items():
            roles = {target: source for source, target in data["bones"].items() if source in names}
            candidates.append((len(roles), data["name"], roles))
        aliases = _plain_map()
        roles = _resolve(names, aliases)
        candidates.append((len(roles), "BoneForge Legacy / Rigify Metarig", roles))
        vroid = {"hips": ("J_Bip_C_Hips",), "spine.01": ("J_Bip_C_Spine",),
                 "chest": ("J_Bip_C_Chest",), "neck": ("J_Bip_C_Neck",), "head": ("J_Bip_C_Head",)}
        mmd = {"hips": ("\u4e0b\u534a\u8eab", "Lower Body", "\u30bb\u30f3\u30bf\u30fc", "Center"),
               "spine.01": ("\u4e0a\u534a\u8eab", "Upper Body"), "chest": ("\u4e0a\u534a\u8eab2", "Upper Body 2"),
               "neck": ("\u9996", "Neck"), "head": ("\u982d", "Head")}
        for side, english, japanese in (("L", "Left", "\u5de6"), ("R", "Right", "\u53f3")):
            for role, vr, jp, en in (("upperarm", "UpperArm", "\u8155", "Arm"),
                                    ("forearm", "LowerArm", "\u3072\u3058", "Elbow"),
                                    ("hand", "Hand", "\u624b\u9996", "Wrist"),
                                    ("thigh", "UpperLeg", "\u8db3", "Leg"),
                                    ("shin", "LowerLeg", "\u3072\u3056", "Knee"),
                                    ("foot", "Foot", "\u8db3\u9996", "Ankle")):
                vroid[f"{role}.fk-{side}"] = (f"J_Bip_{side}_{vr}",)
                mmd[f"{role}.fk-{side}"] = (japanese + jp, english + " " + en)
        for label, aliases in (("VRoid / VRM", vroid), ("MMD", mmd)):
            roles = _resolve(names, aliases)
            candidates.append((len(roles), label, roles))
        count, label, roles = max(candidates, key=lambda item: item[0])
        if count < 6:
            return RigProfile("Unrecognized", {}, (), REQUIRED,
                              ("Use selected editable controls; automatic rig mapping needs review.",),
                              family="unknown", schema="unmapped")
        controls = set(roles.values())
        if label == "Rigify Deform":
            controls = set()
            warnings.append("Deform-only Rigify skeleton detected. Use a generated control rig for writing.")
    if label == "BoneForge Legacy / Rigify Metarig" and "spine.006" in names:
        controls |= names & {"spine.005"}
    missing = tuple(role for role in REQUIRED if role not in roles)
    return RigProfile(label, roles, tuple(sorted(controls)), missing, tuple(warnings))
