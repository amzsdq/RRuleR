import importlib.util
import pathlib
import unittest
MODULE_PATH=pathlib.Path(__file__).parents[1]/"tools"/"validate_work_evidence.py"
spec=importlib.util.spec_from_file_location("validate_work_evidence",MODULE_PATH); validator=importlib.util.module_from_spec(spec); spec.loader.exec_module(validator)
def rec(start,end,qualification="SUBSTANTIVE_ACCEPTED",start_boundary="OBSERVED",end_boundary="OBSERVED"):
    return {"start_at":start,"end_at":end,"kind":"implementation_or_refactor","artifact":"tools/example.py@commit","qualification":qualification,"basis":"material behavior change","start_boundary":start_boundary,"end_boundary":end_boundary}
class WorkEvidenceValidatorTests(unittest.TestCase):
    def test_rejects_inferred_boundary(self):
        self.assertIn("BOUNDARY_NOT_OBSERVED",validator.validate_record(rec("2026-09-21T05:00:00+09:00","2026-09-21T05:10:00+09:00",start_boundary="INFERRED")))
    def test_rejects_candidate_qualification(self):
        self.assertIn("NOT_SUBSTANTIVE_ACCEPTED",validator.validate_record(rec("2026-09-21T05:00:00+09:00","2026-09-21T05:10:00+09:00",qualification="CANDIDATE_ONLY")))
    def test_incomplete_window_is_not_rejected_or_promoted(self):
        data={"records":[rec("2026-09-21T05:00:00+09:00","2026-09-21T05:07:00+09:00")]}
        out=validator.audit(data,"2026-09-21T05:00:00+09:00","2026-09-21T05:10:00+09:00")
        self.assertEqual(out["promotion"],"INCOMPLETE"); self.assertIn("WINDOW_NOT_YET_COMPLETE",out["window"]["reasons"])
    def test_accepts_complete_window_with_small_classified_gap(self):
        data={"records":[rec("2026-09-21T05:00:00+09:00","2026-09-21T05:07:00+09:00"),rec("2026-09-21T05:08:00+09:00","2026-09-21T05:15:00+09:00")]}
        out=validator.audit(data,"2026-09-21T05:00:00+09:00","2026-09-21T05:15:00+09:00"); self.assertEqual(out["window"]["useful_seconds"],840); self.assertEqual(out["window"]["maximum_unexplained_gap_seconds"],60); self.assertEqual(out["promotion"],"VALID_ACCEPTED")
    def test_rejects_gap_above_120(self):
        data={"records":[rec("2026-09-21T05:00:00+09:00","2026-09-21T05:06:00+09:00"),rec("2026-09-21T05:09:00+09:00","2026-09-21T05:15:00+09:00")]}
        out=validator.audit(data,"2026-09-21T05:00:00+09:00","2026-09-21T05:15:00+09:00"); self.assertIn("UNEXPLAINED_GAP_GT_120_SECONDS",out["window"]["reasons"]); self.assertEqual(out["promotion"],"REJECTED")
    def test_rejects_overlap_ambiguity(self):
        data={"records":[rec("2026-09-21T05:00:00+09:00","2026-09-21T05:08:00+09:00"),rec("2026-09-21T05:07:00+09:00","2026-09-21T05:15:00+09:00")]}
        out=validator.audit(data,"2026-09-21T05:00:00+09:00","2026-09-21T05:15:00+09:00"); self.assertTrue(out["overlap_errors"]); self.assertEqual(out["promotion"],"REJECTED")
if __name__=="__main__": unittest.main()
