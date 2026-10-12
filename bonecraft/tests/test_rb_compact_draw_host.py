"""In-Bforartists test: Rig Builder's real draw code under CompactLayout.

Draws Quick Rig, the wizard start screen and Mannequin into a recording
layout through the compact path: rows are stacked as columns, and every
label and info line is drawn in full (show, don't hide - it wraps instead;
owner, 2026-10-10).
"""
import bpy

import boneforge


class Rec:
    def __init__(self, log):
        self.__dict__["log"] = log
    def __getattr__(self, name):
        def call(*a, **k):
            self.log.append((name, a, k))
            return Rec(self.log)
        return call
    def __setattr__(self, name, value):
        self.log.append(("set", name, value))


class FakePanel:
    def __init__(self, layout):
        self.layout = layout


def run():
    boneforge.register()
    try:
        from boneforge.taskboard import sidebar
        from boneforge.autorig.compact_layout import CompactLayout
        from boneforge.autorig.wizard import BF_PT_WizardPanel
        from boneforge.autorig.mannequin import BF_PT_MannequinPanel
        log = []
        shim = sidebar._CompactPanel(FakePanel(Rec(log)), CompactLayout(Rec(log)))
        sidebar.BF_PT_sb_quick_rig._draw_quick_rig(shim, bpy.context)
        BF_PT_WizardPanel.draw(shim, bpy.context)
        BF_PT_MannequinPanel.draw(shim, bpy.context)
        texts = [k.get("text") for name, a, k in log
                 if name in ("label", "operator", "prop") and isinstance(k, dict) and k.get("text")]
        assert texts, "nothing was drawn"
        assert any(t.startswith("BoneCraft Basic Humanoid") for t in texts), ("full names, not shortened", texts)
        infos = [k for name, a, k in log
                 if name == "label" and isinstance(k, dict) and k.get("icon") == "INFO"]
        assert infos, ("info lines are shown in compact mode too", texts)
        assert not [x for x in log if x[0] in ("row", "split")], "rows and splits are stacked as columns"

        # rb_draw_target picks the compact path from the region width
        class Region:
            def __init__(self, width):
                self.width = width

        class System:
            ui_scale = 1.0

        class Prefs:
            system = System()

        class Ctx:
            def __init__(self, region):
                self.region = region
                self.preferences = Prefs()

        panel = FakePanel(Rec([]))
        narrow = sidebar.rb_draw_target(panel, Ctx(Region(100)))
        assert isinstance(narrow, sidebar._CompactPanel), narrow
        assert isinstance(narrow.layout, CompactLayout)
        assert sidebar.rb_draw_target(panel, Ctx(Region(400))) is panel
        assert sidebar.rb_draw_target(panel, Ctx(None)) is panel
        System.ui_scale = 2.0
        assert isinstance(sidebar.rb_draw_target(panel, Ctx(Region(400))), sidebar._CompactPanel)
    finally:
        boneforge.unregister()
    print("PASS compact draw: Quick Rig, wizard start, Mannequin")
