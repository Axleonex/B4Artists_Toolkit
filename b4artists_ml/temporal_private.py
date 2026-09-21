"""Private working-rig execution for source-preserving temporal previews.
SPDX-License-Identifier: GPL-2.0-or-later
Blender data stays on the main thread. Only validated samples leave the working
rig, and the source transaction is checked before and after every public step.
"""
import math
import time
import bpy
from . import body_proxy, temporal_generation as generation, workflow as w


class WorkingTransaction(generation.Transaction):
    """The private rig need not restore its pose at each internal solver yield."""
    def pause(self, progress, cancel_requested):
        yield progress
        if cancel_requested is not None and cancel_requested():
            raise InterruptedError('Temporal projection cancelled')


class PrivateJob:
    def __init__(self, obj, predictor, options, *, chunk_seconds=.02):
        if not math.isfinite(chunk_seconds) or not 0 <= chunk_seconds <= .1:
            raise ValueError('Invalid temporal scheduling budget')
        key = obj.as_pointer()
        if key in generation._OWNERS:
            raise ValueError('A temporal job already owns this rig')
        self.obj = obj
        self.scene = bpy.context.scene
        self.key = key
        self.guard = generation.Transaction(obj, self.scene)
        self.proxy = body_proxy.EvaluationProxy(obj, (), defer=True)
        self.predictor = predictor
        self.options = dict(options)
        self.chunk_seconds = chunk_seconds
        self.preparation = None
        self.steps = None
        self.closed = False
        self.running = False
        self.reason = None
        self.execution_path = 'private_rig'
        generation._OWNERS[key] = self.guard
        generation._LIVE[id(self)] = self
        try:
            self.guard.guard()
            self.preparation = self.proxy.prepare_steps(obj, [p.name for p in obj.pose.bones])
        except BaseException:
            self.close()
            raise

    def __iter__(self):
        return self

    def _context(self):
        layer = self.proxy.scene.view_layers[0]
        return bpy.context.temp_override(
            scene=self.proxy.scene, view_layer=layer, object=self.proxy.obj,
            active_object=self.proxy.obj, selected_objects=[self.proxy.obj],
            selected_editable_objects=[self.proxy.obj])

    def __next__(self):
        if self.reason is not None:
            raise InterruptedError(self.reason)
        if self.closed:
            raise StopIteration
        started = time.perf_counter()
        self.running = True
        finished = False
        answer = None
        try:
            self.guard.guard()
            if self.preparation is not None:
                try:
                    phase = next(self.preparation)
                    progress = dict(phase='preparing_' + phase)
                except StopIteration:
                    self.preparation = None
                    # The source action is read-only. The proxy owns separate rig
                    # channels, driver targets and scene time for its evaluations.
                    source_ad = self.obj.animation_data
                    w.assign_action(self.proxy.obj, source_ad.action if source_ad else None,
                                    w._slot(source_ad))
                    self.steps = generation._generate_steps(
                        self.proxy.obj, self.predictor,
                        _transaction_factory=WorkingTransaction, **self.options)
                    progress = dict(phase='working_rig_ready')
            else:
                advanced = False
                with self._context():
                    # Always advance once: a large source guard must not starve
                    # solving by consuming the entire scheduling budget.
                    while not advanced or time.perf_counter() - started < self.chunk_seconds:
                        try:
                            progress = next(self.steps)
                            advanced = True
                        except StopIteration as done:
                            answer = done.value
                            finished = True
                            break
            self.guard.guard()
        except BaseException:
            self.running = False
            self.close()
            raise
        finally:
            self.running = False
        if self.reason is not None:
            self.close()
            raise InterruptedError(self.reason)
        if finished:
            self.close()
            raise StopIteration(answer)
        return progress

    def close(self):
        if self.closed:
            return
        if self.running:
            raise RuntimeError('Cannot close temporal work while executing a step')
        try:
            try:
                if self.steps is not None:
                    with self._context():
                        self.steps.close()
            finally:
                if self.preparation is not None:
                    self.preparation.close()
        finally:
            try:
                self.proxy.close()
            finally:
                self.closed = True
                generation._LIVE.pop(id(self), None)
                if generation._OWNERS.get(self.key) is self.guard:
                    generation._OWNERS.pop(self.key, None)

    def cancel(self, reason='Temporal generation cancelled'):
        self.reason = reason
        if not self.running:
            self.close()


def create_job(obj, predictor, options):
    """Keep existing rig support when a dependency-safe copy is unavailable."""
    w.require_rig(obj)
    try:
        body_proxy.dependency_bones(obj, [p.name for p in obj.pose.bones])
    except ValueError:
        # This eligibility probe never mutates source data. The original path
        # retains all of its own space, constraint, curve and lifecycle guards.
        job = generation.Job(obj, predictor, options)
        job.execution_path = 'guarded_source'
        return job
    return PrivateJob(obj, predictor, options)
