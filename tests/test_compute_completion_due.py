#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from compute_completion_due import compute


def test_exact_second_completion_relative_due():
    out = compute("2026-09-21T18:51:46+09:00", 60)
    assert out["due_at"] == "2026-09-21T18:52:46+09:00"
    assert out["local_dtstart"] == "20260921T185246"
    assert out["second_precision_preserved"] is True


def test_cross_minute_and_hour_preserves_exact_offset():
    out = compute("2026-09-21T18:59:31+09:00", 90)
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
