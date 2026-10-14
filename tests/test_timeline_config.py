import ast
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('timeline_config',ROOT/'anim_assist/ui/timeline_config.py')
config=importlib.util.module_from_spec(spec); spec.loader.exec_module(config)
tree=ast.parse((ROOT/'anim_assist/ui/timeline_catalog.py').read_text(encoding='utf-8'))
actions=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign)
             and any(isinstance(t,ast.Name) and t.id=='ACTIONS' for t in n.targets))


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
        for raw in ('{}','not json','{"schema_version":2}','{"schema_version":true}'):
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


if __name__=='__main__': unittest.main()
