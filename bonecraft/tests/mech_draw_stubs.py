# bonecraft/tests/mech_draw_stubs.py
"""Draw stubs shared by the Mechanisms host tests (a helper module, not a test: no run())."""
import bpy


class Rec:
    """Records what a panel draw asks for: (call, args, keywords), and ("set", name, value) for each attribute set."""
    def __init__(self, log):
        self.__dict__["log"] = log

    def __getattr__(self, name):
        def call(*a, **k):
            self.log.append((name, a, k))
            return Rec(self.log)
        return call

    def __setattr__(self, name, value):
        self.log.append(("set", name, value))


class _Prefs:
    def __init__(self, tab, helpers):
        self.show_tab_boneforge, self.show_helpers = tab, helpers

    def __getattr__(self, name):
        return True


class Ctx:
    """bpy.context with the add-on's preferences stubbed (the test host has no 'boneforge' add-on entry).

    ``tab`` and ``helpers`` set show_tab_boneforge and show_helpers; every other preference is True."""
    def __init__(self, tab=True, helpers=True):
        prefs = _Prefs(tab, helpers)
        self.preferences = type("P", (), {"addons": {"boneforge": type("A", (), {"preferences": prefs})()}})()

    def __getattr__(self, name):
        return getattr(bpy.context, name)
