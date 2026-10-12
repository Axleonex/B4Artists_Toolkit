# bonecraft/tests/test_icon_meaning_host.py
"""In-Bforartists test: every BoneCraft icon keeps one meaning (b4artists-ui-ux R7; Blender HIG, Icons).

1. Tool Shelf buttons show only their icon in a narrow shelf, so no two shelf buttons share one, and a
   shelf icon is not reused for another action unless MEANINGS names what it means.
2. Operators: one operator shows one icon everywhere (except the few in MANY_ICON_OPERATORS, whose
   buttons pass different settings), and an icon on buttons of different operators must have one
   meaning written in MEANINGS.
3. Labels: a label with fixed wording (a heading or a message) carries no icon or a status icon.
   Only a label that shows a name (a bone, an armature, a mesh) keeps that thing's type icon.
The scan reads the source through the AST, as test_ui_icons_host does.
"""
import ast
import collections
import os

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "boneforge")

# Icons a label may carry next to fixed wording: they report a state, not a topic.
STATUS = {"INFO", "ERROR", "WARNING", "CHECKMARK", "QUESTION", "CANCEL", "RADIOBUT_OFF", "RADIOBUT_ON",
          "LOCKED", "UNLOCKED", "BLANK1", "NONE", "REC", "DOT", "LAYER_USED", "LAYER_ACTIVE"}

# Icons shown on buttons of several operators, with the one meaning they share.
MEANINGS = {
    "ADD": "add or create something",
    "REMOVE": "remove from a list, or make smaller",
    "X": "remove, delete or clear one item",
    "TRASH": "delete data or clean up",
    "CHECKMARK": "confirm, accept or validate",
    "FILE_REFRESH": "refresh, rebuild or run again",
    "VIEWZOOM": "analyze, inspect or detect",
    "EXPORT": "export",
    "IMPORT": "import",
    "URL": "open a web page",
    "PREFERENCES": "open the add-on preferences",
    "PLAY": "play or test motion",
    "PLUGIN": "install or enable an add-on",
    "AUTO": "match or enhance automatically",
    "SHADERFX": "guess from the mesh",
    "AUTOMERGE_ON": "merge bones or armatures",
    "JOIN": "join meshes",
    "SORTALPHA": "fix or convert names",
    "RENAME": "rename",
    "COPYDOWN": "copy",
    "FILE_FOLDER": "browse for a file",
    "FILE_TICK": "save",
    "FORWARD": "go to the next step",
    "LOOP_BACK": "reset or revert",
    "MOD_MIRROR": "mirror",
    "REC": "capture",
    "TRIA_UP": "move up",
    "TRIA_DOWN": "move down",
    "PINNED": "bind or protect",
    "PHYSICS": "add jiggle physics",
    "SHAPEKEY_DATA": "work on shape keys",
    "HIDE_OFF": "show or preview",
    "RESTRICT_SELECT_OFF": "select",
    "OUTLINER_OB_ARMATURE": "add a rig",
    "OUTLINER_OB_MESH": "add a mannequin",
    "APPLYALL": "apply transforms",
    "POSE_HLT": "apply or load a pose",
    "PIVOT_CURSOR": "set a part's pivot",
    "MODIFIER": "fix a model",
    "SPEAKER": "lip sync and visemes",
    "TAG": "tag or sort into a category",
    "WINDOW": "open a window",
    "GROUP_BONE": "bone collections and picker groups",
}

# Operators whose buttons pass different settings, each with its own icon.
MANY_ICON_OPERATORS = {"boneforge.picker_resize_control", "boneforge.vrc_detect_convention",
                       "boneforge.tangent_set_type"}


def _fixed_wording(text):
    """True when a label's text is fixed wording, False when it is a name (or no text at all)."""
    if isinstance(text, ast.Constant):
        return bool(text.value)
    if isinstance(text, ast.JoinedStr):
        return any(isinstance(v, ast.Constant) and any(c.isalpha() for c in v.value) for v in text.values)
    if isinstance(text, ast.Call) and isinstance(text.func, ast.Name) and text.func.id == "T":
        return True
    return isinstance(text, ast.BinOp)


