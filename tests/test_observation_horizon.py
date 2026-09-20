import importlib.util
import pathlib
import unittest
MODULE_PATH=pathlib.Path(__file__).parents[1]/"tools"/"validate_work_evidence.py"
spec=importlib.util.spec_from_file_location("validate_work_evidence",MODULE_PATH)
validator=importlib.util.module_from_spec(spec); spec.loader.exec_module(validator)

def rec(start,end,record_id):
    return {"record_id":record_id,"start_at":start,"end_at":end,"kind":"implementation_or_refactor","artifact":"tools/example.py@commit","qualification":"SUBSTANTIVE_ACCEPTED","basis":"material behavior change","start_boundary":"OBSERVED","end_boundary":"OBSERVED"}

class ObservationHorizonTests(unittest.TestCase):
    def test_trusted_horizon_preserves_legitimate_60s_trailing_gap(self):
        data={"records":[rec("2026-09-21T05:00:00+09:00","2026-09-21T05:14:00+09:00","A")]}
        out=validator.audit(data,"2026-09-21T05:00:00+09:00","2026-09-21T05:15:00+09:00","2026-09-21T05:15:00+09:00")
        self.assertEqual(out["window"]["useful_seconds"],840)
        self.assertEqual(out["window"]["maximum_unexplained_gap_seconds"],60)
        self.assertEqual(out["promotion"],"VALID_ACCEPTED")

    def test_caller_future_horizon_fails_closed(self):
        data={"records":[rec("2026-09-21T05:00:00+09:00","2026-09-21T05:14:00+09:00","A")]}
        out=validator.audit(data,"2026-09-21T05:00:00+09:00","2026-09-21T05:16:00+09:00","2026-09-21T05:15:00+09:00")
        self.assertEqual(out["promotion"],"REJECTED")
        self.assertEqual(out["window"]["reasons"],["UNTRUSTED_OBSERVATION_HORIZON"])

if __name__=="__main__": unittest.main()
