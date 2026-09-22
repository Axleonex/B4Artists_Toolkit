"""B4Artists Machine Learning: independent, local animation assistance.

SPDX-License-Identifier: GPL-2.0-or-later
"""
bl_info = {
    "name": "B4Artists Machine Learning",
    "author": "axlbot",
    "version": (0, 38, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > B4Artists ML",
    "description": "Standalone local procedural animation assistance (public beta).",
    "category": "Animation",
}
_registered = False
_stub = None


def is_bforartists(app=None):
    if app is None:
        import bpy
        app = bpy.app
    branch = getattr(app, "build_branch", b"")
    if isinstance(branch, bytes):
        branch = branch.decode("utf-8", errors="replace")
    return bool(getattr(app, "bforartists", False) or
                str(branch).lower().startswith("bfa") or
                "bforartists" in getattr(app, "binary_path", "").lower() or
                "bforartists" in getattr(app, "version_string", "").lower())


def register():
    global _registered, _stub
    import bpy
    if _registered or _stub is not None:
        return
    if not is_bforartists():
        class B4ML_AP_unsupported(bpy.types.AddonPreferences):
            bl_idname = __name__

            def draw(self, context):
                self.layout.label(text="B4Artists Machine Learning requires Bforartists.", icon='ERROR')
                self.layout.operator("wm.url_open", text="Get Bforartists").url = "https://www.bforartists.de"
        bpy.utils.register_class(B4ML_AP_unsupported)
        _stub = B4ML_AP_unsupported
        return
    from . import ui
    ui.register()
    _registered = True


def unregister():
    global _registered, _stub
    import bpy
    if _stub is not None:
        bpy.utils.unregister_class(_stub)
        _stub = None
    if _registered:
        from . import ui
        ui.unregister()
        _registered = False
