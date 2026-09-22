import unittest
from validate_run_records import validate

class RunValidationTests(unittest.TestCase):
    def record(self):
        return dict(run_started_at='2026-09-21T17:00:00+00:00',run_ended_at='2026-09-21T17:10:00+00:00',duration_seconds=600,turn_outcome='CONTINUE',end_reason='VERIFIED_SAME_CANONICAL_CONTINUATION',program_status_at_end='CONTINUE',close_decision='TIME_BOUNDARY',verified_next_fast_due_at='2026-09-21T17:11:00+00:00',normal_close_offset_seconds=60)
    def trace(self):
        return dict(unit_id='U1',start_at='2026-09-21T17:01:00+00:00',end_at='2026-09-21T17:02:00+00:00',duration_seconds=60,artifact='tools/example.py@abc',work_evidence_ref='WE-E81-001',message='완료: validator hardened (duration 1m 0s)',durably_persisted=True,continued_same_wake=True,source_kind='test_or_validator_added_or_hardened')
    def test_normal(self): validate(self.record())
    def test_missing_exact_due_rejected(self):
        r=self.record(); del r['verified_next_fast_due_at']
        with self.assertRaises((ValueError,KeyError)): validate(r)
    def test_sixty_minutes_is_not_sixty_seconds(self):
        r=self.record(); r['verified_next_fast_due_at']='2026-09-21T18:10:00+00:00'
        with self.assertRaises(ValueError): validate(r)
    def test_wrong_declared_offset_rejected(self):
        r=self.record(); r['normal_close_offset_seconds']=3600
        with self.assertRaises(ValueError): validate(r)
    def test_missing_duration(self):
        r=self.record(); del r['duration_seconds']
        with self.assertRaises(ValueError): validate(r)
    def test_false_duration(self):
        r=self.record(); r['duration_seconds']=700
        with self.assertRaises(ValueError): validate(r)
    def test_packet_close_rejected(self):
        r=self.record(); r.update(run_ended_at='2026-09-21T17:02:00+00:00',duration_seconds=120)
        with self.assertRaises(ValueError): validate(r)
    def test_old_documented_no_work_exception_rejected(self):
        r=self.record(); r.update(run_ended_at='2026-09-21T17:02:00+00:00',duration_seconds=120,close_decision='EXCEPTION',short_turn_reason='NO_SAFE_RUNNABLE_WORK_AFTER_EXPLICIT_SCAN',alternatives_checked=['x'])
        with self.assertRaises(ValueError): validate(r)
    def test_platform_enforced_pre600_continue_accepted(self):
        r=self.record(); r.update(run_ended_at='2026-09-21T17:02:00+00:00',duration_seconds=120,close_decision='EXCEPTION',short_turn_reason='PLATFORM_ENFORCED_TERMINATION',end_reason='PLATFORM_ENFORCED_TERMINATION'); r.pop('verified_next_fast_due_at'); r.pop('normal_close_offset_seconds'); validate(r)
    def test_budget_close_before_600_rejected(self):
        r=self.record(); r.update(run_ended_at='2026-09-21T17:09:00+00:00',duration_seconds=540,close_decision='BUDGET_EXHAUSTED')
        with self.assertRaises(ValueError): validate(r)
    def test_early_handoff_without_exception_rejected(self):
        r=self.record(); r.update(run_ended_at='2026-09-21T17:09:59+00:00',duration_seconds=599,close_decision='HANDOFF')
        with self.assertRaises(ValueError): validate(r)
    def test_custom_recurring_end_reason_accepted_at_600(self):
        r=self.record(); r['end_reason']='VERIFIED_SAME_CANONICAL_CUSTOM_RECURRING_CONTINUATION'; r.pop('verified_next_fast_due_at'); r.pop('normal_close_offset_seconds'); validate(r)
    def test_pre_hard_floor_history_preserved(self): validate(dict(run_started_at='2026-09-21T10:00:00+00:00',run_ended_at='2026-09-21T10:02:00+00:00'))
    def test_no_inflated_useful_time(self):
        r=self.record(); r['productive_substantive_seconds']=601
        with self.assertRaises(ValueError): validate(r)
    def test_v55_trace_record_accepted(self):
        r=self.record(); r.update(chat_trace_policy='DURABLE_UNIT_CHAT_TRACE_CANARY_V5_5',schedule_trace_verified=True,final_due_trace_verified=True,unit_completion_traces=[self.trace()]); validate(r)
    def test_v55_unpersisted_trace_rejected(self):
        r=self.record(); t=self.trace(); t['durably_persisted']=False; r.update(chat_trace_policy='DURABLE_UNIT_CHAT_TRACE_CANARY_V5_5',schedule_trace_verified=True,final_due_trace_verified=True,unit_completion_traces=[t])
        with self.assertRaises(ValueError): validate(r)
    def test_v55_scheduler_only_completion_trace_rejected(self):
        r=self.record(); t=self.trace(); t['source_kind']='SCHEDULER_MUTATION_ALONE'; r.update(chat_trace_policy='DURABLE_UNIT_CHAT_TRACE_CANARY_V5_5',schedule_trace_verified=True,final_due_trace_verified=True,unit_completion_traces=[t])
        with self.assertRaises(ValueError): validate(r)
    def test_v55_missing_final_due_trace_rejected(self):
        r=self.record(); r.update(chat_trace_policy='DURABLE_UNIT_CHAT_TRACE_CANARY_V5_5',schedule_trace_verified=True,final_due_trace_verified=False,unit_completion_traces=[self.trace()])
        with self.assertRaises(ValueError): validate(r)
    def test_v56_durable_pending_trace_accepted_without_intermediate_delivery(self):
        r=self.record(); t=self.trace(); t['delivery_state']='TRACE_DURABLY_RECORDED'; r.update(chat_trace_policy='DURABLE_FIRST_FINAL_FLUSH_V5_6',trace_ledger_ref='state/TURN_TRACES.json',schedule_trace_durably_recorded=True,final_due_trace_durably_recorded=True,intermediate_delivery_required_for_execution_success=False,unit_completion_traces=[t]); validate(r)
    def test_v56_delivery_state_required(self):
        r=self.record(); t=self.trace(); r.update(chat_trace_policy='DURABLE_FIRST_FINAL_FLUSH_V5_6',trace_ledger_ref='state/TURN_TRACES.json',schedule_trace_durably_recorded=True,final_due_trace_durably_recorded=True,intermediate_delivery_required_for_execution_success=False,unit_completion_traces=[t])
        with self.assertRaises(ValueError): validate(r)
    def test_v56_cannot_require_intermediate_delivery_for_execution(self):
        r=self.record(); t=self.trace(); t['delivery_state']='TRACE_INTERMEDIATE_DELIVERED'; r.update(chat_trace_policy='DURABLE_FIRST_FINAL_FLUSH_V5_6',trace_ledger_ref='state/TURN_TRACES.json',schedule_trace_durably_recorded=True,final_due_trace_durably_recorded=True,intermediate_delivery_required_for_execution_success=True,unit_completion_traces=[t])
        with self.assertRaises(ValueError): validate(r)

if __name__=='__main__': unittest.main()
