"""Qt bridge for reviewed lesson assistance and question authoring."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from .content import assistant_response


class TeachingBridge(QObject):
    changed = Signal()

    def __init__(self, bridge):
        super().__init__(bridge)
        self.bridge = bridge
        self._response = {"available": False, "text": "Chọn một hành động để dùng nội dung đã chuẩn bị.", "untouched": True}
        bridge.selectionChanged.connect(self.reset)
        bridge.changed.connect(self.changed)

    @Slot()
    def reset(self):
        self._response = {"available": False, "text": "Chọn một hành động để dùng nội dung đã chuẩn bị.", "untouched": True}
        self.changed.emit()

    @Property("QVariantList", notify=changed)
    def items(self):
        return self.bridge.segment.get("support", [])

    @Property("QVariantList", notify=changed)
    def questions(self):
        return self.bridge.lesson.get("questions", [])

    @Property("QVariantMap", notify=changed)
    def response(self):
        return self._response

    def update(self, action):
        if self.bridge.busy:
            return False
        try:
            self.bridge._lesson = action()
            self.bridge.inform("Đã lưu nội dung chuẩn bị cho bài.")
            self.changed.emit()
            return True
        except Exception as exc:
            self.bridge.inform(str(exc), True)
            return False

    @Slot(str, str, str, str, bool, result=bool)
    def saveSupport(self, item_id, kind, vi, en, approved):
        return self.update(lambda: self.bridge.library.save_support(
            self.bridge.lesson["id"], self.bridge.segment["id"],
            {"kind": kind, "vi": vi, "en": en, "approved": approved}, item_id
        ))

    @Slot(str)
    def deleteSupport(self, item_id):
        self.update(lambda: self.bridge.library.delete_support(
            self.bridge.lesson["id"], self.bridge.segment["id"], item_id
        ))

    @Slot(str, str, str, str, str, int, str, bool, str, str, str, result=bool)
    def saveQuestion(self, question_id, kind, vi, en, options, correct_index, rationale, approved, concept_label, comparison_group, rationale_en):
        parsed = []
        for line in options.splitlines():
            if not line.strip():
                continue
            parts = [part.strip() for part in line.split("|")]
            if len(parts) not in (2, 3):
                self.bridge.inform("Mỗi lựa chọn viết: tiếng Việt | English | hiểu nhầm (tùy chọn).", True)
                return False
            parsed.append({"vi": parts[0], "en": parts[1], "misconception": parts[2] if len(parts) == 3 else ""})
        existing = next((q for q in self.questions if q["id"] == question_id), None)
        value = {"kind": kind, "vi": vi, "en": en, "options": parsed,
                 "correct": chr(65 + correct_index) if 0 <= correct_index < 6 else None,
                 "concept_id": existing["concept_id"] if existing else self.bridge.segment["id"],
                 "concept_label": concept_label.strip() or self.bridge.segment["locator"],
                 "comparison_group": comparison_group, "rationale_en": rationale_en,
                 "rationale_vi": rationale, "approved": approved}
        return self.update(lambda: self.bridge.library.save_question(self.bridge.lesson["id"], value, question_id))

    @Slot(str)
    def deleteQuestion(self, question_id):
        self.update(lambda: self.bridge.library.delete_question(self.bridge.lesson["id"], question_id))

    @Slot(str, str)
    def ask(self, action, language):
        if language not in ("vi", "en"):
            return
        self._response = assistant_response(self.bridge.segment, action, language,
                                            self.bridge.lesson.get("level", 2))
        self.changed.emit()
