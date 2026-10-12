# bonecraft/tests/test_action_first_host.py
"""In-Bforartists test: a panel shows its action first and its settings in a fold below it
(UI critique, 2026-10-10: act first, tune later; operators set apart from their properties).

What the action works on (a driver mesh, the text to lip-sync) stays above the action: you pick it first.
"""
import bpy

import boneforge
from mech_draw_stubs import Ctx, Rec


class FoldRec(Rec):
    """A recording layout whose folds open: what is drawn inside a fold is logged to ``fold``."""

    def __init__(self, log, fold):
        super().__init__(log)
        self.__dict__["fold"] = fold

    def __getattr__(self, name):
        if name == "panel":
            def panel(*a, **k):
                self.log.append(("panel", a, k))
                return Rec(self.log), FoldRec(self.fold, self.fold)
            return panel

        def call(*a, **k):
            self.log.append((name, a, k))
            return FoldRec(self.log, self.fold)
        return call


class Shim:
    def __init__(self):
        self.main, self.fold = [], []
        self.layout = FoldRec(self.main, self.fold)


def _draw(idname):
    shim = Shim()
    getattr(bpy.types, idname).draw(shim, Ctx())
    return shim


def _props(log):
    return {a[1] for n, a, k in log if n == "prop" and len(a) >= 2}


def _ops(log):
    return [a[0] for n, a, k in log if n == "operator" and a]


def _check(idname, action, tuning, inputs=()):
    shim = _draw(idname)
    assert action in _ops(shim.main), (idname, "the action is drawn first, outside the fold", _ops(shim.main))
    early = _props(shim.main) & set(tuning)
    assert not early, (idname, "settings drawn beside the action instead of folded below it", early)
    assert set(tuning) <= _props(shim.fold), (idname, "settings in the fold", _props(shim.fold))
    assert set(inputs) <= _props(shim.main), (idname, "what it acts on stays above", _props(shim.main))
    first_op = next(i for i, (n, a, k) in enumerate(shim.main) if n == "operator")
    folds = [i for i, (n, a, k) in enumerate(shim.main) if n == "panel"]
    assert folds and folds[0] > first_op, (idname, "the fold comes after the action")


def run():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    boneforge.register()
    try:
        ctx = bpy.context
        mesh = bpy.data.objects.new("bc_af_mesh", bpy.data.meshes.new("bc_af_mesh"))
        ctx.scene.collection.objects.link(mesh)
        ctx.view_layer.objects.active = mesh
        # Delta Mush: add it, tune it after (the operator's own options); Proximity Wrap: pick the driver,
        # bind, then tune falloff and distance
        shim = _draw("BONEFORGE_PT_p2b_delta_mush")
        assert "boneforge.add_delta_mush" in _ops(shim.main), _ops(shim.main)
        assert not _props(shim.main), ("Delta Mush asks for nothing before adding", _props(shim.main))
        overridden = {a for n, a, v in shim.main if n == "set"} & {"iterations", "smooth_strength", "pin_borders",
                                                                   "only_smooth_deform"}
        assert not overridden, ("the button does not override the last-used options", overridden)
        _check("BONEFORGE_PT_p2b_proximity_wrap", "boneforge.bind_proximity_wrap",
               ("falloff_type", "max_distance"), inputs=("driver_mesh",))
        # Chain Dynamics, Lip Sync: on an armature
        arm = bpy.data.objects.new("bc_af_rig", bpy.data.armatures.new("bc_af_rig"))
        ctx.scene.collection.objects.link(arm)
        ctx.view_layer.objects.active = arm
        _check("BONEFORGE_PT_p2c_chain_dynamics", "boneforge.add_chain_dynamics",
               ("stiffness", "damping", "mass", "gravity_scale"))
        _check("BONEFORGE_PT_p2c_lip_sync", "boneforge.generate_lip_sync",
               ("frames_per_phoneme", "smooth"), inputs=("text",))
        # Delta Mover, Smart Bake
        _check("BONEFORGE_PT_delta_mover", "boneforge.delta_move",
               ("offset_x", "offset_y", "world_units", "uniform"))
        _check("BONEFORGE_PT_buffer_bake", "boneforge.smart_bake", ("smart_bake_tolerance",))
        # CATS: which shapes / which meshes come first; how to treat existing ones is folded below
        _check("CATS_PT_visemes", "boneforge.cats_generate_visemes", ("overwrite_existing",),
               inputs=("a_shape", "o_shape", "ch_shape"))
        ctx.scene.boneforge_vrc_join_meshes_settings.meshes.add().name = "bc_af_mesh"
        _check("CATS_PT_join_meshes", "boneforge.vrc_join_meshes", ("shape_key_conflict_mode",),
               inputs=("include",))
        # Mannequin (Rig Builder): its buttons first, mode / body / density folded below them
        ctx.view_layer.objects.active = arm
        _check("BF_PT_rb_mannequin", "boneforge.quick_mannequin",
               ("boneforge_mannequin_mode", "boneforge_mannequin_body_type", "boneforge_mannequin_density"))
        # the optimizer's four toggles fed nothing: they are gone, the four fixes remain
        shim = _draw("BONEFORGE_PT_vrc_optimizer")
        dead = {"remove_zero_weight_bones", "merge_same_material_meshes", "remove_unused_shape_keys",
                "remove_unused_vertex_groups"}
        assert not _props(shim.main) & dead, _props(shim.main) & dead
        assert {"boneforge.vrc_remove_zero_weight_bones", "boneforge.vrc_remove_unused_vertex_groups"} <= \
            set(_ops(shim.main)), _ops(shim.main)
    finally:
        boneforge.unregister()
    print("PASS action first: panels show the action, then their settings in a fold")
