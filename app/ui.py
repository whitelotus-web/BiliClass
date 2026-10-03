import json
import os
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path
from threading import Event

from PySide6.QtCore import Property, QObject, QPoint, QThread, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices, QFont, QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle

from biliclass_m0.contracts import LevelPolicy
from biliclass_m0.paths import RESOURCES

from . import speech
from .classroom_ui import ClassroomBridge
from .input_analysis import analyze_document, assess_blocks
from .knowledge import ensure_builtin_foundation, load_pack
from .lesson_templates import block_type, catalog, example_plan, slide_pages, slide_plan, source_image
from .library import Library, lesson_status
from .pack import export_pack, import_pack
from .paths import RESOURCE_ROOT, user_data
from .portable_audio import available_audio
from .powerpoint import PowerPointSession, slide_for_locator, verified_presentation
from .readiness import assess
from .storage import backup_library, configure_logging, restore_backup
from .teaching import TeachingBridge
from .text_quality import review_warnings
from .translation import find_model, translate_draft
from .updater import check_for_update, download_and_stage, launch_install


class Job(QThread):
    completed = Signal(object, str)

    def __init__(self, action, parent):
        super().__init__(parent)
        self.action = action

    def run(self):
        try:
            self.completed.emit(self.action(), "")
        except Exception as exc:
            self.completed.emit(None, str(exc))


