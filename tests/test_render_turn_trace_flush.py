import copy
import unittest
from tools.render_turn_trace_flush import pending_messages
from tests.test_validate_turn_traces import BASE

class RenderTraceFlushTests(unittest.TestCase):
    def test_pending_is_rendered(self): self.assertEqual(len(pending_messages(copy.deepcopy(BASE))),1)
    def test_intermediate_delivered_is_not_repeated(self):
        d=copy.deepcopy(BASE); d["traces"][0]["delivery_state"]="TRACE_INTERMEDIATE_DELIVERED"; self.assertEqual(pending_messages(d),[])
    def test_order_is_preserved(self):
        d=copy.deepcopy(BASE); x=copy.deepcopy(d["traces"][0]); x["trace_id"]="T2"; x["created_at"]="2026-09-22T11:00:01+09:00"; x["message"]="완료: second (duration 1s)"; d["traces"].append(x); self.assertEqual(pending_messages(d),[d["traces"][0]["message"],x["message"]])

if __name__=="__main__": unittest.main()
