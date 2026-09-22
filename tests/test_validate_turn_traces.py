import copy
import unittest
from tools.validate_turn_traces import validate

STATES=["TRACE_DURABLY_RECORDED","TRACE_INTERMEDIATE_DELIVERED","TRACE_FINAL_FLUSH_DELIVERED"]
BASE={"schema_version":"1.0","active_run_id":"RUN-X","authority_epoch":1,"delivery_states":STATES,
 "rules":{"durable_before_delivery":True,"trace_is_never_close_authority":True,"unit_trace_requires_artifact_backed_work_evidence":True,"delivery_must_not_be_inferred":True,"final_flush_required_for_undelivered_traces":True},
 "traces":[{"trace_id":"T1","kind":"BOUNDED_SUBSTANTIVE_UNIT","created_at":"2026-09-22T11:00:00+09:00","message":"완료: test (duration 1s)","delivery_state":"TRACE_DURABLY_RECORDED","evidence":["x@y"]}]}

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
    def test_chronological_order_required(self):
        d=copy.deepcopy(BASE); x=copy.deepcopy(d["traces"][0]); x["trace_id"]="T2"; x["created_at"]="2026-09-22T10:59:59+09:00"; d["traces"].append(x); self.assertTrue(validate(d))
    def test_final_flush_must_be_terminal_delivery_phase(self):
        d=copy.deepcopy(BASE); d["traces"][0]["delivery_state"]="TRACE_FINAL_FLUSH_DELIVERED"; x=copy.deepcopy(d["traces"][0]); x["trace_id"]="T2"; x["created_at"]="2026-09-22T11:00:01+09:00"; x["delivery_state"]="TRACE_DURABLY_RECORDED"; d["traces"].append(x); self.assertTrue(validate(d))
    def test_delivery_safety_rules_required(self):
        d=copy.deepcopy(BASE); d["rules"]["delivery_must_not_be_inferred"]=False; self.assertTrue(validate(d))
    def test_declared_states_cannot_drift(self):
        d=copy.deepcopy(BASE); d["delivery_states"].remove("TRACE_FINAL_FLUSH_DELIVERED"); self.assertTrue(validate(d))
    def test_active_identity_required(self):
        d=copy.deepcopy(BASE); d["active_run_id"]=""; self.assertTrue(validate(d))

if __name__=="__main__": unittest.main()
