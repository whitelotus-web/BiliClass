"""One application identity for the window, taskbar and packaged executable."""

import os

from .paths import RESOURCE_ROOT

APP_SUBTITLE = 'Trợ lý dạy học song ngữ'


def configure_application(application):
    from PySide6.QtGui import QIcon

    from . import __version__

    if os.name == 'nt':
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('BiliClass.Desktop')
    application.setApplicationName('BiliClass')
    application.setOrganizationName('BiliClass')
    application.setApplicationVersion(__version__)
    application.setWindowIcon(QIcon(str(RESOURCE_ROOT / 'assets' / 'brand' / 'biliclass.ico')))
