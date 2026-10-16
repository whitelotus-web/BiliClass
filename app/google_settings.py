"""Small Qt facade; QML only receives masked key metadata."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from .google_translation import DEFAULT_BUDGET, KeyStore


class GoogleSettings(QObject):
    changed = Signal()

    def __init__(self, bridge):
        super().__init__(bridge)
        self.bridge = bridge
        self._state = {"keys": [], "budget": DEFAULT_BUDGET, "configured": False, "message": ""}
        self.refresh()

    @Property("QVariantMap", notify=changed)
    def state(self):
        return self._state

    def store(self):
        return KeyStore(self.bridge.library.directory)

    @Slot()
    def refresh(self):
        try:
            rows = self.store().public()
            self._state = {
                "keys": rows,
                "configured": bool(rows),
                "budget": self.bridge.library.setting("google_character_budget", DEFAULT_BUDGET),
                "month": KeyStore.month(),
                "message": "",
            }
        except (ValueError, OSError) as exc:
            self._state = {**self._state, "keys": [], "configured": False, "message": str(exc)}
        from .local_ocr import model_paths
        from .vietnamese_ocr import pack_directory

        self._state["ocrReady"] = bool(model_paths() and pack_directory())
        self.changed.emit()

    @Slot()
    def prepareOcr(self):
        if self.bridge._busy:
            return
        from .local_ocr import prepare_models

        def done(_):
            self.refresh()
            self.bridge.inform(
                "Đã chuẩn bị nhận diện chữ Việt–Anh trong ảnh. Ảnh được đọc tại máy."
                if self._state["ocrReady"]
                else "Đã có OCR cơ bản. Cần gói OCR Việt–Anh đầy đủ của BiliClass để kiểm tra dấu trước khi tự che chữ trong ảnh."
            )

        self.bridge.launch(prepare_models, done)

    @Slot(str, int, result=bool)
    def save(self, text, budget):
        if self.bridge._busy:
            return False
        try:
            if not 1 <= budget <= DEFAULT_BUDGET:
                raise ValueError("Giới hạn ký tự từ 1 đến 500.000/dự án/tháng.")
            if text.strip():
                self.store().add(text)
            self.bridge.library.set_setting("google_character_budget", budget)
            self.refresh()
            if text.strip() and not self._state.get("configured"):
                self.bridge.inform(
                    self._state.get("message")
                    or "Chưa đọc lại được key vừa lưu. Giữ nội dung nhập và thử lưu lại.",
                    True,
                )
                return False
            self.bridge.inform("Đã lưu cấu hình Google Dịch. Key được mã hóa trên tài khoản Windows này.")
            return True
        except (ValueError, OSError) as exc:
            self.bridge.inform(str(exc), True)
            return False

    @Slot(str)
    def remove(self, key_id):
        if not self.bridge._busy:
            try:
                self.store().remove(key_id)
                self.refresh()
            except (ValueError, OSError) as exc:
                self.bridge.inform(str(exc), True)

    @Slot()
    def recheck(self):
        if not self.bridge._busy:
            self.store().recheck()
            self.refresh()
            self.bridge.inform("Đã cho phép thử lại key ở lượt dịch tiếp theo. Bộ đếm ký tự được giữ nguyên.")
