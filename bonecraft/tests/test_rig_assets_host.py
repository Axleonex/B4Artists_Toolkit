"""In-Bforartists test: library registration and the BoneCraft Rigs shelf."""
import os
import tempfile

import bpy

import boneforge


def _libs():
    return bpy.context.preferences.filepaths.asset_libraries


def _entries():
    return [(l.name, l.path) for l in _libs()]


def run():
    from boneforge.autorig import rig_assets as ra
    boneforge.register()
    try:
        assert ra.ours(_entries(), ra.assets_dir()) == [ra.LIB_NAME], _entries()
        assert hasattr(bpy.types, ra.SHELF_IDNAME), "shelf not registered"
        ra.register_library()                                   # idempotent
        assert [n for n, _ in _entries()].count(ra.LIB_NAME) == 1, _entries()
    finally:
        boneforge.unregister()
    assert ra.ours(_entries(), ra.assets_dir()) == [], "library left after unregister"
    assert not hasattr(bpy.types, ra.SHELF_IDNAME)

    # Review Focus 4: the user's own "BoneCraft Rigs" is never touched
    other = tempfile.mkdtemp()
    user_lib = _libs().new(name=ra.LIB_NAME, directory=other)
    user_path = user_lib.path
    try:
        boneforge.register()
        try:
            assert (ra.LIB_NAME, user_path) in _entries(), _entries()
            assert ra.ours(_entries(), ra.assets_dir()) == [ra.LIB_FALLBACK_NAME], _entries()
        finally:
            boneforge.unregister()
        names = [n for n, _ in _entries()]
        assert ra.LIB_NAME in names and ra.LIB_FALLBACK_NAME not in names, names
    finally:
        for lib in list(_libs()):
            if lib.name == ra.LIB_NAME and lib.path == user_path:
                _libs().remove(lib)
        os.rmdir(other)
    # Review finding: a matching entry (same name AND folder) that existed before
    # BoneCraft was enabled was not added by BoneCraft, so disabling keeps it.
    pre = _libs().new(name=ra.LIB_NAME, directory=ra.assets_dir())
    pre_entry = (pre.name, pre.path)
    try:
        boneforge.register()
        try:
            assert [n for n, _ in _entries()].count(ra.LIB_NAME) == 1, _entries()
        finally:
            boneforge.unregister()
        assert pre_entry in _entries(), ("pre-existing entry removed on disable", _entries())
    finally:
        for lib in list(_libs()):
            if (lib.name, lib.path) == pre_entry:
                _libs().remove(lib)
    print("PASS rig assets: library add/remove, shelf, user library untouched")
