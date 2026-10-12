"""In-Bforartists layout test: Import / Export lives on the CATS tab.

Registers the whole add-on, then checks the registered panel classes:

* the Import / Export hub (``BF_PT_sb_io``) is a CATS-tab section placed
  after the VRChat section, closed by default;
* every child panel of the hub is on the CATS tab too (a child left on
  another tab would draw nowhere);
* negative control: no BoneCraft-tab panel is visible-and-top-level as
  Import / Export any more.
"""
import bpy

import boneforge

_IO_CHILDREN = ("BONEFORGE_PT_profile_export", "BONEFORGE_PT_vrm", "BONEFORGE_PT_mmd")


def _registered(name):
    cls = getattr(bpy.types, name, None)
    assert cls is not None, "panel not registered: %s" % name
    return cls


def run():
    boneforge.register()
    try:
        io = _registered("BF_PT_sb_io")
        assert io.bl_category == "CATS", io.bl_category
        assert "DEFAULT_CLOSED" in getattr(io, "bl_options", set())
        vrchat = _registered("BF_PT_sb_vrchat")
        assert io.bl_order > vrchat.bl_order, (io.bl_order, vrchat.bl_order)

        for name in _IO_CHILDREN:
            child = _registered(name)
            assert child.bl_parent_id == "BF_PT_sb_io", (name, child.bl_parent_id)
            assert child.bl_category == "CATS", (name, child.bl_category)

        bone_tab_io = [
            cls.__name__ for cls in bpy.types.Panel.__subclasses__()
            if getattr(cls, "bl_category", "") == "BoneCraft"
            and getattr(cls, "bl_parent_id", "") in ("", "BF_PT_sb_io")
            and cls.__name__ in ("BF_PT_sb_io",) + _IO_CHILDREN
        ]
        assert bone_tab_io == [], bone_tab_io
    finally:
        boneforge.unregister()
    print("PASS sidebar layout: Import / Export is a CATS-tab section")


if __name__ == "__main__":
    run()
