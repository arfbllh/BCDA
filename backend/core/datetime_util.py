"""UTC timestamps for DB columns and API payloads (replaces deprecated utcnow())."""

from datetime import datetime, timezone


def utc_now():
    """UTC 'now' as naive datetime for DateTime columns (wall clock in UTC)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def utc_now_iso():
    """ISO-8601 UTC string with Z suffix for JSON."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
