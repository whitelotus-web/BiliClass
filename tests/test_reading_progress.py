from app.reading_progress import ReadingProgress


def lines(*numbers):
    return [(('en', number, 0), f'Line {number}') for number in numbers]


def test_initial_then_reveal_reads_only_new_lines_without_automatic_replay():
    progress = ReadingProgress()
    progress.enter(256)
    assert progress.choose('en', lines(1)) == lines(1)
    progress.finish(256, 'en', lines(1))
    assert progress.choose('en', lines(1)) == [], 'Auto waits for new content instead of replaying the old build'
    assert progress.choose('en', lines(1, 2, 3)) == lines(2, 3)
    progress.finish(256, 'en', lines(2, 3))
    assert progress.choose('en', lines(1, 2, 3, 4, 5)) == lines(4, 5)
    progress.finish(256, 'en', lines(4, 5))
    assert progress.choose('en', lines(1, 2, 3, 4, 5, 6)) == lines(6)
    progress.finish(256, 'en', lines(6))
    assert progress.choose('en', lines(1, 2, 3, 4, 5, 6)) == []


def test_repeated_title_skipped_only_on_forward_continuation_and_after_it_was_read():
    progress = ReadingProgress()
    title = [(('en', 'title', 0), 'Energy')]
    progress.enter(256, 1)
    progress.finish(256, 'en', title)
    for page in (2, 3):
        progress.enter(255 + page, page)
        assert progress.choose('en', title + lines(page), titles={'Energy'}) == lines(page)
        assert progress.choose('vi', title, titles={'Energy'}) == title
    progress.enter(256, 1)
    assert progress.choose('en', title, titles={'Energy'}) == title, 'Backwards navigation permits rereading'


def test_reveal_several_steps_before_first_read_and_keep_unfinished_chunks():
    progress = ReadingProgress()
    progress.enter(256)
    assert progress.choose('en', lines(1, 2, 3)) == lines(1, 2, 3)
    progress.finish(256, 'en', lines(1))  # Interrupted during line 2.
    assert progress.choose('en', lines(1, 2, 3, 4, 5)) == lines(2, 3, 4, 5)
    assert progress.choose('vi', lines(1, 2, 3)) == lines(1, 2, 3), 'Language choices have their own progress'
    progress.enter(257)
    assert progress.choose('en', lines(1, 2, 3, 4, 5, 6)) == lines(1, 2, 3, 4, 5, 6)
    progress.finish(256, 'en', lines(1, 2, 3))  # A stale completion from the previous slide.
    assert progress.choose('en', lines(1, 2, 3)) == lines(1, 2, 3)
