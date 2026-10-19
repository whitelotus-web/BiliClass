from app.reading_progress import ReadingProgress


def lines(*numbers):
    return [(('en', number, 0), f'Line {number}') for number in numbers]


def test_initial_then_reveal_and_read_only_new_lines_and_replay_visible_after_completion():
    progress = ReadingProgress()
    progress.enter(256)
    assert progress.choose('en', lines(1)) == lines(1)
    progress.finish(256, 'en', lines(1))
    assert progress.choose('en', lines(1)) == lines(1), 'Replay the first line without revealing hidden text'
    assert progress.choose('en', lines(1, 2, 3)) == lines(2, 3)
    progress.finish(256, 'en', lines(2, 3))
    assert progress.choose('en', lines(1, 2, 3, 4, 5)) == lines(4, 5)
    progress.finish(256, 'en', lines(4, 5))
    assert progress.choose('en', lines(1, 2, 3, 4, 5, 6)) == lines(6)
    progress.finish(256, 'en', lines(6))
    assert progress.choose('en', lines(1, 2, 3, 4, 5, 6)) == lines(1, 2, 3, 4, 5, 6)


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
