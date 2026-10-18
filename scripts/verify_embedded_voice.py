"""Explicitly play saved native PowerPoint audio; no synthesis or source writes."""

import argparse
import hashlib
import io
import json
import multiprocessing
import queue
import time
import wave
import zipfile
from pathlib import Path

from app.powerpoint import _office_session


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--presentation', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    parser.add_argument('--slides', type=int, nargs='+', default=[1])
    args = parser.parse_args()
    path = args.presentation.resolve(strict=True)
    original = hashlib.sha256(path.read_bytes()).hexdigest()
    with zipfile.ZipFile(path) as archive:
        names = [n for n in archive.namelist() if n.startswith('ppt/media/biliclass-') and n.endswith('.wav')]
        assert names, 'No embedded WAVs'
        with wave.open(io.BytesIO(archive.read(names[0])), 'rb') as audio:
            samples = audio.readframes(min(audio.getnframes(), audio.getframerate() * 5))
            assert audio.getnframes() and any(samples), 'Empty/silent saved voice'
    context = multiprocessing.get_context('spawn')
    commands, events = context.Queue(), context.Queue()
    child = context.Process(target=_office_session, args=(str(path), 1, commands, events, True))
    child.start()
    received = []

    def wait_for(check, seconds=40):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            try:
                event = events.get(timeout=.2)
            except queue.Empty:
                assert child.is_alive(), 'Office helper stopped unexpectedly'
                continue
            assert not event.get('error') and event.get('event') != 'media_error', event
            received.append(event)
            if check(event):
                return event
        raise TimeoutError('Native audio verification timed out')

    try:
        wait_for(lambda event: event.get('active'))
        for number in args.slides:
            commands.put(('goto', number))
            if number != 1:
                wait_for(lambda event: event.get('active') and event.get('slide') == number)
            for language in ('en', 'vi', 'both'):
                commands.put(('play_media', language))
                wait_for(lambda event: event.get('event') == 'media_started' and event.get('language') == language, 10)
                time.sleep(.6)
                commands.put(('pause_media', None))
                wait_for(lambda event: event.get('event') == 'media_paused', 10)
                commands.put(('resume_media', None))
                wait_for(lambda event: event.get('event') == 'media_resumed', 10)
                commands.put(('stop_media', None))
                wait_for(lambda event: event.get('event') == 'media_stopped', 10)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == original
        result = dict(status='passed', wav_files=len(names), nonzero_wav=True, source_unchanged=True,
                      native_languages=['en', 'vi', 'both'], native_pause_resume=True,
                      native_slides=args.slides,
                      scope='Actual Office playback API and nonzero WAV; no microphone/acoustic or pronunciation certification')
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result), flush=True)
    finally:
        commands.put(('stop', None))
        child.join(15)
        if child.is_alive():
            child.terminate()
            child.join(5)
        commands.close()
        events.close()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
