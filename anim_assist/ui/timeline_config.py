"""Pure presentation model; layouts contain no scene or gesture state."""
import copy
import json
import math
import uuid

FAMILY_ORDER = ('tween', 'timing', 'curves', 'keys', 'pose', 'bake', 'motion')
MODES = ('HIDDEN', 'BUTTON', 'POPOUT', 'INLINE')
# (label, unit, neutral/default, display minimum, display maximum, hard minimum, hard maximum)
SLIDERS = {
    'DRAG': ('Breakdown', '%', 50., 0., 100., -100., 200.),
    'SMOOTH': ('Smooth', '%', 0., 0., 100., None, None),
    'NEIGHBORS': ('Neighbors', '%', 0., 0., 100., None, None),
    'FRAME': ('Reference', '%', 0., 0., 100., None, None),
    'EASE': ('Ease', '%', 0., 0., 100., None, None),
    'AMPLIFY': ('Push/Pull', '%', 0., -100., 200., None, None),
    'SCALE_DRAG': ('Timing Scale', '%', 100., 50., 200., 1., None),
    'OFFSET_DRAG': ('Timing Offset', 'f', 0., -10., 10., None, None),
}
RECOMMENDED_BUTTONS = {'B25', 'B50', 'B75', 'NUDGE_LEFT', 'NUDGE_RIGHT',
                       'COPY_KEYS', 'PASTE_KEYS', 'MIRROR_SELECTED', 'BAKE_STEP', 'TRAIL_SHOW'}


def tool_default(action):
    entry = dict(action=action, mode='HIDDEN', label_mode='LABEL', width=120.)
    if action in SLIDERS:
        label, unit, default, low, high, _min, _max = SLIDERS[action]
        entry.update(range_min=low, range_max=high, default=default, sensitivity=200.,
                     precision=1, snap_enabled=False, snap_step=1., presets=[],
                     overshoot_enabled=False)
    return entry


def recommended(actions):
    tools = {action: tool_default(action) for action in actions}
    for action in RECOMMENDED_BUTTONS & tools.keys(): tools[action]['mode'] = 'BUTTON'
    for action in ('DRAG', 'SMOOTH'):
        if action in tools: tools[action]['mode'] = 'INLINE'
    if 'SCALE_DRAG' in tools: tools['SCALE_DRAG']['mode'] = 'POPOUT'
    layout = dict(id='recommended', name='Recommended', order=list(actions), tools=tools)
    return dict(schema_version=1, active=layout, active_saved_id='recommended', saved=[])


