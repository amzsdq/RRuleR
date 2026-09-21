import unittest
from tools.validate_observation_horizon import validate


POLICY = {"accepted_provenance_kinds": ["GITHUB_ACTIONS_OBSERVED_TIMESTAMP", "GITHUB_COMMIT_COMMITTER_TIMESTAMP"]}


class ObservationHorizonValidatorTests(unittest.TestCase):
    def test_accepts_successful_actions_exact_timestamp(self):
        horizon = {"provenance_kind": "GITHUB_ACTIONS_OBSERVED_TIMESTAMP", "provenance_ref": "123", "trusted_observed_through": "2026-09-20T23:05:48+00:00"}
        source = {"status": "completed", "conclusion": "success", "updated_at": "2026-09-20T23:05:48Z"}
        self.assertTrue(validate(horizon, POLICY, source))

    def test_accepts_forward_transition(self):
        previous = {"trusted_observed_through": "2026-09-20T23:04:48+00:00"}
        horizon = {"provenance_kind": "GITHUB_ACTIONS_OBSERVED_TIMESTAMP", "provenance_ref": "123", "trusted_observed_through": "2026-09-20T23:05:48+00:00"}
        source = {"status": "completed", "conclusion": "success", "updated_at": "2026-09-20T23:05:48Z"}
        self.assertTrue(validate(horizon, POLICY, source, previous=previous))

    def test_rejects_horizon_rollback(self):
        previous = {"trusted_observed_through": "2026-09-20T23:06:48+00:00"}
        horizon = {"provenance_kind": "GITHUB_ACTIONS_OBSERVED_TIMESTAMP", "provenance_ref": "123", "trusted_observed_through": "2026-09-20T23:05:48+00:00"}
        source = {"status": "completed", "conclusion": "success", "updated_at": "2026-09-20T23:05:48Z"}
        with self.assertRaisesRegex(ValueError, "rollback"):
            validate(horizon, POLICY, source, previous=previous)

    def test_rejects_rollback_against_any_merge_parent(self):
        parents = [
            {"trusted_observed_through": "2026-09-20T23:04:48+00:00"},
            {"trusted_observed_through": "2026-09-20T23:06:48+00:00"},
        ]
        horizon = {"provenance_kind": "GITHUB_ACTIONS_OBSERVED_TIMESTAMP", "provenance_ref": "123", "trusted_observed_through": "2026-09-20T23:05:48+00:00"}
        source = {"status": "completed", "conclusion": "success", "updated_at": "2026-09-20T23:05:48Z"}
        with self.assertRaisesRegex(ValueError, "rollback"):
            validate(horizon, POLICY, source, previous_states=parents)

    def test_accepts_horizon_at_or_above_all_merge_parents(self):
        parents = [
            {"trusted_observed_through": "2026-09-20T23:04:48+00:00"},
            {"trusted_observed_through": "2026-09-20T23:05:48+00:00"},
        ]
        horizon = {"provenance_kind": "GITHUB_ACTIONS_OBSERVED_TIMESTAMP", "provenance_ref": "123", "trusted_observed_through": "2026-09-20T23:05:48+00:00"}
        source = {"status": "completed", "conclusion": "success", "updated_at": "2026-09-20T23:05:48Z"}
        self.assertTrue(validate(horizon, POLICY, source, previous_states=parents))

    def test_rejects_forged_timestamp(self):
        horizon = {"provenance_kind": "GITHUB_ACTIONS_OBSERVED_TIMESTAMP", "provenance_ref": "123", "trusted_observed_through": "2026-09-20T23:06:48+00:00"}
        source = {"status": "completed", "conclusion": "success", "updated_at": "2026-09-20T23:05:48Z"}
        with self.assertRaisesRegex(ValueError, "does not match"):
            validate(horizon, POLICY, source)

    def test_rejects_unsuccessful_actions_run(self):
        horizon = {"provenance_kind": "GITHUB_ACTIONS_OBSERVED_TIMESTAMP", "provenance_ref": "123", "trusted_observed_through": "2026-09-20T23:05:48+00:00"}
        source = {"status": "completed", "conclusion": "failure", "updated_at": "2026-09-20T23:05:48Z"}
        with self.assertRaisesRegex(ValueError, "not successful"):
            validate(horizon, POLICY, source)

    def test_rejects_unsupported_kind(self):
        horizon = {"provenance_kind": "LOCAL_UNPERSISTED_CLOCK", "provenance_ref": "x", "trusted_observed_through": "2026-09-20T23:05:48+00:00"}
        with self.assertRaisesRegex(ValueError, "unsupported"):
            validate(horizon, POLICY, {})

    def test_rejects_timezone_less_timestamp(self):
        horizon = {"provenance_kind": "GITHUB_COMMIT_COMMITTER_TIMESTAMP", "provenance_ref": "abc", "trusted_observed_through": "2026-09-20T23:05:48"}
        source = {"commit": {"committer": {"date": "2026-09-20T23:05:48Z"}}}
        with self.assertRaisesRegex(ValueError, "lacks timezone"):
            validate(horizon, POLICY, source)


if __name__ == "__main__":
    unittest.main()
