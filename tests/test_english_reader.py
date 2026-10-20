import time
from threading import Event

import pytest
from PySide6.QtCore import QCoreApplication

from app import speech
from app.english_reader import EnglishReader, WindowsWavePlayer


class Player:
    def __init__(self):
        self.calls = []
        self.opened = False
        self.ended = False

    def play(self, path):
        self.calls.append(("play", path))
        self.opened = True
        self.ended = False

    def stop(self):
        self.calls.append(("stop",))
        self.opened = False

    def pause(self):
        self.calls.append(("pause",))

    def resume(self):
        self.calls.append(("resume",))

    def finished(self):
        return self.ended


@pytest.fixture(scope="session")
def qt():
    return QCoreApplication.instance() or QCoreApplication([])


def wait(qt, condition):
    deadline = time.monotonic() + 3
    while not condition() and time.monotonic() < deadline:
        qt.processEvents()
        time.sleep(.01)
    assert condition()


def test_single_slide_queue_pause_resume_end_and_no_auto_read(qt, tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(speech, "synthesize", lambda text, *_: calls.append(text) or {"path": text})
    player = Player()
    reader = EnglishReader(tmp_path, player=player)
    finished = []
    reader.chunkFinished.connect(finished.append)
    assert reader.state == "stopped" and not calls
    reader.start(["Kinetic energy", "The energy is conserved."], "kokoro:af_heart", 0)
    wait(qt, lambda: reader.state == "reading")
    reader.pause()
    assert reader.state == "paused"
    player.ended = True
    reader._tick()
    assert reader.position == 0
    assert not finished
    reader.resume()
    assert reader.state == "reading"
    player.ended = True
    reader._tick()
    wait(qt, lambda: len(calls) == 2 and reader.state == "reading")
    player.ended = True
    reader._tick()
    assert reader.state == "stopped"
    assert finished == [0, 1]
    assert calls == ["Kinetic energy", "The energy is conserved."]
    assert [c[0] for c in player.calls].count("pause") == 1
    assert [c[0] for c in player.calls].count("resume") == 1
    reader.shutdown()


def test_paragraph_gap_can_pause_and_cancel_without_late_playback(qt, tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(speech, 'synthesize', lambda text, *_: calls.append(text) or {'path':text})
    player = Player()
    reader = EnglishReader(tmp_path, player=player)
    reader.start(['Heading', 'Paragraph body.'], 'english', 0)
    wait(qt, lambda: reader.state == 'reading')
    player.ended = True
    reader._tick()
    assert reader._between_chunks and reader.gap.isActive() and calls == ['Heading']
    reader.pause()
    reader._finish_gap()
    assert calls == ['Heading'] and reader.state == 'paused'
    reader.resume()
    reader.stop()
    reader._finish_gap()
    assert not reader.gap.isActive() and calls == ['Heading'] and reader.state == 'stopped'
    reader.shutdown()


def test_cached_teaching_never_synthesizes_missing_audio(qt, tmp_path, monkeypatch):
    monkeypatch.setattr(speech, 'synthesize', lambda *_: pytest.fail('Teaching may only play existing audio'))
    reader = EnglishReader(tmp_path, player=Player())
    reader.start(['Missing recording'], 'vieneu:Mai Anh', 0, cache_only=True)
    assert reader.state == 'error' and reader.worker is None
    assert not reader.player.opened
    reader.shutdown()


def test_slide_change_cancels_pending_tts_without_late_playback(qt, tmp_path, monkeypatch):
    entered, release = Event(), Event()

    def slow(*_):
        entered.set()
        release.wait(2)
        return {"path": "old.wav"}

    monkeypatch.setattr(speech, "synthesize", slow)
    player = Player()
    reader = EnglishReader(tmp_path, player=player)
    reader.start(["Old slide"], "english", 0)
    wait(qt, entered.is_set)
    reader.stop()
    release.set()
    wait(qt, lambda: reader.worker is None)
    assert not any(c[0] == "play" for c in player.calls)
    assert reader.state == "stopped"
    reader.shutdown()


def test_repeated_clicks_do_not_overlap_workers_or_play_old_result(qt, tmp_path, monkeypatch):
    entered, release = Event(), Event()
    calls = []

    def slow(text, *_):
        calls.append(text)
        entered.set()
        release.wait(2)
        return {"path": text}

    monkeypatch.setattr(speech, "synthesize", slow)
    player = Player()
    reader = EnglishReader(tmp_path, player=player)
    reader.start(["First request"], "english", 0)
    wait(qt, entered.is_set)
    reader.start(["Second request"], "english", 0)
    reader.start(["Final request"], "english", 0)
    release.set()
    wait(qt, lambda: reader.state == "reading")
    assert calls == ["First request", "Final request"]
    assert [c for c in player.calls if c[0] == "play"] == [("play", "Final request")]
    reader.shutdown()


def test_pause_while_synthesizing_keeps_audio_paused(qt, tmp_path, monkeypatch):
    entered, release = Event(), Event()

    def slow(*_):
        entered.set()
        release.wait(2)
        return {"path": "ready.wav"}

    monkeypatch.setattr(speech, "synthesize", slow)
    player = Player()
    reader = EnglishReader(tmp_path, player=player)
    reader.start(["The energy is conserved."], "english", 0)
    wait(qt, entered.is_set)
    reader.pause()
    release.set()
    wait(qt, lambda: reader.worker is None)
    assert reader.state == "paused" and player.calls[-1] == ("pause",)
    reader.resume()
    assert reader.state == "reading"
    reader.shutdown()


def test_tts_failure_is_visible_and_releases_playback(qt, tmp_path, monkeypatch):
    def failed(*_):
        raise ValueError("unavailable engine")

    monkeypatch.setattr(speech, "synthesize", failed)
    reader = EnglishReader(tmp_path, player=Player())
    errors = []
    reader.failed.connect(errors.append)
    reader.start(["The energy is conserved."], "english", 0)
    wait(qt, lambda: reader.state == "error")
    assert errors and not reader.player.opened
    reader.shutdown()


def test_native_player_uses_short_unchanged_copy_and_cleans_only_owned_file(tmp_path, monkeypatch):
    source = tmp_path / ("a"*64 + ".wav")
    source.write_bytes(b"wav fixture")
    player = WindowsWavePlayer()
    commands = []
    monkeypatch.setattr(player, "_command", lambda command: commands.append(command) or "")
    player.play(source)
    directory = player.playback_directory
    assert (directory / "read.wav").read_bytes() == source.read_bytes()
    assert 'read.wav"' in commands[0] and source.name not in commands[0]
    player.stop()
    assert not directory.exists() and source.read_bytes() == b"wav fixture"


def test_volume_attenuates_private_pcm_without_modifying_cache_and_keeps_pause_position(tmp_path, monkeypatch):
    import array
    import wave

    path = tmp_path / 'speech.wav'
    with wave.open(str(path), 'wb') as audio:
        audio.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
        audio.writeframes(array.array('h', [10000, -10000] * 24000).tobytes())
    original = path.read_bytes()
    player = WindowsWavePlayer()
    commands = []
    def command(value):
        commands.append(value)
        return '450' if value.endswith(' position') else 'paused' if value.endswith(' mode') else ''
    monkeypatch.setattr(player, '_command', command)
    player.play(path)
    player.set_volume(50)
    with wave.open(str(player.playback_directory / 'read.wav'), 'rb') as audio:
        assert array.array('h', audio.readframes(2)).tolist() == [5000, -5000]
    assert commands[-1] == f'seek {player.alias} to 450'
    assert path.read_bytes() == original
    player.stop()
