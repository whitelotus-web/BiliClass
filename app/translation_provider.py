"""Explicit opt-in routing. Legacy jobs always retain Google; no silent fallback."""

from contextlib import closing
from pathlib import Path

from .google_translation import DEFAULT_BUDGET, KeyStore, TranslationProblem
from .library import Library

PROVIDERS = {'google': 'Google Cloud Translation', 'languageapp': 'Google Apps Script · LanguageApp',
             'gemini': 'Gemini API', 'deepl': 'DeepL API Developer', 'azure': 'Microsoft Azure Translator (bài cũ)'}
SELECTABLE = ('google', 'languageapp', 'gemini', 'deepl')


def maximum(provider):
    if provider in {'google', 'azure'}:
        return DEFAULT_BUDGET if provider == 'google' else 2_000_000
    from .alternative_translation import LIMITS

    return LIMITS[provider]


def validate(provider):
    if provider not in PROVIDERS:
        raise TranslationProblem('api_settings', 'Cơ chế dịch chưa hợp lệ. Chọn lại trong Cài đặt → Dịch thuật.')
    return provider


def snapshot(directory, provider=None, *, include_profile=True):
    from .translation_knowledge import MODE_VERSION, options

    knowledge = dict(translation_knowledge_version=MODE_VERSION, translation_knowledge_online=True)
    if not (Path(directory) / 'library.db').exists():
        provider = validate(provider if provider is not None else 'google')
        ceiling = maximum(provider)
        budget = ceiling
    else:
        with closing(Library.read_only(directory)) as library:
            knowledge = options(library)
            saved = library.setting('translation_provider', 'google')
            # Only new work migrates away from Azure. Explicit checkpoint routes stay pinned.
            provider = validate(provider if provider is not None else 'google' if saved == 'azure' else saved)
            ceiling = maximum(provider)
            budget = library.setting(provider + '_character_budget', ceiling)
    if type(budget) is not int or not 1 <= budget <= ceiling:
        raise TranslationProblem('api_settings', 'Giới hạn ký tự chưa hợp lệ. Lưu lại cấu hình dịch trong Cài đặt.')
    result = {'translation_provider': provider, 'translation_budget': budget, **knowledge}
    if include_profile and provider in SELECTABLE[1:]:
        from .alternative_translation import AlternativeStore

        result['translation_profile'] = AlternativeStore(directory, provider).profile()
    return result


def require_credentials(directory, provider):
    validate(provider)
    if provider == 'azure':
        from .azure_translation import AzureKeyStore

        configured = bool(AzureKeyStore(directory).keys())
    elif provider == 'google':
        configured = bool(KeyStore(directory).keys())
    else:
        from .alternative_translation import AlternativeStore

        configured = bool(AlternativeStore(directory, provider).keys())
    if not configured:
        raise TranslationProblem('api_settings', f'Thêm cấu hình {PROVIDERS[provider]} trong Cài đặt → Dịch thuật trước khi chuyển đổi.')


def build_translator(directory, config, legacy_budget, google_factory):
    # Missing field means an RC167 checkpoint, even when Settings now selects Azure.
    provider = validate(config.get('translation_provider', 'google'))
    budget = config.get('translation_budget', legacy_budget if provider == 'google' else maximum(provider))
    if provider == 'google':
        return google_factory(directory, budget)
    if provider == 'azure':
        from .azure_translation import AzureTranslator

        return AzureTranslator(directory, budget)
    from .alternative_translation import AlternativeTranslator

    return AlternativeTranslator(directory, provider, budget, profile=config.get('translation_profile'))
