#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from compute_completion_due import (
    NORMAL_CLOSE_OFFSET_HUMAN,
    NORMAL_CLOSE_OFFSET_SECONDS,
    compute,
)


def test_default_normal_close_is_exactly_one_minute_sixty_seconds():
    out = compute("2026-09-21T18:51:46+09:00")
    assert NORMAL_CLOSE_OFFSET_SECONDS == 60
    assert NORMAL_CLOSE_OFFSET_HUMAN == "1 minute (60 seconds)"
    assert out["offset_seconds"] == 60
    assert out["offset_human"] == "1 minute (60 seconds)"
    assert out["due_at"] == "2026-09-21T18:52:46+09:00"
    assert out["local_dtstart"] == "20260921T185246"
    assert out["second_precision_preserved"] is True
    assert out["recurrence_does_not_change_offset"] is True


def test_sixty_seconds_never_means_sixty_minutes():
    out = compute("2026-09-21T18:59:31+09:00", 60)
    assert out["due_at"] == "2026-09-21T19:00:31+09:00"
    assert out["due_at"] != "2026-09-21T19:59:31+09:00"


def test_cross_minute_and_hour_preserves_exact_offset():
    out = compute("2026-09-21T18:59:31+09:00", 90)
    assert out["offset_human"] == "90 seconds"
    assert out["due_at"] == "2026-09-21T19:01:01+09:00"
    assert out["local_dtstart"] == "20260921T190101"


def test_rejects_naive_timestamp_and_bad_offset():
    for close, offset in (("2026-09-21T18:51:46", 60), ("2026-09-21T18:51:46+09:00", -1)):
        try:
            compute(close, offset)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid completion due input accepted")
