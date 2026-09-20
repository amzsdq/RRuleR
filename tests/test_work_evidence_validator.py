import importlib.util
import pathlib
import unittest
MODULE_PATH=pathlib.Path(__file__).parents[1]/"tools"/"validate_work_evidence.py"
spec=importlib.util.spec_from_file_location("validate_work_evidence",MODULE_PATH); validator=importlib.util.module_from_spec(spec); spec.loader.exec_module(validator)
def rec(start,end,qualification="SUBSTANTIVE_ACCEPTED",start_boundary="OBSERVED",end_boundary="OBSERVED",observed_seconds=None,record_id=None):
    out={"record_id":record_id or f"WE-{start}-{end}","start_at":start,"end_at":end,"kind":"implementation_or_refactor","artifact":"tools/example.py@commit","qualification":qualification,"basis":"material behavior change","start_boundary":start_boundary,"end_boundary":end_boundary}
    if observed_seconds is not None: out["observed_seconds"]=observed_seconds
    return out
class WorkEvidenceValidatorTests(unittest.TestCase):
    def test_rejects_inferred_boundary(self): self.assertIn("BOUNDARY_NOT_OBSERVED",validator.validate_record(rec("2026-09-21T05:00:00+09:00","2026-09-21T05:10:00+09:00",start_boundary="INFERRED")))
    def test_rejects_candidate_qualification(self): self.assertIn("NOT_SUBSTANTIVE_ACCEPTED",validator.validate_record(rec("2026-09-21T05:00:00+09:00","2026-09-21T05:10:00+09:00",qualification="CANDIDATE_ONLY")))
    def test_rejects_declared_duration_mismatch(self): self.assertIn("OBSERVED_SECONDS_MISMATCH",validator.validate_record(rec("2026-09-21T05:00:00+09:00","2026-09-21T05:01:00+09:00",observed_seconds=61)))
    def test_accepts_matching_declared_duration(self): self.assertNotIn("OBSERVED_SECONDS_MISMATCH",validator.validate_record(rec("2026-09-21T05:00:00+09:00","2026-09-21T05:01:00+09:00",observed_seconds=60)))
    def test_rejects_duplicate_record_identity(self):
        data={"records":[rec("2026-09-21T05:00:00+09:00","2026-09-21T05:07:00+09:00",record_id="DUP"),rec("2026-09-21T05:08:00+09:00","2026-09-21T05:15:00+09:00",record_id="DUP")]}; out=validator.audit(data,"2026-09-21T05:00:00+09:00","2026-09-21T05:15:00+09:00"); self.assertEqual(out["duplicate_record_ids"],["DUP"]); self.assertEqual(out["promotion"],"REJECTED")
    def test_incomplete_window_is_not_rejected_or_promoted(self):
        data={"records":[rec("2026-09-21T05:00:00+09:00","2026-09-21T05:07:00+09:00")]}; out=validator.audit(data,"2026-09-21T05:00:00+09:00","2026-09-21T05:10:00+09:00"); self.assertEqual(out["promotion"],"INCOMPLETE"); self.assertIn("WINDOW_NOT_YET_COMPLETE",out["window"]["reasons"])
    def test_accepts_complete_window_with_small_classified_gap(self):
        data={"records":[rec("2026-09-21T05:00:00+09:00","2026-09-21T05:07:00+09:00"),rec("2026-09-21T05:08:00+09:00","2026-09-21T05:15:00+09:00")]}; out=validator.audit(data,"2026-09-21T05:00:00+09:00","2026-09-21T05:15:00+09:00"); self.assertEqual(out["window"]["useful_seconds"],840); self.assertEqual(out["window"]["maximum_unexplained_gap_seconds"],60); self.assertEqual(out["promotion"],"VALID_ACCEPTED")
    def test_rejects_gap_above_120(self):
        data={"records":[rec("2026-09-21T05:00:00+09:00","2026-09-21T05:06:00+09:00"),rec("2026-09-21T05:09:00+09:00","2026-09-21T05:15:00+09:00")]}; out=validator.audit(data,"2026-09-21T05:00:00+09:00","2026-09-21T05:15:00+09:00"); self.assertIn("UNEXPLAINED_GAP_GT_120_SECONDS",out["window"]["reasons"]); self.assertEqual(out["promotion"],"REJECTED")
    def test_rejects_overlap_ambiguity(self):
        data={"records":[rec("2026-09-21T05:00:00+09:00","2026-09-21T05:08:00+09:00"),rec("2026-09-21T05:07:00+09:00","2026-09-21T05:15:00+09:00")]}; out=validator.audit(data,"2026-09-21T05:00:00+09:00","2026-09-21T05:15:00+09:00"); self.assertTrue(out["overlap_errors"]); self.assertEqual(out["promotion"],"REJECTED")
    def test_overlap_does_not_double_count_reported_useful_seconds(self):
        data={"records":[rec("2026-09-21T05:00:00+09:00","2026-09-21T05:10:00+09:00"),rec("2026-09-21T05:05:00+09:00","2026-09-21T05:15:00+09:00")]}; out=validator.audit(data,"2026-09-21T05:00:00+09:00","2026-09-21T05:15:00+09:00"); self.assertEqual(out["window"]["useful_seconds"],900); self.assertEqual(out["window"]["union_interval_count"],1); self.assertIn("OVERLAPPING_INTERVALS",out["window"]["reasons"]); self.assertEqual(out["promotion"],"REJECTED")
    def test_invalid_record_wholly_outside_window_does_not_poison_promotion(self):
        outside=rec("2026-09-21T04:00:00+09:00","2026-09-21T04:01:00+09:00",qualification="CANDIDATE_ONLY"); data={"records":[outside,rec("2026-09-21T05:00:00+09:00","2026-09-21T05:07:00+09:00"),rec("2026-09-21T05:08:00+09:00","2026-09-21T05:15:00+09:00")]}; out=validator.audit(data,"2026-09-21T05:00:00+09:00","2026-09-21T05:15:00+09:00"); self.assertTrue(out["record_results"][0]["errors"]); self.assertNotIn("INVALID_RECORD_PRESENT",out["window"]["reasons"]); self.assertEqual(out["promotion"],"VALID_ACCEPTED")
    def test_invalid_record_intersecting_window_still_fails_closed(self):
        bad=rec("2026-09-21T05:02:00+09:00","2026-09-21T05:03:00+09:00",qualification="CANDIDATE_ONLY"); data={"records":[bad,rec("2026-09-21T05:00:00+09:00","2026-09-21T05:07:00+09:00"),rec("2026-09-21T05:08:00+09:00","2026-09-21T05:15:00+09:00")]}; out=validator.audit(data,"2026-09-21T05:00:00+09:00","2026-09-21T05:15:00+09:00"); self.assertIn("INVALID_RECORD_PRESENT",out["window"]["reasons"]); self.assertEqual(out["promotion"],"REJECTED")
    def test_fixed_window_start_is_deterministic_local_quarter_boundary(self):
        self.assertEqual(validator.fixed_window_start("2026-09-21T05:07:31+09:00").isoformat(),"2026-09-21T05:00:00+09:00"); self.assertEqual(validator.fixed_window_start("2026-09-21T05:15:00+09:00").isoformat(),"2026-09-21T05:15:00+09:00")
    def test_enumerates_only_fully_observed_fixed_windows(self): self.assertEqual(validator.enumerate_completed_fixed_windows("2026-09-21T05:02:00+09:00","2026-09-21T05:46:00+09:00"),["2026-09-21T05:15:00+09:00","2026-09-21T05:30:00+09:00"])
    def test_exact_boundary_allows_that_fixed_window(self): self.assertEqual(validator.enumerate_completed_fixed_windows("2026-09-21T05:00:00+09:00","2026-09-21T05:15:00+09:00"),["2026-09-21T05:00:00+09:00"])
    def test_arbitrary_complete_window_cannot_be_promoted(self):
        data={"records":[rec("2026-09-21T05:01:00+09:00","2026-09-21T05:15:00+09:00"),rec("2026-09-21T05:15:00+09:00","2026-09-21T05:16:00+09:00")]}; out=validator.audit(data,"2026-09-21T05:01:00+09:00","2026-09-21T05:16:00+09:00"); self.assertIn("NON_FIXED_WINDOW_BOUNDARY",out["window"]["reasons"]); self.assertEqual(out["promotion"],"REJECTED")
if __name__=="__main__": unittest.main()
