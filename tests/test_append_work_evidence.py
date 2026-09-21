#!/usr/bin/env python3
import argparse
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from append_work_evidence import append_record, build_record


def args(**overrides):
    base = dict(
        record_id="WE-TEST-001",
        authority_epoch=59,
        run_id="RUN-TEST",
        start_at="2026-09-21T15:50:00+09:00",
        end_at="2026-09-21T15:51:00+09:00",
        kind="implementation",
        artifact="artifact@deadbeef",
        basis="Observed start and end with materially new artifact.",
    )
    base.update(overrides)
    return argparse.Namespace(**base)


def ledger():
    return {"records": [], "collection": {"historical_backfill": False}}


def test_build_record_computes_duration_and_observed_boundaries():
    record = build_record(args())
    assert record["observed_seconds"] == 60
    assert record["start_boundary"] == "OBSERVED"
    assert record["end_boundary"] == "OBSERVED"


def test_append_updates_latest_record():
    data = append_record(ledger(), build_record(args()))
    assert data["collection"]["latest_observed_record"] == "WE-TEST-001"
    assert len(data["records"]) == 1


def test_duplicate_record_is_rejected():
    data = append_record(ledger(), build_record(args()))
    try:
        append_record(data, build_record(args()))
    except ValueError as exc:
        assert "duplicate" in str(exc)
    else:
        raise AssertionError("duplicate record accepted")


def test_overlap_is_rejected():
    data = append_record(ledger(), build_record(args()))
    overlapping = build_record(args(record_id="WE-TEST-002", start_at="2026-09-21T15:50:30+09:00", end_at="2026-09-21T15:51:30+09:00"))
    try:
        append_record(data, overlapping)
    except ValueError as exc:
        assert "overlap" in str(exc)
    else:
        raise AssertionError("overlapping interval accepted")


def test_naive_timestamp_is_rejected():
    try:
        build_record(args(start_at="2026-09-21T15:50:00"))
    except ValueError as exc:
        assert "timezone" in str(exc)
    else:
        raise AssertionError("naive timestamp accepted")
