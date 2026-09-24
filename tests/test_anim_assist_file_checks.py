"""Anim Assist file checks: clean enable, migration on enable and on every file open.

Blender enables add-ons with ``bpy.data`` restricted, so register() must not
touch scenes; the check and migration run once data is readable, and again
after each file load.

Run with:
    bforartists --background --factory-startup --python-exit-code 1 --python tests/test_anim_assist_file_checks.py
"""

from __future__ import annotations

import logging
import os
import sys
import tempfile
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import addon_utils  # noqa: E402


class _Collect(logging.Handler):
    def __init__(self) -> None:
        super().__init__(logging.WARNING)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def _reopen(path: str) -> None:
    bpy.ops.wm.save_as_mainfile(filepath=path)
    bpy.ops.wm.open_mainfile(filepath=path)


def main() -> None:
    collect = _Collect()
    logging.getLogger("anim_assist").addHandler(collect)

    # 1. Enable exactly as Preferences / startup do (restricted bpy.data).
    addon_utils.enable("anim_assist", default_set=False)
    from anim_assist import constants
    from anim_assist.core import migration

    errors = [r.getMessage() for r in collect.records if r.levelno >= logging.ERROR]
    assert not errors, f"errors while enabling: {errors}"

    # Timers never fire in background mode, so run a pending check by hand.
    if bpy.app.timers.is_registered(migration._check_open_file_timer):
        assert migration._check_open_file_timer() is None
        bpy.app.timers.unregister(migration._check_open_file_timer)
    current = constants.MIGRATION_CURRENT_VERSION
    scene_props = getattr(bpy.context.scene, constants.SCENE_PROP_ATTR)
    assert scene_props.migration_version == current, scene_props.migration_version
    print(f"ENABLE OK: no errors, open scene migrated to v{current}")

    with tempfile.TemporaryDirectory() as tmp:
        # 2. An older file is migrated when it is opened.
        getattr(bpy.context.scene, constants.SCENE_PROP_ATTR).migration_version = 1
        _reopen(os.path.join(tmp, "old.blend"))
        got = getattr(bpy.context.scene, constants.SCENE_PROP_ATTR).migration_version
        assert got == current, got
        print(f"LOAD OK: v1 file migrated to v{current} on open")

        # 3. A file from a newer Anim Assist is flagged, never downgraded.
        collect.records.clear()
        getattr(bpy.context.scene, constants.SCENE_PROP_ATTR).migration_version = 99
        _reopen(os.path.join(tmp, "newer.blend"))
        got = getattr(bpy.context.scene, constants.SCENE_PROP_ATTR).migration_version
        assert got == 99, got
        warned = [r.getMessage() for r in collect.records if "schema v99" in r.getMessage()]
        assert len(warned) == 1, [r.getMessage() for r in collect.records]
        print("LOAD OK: newer file warned once, left at v99")

    # 4. Disabling leaves no pending check behind.
    addon_utils.disable("anim_assist", default_set=False)
    assert not bpy.app.timers.is_registered(migration._check_open_file_timer)
    errors = [r.getMessage() for r in collect.records if r.levelno >= logging.ERROR]
    assert not errors, errors
    print("DISABLE OK")


if __name__ == "__main__":
    main()
