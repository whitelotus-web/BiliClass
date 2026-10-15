"""Export the code-native BiliClass book mark to Windows icon sizes."""

import io
from pathlib import Path

from PIL import Image
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer


def main():
    folder = Path(__file__).resolve().parents[1] / 'app/assets/brand'
    renderer = QSvgRenderer(str(folder / 'biliclass.svg'))
    assert renderer.isValid()
    image = QImage(256, 256, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    painter = QPainter(image)
    renderer.render(painter, QRectF(0, 0, 256, 256))
    painter.end()
    assert image.save(str(folder / 'biliclass.png'))
    with Image.open(folder / 'biliclass.png') as png:
        output = io.BytesIO()
        png.save(output, format='ICO', sizes=[(s, s) for s in (16, 20, 24, 32, 40, 48, 64, 128, 256)])
        (folder / 'biliclass.ico').write_bytes(output.getvalue())


if __name__ == '__main__':
    main()
