"""Keep the normal desktop window inside its screen's usable work area."""

from PySide6.QtCore import QObject, QPoint, QRect, QSize, Qt, QTimer


def normal_geometry(area, requested, margins=(0, 0, 0, 0), position=None):
    """All values are Qt logical pixels; area excludes the Windows taskbar.

    Budget the native frame as well as the client, and leave a little room
    around a normal window. Never impose a minimum larger than that budget.
    """
    left, top, right, bottom = (max(0, int(n)) for n in margins)
    frame_width, frame_height = left + right, top + bottom
    cap_width = max(1, int(area.width() * .94) - frame_width)
    cap_height = max(1, int(area.height() * .92) - frame_height)
    minimum = QSize(min(1080, cap_width), min(700, cap_height))
    width = max(minimum.width(), min(requested.width(), cap_width))
    height = max(minimum.height(), min(requested.height(), cap_height))
    outer_width, outer_height = width + frame_width, height + frame_height
    if position is None:
        x = area.x() + (area.width() - outer_width) // 2 + left
        y = area.y() + (area.height() - outer_height) // 2 + top
    else:
        x = min(max(position.x(), area.x() + left), area.x() + area.width() - outer_width + left)
        y = min(max(position.y(), area.y() + top), area.y() + area.height() - outer_height + top)
    return QRect(x, y, width, height), minimum


class WindowGeometry(QObject):
    """Fit before showing, after native frame creation and on screen changes.

    Normal maximize/minimize/fullscreen behavior belongs to Windows. Never
    resize those states or change the normal restore size to the maximized size.
    """

    def __init__(self, window, requested):
        super().__init__(window)
        self.window = window
        self.screen = None
        self._initial = True
        self._requested = QSize(requested)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.fit)
        window.screenChanged.connect(self._screen_changed)
        window.visibleChanged.connect(self.schedule)
        window.windowStateChanged.connect(self.schedule)
        self._screen_changed(window.screen())
        self.fit()

    def _screen_changed(self, screen):
        if self.screen is not None:
            self.screen.availableGeometryChanged.disconnect(self.schedule)
            self.screen.logicalDotsPerInchChanged.disconnect(self.schedule)
        self.screen = screen
        if screen is not None:
            screen.availableGeometryChanged.connect(self.schedule)
            screen.logicalDotsPerInchChanged.connect(self.schedule)
        self.schedule()

    def schedule(self, *_):
        self._timer.start(0)

    def _area(self):
        return self.screen.availableGeometry() if self.screen else QRect()

    def fit(self):
        area = self._area()
        if area.isEmpty():
            return
        frame = self.window.frameMargins()
        margins = frame.left(), frame.top(), frame.right(), frame.bottom()
        geometry, minimum = normal_geometry(area, self._requested if self._initial else self.window.size(),
                                             margins, None if self._initial else self.window.position())
        self.window.setMinimumSize(minimum)
        if self.window.windowState() != Qt.WindowNoState:
            return
        self.window.resize(geometry.size())
        self.window.setPosition(QPoint(geometry.x(), geometry.y()))
        # A hidden window can still have unknown frame margins. Re-center once
        # on the first visible pass, before preserving subsequent user placement.
        if self.window.isVisible():
            self._initial = False
