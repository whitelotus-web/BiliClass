"""The speech engine must not leave a process-wide BLAS limit behind."""

import ctypes
import os
import shutil
from uuid import uuid4

import numpy as np
import pytest
from threadpoolctl import threadpool_info

from app import speech
from app.voice_threads import _blas_controls, blas_budget


def pool_snapshot():
    if os.name == 'nt':
        return [{'handle': handle, 'user_api': 'blas', 'num_threads': get()}
                for handle, get, _ in _blas_controls()]
    return threadpool_info()


@pytest.mark.parametrize("failure", [False, True])
def test_blas_budget_is_limited_only_during_inference(monkeypatch, tmp_path, failure):
    before = pool_snapshot()
    calls = []

    class Engine:
        def infer(self, text, voice):
            calls.append((text, voice))
            pools = [pool for pool in pool_snapshot() if pool["user_api"] == "blas"]
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
    assert pool_snapshot() == before


@pytest.mark.skipif(os.name != "nt", reason="Windows live DLL control")
def test_unicode_dll_is_controlled_by_its_loaded_handle_without_path_reload(tmp_path):
    # threadpoolctl's Windows filename snapshot can replace Vietnamese letters
    # with '?'. Read the live module's Unicode filename instead.
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetModuleFileNameW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint32]
    kernel.GetModuleFileNameW.restype = ctypes.c_uint32
    name = ctypes.create_unicode_buffer(32768)
    assert kernel.GetModuleFileNameW(_blas_controls()[0][0], name, len(name))
    source = name.value
    folder = tmp_path / "Cài đặt tiếng Việt – giọng đọc"
    folder.mkdir()
    destination = folder / ("libscipy_openblas_biliclass_test_" + uuid4().hex + ".dll")
    shutil.copyfile(source, destination)
    library = ctypes.CDLL(str(destination))
    try:
        native = next(control for control in _blas_controls() if control[0] == library._handle)
        previous = native[1]()
        with blas_budget():
            assert native[1]() == 1
        assert native[1]() == previous
        with pytest.raises(RuntimeError, match="stop"):
            with blas_budget():
                assert native[1]() == 1
                raise RuntimeError("stop")
        assert native[1]() == previous
    finally:
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.FreeLibrary.argtypes = [ctypes.c_void_p]
        kernel.FreeLibrary.restype = ctypes.c_int
        assert kernel.FreeLibrary(library._handle)
