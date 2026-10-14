import importlib.util
from pathlib import Path
import unittest

path=Path(__file__).resolve().parents[1]/'anim_assist/core/timeline_slider_session.py'
spec=importlib.util.spec_from_file_location('slider_session',path)
session=importlib.util.module_from_spec(spec); spec.loader.exec_module(session)


class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.value=7
        self.valid=True
        self.tx=session.Transaction(lambda:setattr(self,'value',7),
            lambda v:setattr(self,'value',self.value+v),lambda:self.valid)

    def test_absolute_preview(self):
        for n in range(30): self.tx.preview(n)
        self.assertEqual(self.value,36)
        self.tx.preview(2)
        self.assertEqual(self.value,9)

    def test_cancel(self):
        self.tx.preview(100); self.tx.cancel(); self.tx.cancel()
        self.assertEqual(self.value,7)
        with self.assertRaises(ValueError): self.tx.preview(2)

    def test_commit(self):
        self.tx.preview(3); self.tx.commit(); self.tx.cancel()
        self.assertEqual(self.value,10)

    def test_invalid_target(self):
        self.valid=False
        with self.assertRaises(ValueError): self.tx.preview(3)
        self.assertEqual(self.value,7)

    def test_exception_restores(self):
        def broken(v):
            self.value=99
            raise RuntimeError('fixture failure')
        self.tx.apply=broken
        with self.assertRaises(RuntimeError): self.tx.preview(4)
        self.assertEqual(self.value,7)

    def test_nonfinite(self):
        with self.assertRaises(ValueError): self.tx.preview(float('nan'))
        self.assertEqual(self.value,7)


if __name__=='__main__': unittest.main()
