import importlib.util
import pathlib
import unittest

MODULE_PATH=pathlib.Path(__file__).parents[1]/"tools"/"validate_work_evidence.py"
spec=importlib.util.spec_from_file_location("validate_work_evidence",MODULE_PATH)
validator=importlib.util.module_from_spec(spec); spec.loader.exec_module(validator)

def rec(start,end,record_id):
    return {"record_id":record_id,"start_at":start,"end_at":end,"kind":"implementation_or_refactor","artifact":"tools/example.py@commit","qualification":"SUBSTANTIVE_ACCEPTED","basis":"material behavior change","start_boundary":"OBSERVED","end_boundary":"OBSERVED"}

class WorkEvidenceSelectionTests(unittest.TestCase):
    def test_four_window_streak_selects_freshest_three(self):
        data={"records":[
            rec("2026-09-21T05:00:00+09:00","2026-09-21T05:14:00+09:00","A"),
            rec("2026-09-21T05:15:00+09:00","2026-09-21T05:29:00+09:00","B"),
            rec("2026-09-21T05:30:00+09:00","2026-09-21T05:44:00+09:00","C"),
            rec("2026-09-21T05:45:00+09:00","2026-09-21T05:59:00+09:00","D") ]}
        out=validator.evaluate_consecutive_windows(data,"2026-09-21T05:00:00+09:00","2026-09-21T06:00:00+09:00")
        self.assertEqual(out["longest_consecutive_accepted"],4)
        self.assertEqual(out["selected_windows"],["2026-09-20T20:15:00+00:00","2026-09-20T20:30:00+00:00","2026-09-20T20:45:00+00:00"])
        self.assertEqual(out["selection_policy"],"FRESHEST_LONGEST_STREAK_THEN_FRESHEST_REQUIRED_WINDOWS")

    def test_equal_length_streak_tie_selects_fresher_streak(self):
        data={"records":[
            rec("2026-09-21T05:00:00+09:00","2026-09-21T05:14:00+09:00","A"),
            rec("2026-09-21T05:15:00+09:00","2026-09-21T05:29:00+09:00","B"),
            rec("2026-09-21T05:30:00+09:00","2026-09-21T05:44:00+09:00","C"),
            rec("2026-09-21T06:00:00+09:00","2026-09-21T06:14:00+09:00","D"),
            rec("2026-09-21T06:15:00+09:00","2026-09-21T06:29:00+09:00","E"),
            rec("2026-09-21T06:30:00+09:00","2026-09-21T06:44:00+09:00","F") ]}
        out=validator.evaluate_consecutive_windows(data,"2026-09-21T05:00:00+09:00","2026-09-21T06:45:00+09:00")
        self.assertEqual(out["longest_consecutive_accepted"],3)
        self.assertEqual(out["selected_windows"],["2026-09-20T21:00:00+00:00","2026-09-20T21:15:00+00:00","2026-09-20T21:30:00+00:00"])

    def test_malformed_first_observed_fails_closed(self):
        out=validator.evaluate_consecutive_windows({"records":[]},"not-a-time","2026-09-21T06:45:00+09:00")
        self.assertEqual(out["p0_acceptance"],"NOT_YET")
        self.assertEqual(out["selected_windows"],[])
        self.assertIsNotNone(out["observation_boundary_error"])

    def test_naive_last_observed_fails_closed(self):
        out=validator.evaluate_consecutive_windows({"records":[]},"2026-09-21T05:00:00+09:00","2026-09-21T06:45:00")
        self.assertEqual(out["p0_acceptance"],"NOT_YET")
        self.assertEqual(out["completed_window_count"],0)
        self.assertIn("timezone",out["observation_boundary_error"])

    def test_reversed_observation_bounds_fail_closed(self):
        out=validator.evaluate_consecutive_windows({"records":[]},"2026-09-21T07:00:00+09:00","2026-09-21T06:45:00+09:00")
        self.assertEqual(out["p0_acceptance"],"NOT_YET")
        self.assertEqual(out["longest_consecutive_accepted"],0)
        self.assertIn("precedes",out["observation_boundary_error"])

if __name__=="__main__": unittest.main()
