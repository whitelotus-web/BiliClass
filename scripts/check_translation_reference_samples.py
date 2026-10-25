"""Tiny opt-in live comparison on synthetic school text, never teacher slides."""

import argparse
import json
import tempfile
from pathlib import Path
from threading import Event
from uuid import uuid4

from app.google_translation import TranslationProblem
from app.translation_knowledge import prepare
from app.translation_provider import SELECTABLE, build_translator, require_credentials

SAMPLES = (
    ('Toán', 'Xác suất có điều kiện',
     'Xác suất có điều kiện mô tả khả năng xảy ra của một biến cố khi đã biết biến cố khác xảy ra.'),
    ('Sinh học', 'Dịch mã',
     'Tế bào sử dụng thông tin trên RNA để tổng hợp protein trong quá trình dịch mã.'),
    ('Tin học', 'Xác thực',
     'Xác thực giúp kiểm tra danh tính người dùng trước khi cấp quyền truy cập.'),
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--library', required=True)
    parser.add_argument('--live', action='store_true', help='Use configured API credentials and a small amount of service quota')
    parser.add_argument('--fresh', action='store_true', help='Use a separate probe cache so old successes cannot hide current service errors')
    parser.add_argument('--report', default='reports/rc168-expanded-live-reference/samples.json')
    args = parser.parse_args()
    if not args.live:
        parser.error('Live calls require --live. No requests were sent.')
    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    probe_id = uuid4().hex if args.fresh else ''
    with tempfile.TemporaryDirectory(prefix='reference-probe-', dir=report.parent) as temporary:
        for provider in SELECTABLE:
            try:
                require_credentials(args.library, provider)
            except (OSError, ValueError) as exc:
                rows.append(dict(provider=provider, status='unavailable', code=getattr(exc, 'code', 'local_configuration')))
                continue
            for subject, heading, text in SAMPLES:
                folder = Path(temporary) / (provider + '-' + str(len(rows)))
                folder.mkdir()
                config = dict(translation_knowledge_version=1, translation_knowledge_online=True,
                              subject=subject, grade='11', title=heading, source_sha256='synthetic-probe')
                plan = prepare(temporary, folder, config, [dict(text=heading), dict(text=text)], Event(),
                               resolver=lambda *_a, **_k: None)
                try:
                    from app.google_translation import Translator

                    translator = build_translator(args.library, {'translation_provider': provider}, 500_000, Translator)
                    calls = []
                    transport = translator.transport

                    def counted(*values):
                        calls.append(True)
                        return transport(*values)

                    translator.transport = counted
                    if probe_id:
                        translator.cache_namespace += '|live-probe|' + probe_id
                    translator.configure_terms(subject, [])
                    translator.configure_knowledge(plan)
                    translated = translator.translate([heading, text], Event())
                    rows.append(dict(provider=provider, subject=subject, status='translated', source=[heading, text],
                                     english=translated, reference_terms=len(plan['terms']), api_calls=len(calls)))
                except (TranslationProblem, OSError, ValueError) as exc:
                    rows.append(dict(provider=provider, subject=subject, status='unavailable',
                                     code=getattr(exc, 'code', 'local_configuration')))
                    break  # No repeated failing calls or fallback to another service.
                report.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
    report.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(rows, ensure_ascii=False))


if __name__ == '__main__':
    main()
