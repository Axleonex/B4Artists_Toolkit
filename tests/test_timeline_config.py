import ast
import copy
import json
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('timeline_config',ROOT/'anim_assist/ui/timeline_config.py')
config=importlib.util.module_from_spec(spec); spec.loader.exec_module(config)
tree=ast.parse((ROOT/'anim_assist/ui/timeline_catalog.py').read_text(encoding='utf-8'))
actions=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign)
             and any(isinstance(t,ast.Name) and t.id=='ACTIONS' for t in n.targets))
groups=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign)
            and any(isinstance(t,ast.Name) and t.id=='GROUPS' for t in n.targets))
config.register_families(groups)
family={a:k for k,_l,acts in groups for a in acts if a}


class ConfigTests(unittest.TestCase):
    def setUp(self): self.record=config.recommended(actions)

    def test_defaults(self):
        tools=self.record['active']['tools']
        self.assertEqual(len(tools),89)
        self.assertEqual({k for k,v in tools.items() if v['mode']=='INLINE'},{'DRAG','SMOOTH'})
        self.assertEqual(tools['SCALE_DRAG']['mode'],'POPOUT')
        self.assertEqual(len(config.SLIDERS),8)
        self.assertEqual(config.FAMILY_ORDER[:3],('tween','timing','curves'))

    def test_roundtrip(self):
        self.assertEqual(config.decode(config.encode(self.record,actions),actions),self.record)

    def test_invalid_modes(self):
        for action in ('COPY_KEYS','OFFSET','BAKE_STEP'):
            for mode in ('INLINE','POPOUT','invalid'):
                with self.assertRaises(ValueError): config.validate_tool(action,{'mode':mode})

    def test_invalid_numeric(self):
        for value in (float('nan'),float('inf'),True,'50'):
            with self.assertRaises(ValueError): config.validate_tool('DRAG',{'default':value})
        for fields in ({'range_min':100,'range_max':0},{'range_min':-101},
                       {'range_max':201},{'width':40},{'precision':2.5},{'snap_step':0}):
            with self.assertRaises(ValueError): config.validate_tool('DRAG',fields)
        with self.assertRaises(ValueError): config.validate_tool('SCALE_DRAG',{'range_min':0})

    def test_extended_ranges(self):
        self.assertEqual(config.validate_tool('SCALE_DRAG',{'range_max':500})['range_max'],500)
        self.assertEqual(config.validate_tool('SMOOTH',{'range_min':-100,'range_max':200})['range_min'],-100)

    def test_old_selection(self):
        for selected in (set(),{'B25','SMOOTH','OFFSET'}):
            old=config.from_legacy(actions,selected)
            self.assertEqual({k for k,v in old['active']['tools'].items() if v['mode']!='HIDDEN'},selected)
            self.assertEqual(config.decode(config.encode(old,actions),actions),old)

    def test_future_and_bad_records(self):
        before=copy.deepcopy(self.record)
        for raw in ('{}','not json','{"schema_version":3}','{"schema_version":true}'):
            with self.assertRaises(ValueError): config.decode(raw,actions)
        self.assertEqual(self.record,before)

    def test_unknown_records_preserved(self):
        self.record['active']['tools']['FUTURE_TOOL']={'special':42,'mode':'INLINE'}
        result=config.decode(config.encode(self.record,actions),actions)
        self.assertEqual(result['active']['tools']['FUTURE_TOOL'],{'special':42,'mode':'INLINE'})
        self.assertIn('FUTURE_TOOL',result['active']['order'])

    def test_library(self):
        config.save_as(self.record,' Blocking '); blocking=self.record['active_saved_id']
        self.record['active']['tools']['DRAG']['mode']='POPOUT'
        self.assertTrue(config.modified(self.record,actions))
        config.save_as(self.record,'Polish'); polish=self.record['active_saved_id']
        config.load(self.record,blocking,actions)
        self.assertEqual(self.record['active']['tools']['DRAG']['mode'],'INLINE')
        config.rename(self.record,blocking,'ブロック')
        self.assertEqual(self.record['active']['name'],'ブロック')
        config.delete(self.record,blocking)
        self.assertEqual(self.record['active']['name'],'Custom')
        config.load(self.record,'recommended',actions)
        self.assertEqual(len(self.record['saved']),1)
        self.assertEqual(self.record['saved'][0]['id'],polish)

    def test_name_errors_and_protected_defaults(self):
        config.save_as(self.record,'Blocking')
        for name in ('','   ','x'*65,'blocking','Recommended'):
            before=copy.deepcopy(self.record)
            with self.assertRaises(ValueError): config.save_as(self.record,name)
            self.assertEqual(before,self.record)
        for fn in (lambda:config.delete(self.record,'recommended'),
                   lambda:config.rename(self.record,'recommended','Other')):
            with self.assertRaises(ValueError): fn()

    def test_update_and_deep_copy(self):
        config.save_as(self.record,'One')
        self.record['active']['tools']['DRAG']['presets']=[25,50,75]
        self.assertEqual(self.record['saved'][0]['tools']['DRAG']['presets'],[])
        config.update_saved(self.record)
        self.assertFalse(config.modified(self.record,actions))

    def test_pointer_precision_snap(self):
        tool=config.tool_default('DRAG')
        self.assertEqual(config.value_from_pointer(tool,50,50),75)
        self.assertEqual(config.value_from_pointer(tool,50,50,precise=True),52.5)
        self.assertEqual(config.value_from_pointer(tool,50,10000),100)
        tool['snap_step']=25
        self.assertEqual(config.value_from_pointer(tool,50,60,snap=True),75)

    def test_stage_defaults_match_table(self):
        stages=self.record['active']['stages']
        self.assertEqual(stages['SPLINE']['order'],['REFERENCE','FRAME','NEIGHBORS','EASE','SMOOTH','AMPLIFY',
                                                    'HANDLE_CLAMPED','HANDLE_VECTOR','HANDLE_FREE'])
        self.assertEqual(stages['SPLINE']['tools']['FRAME'],{'mode':'POPOUT','label_mode':'LABEL'})
        self.assertEqual(stages['BLOCK']['tools']['DRAG']['mode'],'INLINE')
        self.assertEqual(stages['POLISH']['tools']['OFFSET_DRAG']['mode'],'INLINE')
        self.assertEqual(len(stages['DELIVER']['order']),8)
        for stage in config.STAGE_KEYS:
            allowed=set(config.stage_families(stage))
            self.assertTrue(all(family[a] in allowed for a in stages[stage]['order']),stage)
            self.assertEqual(stages[stage],config.stage_default(stage))

    def test_v1_migration_keeps_library(self):
        old=copy.deepcopy(self.record); old['schema_version']=1
        old['active'].pop('stages')
        saved=copy.deepcopy(old['active']); saved.update(id='abc',name='Blocking')
        saved['tools']['DRAG']['mode']='POPOUT'; old['saved']=[saved]; old['active_saved_id']='abc'
        result=config.decode(json.dumps(old),actions)
        self.assertEqual(result['schema_version'],2)
        self.assertEqual(result['active_saved_id'],'abc')
        self.assertEqual(result['saved'][0]['name'],'Blocking')
        self.assertEqual(result['saved'][0]['tools']['DRAG']['mode'],'POPOUT')
        self.assertEqual(result['saved'][0]['stages']['BLOCK'],config.stage_default('BLOCK'))
        self.assertEqual(result['active']['tools'],self.record['active']['tools'])

    def test_invalid_stage_rejected(self):
        bad=[('BLOCK',{'order':['B25','B25'],'tools':{'B25':{'mode':'BUTTON'}}}),
             ('BLOCK',{'order':['B25'],'tools':{'B25':{'mode':'INLINE'}}}),
             ('BLOCK',{'order':['TRAIL_SHOW'],'tools':{'TRAIL_SHOW':{'mode':'BUTTON'}}}),
             ('SPLINE',{'order':[],'tools':{'SMOOTH':{'mode':'INLINE'}}})]
        for stage,setup in bad:
            record=copy.deepcopy(self.record); record['active']['stages'][stage]=setup
            with self.assertRaises(ValueError,msg=(stage,setup)): config.validate(record,actions)

    def test_stage_roundtrip_and_modified(self):
        self.assertEqual(config.decode(config.encode(self.record,actions),actions),self.record)
        self.assertFalse(config.modified(self.record,actions))
        config.set_stage_tool(self.record,'SPLINE','SMOOTH',mode='HIDDEN')
        self.assertNotIn('SMOOTH',self.record['active']['stages']['SPLINE']['order'])
        self.assertTrue(config.modified(self.record,actions))
        self.assertEqual(config.decode(config.encode(self.record,actions),actions),self.record)

    def test_reset_stage_only_current(self):
        config.set_stage_tool(self.record,'BLOCK','INBETWEEN',mode='HIDDEN')
        config.set_stage_tool(self.record,'POLISH','SNAP',mode='HIDDEN')
        config.reset_stage(self.record,'BLOCK')
        stages=self.record['active']['stages']
        self.assertEqual(stages['BLOCK'],config.stage_default('BLOCK'))
        self.assertNotIn('SNAP',stages['POLISH']['order'])
        config.load(self.record,'recommended',actions)
        self.assertEqual(self.record['active']['stages']['POLISH'],config.stage_default('POLISH'))

    def test_set_stage_tool_show_hide(self):
        config.set_stage_tool(self.record,'BLOCK','INBETWEEN',mode='HIDDEN')
        config.set_stage_tool(self.record,'BLOCK','INBETWEEN',mode='BUTTON')
        order=self.record['active']['stages']['BLOCK']['order']
        self.assertEqual([a for a in order if family[a]=='tween'][-1],'INBETWEEN')
        self.assertLess(order.index('INBETWEEN'),order.index('RANGE'))
        config.set_stage_tool(self.record,'BLOCK','GROW_BOTH',mode='BUTTON')
        self.assertEqual([a for a in order if family[a]=='keys'][-1],'GROW_BOTH')
        config.set_stage_tool(self.record,'ALL','B25',mode='HIDDEN')
        self.assertEqual(self.record['active']['tools']['B25']['mode'],'HIDDEN')
        self.assertIn('B25',order)

    def test_pin_target(self):
        self.assertEqual(config.pin_target('BLOCK','BAKE_STEP'),'ALL')
        self.assertEqual(config.pin_target('BLOCK','INBETWEEN'),'BLOCK')
        self.assertEqual(config.pin_target('ALL','INBETWEEN'),'ALL')

    def test_entries_round_trip_per_stage(self):
        entries=config.stage_entries(self.record,'BLOCK',actions)
        self.assertEqual({family[e['action']] for e in entries},{'tween','keys'})
        self.assertEqual([e['action'] for e in entries][:3],['B25','B50','B75'])
        by={e['action']:e for e in entries}
        hold=entries.pop([e['action'] for e in entries].index('TYPE_HOLD'))
        entries.insert([e['action'] for e in entries].index('RANGE'),hold)
        by['INBETWEEN']['mode']='HIDDEN'; by['DRAG']['width']=150.
        before_all=copy.deepcopy(self.record['active']['order'])
        polish=copy.deepcopy(self.record['active']['stages']['POLISH'])
        config.apply_entries(self.record,'BLOCK',entries,actions)
        order=self.record['active']['stages']['BLOCK']['order']
        self.assertLess(order.index('TYPE_HOLD'),order.index('RANGE'))
        self.assertNotIn('INBETWEEN',order)
        self.assertEqual(self.record['active']['tools']['DRAG']['width'],150.)
        self.assertEqual(self.record['active']['order'],before_all)
        self.assertEqual(self.record['active']['stages']['POLISH'],polish)
        self.assertEqual(len(config.stage_entries(self.record,'ALL',actions)),89)
        config.validate(self.record,actions)

    def test_future_stage_tools_survive_settings(self):
        self.record['active']['tools']['FUTURE']={'mode':'BUTTON'}
        self.record['active']['stages']['BLOCK']['order'].append('FUTURE')
        self.record['active']['stages']['BLOCK']['tools']['FUTURE']={'mode':'BUTTON','extra':1}
        record=config.validate(self.record,actions)
        config.apply_entries(record,'BLOCK',config.stage_entries(record,'BLOCK',actions),actions)
        self.assertIn('FUTURE',record['active']['stages']['BLOCK']['order'])
        self.assertEqual(record['active']['stages']['BLOCK']['tools']['FUTURE'],{'mode':'BUTTON','extra':1})

    def test_malformed_unknown_stage_tool_rejected(self):
        for setup in ({'order':['FUTURE'],'tools':{'FUTURE':[1]}},{'order':[],'tools':{'FUTURE':'x'}}):
            record=copy.deepcopy(self.record); record['active']['stages']['BLOCK']=setup
            with self.assertRaises(ValueError): config.validate(record,actions)

    def test_hundred_layouts_fit(self):
        for index in range(100):
            config.save_as(self.record,f'Layout {index}')
        self.assertLessEqual(len(config.encode(self.record,actions)),config.RECORD_LIMIT)


if __name__=='__main__': unittest.main()
