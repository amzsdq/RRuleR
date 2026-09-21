#!/usr/bin/env python3
"""Compute an exact-second completion-relative DTSTART without minute rounding."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta


def compute(close_at: str, offset_seconds: int = 60) -> dict:
    close = datetime.fromisoformat(close_at)
    if close.tzinfo is None:
        raise ValueError("close_at must include timezone")
    if type(offset_seconds) is not int or offset_seconds < 0:
        raise ValueError("offset_seconds must be a non-negative integer")
    due = close + timedelta(seconds=offset_seconds)
    return {
        "close_at": close.isoformat(),
        "offset_seconds": offset_seconds,
        "due_at": due.isoformat(),
        "local_dtstart": due.strftime("%Y%m%dT%H%M%S"),
        "second_precision_preserved": due.second == (close.second + offset_seconds) % 60,
    }


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("usage: compute_completion_due.py CLOSE_AT [OFFSET_SECONDS]", file=sys.stderr)
        return 2
    offset = int(sys.argv[2]) if len(sys.argv) == 3 else 60
    print(json.dumps(compute(sys.argv[1], offset), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
