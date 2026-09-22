import copy
import unittest
from tools.validate_turn_traces import validate

BASE={
 "schema_version":"1.0",
 "rules":{"durable_before_delivery":True},
 "traces":[{"trace_id":"T1","kind":"BOUNDED_SUBSTANTIVE_UNIT","created_at":"2026-09-22T11:00:00+09:00","message":"완료: test (duration 1s)","delivery_state":"TRACE_DURABLY_RECORDED","evidence":["x@y"]}]
}

class TurnTraceTests(unittest.TestCase):
    def test_valid(self): self.assertEqual(validate(copy.deepcopy(BASE)),[])
    def test_duplicate_id_rejected(self):
        d=copy.deepcopy(BASE); d["traces"].append(copy.deepcopy(d["traces"][0])); self.assertTrue(validate(d))
    def test_delivery_inference_state_rejected(self):
        d=copy.deepcopy(BASE); d["traces"][0]["delivery_state"]="DELIVERED_ASSUMED"; self.assertTrue(validate(d))
    def test_substantive_trace_requires_completion_prefix(self):
        d=copy.deepcopy(BASE); d["traces"][0]["message"]="did work"; self.assertTrue(validate(d))
    def test_evidence_required(self):
        d=copy.deepcopy(BASE); d["traces"][0]["evidence"]=[]; self.assertTrue(validate(d))

if __name__=="__main__": unittest.main()
