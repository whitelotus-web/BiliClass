"""Session health and task cooldowns are separate, durable observations."""

import re
import time

AUTH_ERRORS = {"login", "verification", "auth_response", "browser_changed"}
TEMPORARY_ERRORS = {"network", "browser"}
SESSION_CHECK_INTERVAL = 7200
RECOVERY_CHECK_INTERVAL = 300
UNKNOWN_QUOTA_BACKOFF = 1800


def retry_delay(message):
    """Read a relative delay only after the caller has identified a quota notice."""
    delays = []
    for match in re.finditer(
        r"\b(?:after|in|sau)\s+(\d+(?:[.,]\d+)?)\s*"
        r"(seconds?|secs?|giây|hours?|hrs?|giờ|minutes?|mins?|phút|days?|ngày)\b",
        str(message).casefold(),
    ):
        value = float(match[1].replace(",", "."))
        unit = match[2]
        factor = 86400 if unit.startswith(("day", "ngày")) else (
            3600 if unit.startswith(("hour", "hr", "giờ")) else (
                60 if unit.startswith(("minute", "min", "phút")) else 1
            )
        )
        seconds = value * factor
        if 0 < seconds <= 366 * 86400:
            delays.append(int(seconds))
    return max(delays, default=0)


def quota_blocked(account, now=None):
    now = time.time() if now is None else now
    retry_at = account.get("quota_retry_at", 0)
    return bool(account.get("quota_limited") and (not retry_at or retry_at > now))


def temporary_blocked(account, now=None):
    now = time.time() if now is None else now
    return (account.get("last_error", {}).get("code") in TEMPORARY_ERRORS
            and account.get("connection_retry_at", 0) > now)


def health_due(account, now=None):
    """Probe idle, stale profiles; a challenge requires the human login flow."""
    now = time.time() if now is None else now
    code = account.get("last_error", {}).get("code", "")
    if code in AUTH_ERRORS or not (account.get("saved_at") or account.get("ready")):
        return False
    if quota_blocked(account, now):
        return False
    interval = RECOVERY_CHECK_INTERVAL if code in TEMPORARY_ERRORS or account.get("quota_limited") else SESSION_CHECK_INTERVAL
    last_probe = max(account.get("checked_at", 0), account.get("probe_attempted_at", 0))
    return now - last_probe >= interval
