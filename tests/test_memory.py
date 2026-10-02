from app.library import Library
from app.pack import export_pack, import_pack


def approved(library, subject, source, target):
    lesson = library.create(source[:30], subject, "THPT", "11", [("Đoạn 1", source)])
    return library.edit_segment(
        lesson["id"], lesson["segments"][0]["id"], source, target, True
    )


def test_teacher_approved_memory_is_bidirectional_and_subject_scoped(tmp_path):
    library = Library(tmp_path / "library")
    lesson = approved(library, "Sinh học", "Tế bào là đơn vị cơ bản.", "The cell is the basic unit.")
    approved(library, "Tin học", "Tế bào là đơn vị cơ bản.", "A cell is the basic unit.")
    result = library.approved_translations("Sinh học", "  Tế bào là\nđơn vị cơ bản.  ")
    assert [item["text"] for item in result] == ["The cell is the basic unit."]
    assert result[0]["lessons"] == [lesson["title"]]
    assert library.approved_translations("Sinh học", "The cell is the basic unit.", "en")[0][
        "text"
    ] == "Tế bào là đơn vị cơ bản."
    assert library.approved_translations("Vật lý", "Tế bào là đơn vị cơ bản.") == []
    assert library.approved_translations("Sinh học", "Tế bào là đơn vị cơ bản!") == []
    assert library.approved_translations(
        "Sinh học", "Tế bào là đơn vị cơ bản.", exclude=(lesson["id"], lesson["segments"][0]["id"])
    ) == []
    library.close()


def test_conflicting_approved_phrases_remain_choices_not_an_automatic_answer(tmp_path):
    library = Library(tmp_path / "library")
    first = approved(library, "Lịch sử", "Đưa ra bằng chứng.", "Present evidence.")
    second = approved(library, "Lịch sử", "Đưa ra bằng chứng.", "Provide supporting evidence.")
    results = library.approved_translations("Lịch sử", "Đưa ra bằng chứng.")
    assert {item["text"] for item in results} == {"Present evidence.", "Provide supporting evidence."}
    assert all(item["count"] == 1 for item in results)
    library.edit_segment(
        second["id"], second["segments"][0]["id"], "Đưa ra bằng chứng.", "Draft change."
    )
    assert [item["text"] for item in library.approved_translations("Lịch sử", "Đưa ra bằng chứng.")] == [
        "Present evidence."
    ]
    library.restore_revision(first["id"], 1)
    assert library.approved_translations("Lịch sử", "Đưa ra bằng chứng.") == []
    library.close()


def test_imported_pack_does_not_train_local_memory_until_review(tmp_path):
    origin = Library(tmp_path / "origin")
    lesson = approved(origin, "Ngữ văn", "Nêu nhận xét.", "Give your opinion.")
    pack = export_pack(origin, lesson["id"], tmp_path / "lesson.biliclass")
    destination = Library(tmp_path / "destination")
    copied = import_pack(destination, pack)
    assert destination.approved_translations("Ngữ văn", "Nêu nhận xét.") == []
    destination.edit_segment(
        copied["id"], copied["segments"][0]["id"], "Nêu nhận xét.", "Give your opinion.", True
    )
    assert destination.approved_translations("Ngữ văn", "Nêu nhận xét.")[0]["text"] == (
        "Give your opinion."
    )
    origin.close()
    destination.close()
