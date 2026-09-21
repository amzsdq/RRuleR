import json
import tempfile
import unittest
from pathlib import Path
from tools.validate_observation_horizon import load_predecessor_states, validate, validate_actions_causality


POLICY = {"accepted_provenance_kinds": ["GITHUB_ACTIONS_OBSERVED_TIMESTAMP"]}


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
        parents = [{"trusted_observed_through": "2026-09-20T23:04:48+00:00"}, {"trusted_observed_through": "2026-09-20T23:06:48+00:00"}]
        horizon = {"provenance_kind": "GITHUB_ACTIONS_OBSERVED_TIMESTAMP", "provenance_ref": "123", "trusted_observed_through": "2026-09-20T23:05:48+00:00"}
        source = {"status": "completed", "conclusion": "success", "updated_at": "2026-09-20T23:05:48Z"}
        with self.assertRaisesRegex(ValueError, "rollback"):
            validate(horizon, POLICY, source, previous_states=parents)

    def test_accepts_horizon_at_or_above_all_merge_parents(self):
        parents = [{"trusted_observed_through": "2026-09-20T23:04:48+00:00"}, {"trusted_observed_through": "2026-09-20T23:05:48+00:00"}]
        horizon = {"provenance_kind": "GITHUB_ACTIONS_OBSERVED_TIMESTAMP", "provenance_ref": "123", "trusted_observed_through": "2026-09-20T23:05:48+00:00"}
        source = {"status": "completed", "conclusion": "success", "updated_at": "2026-09-20T23:05:48Z"}
        self.assertTrue(validate(horizon, POLICY, source, previous_states=parents))

    def test_rejects_explicit_missing_predecessor_file(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing-parent.json"
            with self.assertRaisesRegex(ValueError, "predecessor.*missing"):
                load_predecessor_states([missing])

    def test_loads_all_explicit_predecessor_files(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "parent-1.json"
            second = Path(directory) / "parent-2.json"
            first.write_text(json.dumps({"trusted_observed_through": "2026-09-20T23:04:48+00:00"}))
            second.write_text(json.dumps({"trusted_observed_through": "2026-09-20T23:05:48+00:00"}))
            states = load_predecessor_states([first, second])
            self.assertEqual(len(states), 2)

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

    def test_rejects_commit_committer_timestamp_even_if_exact(self):
        horizon = {"provenance_kind": "GITHUB_COMMIT_COMMITTER_TIMESTAMP", "provenance_ref": "abc", "trusted_observed_through": "2099-01-01T00:00:00+00:00"}
        source = {"commit": {"committer": {"date": "2099-01-01T00:00:00Z"}}}
        with self.assertRaisesRegex(ValueError, "unsupported"):
            validate(horizon, POLICY, source)

    def test_rejects_unsupported_kind(self):
        horizon = {"provenance_kind": "LOCAL_UNPERSISTED_CLOCK", "provenance_ref": "x", "trusted_observed_through": "2026-09-20T23:05:48+00:00"}
        with self.assertRaisesRegex(ValueError, "unsupported"):
            validate(horizon, POLICY, {})

    def test_rejects_timezone_less_timestamp(self):
        horizon = {"provenance_kind": "GITHUB_ACTIONS_OBSERVED_TIMESTAMP", "provenance_ref": "123", "trusted_observed_through": "2026-09-20T23:05:48"}
        source = {"status": "completed", "conclusion": "success", "updated_at": "2026-09-20T23:05:48Z"}
        with self.assertRaisesRegex(ValueError, "lacks timezone"):
            validate(horizon, POLICY, source)

    def test_accepts_trusted_actions_ancestor(self):
        source = {"event": "push", "head_branch": "main", "path": ".github/workflows/validate-control-plane.yml", "head_sha": "aaa"}
        compare = {"status": "ahead", "base_commit": {"sha": "aaa"}, "merge_base_commit": {"sha": "aaa"}}
        self.assertTrue(validate_actions_causality(source, compare, "bbb"))

    def test_rejects_unrelated_successful_actions_run(self):
        source = {"event": "push", "head_branch": "main", "path": ".github/workflows/validate-control-plane.yml", "head_sha": "aaa"}
        compare = {"status": "diverged", "base_commit": {"sha": "aaa"}, "merge_base_commit": {"sha": "ccc"}}
        with self.assertRaisesRegex(ValueError, "not an ancestor"):
            validate_actions_causality(source, compare, "bbb")

    def test_rejects_untrusted_workflow_even_if_successful(self):
        source = {"event": "push", "head_branch": "main", "path": ".github/workflows/unrelated.yml", "head_sha": "aaa"}
        compare = {"status": "ahead", "base_commit": {"sha": "aaa"}, "merge_base_commit": {"sha": "aaa"}}
        with self.assertRaisesRegex(ValueError, "workflow is not trusted"):
            validate_actions_causality(source, compare, "bbb")

    def test_rejects_non_push_provenance(self):
        source = {"event": "workflow_dispatch", "head_branch": "main", "path": ".github/workflows/validate-control-plane.yml", "head_sha": "aaa"}
        compare = {"status": "ahead", "base_commit": {"sha": "aaa"}, "merge_base_commit": {"sha": "aaa"}}
        with self.assertRaisesRegex(ValueError, "trusted main push"):
            validate_actions_causality(source, compare, "bbb")


if __name__ == "__main__":
    unittest.main()
