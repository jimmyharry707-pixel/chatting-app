"""UTC timestamps and user-facing relative time formatting."""
from datetime import datetime, timezone

def utc_now(): return datetime.now(timezone.utc)
def utc_iso(): return utc_now().isoformat(timespec="seconds")

def parse_timestamp(value):
    if not value: return None
    try: return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError): return None

def local_clock(value, fmt="%H:%M"):
    parsed = parse_timestamp(value)
    return parsed.astimezone().strftime(fmt) if parsed else ""

def relative_age(value):
    parsed = parse_timestamp(value)
    if not parsed: return "unknown"
    seconds = max(0, int((utc_now() - parsed).total_seconds()))
    if seconds < 60: return "just now"
    if seconds < 3600: return f"{seconds // 60}m ago"
    if seconds < 86400: return f"{seconds // 3600}h ago"
    return f"{seconds // 86400}d ago"
