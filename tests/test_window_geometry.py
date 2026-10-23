import pytest
from PySide6.QtCore import QPoint, QRect, QSize

from app.window_geometry import normal_geometry


@pytest.mark.parametrize('scale', [1, 1.25, 1.5, 2])
@pytest.mark.parametrize('physical', [(1366, 728), (1920, 1040), (1536, 824)])
@pytest.mark.parametrize('origin', [(0, 0), (-1536, 40), (80, -900)])
def test_laptop_startup_frame_and_minimum_fit_logical_work_area(scale, physical, origin):
    area = QRect(*origin, int(physical[0]/scale), int(physical[1]/scale))
    margins = (8, 30, 8, 8)
    client, minimum = normal_geometry(area, QSize(1366, 850), margins)
    outer = client.adjusted(-8, -30, 8, 8)
    assert area.contains(outer)
    assert outer.height() < area.height(), 'Normal opening leaves room above the taskbar'
    assert outer.width() < area.width()
    assert minimum.width() <= client.width() and minimum.height() <= client.height()
    assert abs(outer.center().x() - area.center().x()) <= 1
    assert abs(outer.center().y() - area.center().y()) <= 1


@pytest.mark.parametrize('position', [QPoint(-5000, -5000), QPoint(5000, 5000), QPoint(100, 100)])
def test_restore_and_screen_changes_clamp_position_without_progressive_shrinking(position):
    area = QRect(-1200, 35, 1200, 665)
    margins = (8, 0, 8, 8)  # Expanded Windows caption is already in the client.
    rect, minimum = normal_geometry(area, QSize(1366, 850), margins, position)
    assert area.contains(rect.adjusted(-8, 0, 8, 8))
    for _ in range(5):
        restored, restored_minimum = normal_geometry(area, rect.size(), margins, rect.topLeft())
        assert restored == rect and restored_minimum == minimum


def test_large_screen_preserves_default_size_and_an_existing_valid_user_position():
    area = QRect(1920, 0, 1920, 1040)
    rect, minimum = normal_geometry(area, QSize(1366, 850), (8, 0, 8, 8), QPoint(2030, 40))
    assert rect == QRect(2030, 40, 1366, 850)
    assert minimum == QSize(1080, 700)
