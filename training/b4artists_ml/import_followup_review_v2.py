"""Strict, read-only validation of the captured Axlbot follow-up review.

No rating is synthesized or promoted to training authorization. The capture's
canonical SHA-256 was independently matched to the visible browser export.
"""
import hashlib
import json
from pathlib import Path
import re
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
TRAIN = ROOT / 'training/b4artists_ml'
REVIEW = TRAIN / 'results/review-directed-followup-reviewer-v2'
EXPORT = TRAIN / 'results/human-review-exports/b4ml-review-directed-followup-human-review-v2-axlbot.json'
CAPTURE_HASH = '0819d253b73347be9fa23fc647c8cfe10c3f2889712dcd5c1a45ab620063ddf5'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('Nonfinite JSON: ' + value)
    return json.loads(path.read_text(encoding='utf-8-sig'), object_pairs_hook=unique, parse_constant=invalid)


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def validate(value=None, *, require_capture=True):
    value = read(EXPORT) if value is None else value
    data = read(REVIEW / 'review-data.json')
    manifest = read(REVIEW / 'manifest.json')
    if value.get('schema') != 'b4ml-review-directed-followup-human-review-v2':
        raise ValueError('Wrong review schema')
    for key, expected in [('complete', True), ('human_authored', True), ('training_authorized', False), ('model_promotion_authorized', False)]:
        if value.get(key) is not expected:
            raise ValueError('Invalid authorization/completion field: ' + key)
    if value.get('source_data_sha256') != sha(REVIEW / 'review-data.json') or manifest['data_sha256'] != value['source_data_sha256']:
        raise ValueError('Stale review data')
    if value.get('source_qualification_sha256') != data['source_qualification_sha256']:
        raise ValueError('Stale qualification identity')
    if value['source_qualification_sha256'] != sha(TRAIN / 'results/procedural-vertical-slice-v18-focused.json'):
        raise ValueError('Stale qualification receipt')
    if value.get('reviewer') != {'id': 'Axlbot', 'experience': '10+ years'}:
        raise ValueError('Unexpected reviewer metadata')
    exported = datetime.fromisoformat(value['exported_utc'].replace('Z', '+00:00'))
    cases = value.get('cases', [])
    expected = {c['id']: c for c in data['cases']}
    if len(cases) != 16 or len({c['id'] for c in cases}) != 16 or set(expected) != {c['id'] for c in cases}:
        raise ValueError('Missing, duplicate or unexpected cases')
    summary = []
    for case in cases:
        rating, identity = case['rating'], expected[case['id']]['reveal']
        if case['revealed_identity'] != identity:
            raise ValueError('Changed blind identity mapping')
        if rating.get('locked') is not True or rating.get('blind_at_rating') is not True or rating.get('reveal_seen') is not True or rating.get('history'):
            raise ValueError('Expected original locked blind rating')
        if datetime.fromisoformat(rating['locked_utc'].replace('Z', '+00:00')) > exported:
            raise ValueError('Lock after export')
        values = rating['values']
        for dimension in ('naturalness', 'contact', 'continuity', 'intent'):
            for label in ('A', 'B'):
                if values.get(dimension + label) not in ('1', '2', '3', '4', '5'):
                    raise ValueError('Missing/invalid score')
        for label in ('A', 'B'):
            if values.get('acceptable' + label) not in ('yes', 'no'):
                raise ValueError('Missing acceptability')
            for field in ('corrections', 'interactions'):
                estimate = values.get(field + label)
                if not isinstance(estimate, str) or (estimate != '' and not re.fullmatch(r'\d{1,3}', estimate)):
                    raise ValueError('Invalid optional estimate')
            blend = (ROOT / identity[label]['blend_path']).resolve()
            if not blend.is_relative_to(ROOT.resolve()) or sha(blend) != identity[label]['blend_sha256'] or sha(blend.parent / 'report.json') != identity[label]['report_sha256']:
                raise ValueError('Stale/out-of-scope native scene identity')
        if values.get('preference') not in ('A', 'B', 'tie', 'neither') or not isinstance(values.get('notes'), str):
            raise ValueError('Invalid preference/notes')
        candidate = next(k for k, ident in identity.items() if ident['variant'] == 'candidate')
        baseline = 'B' if candidate == 'A' else 'A'
        preference = values['preference']
        summary.append(dict(id=case['id'], candidate_acceptable=values['acceptable' + candidate] == 'yes',
            baseline_acceptable=values['acceptable' + baseline] == 'yes',
            preference=('candidate' if preference == candidate else 'baseline' if preference == baseline else preference), notes=values['notes']))
    if require_capture and canonical_hash(value) != CAPTURE_HASH:
        raise ValueError('Human capture differs from visible browser export')
    return dict(schema='b4ml-human-review-summary-v2', complete=True, cases=summary,
        candidate_acceptable=sum(c['candidate_acceptable'] for c in summary),
        baseline_acceptable=sum(c['baseline_acceptable'] for c in summary),
        preferences={k: sum(c['preference'] == k for c in summary) for k in ('candidate', 'baseline', 'tie', 'neither')},
        export_sha256=sha(EXPORT), canonical_capture_sha256=CAPTURE_HASH,
        identity_receipt='not established by reviewer display name', training_authorized=False,
        model_promotion_authorized=False, full_goal_complete=False,
        scope='Ratings describe the exact v2 browser representation; not a native scene usability pass.')


if __name__ == '__main__':
    result = validate()
    destination = REVIEW / 'human-review-summary-v2.json'
    with destination.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
    print(json.dumps(result, indent=2))
