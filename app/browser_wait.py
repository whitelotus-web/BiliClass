"""A durable response wait budget; reconnecting never restarts the same wait."""

import math
import time


class ResponseWait:
    def __init__(self, folder, record, timeout):
        self.folder, self.record, self.timeout = folder, record, timeout
        self.key = None
        self.started = self.saved_at = time.monotonic()
        self.elapsed = 0.0

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
            self.record.pop('wait_exhausted', None)
        total = self.elapsed + now - self.started
        self.record['response_wait'] = {'key': key, 'seconds': round(total, 3), 'limit': self.timeout}
        self.record['wait_exhausted'] = total >= self.timeout
        if force or now - self.saved_at >= 5:
            write_record(self.folder, self.record)
            self.saved_at = now
        return max(0.0, self.timeout - total)

    def __exit__(self, *_):
        self.checkpoint(force=True)