def scan(source, where):
    """(operator uses, label offences) in ``source``: [(idname, icon, where:line)], [(where:line, icon)]."""
    ops, labels = [], []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        kw = next((k for k in node.keywords if k.arg == "icon"), None)
        if kw is None or not isinstance(kw.value, ast.Constant):
            continue
        icon, at = kw.value.value, f"{where}:{node.lineno}"
        name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", None)
        if name == "operator" and node.args and isinstance(node.args[0], ast.Constant):
            ops.append((node.args[0].value, icon, at))
        elif name in ("label", "draw_wrapped") and icon not in STATUS:
            if name == "label":
                text = next((k.value for k in node.keywords if k.arg == "text"), node.args[0] if node.args else None)
            else:
                text = node.args[2] if len(node.args) > 2 else next(
                    (k.value for k in node.keywords if k.arg == "text"), None)
            if _fixed_wording(text):
                labels.append((at, icon))
    return ops, labels


def scan_tree(root=None):
    root = root or ROOT
    ops, labels = [], []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ("__pycache__", "i18n")]
        for fn in filenames:
            if fn.endswith(".py"):
                path = os.path.join(dirpath, fn)
                with open(path, encoding="utf-8") as fh:
                    o, lab = scan(fh.read(), os.path.relpath(path, root).replace("\\", "/"))
                ops += o
                labels += lab
    return ops, labels


def shared_without_meaning(ops):
    """{icon: [operators]} for icons on several operators that MEANINGS does not explain."""
    by_icon = collections.defaultdict(set)
    for idname, icon, _ in ops:
        by_icon[icon].add(idname)
    return {i: sorted(o) for i, o in by_icon.items() if len(o) > 1 and i not in MEANINGS}


def operators_with_many_icons(ops):
    by_op = collections.defaultdict(set)
    for idname, icon, at in ops:
        by_op[idname].add(icon)
    return {o: sorted(i) for o, i in by_op.items() if len(i) > 1 and o not in MANY_ICON_OPERATORS}


def run():
    # the scanner itself
    sample = ('row.label(text=T("Bones"), icon="BONE_DATA")\n'
              'row.label(text=bone.name, icon="BONE_DATA")\n'
              'row.label(text=f"Deform ({n})", icon="BONE_DATA")\n'
              'row.label(text=f"  {c.name}", icon="SPHERE")\n'
              'row.label(text="Done", icon="CHECKMARK")\n'
              'draw_wrapped(col, context, T("Quick Wins"), icon="SOLO_ON")\n'
              'row.operator("boneforge.a", icon="ADD")\n')
    ops, labels = scan(sample, "s")
    assert labels == [("s:1", "BONE_DATA"), ("s:3", "BONE_DATA"), ("s:6", "SOLO_ON")], labels
    assert ops == [("boneforge.a", "ADD", "s:7")], ops
    assert shared_without_meaning([("a", "GRAPH", ""), ("b", "GRAPH", "")]) == {"GRAPH": ["a", "b"]}

    import bpy
    valid = set(bpy.types.UILayout.bl_rna.functions["label"].parameters["icon"].enum_items.keys())
    assert set(MEANINGS) <= valid and STATUS <= valid, sorted((set(MEANINGS) | STATUS) - valid)

    ops, labels = scan_tree()
    assert labels == [], "labels with fixed wording and a topic icon: %s" % labels
    assert shared_without_meaning(ops) == {}, shared_without_meaning(ops)
    assert operators_with_many_icons(ops) == {}, operators_with_many_icons(ops)

    # Tool Shelf: unique icons; a shelf icon elsewhere only on the same operator or with a written meaning
    from boneforge.core import access
    entries = [e for group in (access.POSE_ENTRIES, access.WEIGHT_ENTRIES, access.CHECK_ENTRIES)
               for e in group if e]
    icons = [e[2] for e in entries]
    assert len(icons) == len(set(icons)), sorted(i for i in icons if icons.count(i) > 1)
    owner = {e[2]: e[0] for e in entries}
    stray = [(at, icon, idname) for idname, icon, at in ops
             if icon in owner and idname != owner[icon] and icon not in MEANINGS]
    assert stray == [], "shelf icons reused for another action: %s" % stray
    print("PASS icon meaning: shelf icons unique, one icon per operator, shared icons have one written "
          "meaning, no topic icons on fixed-wording labels")
