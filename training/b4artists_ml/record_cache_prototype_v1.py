"""Research-only exact-payload cache of locally encoded JSON primitive records."""
from collections import OrderedDict
import marshal
class RecordCopies:
 def __init__(self,decode,entries=4,payload_characters=524288,blob_bytes=1048576):
  self.decode=decode;self.entries=entries;self.payload_characters=payload_characters;self.blob_bytes=blob_bytes;self.cache=OrderedDict();self.hits=self.misses=0
 def __call__(self,payload):
  if not isinstance(payload,str) or len(payload)>self.payload_characters:return self.decode(payload)
  if payload in self.cache:
   self.hits+=1;blob=self.cache.pop(payload);self.cache[payload]=blob;return marshal.loads(blob)
  self.misses+=1;record=self.decode(payload)
  # Only primitive trees returned by our original JSON decoder enter this encoder.
  # No external binary blob is accepted or persisted.
  blob=marshal.dumps(record)
  if len(blob)<=self.blob_bytes:
   self.cache[payload]=blob
   while len(self.cache)>self.entries:self.cache.popitem(last=False)
  return record
 def clear(self):self.cache.clear()
def install():
 from b4artists_ml import body_preview
 cache=RecordCopies(body_preview._decode);body_preview._decode=cache;return cache
