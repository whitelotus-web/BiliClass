"""Rasterize the code-native pause badge for Office's media picture overlay."""

from pathlib import Path

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer


def main():
    folder = Path(__file__).resolve().parents[1] / 'app/assets/actions'
    renderer = QSvgRenderer(str(folder / 'speaker-pause.svg'))
    assert renderer.isValid()
    image = QImage(128, 128, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    painter = QPainter(image)
    renderer.render(painter, QRectF(0, 0, 128, 128))
    painter.end()
    assert image.save(str(folder / 'speaker-pause.png'))


if __name__ == '__main__':
    main()
