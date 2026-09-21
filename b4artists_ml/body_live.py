"""Opt-in newest-request scheduling for the reversible whole-body pose preview.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import math
import time
import bpy
from . import body_preview as body, workflow as w, posing as p

_WATCHERS = {}
QUIET_SECONDS = .15


def _now(value):
    value = time.monotonic() if value is None else float(value)
    if not math.isfinite(value):
        raise ValueError('Live preview clock must be finite')
    return value


def _pose(obj, watcher):
    return w.raw_pose(obj, watcher['controls'])


def start(obj, *, now=None):
    key = obj.as_pointer()
    if key in _WATCHERS or obj.b4ml.body_running:
        raise ValueError('A live preview or solve already owns this rig')
    with body._ReadScope(obj) as scope:
        record = body._read(obj, _scope=scope)
        current = w.raw_pose(obj, record['preview'].keys())
        if body._plain(current) != record['preview']:
            raise ValueError('Pose controls changed; cancel or solve the preview before starting Live Solve')
        session = body._get(obj, _scope=scope)
        signature = body._request(obj, session, _scope=scope)[2]
        tick = _now(now)
        _WATCHERS[key] = dict(obj=obj, scene=bpy.context.scene, frame=session.frame,
                             token=record['token'], controls=session.binding['controls'],
                             signature=signature, changed_at=tick, last_tick=tick,
                             pose=current, job=None, completed=0, cancelled=0)
        obj.b4ml.body_live = True
        obj.b4ml.status = 'Live Solve on; move pose targets'


def stop(obj, *, preserve_pose=None):
    key = obj.as_pointer(); watcher = _WATCHERS.pop(key, None)
    try:
        if watcher is not None and watcher['job'] is not None and body._JOBS.get(key) is watcher['job']:
            body.abort(obj)
    finally:
        obj.b4ml.body_live = False
        if preserve_pose is not None:
            w.restore_pose(obj, preserve_pose)
            p._update(obj)


def stop_all():
    for key, watcher in list(_WATCHERS.items()):
        try:
            stop(watcher['obj'])
        except (ReferenceError, RuntimeError, ValueError):
            _WATCHERS.pop(key, None)


def tick(obj, *, now=None):
    """At most one cooperative solver step; returns idle/queued/solving/ready/stopped.

    Inputs are inspected before advancing a fit. A stale fit is cancelled before
    another derivative probe; only the newest request can become the kept preview.
    """
    key = obj.as_pointer(); watcher = _WATCHERS.get(key)
    if watcher is None:
        return 'stopped'
    if not obj.b4ml.body_live:
        stop(obj); return 'stopped'
    try:
        with body._ReadScope(obj) as scope:
            clock = _now(now)
            if clock < watcher['last_tick']:
                raise ValueError('Live preview clock moved backwards')
            watcher['last_tick'] = clock
            if bpy.context.scene != watcher['scene'] or (bpy.context.scene.frame_current, bpy.context.scene.frame_subframe) != watcher['frame']:
                raise ValueError('Scene or frame changed; Live Solve stopped')
            if not obj.b4ml.body_payload or body._read(obj, _scope=scope)['token'] != watcher['token']:
                raise ValueError('Preview ownership changed; Live Solve stopped')
            current_pose = _pose(obj, watcher)
            if current_pose != watcher['pose']:
                # Preserve newer direct control edits, even when a fit is in flight.
                # The existing Keep guard refuses this unverified pose until solved.
                stop(obj, preserve_pose=current_pose)
                obj.b4ml.status = 'Live Solve stopped; direct rig edits preserved'
                return 'stopped'
            session = body._get(obj, _scope=scope)
            signature = body._request(obj, session, _scope=scope)[2]
            job = body._JOBS.get(key)
            if job is not None and job is not watcher['job']:
                raise ValueError('Another solver owns this rig; Live Solve stopped')
            if signature != watcher['signature']:
                if job is not None:
                    body.abort(obj); watcher['cancelled'] += 1
                watcher['job'] = None; watcher['signature'] = signature
                watcher['changed_at'] = clock; watcher['pose'] = _pose(obj, watcher)
                obj.b4ml.status = 'Live Solve waiting for target edits to settle'
                return 'queued'
            if job is None:
                if body._read(obj, _scope=scope)['signature'] == signature:
                    return 'idle'
                if clock-watcher['changed_at'] < QUIET_SECONDS:
                    return 'queued'
                body.start(obj, _live=True)
                watcher['job'] = body._JOBS[key]
            done = body.step(obj, _scope=scope)
            watcher['pose'] = _pose(obj, watcher)
            if done:
                watcher['job'] = None; watcher['completed'] += 1
                obj.b4ml.status = 'Live preview ready; move targets or keep the pose'
                return 'ready'
            return 'solving'
    except BaseException:
        stop(obj)
        raise


@bpy.app.handlers.persistent
def after_restore(*args):
    """Undo memfiles can retain SKIP_SAVE flags; no restored file owns a timer."""
    for obj in bpy.data.objects:
        if not hasattr(obj, 'b4ml'):
            continue
        state = obj.b4ml
        if state.body_live:
            state.body_live = False
            if obj.as_pointer() not in body._JOBS:
                state.body_running = False
                state.body_progress = ''
            state.status = 'Live Solve stopped after restoring scene state'
