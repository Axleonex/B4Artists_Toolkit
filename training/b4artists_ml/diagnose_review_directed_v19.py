"""Diagnose displayed motion versus v2 exported skeletons without editing scenes."""
import hashlib
import json
import math
from pathlib import Path
import os
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
TRAIN = ROOT / 'training/b4artists_ml'
OLD = TRAIN / 'results/review-directed-followup-reviewer-v2'
OUT = TRAIN / 'results/review-display-recovery-v3'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_point(matrix, point):
    if len(matrix) != 4 or any(len(row) != 4 for row in matrix) or len(point) != 3:
        raise ValueError('Expected a 4x4 affine transform and a 3D point')
    if any(type(v) not in (int, float) or not math.isfinite(v) for row in matrix for v in row) or any(type(v) not in (int, float) or not math.isfinite(v) for v in point):
        raise ValueError('Nonfinite transform/point')
    if matrix[3] != [0, 0, 0, 1]:
        raise ValueError('Expected affine transform')
    return [sum(matrix[i][j] * point[j] for j in range(3)) + matrix[i][3] for i in range(3)]


def metrics(value):
    points = value['samples']
    return dict(maximum_two_foot_clearance=max(min(s[13][2], s[16][2]) - value['floor_z'] for s in points),
        pelvis_vertical_range=max(s[0][2] for s in points) - min(s[0][2] for s in points))


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)


def marker(value):
    return 'B4ML_DISPLAY_RECOVERY=' + json.dumps({key: value.get(key) for key in ('variant', 'profile', 'task', 'complete', 'error', 'seconds')}, allow_nan=False)


def qualified_exit(code, log, value):
    at = log.find(marker(value))
    crash = log.find('EXCEPTION_ACCESS_VIOLATION')
    if value.get('complete') is not True or at < 0:
        return False
    if code == 0:
        return crash < 0
    return code & 0xffffffff == 0xc0000005 and crash > at and 'ucrtbase.dll' in log[crash:]


def host(variant, profile, task):
    import bpy
    from mathutils import Vector
    sys.path[:0] = [str(ROOT), str(TRAIN)]
    import b4artists_ml
    from b4artists_ml import body_solver, motion_layer, posing
    started = time.perf_counter()
    result = dict(variant=variant, profile=profile, task=task, complete=False)
    try:
        b4artists_ml.register()
        old_path = OLD / 'extracted' / f'{variant}-{profile}-{task}.json'
        old = read(old_path)
        blend = ROOT / old['blend_path']
        report_path = blend.parent / 'report.json'
        if sha(blend) != old['blend_sha256'] or sha(report_path) != old['report_sha256']:
            raise ValueError('Source scene changed')
        report = read(report_path)
        animated = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o.animation_data and o.animation_data.action]
        if len(animated) != 1:
            raise ValueError('Ambiguous animated armature')
        obj = animated[0]
        scene = next(s for s in bpy.data.scenes if obj.name in s.objects)
        bpy.context.window.scene = scene
        binding = body_solver.mapping(obj, writable=False)
        if list(binding['names']) != old['semantic_bones']:
            raise ValueError('Semantic mapping changed')
        names = binding['names']
        axes = [Vector(a) for a in report['task_basis_world']]
        height = report['reference_height']
        raw_rows, corrected_rows, layers = [], [], []
        instance_error = 0.0
        origin = None
        has_layer = motion_layer.find(obj) is not None
        if has_layer:
            motion_layer.validate(obj)
        for frame in old['frames']:
            scene.frame_set(math.floor(frame), subframe=frame % 1)
            posing._update(obj)
            graph = bpy.context.evaluated_depsgraph_get()
            evaluated = obj.evaluated_get(graph)
            raw = [evaluated.matrix_world @ evaluated.pose.bones[name].head for name in names]
            if origin is None:
                origin = raw[0].copy()
            layer = motion_layer.transform(obj)
            layer_values = [list(row) for row in layer]
            corrected = [Vector(transform_point(layer_values, list(p))) for p in raw]
            # Independent native renderer/depsgraph instance matrix, not the
            # same workflow transform, verifies the exported display positions.
            instances = [i.matrix_world.copy() for i in graph.object_instances
                         if i.object.original == obj and bool(i.is_instance) == has_layer]
            if len(instances) != 1:
                raise ValueError(f'Expected one displayed armature instance, found {len(instances)}')
            native = [instances[0] @ evaluated.pose.bones[name].head for name in names]
            instance_error = max(instance_error, max((a-b).length / height for a,b in zip(corrected, native)))
            def project(points):
                return [[round(float((p-origin).dot(axis) / height), 7) for axis in axes] for p in points]
            raw_rows.append(project(raw))
            corrected_rows.append(project(corrected))
            layers.append(layer_values)
        legacy_error = max(abs(a-b) for sa,sb in zip(raw_rows, old['samples']) for pa,pb in zip(sa,sb) for a,b in zip(pa,pb))
        if legacy_error > 2e-6 or instance_error > 2e-6:
            raise ValueError(f'Native parity failure: legacy={legacy_error}, displayed={instance_error}')
        result = dict(old, schema='b4ml-displayed-scene-extract-v3', samples=corrected_rows,
            has_native_motion_layer=has_layer, layer_matrices=layers,
            prior_extract_sha256=sha(old_path), extractor_sha256=sha(Path(__file__)),
            maximum_legacy_reproduction_error=legacy_error, maximum_native_instance_error=instance_error,
            maximum_display_difference=max(abs(a-b) for sa,sb in zip(raw_rows,corrected_rows) for pa,pb in zip(sa,sb) for a,b in zip(pa,pb)),
            old_metrics=metrics(old), complete=True)
        result['corrected_metrics'] = metrics(result)
        result['full_goal_complete'] = False
    except Exception:
        result.update(complete=False, error=traceback.format_exc())
    result['seconds'] = time.perf_counter() - started
    write_new(OUT / 'extracted' / f'{variant}-{profile}-{task}.json', result)
    print(marker(result), flush=True)


