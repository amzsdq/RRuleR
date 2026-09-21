import unittest
from tools.validate_observation_horizon import provenance_record, validate

POLICY = {"accepted_provenance_kinds": ["GITHUB_ACTIONS_OBSERVED_TIMESTAMP"]}

def horizon(ref, trusted, history=None):
    return {"provenance_kind":"GITHUB_ACTIONS_OBSERVED_TIMESTAMP","provenance_ref":ref,"provenance_attempt":1,"trusted_observed_through":trusted,"provenance_history":list(history or [])}

def source(updated):
    return {"status":"completed","conclusion":"success","run_attempt":1,"updated_at":updated}

def canonical(records):
    return sorted(records, key=lambda r: tuple("" if v is None else str(v) for v in (r.get("provenance_kind"), str(r.get("provenance_ref", "")), r.get("provenance_attempt"), r.get("trusted_observed_through"))))

class ObservationHorizonMergeTests(unittest.TestCase):
    def test_accepts_deterministic_union_of_divergent_parent_histories(self):
        old_a = horizon("100", "2026-09-20T22:00:00+00:00")
        old_b = horizon("101", "2026-09-20T22:01:00+00:00")
        left = horizon("200", "2026-09-20T23:00:00+00:00", [provenance_record(old_a)])
        right = horizon("201", "2026-09-20T23:01:00+00:00", [provenance_record(old_b)])
        records = canonical([provenance_record(old_a), provenance_record(old_b), provenance_record(left), provenance_record(right)])
        current = horizon("300", "2026-09-20T23:05:48+00:00", records)
        self.assertTrue(validate(current, POLICY, source("2026-09-20T23:05:48Z"), previous_states=[left, right]))

    def test_rejects_merge_that_drops_one_parent_history(self):
        old_a = horizon("100", "2026-09-20T22:00:00+00:00")
        old_b = horizon("101", "2026-09-20T22:01:00+00:00")
        left = horizon("200", "2026-09-20T23:00:00+00:00", [provenance_record(old_a)])
        right = horizon("201", "2026-09-20T23:01:00+00:00", [provenance_record(old_b)])
        records = canonical([provenance_record(old_a), provenance_record(left), provenance_record(right)])
        current = horizon("300", "2026-09-20T23:05:48+00:00", records)
        with self.assertRaisesRegex(ValueError, "lost required merge-parent"):
            validate(current, POLICY, source("2026-09-20T23:05:48Z"), previous_states=[left, right])

    def test_rejects_nondeterministic_union_order(self):
        left = horizon("200", "2026-09-20T23:00:00+00:00")
        right = horizon("201", "2026-09-20T23:01:00+00:00")
        records = [provenance_record(right), provenance_record(left)]
        current = horizon("300", "2026-09-20T23:05:48+00:00", records)
        with self.assertRaisesRegex(ValueError, "deterministic canonical order"):
            validate(current, POLICY, source("2026-09-20T23:05:48Z"), previous_states=[left, right])

    def test_rejects_retired_identity_reuse_from_either_parent(self):
        retired = horizon("201", "2026-09-20T22:30:00+00:00")
        left = horizon("200", "2026-09-20T23:00:00+00:00", [provenance_record(retired)])
        right = horizon("202", "2026-09-20T23:01:00+00:00")
        records = canonical([provenance_record(retired), provenance_record(left), provenance_record(right)])
        current = horizon("201", "2026-09-20T23:05:48+00:00", records)
        with self.assertRaisesRegex(ValueError, "retired.*cannot be reused"):
            validate(current, POLICY, source("2026-09-20T23:05:48Z"), previous_states=[left, right])

if __name__ == "__main__":
    unittest.main()
