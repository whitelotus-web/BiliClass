"""Bounded, explicit job routes; health checks never send background translations."""

import hashlib
import json
import math
import sqlite3
import threading
import time
from collections import Counter
from pathlib import Path

from .google_translation import KeyStore, TranslationProblem, Translator, _atomic, chunks

RECOVERABLE = {'api_settings', 'api_key', 'api_budget', 'api_quota', 'api_rate', 'api_network',
               'api_billing', 'api_model', 'api_deployment'}
_LOCK = threading.RLock()


def identity(directory, provider):
    from .alternative_translation import AlternativeStore

    store = KeyStore(directory) if provider == 'google' else AlternativeStore(directory, provider)
    rows = store.keys()
    raw = json.dumps([(row['id'], row.get('option', ''), hashlib.sha256(row['key'].encode()).hexdigest()) for row in rows])
    return hashlib.sha256(raw.encode()).hexdigest() if rows else ''


def health(directory):
    try:
        path = Path(directory) / 'translation-service-health.json'
        if path.stat().st_size > 16384:
            return {}
        value = json.loads(path.read_text(encoding='utf-8'))
        return {key: row for key, row in value.items() if key in {'google', 'languageapp', 'gemini', 'deepl'}
                and isinstance(row, dict) and isinstance(row.get('identity'), str)
                and row.get('code') in RECOVERABLE | {''}
                and all(type(row.get(field)) in {int, float} and math.isfinite(row[field]) for field in ('checked', 'until'))} if isinstance(value, dict) else {}
    except (OSError, ValueError, TypeError):
        return {}


def record(directory, provider, error=None):
    try:
        signature = identity(directory, provider)
        with _LOCK:
            values = health(directory)
            values[provider] = dict(identity=signature, checked=time.time(), code=getattr(error, 'code', ''),
                                    until=time.time() + min(3600, max(60, getattr(error, 'retry_after', 0) or 0)) if error else 0)
            _atomic(Path(directory) / 'translation-service-health.json', json.dumps(values).encode())
    except (OSError, ValueError, sqlite3.DatabaseError):
        pass  # Advisory state must never break a translation or hide its real error.


def service_states(directory):
    from .translation_provider import PROVIDERS, SELECTABLE

    values, result = health(directory), []
    for provider in SELECTABLE:
        try:
            signature = identity(directory, provider)
            row = values.get(provider, {})
            current = isinstance(row, dict) and signature and row.get('identity') == signature
            code = row.get('code', '') if current else ''
            checked = row.get('checked', 0) if current else 0
            status = 'Chưa thiết lập' if not signature else 'Tạm chưa dùng được' if code else 'Đã dịch/kết nối được' if checked else 'Chưa kiểm tra kết nối'
            result.append(dict(provider=provider, label=PROVIDERS[provider], configured=bool(signature),
                               warning=bool(signature and code), status=status, checked=checked, code=code))
        except (OSError, ValueError, sqlite3.DatabaseError):
            result.append(dict(provider=provider, label=PROVIDERS[provider], configured=False,
                               warning=True, status='Cần lưu lại cấu hình', checked=0, code='api_settings'))
    return result


def forget(directory, provider):
    try:
        with _LOCK:
            values = health(directory)
            values.pop(provider, None)
            _atomic(Path(directory) / 'translation-service-health.json', json.dumps(values).encode())
    except OSError:
        pass


def routes(directory, primary):
    from .translation_provider import SELECTABLE, require_credentials, snapshot

    result = []
    for provider in dict.fromkeys((primary, *SELECTABLE)):
        if provider not in SELECTABLE:
            continue
        try:
            require_credentials(directory, provider)
            result.append(snapshot(directory, provider))
        except (OSError, ValueError, sqlite3.DatabaseError):
            continue
    return result


