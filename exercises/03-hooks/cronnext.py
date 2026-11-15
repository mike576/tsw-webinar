"""Compute the next run time of a cron expression. See TASK.md for the spec."""

from __future__ import annotations

from datetime import datetime


def next_run(expr: str, after: datetime) -> datetime:
    raise NotImplementedError
