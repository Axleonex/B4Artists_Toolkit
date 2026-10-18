"""Compare the All row of this source with the 12.9.1 ZIP: the tabs-versus-stage-button
choice and the tools shown, across 2,232 layouts (186 widths 250-2100 px, UI scales
1/1.5/2, two text widths, Recommended and every-12.9.1-tool-visible layouts).

Run from the repository root:  python docs/anim_assist/plans/2026-10-17-stage-toolsets/compare_all_row.py
"""
import ast
import copy
import types
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def literals(text, names):
    out = {}
    for node in ast.parse(text).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in names:
                    out[target.id] = ast.literal_eval(node.value)
    return out


def model(config_text, catalog_text):
    module = types.ModuleType('config')
    exec(compile(config_text, 'timeline_config.py', 'exec'), module.__dict__)
    values = literals(catalog_text, {'ACTIONS', 'QUICK_LABELS', 'GROUPS'})
    if hasattr(module, 'register_families'):
        module.register_families(values['GROUPS'])
    return module, values


zip_ = zipfile.ZipFile(ROOT / 'releases/b4_anim_assist_v12.9.1.zip')
old, old_values = model(zip_.read('B4_anim_assist/ui/timeline_config.py').decode(),
                        zip_.read('B4_anim_assist/ui/timeline_catalog.py').decode())
old_labels = {**old_values['QUICK_LABELS'], 'COPY_KEYS': 'Copy', 'PASTE_KEYS': 'Paste',
              'MIRROR_SELECTED': 'Mirror', 'BAKE_STEP': 'Bake Object', 'TRAIL_SHOW': 'Trails'}
new, new_values = model((ROOT / 'anim_assist/ui/timeline_config.py').read_text(encoding='utf-8'),
                        (ROOT / 'anim_assist/ui/timeline_catalog.py').read_text(encoding='utf-8'))
overlay = literals((ROOT / 'anim_assist/ui/timeline_overlay.py').read_text(encoding='utf-8'), {'ROW_LABELS', 'ALL_ROW_LABELS'})
new_labels = {**new_values['QUICK_LABELS'], **overlay['ROW_LABELS'], **overlay.get('ALL_ROW_LABELS', {})}
shared = set(old_values['ACTIONS'])


def records(module, values, every):
    record = module.recommended(values['ACTIONS'])
    if every:
        for action, tool in record['active']['tools'].items():
            tool['mode'] = ('INLINE' if action in module.SLIDERS else 'BUTTON') if action in shared else 'HIDDEN'
    return record


def run(module, values, labels, record, width, scale, char):
    items = module.toolbar_layout(width, 120 * scale, 28 * scale, False, copy.deepcopy(record),
                                  values['GROUPS'], labels, lambda t: len(t) * char * scale, 'ALL')
    lead = 'TABS' if any(i[0] == 'STAGE' for i in items) else 'BUTTON'
    tools = [i[1] for i in items if i[0] in {'ACTION', 'SLIDER', 'POPOUT', 'PRESET'}]
    return lead, tools


total = lead_same = tools_same = 0
diffs = []
for every in (False, True):
    old_record, new_record = records(old, old_values, every), records(new, new_values, every)
    for scale in (1, 1.5, 2):
        for char in (6, 7):
            for width in range(250, 2101, 10):
                a = run(old, old_values, old_labels, old_record, width, scale, char)
                b = run(new, new_values, new_labels, new_record, width, scale, char)
                total += 1
                lead_same += a[0] == b[0]
                tools_same += a[1] == b[1]
                if a[1] != b[1]:
                    diffs.append((every, scale, char, width, len(a[1]), len(b[1])))
print(f'layouts {total}; same tabs-or-button choice {lead_same}; same tools {tools_same}')
fewer = sum(1 for d in diffs if d[5] < d[4])
print(f'differ {len(diffs)}: fewer tools in {fewer}, more in {sum(1 for d in diffs if d[5] > d[4])}, '
      f'same count but different tools in {sum(1 for d in diffs if d[5] == d[4])}')
print('widest differing row:', max((d[3] * d[1] for d in diffs), default=0), 'px')
