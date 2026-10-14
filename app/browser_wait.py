"""A durable response wait budget; reconnecting never restarts the same wait."""

import math
import time


class ResponseWait:
    def __init__(self, folder, record, timeout):
        self.folder, self.record, self.timeout = folder, record, timeout
        self.key = None
        self.started = self.saved_at = time.monotonic()
        self.elapsed = 0.0
        self.limit = timeout

    def __enter__(self):
        self.checkpoint(force=True)
        return self

    def checkpoint(self, force=False):
        from .browser_automation import write_record

        now = time.monotonic()
        key = self.record.get('send_sha256') or (self.record.get('url', '') + ':' + str(self.record.get('followups', 0)))
        if key != self.key:
            old = self.record.get('response_wait', {})
            elapsed = old.get('seconds', 0) if isinstance(old, dict) and old.get('key') == key else 0
            self.elapsed = float(elapsed) if type(elapsed) in (int, float) and math.isfinite(elapsed) and elapsed >= 0 else 0.0
            self.key, self.started = key, now
            old_limit = old.get('limit', self.timeout) if isinstance(old, dict) and old.get('key') == key else self.timeout
            same_policy = isinstance(old, dict) and old.get('base_limit', self.timeout) == self.timeout
            self.limit = (float(old_limit) if same_policy and type(old_limit) in (int, float)
                          and math.isfinite(old_limit) and self.timeout <= old_limit <= self.maximum
                          else self.timeout)
            self.record.pop('wait_exhausted', None)
        total = self.elapsed + now - self.started
        self.record['response_wait'] = {'key': key, 'seconds': round(total, 3), 'limit': self.limit, 'base_limit': self.timeout}
        self.record['wait_exhausted'] = total >= self.limit
        if force or now - self.saved_at >= 5:
            write_record(self.folder, self.record)
            self.saved_at = now
        return max(0.0, self.limit - total)

    @property
    def maximum(self):
        # Long slide jobs may still be producing output at the initial
        # 15-minute checkpoint. Keep following an active turn, bounded at an
        # hour of actual observation. Small test/custom budgets stay strict.
        return max(self.timeout, 3600) if self.timeout >= 900 else self.timeout

    def extend_active(self, generating):
        remaining = self.checkpoint()
        if remaining > 0:
            return True
        elapsed = self.record['response_wait']['seconds']
        if not generating or self.limit >= self.maximum or elapsed >= self.maximum:
            return False
        self.limit = min(self.maximum, max(self.limit, elapsed) + 300)
        self.checkpoint(force=True)
        return True

    def __exit__(self, *_):
        self.checkpoint(force=True)


def stale_refresh(record, signature, *, generating, after=180, maximum=3):
    """Persist a bounded read-only refresh of a silent, still-running turn."""
    import hashlib

    wait = record['response_wait']
    key, seconds = wait['key'], wait['seconds']
    fingerprint = hashlib.sha256(signature.encode('utf-8')).hexdigest()
    previous = record.get('response_watch', {})
    if not isinstance(previous, dict) or previous.get('key') != key:
        previous = {'key': key, 'fingerprint': fingerprint, 'at': seconds, 'refreshes': 0}
        record['response_watch'] = previous
    if not generating or previous.get('fingerprint') != fingerprint:
        previous.update(fingerprint=fingerprint, at=seconds)
        return False
    age = seconds - previous.get('at', seconds)
    if age < after or previous.get('refreshes', 0) >= maximum:
        return False
    previous.update(at=seconds, refreshes=previous.get('refreshes', 0) + 1)
    return True


def timeout_probe_available(record):
    wait = record.get('response_wait', {})
    key = record.get('send_sha256')
    return (isinstance(wait, dict) and record.get('state') == 'waiting' and record.get('error') == 'timeout'
            and bool(key) and wait.get('key') == key and record.get('timeout_probe_key') != key
            and type(wait.get('limit')) in (int, float) and 900 <= wait['limit'] < 3600
            and type(wait.get('seconds')) in (int, float) and 0 <= wait['seconds'] < 3600)
