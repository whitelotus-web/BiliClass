"""Rasterize labelled, code-native media buttons for Office (no extra font file)."""

from pathlib import Path

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer


def icon_svg(language, paused=False, mini=False):
    label = {'vi': 'VI', 'en': 'EN', 'both': 'VI+EN'}[language]
    if mini:
        width, height = 160, 64
        plate = '<rect x="1" y="1" width="158" height="62" rx="16" fill="#fff" stroke="#cbdcf4" stroke-width="2"/>'
        glyph_transform = 'translate(6,6) scale(1.05)'
        badge = f'<rect x="72" y="23" width="80" height="32" rx="9" fill="#0869f9"/><text x="112" y="46" text-anchor="middle" font-size="24" fill="#fff">{label}</text>'
    else:
        width = height = 72
        plate = '<rect x="1" y="1" width="62" height="62" rx="15" fill="#fff" stroke="#cbdcf4" stroke-width="2"/>'
        glyph_transform = 'translate(3,2)'
        badge_width = 48 if language == 'both' else 28
        badge = f'<rect x="{72-badge_width}" y="48" width="{badge_width}" height="22" rx="7" fill="#0869f9"/><text x="{72-badge_width/2}" y="64" text-anchor="middle" font-size="16" fill="#fff">{label}</text>'
    glyph = ('<rect x="18" y="14" width="8" height="28" rx="2" fill="#0869f9"/><rect x="33" y="14" width="8" height="28" rx="2" fill="#0869f9"/>' if paused else
             '<path d="M11 22h10l13-10v34L21 36H11z M41 20q9 8 0 16 M46 14q15 14 0 28" fill="none" stroke="#0869f9" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><g font-family="Segoe UI" font-weight="700">{plate}<g transform="{glyph_transform}">{glyph}</g>{badge}</g></svg>'


def rasterize(source, path, width, height):
    renderer = QSvgRenderer(source)
    assert renderer.isValid()
    image = QImage(width, height, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    painter = QPainter(image)
    renderer.render(painter, QRectF(0, 0, width, height))
    painter.end()
    assert image.save(str(path))


def main():
    app = QGuiApplication.instance() or QGuiApplication([])
    app.setApplicationName('BiliClass media icon export')
    folder = Path(__file__).resolve().parents[1] / 'app/assets/actions'
    rasterize((folder / 'speaker-pause.svg').read_bytes(), folder / 'speaker-pause.png', 128, 128)
    for language in ('vi', 'en', 'both'):
        for paused in (False, True):
            for mini in (False, True):
                filename = 'speaker-' + ('pause-' if paused else '') + language + ('-mini' if mini else '') + '.png'
                rasterize(icon_svg(language, paused, mini).encode(), folder / filename, 320 if mini else 144, 128 if mini else 144)


if __name__ == '__main__':
    main()
