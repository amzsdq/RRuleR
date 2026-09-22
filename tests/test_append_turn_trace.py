import copy
import unittest
from tools.append_turn_trace import append_trace
from tests.test_validate_turn_traces import BASE

class AppendTraceTests(unittest.TestCase):
    def test_append_valid_trace(self):
        t={"trace_id":"T2","kind":"BOUNDED_SUBSTANTIVE_UNIT","created_at":"2026-09-22T11:00:01+09:00","message":"완료: next (duration 1s)","delivery_state":"TRACE_DURABLY_RECORDED","evidence":["a@b"]}
        d=append_trace(copy.deepcopy(BASE),t); self.assertEqual(len(d["traces"]),2)
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError): append_trace(copy.deepcopy(BASE),copy.deepcopy(BASE["traces"][0]))
    def test_out_of_order_rejected(self):
        t={"trace_id":"T2","kind":"BOUNDED_SUBSTANTIVE_UNIT","created_at":"2026-09-22T10:59:59+09:00","message":"완료: old (duration 1s)","delivery_state":"TRACE_DURABLY_RECORDED","evidence":["a@b"]}
        with self.assertRaises(ValueError): append_trace(copy.deepcopy(BASE),t)

if __name__=="__main__": unittest.main()
