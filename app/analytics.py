"""Observable classroom results with explicit denominators and recheck separation."""

import csv
import json
import sqlite3
from pathlib import Path


def connection(directory):
    path = Path(directory) / "classroom.db"
    if not path.exists():
        return None
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def list_sessions(directory):
    conn = connection(directory)
    if conn is None:
        return []
    try:
        result = []
        for row in conn.execute("SELECT id,title,status,created,ended,lesson FROM sessions ORDER BY created DESC"):
            entry = dict(row)
            lesson = json.loads(entry.pop("lesson"))
            entry.update(lesson_id=lesson.get("id", ""), lesson_title=lesson.get("title", ""),
                         subject=lesson.get("subject", ""), grade=lesson.get("grade", ""),
                         revision=lesson.get("revision", 0), level=lesson.get("level", 2))
            result.append(entry)
        return result
    finally:
        conn.close()


def report(directory, session_id):
    conn = connection(directory)
    if conn is None:
        raise ValueError("Chưa có kết quả lớp học.")
    try:
        session = conn.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
        if not session:
            raise ValueError("Không tìm thấy phiên học.")
        lesson = json.loads(session["lesson"])
        rounds, concepts, participants, language_items = [], {}, set(), []
        for row in conn.execute("SELECT * FROM rounds WHERE session_id=? ORDER BY opened", (session_id,)):
            question = json.loads(row["question"])
            responses = list(conn.execute("SELECT participant_id,option_id FROM answers WHERE round_id=?", (row["id"],)))
            answered = len(responses)
            correct = sum(r["option_id"] == question["correct"] for r in responses) if question["kind"] != "poll" else None
            eligible = row["eligible"] if row["eligible"] is not None else conn.execute("SELECT count(*) FROM participants WHERE session_id=?", (session_id,)).fetchone()[0]
            distribution = []
            for option in question["options"]:
                count = sum(r["option_id"] == option["id"] for r in responses)
                distribution.append({"id": option["id"], "vi": option["vi"], "en": option["en"], "count": count,
                                     "percent": round(count / answered * 100, 1) if answered else None,
                                     "misconception": option["misconception"] if option["id"] != question["correct"] and question["kind"] != "poll" else ""})
            rounds.append({"id": row["id"], "question_id": question["id"], "prompt": question["vi"], "concept": question["concept_label"],
                           "kind": question["kind"], "language": row["language"], "status": row["status"],
                           "recheck_of": row["recheck_of"], "answered": answered, "eligible": eligible,
                           "unanswered": max(0, eligible-answered), "correct": correct,
                           "percent": round(correct / answered * 100, 1) if answered and correct is not None else None,
                           "participation": round(answered / eligible * 100, 1) if eligible else None,
                           "options": distribution, "respondents": sorted(r["participant_id"] for r in responses)})
            participants.update(r["participant_id"] for r in responses)
            if question.get("comparison_group") and not row["recheck_of"] and question["kind"] != "poll" and row["status"] != "open" and row["language"] in ("vi", "en"):
                language_items.append({"group": question["comparison_group"], "concept": question["concept_id"],
                                       "question": question["id"], "language": row["language"], "eligible": eligible,
                                       "responses": {r["participant_id"]: r["option_id"] == question["correct"] for r in responses}})
            if row["recheck_of"] or question["kind"] == "poll" or row["status"] == "open":
                continue
            concept = concepts.setdefault(question["concept_id"], {"label": question["concept_label"], "questions": set(), "people": set(), "answered": 0, "correct": 0})
            concept["questions"].add(question["id"])
            concept["people"].update(r["participant_id"] for r in responses)
            concept["answered"] += answered
            concept["correct"] += correct
        bars = []
        for concept in concepts.values():
            enough = len(concept["questions"]) >= 2 and len(concept["people"]) >= 10
            percent = round(concept["correct"] / concept["answered"] * 100, 1) if concept["answered"] else None
            bars.append({"label": concept["label"], "questions": len(concept["questions"]), "people": len(concept["people"]),
                         "answered": concept["answered"], "correct": concept["correct"], "percent": percent,
                         "confidence": "enough" if enough else "insufficient", "tone": "gray" if not enough else "green" if percent >= 80 else "amber" if percent >= 60 else "red"})
        comparisons = []
        by_id = {r["id"]: r for r in rounds}
        for result in rounds:
            before = by_id.get(result["recheck_of"])
            if before:
                same = result["respondents"] == before["respondents"]
                comparisons.append({"before": before["percent"], "after": result["percent"],
                                    "before_count": before["answered"], "after_count": result["answered"], "same_participants": same,
                                    "label": result["prompt"], "note": "Cùng người trả lời; đây là lượt kiểm tra lại cùng câu." if same else "Nhóm người trả lời thay đổi; không coi chênh lệch là tiến bộ cá nhân."})
        for item in rounds:
            item.pop("respondents")  # no identifiers needed in UI summary
        language_summary = compare_languages(language_items, lesson["level"])
        return {"id": session_id, "title": session["title"], "status": session["status"], "rounds": rounds, "concepts": bars,
                "comparisons": comparisons, "participants_responded": len(participants),
                "lesson_id": lesson.get("id", ""), "lesson_title": lesson.get("title", ""),
                "subject": lesson.get("subject", ""), "grade": lesson.get("grade", ""),
                "revision": lesson.get("revision", 0), "level": lesson["level"],
                "language_comparison": language_summary,
                "recommendation": language_summary["recommendation"]}
    finally:
        conn.close()


