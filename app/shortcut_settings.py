"""Mascot shortcut preferences, separate from appearance preferences."""

import sqlite3

from PySide6.QtCore import Property, QObject, Signal, Slot

from .slideshow_shortcuts import DEFAULTS, display, saved_bindings, validate


class ShortcutSettings(QObject):
    changed = Signal()

    def __init__(self, bridge):
        super().__init__(bridge)
        self.bridge = bridge
        self.bindings = saved_bindings(bridge.library.setting('mascot_shortcuts', {}))
        self.message = ''
        self.error = False

    @Property('QVariantMap', notify=changed)
    def state(self):
        return {'bindings': dict(self.bindings), 'labels': {k: display(v) for k, v in self.bindings.items()},
                'message': self.message, 'error': self.error}

    @Slot('QVariantMap', result=bool)
    def save(self, bindings):
        try:
            result = validate(bindings)
            self.bridge.library.set_setting('mascot_shortcuts', result)
        except (ValueError, OSError) as exc:
            self.message, self.error = str(exc), True
            self.changed.emit()
            return False
        except sqlite3.Error:
            self.message, self.error = 'Chưa lưu được phím đọc. Thử lại khi thư viện sẵn sàng.', True
            self.changed.emit()
            return False
        self.bindings = result
        worker = self.bridge.powerpoint_worker
        if worker:
            worker.navigate('set_shortcuts', result)
        self.message, self.error = 'Đã lưu phím đọc. Áp dụng ngay cho bài đang gắn với Mascot.', False
        self.changed.emit()
        return True

    @Slot()
    def reset(self):
        self.save(dict(DEFAULTS))
