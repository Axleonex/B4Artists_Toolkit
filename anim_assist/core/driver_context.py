"""Driver targets from the current editor, without falling back to an Action."""
from __future__ import annotations
from ..i18n import T, F


def in_driver_editor(context) -> bool:
    space = getattr(context, "space_data", None)
    return bool(space and space.type == "GRAPH_EDITOR" and space.mode == "DRIVERS")


def driver_curves(context, *, selected=False, editable=False) -> list:
    """Respect native editor visibility, channel selection, locks and ID editability."""
    if not in_driver_editor(context):
        return []
    curves = getattr(context, "visible_fcurves", ()) or ()
    return [fc for fc in curves if fc.driver is not None and not fc.hide
            and (not selected or fc.select)
            and (not editable or (not fc.lock and fc.id_data.is_editable))]


def active_driver(context):
    """Inspect the active curve, or the sole selected visible driver.

    Native active_editable_fcurve disappears on lock. Retain the explicitly
    selected driver so its right-sidebar lock control can still unlock it.
    """
    if not in_driver_editor(context):
        return None
    fc = getattr(context, "active_editable_fcurve", None)
    visible = driver_curves(context)
    if fc is not None and fc in visible:
        return fc
    selected = [curve for curve in visible if curve.select]
    return selected[0] if len(selected) == 1 else None


def driver_issues(fc, context) -> list[str]:
    """Read-only checks for a single driver; run on request, never on redraw."""
    driver = fc.driver
    issues = []
    if not driver.is_valid:
        issues.append(T("Driver evaluation failed; check the expression and targets, then refresh dependencies."))
    if not fc.id_data.is_editable:
        issues.append(T("Owner is linked or read-only."))
    if fc.lock:
        issues.append(T("Channel is locked."))
    if fc.mute:
        issues.append(T("Driver is muted."))
    for variable in driver.variables:
        for target in variable.targets:
            if variable.type == "CONTEXT_PROP":
                owner = context.scene if target.context_property == "ACTIVE_SCENE" else context.view_layer
            else:
                owner = target.id
            if owner is None:
                issues.append(F("Variable {name}: missing target.", name=variable.name))
                continue
            if variable.type in {"SINGLE_PROP", "CONTEXT_PROP"}:
                try:
                    if not target.data_path:
                        raise ValueError("Empty property path")
                    owner.path_resolve(target.data_path)
                except (ValueError, AttributeError, KeyError, TypeError):
                    if not target.use_fallback_value:
                        issues.append(F("Variable {name}: unresolved property path {path!r}.", name=variable.name, path=target.data_path))
            elif target.bone_target:
                pose = getattr(owner, "pose", None)
                if pose is None or pose.bones.get(target.bone_target) is None:
                    issues.append(F("Variable {name}: missing bone {bone!r}.", name=variable.name, bone=target.bone_target))
    return issues
