import unittest
from tools.audit_latest_run_record import audit
class LatestRunAuditTests(unittest.TestCase):
    def test_active_run_does_not_require_close_record(self): self.assertEqual(audit({'run_state':'ACTIVE','current_owner':'R1'},[]),[])
    def test_closed_run_requires_record(self): self.assertTrue(audit({'run_state':'CHECKPOINTED','current_owner':'R1'},[]))
    def test_open_record_does_not_satisfy_closed_run(self): self.assertTrue(audit({'run_state':'HANDOFF_COMMITTED','current_owner':'R1'},[{'run_id':'R1','run_ended_at':None}]))
    def test_closed_record_satisfies_gate(self): self.assertEqual(audit({'run_state':'HANDOFF_COMMITTED','current_owner':'R1'},[{'run_id':'R1','run_ended_at':'2026-09-22T11:00:00+09:00'}]),[])
    def test_obs_prefixed_observation_id_satisfies_gate(self): self.assertEqual(audit({'run_state':'HANDOFF_COMMITTED','current_owner':'RUN-UTIL-X'},[{'observation_id':'OBS-RUN-UTIL-X','run_ended_at':'2026-09-22T11:00:00+09:00'}]),[])
if __name__=='__main__': unittest.main()
