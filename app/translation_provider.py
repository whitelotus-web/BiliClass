"""Explicit opt-in routing. Legacy jobs always retain Google; no silent fallback."""

from contextlib import closing
from pathlib import Path

from .google_translation import DEFAULT_BUDGET, KeyStore, TranslationProblem
from .library import Library

PROVIDERS = {'google': 'Google Cloud Translation', 'azure': 'Microsoft Azure Translator'}


def validate(provider):
    if provider not in PROVIDERS:
        raise TranslationProblem('api_settings', 'Cơ chế dịch chưa hợp lệ. Chọn lại trong Cài đặt → Google Dịch.')
    return provider


def snapshot(directory, provider=None):
    if not (Path(directory) / 'library.db').exists():
        provider = validate(provider if provider is not None else 'google')
        maximum = 2_000_000 if provider == 'azure' else DEFAULT_BUDGET
        budget = maximum
    else:
        with closing(Library.read_only(directory)) as library:
            provider = validate(provider if provider is not None else library.setting('translation_provider', 'google'))
            maximum = 2_000_000 if provider == 'azure' else DEFAULT_BUDGET
            budget = library.setting(provider + '_character_budget', maximum)
    if type(budget) is not int or not 1 <= budget <= maximum:
        raise TranslationProblem('api_settings', 'Giới hạn ký tự chưa hợp lệ. Lưu lại cấu hình dịch trong Cài đặt.')
    return {'translation_provider': provider, 'translation_budget': budget}


def require_credentials(directory, provider):
    validate(provider)
    if provider == 'azure':
        from .azure_translation import AzureKeyStore

        configured = bool(AzureKeyStore(directory).keys())
    else:
        configured = bool(KeyStore(directory).keys())
    if not configured:
        raise TranslationProblem('api_settings', f'Thêm cấu hình {PROVIDERS[provider]} trong Cài đặt → Google Dịch trước khi chuyển đổi.')


def build_translator(directory, config, legacy_budget, google_factory):
    # Missing field means an RC167 checkpoint, even when Settings now selects Azure.
    provider = validate(config.get('translation_provider', 'google'))
    budget = config.get('translation_budget', legacy_budget if provider == 'google' else 2_000_000)
    if provider == 'google':
        return google_factory(directory, budget)
    from .azure_translation import AzureTranslator

    return AzureTranslator(directory, budget)
