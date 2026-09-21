"""Record reconstruction isolation, bounds, malformed inputs and host lifetime."""
from pathlib import Path
import os, sys, json, math, unittest, tracemalloc
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get('B4ML_PACKAGE', str(ROOT)), str(ROOT/'tests')]
from b4artists_ml.record_cache import RecordCopies


class RecordCopyTests(unittest.TestCase):
    def test_fresh_nested_trees_preserve_primitive_values(self):
        payload = json.dumps(dict(schema=1, data=[{'unicode':'???', 'big':2**100,
            'float':-0.0, 'bool':True, 'none':None, 'array':[1, 2]}]))
        cache = RecordCopies(); first = cache.read(payload); second = cache.read(payload)
        self.assertEqual(first, second); self.assertIsNot(first, second)
        self.assertIsNot(first['data'][0], second['data'][0])
        first['data'][0]['array'][0] = 9
        self.assertEqual(cache.read(payload), second)
        self.assertEqual(math.copysign(1, second['data'][0]['float']), -1)

    def test_exact_key_change_and_reversion(self):
        cache = RecordCopies(); a = '{"schema":1,"value":[1]}'
        b = '{"schema":1,"value":[2]}'; spaced = '{ "schema": 1, "value": [1] }'
        self.assertEqual(cache.read(a)['value'], [1]); cache.read(b); cache.read(spaced)
        self.assertEqual(len(cache._entries), 3)
        self.assertEqual(cache.read(a)['value'], [1])

    def test_invalid_json_schema_and_top_level_are_not_cached(self):
        cache = RecordCopies(); good = '{"schema":1}'
        cache.read(good); before = list(cache._entries); size = cache.retained_bytes
        for bad in ('{', 'null', '[]', '1', '"text"', '{}', '{"schema":2}'):
            for _ in range(2):
                with self.assertRaises(ValueError): cache.read(bad)
            self.assertEqual(list(cache._entries), before)
            self.assertEqual(cache.retained_bytes, size)

    def test_original_bytes_and_nonfinite_parse_semantics_retained(self):
        cache = RecordCopies(); value = b'{"schema":1,"x":[NaN,Infinity,-Infinity]}'
        a = cache.read(value); self.assertTrue(math.isnan(a['x'][0]))
        self.assertEqual(a['x'][1:], [math.inf, -math.inf]); self.assertFalse(cache._entries)
        text = value.decode(); cache.read(text); b = cache.read(text)
        self.assertTrue(math.isnan(b['x'][0])); self.assertEqual(b['x'][1:], a['x'][1:])
        with self.assertRaises(TypeError): cache.read(None)
        with self.assertRaises(UnicodeDecodeError): cache.read(b'\xff')

    def test_lru_eviction_reconstructs_original_after_mutation(self):
        cache = RecordCopies(); rows = [json.dumps(dict(schema=1, x=[i])) for i in range(5)]
        for row in rows[:4]: cache.read(row)
        cache.read(rows[0])['x'][0] = 99; cache.read(rows[4])
        self.assertEqual(len(cache._entries), 4); self.assertNotIn(rows[1], cache._entries)
        self.assertIn(rows[0], cache._entries); self.assertEqual(cache.read(rows[1])['x'], [1])

    def test_oversized_payload_and_blob_bypass(self):
        payload = '{"schema":1,"x":[1,2,3]}'
        for limit in ('MAX_PAYLOAD_CHARACTERS', 'MAX_BLOB_BYTES', 'MAX_RETAINED_BYTES'):
            cache = RecordCopies()
            with patch.object(cache, limit, 1):
                self.assertEqual(cache.read(payload), json.loads(payload))
                self.assertFalse(cache._entries); self.assertEqual(cache.retained_bytes, 0)

    def test_encoder_limits_fall_back_without_caching(self):
        cache = RecordCopies(); payload = '{"schema":1,"x":[1,2]}'
        for error in (ValueError, OverflowError, RecursionError):
            with patch('b4artists_ml.record_cache.marshal.dumps', side_effect=error):
                self.assertEqual(cache.read(payload), json.loads(payload))
                self.assertFalse(cache._entries)

    def test_memory_accounting_eviction_and_clear(self):
        cache = RecordCopies()
        for i in range(12):
            payload = json.dumps(dict(schema=1, text='???'*60000, index=i), ensure_ascii=False)
            cache.read(payload)
            self.assertLessEqual(len(cache._entries), 4)
            self.assertEqual(cache.retained_bytes, sum(sys.getsizeof(k)+sys.getsizeof(v)
                for k,v in cache._entries.items()))
            self.assertLessEqual(cache.retained_bytes, cache.MAX_RETAINED_BYTES)
        cache.clear(); self.assertFalse(cache._entries); self.assertEqual(cache.retained_bytes, 0)

    def test_total_byte_budget_evicts_before_entry_limit(self):
        cache = RecordCopies()
        with patch.object(cache, 'MAX_RETAINED_BYTES', 3000):
            for i in range(6):
                cache.read(json.dumps(dict(schema=1, x='a'*1000, i=i)))
                self.assertLessEqual(cache.retained_bytes, 3000)
            self.assertEqual(len(cache._entries), 1)

    def test_measured_retained_allocation_stays_bounded_and_releases(self):
        cache = RecordCopies(); tracemalloc.start()
        try:
            baseline = tracemalloc.get_traced_memory()[0]
            for i in range(24):
                payload = json.dumps(dict(schema=1, x='a'*480000, i=i))
                record = cache.read(payload)
                del payload, record
            retained, peak = tracemalloc.get_traced_memory()
            self.assertLess(retained-baseline, cache.MAX_RETAINED_BYTES+65536)
            self.assertLess(peak-baseline, 10*1024*1024)
            cache.clear()
            self.assertLess(tracemalloc.get_traced_memory()[0]-baseline, 65536)
        finally: tracemalloc.stop()


class RecordCacheHostTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_b4artists_ml_body_live import LivePoseTests
        LivePoseTests.setUpClass(); cls.helper = LivePoseTests()
    def tearDown(self): self.helper.tearDown()

    def test_finish_discards_cache_and_preserves_source(self):
        import bpy
        from b4artists_ml import body_preview as body, workflow as w
        ob, source, *_ = self.helper.fixture()
        body._read(ob); self.assertTrue(body._RECORDS._entries)
        body.finish(ob, bpy.context.scene, False)
        self.assertEqual(w.raw_pose(ob), source)
        self.assertFalse(body._RECORDS._entries)

    def test_reset_and_save_clear_cache_with_pending_preview(self):
        from b4artists_ml import body_preview as body
        ob, *_ = self.helper.fixture(); original = ob.b4ml.body_payload
        for callback in (body.reset_runtime, body.before_save):
            body._read(ob); self.assertTrue(body._RECORDS._entries)
            callback(); self.assertFalse(body._RECORDS._entries)
            self.assertEqual(ob.b4ml.body_payload, original)
            self.assertEqual(body._read(ob), json.loads(original))

    def test_lifecycle_handlers_and_unregister_release_records(self):
        import bpy
        from b4artists_ml import body_preview as body
        for name in ('load_pre','undo_pre','redo_pre'):
            self.assertIn(body.reset_runtime, getattr(bpy.app.handlers,name))
        self.assertIn(body.before_save, bpy.app.handlers.save_pre)
        body._decode('{"schema":1,"test":[1]}')
        body.unregister(); self.assertFalse(body._RECORDS._entries)
        body.register()

    def test_malformed_payload_stops_live_and_preserves_preview(self):
        from b4artists_ml import body_preview as body, body_live as live, workflow as w
        ob, *_ = self.helper.fixture(); body.solve(ob); before = w.raw_pose(ob)
        original = ob.b4ml.body_payload; live.start(ob, now=0.)
        body._read(ob); ob.b4ml.body_payload='[]'
        try:
            with self.assertRaisesRegex(ValueError, 'Unsupported whole-body preview record'):
                live.tick(ob, now=.02)
            self.assertFalse(ob.b4ml.body_live); self.assertFalse(body._JOBS)
            self.assertEqual(w.raw_pose(ob), before)
        finally: ob.b4ml.body_payload=original


if __name__ == '__main__': unittest.main()
