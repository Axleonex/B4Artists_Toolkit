"""Isolated Anim Assist baseline/candidate regression runner (normal Python)."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile


def write_coverage(results, destination):
    """Queue every operator; a sample PASS never implies complete feature proof."""
    census = results.get('census') or {}
    ops = census.get('operators', [])
    if not ops:
        return
    direct = {}
    for check in results.get('behavioral_checks', []):
        for op in check.get('invoked_operators', []):
            direct.setdefault(op, []).append(check)
    fixtures = {'p2': 'animated + selected keys', 'p3': 'animated/paired armature + two bounding poses',
        'p4': 'animated + offset settings', 'p5': 'animated + VIEW_3D overlay/window',
        'p6': 'animated + timing/range settings', 'p7': 'animated/paired armature + tagged proxy session',
        'p8': 'two objects or paired armature + explicit match/switch target',
        'p9': 'paired armature in Pose Mode; hand.L/hand.R',
        'p10': 'disposable scene settings/favorites/recents/preset/macro files',
        'p11': 'animated/paired armature + real NLA/action layer stack',
        'p12': 'configured real WAV + jaw/shape-key face; optional Rhubarb remains PENDING'}
    rows = []
    for op in ops:
        source = (op['source'] or '').replace('\\', '/')
        module = Path(source).stem
        family = module.split('_')[0] if re.match(r'p\d+_', module) else module
        routes = list(census.get('panel_routes', {}).get(op['id'], []))
        if op['searchable']: routes.append('Search')
        for space, groups in census.get('menus', {}).items():
            for group in groups:
                if op['id'] in group['operators']: routes.append(space + ' menu: ' + group['group'])
        if op['id'] in census.get('pie_ids', []): routes.append('Anim Assist pie')
        scenarios = direct.get(op['id'], [])
        statuses = {c['status'] for c in scenarios}
        rows.append({'operator_id': op['id'], 'label': op['label'], 'family': family,
            'classification': 'INTERNAL bookkeeping' if op['id'] == 'animassist.p10_record_recent' else 'PUBLIC',
            'source': source, 'line': op['line'], 'routes': '; '.join(routes) or 'PENDING route inspection',
            'valid_fixture': fixtures.get(family, 'Disposable editor scene/preferences: ' + module),
            'invalid_fixture': 'Same fixture with prerequisites removed individually; verify poll/cancel and unchanged scene/history',
            'expected_effect': op['description'] or op['doc'] or op['label'],
            'parameters_json': json.dumps(op['properties'], ensure_ascii=False),
            'scope_contract': 'Check the explicitly targeted keys/objects/bones/layers; compare untouched data. Precise scope needs per-operator review.',
            'automated_sample_status': 'FAIL' if 'FAIL' in statuses else 'PASS' if statuses else 'NOT RUN',
            'automated_scenarios': '; '.join(c['name'] for c in scenarios),
            'coverage_method': 'Automatic sample + required remaining manual/host contracts' if scenarios else 'Queued manual/host contract',
            'baseline_evidence': destination.with_name('baseline-results.json').name if scenarios else '',
            'cancellation': 'NOT VERIFIED per operator; invoke/Esc/file-dialog checks remain queued',
            'undo_redo': 'NOT VERIFIED in a real window' if 'UNDO' in op['options'] else 'No UNDO declared; verify relevant state/file/dispatch contract',
            'full_feature_status': 'FAIL' if 'FAIL' in statuses else 'PENDING',
            'remaining_procedure': 'Reset valid fixture; run ' + op['label'] +
                ' using recorded RNA parameters; measure expected_effect and untouched scope; remove each prerequisite; retry after recovery; cancel invocation; repeat then reacquire data after Undo/Redo where applicable. Record actual results, not FINISHED alone.'})
    assert len(rows) == len({row['operator_id'] for row in rows}) == len(ops)
    with destination.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--source-root', type=Path)
    source.add_argument('--zip', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mode', choices=('baseline', 'candidate'), required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    logdir = output.parent / (output.stem + '-logs')
    logdir.mkdir(exist_ok=True)
    results = {'mode': args.mode, 'host_path': args.host, 'suites': [],
               'limitations': ['Background execution does not prove real-window Undo/Redo or owner usability.']}
    with tempfile.TemporaryDirectory(prefix='anim-assist-regression-') as temporary:
        root = Path(temporary)
        source_root = root / 'anim_assist'
        if args.source_root:
            shutil.copytree(args.source_root.resolve(), source_root,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        else:
            with zipfile.ZipFile(args.zip) as archive:
                names = [n for n in archive.namelist() if not n.endswith('/')]
                roots = {n.split('/')[0] for n in names}
                if len(roots) != 1:
                    raise ValueError('Archive must have one package root')
                package = roots.pop()
                for name in names:
                    relative = Path(name).relative_to(package)
                    if '..' in relative.parts or relative.is_absolute():
                        raise ValueError('Unsafe ZIP entry')
                    path = source_root / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(archive.read(name))
        results['source_hashes'] = {p.relative_to(source_root).as_posix():
            hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source_root.rglob('*')) if p.is_file()}
        (root / 'tests').mkdir()
        host_env = os.environ.copy()
        host_env['PYTHONDONTWRITEBYTECODE'] = '1'
        for kind in ('CONFIG', 'SCRIPTS', 'DATAFILES'):
            directory = root / ('user-' + kind.lower())
            directory.mkdir()
            host_env['BLENDER_USER_' + kind] = str(directory)

        def run(name, command, *, markers=(), unittest=False, result_file=None):
            entry = {'name': name, 'command': command}
            try:
                process = subprocess.run(command, capture_output=True, text=True,
                    encoding='utf-8', errors='replace', env=host_env, timeout=240)
                log = process.stdout + '\n' + process.stderr
                entry['exit_code'] = process.returncode
                entry['passed'] = process.returncode == 0 and all(m in log for m in markers)
                if unittest:
                    match = re.search(r'Ran (\d+) tests?', log)
                    entry['test_count'] = int(match[1]) if match else 0
                    entry['passed'] &= entry['test_count'] > 0 and '\nOK' in log
                    if re.search(r'OK \(skipped=', log):
                        entry['passed'] = False
                        entry['error'] = 'Skipped internal tests need explicit classification'
                if result_file:
                    entry['result'] = json.loads(result_file.read_text(encoding='utf-8'))
                    entry['passed'] &= entry['result'].get('passed') is True
                    shutil.copy2(result_file, logdir / (name + '.json'))
                if 'Traceback (most recent call last)' in log:
                    # The historical probe deliberately catches an ERROR report;
                    # report_failure logs that one expected negative-path trace.
                    traces = log.split('Traceback (most recent call last):')[1:]
                    expected = (name == 'repair_checks' and len(traces) == 1
                        and re.search(r'\nRuntimeError: Error: No lipsync layer link to bake\.[^\n]*', traces[0])
                        and result_file and entry.get('result', {}).get('passed') is True
                        and len(entry['result'].get('checks', [])) == 26)
                    if not expected:
                        entry['passed'] = False
                    else:
                        entry['expected_negative_trace'] = 'Unconfigured Lipsync Search raises ERROR; history stays unchanged'
                (logdir / (name + '.txt')).write_text(log, encoding='utf-8')
                entry['log'] = str(logdir / (name + '.txt'))
            except Exception as error:
                entry.update(passed=False, error=repr(error))
            results['suites'].append(entry)
            output.write_text(json.dumps(results, indent=2), encoding='utf-8')
            print(name + ': ' + ('PASS' if entry['passed'] else 'FAIL'), flush=True)

        scripts = sorted((source_root / 'tests').glob('test_*.py'))
        if len(scripts) != 9:
            raise AssertionError('Expected nine existing scripts; found ' + str(len(scripts)))
        for script in scripts:
            run(script.stem, [sys.executable, str(script)], unittest=True)
        base = [args.host, '--background', '--factory-startup', '--python-exit-code', '1', '--python']
        for name, markers in (
            ('test_anim_assist_layout', ('LAYOUT OK:', 'UNREGISTER OK')),
            ('test_anim_assist_file_checks', ('ENABLE OK:', 'LOAD OK: v1', 'LOAD OK: newer', 'DISABLE OK'))):
            script = root / 'tests' / (name + '.py')
            shutil.copy2(repo / 'tests' / script.name, script)
            run(name, base + [str(script)], markers=markers)
        # Preserve the exact released imports, with all results in this disposable root.
        shutil.copytree(source_root, root / 'B4_anim_assist')
        repair = root / 'repair-check.py'
        shutil.copy2(repo / 'docs/anim_assist/releases/12.1.1/runtime-check.py', repair)
        run('repair_checks', base + [str(repair), '--', str(root)],
            result_file=root / 'runtime-results.json')
        workflow = root / 'tests' / 'test_anim_assist_workflows.py'
        shutil.copy2(repo / 'tests' / workflow.name, workflow)
        workflow_result = root / 'workflow-results.json'
        run('workflows', base + [str(workflow), '--', str(root), str(workflow_result), str(logdir / 'fixtures')],
            result_file=workflow_result)
        if workflow_result.exists():
            data = json.loads(workflow_result.read_text())
            results['census'] = data.get('census')
            results['behavioral_checks'] = data.get('checks', [])
            results['lipsync_diagnostic'] = data.get('lipsync_diagnostic')
    results['passed'] = bool(results['suites']) and all(e['passed'] for e in results['suites'])
    results['internal_test_count'] = sum(e.get('test_count', 0) for e in results['suites'])
    results['full_feature_gate'] = 'PENDING: per-operator manual/host gaps; baseline failure blocks UI execution'
    write_coverage(results, output.parent / 'feature-coverage.csv')
    output.write_text(json.dumps(results, indent=2), encoding='utf-8')
    return 0 if results['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
