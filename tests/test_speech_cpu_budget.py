"""The speech engine must not leave a process-wide BLAS limit behind."""

import numpy as np
import pytest
from threadpoolctl import threadpool_info

from app import speech


@pytest.mark.parametrize("failure", [False, True])
def test_blas_budget_is_limited_only_during_inference(monkeypatch, tmp_path, failure):
    before = threadpool_info()
    calls = []

    class Engine:
        def infer(self, text, voice):
            calls.append((text, voice))
            pools = [pool for pool in threadpool_info() if pool["user_api"] == "blas"]
            assert pools and all(pool["num_threads"] == 1 for pool in pools)
            if failure:
                raise RuntimeError("inference failed")
            return np.ones(4800, dtype=np.float32) * .05

    monkeypatch.setattr(speech, "_vieneu_engine", lambda _: Engine())
    path = tmp_path / "test.wav"
    if failure:
        with pytest.raises(RuntimeError, match="inference failed"):
            speech._synthesize_vieneu("Xin chào. Hello.", "vieneu:Mai Anh", 0, path)
    else:
        speech._synthesize_vieneu("Xin chào. Hello.", "vieneu:Mai Anh", 0, path)
        assert speech.valid_audio(path)
    assert calls == [("Xin chào. Hello.", "Mai Anh")]
    assert threadpool_info() == before
