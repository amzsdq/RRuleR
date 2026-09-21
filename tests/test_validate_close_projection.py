#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_close_projection import validate_projection


def _closed():
    current = {
        "run_state": "HANDOFF_COMMITTED",
        "current_owner": "RUN-1",
        "authority_epoch": 7,
        "continuation": {"next_due_at": "2026-09-21T10:11:00+09:00"},
    }
    activity = {
        "status": "HANDOFF_READY",
        "active_run_id": None,
        "authority_epoch": 7,
        "handoff_ready": True,
        "next_wake_due_at": "2026-09-21T10:11:00+09:00",
    }
    handoff = {
        "handoff_state": "COMMITTED",
        "predecessor_run_id": "RUN-1",
        "predecessor_authority_epoch": 7,
        "successor_expected_at": "2026-09-21T10:11:00+09:00",
    }
    return current, activity, handoff


class CloseProjectionTests(unittest.TestCase):
    def test_valid_closed_projection(self):
        self.assertTrue(validate_projection(*_closed())["valid"])

    def test_closed_projection_rejects_stale_working_activity(self):
        current, activity, handoff = _closed()
        activity.update(status="WORKING", active_run_id="RUN-1", handoff_ready=False)
        result = validate_projection(current, activity, handoff)
        self.assertFalse(result["valid"])
        self.assertEqual(result["errors"][:3], [
            "CLOSED_CURRENT_REQUIRES_HANDOFF_READY_ACTIVITY",
            "CLOSED_ACTIVITY_MUST_CLEAR_ACTIVE_RUN_ID",
            "CLOSED_ACTIVITY_MUST_BE_HANDOFF_READY",
        ])

    def test_closed_projection_rejects_due_and_epoch_drift(self):
        current, activity, handoff = _closed()
        activity["authority_epoch"] = 6
        activity["next_wake_due_at"] = "2026-09-21T10:12:00+09:00"
        handoff["predecessor_authority_epoch"] = 6
        handoff["successor_expected_at"] = "2026-09-21T10:12:00+09:00"
        result = validate_projection(current, activity, handoff)
        self.assertFalse(result["valid"])
        self.assertIn("ACTIVITY_AUTHORITY_EPOCH_MISMATCH", result["errors"])
        self.assertIn("CLOSED_ACTIVITY_NEXT_DUE_MISMATCH", result["errors"])
        self.assertIn("CLOSED_HANDOFF_NEXT_DUE_MISMATCH", result["errors"])

    def test_valid_working_projection(self):
        current, activity, handoff = _closed()
        current["run_state"] = "WORKING"
        activity.update(status="WORKING", active_run_id="RUN-1", handoff_ready=False)
        handoff.update(handoff_state="RECOVERY_CLAIMED", successor_run_id="RUN-1")
        self.assertTrue(validate_projection(current, activity, handoff)["valid"])

    def test_working_projection_rejects_owner_mismatch(self):
        current, activity, handoff = _closed()
        current["run_state"] = "WORKING"
        activity.update(status="WORKING", active_run_id="RUN-OLD", handoff_ready=False)
        handoff.update(handoff_state="RECOVERY_CLAIMED", successor_run_id="RUN-OLD")
        result = validate_projection(current, activity, handoff)
        self.assertFalse(result["valid"])
        self.assertEqual(result["errors"], [
            "WORKING_ACTIVITY_OWNER_MISMATCH",
            "WORKING_HANDOFF_SUCCESSOR_MISMATCH",
        ])
