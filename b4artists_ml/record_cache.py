"""Bounded, independent copies of persistent whole-body JSON records.
SPDX-License-Identifier: GPL-2.0-or-later
"""
from collections import OrderedDict
import json
import marshal
import sys


class RecordCopies:
    """Retain only locally encoded primitives, never external binary data.

    Each hit reconstructs a fresh tree. The original JSON string is the exact
    key, so a changed or restored payload cannot return another payload's data.
    No Blender object, pointer or mutable record survives in this cache.
    """
    MAX_ENTRIES = 4
    MAX_PAYLOAD_CHARACTERS = 524288
    MAX_BLOB_BYTES = 1048576
    MAX_RETAINED_BYTES = 4194304

    def __init__(self):
        self._entries = OrderedDict()
        self.retained_bytes = 0

    @staticmethod
    def _parse(payload):
        record = json.loads(payload)
        if not isinstance(record, dict) or record.get('schema') != 1:
            raise ValueError('Unsupported whole-body preview record')
        return record

    def read(self, payload):
        if not isinstance(payload, str) or len(payload) > self.MAX_PAYLOAD_CHARACTERS:
            return self._parse(payload)
        cached = self._entries.get(payload)
        if cached is not None:
            self._entries.move_to_end(payload)
            # Blob comes only from our successful JSON parse and local dumps.
            return marshal.loads(cached)
        record = self._parse(payload)
        try:
            blob = marshal.dumps(record)
        except (ValueError, OverflowError, RecursionError):
            # An implementation limit in the optimization must not reject JSON
            # that the original decoder can read (for example, a deep tree).
            return record
        size = sys.getsizeof(payload) + sys.getsizeof(blob)
        if len(blob) > self.MAX_BLOB_BYTES or size > self.MAX_RETAINED_BYTES:
            return record
        while self._entries and (len(self._entries) >= self.MAX_ENTRIES or
                                 self.retained_bytes + size > self.MAX_RETAINED_BYTES):
            old_key, old_blob = self._entries.popitem(last=False)
            self.retained_bytes -= sys.getsizeof(old_key) + sys.getsizeof(old_blob)
        self._entries[payload] = blob
        self.retained_bytes += size
        return record

    def clear(self):
        self._entries.clear()
        self.retained_bytes = 0