def finite(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(label+' must be a finite number')
    if abs(value) > 1e8: raise ValueError(label+' is outside the numeric display limit')
    return float(value)


def validate_tool(action, raw):
    if not isinstance(raw, dict): raise ValueError('Tool settings must be an object')
    result = tool_default(action)
    result.update({k: copy.deepcopy(v) for k, v in raw.items() if k in result})
    result['action'] = action
    if result['mode'] not in MODES or (action not in SLIDERS and result['mode'] in {'POPOUT','INLINE'}):
        raise ValueError('This tool does not support the selected display mode')
    if result['label_mode'] not in {'LABEL','ICON'}: raise ValueError('Choose Label or Icon')
    result['width'] = finite(result['width'], 'Slider width')
    if not 80 <= result['width'] <= 240: raise ValueError('Slider width must be 80–240')
    if action not in SLIDERS: return result
    for name in ('range_min','range_max','default','sensitivity','snap_step'):
        result[name] = finite(result[name], name)
    low, high = result['range_min'], result['range_max']
    if low >= high: raise ValueError('Minimum must be below maximum')
    if not low <= result['default'] <= high: raise ValueError('Default must be inside the slider range')
    hard_min, hard_max = SLIDERS[action][-2:]
    if hard_min is not None and low < hard_min: raise ValueError('Minimum is below the tool limit')
    if hard_max is not None and high > hard_max: raise ValueError('Maximum exceeds the tool limit')
    if not 10 <= result['sensitivity'] <= 2000: raise ValueError('Sensitivity must be 10–2000 pixels')
    if result['snap_step'] <= 0: raise ValueError('Snap step must be positive')
    if type(result['precision']) is not int or not 0 <= result['precision'] <= 4:
        raise ValueError('Precision must be 0–4 decimal places')
    for name in ('snap_enabled','overshoot_enabled'):
        if type(result[name]) is not bool: raise ValueError(name+' must be a checkbox')
    if not isinstance(result['presets'], list) or len(result['presets']) > 12:
        raise ValueError('Use at most 12 numeric presets')
    result['presets'] = [finite(v,'Preset') for v in result['presets']]
    if any(not low <= v <= high for v in result['presets']): raise ValueError('Presets must be inside the range')
    return result


def validate_layout(raw, actions):
    if not isinstance(raw, dict) or not isinstance(raw.get('tools'), dict):
        raise ValueError('Layout must contain tool settings')
    if not isinstance(raw.get('id'), str) or not raw['id']: raise ValueError('Layout identity is missing')
    name = validate_name(raw.get('name',''), allow_recommended=True)
    order = raw.get('order', [])
    if not isinstance(order,list) or any(not isinstance(k,str) for k in order) or len(set(order)) != len(order):
        raise ValueError('Tool order must contain unique action IDs')
    tools = {k: validate_tool(k, raw['tools'].get(k,{})) for k in actions}
    # Keep unknown tool records intact, hidden from current UI, for forward compatibility.
    unknown = {k: copy.deepcopy(v) for k,v in raw['tools'].items() if k not in actions}
    tools.update(unknown)
    order = order + [k for k in tools if k not in order]
    return dict(id=raw['id'], name=name, order=order, tools=tools)


def validate(record, actions):
    if not isinstance(record,dict) or type(record.get('schema_version')) is not int or record['schema_version'] != 1:
        raise ValueError('Unsupported toolbar layout version; keep the original settings file')
    saved = record.get('saved')
    if not isinstance(saved,list) or len(saved) > 100: raise ValueError('Layout library must have at most 100 entries')
    active = validate_layout(record.get('active'),actions)
    items = [validate_layout(item,actions) for item in saved]
    identities = [x['id'] for x in items]
    names = [x['name'].casefold() for x in items]
    if len(set(identities)) != len(items) or len(set(names)) != len(items):
        raise ValueError('Saved layouts need unique names and identities')
    if 'recommended' in identities or 'recommended' in names:
        raise ValueError('Recommended is a protected built-in layout')
    selected = record.get('active_saved_id')
    if selected is not None and selected not in ['recommended',*identities]: selected = None
    return dict(schema_version=1,active=active,active_saved_id=selected,saved=items)


def decode(raw, actions):
    if not isinstance(raw,str) or len(raw) > 1_000_000: raise ValueError('Toolbar settings record is too large')
    try: record = json.loads(raw)
    except (ValueError, TypeError) as exc: raise ValueError('Toolbar settings are not valid JSON') from exc
    return validate(record,actions)


def encode(record, actions):
    raw=json.dumps(validate(record,actions),ensure_ascii=False,separators=(',',':'),sort_keys=True,allow_nan=False)
    if len(raw)>1_000_000: raise ValueError('Layout library is too large; remove unused layouts')
    return raw


def from_legacy(actions, selected):
    result = recommended(actions)
    result['active_saved_id'] = None
    result['active'].update(id='custom',name='Custom')
    for key, tool in result['active']['tools'].items():
        tool['mode'] = ('POPOUT' if key in SLIDERS else 'BUTTON') if key in selected else 'HIDDEN'
    return result


def validate_name(name, allow_recommended=False):
    if not isinstance(name,str): raise ValueError('Enter a layout name')
    name = name.strip()
    if not name or len(name)>64: raise ValueError('Use a name with 1–64 characters')
    if not allow_recommended and name.casefold()=='recommended': raise ValueError('Recommended is reserved')
    return name


def save_as(record,name):
    name=validate_name(name)
    if any(x['name'].casefold()==name.casefold() for x in record['saved']):
        raise ValueError('That name already exists; choose another name or Update Saved Layout')
    item=copy.deepcopy(record['active']); item.update(id=uuid.uuid4().hex,name=name)
    record['saved'].append(item)
    record['active']=copy.deepcopy(item); record['active_saved_id']=item['id']


def load(record,ident,actions):
    item=recommended(actions)['active'] if ident=='recommended' else next((x for x in record['saved'] if x['id']==ident),None)
    if item is None: raise ValueError('Choose an existing saved layout')
    record['active']=copy.deepcopy(item); record['active_saved_id']=ident


def update_saved(record):
    ident=record['active_saved_id']
    if ident in {None,'recommended'}: raise ValueError('Use Save As to create your own layout')
    index=next((i for i,x in enumerate(record['saved']) if x['id']==ident),None)
    if index is None: raise ValueError('Saved layout no longer exists')
    record['saved'][index]=copy.deepcopy(record['active'])


def rename(record,ident,name):
    name=validate_name(name)
    if ident=='recommended': raise ValueError('Recommended cannot be renamed')
    if any(x['id']!=ident and x['name'].casefold()==name.casefold() for x in record['saved']):
        raise ValueError('That layout name already exists')
    item=next((x for x in record['saved'] if x['id']==ident),None)
    if item is None: raise ValueError('Choose an existing saved layout')
    item['name']=name
    if record['active_saved_id']==ident: record['active']['name']=name


def delete(record,ident):
    if ident=='recommended': raise ValueError('Recommended cannot be deleted')
    if not any(x['id']==ident for x in record['saved']): raise ValueError('Choose an existing saved layout')
    record['saved']=[x for x in record['saved'] if x['id']!=ident]
    if record['active_saved_id']==ident:
        record['active_saved_id']=None
        record['active'].update(id='custom',name='Custom')


def modified(record,actions):
    ident=record['active_saved_id']
    if ident is None: return True
    original=recommended(actions)['active'] if ident=='recommended' else next(x for x in record['saved'] if x['id']==ident)
    return record['active'] != original


def value_from_pointer(tool,start_value,delta,precise=False,snap=False):
    scale=(tool['range_max']-tool['range_min'])/tool['sensitivity']
    value=start_value+delta*scale*(.1 if precise else 1.)
    if tool['snap_enabled'] or snap: value=round(value/tool['snap_step'])*tool['snap_step']
    return min(tool['range_max'],max(tool['range_min'],value))


def effective_tool(action,tool):
    result=copy.deepcopy(tool)
    if action in SLIDERS and not tool['overshoot_enabled']:
        result['range_min'],result['range_max']=SLIDERS[action][3:5]
        result['default']=min(result['range_max'],max(result['range_min'],result['default']))
    return result
