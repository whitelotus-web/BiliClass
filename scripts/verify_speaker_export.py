"""Office imports and preserves exported independent speaker command sequences.

Uses only disposable, silent fixtures. This checks Office's parser and media API;
it does not certify physical mouse clicks or the visible animation state.
"""

import hashlib
import json
import sys
import tempfile
import time
import zipfile
from pathlib import Path

import pythoncom
import win32com.client
from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from test_teaching_session import prepared_lesson

from app.lesson_files import save_presentation
from app.source_deck import NS, source_slide_parts


def commands(path):
    with zipfile.ZipFile(path) as archive:
        return [[node.get('cmd') for node in etree.fromstring(archive.read(part)).findall('.//p:cmd', NS)]
                for part in source_slide_parts(path)]


def main():
    pythoncom.CoInitialize()
    report = Path('reports/rc77/speaker-export.json')
    report.parent.mkdir(parents=True, exist_ok=True)
    presentation = None
    try:
        with tempfile.TemporaryDirectory(prefix='bcl-native-speaker-') as folder:
            folder = Path(folder)
            lesson, preview, directory, source = prepared_lesson(folder)
            original = hashlib.sha256(source.read_bytes()).hexdigest()
            exported, normalized = folder / 'Exported.pptx', folder / 'Office roundtrip.pptx'
            save_presentation(lesson, preview, directory, exported, with_voice=True)
            before = commands(exported)
            office = win32com.client.Dispatch('PowerPoint.Application')
            presentation = office.Presentations.Open(str(exported), ReadOnly=True, Untitled=False, WithWindow=False)
            assert presentation.Slides.Count == 3
            counts = [slide.TimeLine.InteractiveSequences.Count for slide in presentation.Slides]
            assert counts == [6, 0, 2], counts
            presentation.SaveCopyAs(str(normalized), 24)
            after = commands(normalized)
            assert [sorted(page) for page in before] == [sorted(page) for page in after], (before, after)
            show = presentation.SlideShowSettings
            show.ShowWithAnimation = True
            show.ShowType = 2  # A windowed fixture; no synthetic OS input.
            view = show.Run().View
            try:
                time.sleep(.15)
                media = [shape for shape in presentation.Slides(1).Shapes
                         if str(shape.Name).startswith('BiliClass audio ')]
                assert len(media) == 3
                for shape in media:
                    player = view.Player(shape.Id)
                    assert player.State != 0, 'Export must never autoplay'
                    player.Play()
                    time.sleep(.12)
                    assert player.State == 0, 'Off-canvas media must still play on demand'
                    player.Pause()
                    assert player.State == 1
                    player.Play()
                    assert player.State == 0
                    player.Stop()
            finally:
                view.Exit()
            assert hashlib.sha256(source.read_bytes()).hexdigest() == original
            result = {'status': 'passed', 'native_interactive_sequences': counts,
                      'command_roundtrip_preserved': True, 'native_off_canvas_audio_play_pause_resume': True,
                      'no_autoplay': True, 'source_unchanged': True,
                      'scope': 'Office parser and media API on silent fixtures; physical click/icon-state test still required'}
            report.write_text(json.dumps(result, indent=2), encoding='utf-8')
            print(json.dumps(result), flush=True)
    finally:
        if presentation is not None:
            # SlideShowView.Exit can already close a WithWindow=False fixture.
            try:
                presentation.Saved = True
                presentation.Close()
            except pythoncom.com_error:
                pass
        pythoncom.CoUninitialize()


if __name__ == '__main__':
    main()
