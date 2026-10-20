from app.slideshow_overlay import pixels


def test_play_and_pause_have_visible_different_artwork_with_premultiplied_alpha():
    for language in ('vi', 'en', 'both'):
        ready = pixels(language, False, 42, 42)
        pause = pixels(language, True, 42, 42)
        assert ready != pause
        for data in (ready, pause):
            assert len(data) == 42 * 42 * 4
            assert sum(alpha > 32 for alpha in data[3::4]) > 100
            assert all(max(data[i:i + 3]) <= data[i + 3] for i in range(0, len(data), 4))
