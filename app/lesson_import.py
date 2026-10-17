"""Publish a converted lesson on a worker-owned database connection."""

import json
from contextlib import closing

from .chatgpt_handoff import external_preview
from .library import Library
from .storage_space import MIB, require_space


def save_conversion(directory, config, source, inspection, cancel=None):
    """Resume an interrupted import without creating a second lesson.

    The caller owns the conversion job/profile lock. Never pass the GUI's
    sqlite connection across threads or start narration as part of this step.
    """
    if cancel is not None and cancel.is_set():
        raise InterruptedError("Đã dừng; kết quả nhận được vẫn được giữ.")
    require_space(directory, 16 * MIB)
    with closing(Library(directory)) as library:
        lesson = None
        # Serialize the lookup+insert across app instances too. The complete
        # lesson is committed in one write before hashing its preview.
        with library.db:
            library.db.execute("BEGIN IMMEDIATE")
            request_id = config.get("request_id")
            if request_id:
                for row in library.db.execute("SELECT content FROM lessons"):
                    saved = json.loads(row[0])
                    if saved.get("external_deck", {}).get("request_id") == request_id:
                        if saved.get("deleted_at"):
                            raise ValueError("Bài đã nhận đang ở thùng rác. Khôi phục trong thư viện để mở lại.")
                        lesson = saved
                        break
            if lesson is None:
                lesson = library.create_external_lesson(config, source, inspection)
            else:
                # Legacy normalization must use the same lock as the lookup,
                # so another connection cannot edit the lesson in between.
                from .narration_script import prepare

                lesson = prepare(library, lesson)
        # A cancellation after the commit does not delete the saved result.
        # The request ID above lets the next resume find it safely.
        return lesson, external_preview(lesson, directory)