def run(cases):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for variant, profile, task in cases:
        name = f'{variant}-{profile}-{task}'
        extraction = OUT / 'extracted' / (name + '.json')
        process = OUT / 'processes' / (name + '.json')
        log_path = OUT / 'logs' / (name + '.log')
        if process.exists():
            evidence = read(process)
            value = read(extraction)
            if evidence['extract_sha256'] != sha(extraction) or evidence['log_sha256'] != sha(log_path) or value['extractor_sha256'] != sha(Path(__file__)) or not qualified_exit(evidence['returncode'], log_path.read_text(), value):
                raise ValueError('Stale prior extraction; retained')
            rows.append(evidence)
            continue
        if extraction.exists() or log_path.exists():
            raise ValueError('Incomplete diagnostic retained; refusing overwrite')
        old = read(OLD / 'extracted' / (name + '.json'))
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open('x', encoding='utf-8') as log:
            result = subprocess.run(['X:/5.1.0/bforartists.exe', '--background', '--factory-startup', '--disable-autoexec',
                str(ROOT / old['blend_path']), '--python', str(Path(__file__).resolve()), '--', variant, profile, task],
                stdout=log, stderr=subprocess.STDOUT, timeout=180,
                env=dict(os.environ, OPENBLAS_NUM_THREADS='4', PYTHONDONTWRITEBYTECODE='1'))
        value = read(extraction) if extraction.exists() else {}
        evidence = dict(variant=variant, profile=profile, task=task, returncode=result.returncode,
            qualified=qualified_exit(result.returncode, log_path.read_text(encoding='utf-8',errors='replace'), value),
            extract_sha256=sha(extraction) if extraction.exists() else None, log_sha256=sha(log_path),
            corrected_metrics=value.get('corrected_metrics'), old_metrics=value.get('old_metrics'))
        write_new(process, evidence)
        print(json.dumps(evidence), flush=True)
        if not evidence['qualified']:
            raise ValueError('Unqualified native diagnostic ' + name)
        rows.append(evidence)
    return rows


if __name__ == '__main__':
    if '--' in sys.argv:
        host(*sys.argv[sys.argv.index('--')+1:])
    elif len(sys.argv) == 4:
        run([tuple(sys.argv[1:])])
    else:
        data = read(OLD / 'review-data.json')
        run([(v,c['profile'],c['task']) for c in data['cases'] for v in ('baseline','candidate')])
