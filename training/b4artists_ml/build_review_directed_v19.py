"""Build v3 display-recovery review, NOT a new procedural animation revision.

The v19 engineering investigation found a lost native motion-instance transform.
Retain v15/v17/v18 scenes and v2 reviews byte-for-byte; resample all 32 scenes,
show only changed comparisons, and explicitly label the re-review non-blind.
"""
import copy
import json
import math
from pathlib import Path
import sys

TRAIN = Path(__file__).resolve().parent
sys.path.insert(0, str(TRAIN))
import diagnose_review_directed_v19 as diag
import import_followup_review_v2 as human

OUT = TRAIN / 'results/review-directed-followup-reviewer-v3'
TEMPLATE = TRAIN / 'review_directed_followup_template_v2.html'


def validate_extraction(variant, case):
    name = f"{variant}-{case['profile']}-{case['task']}"
    path = diag.OUT / 'extracted' / (name + '.json')
    process = diag.read(diag.OUT / 'processes' / (name + '.json'))
    log = diag.OUT / 'logs' / (name + '.log')
    value = diag.read(path)
    if (value.get('variant') != variant or value.get('profile') != case['profile'] or value.get('task') != case['task'] or
            process.get('variant') != variant or process.get('profile') != case['profile'] or process.get('task') != case['task'] or
            process.get('qualified') is not True or process['extract_sha256'] != diag.sha(path) or
            process['log_sha256'] != diag.sha(log) or not diag.qualified_exit(process['returncode'], log.read_text(), value) or
            value['extractor_sha256'] != diag.sha(Path(diag.__file__))):
        raise ValueError('Unqualified/stale displayed-scene extraction: ' + name)
    old = diag.OLD / 'extracted' / (name + '.json')
    prior = diag.read(old)
    blend = diag.ROOT / prior['blend_path']
    if (value['prior_extract_sha256'] != diag.sha(old) or value['blend_path'] != prior['blend_path'] or
            value['blend_sha256'] != diag.sha(blend) or value['report_sha256'] != diag.sha(blend.parent / 'report.json')):
        raise ValueError('Source scene changed: ' + name)
    for key in ('frames', 'fps', 'floor_z', 'priority_frames', 'semantic_bones'):
        if value[key] != prior[key]:
            raise ValueError('Timing/floor/mapping changed: ' + key)
    def number(v):
        if type(v) not in (int, float) or not math.isfinite(v):
            raise ValueError('Nonfinite/nonnumeric evidence')
        return v
    if len(value['samples']) != 49 or len(value['layer_matrices']) != 49:
        raise ValueError('Incomplete sampling')
    for sample in value['samples']:
        if len(sample) != 17 or any(len(p) != 3 for p in sample):
            raise ValueError('Wrong skeleton shape')
        for point in sample:
            for coordinate in point:
                number(coordinate)
    for key in ('maximum_legacy_reproduction_error', 'maximum_native_instance_error'):
        if not 0 <= number(value[key]) <= 2e-6:
            raise ValueError('Native parity failure')
    difference = max(abs(a-b) for sa,sb in zip(value['samples'],prior['samples']) for pa,pb in zip(sa,sb) for a,b in zip(pa,pb))
    if abs(difference - number(value['maximum_display_difference'])) > 1e-9 or value['corrected_metrics'] != diag.metrics(value):
        raise ValueError('Inconsistent derived display metrics')
    if type(value.get('has_native_motion_layer')) is not bool or (not value['has_native_motion_layer'] and difference > 2e-6):
        raise ValueError('Non-layer scene unexpectedly changed')
    return value


