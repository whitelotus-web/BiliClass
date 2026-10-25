"""Unit tests never contact the optional public terminology service."""

import pytest


@pytest.fixture(autouse=True)
def reference_network_fixture(monkeypatch):
    monkeypatch.setattr('app.translation_knowledge.lookup', lambda *args, **kwargs: None)
