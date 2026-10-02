"""Transactional local drafts. SQLite is owned by the UI/application thread."""

import copy
import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from .lesson_design import PRESETS, classify_block


class RevisionConflict(ValueError):
    pass


def now():
    return datetime.now(UTC).isoformat()


def lesson_status(segments):
    if not segments or not any(s.get("en", "").strip() and s.get("vi", "").strip() for s in segments):
        return "DRAFT"
    if all(s.get("approved") and s.get("en", "").strip() and s.get("vi", "").strip() for s in segments):
        return "READY_TO_TEACH"
    return "REVIEW_REQUIRED"


def memory_key(text):
    """Match whole segments despite document line wrapping, without changing case or punctuation."""
    return " ".join(text.split())


class Library:
    def __init__(self, directory: Path):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.directory / "library.db")
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA busy_timeout=5000")
        version = self.db.execute("PRAGMA user_version").fetchone()[0]
        if version > 3:
            self.db.close()
            raise ValueError("Thư viện được tạo bằng phiên bản mới hơn. Hãy cập nhật BiliClass.")
        if version == 1:
            snapshot = self.directory / "backups" / "before-schema-2.db"
            snapshot.parent.mkdir(exist_ok=True)
            if not snapshot.exists():
                with sqlite3.connect(snapshot) as backup:
                    self.db.backup(backup)
        if version == 2:
            snapshot = self.directory / "backups" / "before-schema-3.db"
            snapshot.parent.mkdir(exist_ok=True)
            if not snapshot.exists():
                with sqlite3.connect(snapshot) as backup:
                    self.db.backup(backup)
        with self.db:
            self.db.executescript("""
                CREATE TABLE IF NOT EXISTS lessons (
                  id TEXT PRIMARY KEY, title TEXT NOT NULL, subject TEXT NOT NULL,
                  education_level TEXT NOT NULL, grade TEXT NOT NULL,
                  revision INTEGER NOT NULL, content TEXT NOT NULL, updated_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS glossary (
                  id TEXT PRIMARY KEY, teacher_id TEXT NOT NULL, subject TEXT NOT NULL,
                  vi TEXT NOT NULL, en TEXT NOT NULL, locked INTEGER NOT NULL DEFAULT 1,
                  UNIQUE(teacher_id, subject, vi));
                CREATE TABLE IF NOT EXISTS lesson_revisions (
                  lesson_id TEXT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
                  revision INTEGER NOT NULL, content TEXT NOT NULL, saved_at TEXT NOT NULL,
                  PRIMARY KEY(lesson_id,revision));
                CREATE TABLE IF NOT EXISTS knowledge_sources (
                  id TEXT PRIMARY KEY, pack_id TEXT NOT NULL, pack_version TEXT NOT NULL,
                  title TEXT NOT NULL, publisher TEXT NOT NULL, document_no TEXT NOT NULL,
                  issued_at TEXT NOT NULL, effective_at TEXT NOT NULL, source_url TEXT NOT NULL,
                  official INTEGER NOT NULL DEFAULT 0, source_type TEXT NOT NULL,
                  retrieved_at TEXT NOT NULL, status TEXT NOT NULL, license TEXT NOT NULL,
                  notes TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS knowledge_entries (
                  id TEXT PRIMARY KEY, pack_id TEXT NOT NULL, pack_version TEXT NOT NULL,
                  subject TEXT NOT NULL, grade TEXT NOT NULL, kind TEXT NOT NULL,
                  vi TEXT NOT NULL, en TEXT NOT NULL, definition_vi TEXT NOT NULL,
                  definition_en TEXT NOT NULL, aliases_json TEXT NOT NULL,
                  source_ids_json TEXT NOT NULL, status TEXT NOT NULL,
                  confidence TEXT NOT NULL, updated_at TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS idx_knowledge_entries_subject
                  ON knowledge_entries(subject, grade, kind);
                CREATE INDEX IF NOT EXISTS idx_knowledge_entries_pack
                  ON knowledge_entries(pack_id, pack_version);
                PRAGMA user_version=3;
            """)

    def close(self):
        self.db.close()

    def list_lessons(self):
        from .readiness import preparation_current

        rows = self.db.execute("SELECT * FROM lessons ORDER BY updated_at DESC").fetchall()
        result = []
        for row in rows:
            lesson = json.loads(row["content"])
            result.append(
                {
                    **dict(row),
                    "content": None,
                    "segments_count": len(lesson["segments"]),
                    "approved_count": sum(bool(s["approved"]) for s in lesson["segments"]),
                    "status": lesson_status(lesson["segments"]),
                    "prepared": preparation_current(lesson),
                }
            )
        return result

    def get(self, lesson_id):
        row = self.db.execute("SELECT content FROM lessons WHERE id=?", (lesson_id,)).fetchone()
        if not row:
            raise ValueError("Không tìm thấy bài học.")
        lesson = json.loads(row[0])
        lesson.setdefault("source_language", "vi")
        for segment in lesson["segments"]:
            segment.setdefault("source_text", segment[lesson["source_language"]])
        return lesson

    def create(self, title, subject, education_level, grade, blocks, source=None, source_language="vi"):
        if source_language not in ("vi", "en"):
            raise ValueError("Ngôn ngữ nguồn phải là tiếng Việt hoặc tiếng Anh.")
        if not title.strip() or not subject.strip():
            raise ValueError("Nhập tên bài học và môn học.")
        segments = [
            {
                "id": str(uuid4()),
                "vi": text if source_language == "vi" else "",
                "en": text if source_language == "en" else "",
                "source_text": text,
                "approved": False,
                "locked": False,
                "locator": locator,
                "kind": classify_block(text),
            }
            for locator, text in blocks
            if text.strip()
        ]
        if not segments:
            raise ValueError("Chưa tìm thấy nội dung văn bản. Tài liệu ảnh cần OCR ở giai đoạn sau.")
        if any(len(s["source_text"]) > 100_000 for s in segments):
            raise ValueError("Một đoạn vượt 100.000 ký tự; hãy chia nhỏ nội dung nguồn.")
        if len(segments) > 10000 or sum(len(s["source_text"]) for s in segments) > 1_000_000:
            raise ValueError("Nội dung vượt giới hạn của bản thử.")
        lesson = {
            "id": str(uuid4()),
            "title": title.strip(),
            "subject": subject.strip(),
            "education_level": education_level.strip(),
            "grade": grade.strip(),
            "revision": 1,
            "segments": segments,
            "source": source,
            "source_language": source_language,
            "level": 2,
            "layout": "line_pair",
            "teaching_preset": "standard",
            "presentation_style": "source" if source and source.get("file", "").lower().endswith(".pptx") else "template",
            "updated_at": now(),
        }
        self._write(lesson, new=True)
        return lesson

    def _write(self, lesson, new=False):
        content = json.dumps(lesson, ensure_ascii=False)
        values = (
            lesson["title"],
            lesson["subject"],
            lesson["education_level"],
            lesson["grade"],
            lesson["revision"],
            content,
            lesson["updated_at"],
            lesson["id"],
        )
        with self.db:
            if new:
                self.db.execute(
                    "INSERT INTO lessons(title,subject,education_level,grade,revision,content,updated_at,id) VALUES(?,?,?,?,?,?,?,?)",
                    values,
                )
            else:
                current = self.db.execute(
                    "SELECT revision,content FROM lessons WHERE id=?", (lesson["id"],)
                ).fetchone()
                if current:
                    self.db.execute(
                        "INSERT OR IGNORE INTO lesson_revisions VALUES(?,?,?,?)",
                        (lesson["id"], current["revision"], current["content"], now()),
                    )
                    self.db.execute(
                        "DELETE FROM lesson_revisions WHERE lesson_id=? AND revision NOT IN (SELECT revision FROM lesson_revisions WHERE lesson_id=? ORDER BY revision DESC LIMIT 30)",
                        (lesson["id"], lesson["id"]),
                    )
                self.db.execute(
                    "UPDATE lessons SET title=?,subject=?,education_level=?,grade=?,revision=?,content=?,updated_at=? WHERE id=?",
                    values,
                )

    def edit_segment(self, lesson_id, segment_id, vi, en, approve=False, locked=False):
        lesson = self.get(lesson_id)
        source = vi if lesson["source_language"] == "vi" else en
        if not source.strip():
            raise ValueError("Nội dung nguồn không được để trống.")
        if len(vi) + len(en) > 100_000:
            raise ValueError("Đoạn quá dài; hãy chia nhỏ nội dung trước khi biên tập.")
        if approve and not (en.strip() and vi.strip()):
            raise ValueError("Cần cả tiếng Việt và tiếng Anh trước khi duyệt đoạn này.")
        segment = next((s for s in lesson["segments"] if s["id"] == segment_id), None)
        if segment is None:
            raise ValueError("Không tìm thấy đoạn cần sửa.")
        if (vi, en) != (segment["vi"], segment["en"]):
            for item in segment.get("support", []):
                item["approved"] = False
            for question in lesson.get("questions", []):
                if question.get("concept_id") == segment_id:
                    question["approved"] = False
        segment.update(vi=vi, en=en, approved=bool(approve), locked=bool(locked))
        lesson["revision"] += 1
        lesson["updated_at"] = now()
        self._write(lesson)
        return lesson

    def apply_translation(self, lesson_id, segment_id, text, expected_revision, source_language="vi"):
        lesson = self.get(lesson_id)
        if lesson["revision"] != expected_revision:
            raise RevisionConflict("Bài vừa được sửa. Bản dịch cũ chưa được áp dụng; hãy thử lại.")
        segment = next(s for s in lesson["segments"] if s["id"] == segment_id)
        if segment["locked"]:
            raise RevisionConflict("Đoạn đã khóa; bỏ khóa trước khi tạo bản dịch mới.")
        if source_language not in ("vi", "en"):
            raise ValueError("Hướng dịch không hợp lệ.")
        return self.edit_segment(
            lesson_id,
            segment_id,
            segment["vi"] if source_language == "vi" else text,
            text if source_language == "vi" else segment["en"],
            approve=False,
        )

    def history(self, lesson_id):
        return [
            dict(row)
            for row in self.db.execute(
                "SELECT revision,saved_at FROM lesson_revisions WHERE lesson_id=? ORDER BY revision DESC",
                (lesson_id,),
            ).fetchall()
        ]

    def restore_revision(self, lesson_id, revision):
        current = self.get(lesson_id)
        row = self.db.execute(
            "SELECT content FROM lesson_revisions WHERE lesson_id=? AND revision=?", (lesson_id, revision)
        ).fetchone()
        if not row:
            raise ValueError("Phiên bản này không còn trong lịch sử 30 bản gần nhất.")
        previous = json.loads(row[0])
        previous.update(revision=current["revision"] + 1, updated_at=now())
        for segment in previous["segments"]:
            segment["approved"] = False
            for item in segment.get("support", []):
                item["approved"] = False
        for question in previous.get("questions", []):
            question["approved"] = False
        self._write(previous)
        return self.get(lesson_id)

    def split_segment(self, lesson_id, segment_id, vi_position, en_position):
        lesson = self.get(lesson_id)
        index = next(i for i, s in enumerate(lesson["segments"]) if s["id"] == segment_id)
        segment = lesson["segments"][index]
        parts = {}
        for language, position in (("vi", vi_position), ("en", en_position)):
            value = segment[language]
            if value.strip():
                if not isinstance(position, int) or not 0 < position < len(value):
                    raise ValueError("Đặt con trỏ ở điểm tách bên trong mỗi ô ngôn ngữ có nội dung.")
                first, second = value[:position].strip(), value[position:].strip()
                if not first or not second:
                    raise ValueError("Mỗi phần sau khi tách phải có nội dung.")
                parts[language] = [first, second]
            else:
                parts[language] = ["", ""]
        children = [
            {
                **copy.deepcopy(segment),
                "id": str(uuid4()),
                "vi": parts["vi"][i],
                "en": parts["en"][i],
                "locator": segment["locator"] + f" · phần {i + 1}",
                "approved": False,
                "split_from": segment_id,
            }
            for i in range(2)
        ]
        for child in children:
            for item in child.get("support", []):
                item.update(id=str(uuid4()), approved=False)
        for question in lesson.get("questions", []):
            if question.get("concept_id") == segment_id:
                question.update(concept_id=children[0]["id"], approved=False)
        # Keep original source text on both fragments for traceability; edited text
        # must never silently replace the immutable extraction snapshot.
        lesson["segments"][index : index + 1] = children
        lesson.update(revision=lesson["revision"] + 1, updated_at=now())
        self._write(lesson)
        return lesson

    def set_presentation(self, lesson_id, level, layout):
        if type(level) is not int or not 0 <= level <= 5:
            raise ValueError("Level phải từ L0 đến L5.")
        if layout not in {"keyword_overlay", "line_pair", "split_view", "english_rescue"}:
            raise ValueError("Layout không hợp lệ.")
        lesson = self.get(lesson_id)
        lesson.update(level=level, layout=layout, revision=lesson["revision"] + 1, updated_at=now())
        self._write(lesson)
        return lesson

    def set_teaching_preset(self, lesson_id, preset):
        if preset not in PRESETS:
            raise ValueError("Chọn một kiểu dạy hợp lệ.")
        lesson = self.get(lesson_id)
        if lesson.get("teaching_preset", "standard") == preset:
            return lesson
        lesson.update(teaching_preset=preset, revision=lesson["revision"] + 1, updated_at=now())
        self._write(lesson)
        return lesson

    def set_presentation_style(self, lesson_id, style):
        if style not in {"source", "template"}:
            raise ValueError("Chọn cách trình bày hợp lệ.")
        lesson = self.get(lesson_id)
        if style == "source" and not (lesson.get("source") or {}).get("file", "").lower().endswith(".pptx"):
            raise ValueError("Giữ thiết kế gốc cần tài liệu PowerPoint.")
        if lesson.get("presentation_style", "template") == style:
            return lesson
        lesson.update(presentation_style=style, revision=lesson["revision"] + 1, updated_at=now())
        self._write(lesson)
        return lesson

    def set_block_type(self, lesson_id, segment_id, kind):
        from .lesson_templates import catalog

        if kind not in {item["id"] for item in catalog()["blocks"]}:
            raise ValueError("Chọn một loại slide hợp lệ.")
        lesson = self.get(lesson_id)
        segment = next((item for item in lesson["segments"] if item["id"] == segment_id), None)
        if segment is None:
            raise ValueError("Không tìm thấy đoạn bài học.")
        if segment.get("kind") != kind:
            segment["kind"] = kind
            lesson.update(revision=lesson["revision"] + 1, updated_at=now())
            self._write(lesson)
        return lesson

    def mark_prepared(self, lesson_id, expected_revision):
        from .readiness import text_readiness

        lesson = self.get(lesson_id)
        if lesson["revision"] != expected_revision:
            raise RevisionConflict("Bài vừa được sửa. Hãy kiểm tra và chuẩn bị lại.")
        if not text_readiness(lesson, self.directory)["text_ready"]:
            raise ValueError("Duyệt đủ cặp Việt–Anh và kiểm tra nguồn trước khi chốt bản chuẩn bị.")
        lesson["prepared"] = {"revision": lesson["revision"],
                              "source_sha256": (lesson.get("source") or {}).get("sha256", ""),
                              "created_at": now()}
        self._write(lesson)
        return lesson

    def save_support(self, lesson_id, segment_id, item, item_id=""):
        from .content import validate_support
        lesson = self.get(lesson_id)
        segment = next(s for s in lesson["segments"] if s["id"] == segment_id)
        prepared = validate_support(item)
        items = segment.setdefault("support", [])
        if len(items) >= 100 and not item_id:
            raise ValueError("Một đoạn hỗ trợ tối đa 100 mục trợ giảng.")
        if item_id:
            index = next(i for i, item in enumerate(items) if item["id"] == item_id)
            prepared["id"] = item_id
            items[index] = prepared
        else:
            items.append(prepared)
        lesson.update(revision=lesson["revision"] + 1, updated_at=now())
        self._write(lesson)
        return lesson

    def delete_support(self, lesson_id, segment_id, item_id):
        lesson = self.get(lesson_id)
        segment = next(s for s in lesson["segments"] if s["id"] == segment_id)
        segment["support"] = [s for s in segment.get("support", []) if s["id"] != item_id]
        lesson.update(revision=lesson["revision"] + 1, updated_at=now())
        self._write(lesson)
        return lesson

    def save_question(self, lesson_id, value, question_id=""):
        from .content import validate_question
        lesson = self.get(lesson_id)
        question = validate_question(value)
        if question["concept_id"] not in {s["id"] for s in lesson["segments"]}:
            raise ValueError("Câu hỏi phải liên kết một đoạn còn trong bài.")
        questions = lesson.setdefault("questions", [])
        if len(questions) >= 200 and not question_id:
            raise ValueError("Một bài hỗ trợ tối đa 200 câu hỏi.")
        if question_id:
            index = next(i for i, item in enumerate(questions) if item["id"] == question_id)
            question["id"] = question_id
            questions[index] = question
        else:
            questions.append(question)
        lesson.update(revision=lesson["revision"] + 1, updated_at=now())
        self._write(lesson)
        return lesson

    def delete_question(self, lesson_id, question_id):
        lesson = self.get(lesson_id)
        lesson["questions"] = [q for q in lesson.get("questions", []) if q["id"] != question_id]
        lesson.update(revision=lesson["revision"] + 1, updated_at=now())
        self._write(lesson)
        return lesson

    def update_metadata(self, lesson_id, title, subject, education, grade):
        values = [title, subject, education, grade]
        if any(not isinstance(v, str) or not v.strip() or len(v) > 200 for v in values):
            raise ValueError("Điền đầy đủ tên bài, môn, cấp và khối; tối đa 200 ký tự mỗi mục.")
        lesson = self.get(lesson_id)
        if subject.strip() != lesson["subject"]:
            for segment in lesson["segments"]:
                segment["approved"] = False
                for item in segment.get("support", []):
                    item["approved"] = False
            for question in lesson.get("questions", []):
                question["approved"] = False
        lesson.update(title=title.strip(), subject=subject.strip(), education_level=education.strip(),
                      grade=grade.strip(), revision=lesson["revision"] + 1, updated_at=now())
        self._write(lesson)
        return lesson

    def setting(self, key, default):
        row = self.db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else default

    def set_setting(self, key, value):
        with self.db:
            self.db.execute(
                "INSERT INTO settings VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, json.dumps(value, ensure_ascii=False)),
            )

    def glossary(self, subject="", teacher_id="local-teacher"):
        rows = self.db.execute(
            "SELECT * FROM glossary WHERE teacher_id=? AND (?='' OR subject=?) ORDER BY subject,vi",
            (teacher_id, subject, subject),
        ).fetchall()
        return [dict(row) for row in rows]

    def save_term(self, subject, vi, en, locked=True, teacher_id="local-teacher"):
        if not all(value.strip() for value in (subject, vi, en)):
            raise ValueError("Nhập môn, thuật ngữ Việt và bản tiếng Anh.")
        with self.db:
            self.db.execute(
                """INSERT INTO glossary VALUES(?,?,?,?,?,?)
                ON CONFLICT(teacher_id,subject,vi) DO UPDATE SET en=excluded.en,locked=excluded.locked""",
                (str(uuid4()), teacher_id, subject.strip(), vi.strip(), en.strip(), int(locked)),
            )

    def delete_term(self, term_id, teacher_id="local-teacher"):
        with self.db:
            self.db.execute("DELETE FROM glossary WHERE id=? AND teacher_id=?", (term_id, teacher_id))

    def knowledge_pack(self, pack_id):
        row = self.db.execute(
            "SELECT pack_id,pack_version AS version,MAX(retrieved_at) AS retrieved_at "
            "FROM knowledge_sources WHERE pack_id=? GROUP BY pack_id,pack_version",
            (pack_id,),
        ).fetchone()
        return dict(row) if row else None

    def install_knowledge_pack(self, pack):
        """Replace one pack atomically; teacher glossary is deliberately untouched."""
        from .knowledge import validate_pack

        pack = validate_pack(pack)
        manifest = pack["manifest"]
        pack_id, pack_version = manifest["pack_id"], manifest["version"]
        with self.db:
            self.db.execute("DELETE FROM knowledge_entries WHERE pack_id=?", (pack_id,))
            self.db.execute("DELETE FROM knowledge_sources WHERE pack_id=?", (pack_id,))
            self.db.executemany(
                """INSERT INTO knowledge_sources
                (id,pack_id,pack_version,title,publisher,document_no,issued_at,effective_at,
                 source_url,official,source_type,retrieved_at,status,license,notes)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                [
                    (
                        source["id"], pack_id, pack_version, source["title"], source["publisher"],
                        source["document_no"], source["issued_at"], source["effective_at"],
                        source["source_url"], int(source["official"]), source["source_type"],
                        source["retrieved_at"], source["status"], source["license"], source["notes"],
                    )
                    for source in pack["sources"]
                ],
            )
            self.db.executemany(
                """INSERT INTO knowledge_entries
                (id,pack_id,pack_version,subject,grade,kind,vi,en,definition_vi,definition_en,
                 aliases_json,source_ids_json,status,confidence,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                [
                    (
                        entry["id"], pack_id, pack_version, entry["subject"], entry["grade"],
                        entry["kind"], entry["vi"], entry["en"], entry["definition_vi"],
                        entry["definition_en"], json.dumps(entry["aliases"], ensure_ascii=False),
                        json.dumps(entry["source_ids"], ensure_ascii=False), entry["status"],
                        entry["confidence"], entry["updated_at"],
                    )
                    for entry in pack["entries"]
                ],
            )

    def knowledge_sources(self):
        rows = self.db.execute(
            "SELECT * FROM knowledge_sources ORDER BY official DESC, issued_at DESC, title"
        ).fetchall()
        return [dict(row) for row in rows]

    def knowledge_entry(self, entry_id):
        row = self.db.execute(
            "SELECT * FROM knowledge_entries WHERE id=?", (entry_id,)
        ).fetchone()
        if not row:
            return None
        item = dict(row)
        item["aliases"] = json.loads(item.pop("aliases_json"))
        item["source_ids"] = json.loads(item.pop("source_ids_json"))
        return item

    def knowledge_entries(self, query="", subject="", grade="", limit=200):
        query = " ".join(str(query).split()).casefold()
        subject = str(subject or "").strip()
        grade = str(grade or "").strip()
        rows = self.db.execute(
            "SELECT * FROM knowledge_entries WHERE (?='' OR subject=?) AND (?='' OR grade='' OR grade=?) "
            "ORDER BY CASE kind WHEN 'term' THEN 0 WHEN 'subject' THEN 1 ELSE 2 END, vi",
            (subject, subject, grade, grade),
        ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["aliases"] = json.loads(item.pop("aliases_json"))
            item["source_ids"] = json.loads(item.pop("source_ids_json"))
            if query:
                haystack = " ".join(
                    [item["vi"], item["en"], item["subject"], item["kind"], *item["aliases"]]
                ).casefold()
                if query not in haystack:
                    continue
            source_rows = []
            for source_id in item["source_ids"]:
                source = self.db.execute(
                    "SELECT id,title,source_url,document_no,official,source_type FROM knowledge_sources WHERE id=?",
                    (source_id,),
                ).fetchone()
                if source:
                    source_rows.append(dict(source))
            item["sources"] = source_rows
            result.append(item)
            if len(result) >= max(1, min(int(limit), 50_000)):
                break
        return result

    def knowledge_translation(self, subject, text, source_language="vi"):
        """Resolve an exact pack term after teacher-approved memory.

        Official/curated foundation entries win over entries marked as online.
        Ambiguous alternatives are returned as no result so the UI can ask the
        teacher instead of silently choosing a meaning across subjects.
        """
        if source_language not in ("vi", "en") or not subject.strip() or not text.strip():
            return None
        source, target = ("vi", "en") if source_language == "vi" else ("en", "vi")
        matches = []
        for entry in self.knowledge_entries(query=text, limit=50_000):
            if entry["subject"] not in (subject.strip(), "Chung"):
                continue
            if entry[source].strip() != text.strip():
                continue
            source_types = {source_row["source_type"] for source_row in entry["sources"]}
            online = bool(source_types) and all(source_type.startswith("online") for source_type in source_types)
            matches.append({"text": entry[target], "online": online, "entry": entry})
        if not matches:
            return None
        curated = {item["text"] for item in matches if not item["online"]}
        online = {item["text"] for item in matches if item["online"]}
        if len(curated) == 1:
            return {"text": next(iter(curated)), "tier": "knowledge"}
        if not curated and len(online) == 1:
            return {"text": next(iter(online)), "tier": "online"}
        return None

    def knowledge_terms(self, subject, include_online=False):
        """Return source-backed terms for model protection, without mutating glossary."""
        if not subject.strip():
            return []
        result = []
        for entry in self.knowledge_entries(limit=50_000):
            if entry["subject"] not in (subject.strip(), "Chung"):
                continue
            source_types = {source_row["source_type"] for source_row in entry["sources"]}
            online = bool(source_types) and all(source_type.startswith("online") for source_type in source_types)
            if online and not include_online:
                continue
            result.append({"id": entry["id"], "subject": entry["subject"], "vi": entry["vi"],
                           "en": entry["en"], "locked": True, "source": "online" if online else "knowledge"})
        return result

    def knowledge_stats(self):
        packs = self.db.execute(
            "SELECT COUNT(DISTINCT pack_id) FROM knowledge_sources"
        ).fetchone()[0]
        entries = self.db.execute("SELECT COUNT(*) FROM knowledge_entries").fetchone()[0]
        sources = self.db.execute("SELECT COUNT(*) FROM knowledge_sources").fetchone()[0]
        return {"packs": packs, "entries": entries, "sources": sources}

    def exact_translation(self, subject, text, teacher_id="local-teacher", source_language="vi"):
        source, target = ("vi", "en") if source_language == "vi" else ("en", "vi")
        rows = self.db.execute(
            f"SELECT DISTINCT {target} FROM glossary WHERE teacher_id=? AND subject=? AND {source}=?",
            (teacher_id, subject, text.strip()),
        ).fetchall()
        return rows[0][0] if len(rows) == 1 else None  # ambiguous reverse matches need review

    def approved_translations(self, subject, text, source_language="vi", exclude=None):
        """Find current, explicitly approved wording from lessons in the same subject.

        Drafts, revision history and imported packs awaiting local review never teach memory.
        Return every distinct target so different teacher choices remain visible.
        """
        if source_language not in ("vi", "en"):
            raise ValueError("Hướng dịch không hợp lệ.")
        source_text = memory_key(text)
        if not source_text or not subject.strip():
            return []
        target_language = "en" if source_language == "vi" else "vi"
        matches = {}
        rows = self.db.execute(
            "SELECT id,title,content FROM lessons WHERE subject=? ORDER BY updated_at DESC",
            (subject,),
        )
        for row in rows:
            for segment in json.loads(row["content"])["segments"]:
                if (row["id"], segment["id"]) == exclude or not segment.get("approved"):
                    continue
                if memory_key(segment[source_language]) != source_text:
                    continue
                target = segment[target_language].strip()
                if not target:
                    continue
                result = matches.setdefault(target, {"text": target, "count": 0, "lessons": []})
                result["count"] += 1
                if row["title"] not in result["lessons"] and len(result["lessons"]) < 3:
                    result["lessons"].append(row["title"])
        return sorted(matches.values(), key=lambda item: -item["count"])

    def store_source(self, path):
        if not Path(path).is_file() or Path(path).stat().st_size > 50 * 1024**2:
            raise ValueError("Tệp nguồn không đọc được hoặc vượt 50 MB.")
        data = Path(path).read_bytes()
        if len(data) > 50 * 1024**2:
            raise ValueError("Tệp nguồn vượt 50 MB.")
        digest = hashlib.sha256(data).hexdigest()
        assets = self.directory / "sources"
        assets.mkdir(exist_ok=True)
        suffix = Path(path).suffix.lower()
        target = assets / (digest + suffix)
        if not target.exists():
            target.write_bytes(data)
        return {"name": Path(path).name, "sha256": digest, "file": target.name}

    def similar_translations(self, subject, text, source_language="vi", exclude=None):
        from difflib import SequenceMatcher
        if source_language not in ("vi", "en") or len(text) > 5000:
            return []
        target = "en" if source_language == "vi" else "vi"
        key, matches = memory_key(text), {}
        if len(key) < 12:
            return []
        for row in self.db.execute("SELECT id,title,content FROM lessons WHERE subject=?", (subject,)):
            for segment in json.loads(row["content"])["segments"]:
                if not segment.get("approved") or (row["id"], segment["id"]) == exclude:
                    continue
                source = memory_key(segment[source_language])
                if len(source) > 5000 or source == key:
                    continue
                matcher = SequenceMatcher(None, key, source, autojunk=False)
                if matcher.quick_ratio() < .75:
                    continue
                score = matcher.ratio()
                if score >= .75:
                    value = {"text": segment[target], "source": source, "similarity": round(score*100), "count": 1, "lessons": [row["title"]]}
                    matches[(source, segment[target])] = value
        return sorted(matches.values(), key=lambda item: -item["similarity"])[:5]