def assemble():
    human.validate()
    old = diag.read(diag.OLD / 'review-data.json')
    payload = copy.deepcopy(old)
    changed, unchanged, evidence = [], [], []
    for case in old['cases']:
        values = {v: validate_extraction(v, case) for v in ('baseline', 'candidate')}
        difference = max(v['maximum_display_difference'] for v in values.values())
        evidence.append(dict(id=case['id'], maximum_display_difference=difference,
            variants={v: dict(extract_sha256=diag.sha(diag.OUT / 'extracted' / f"{v}-{case['profile']}-{case['task']}.json"),
                old_metrics=x['old_metrics'], corrected_metrics=x['corrected_metrics'],
                maximum_native_instance_error=x['maximum_native_instance_error']) for v,x in values.items()}))
        if difference <= 2e-6:
            unchanged.append(case['id'])
            continue
        row = copy.deepcopy(case)
        for label, identity in case['reveal'].items():
            value = values[identity['variant']]
            row['methods'][label]['samples'] = value['samples']
        points = [p for value in values.values() for sample in value['samples'] for p in sample]
        lows = [min(p[i] for p in points) for i in range(3)]
        highs = [max(p[i] for p in points) for i in range(3)]
        lows[2] = min(lows[2], *(v['floor_z'] for v in values.values()))
        row['center'] = [(a+b)/2 for a,b in zip(lows,highs)]
        row['radius'] = max(.2, max(math.dist(p,row['center']) for p in points))
        row['prompt'] = 'Corrected full-body display. ' + case['prompt']
        changed.append(row)
    payload.update(schema='b4ml-review-directed-followup-review-data-v3', title='Corrected whole-body preview', cases=changed,
        human_review_status='pending non-blind corrected-display review', prior_exposure=True,
        source_human_review_sha256=diag.sha(human.EXPORT), source_display_recovery_sha256=human.canonical_hash(evidence),
        training_authorized=False, model_promotion_authorized=False, full_goal_complete=False)
    recovery = dict(schema='b4ml-display-recovery-v3', source_data_sha256=diag.sha(diag.OLD / 'review-data.json'),
        source_human_review_sha256=diag.sha(human.EXPORT), native_comparisons=32,
        affected_cases=[c['id'] for c in changed], unaffected_cases=unchanged, evidence=evidence,
        interpretation='Old ratings remain valid for their displayed representation. Affected cases require a non-blind native-display re-review; unaffected ratings are preserved, not discarded.',
        native_animation_modified=False, training_authorized=False, model_promotion_authorized=False, full_goal_complete=False)
    return payload, recovery


def render_page(payload, data_hash):
    page = TEMPLATE.read_text(encoding='utf-8')
    replacements = {
        'Follow-up review 2': 'Corrected whole-body preview',
        'Independent human assessment pending': 'Corrected-display re-review',
        'Compare the new v18 candidate with the previously reviewed v15/v17 candidate. A/B identities stay hidden until you lock each case. Your earlier ratings remain untouched.':
            'The previous preview omitted whole-body flight motion. This page shows the SAME saved animations with their native motion layers restored. Only the affected comparisons need another look; every earlier rating is backed up and unchanged. This is a non-blind re-review, not new model training.',
        'Blind variant': 'Previously viewed variant',
        'a completed review requires all 16 cases locked': f'a completed corrected-display review requires these {len(payload["cases"])} affected cases locked',
        'b4ml-review-directed-followup-v2-': 'b4ml-review-directed-followup-v3-',
        'b4ml-review-directed-followup-human-review-v2': 'b4ml-review-directed-followup-human-review-v3',
        'blind_at_rating:!prior.reveal_seen': 'blind_at_rating:false',
        'shown=Boolean(review?.reveal_seen)': 'shown=true',
        'source_qualification_sha256:data.source_qualification_sha256,reviewer:':
            'source_qualification_sha256:data.source_qualification_sha256,source_display_recovery_sha256:data.source_display_recovery_sha256,prior_exposure:true,reviewer:',
        'reveal_seen?c.reveal:null': 'locked?c.reveal:null',
        'the original blind rating is retained': 'the original rating is retained',
    }
    for before, after in replacements.items():
        if before not in page:
            raise ValueError('Template anchor changed: ' + before)
        page = page.replace(before, after)
    encoded = json.dumps(payload, separators=(',', ':'), ensure_ascii=False, allow_nan=False)
    return page.replace('__REVIEW_DATA__', encoded.replace('<', '\\u003c')).replace('__DATA_SHA256__', data_hash)


def build():
    if OUT.exists():
        raise ValueError('Immutable corrected review already exists; refusing overwrite')
    payload, recovery = assemble()
    encoded = json.dumps(payload, separators=(',', ':'), ensure_ascii=False, allow_nan=False)
    import hashlib
    data_hash = hashlib.sha256(encoded.encode()).hexdigest()
    page = render_page(payload, data_hash)
    OUT.mkdir(parents=True)
    for name, text in [('review-data.json', encoded), ('reviewer.html', page)]:
        with (OUT / name).open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(text)
    diag.write_new(OUT / 'display-recovery.json', recovery)
    manifest = dict(schema='b4ml-review-display-recovery-manifest-v3', complete=True,
        cases=len(payload['cases']), native_comparisons=32, human_review_status='pending',
        data_sha256=data_hash, html_sha256=diag.sha(OUT / 'reviewer.html'),
        builder_sha256=diag.sha(Path(__file__)), extractor_sha256=diag.sha(Path(diag.__file__)),
        template_sha256=diag.sha(TEMPLATE), recovery_sha256=diag.sha(OUT / 'display-recovery.json'),
        training_authorized=False, model_promotion_authorized=False, full_goal_complete=False)
    diag.write_new(OUT / 'manifest.json', manifest)
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    build()