class Bridge(QObject):
    changed = Signal()
    selectionChanged = Signal()
    navigate = Signal(str)
    memoryChoicesAvailable = Signal()
    closeMemoryChoicesRequested = Signal()
    projectClassroomRequested = Signal()
    powerpointSlideChanged = Signal(int)
    mascotStateChanged = Signal()
    mascotPreferencesSaved = Signal(bool)
    updateChanged = Signal()
    updateProgress = Signal(int)
    inputAssessmentChanged = Signal()
    comparisonReady = Signal()

    @Property(bool, constant=True)
    def developmentMode(self):
        return not getattr(sys, "frozen", False)

    @Property(str, constant=True)
    def appVersion(self):
        from . import __version__

        return __version__

    @Property("QVariantMap", notify=updateChanged)
    def updateState(self):
        return self._update_state

    @Property(bool, notify=updateChanged)
    def updateApplying(self):
        return self._update_applying

    def __init__(self, library):
        super().__init__()
        self.library = library
        self.logger = configure_logging(library.directory)
        try:
            ensure_builtin_foundation(self.library)
        except Exception as exc:
            self.logger.warning("Could not install bundled knowledge foundation: %s", exc)
        self._lesson = {}
        self._segment_index = 0
        self._busy = False
        self._speaking = False
        self._speech_timer = QTimer(self)
        self._speech_timer.setSingleShot(True)
        self._speech_timer.timeout.connect(self.stopSpeech)
        self._message = ""
        self._error = False
        self._logo_revision = 0
        self.worker = None
        self.update_worker = None
        self._update_release = None
        self._update_package = None
        self._update_applying = False
        self._update_cancel = Event()
        self._update_state = {"checking": False, "downloading": False, "available": False,
                              "ready": False, "progress": 0, "version": "", "message": ""}
        self.updateProgress.connect(self._on_update_progress)
        self.callback = None
        self.job_result = None
        self.cancel_event = Event()
        self._memory_choices = []
        self._memory_request = None
        self._input_result = None
        self._input_path = ""
        self._conversion_report = []
        self._comparison = {}
        self.powerpoint_worker = None
        self._powerpoint_lesson_id = None
        self._powerpoint_source_map = []
        self._powerpoint_state = {"active": False, "slide": 0, "total": 0, "message": ""}
        self._readiness = {"checks": [], "text_ready": False, "total": 0, "approved": 0}
        self.teaching = TeachingBridge(self)
        self.classroom = ClassroomBridge(self)
        self.classroom.changed.connect(self.mascotStateChanged)
        self.changed.connect(self.mascotStateChanged)
        try:
            self._voices = speech.list_voices()
        except Exception:
            self._voices = []  # text editing remains usable without SAPI

    @Property("QVariantList", notify=changed)
    def lessons(self):
        return self.library.list_lessons()

    @Property("QVariantMap", notify=changed)
    def lesson(self):
        return self._lesson

    @Property("QVariantMap", notify=inputAssessmentChanged)
    def inputAssessment(self):
        if not self._input_result:
            return {}
        return {key: value for key, value in self._input_result["profile"].items() if key != "units"}

    @Property("QVariantList", notify=changed)
    def conversionReport(self):
        return self._conversion_report

    @Property("QVariantMap", notify=changed)
    def comparison(self):
        return self._comparison

    @Slot(int)
    def comparePowerPoint(self, output_slide):
        from .powerpoint_review import render_pair
        from .source_deck import prepare_source_deck

        if not self._lesson or self._busy:
            return
        lesson, directory = self._lesson, self.library.directory
        terms = self.library.glossary(lesson.get("subject", ""))

        def render():
            converted = prepare_source_deck(lesson, directory, terms)
            return render_pair(verified_presentation(lesson, directory), converted, output_slide, directory)

        def opened(result):
            if lesson["id"] != self._lesson.get("id") or lesson["revision"] != self._lesson.get("revision"):
                return
            result["source_image"] = QUrl.fromLocalFile(result["source_image"]).toString()
            result["result_image"] = QUrl.fromLocalFile(result["result_image"]).toString()
            self._comparison = result
            self._conversion_report = result["report"]
            self.changed.emit()
            self.comparisonReady.emit()
            self.inform("Đã đối chiếu bằng PowerPoint. Kiểm tra chữ và hiệu ứng trước khi dạy.")

        self.launch(render, opened)

    @Slot()
    def clearInputAssessment(self):
        self._input_path = ""
        self._input_result = None
        self.inputAssessmentChanged.emit()

    @Slot(str, str)
    def assessInput(self, file_url, language):
        if self._busy:
            return
        import hashlib

        path = Path(QUrl(file_url).toLocalFile())
        self.clearInputAssessment()
        self._input_path = str(path)

        def analyze():
            if not path.is_file() or path.stat().st_size > 50 * 1024**2:
                raise ValueError("Không đọc được tệp hoặc tệp vượt 50 MB.")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            result = analyze_document(path, language, self.cancel_event)
            if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError("Tệp vừa thay đổi trong lúc đánh giá. Hãy chọn lại.")
            result.update(sha256=digest, ocr_language=language)
            return result

        def finished(result):
            if self._input_path == str(path):
                self._input_result = result
                self.inputAssessmentChanged.emit()
                self.inform("Đã đánh giá đầu vào: " + result["profile"]["label"] + ". Các cặp nhận diện vẫn cần thầy cô duyệt.")

        self.launch(analyze, finished)

    @Property("QVariantMap", notify=changed)
    def segment(self):
        segments = self._lesson.get("segments", [])
        return segments[self._segment_index] if segments else {}

    @Property(int, notify=changed)
    def segmentIndex(self):
        return self._segment_index

    @Property("QVariantMap", notify=changed)
    def policy(self):
        return asdict(LevelPolicy.for_level(self._lesson.get("level", 2)))

    @Slot(bool, result="QVariantMap")
    def presentationContent(self, rescue):
        from .presentation_policy import presentation_content
        return presentation_content(self.segment, self._lesson.get("level", 2), self._lesson.get("layout", "line_pair"), rescue, self.lessonTerms)

    @Property("QVariantList", constant=True)
    def slideTypes(self):
        return [{"id": item["id"], "label": item["label"]} for item in catalog()["blocks"]]

    @Property("QVariantList", constant=True)
    def templatePresets(self):
        return catalog()["presets"]

    @Property(str, notify=changed)
    def currentSlideType(self):
        return block_type(self.segment.get("kind", "unknown"))["id"]

    @Slot(str, str, int, str, result="QVariantMap")
    def templateExample(self, preset, kind, level, layout):
        return example_plan(preset, kind, level, layout)

    @Slot(str)
    def openTemplateSample(self, preset):
        if preset not in {item["id"] for item in catalog()["presets"]}:
            return
        path = RESOURCE_ROOT / "assets/templates" / (preset + "-classroom.pptx")
        if path.is_file():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
        else:
            self.inform("Chưa có file PowerPoint mẫu trên máy này.", True)

    @Slot(bool, result="QVariantList")
    def templatePages(self, rescue):
        image = None
        try:
            image = source_image(self._lesson, self.library.directory, self.segment)
            return slide_pages(self._lesson, self.segment, terms=self.lessonTerms, rescue=rescue,
                               image=QUrl.fromLocalFile(str(image)).toString() if image else "")
        except ValueError as exc:
            plan = slide_plan(self._lesson, self.segment, terms=self.lessonTerms, rescue=rescue,
                              image=QUrl.fromLocalFile(str(image)).toString() if image else "")
            plan["overflow"] = True
            plan["error"] = str(exc)
            return [plan]

    @Slot(str)
    def setSlideType(self, kind):
        if not self._lesson:
            return
        try:
            self._lesson = self.library.set_block_type(self._lesson["id"], self.segment["id"], kind)
            self.changed.emit()
            self.selectionChanged.emit()
            self.inform("Đã đổi loại slide. Kiểm tra bố cục và chuẩn bị lại bài.")
        except Exception as exc:
            self.inform(str(exc), True)

    @Property(str, notify=changed)
    def status(self):
        return lesson_status(self._lesson.get("segments", []))

    @Property(int, notify=changed)
    def approvedCount(self):
        return sum(bool(s["approved"]) for s in self._lesson.get("segments", []))

    @Property("QVariantList", notify=changed)
    def terms(self):
        return self.library.glossary()

    @Property("QVariantList", notify=changed)
    def lessonTerms(self):
        if not self._lesson:
            return []
        text = (self.segment.get("vi", "") + " " + self.segment.get("en", "")).casefold()
        return [term for term in self.library.glossary(self._lesson["subject"])
                if term["vi"].casefold() in text or term["en"].casefold() in text]

    @Property("QVariantList", notify=changed)
    def knowledgeSources(self):
        return self.library.knowledge_sources()

    @Property("QVariantMap", notify=changed)
    def knowledgeStats(self):
        return self.library.knowledge_stats()

    @Slot(str, str, str, result="QVariantList")
    def searchKnowledge(self, query="", subject="", grade=""):
        return self.library.knowledge_entries(query, subject, grade)

    @Slot(str)
    def promoteKnowledgeTerm(self, entry_id):
        try:
            entry = self.library.knowledge_entry(entry_id)
            if not entry:
                raise ValueError("Không tìm thấy mục kiến thức.")
            existing = [term for term in self.library.glossary(entry["subject"])
                        if term["vi"] == entry["vi"]]
            if existing:
                raise ValueError("Thuật ngữ này đã có trong kho riêng. Mở Thuật ngữ để xem hoặc sửa bản đã lưu.")
            self.library.save_term(entry["subject"], entry["vi"], entry["en"], True)
            self.inform("Đã đưa thuật ngữ vào kho riêng của môn này.")
        except Exception as exc:
            self.inform(str(exc), True)

    @Property(QObject, constant=True)
    def teachingContext(self):
        return self.teaching

    @Property("QVariantList", notify=changed)
    def reviewWarnings(self):
        return review_warnings(self.segment.get("vi", ""), self.segment.get("en", ""))

    @Property(QObject, constant=True)
    def classroomContext(self):
        return self.classroom

    @Property("QVariantList", notify=changed)
    def memoryChoices(self):
        return self._memory_choices

    @Property(bool, notify=changed)
    def powerpointAvailable(self):
        source = self._lesson.get("source") or {}
        return bool(source.get("file", "").lower().endswith(".pptx"))

    @Property("QVariantMap", notify=changed)
    def powerpointState(self):
        return self._powerpoint_state

    @Property("QVariantList", notify=changed)
    def screens(self):
        return [{"name": f"Màn hình {index + 1} · {screen.name()}", "index": index}
                for index, screen in enumerate(QGuiApplication.screens())]

    @Slot(QObject, int)
    def showProjector(self, window, index):
        screens = QGuiApplication.screens()
        if not screens or window is None:
            return
        screen = screens[max(0, min(index, len(screens) - 1))]
        window.setScreen(screen)
        rect = screen.availableGeometry()
        window.setGeometry(rect.x() + 20, rect.y() + 20, max(800, rect.width() - 40), max(500, rect.height() - 40))
        if len(screens) > 1 and screen != QGuiApplication.primaryScreen():
            window.showFullScreen()
        else:
            window.showNormal()
            self.inform("Đang dùng một màn hình hoặc màn hình chính: mở cửa sổ lớp học để thầy cô tự bố trí.")

    @Property("QVariantList", notify=changed)
    def history(self):
        return self.library.history(self._lesson["id"]) if self._lesson else []

    @Property(bool, notify=changed)
    def reverseModelReady(self):
        return find_model("en") is not None

    @Property("QVariantList", notify=changed)
    def englishVoices(self):
        return [v for v in self._voices if v["language"] == "en"]

    @Property(bool, notify=changed)
    def kokoroReady(self):
        return speech.kokoro_ready()

    @Property(bool, notify=changed)
    def vieneuReady(self):
        return speech.vieneu_ready()

    @Property("QVariantList", notify=changed)
    def voicePairs(self):
        return [
            {"name": "Êm dịu · Bắc / Mỹ", "vi": "vieneu:Mai Anh", "en": "kokoro:af_heart"},
            {"name": "Tươi sáng · Nam / Mỹ", "vi": "vieneu:Thùy Dung", "en": "kokoro:af_bella"},
            {"name": "Mạch lạc · Bắc / Mỹ", "vi": "vieneu:Hải Đăng", "en": "kokoro:am_michael"},
            {"name": "Ấm áp · Nam / Anh", "vi": "vieneu:Thái Sơn", "en": "kokoro:bm_george"},
        ] if self.vieneuReady and self.kokoroReady else []

    @Property("QVariantList", notify=changed)
    def vietnameseVoices(self):
        return [v for v in self._voices if v["language"] == "vi"]

    @Property("QVariantMap", notify=changed)
    def voiceSettings(self):
        result = {"rate": self.library.setting("voice_rate", 0)}
        for language in ("en", "vi"):
            available = [v for v in self._voices if v["language"] == language]
            selected = self.library.setting("voice_" + language, "")
            ids = [v["id"] for v in available]
            result[language] = selected if selected in ids else ids[0] if ids else ""
            result[language + "_index"] = ids.index(result[language]) if ids else -1
        return result

    @Property("QVariantMap", notify=changed)
    def readiness(self):
        return self._readiness

    @Property("QVariantMap", notify=changed)
    def settings(self):
        return {
            "teacher": self.library.setting("teacher", "Thầy cô"),
            "school": self.library.setting("school", ""),
            "subjects": self.library.setting("teaching_subjects", []),
            "show_profile": self.library.setting("show_profile", True),
            "mascot": self.library.setting("mascot", "Milo"),
        }

    @Property(str, notify=changed)
    def schoolLogoUrl(self):
        path = self.library.directory / "assets" / "school-logo.png"
        return QUrl.fromLocalFile(str(path)).toString() + f"?v={self._logo_revision}" if path.is_file() else ""

    @Property("QVariantMap", notify=changed)
    def classroomSettings(self):
        return self.library.setting("classroom_options", {
            "mode": "anonymous", "capacity": 50, "duration": 60, "language": "both"
        })

    @Property(str, notify=mascotStateChanged)
    def mascotState(self):
        return "speaking" if self._speaking else "thinking" if self._busy else "celebrate" if self.classroom.state.get("status") == "ended" else "idle"

    @Property("QVariantMap", notify=changed)
    def mascotSettings(self):
        defaults = {
            "visible": True, "size": 110, "position": "right", "reduced_motion": False,
            "accessories": True, "show_explanation": True, "show_quiz": True,
        }
        saved = self.library.setting("mascot_options", {})
        return {**defaults, **saved} if isinstance(saved, dict) else defaults

    @Slot(QObject)
    def showCompanion(self, window):
        extent = int(window.property("mascotExtent"))
        saved = self.library.setting("mascot_location", {})
        screen = QGuiApplication.primaryScreen()
        if isinstance(saved, dict) and isinstance(saved.get("x"), int) and isinstance(saved.get("y"), int):
            candidate = QGuiApplication.screenAt(QPoint(saved["x"] + extent // 2, saved["y"] + extent // 2))
            if candidate is not None:
                screen = candidate
                anchor_x, anchor_y = saved["x"], saved["y"]
            else:
                saved = {}
        else:
            saved = {}
        area = screen.availableGeometry()
        if not saved:
            anchor_x = area.left() + 20 if self.mascotSettings["position"] == "left" else area.right() - extent - 19
            anchor_y = area.bottom() - extent - 19

        right_edge = area.left() + area.width()
        bottom_edge = area.top() + area.height()
        menu_on_left = self.mascotSettings["position"] == "right"
        if anchor_x + window.width() > right_edge:
            menu_on_left = True
        elif anchor_x - (window.width() - extent) < area.left():
            menu_on_left = False
        menu_above = anchor_y - (window.height() - extent) >= area.top()
        if not menu_above and anchor_y + window.height() > bottom_edge:
            menu_above = anchor_y - area.top() >= bottom_edge - (anchor_y + extent)
        window.setProperty("mascotAtRight", menu_on_left)
        window.setProperty("mascotAtBottom", menu_above)
        x = anchor_x - (window.width() - extent if menu_on_left else 0)
        y = anchor_y - (window.height() - extent if menu_above else 0)
        window.setX(max(area.left(), min(x, right_edge - window.width())))
        window.setY(max(area.top(), min(y, bottom_edge - window.height())))
        window.show()

    @Slot(int, int)
    def saveMascotLocation(self, x, y):
        self.library.set_setting("mascot_location", {"x": x, "y": y})

    @Slot()
    def resetMascotLocation(self):
        self.library.set_setting("mascot_location", {})

    @Slot()
    def requestClassroomProjection(self):
        self.projectClassroomRequested.emit()

    @Property(bool, notify=changed)
    def modelReady(self):
        return find_model() is not None

    @Property(bool, notify=changed)
    def busy(self):
        return self._busy

    @Property(str, notify=changed)
    def message(self):
        return self._message

    @Property(bool, notify=changed)
    def error(self):
        return self._error

    @Property(str, notify=changed)
    def dataPath(self):
        return str(self.library.directory)

    def inform(self, message, error=False):
        self._message, self._error = message, error
        if error:
            self.logger.warning("Operation reported an error")
        self.changed.emit()

    def _set_update_state(self, **changes):
        self._update_state = dict(self._update_state, **changes)
        self.updateChanged.emit()

    @Slot(int)
    def _on_update_progress(self, value):
        self._set_update_state(progress=value, message=f"Đang tải bản mới · {value}%")

    @Slot(bool)
    def checkForUpdates(self, silent=False):
        if self.developmentMode:
            if not silent:
                self.inform("Bản mã nguồn được cập nhật bằng Git; cập nhật tự động dành cho bản Windows đóng gói.")
            return
        if self.update_worker and self.update_worker.isRunning():
            return
        self._set_update_state(checking=True, message="Đang kiểm tra phiên bản…")
        self.update_worker = Job(check_for_update, self)

        def completed(result, error):
            if error:
                self._set_update_state(checking=False, message="Chưa kiểm tra được bản mới. Thử lại khi có mạng.")
                if not silent:
                    self.inform("Chưa kiểm tra được cập nhật: " + error, True)
            elif result:
                self._update_release = result
                self._set_update_state(checking=False, available=True, version=result["version"],
                                       message="Đã có BiliClass " + result["version"])
            else:
                self._update_release = None
                self._set_update_state(checking=False, available=False, message="Đang dùng bản mới nhất.")
                if not silent:
                    self.inform("BiliClass đang là bản mới nhất.")

        self.update_worker.completed.connect(completed)
        self.update_worker.finished.connect(self._update_job_finished)
        self.update_worker.start()

    @Slot()
    def _update_job_finished(self):
        self.update_worker = None

    @Slot()
    def downloadUpdate(self):
        if (not self._update_release or self._update_package or self._busy or self.classroom.running
                or (self.update_worker and self.update_worker.isRunning())):
            self.inform("Đóng lớp và hoàn tất tác vụ trước khi cập nhật.", True)
            return
        self._update_cancel.clear()
        self._set_update_state(downloading=True, progress=0, message="Đang tải bản mới…")
        self.update_worker = Job(lambda: download_and_stage(
            self._update_release, self.library.directory, self.updateProgress.emit, self._update_cancel), self)

        def completed(result, error):
            self._set_update_state(downloading=False)
            if error:
                self._set_update_state(message=error)
                self.inform(error, True)
                return
            self._update_package = result
            self._set_update_state(ready=True, progress=100, message="Đã tải và kiểm tra. Đang chuyển sang bản mới…")
            self.applyDownloadedUpdate()

        self.update_worker.completed.connect(completed)
        self.update_worker.finished.connect(self._update_job_finished)
        self.update_worker.start()

    @Slot()
    def cancelUpdate(self):
        self._update_cancel.set()
        self._set_update_state(message="Đang hủy tải bản cập nhật…")

    @Slot()
    def applyDownloadedUpdate(self):
        if not self._update_package or self._busy or self.classroom.running:
            self._set_update_state(message="Đóng lớp và hoàn tất tác vụ rồi bấm Cập nhật lần nữa.")
            return
        try:
            launch_install(self._update_package, os.getpid())
        except Exception as exc:
            self._set_update_state(message="Chưa cài được bản mới: " + str(exc))
            self.inform(str(exc), True)
            return
        self._update_applying = True
        self.updateChanged.emit()
        QTimer.singleShot(0, QGuiApplication.quit)

    def launch(self, action, callback):
        if self._busy:
            return
        self._busy = True
        self.cancel_event.clear()
        self.callback = callback
        self.worker = Job(action, self)
        self.worker.completed.connect(self.receiveResult)
        self.worker.finished.connect(self.finishJob)
        self.worker.start()
        self.inform("Đang xử lý tại máy…")

    @Slot(object, str)
    def receiveResult(self, result, error):
        self.job_result = (result, error)

    @Slot()
    def finishJob(self):
        self._busy = False
        result, error = self.job_result
        try:
            if self.cancel_event.is_set():
                if self.classroom.runtime and not self.classroom.joinUrl:
                    self.classroom.disconnect()
                self.inform(
                    "Đã dừng tác vụ. Kết quả mới chưa được áp dụng; âm thanh đã tạo có thể được dùng lại."
                )
            elif error:
                self.inform(error, True)
            else:
                self.callback(result)
        except Exception as exc:
            self.inform(str(exc), True)
        self.worker.deleteLater()
        self.worker = self.callback = self.job_result = None
        self.changed.emit()

    @Slot()
    def cancelJob(self):
        if self._busy:
            self.cancel_event.set()
            self.inform("Đang dừng sau bước xử lý hiện tại…")

    @Slot()
    def refreshReadiness(self):
        if not self._lesson:
            return
        try:
            self._readiness = assess(
                self._lesson,
                self.library.directory,
                self._voices,
                self.voiceSettings,
                self.voiceSettings["rate"],
            )
            self.changed.emit()
        except Exception as exc:
            self.inform(str(exc), True)

    @Slot()
    def prepareLesson(self):
        if not self._lesson or self._busy:
            return
        try:
            self._lesson = self.library.mark_prepared(self._lesson["id"], self._lesson["revision"])
            self.refreshReadiness()
            self.inform("Đã chốt bản chuẩn bị. Nếu sửa bài, hãy chốt lại trước khi mở lớp.")
        except Exception as exc:
            self.inform(str(exc), True)

    @Slot(str, int)
    def setVoice(self, language, index):
        voices = [v for v in self._voices if v["language"] == language]
        if language in ("vi", "en") and 0 <= index < len(voices):
            self.library.set_setting("voice_" + language, voices[index]["id"])
            self.inform("Đã chọn giọng đọc. Mascot vẫn giữ nguyên.")

    @Slot(int)
    def setVoicePair(self, index):
        pairs = self.voicePairs
        if not 0 <= index < len(pairs):
            return
        pair = pairs[index]
        ids = {voice["id"] for voice in self._voices}
        if pair["vi"] not in ids or pair["en"] not in ids:
            self.inform("Bộ giọng này chưa có đủ model trên máy.", True)
            return
        self.library.set_setting("voice_vi", pair["vi"])
        self.library.set_setting("voice_en", pair["en"])
        self.inform("Đã lưu cả giọng Việt và English cho bài giảng song ngữ.")

    @Slot(int)
    def setVoiceRate(self, rate):
        if -3 <= rate <= 3:
            self.library.set_setting("voice_rate", rate)
            self.inform("Đã lưu tốc độ giọng đọc.")

    @Slot(str)
    def previewVoice(self, sample):
        self._preview_voice(self.voiceSettings["en"], sample)

    @Slot(int, str)
    def previewVoiceChoice(self, index, sample):
        voices = self.englishVoices
        if 0 <= index < len(voices):
            self._preview_voice(voices[index]["id"], sample)

    @Slot(int, str)
    def previewVietnameseVoiceChoice(self, index, sample):
        voices = self.vietnameseVoices
        if 0 <= index < len(voices):
            self._preview_voice(voices[index]["id"], sample)

    @Slot(str)
    def previewVietnameseVoice(self, sample):
        self._preview_voice(self.voiceSettings["vi"], sample)

    def _preview_voice(self, voice, sample):
        if not voice:
            self.inform("Máy chưa có giọng đọc phù hợp để nghe thử.", True)
            return
        sample = sample.strip()
        if not sample or len(sample) > 250:
            self.inform("Câu nghe thử cần từ 1 đến 250 ký tự.", True)
            return
        self.stopSpeech()
        rate = self.voiceSettings["rate"]
        self.launch(
            lambda: speech.synthesize(sample, voice, rate, self.library.directory / "audio"),
            lambda result: (self._play_audio(result["path"]), self.inform("Đang nghe thử giọng đã chọn.")),
        )

    @Slot(str, str, result="QVariantList")
    def inspectPair(self, vi, en):
        return review_warnings(vi, en)

    @Property("QVariantMap", notify=changed)
    def audioAvailable(self):
        return {lang: bool(self.voiceSettings[lang] or available_audio(
            self.library.directory, self.segment.get(lang, ""), lang, "", 0)) for lang in ("vi", "en")}

    @Slot(str)
    def speakSegment(self, language):
        if self._busy or language not in ("vi", "en") or not self.segment:
            return
        voice = self.voiceSettings[language]
        text, rate = self.segment[language], self.voiceSettings["rate"]
        cached = available_audio(self.library.directory, text, language, voice, rate)
        if cached:
            speech.stop()
            self._play_audio(cached)
            self.inform("Đang phát âm thanh đã chuẩn bị đúng nội dung.")
            return
        if not voice:
            self.inform("Máy chưa có giọng đọc phù hợp. Nội dung dạng chữ vẫn sử dụng được.", True)
            return
        text, rate = self.segment[language], self.voiceSettings["rate"]
        speech.stop()

        def completed(result):
            self._play_audio(result["path"])
            self.inform("Đang phát âm thanh đã lưu trên máy. Dùng nút Dừng để ngừng phát.")

        self.launch(lambda: speech.synthesize(text, voice, rate, self.library.directory / "audio"), completed)

    def _play_audio(self, path):
        import wave
        with wave.open(str(path), "rb") as audio:
            duration = audio.getnframes() / audio.getframerate()
        speech.play(path)
        self._speaking = True
        self._speech_timer.start(int(duration * 1000) + 50)
        self.changed.emit()

    @Slot()
    def stopSpeech(self):
        speech.stop()
        self._speaking = False
        self._speech_timer.stop()
        self.changed.emit()

    @Slot(str)
    def prepareAudio(self, language):
        if language not in ("vi", "en") or not self._lesson:
            return
        voice, rate = self.voiceSettings[language], self.voiceSettings["rate"]
        if not voice:
            self.inform("Chọn giọng đọc trong Cài đặt trước khi chuẩn bị âm thanh.", True)
            return
        texts = [s[language] for s in self._lesson["segments"] if s["approved"] and s[language].strip()]
        if not texts:
            self.inform("Duyệt ít nhất một đoạn trước khi chuẩn bị âm thanh.", True)
            return

        def prepare():
            count = 0
            for text in texts:
                if self.cancel_event.is_set():
                    break
                speech.synthesize(text, voice, rate, self.library.directory / "audio")
                count += 1
            return count

        def completed(count):
            self.refreshReadiness()
            self.inform(f"Đã chuẩn bị âm thanh cho {count} đoạn đã duyệt. Chưa phát loa.")

        self.launch(prepare, completed)

    @Slot(str)
    def openLesson(self, lesson_id):
        try:
            self._conversion_report = []
            self._comparison = {}
            self.dismissMemoryChoices()
            if self._powerpoint_lesson_id and self._powerpoint_lesson_id != lesson_id:
                self.stopPowerPoint()
            self._lesson = self.library.get(lesson_id)
            self._segment_index = 0
            self.changed.emit()
            self.selectionChanged.emit()
            self.navigate.emit("editor")
        except Exception as exc:
            self.inform(str(exc), True)

    @Slot(str)
    def selectLessonForClass(self, lesson_id):
        try:
            self._lesson = self.library.get(lesson_id)
            self._segment_index = 0
            self.refreshReadiness()
            self.changed.emit()
            self.selectionChanged.emit()
            self.inform("Đã chọn bài cho lớp học. Kiểm tra trạng thái chuẩn bị trước khi mở lớp.")
        except Exception as exc:
            self.inform(str(exc), True)

    @Slot(int)
    def selectSegment(self, index):
        if 0 <= index < len(self._lesson.get("segments", [])):
            self.dismissMemoryChoices()
            self._segment_index = index
            self.changed.emit()
            self.selectionChanged.emit()

    @Slot()
    def startPowerPoint(self):
        if not self._lesson:
            return
        if self.powerpoint_worker is not None:
            self.inform("PowerPoint đang mở hoặc đang đóng. Hãy chờ hoàn tất.")
            return
        try:
            path = verified_presentation(self._lesson, self.library.directory)
            self._start_powerpoint_session(path)
            self.inform("Đang mở bản PowerPoint nguồn ở chế độ chỉ đọc…")
        except Exception as exc:
            self.inform(str(exc), True)

    def _start_powerpoint_session(self, path, source_map=None):
        initial = slide_for_locator(self.segment.get("locator", "")) or 1
        self._powerpoint_source_map = source_map or []
        if self._powerpoint_source_map:
            initial = self._powerpoint_source_map.index(initial) + 1
        worker = PowerPointSession(path, initial, self)
        self.powerpoint_worker = worker
        self._powerpoint_lesson_id = self._lesson["id"]
        worker.stateChanged.connect(self._powerpoint_changed)
        worker.failed.connect(self._powerpoint_failed)
        worker.finished.connect(self._powerpoint_finished)
        worker.start()

    @Slot()
    def startBilingualPowerPoint(self):
        from .source_deck import prepare_source_deck

        if not self._lesson or self._busy:
            return
        if self.powerpoint_worker is not None:
            self.inform("PowerPoint đang mở hoặc đang đóng. Hãy chờ hoàn tất.")
            return
        lesson, directory = self._lesson, self.library.directory
        terms = self.library.glossary(lesson.get("subject", ""))

        def opened(result):
            if self._lesson.get("id") != lesson["id"]:
                return
            self._conversion_report = result.get("report", [])
            self.changed.emit()
            self._start_powerpoint_session(result["path"], result["slide_map"])
            self.inform("Đang trình chiếu bản song ngữ, giữ thiết kế PowerPoint gốc…")

        self.launch(lambda: prepare_source_deck(lesson, directory, terms), opened)

    @Slot(object)
    def _powerpoint_changed(self, state):
        if self._powerpoint_lesson_id == self._lesson.get("id"):
            index = state.get("slide", 0)
            source_slide = self._powerpoint_source_map[index - 1] if 0 < index <= len(self._powerpoint_source_map) else index
            state = {**state, "source_slide": source_slide}
            previous = self._powerpoint_state.get("source_slide", self._powerpoint_state.get("slide"))
            self._powerpoint_state = state
            if state.get("active") and previous != source_slide:
                self.powerpointSlideChanged.emit(source_slide)
            self.changed.emit()

    @Slot(str)
    def _powerpoint_failed(self, error):
        self.inform(error, True)

    @Slot()
    def _powerpoint_finished(self):
        worker = self.powerpoint_worker
        if worker is not None:
            worker.deleteLater()
        self.powerpoint_worker = None
        self._powerpoint_lesson_id = None
        self._powerpoint_source_map = []
        self._powerpoint_state = {"active": False, "slide": 0, "total": 0, "message": ""}
        self.changed.emit()

    @Slot()
    def followPowerPoint(self):
        current = self._powerpoint_state.get("source_slide", self._powerpoint_state.get("slide"))
        for index, segment in enumerate(self._lesson.get("segments", [])):
            if slide_for_locator(segment.get("locator", "")) == current:
                self.stopSpeech()
                self.selectSegment(index)
                return
        self.inform("Slide này chưa có đoạn văn bản được nhập. Thầy cô chọn nội dung thủ công.")

    @Slot(str)
    def navigatePowerPoint(self, command):
        if not self.powerpoint_worker or not self._powerpoint_state["active"]:
            self.inform("Chưa có trình chiếu PowerPoint đang hoạt động.", True)
            return
        if command == "goto":
            slide = slide_for_locator(self.segment.get("locator", ""))
            if slide is None:
                self.inform("Đoạn này không liên kết với slide trong nguồn PowerPoint.", True)
                return
            if self._powerpoint_source_map:
                slide = self._powerpoint_source_map.index(slide) + 1
            self.powerpoint_worker.navigate("goto", slide)
        elif command in ("next", "previous"):
            self.powerpoint_worker.navigate(command)

    @Slot()
    def stopPowerPoint(self):
        if self.powerpoint_worker:
            self.powerpoint_worker.stop()
            self._powerpoint_state = {**self._powerpoint_state, "message": "Đang đóng PowerPoint…"}
            self.changed.emit()

    @Slot(str, str, str, str, str, str, str, int, str, str, str, str)
    def createLesson(self, title, subject, education, grade, text, file_url, source_language, level, layout, preset, style="", mode="level"):
        if not title.strip() or not subject.strip():
            self.inform("Nhập tên bài học và môn học.", True)
            return
        if bool(text.strip()) == bool(file_url):
            self.inform("Chọn một nguồn: tệp tài liệu hoặc nội dung dán vào.", True)
            return
        if (level not in range(5) or layout not in {"keyword_overlay", "line_pair", "split_view", "english_rescue", "level_auto"}
                or preset not in {"standard", "visual", "practice"} or style not in {"", "source", "template"}
                or mode not in {"level", "preserve", "paired"} or source_language not in {"vi", "en"}):
            self.inform("Chọn L0–L4 và một kiểu trình bày hợp lệ.", True)
            return
        path = Path(QUrl(file_url).toLocalFile()) if file_url else None
        cached = self._input_result if path and self._input_path == str(path) else None

        def prepare():
            source = self.library.store_source(path) if path else None  # file I/O only
            if path:
                result = cached if cached and cached["sha256"] == source["sha256"] and cached["ocr_language"] == source_language else analyze_document(
                    self.library.directory / "sources" / source["file"], source_language, self.cancel_event)
            else:
                blocks = [(f"Đoạn {i + 1}", p.strip()) for i, p in enumerate(text.split("\n\n")) if p.strip()]
                result = {"blocks": blocks, "profile": assess_blocks(blocks, "text", source_language)}
            if source:
                source["warnings"] = result["profile"]["warnings"]
            return result, source

        def created(result):
            result, source = result
            profile = result["profile"]
            lesson = self.library.create(title, subject, education, grade, result["blocks"], source, profile["primary_language"], profile)
            self.library.set_presentation(lesson["id"], level, layout)
            self.library.set_teaching_preset(lesson["id"], preset)
            if style:
                lesson = self.library.set_presentation_style(lesson["id"], style)
            if lesson["presentation_style"] == "source":
                self.library.set_conversion_mode(lesson["id"], mode)
            self.openLesson(lesson["id"])
            self.inform("Đã tạo bài học. Kiểm tra văn bản nguồn trước khi dịch và duyệt.")

        self.launch(prepare, created)

    @Slot(str)
    def setTeachingPreset(self, preset):
        if not self._lesson:
            return
        try:
            self._lesson = self.library.set_teaching_preset(self._lesson["id"], preset)
            self.selectionChanged.emit()
            self.inform("Đã lưu kiểu dạy cho bài này.")
        except Exception as exc:
            self.inform(str(exc), True)

    @Slot(str)
    def setPresentationStyle(self, style):
        if not self._lesson:
            return
        try:
            self._lesson = self.library.set_presentation_style(self._lesson["id"], style)
            self.changed.emit()
            self.selectionChanged.emit()
            self.inform("Đã chọn giữ thiết kế PowerPoint gốc." if style == "source" else "Đã chọn bố cục của BiliClass.")
        except Exception as exc:
            self.inform(str(exc), True)

    @Slot(str)
    def setConversionMode(self, mode):
        if not self._lesson:
            return
        try:
            self._lesson = self.library.set_conversion_mode(self._lesson["id"], mode)
            self._conversion_report = []
            self._comparison = {}
            self.changed.emit()
            self.inform("Đã đổi cách chuyển đổi. Kiểm tra bản song ngữ trước khi dạy.")
        except Exception as exc:
            self.inform(str(exc), True)

    @Slot()
    def previewSourcePowerPoint(self):
        from .source_deck import prepare_source_deck

        if not self._lesson or self._busy:
            return
        lesson, directory = self._lesson, self.library.directory
        terms = self.library.glossary(lesson.get("subject", ""))

        def opened(result):
            self._conversion_report = result.get("report", [])
            self.changed.emit()
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(result["path"])):
                self.inform("Đã tạo bản song ngữ nhưng máy chưa có ứng dụng mở PowerPoint: " + result["path"], True)
            else:
                self.inform("Đã mở bản song ngữ cùng thiết kế gốc. Bản gốc được giữ riêng trong thư viện.")

        self.launch(lambda: prepare_source_deck(lesson, directory, terms), opened)

    @Slot(str, str, bool, bool, result=bool)
    def saveSegment(self, vi, en, approve, locked):
        try:
            self._lesson = self.library.edit_segment(
                self._lesson["id"], self.segment["id"], vi, en, approve, locked
            )
            self.inform("Đã duyệt và lưu đoạn này." if approve else "Đã lưu bản nháp.")
            self.selectionChanged.emit()
            return True
        except Exception as exc:
            self.inform(str(exc), True)
            return False

    @Slot(str, str, bool, result=bool)
    def autoSave(self, vi, en, locked):
        if self._busy or not self._lesson:
            return False
        try:
            self._lesson = self.library.edit_segment(
                self._lesson["id"], self.segment["id"], vi, en, False, locked
            )
            self.inform("Đã tự lưu bản nháp. Nội dung vừa sửa cần duyệt lại.")
            return True  # do not reset editor text, selection or caret
        except Exception as exc:
            self.inform("Chưa tự lưu: " + str(exc), True)
            return False

    @Slot(int)
    def restoreRevision(self, revision):
        try:
            self._lesson = self.library.restore_revision(self._lesson["id"], revision)
            self._segment_index = 0
            self.changed.emit()
            self.selectionChanged.emit()
            self.inform("Đã khôi phục thành phiên bản mới. Kiểm tra và duyệt lại nội dung.")
        except Exception as exc:
            self.inform(str(exc), True)

    @Slot(int, int)
    def splitSegment(self, vi_position, en_position):
        try:
            # QML cursor positions count UTF-16 code units; Python slices Unicode codepoints.
            def codepoint_offset(text, position):
                raw = text.encode("utf-16-le")
                try:
                    return len(raw[: position * 2].decode("utf-16-le"))
                except UnicodeDecodeError:
                    raise ValueError("Không thể tách giữa một ký tự; hãy dời con trỏ.") from None

            vi = codepoint_offset(self.segment["vi"], vi_position)
            en = codepoint_offset(self.segment["en"], en_position)
            self._lesson = self.library.split_segment(self._lesson["id"], self.segment["id"], vi, en)
            self.changed.emit()
            self.selectionChanged.emit()
            self.inform("Đã tách thành hai đoạn. Bản trích xuất gốc vẫn được giữ.")
        except Exception as exc:
            self.inform(str(exc), True)

    @Slot(str)
    def suggestSimilar(self, source_language):
        if self._busy or not self._lesson or self.segment.get("locked") or source_language not in ("vi", "en"):
            return
        self.dismissMemoryChoices()
        self._memory_request = (self._lesson["id"], self.segment["id"], self._lesson["revision"], source_language, self.segment[source_language])
        self._memory_choices = self.library.similar_translations(self._lesson["subject"], self.segment[source_language], source_language, (self._lesson["id"], self.segment["id"]))
        self.changed.emit()
        if self._memory_choices:
            self.memoryChoicesAvailable.emit()
        else:
            self.inform("Chưa tìm thấy đoạn gần giống đã duyệt trong cùng môn.")

    @Slot(str)
    def translate(self, source_language):
        if not self._lesson or self.segment.get("locked"):
            self.inform("Bỏ khóa đoạn trước khi tạo lại bản dịch.", True)
            return
        lesson_id, segment_id = self._lesson["id"], self.segment["id"]
        if source_language not in ("vi", "en"):
            return
        revision, source_text = self._lesson["revision"], self.segment[source_language]
        term = self.library.exact_translation(
            self._lesson["subject"], source_text, source_language=source_language
        )
        request = (lesson_id, segment_id, revision, source_language, source_text)
        self.dismissMemoryChoices()
        if term:
            self._apply_translation(request, term, "Đã tạo bản nháp từ thuật ngữ đã lưu. Cần duyệt lại.")
            return
        choices = self.library.approved_translations(
            self._lesson["subject"], source_text, source_language, exclude=(lesson_id, segment_id)
        )
        if len(choices) == 1:
            self._apply_translation(
                request, choices[0]["text"], "Đã dùng lại bản dịch thầy cô từng duyệt trong cùng môn. Cần duyệt lại."
            )
        elif choices:
            self._memory_request = request
            self._memory_choices = choices
            self.changed.emit()
            self.memoryChoicesAvailable.emit()
            self.inform("Có nhiều bản đã duyệt cho cùng đoạn. Hãy chọn cách diễn đạt phù hợp.")
        else:
            knowledge = self.library.knowledge_translation(self._lesson["subject"], source_text, source_language)
            if knowledge:
                tier = "dữ liệu online có nguồn" if knowledge["tier"] == "online" else "kiến thức nền có nguồn"
                self._apply_translation(request, knowledge["text"], f"Đã dùng {tier}; cần duyệt lại.")
            else:
                self._translate_with_model(request)

    @Slot()
    def translateMissing(self):
        from .bulk_translation import plan_batch, translate_batch

        if self._busy or not self._lesson:
            return
        lesson = self._lesson
        plans = plan_batch(self.library, lesson)
        if not plans:
            self.inform("Không còn phần ngôn ngữ trống chưa khóa. Kiểm tra và duyệt các cặp đang có.")
            return
        terms = self.library.glossary(lesson["subject"])
        teacher_words = {term["vi"] for term in terms}
        terms += [term for term in self.library.knowledge_terms(lesson["subject"]) if term["vi"] not in teacher_words]

        def done(result):
            updated = self.library.apply_batch_translations(lesson["id"], result["drafts"], lesson["revision"])
            if self._lesson.get("id") == lesson["id"]:
                self._lesson = updated
                self.selectionChanged.emit()
            message = f"Đã tạo {len(result['drafts'])} bản nháp cho phần còn thiếu; cần kiểm tra và duyệt. Mỗi lượt xử lý tối đa 50 đoạn."
            if result["warnings"]:
                message += "\n" + "\n".join(result["warnings"][:3])
                if len(result["warnings"]) > 3:
                    message += f"\nCòn {len(result['warnings']) - 3} đoạn cần xử lý riêng."
            self.inform(message)

        self.launch(lambda: translate_batch(plans, terms, self.cancel_event), done)

    def _apply_translation(self, request, translated, message):
        lesson_id, segment_id, revision, source_language, _ = request
        try:
            lesson = self.library.apply_translation(
                lesson_id, segment_id, translated, revision, source_language
            )
            if self._lesson.get("id") == lesson_id:
                self._lesson = lesson
                self.selectionChanged.emit()
            self.inform(message)
        except Exception as exc:
            self.inform(str(exc), True)

    def _translate_with_model(self, request):
        _, _, _, source_language, source_text = request
        terms = self.library.glossary(self._lesson["subject"])
        teacher_words = {term[source_language] for term in terms}
        terms += [term for term in self.library.knowledge_terms(self._lesson["subject"])
                  if term[source_language] not in teacher_words]
        self.launch(
            lambda: translate_draft(source_text, source_language, terms),
            lambda translated: self._apply_translation(
                request,
                translated,
                "Bản dịch máy là bản nháp. Kiểm tra thuật ngữ, số liệu và ý nghĩa trước khi duyệt.",
            ),
        )

    @Slot(int)
    def useMemoryChoice(self, index):
        request = self._memory_request
        choices = self._memory_choices
        self.dismissMemoryChoices()
        self.closeMemoryChoicesRequested.emit()
        if request is None or not 0 <= index < len(choices):
            return
        lesson_id, segment_id, revision, source_language, source_text = request
        if (
            self._lesson.get("id") != lesson_id
            or self.segment.get("id") != segment_id
            or self._lesson.get("revision") != revision
            or self.segment.get(source_language) != source_text
        ):
            self.inform("Đoạn đã thay đổi. Hãy yêu cầu gợi ý lại.", True)
            return
        self._apply_translation(
            request, choices[index]["text"], "Đã dùng bản thầy cô chọn làm bản nháp. Cần duyệt lại."
        )

    @Slot()
    def translateMemoryWithModel(self):
        request = self._memory_request
        self.dismissMemoryChoices()
        self.closeMemoryChoicesRequested.emit()
        if request is None:
            return
        lesson_id, segment_id, revision, source_language, source_text = request
        if (
            self._lesson.get("id") != lesson_id
            or self.segment.get("id") != segment_id
            or self._lesson.get("revision") != revision
            or self.segment.get(source_language) != source_text
        ):
            self.inform("Đoạn đã thay đổi. Hãy yêu cầu dịch lại.", True)
            return
        self._translate_with_model(request)

    @Slot()
    def dismissMemoryChoices(self):
        self._memory_request = None
        self._memory_choices = []
        self.changed.emit()

    @Slot()
    def closeMemoryChoices(self):
        self.dismissMemoryChoices()
        self.closeMemoryChoicesRequested.emit()

    @Slot(int, str)
    def setPresentation(self, level, layout):
        try:
            self._conversion_report = []
            self._comparison = {}
            self._lesson = self.library.set_presentation(self._lesson["id"], level, layout)
            self.changed.emit()
        except Exception as exc:
            self.inform(str(exc), True)

    @Slot(str, str, str, bool)
    def saveTerm(self, subject, vi, en, locked):
        try:
            self.library.save_term(subject, vi, en, locked)
            self.inform("Đã lưu thuật ngữ riêng cho môn này.")
        except Exception as exc:
            self.inform(str(exc), True)

    @Slot(str)
    def deleteTerm(self, term_id):
        self.library.delete_term(term_id)
        self.inform("Đã xóa thuật ngữ.")

    @Slot(str)
    def installKnowledgePack(self, url):
        try:
            pack = load_pack(QUrl(url).toLocalFile())
            self.library.install_knowledge_pack(pack)
            manifest = pack["manifest"]
            self.inform(f"Đã cập nhật kho kiến thức: {manifest['title']} · v{manifest['version']}")
        except Exception as exc:
            self.inform(str(exc), True)

    @Slot(str, str, str, bool)
    def saveTeacherProfile(self, teacher, school, subjects_text, show_profile):
        values = {"teacher": teacher.strip() or "Thầy cô", "school": school.strip()}
        if any(len(value) > 100 for value in values.values()):
            self.inform("Mỗi thông tin hồ sơ tối đa 100 ký tự.", True)
            return
        subjects = list(dict.fromkeys(item.strip() for item in subjects_text.replace(";", ",").split(",") if item.strip()))
        if len(subjects) > 20 or any(len(item) > 100 for item in subjects):
            self.inform("Tối đa 20 bộ môn, mỗi tên tối đa 100 ký tự.", True)
            return
        for key, value in values.items():
            self.library.set_setting(key, value)
        self.library.set_setting("teaching_subjects", subjects)
        self.library.set_setting("show_profile", show_profile)
        self.inform("Đã lưu hồ sơ giáo viên và cách hiển thị trên bài giảng.")

    @Slot(str)
    def saveSchoolLogo(self, url):
        from PIL import Image, ImageOps
        try:
            source = Path(QUrl(url).toLocalFile())
            if source.suffix.lower() not in {".png", ".jpg", ".jpeg"} or source.stat().st_size > 5 * 1024 * 1024:
                raise ValueError("Chỉ nhận PNG/JPG tối đa 5 MB.")
            folder = self.library.directory / "assets"
            folder.mkdir(exist_ok=True)
            with Image.open(source) as opened:
                if opened.width > 4096 or opened.height > 4096:
                    raise ValueError("Logo tối đa 4096 × 4096 pixel.")
                logo = ImageOps.exif_transpose(opened).convert("RGBA")
                logo.thumbnail((900, 900))
                with tempfile.NamedTemporaryFile(dir=folder, suffix=".png", delete=False) as handle:
                    pending = Path(handle.name)
                try:
                    logo.save(pending, format="PNG", optimize=True)
                    os.replace(pending, folder / "school-logo.png")
                finally:
                    pending.unlink(missing_ok=True)
            self._logo_revision += 1
            self.changed.emit()
            self.inform("Đã lưu logo trường. Logo sẽ hiện trong bài giảng khi bật hồ sơ.")
        except Exception as exc:
            self.inform("Không thể tải logo: " + str(exc), True)

    @Slot()
    def removeSchoolLogo(self):
        (self.library.directory / "assets" / "school-logo.png").unlink(missing_ok=True)
        self._logo_revision += 1
        self.changed.emit()
        self.inform("Đã bỏ logo trường.")

    @Slot(str, bool, int, str, bool, bool, bool, bool)
    def saveMascotPreferences(self, mascot, visible, size, position, reduced_motion, accessories, show_explanation, show_quiz):
        if mascot not in ("Milo", "Lumi"):
            self.inform("Mascot không hợp lệ.", True)
            return
        if position in ("left", "right") and position != self.mascotSettings["position"]:
            self.resetMascotLocation()
        self.library.set_setting("mascot", mascot)
        self.library.set_setting("mascot_options", {
            "visible": visible, "size": max(60, min(160, size)),
            "position": position if position in ("left", "right") else "right",
            "reduced_motion": reduced_motion, "accessories": accessories,
            "show_explanation": show_explanation, "show_quiz": show_quiz,
        })
        self.mascotPreferencesSaved.emit(visible)
        self.inform("Đã lưu mascot và cách hiển thị.")

    @Slot(str, int, int, str)
    def saveClassroomSettings(self, mode, capacity, duration, language):
        if mode not in ("anonymous", "seat") or not 1 <= capacity <= 200 or not 5 <= duration <= 3600 or language not in ("both", "vi", "en"):
            self.inform("Cấu hình lớp học không hợp lệ.", True)
            return
        self.library.set_setting("classroom_options", {
            "mode": mode, "capacity": capacity, "duration": duration, "language": language
        })
        self.inform("Đã lưu giá trị mặc định cho lớp học mới.")

    @Slot(str, str, str, str, result=bool)
    def updateMetadata(self, title, subject, education, grade):
        try:
            self._lesson = self.library.update_metadata(self._lesson["id"], title, subject, education, grade)
            self.selectionChanged.emit()
            self.inform("Đã cập nhật thông tin bài. Đổi môn yêu cầu duyệt lại văn bản.")
            return True
        except Exception as exc:
            self.inform(str(exc), True)
            return False

    @Slot()
    def backupLibrary(self):
        self.launch(lambda: backup_library(self.library.directory),
                    lambda path: self.inform("Đã sao lưu thư viện: " + str(path)))

    @Slot(str)
    def restoreLibrary(self, file_url):
        from datetime import datetime
        path = QUrl(file_url).toLocalFile()
        destination = self.library.directory / "recovered" / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        self.launch(lambda: restore_backup(path, destination),
                    lambda output: self.inform(
                        "Đã khôi phục vào " + str(output) + ". Chọn thư mục này qua nút Mở thư viện."
                    ))

    @Slot(str)
    def openLibrary(self, folder_url):
        if self._busy or self.powerpoint_worker or self.classroom.running:
            self.inform("Kết thúc tác vụ và trình chiếu trước khi đổi thư viện.", True)
            return
        try:
            directory = Path(QUrl(folder_url).toLocalFile())
            if not (directory / "library.db").is_file():
                raise ValueError("Thư mục này chưa có thư viện BiliClass.")
            replacement = Library(directory)
            self.library.close()
            self.library = replacement
            try:
                ensure_builtin_foundation(self.library)
            except Exception as exc:
                self.logger.warning("Could not install bundled knowledge foundation: %s", exc)
            self._lesson = {}
            self._segment_index = 0
            self.dismissMemoryChoices()
            self.classroom.refreshReports()
            self.selectionChanged.emit()
            self.navigate.emit("home")
            self.inform("Đã mở thư viện: " + str(directory))
        except Exception as exc:
            self.inform(str(exc), True)

    @Slot(str)
    def exportPowerPoint(self, url):
        from .deck_export import export_deck
        lesson, directory = self._lesson, self.library.directory
        profile = self.settings
        terms = self.library.glossary(lesson.get("subject", ""))
        self.launch(lambda: export_deck(lesson, directory, QUrl(url).toLocalFile(), profile, terms),
                    lambda path: self.inform("Đã xuất PowerPoint song ngữ mới: " + str(path)))

    @Property(str, constant=True)
    def ocrStatus(self):
        from .local_ocr import model_paths
        from .ocr import languages
        available = languages()
        local = " · OCR Việt–Anh cục bộ sẵn sàng" if model_paths() else " · Chưa có OCR Việt–Anh cục bộ"
        return "OCR Windows: " + (", ".join(available) if available else "chưa có gói nhận dạng") + local

    @Property(bool, notify=changed)
    def localOCRAvailable(self):
        from .local_ocr import model_paths
        return bool(model_paths())

    @Slot()
    def prepareLocalOCR(self):
        from .local_ocr import prepare_models

        def ready(_):
            self.changed.emit()
            self.inform("Đã chuẩn bị OCR Việt–Anh. Chọn lại ảnh/PDF scan để nhận dạng; dữ liệu chạy trên máy.")

        self.launch(prepare_models, ready)

    @Slot(str)
    def exportPack(self, url):
        try:
            destination = export_pack(self.library, self._lesson["id"], QUrl(url).toLocalFile())
            self.inform("Đã xuất gói bài: " + str(destination))
        except Exception as exc:
            self.inform(str(exc), True)

    @Slot(str)
    def importPack(self, url):
        try:
            lesson = import_pack(self.library, QUrl(url).toLocalFile())
            self.openLesson(lesson["id"])
            self.inform("Đã nhập thành bản sao. Hãy duyệt nội dung trước khi dùng trên lớp.")
        except Exception as exc:
            self.inform("Chưa nhập được gói: " + str(exc), True)

    @Slot(str)
    def installModel(self, url):
        from .model_packs import install_model_pack
        self.launch(lambda: install_model_pack(QUrl(url).toLocalFile(), user_data() / "models"),
                    lambda path: self.inform("Đã cài gói ngôn ngữ: " + path.name))

    @Slot()
    def openData(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.library.directory)))

    @Slot()
    def openSourceCopy(self):
        import hashlib
        import shutil
        import stat
        import tempfile
        from uuid import uuid4
        source = self._lesson.get("source")
        if not source:
            self.inform("Bài này được tạo từ nội dung dán vào.")
            return
        try:
            path = self.library.directory / "sources" / source["file"]
            if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
                raise ValueError("Nguồn đã thay đổi; không mở bản không khớp checksum.")
            folder = Path(tempfile.gettempdir()) / "BiliClassPreview"
            folder.mkdir(exist_ok=True)
            copy = folder / (str(uuid4()) + path.suffix)
            shutil.copy2(path, copy)
            copy.chmod(stat.S_IREAD)
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(copy)))
            self.inform("Đã mở bản sao chỉ đọc để đối chiếu nguồn.")
        except Exception as exc:
            self.inform(str(exc), True)


