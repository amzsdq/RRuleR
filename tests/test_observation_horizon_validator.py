import json
import tempfile
import unittest
from pathlib import Path
from tools.validate_observation_horizon import load_predecessor_states, provenance_record, validate, validate_actions_causality

POLICY = {"accepted_provenance_kinds": ["GITHUB_ACTIONS_OBSERVED_TIMESTAMP"]}

def actions_horizon(attempt=1, trusted="2026-09-20T23:05:48+00:00", ref="123", history=None):
    return {"provenance_kind": "GITHUB_ACTIONS_OBSERVED_TIMESTAMP", "provenance_ref": ref, "provenance_attempt": attempt, "trusted_observed_through": trusted, "provenance_history": list(history or [])}

def actions_source(attempt=1, updated="2026-09-20T23:05:48Z", conclusion="success"):
    return {"status": "completed", "conclusion": conclusion, "run_attempt": attempt, "updated_at": updated}

class ObservationHorizonValidatorTests(unittest.TestCase):
    def test_accepts_successful_actions_exact_timestamp(self): self.assertTrue(validate(actions_horizon(), POLICY, actions_source()))
    def test_accepts_semantically_equal_timestamp_encoding(self): self.assertTrue(validate(actions_horizon(trusted="2026-09-20T19:05:48-04:00"), POLICY, actions_source(updated="2026-09-20T23:05:48Z")))
    def test_accepts_same_provenance_equivalent_encoding_without_repin(self):
        previous=actions_horizon(trusted="2026-09-20T23:05:48Z"); current=actions_horizon(trusted="2026-09-20T23:05:48+00:00")
        self.assertTrue(validate(current, POLICY, actions_source(), previous=previous))
    def test_accepts_forward_transition(self):
        previous={"trusted_observed_through":"2026-09-20T23:04:48+00:00"}; current=actions_horizon(history=[provenance_record(previous)])
        self.assertTrue(validate(current,POLICY,actions_source(),previous=previous))
    def test_accepts_forward_transition_with_explicit_new_provenance(self):
        previous=actions_horizon(trusted="2026-09-20T23:04:48+00:00",ref="122"); current=actions_horizon(ref="123",history=[provenance_record(previous)])
        self.assertTrue(validate(current,POLICY,actions_source(),previous=previous))
    def test_rejects_same_provenance_repin_after_drift(self):
        previous=actions_horizon(trusted="2026-09-20T23:04:48+00:00",ref="123"); current=actions_horizon(trusted="2026-09-20T23:05:48+00:00",ref="123")
        with self.assertRaisesRegex(ValueError,"cannot be repinned"): validate(current,POLICY,actions_source(),previous=previous)
    def test_rejects_retired_identity_reuse_after_intervening_provenance(self):
        retired=actions_horizon(trusted="2026-09-20T23:04:48+00:00",ref="121"); previous=actions_horizon(trusted="2026-09-20T23:05:00+00:00",ref="122",history=[provenance_record(retired)]); current=actions_horizon(trusted="2026-09-20T23:05:48+00:00",ref="121",history=[provenance_record(retired),provenance_record(previous)])
        with self.assertRaisesRegex(ValueError,"retired.*cannot be reused"): validate(current,POLICY,actions_source(updated="2026-09-20T23:05:48Z"),previous=previous)
    def test_rejects_history_deletion(self):
        retired=actions_horizon(trusted="2026-09-20T23:04:00+00:00",ref="121"); previous=actions_horizon(trusted="2026-09-20T23:04:48+00:00",ref="122",history=[provenance_record(retired)]); current=actions_horizon(ref="123",history=[provenance_record(previous)])
        with self.assertRaisesRegex(ValueError,"append-only"): validate(current,POLICY,actions_source(),previous=previous)
    def test_rejects_horizon_rollback(self):
        with self.assertRaisesRegex(ValueError,"rollback"): validate(actions_horizon(),POLICY,actions_source(),previous={"trusted_observed_through":"2026-09-20T23:06:48+00:00"})
    def test_rejects_rollback_against_any_merge_parent(self):
        parents=[{"trusted_observed_through":"2026-09-20T23:04:48+00:00"},{"trusted_observed_through":"2026-09-20T23:06:48+00:00"}]
        with self.assertRaisesRegex(ValueError,"rollback"): validate(actions_horizon(),POLICY,actions_source(),previous_states=parents)
    def test_accepts_horizon_at_or_above_all_merge_parents_when_identity_unchanged(self): self.assertTrue(validate(actions_horizon(),POLICY,actions_source(),previous_states=[actions_horizon(),actions_horizon()]))
    def test_rejects_explicit_missing_predecessor_file(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError,"predecessor.*missing"): load_predecessor_states([Path(directory)/"missing-parent.json"])
    def test_loads_all_explicit_predecessor_files(self):
        with tempfile.TemporaryDirectory() as directory:
            first=Path(directory)/"parent-1.json"; second=Path(directory)/"parent-2.json"; first.write_text(json.dumps(actions_horizon())); second.write_text(json.dumps(actions_horizon())); self.assertEqual(len(load_predecessor_states([first,second])),2)
    def test_rejects_forged_timestamp(self):
        with self.assertRaisesRegex(ValueError,"drifted"): validate(actions_horizon(trusted="2026-09-20T23:06:48+00:00"),POLICY,actions_source())
    def test_same_attempt_timestamp_drift_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"drifted"): validate(actions_horizon(attempt=1),POLICY,actions_source(attempt=1,updated="2026-09-21T00:05:48Z"))
    def test_rejects_unsuccessful_actions_run(self):
        with self.assertRaisesRegex(ValueError,"not successful"): validate(actions_horizon(),POLICY,actions_source(conclusion="failure"))
    def test_rejects_attempt_mismatch(self):
        with self.assertRaisesRegex(ValueError,"attempt mismatch"): validate(actions_horizon(attempt=1),POLICY,actions_source(attempt=2))
    def test_rerun_cannot_retroactively_move_bound_attempt_timestamp(self):
        with self.assertRaisesRegex(ValueError,"attempt mismatch"): validate(actions_horizon(attempt=1),POLICY,actions_source(attempt=2,updated="2026-09-21T00:05:48Z"))
    def test_rejects_invalid_attempt_value(self):
        horizon=actions_horizon(); horizon["provenance_attempt"]=0
        with self.assertRaisesRegex(ValueError,"attempt is invalid"): validate(horizon,POLICY,actions_source())
    def test_rejects_commit_committer_timestamp_even_if_exact(self):
        horizon={"provenance_kind":"GITHUB_COMMIT_COMMITTER_TIMESTAMP","provenance_ref":"abc","trusted_observed_through":"2099-01-01T00:00:00+00:00"}
        with self.assertRaisesRegex(ValueError,"unsupported"): validate(horizon,POLICY,{"commit":{"committer":{"date":"2099-01-01T00:00:00Z"}}})
    def test_rejects_unsupported_kind(self):
        horizon={"provenance_kind":"LOCAL_UNPERSISTED_CLOCK","provenance_ref":"x","trusted_observed_through":"2026-09-20T23:05:48+00:00"}
        with self.assertRaisesRegex(ValueError,"unsupported"): validate(horizon,POLICY,{})
    def test_rejects_timezone_less_timestamp(self):
        with self.assertRaisesRegex(ValueError,"lacks timezone"): validate(actions_horizon(trusted="2026-09-20T23:05:48"),POLICY,actions_source())
    def test_accepts_trusted_actions_ancestor(self):
        source={"event":"push","head_branch":"main","path":".github/workflows/validate-control-plane.yml","head_sha":"aaa"}; compare={"status":"ahead","base_commit":{"sha":"aaa"},"merge_base_commit":{"sha":"aaa"}}
        self.assertTrue(validate_actions_causality(source,compare,"bbb"))
    def test_rejects_unrelated_successful_actions_run(self):
        source={"event":"push","head_branch":"main","path":".github/workflows/validate-control-plane.yml","head_sha":"aaa"}; compare={"status":"diverged","base_commit":{"sha":"aaa"},"merge_base_commit":{"sha":"ccc"}}
        with self.assertRaisesRegex(ValueError,"not an ancestor"): validate_actions_causality(source,compare,"bbb")
    def test_rejects_untrusted_workflow_even_if_successful(self):
        source={"event":"push","head_branch":"main","path":".github/workflows/unrelated.yml","head_sha":"aaa"}; compare={"status":"ahead","base_commit":{"sha":"aaa"},"merge_base_commit":{"sha":"aaa"}}
        with self.assertRaisesRegex(ValueError,"workflow is not trusted"): validate_actions_causality(source,compare,"bbb")
    def test_rejects_non_push_provenance(self):
        source={"event":"workflow_dispatch","head_branch":"main","path":".github/workflows/validate-control-plane.yml","head_sha":"aaa"}; compare={"status":"ahead","base_commit":{"sha":"aaa"},"merge_base_commit":{"sha":"aaa"}}
        with self.assertRaisesRegex(ValueError,"trusted main push"): validate_actions_causality(source,compare,"bbb")

if __name__=="__main__": unittest.main()