def safe_csv(value):
    text = "" if value is None else str(value)
    return "'" + text if text.startswith(("\t", "\r", "\n")) or text.lstrip().startswith(("=", "+", "-", "@")) else text


def compare_languages(items, level):
    """Teacher-tagged equivalent questions, same respondents; never use rechecks."""
    grouped = {}
    for item in items:
        grouped.setdefault((item["concept"], item["group"]), {"vi": [], "en": []})[item["language"]].append(item)
    pairs = []
    for (_, group), languages in grouped.items():
        if len(languages["vi"]) != 1 or len(languages["en"]) != 1:
            continue
        vi, en = languages["vi"][0], languages["en"][0]
        people = set(vi["responses"])
        if (vi["question"] == en["question"] or people != set(en["responses"]) or len(people) < 10
                or any(len(people) / max(1, item["eligible"]) < .8 for item in (vi, en))):
            continue
        pairs.append({"group": group, "count": len(people), "vi_correct": sum(vi["responses"].values()), "en_correct": sum(en["responses"].values())})
    if len(pairs) < 2:
        return {"eligible": False, "pairs": pairs, "recommendation": "Chưa đủ dữ liệu đối chiếu Việt/Anh: cần ít nhất 2 cặp câu tương đương do thầy cô gắn nhãn, mỗi cặp cùng ít nhất 10 người trả lời và tham gia ≥80%. Không dùng lượt kiểm tra lại."}
    count = sum(p["count"] for p in pairs)
    vi = round(sum(p["vi_correct"] for p in pairs)/count*100, 1)
    en = round(sum(p["en_correct"] for p in pairs)/count*100, 1)
    suggested = min(5, level+1) if vi >= 80 and en >= 80 else max(0, level-1) if vi >= 75 and en < 60 else level
    return {"eligible": True, "pairs": pairs, "vi_percent": vi, "en_percent": en, "suggested_level": suggested,
            "recommendation": f"Gợi ý cân nhắc L{suggested}: {len(pairs)} cặp / {count} lượt trả lời mỗi ngôn ngữ; đúng VI {vi}%, EN {en}%. Tăng một mức khi cả hai ≥80%; giảm khi VI ≥75% và EN <60%; còn lại giữ. Đây là gợi ý từ mẫu quan sát, chưa loại trừ độ khó/thứ tự câu. Thầy cô quyết định."}


def export_csv(directory, session_id, destination):
    data = report(directory, session_id)
    target = Path(destination).with_suffix(".csv")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["Lớp", "Lượt", "Kiểm tra lại của", "Câu hỏi", "Chủ đề", "Loại", "Ngôn ngữ", "Trạng thái", "Đã trả lời", "Đủ điều kiện", "Chưa trả lời", "Đúng", "% đúng / câu trả lời", "% tham gia / đủ điều kiện"])
        for row in data["rounds"]:
            writer.writerow([safe_csv(value) for value in (data["title"], row["id"], row["recheck_of"], row["prompt"], row["concept"], row["kind"], row["language"], row["status"], row["answered"], row["eligible"], row["unanswered"], row["correct"], row["percent"], row["participation"])])
    return target


def delete_session(directory, session_id):
    conn = connection(directory)
    if conn is None:
        return
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        row = conn.execute("SELECT status FROM sessions WHERE id=?", (session_id,)).fetchone()
        if row and row[0] != "ended":
            raise ValueError("Kết thúc phiên học trước khi xóa báo cáo.")
        with conn:
            conn.execute("UPDATE rounds SET recheck_of=NULL WHERE session_id=?", (session_id,))
            conn.execute("DELETE FROM sessions WHERE id=?", (session_id,))
    finally:
        conn.close()


def export_response_csv(directory, session_id, destination):
    conn = connection(directory)
    if conn is None:
        raise ValueError("Chưa có dữ liệu lớp học.")
    target = Path(destination).with_suffix(".csv")
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with target.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["Lượt", "Kiểm tra lại của", "Mã người tham gia", "Chỗ", "Câu hỏi", "Ngôn ngữ", "Lựa chọn", "Đúng", "Thời điểm cập nhật"])
            rows = conn.execute("SELECT r.id,r.recheck_of,r.question,r.language,p.id participant,p.seat,a.option_id,a.updated FROM rounds r JOIN answers a ON a.round_id=r.id JOIN participants p ON p.id=a.participant_id WHERE r.session_id=? ORDER BY r.opened,p.seat,p.id", (session_id,))
            for row in rows:
                question = json.loads(row["question"])
                correct = "" if question["kind"] == "poll" else int(question["correct"] == row["option_id"])
                writer.writerow([safe_csv(v) for v in (row["id"], row["recheck_of"], row["participant"], row["seat"], question["vi"], row["language"], row["option_id"], correct, row["updated"])])
    finally:
        conn.close()
    return target
