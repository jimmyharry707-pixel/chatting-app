"""Timestamp formatting tests."""
from shared.timeutils import parse_timestamp,relative_age,local_clock

def test_parse_timestamp_accepts_iso_value():
    assert parse_timestamp("2026-01-01T10:00:00+00:00") is not None

def test_parse_timestamp_rejects_invalid_value():
    assert parse_timestamp("not-a-date") is None

def test_local_clock_returns_empty_for_missing_value():
    assert local_clock(None)==""

def test_relative_age_handles_missing_value():
    assert relative_age(None)=="unknown"