class RoutedTranslator(Translator):
    """Reuse validated chunks across providers without merging their private caches."""

    def __init__(self, directory, config, google_factory):
        from .translation_provider import SELECTABLE

        self.directory, self.config, self.google_factory = Path(directory), dict(config), google_factory
        self.routes = config['translation_fallback']
        if (not isinstance(self.routes, list) or not 1 <= len(self.routes) <= 4
                or any(not isinstance(row, dict) or row.get('translation_provider') not in SELECTABLE for row in self.routes)
                or len({row['translation_provider'] for row in self.routes}) != len(self.routes)):
            raise TranslationProblem('api_settings', 'Chưa có dịch vụ dự phòng hợp lệ. Thêm cấu hình trong Cài đặt → Dịch thuật.')
        self.used_services, self.notices, self._plan = [], [], None
        self.on_service_notice = None
        self.configure_terms('', [])

    def configure_knowledge(self, plan):
        super().configure_knowledge(plan)
        self._plan = plan

    def _notice(self, message):
        if message not in self.notices:
            self.notices.append(message)
            if self.on_service_notice:
                self.on_service_notice(message)

    def translate(self, texts, cancel, progress=None, *, source='vi', target='en', native_values=None, fragment_repair=True):
        from .translation_batches import NUMBERS
        from .translation_provider import PROVIDERS, build_translator

        hints = native_values if native_values is not None else [{} for _ in texts]
        if len(hints) != len(texts):
            raise ValueError('Ngữ cảnh số liệu không khớp vùng dịch.')
        parts = [[(part, tuple(sorted((key, value) for key, value in hint.items() if key in part)))
                  for line in text.splitlines(keepends=True) for part in chunks(line)]
                 for text, hint in zip(texts, hints, strict=True)]
        jobs = list(dict.fromkeys(job for row in parts for job in row))
        values = {}
        bound = {key: value for key, value in self.config.items() if key != 'translation_work_folder'}
        scope = json.dumps([bound, self.cache_namespace, self._term_rows, source, target], sort_keys=True, ensure_ascii=False)
        ids = {job: hashlib.sha256((scope + json.dumps(job, ensure_ascii=False)).encode()).hexdigest() for job in jobs}
        folder = self.config.get('translation_work_folder')
        ledger_path = Path(folder) / 'routing-results.json' if folder else None
        ledger = {}
        if ledger_path:
            try:
                if ledger_path.stat().st_size <= 16 * 1024**2:
                    ledger = json.loads(ledger_path.read_text(encoding='utf-8'))
                if not isinstance(ledger, dict):
                    ledger = {}
            except (OSError, ValueError):
                pass
        for job in jobs:
            row = ledger.get(ids[job], {})
            value = row.get('value') if isinstance(row, dict) else None
            if (isinstance(value, str) and value.strip() and len(value) < 20000
                    and Counter(NUMBERS.findall(value)) == Counter(NUMBERS.findall(job[0]))):
                values[job] = value
                if row.get('provider') in PROVIDERS and row['provider'] not in self.used_services:
                    self.used_services.append(row['provider'])

        def accept(completed, provider):
            for job, value in completed.items():
                if job in ids:
                    values[job] = value
                    ledger[ids[job]] = dict(value=value, provider=provider)
            if completed and provider not in self.used_services:
                self.used_services.append(provider)
            if ledger_path:
                _atomic(ledger_path, json.dumps(ledger, ensure_ascii=False).encode('utf-8'))

        last = None
        for route in self.routes:
            if cancel.is_set():
                raise InterruptedError('Đã dừng dịch; phần đã đạt được giữ lại.')
            pending = [job for job in jobs if job not in values]
            if not pending:
                break
            provider = route['translation_provider']
            try:
                known = health(self.directory).get(provider, {})
                if (isinstance(known, dict) and known.get('identity') == identity(self.directory, provider)
                        and isinstance(known.get('until'), (int, float)) and known['until'] > time.time()):
                    last = TranslationProblem(known.get('code') or 'api_rate', PROVIDERS[provider] + ' tạm chưa dùng được; chờ rồi tiếp tục hoặc thử kết nối trong Cài đặt.')
                    continue
                delegate = build_translator(self.directory, route, 500_000, self.google_factory)
                delegate.configure_terms(self.term_policy.subject, self._term_rows)
                if self._plan:
                    delegate.configure_knowledge(self._plan)
                delegate.completed_chunks = {}
                # Keep the normal transient retry policy when no fallback is configured.
                delegate.max_retries = 0 if len(self.routes) > 1 else 2
                transport, api_calls = delegate.transport, []

                def tracked(*args):
                    api_calls.append(True)
                    return transport(*args)

                delegate.transport = tracked
                if last:
                    self._notice('Dịch vụ trước tạm chưa dùng được. Đang thử ' + PROVIDERS[provider] + '.')
                baseline = sum(len(job[0]) for job in values)
                total = sum(len(job[0]) for job in jobs)

                def notify(done, _total):
                    if progress:
                        progress(min(total, baseline + done), total)

                try:
                    output = delegate.translate([job[0] for job in pending], cancel, notify, source=source, target=target,
                                                native_values=[dict(job[1]) for job in pending], fragment_repair=fragment_repair)
                    accept(dict(zip(pending, output, strict=True)), provider)
                finally:
                    accept(delegate.completed_chunks, provider)
                    self.reviewed_reused.update(delegate.reviewed_reused)
                if api_calls:
                    record(self.directory, provider)
                if last:
                    self._notice('Đã chuyển sang ' + PROVIDERS[provider] + ' để tiếp tục; phần đã dịch được giữ lại.')
            except TranslationProblem as exc:
                if exc.code not in RECOVERABLE:
                    raise
                if getattr(exc, 'offline', False):
                    raise  # Offline is not evidence that a particular service has failed.
                record(self.directory, provider, exc)
                last = exc
        if any(job not in values for job in jobs):
            raise last or TranslationProblem('api_settings', 'Các dịch vụ đã cấu hình hiện chưa dùng được. Phần đã đạt được giữ để tiếp tục.')
        if progress:
            total = sum(len(job[0]) for job in jobs)
            progress(total, total)
        return [''.join(values[job] for job in row) for row in parts]
