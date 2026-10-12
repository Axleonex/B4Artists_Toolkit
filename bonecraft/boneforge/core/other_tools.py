"""Collapsed group headers for the BoneCraft tab's stray root panels (spec M6).

The tab's curated sections are Overview, Setup Rigging, Skin, Mechanisms and
Review. Every other parentless panel in the BoneCraft category is adopted
under a collapsed group header, so the curated order is what a user scrolls:

- the VRChat utilities (``BONEFORGE_PT_vrc_*``) are left alone: they are
  hidden panels (their poll is False) that the CATS tab's "VRChat Tools"
  section (``taskboard/sidebar.py``) draws, in the owner's order;
- everything else (Bone Merge, the weight utilities, whatever an enabled tool
  package adds) goes to an "Other Tools" header in the BoneCraft tab.

Nothing is hidden: every adopted panel keeps its id, poll and draw, one click
away, and its sub-panels move with it.

``adopt`` runs after registration and again after a tool toggle (a package
switched on registers fresh root panels). It is idempotent, and on any
failure it puts the panel back as it was so no tool ever disappears.
"""
import logging

import bpy
from bpy.types import Panel

from boneforge.i18n import T

logger = logging.getLogger(__name__)

CURATED = ("BF_PT_sb_overview", "BF_PT_sb_setup", "BF_PT_sb_skin", "BF_PT_mech",
           "BF_PT_sb_animate", "BF_PT_sb_other")
VRC_PREFIX = "BONEFORGE_PT_vrc_"

_ADOPTED = []                            # (class, parent id, region, options, category) as they were
_KID_REGIONS = []                        # (descendant class, region, category) as they were


def _pref(context, name):
    try:
        return bool(getattr(context.preferences.addons["boneforge"].preferences, name))
    except (AttributeError, KeyError):
        return True


def _adopted_into(parent_id):
    """True while at least one panel adopted under ``parent_id`` is still registered (a switched-off tool's are not)."""
    return any(cls.bl_parent_id == parent_id and getattr(cls, "is_registered", False) for cls, *_rest in _ADOPTED)


class BF_PT_sb_other(Panel):
    bl_label = " "
    bl_idname = "BF_PT_sb_other"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BoneCraft'
    bl_order = 45
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return _adopted_into(cls.bl_idname) and _pref(context, "show_tab_boneforge")

    def draw_header(self, context):
        self.layout.label(text=T("Other Tools"))

    def draw(self, context):
        pass                                             # only its children draw


HEADERS = (BF_PT_sb_other,)


def _strays():
    """Parentless registered BoneCraft viewport panels outside the curated sections."""
    return [c for c in bpy.types.Panel.__subclasses__()
            if getattr(c, "is_registered", False)
            and getattr(c, "bl_space_type", "") == 'VIEW_3D'
            and getattr(c, "bl_category", "") == 'BoneCraft'
            and not getattr(c, "bl_parent_id", "")
            and getattr(c, "bl_idname", "") not in CURATED
            and not getattr(c, "bl_idname", "").startswith(VRC_PREFIX)]   # drawn by the VRChat Tools section


def _descendants(root_id):
    """Registered descendants of ``root_id``, parents before children."""
    panels = [c for c in bpy.types.Panel.__subclasses__() if getattr(c, "is_registered", False)]
    out, frontier = [], [root_id]
    while frontier:
        pid = frontier.pop(0)
        for c in panels:
            if getattr(c, "bl_parent_id", "") == pid:
                out.append(c)
                frontier.append(getattr(c, "bl_idname", c.__name__))
    return out


def adopt():
    """Re-register every stray (with its subtree) under its group header, in that header's tab and region."""
    for cls in _strays():
        parent = getattr(bpy.types, "BF_PT_sb_other", None)
        if parent is None:
            continue
        kids = _descendants(cls.bl_idname)
        saved = (getattr(cls, "bl_parent_id", ""), cls.bl_region_type, set(getattr(cls, "bl_options", ())),
                 cls.bl_category)
        kid_saved = [(k, k.bl_region_type, k.bl_category) for k in kids]
        try:
            for k in reversed(kids):                      # children first, parents last
                bpy.utils.unregister_class(k)
            bpy.utils.unregister_class(cls)
            cls.bl_parent_id = parent.bl_idname
            cls.bl_category = parent.bl_category          # a child draws in its parent's tab and region
            cls.bl_region_type = parent.bl_region_type
            cls.bl_options = set(getattr(cls, "bl_options", ())) | {'DEFAULT_CLOSED'}
            for k in kids:
                k.bl_category, k.bl_region_type = parent.bl_category, parent.bl_region_type
            bpy.utils.register_class(cls)
            for k in kids:                                # parents before children
                bpy.utils.register_class(k)
            _ADOPTED.append((cls, *saved))
            _KID_REGIONS.extend(kid_saved)
        except Exception:                                # noqa: BLE001 - one bad panel must not hide the rest
            logger.exception("[BoneCraft] could not group %s under %s", cls.bl_idname, parent.bl_idname)
            try:                                         # put everything back as it was: no tool may disappear
                _restore(cls, *saved)
                for k, region, category in kid_saved:
                    k.bl_region_type, k.bl_category = region, category
                if not getattr(cls, "is_registered", False):
                    bpy.utils.register_class(cls)
                for k, _region, _category in kid_saved:
                    if not getattr(k, "is_registered", False):
                        bpy.utils.register_class(k)
            except Exception:                            # noqa: BLE001
                logger.exception("[BoneCraft] could not restore %s", cls.bl_idname)


def _restore(cls, parent_id, region, options, category):
    cls.bl_parent_id = parent_id
    if not parent_id and "bl_parent_id" in cls.__dict__:
        del cls.bl_parent_id                              # a root panel must have no parent attribute at all
    cls.bl_region_type = region
    cls.bl_options = options
    cls.bl_category = category


def register():
    for header in HEADERS:
        if getattr(bpy.types, header.bl_idname, None) is None:
            bpy.utils.register_class(header)
    adopt()


def unregister():
    """Put the adopted classes back as they were, so a re-enable registers them cleanly."""
    for cls, parent_id, region, options, category in reversed(_ADOPTED):
        _restore(cls, parent_id, region, options, category)
    for k, region, category in reversed(_KID_REGIONS):
        k.bl_region_type, k.bl_category = region, category
    _ADOPTED.clear()
    _KID_REGIONS.clear()
    for header in reversed(HEADERS):
        try:
            bpy.utils.unregister_class(header)
        except RuntimeError:
            pass