def run(args):
    app = QGuiApplication([])
    app.setApplicationName("BiliClass")
    app.setOrganizationName("BiliClass")
    QQuickStyle.setStyle("Basic")
    for font in (RESOURCES / "assets").glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(font))
    app.setFont(QFont("Be Vietnam Pro", 10))
    library = Library(user_data())
    if args.seed_demo and not library.list_lessons():
        lesson = library.create(
            "Thảo luận và lập luận",
            "Liên môn",
            "THPT",
            "10",
            [
                ("Hoạt động mở đầu", "Hãy thảo luận theo nhóm và trình bày ý kiến của em."),
                ("Gợi ý thảo luận", "Em có thể đưa ra một ví dụ để giải thích ý kiến này không?"),
                ("Tổng kết", "So sánh các cách giải thích và nêu lý do cho lựa chọn của em."),
            ],
        )
        library.edit_segment(
            lesson["id"],
            lesson["segments"][0]["id"],
            lesson["segments"][0]["vi"],
            "Discuss in groups and share your ideas.",
            True,
        )
        library.save_term("Liên môn", "lập luận", "reasoning")
    bridge = Bridge(library)
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("bridge", bridge)
    warnings = []
    engine.warnings.connect(lambda values: warnings.extend(str(v) for v in values))
    engine.load(QUrl.fromLocalFile(str(RESOURCE_ROOT / "qml" / "Main.qml")))
    if not engine.rootObjects():
        print("\n".join(warnings))
        library.close()
        return 1
    window = engine.rootObjects()[0]
    width, height = (int(n) for n in args.size.split("x"))
    window.resize(width, height)
    if args.page == "editor" and library.list_lessons():
        bridge.openLesson(library.list_lessons()[0]["id"])
    window.setProperty("page", args.page)

    def capture():
        path = Path(args.screenshot or user_data() / "screenshot.png")
        path.parent.mkdir(parents=True, exist_ok=True)
        saved = QQuickWindow.grabWindow(window).save(str(path))
        path.with_suffix(".json").write_text(
            json.dumps(
                {
                    "screenshot": str(path),
                    "saved": saved,
                    "warnings": warnings,
                    "size": [width, height],
                    "page": args.page,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        app.exit(0 if saved and not warnings else 1)

    if args.smoke:
        QTimer.singleShot(2000, capture)
    backup_job = Job(lambda: backup_library(library.directory, daily=True), bridge)
    backup_job.completed.connect(lambda path, error: bridge.logger.warning("Automatic backup failed") if error else bridge.logger.info("Automatic backup finished"))
    if not args.smoke:
        QTimer.singleShot(1000, backup_job.start)
        QTimer.singleShot(4000, lambda: bridge.checkForUpdates(True))
    result = app.exec()
    if backup_job.isRunning():
        backup_job.wait()
    if bridge.update_worker and bridge.update_worker.isRunning():
        bridge._update_cancel.set()
        bridge.update_worker.wait()
    bridge.classroom.disconnect()
    if bridge.powerpoint_worker:
        bridge.stopPowerPoint()
        bridge.powerpoint_worker.wait()  # Helper supervisor has its own bounded shutdown.
    if bridge.worker:
        bridge.worker.wait()  # closing is disabled while jobs run; also safe on OS shutdown
    bridge.library.close()
    speech.stop()
    del engine
    return result
