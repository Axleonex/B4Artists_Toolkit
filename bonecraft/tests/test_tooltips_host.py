# bonecraft/tests/test_tooltips_host.py
"""In-Bforartists test: every BoneCraft operator explains itself (UI critique, 2026-10-10).

- Its tooltip says, in the user's words, what it does: no version notes, internal names or code
  paths, at most three lines.
- Every option shown in Adjust Last Operation or a dialog has a tooltip of its own; what a button
  fills in (which item, which slot) is hidden there instead. Standard file-browser fields are exempt.

Every operator of the add-on is checked.
"""
import re

import bpy

import boneforge

DEV = re.compile(r"\bv\d+\.\d|\(internal\)|bpy\.ops|TODO|registration purposes|``|code path|operator IDs|"
                 r"\b[a-z]+_[a-z_]+\(\)")
FILE_FIELDS = {"filepath", "filename", "directory", "files", "filter_glob", "check_existing", "hide_props_region"}


def _operators():
    for name in dir(bpy.ops.boneforge):
        rna = getattr(bpy.ops.boneforge, name).get_rna_type()
        cls = getattr(bpy.types, rna.identifier, None)
        if cls is not None:
            yield f"boneforge.{name}", rna, cls


def run():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    boneforge.register()
    try:
        bad_text, bad_props, count = [], [], 0
        for idname, rna, cls in _operators():
            count += 1
            desc = rna.description or ""
            if not desc or DEV.search(desc) or desc.count("\n") >= 3 or len(desc) > 320:
                bad_text.append((idname, desc[:90]))
            for p in rna.properties:
                if p.identifier == "rna_type" or p.is_hidden or p.identifier in FILE_FIELDS:
                    continue
                if not p.description:
                    bad_props.append((idname, p.identifier))
        assert count > 300, ("the add-on's operators were not found", count)
        assert not bad_text, ("tooltips that do not speak to the user", bad_text)
        assert not bad_props, ("options with no tooltip (or a button's input that should be hidden)", bad_props)
    finally:
        boneforge.unregister()
    print(f"PASS tooltips: all {count} BoneCraft operators explain themselves and their options")
