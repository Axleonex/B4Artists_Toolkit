"""ui_workflow package registrar — B4Artists ML.

Plan §2.1: registration order is feedback (PropertyGroup + Object.b4ml_ui),
then panel classes in PANEL_MODULES order (setup → pose → motion → review →
advanced, where advanced.CLASSES is parent-first, subpanels after).

Optional editor modules (viewport_overlay, markers, editor_dopesheet) are
loaded lazily in Phases 2/3; their absence never aborts panel registration.

Verified source facts (2026-09-22):
  feedback.py:151-174  register()/unregister() — idempotent, guards bpy
  panels/__init__.py:7  PANEL_MODULES = ('setup','pose','motion','review','advanced')
  panels/setup.py:109   CLASSES = (B4ML_PT_setup,)
  panels/pose.py:295    CLASSES: tuple[type, ...] = (B4ML_PT_pose,)
  panels/motion.py:202  CLASSES = (B4ML_PT_motion,)
  panels/review.py:136  CLASSES = (B4ML_PT_review,)
  panels/advanced.py:1640-1651  CLASSES = (B4ML_PT_advanced, …9 subpanels)
"""
from __future__ import annotations

import importlib

try:
    import bpy
except ImportError:
    bpy = None  # type: ignore[assignment]

# Registration state — populated by register(), cleared by unregister().
_REGISTERED: tuple[type, ...] = ()
_OPTIONAL_REGISTERED: list[str] = []

OPTIONAL_MODULES = ('viewport_overlay', 'markers', 'editor_dopesheet')


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def panel_classes() -> tuple[type, ...]:
    """Return all panel classes in PANEL_MODULES order (advanced last)."""
    from .panels import PANEL_MODULES
    classes: list[type] = []
    for name in PANEL_MODULES:
        mod = importlib.import_module('.panels.' + name, __package__)
        classes.extend(mod.CLASSES)
    return tuple(classes)


# ---------------------------------------------------------------------------
# register / unregister
# ---------------------------------------------------------------------------

def register() -> None:
    global _REGISTERED, _OPTIONAL_REGISTERED
    if bpy is None:
        return

    from . import feedback as _feedback
    _feedback.register()

    registered: list[type] = []
    for cls in panel_classes():
        if getattr(bpy.types, cls.__name__, None) is None:
            bpy.utils.register_class(cls)
        registered.append(cls)
    _REGISTERED = tuple(registered)

    _OPTIONAL_REGISTERED = []
    for name in OPTIONAL_MODULES:
        try:
            mod = importlib.import_module('.' + name, __package__)
        except (ImportError, ModuleNotFoundError):
            continue
        if callable(getattr(mod, 'register', None)):
            try:
                mod.register()
                _OPTIONAL_REGISTERED.append(name)
            except Exception as exc:
                print('[b4ml] optional module failed:', name, exc)


def unregister() -> None:
    global _REGISTERED, _OPTIONAL_REGISTERED
    if bpy is None:
        return

    for name in reversed(_OPTIONAL_REGISTERED):
        try:
            mod = importlib.import_module('.' + name, __package__)
            if callable(getattr(mod, 'unregister', None)):
                mod.unregister()
        except Exception:
            pass
    _OPTIONAL_REGISTERED = []

    for cls in reversed(_REGISTERED):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
    _REGISTERED = ()

    from . import feedback as _feedback
    _feedback.unregister()


def is_registered() -> bool:
    return bool(_REGISTERED)
