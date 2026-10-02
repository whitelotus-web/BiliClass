# Thiết kế dữ liệu dự kiến

Phần 1–8 là hợp đồng thiết kế ban đầu. RC1 ngày 30/09/2026 có database và validator thực thi; xem phần cuối để phân biệt tên bảng/trường thực tế với đề xuất.

## 1. Các thực thể cốt lõi

| Thực thể | Trường chính / quy tắc |
|---|---|
| Subject | `id`, `name_vi`, `name_en`, `is_custom`; môn là dữ liệu mở rộng |
| Lesson | UUID, title, subject_id, education_level/grade cấu hình tự do, tags, nguồn, revision hiện tại |
| LessonRevision | revision ID, lesson_id, content_hash, review state, created_at; giữ lịch sử cho phiên học |
| SourceDocument | source ID, original_name, MIME, SHA-256, relative asset path; bất biến |
| Slide/Page | ID bền vững, source_document_id, source locator, thứ tự, preview asset, các block |
| ContentBlock | ID, kind, source text, source locator/bbox, protected spans, source language |
| BilingualSegment | block_id, VI/EN, variant type, review/lock, provenance, translation revision |
| Concept | ID, title VI/EN, liên kết nhiều slide/block, definition/example/question đã duyệt |
| GlossaryEntry | môn/phạm vi, term VI/EN, sense/context, variant chấp nhận, trạng thái khóa |
| TranslationMemoryEntry | ngôn ngữ nguồn/đích, normalized source, target, scope/môn, context fingerprint, teacher approved |
| PresentationSettings | level L0–L5, layout enum, mascot ID; level khác layout |
| AudioItem | text hash, provider/voice/version/language/rate, file hash/path, status |
| PreparedRevision | revision_id, prepared_at, approved content hash, audio manifest, capability status |

Không dùng số thứ tự slide làm khóa duy nhất; di chuyển/thêm slide không được làm concept trỏ nhầm. Cùng một thuật ngữ có thể có nhiều nghĩa trong các môn; constraint memory phải gồm phạm vi và cặp ngôn ngữ.

`provenance` gồm nguồn của nội dung: extracted, model_translation, teacher_authored hoặc curated_template, cùng source_refs và provider revision khi có. Review đi theo item và revision, không chỉ một boolean “đã duyệt” cho toàn bài.

## 2. Vòng đời bài

Trạng thái bài: `DRAFT → REVIEW_REQUIRED → READY_TO_TEACH`. Tiến độ job chuẩn bị: `idle → preparing → prepared/failed`, tách riêng quyền duyệt nội dung.

Sửa nội dung tạo revision/draft mới; invalidation nội dung và audio liên quan. Revision đang dùng trong session là snapshot bất biến. Một bài không có quiz vẫn đủ điều kiện Prepared nếu phần nội dung giảng dạy đã duyệt; thiếu voice có thể chuẩn bị text-only với nhãn khả năng rõ ràng. Đánh dấu “sẵn sàng phát âm offline” riêng khi audio/voice đã qua kiểm tra.

## 3. Lesson Pack .biliclass

```text
manifest.json
lesson.json
settings.json
source/<document-id>.<ext>
slides/<slide-id>.json
concepts/concepts.json
glossary/glossary.json
quiz/quiz.json
audio/index.json
audio/<content-hash>.wav
assets/<content-hash>.<ext>
```

`manifest.json` có schema_version, minimum_reader_version, lesson_id, revision_id, created_at, capabilities và danh sách file (relative_path, SHA-256, size). `quiz.json` có thể rỗng. Không nhúng model lớn, đường dẫn tuyệt đối máy giáo viên, account/token, classroom database hay dữ liệu học sinh.

Lesson Pack mang thuật ngữ/bản dịch đã duyệt của bài. Import pack không tự ghi đè memory toàn bộ thư viện; nếu muốn nhập glossary vào kho cá nhân, giáo viên chọn phạm vi. Có thể phát cache audio trên máy khác; voice ID trong pack chỉ là metadata, không bảo đảm voice đó đã cài.

Phải validate schema, checksum, path và quota giải nén trước nạp. Pack schema mới chưa hỗ trợ không được sửa rồi lưu đè. Migration tạo bản mới và giữ nguồn. Manifest không tự bảo đảm tệp đáng tin, vẫn cần kiểm tra nội dung khi import.

## 4. Hai database local

| Database | Bảng dự kiến |
|---|---|
| `library.db` | schema_migrations, subjects, lessons, lesson_revisions, source_documents, glossary_entries, translation_memory, audio_cache, settings, preparation_jobs |
| `classroom.db` | schema_migrations, lesson_snapshots, classes, sessions, participants, question_rounds, answers, processed_messages, session_events |

Asset lớn nằm trong kho file theo hash. Draft content có thể lưu JSON có version trong lesson_revisions; những trường cần tìm kiếm/tính toán được index riêng. Không nhân bản mọi trạng thái UI vào database.

Xóa bài không làm hỏng session lịch sử: session giữ snapshot cần thiết. Xóa session sẽ xóa participant/answer/events liên quan bằng transaction. Asset thu gom chỉ khi không còn tham chiếu. Có thao tác backup/export/xóa dữ liệu rõ ràng; log không ghi token hoặc toàn bộ dữ liệu học sinh mặc định.

## 5. Dữ liệu quiz và quyền truy cập

| Thực thể | Hợp đồng |
|---|---|
| Question | ID, revision, type, VI/EN prompt, options, primary concept_id, optional related concepts, language demand tag |
| PrivateQuestionData | correct option hoặc null cho poll, rationale, misconception map, nguồn đã duyệt |
| Session | UUID, join code/token digest, lesson snapshot, class_id tùy chọn, trạng thái, current round, start/end |
| Participant | ID server cấp, session_id, anonymous label hoặc seat, reconnect token digest, last_seen |
| QuestionRound | ID, question revision snapshot, open/close/reveal timestamps, sequence, recheck_of nullable |
| Answer | round_id, participant_id, selected option, submission ID, server timestamp, revision |

UNIQUE `(round_id, participant_id)` cho đáp án hiệu lực; UNIQUE `(session_id, participant_id, submission_id)` cho xử lý retry. Đổi đáp án khi còn mở cập nhật bản ghi nhưng không cộng thêm người trả lời. Poll không có correct option. Học sinh vào lại dùng token đã cấp; không tin participant_id do client gửi riêng.

DTO student gồm prompt/options, round ID, deadline, trạng thái bản thân; không gồm PrivateQuestionData. Teacher DTO có thống kê và đáp án. Payload trả lời bị kiểm tra participant/session/round/option và trạng thái câu theo giờ server. Late answer không bị âm thầm đưa vào kết quả đã đóng.

Anonymous ID chỉ phục vụ phiên/reconnect; không theo dõi một học sinh qua nhiều phiên bằng device fingerprint. Seat có thể gắn danh sách local nếu giáo viên chủ động dùng. So sánh nhiều tiết ở chế độ ẩn danh chỉ ở cấp lớp được giáo viên chọn, không suy ra tiến bộ từng cá nhân.

## 6. Hợp đồng tính chỉ số

Các ngưỡng sau là đề xuất sản phẩm để kiểm chứng cùng giáo viên, không phải chuẩn đo năng lực đã được thẩm định.

- Số đã trả lời = số participant có đáp án hợp lệ duy nhất trong round.
- Phân bố lựa chọn = số chọn lựa chọn / số câu trả lời hợp lệ; tổng có thể lệch 100% nhẹ do làm tròn.
- Tỷ lệ đúng = số đáp án đúng / số đáp án hợp lệ cho câu được chấm. Chưa trả lời thống kê riêng, không mặc định thành sai.
- Tỷ lệ tham gia = số người phản hồi / số người tham gia đủ điều kiện tại thời điểm chốt round; lưu denominator snapshot. Nếu có sĩ số lớp, hiển thị thêm “đã vào/sĩ số”, không thay mẫu số ngầm.
- Mỗi câu có primary concept để tính điểm; related concepts phục vụ tìm kiếm, không nhân đôi điểm. Concept score tổng hợp các lượt ban đầu, kèm số câu khác nhau, số người và số phản hồi.
- Recheck là lượt mới liên kết lượt trước, không ghi đè baseline. Báo cáo cho biết cùng câu hay câu tương đương; nếu đổi nhóm tham gia, hiển thị số lượng và không coi chênh lệch là tiến bộ cá nhân.
- Misconception lấy từ map của đáp án sai đã duyệt; nhãn “có dấu hiệu” và tỷ lệ trên số phản hồi của câu, không suy diễn tự do.
- Ngưỡng màu gợi ý: xanh ≥80%, vàng 60–<80%, đỏ <60%, chỉ áp khi có ít nhất hai câu khác nhau và tối thiểu mười người trả lời cho concept; thiếu dữ liệu dùng xám. Hiện ngưỡng trong trợ giúp và cho hiệu chỉnh sau pilot.
- So sánh câu VI/EN phải lưu language demand và cặp/nhóm câu tương đương. Từ các tập câu không tương đương chỉ báo tỷ lệ quan sát, không kết luận rào cản ngôn ngữ.
- Gợi ý level chỉ xét khi đủ dữ liệu của lớp: đề xuất tối thiểu hai hoạt động và năm câu chấm được ở nhóm cần so sánh. Hiển thị phạm vi mẫu; nếu chưa đủ thì “Chưa đủ dữ liệu để gợi ý”. Giáo viên quyết định, không tự nâng mức.

Một bài song ngữ không chạy quiz sẽ có báo cáo sử dụng cơ bản hoặc thông báo “Chưa có dữ liệu kiểm tra”; không tạo tỷ lệ hiểu bài từ lượt bấm phát âm hay VI Rescue.

## 7. CSV

CSV UTF-8 phù hợp tiếng Việt, cột có định nghĩa: lớp/phiên, bài/revision, câu/lượt, concept, ngôn ngữ, anonymous label/seat tùy chọn, đáp án, correct nullable, timestamp. Kèm bảng tổng hợp với mẫu số và phân biệt initial/recheck/poll.

Xử lý giá trị mở đầu bằng `=`, `+`, `-`, `@` như dữ liệu văn bản để tránh công thức ngoài ý muốn khi mở bằng bảng tính. Không xuất token hoặc dữ liệu cá nhân không được chọn.

## 8. Trường bổ sung từ góp ý

Concept bắt buộc hỗ trợ: explanation_vi, explanation_en, easy_en, examples, teacher_prompts, questions, vi_rescue, vocabulary, quiz_refs, misconceptions, audio_scripts, audio_cache_refs. Các trường có thể rỗng nhưng phải thể hiện thiếu nội dung trong readiness và assistant.

Memory key ít nhất gồm teacher_id + subject_id + source/target language + source text. Readiness lưu warning và override của giáo viên theo revision; override không đổi review state của item.

## Bản triển khai đầu 0.2

Draft SQLite hiện dùng user_version=2; lesson JSON thêm source_language và source_text bất biến tại segment. lesson_revisions giữ 30 bản trước mỗi lần ghi; restore tăng revision và bỏ trạng thái duyệt. Draft pack có kind biliclass-draft, schema_version=2; importer nhận v1 và mặc định nguồn VI. Đây là schema cho lát cắt đang chạy, chưa thay thế prepared Lesson Pack đầy đủ ở trên.

## Hiện trạng 1.0 RC1

`library.db` user_version=2 có `lessons`, `settings`, `glossary`, `lesson_revisions`. Lesson JSON chứa segments, support, questions và cấu hình level/layout; validator trong `content.py`, `library.py`, `pack.py`. Nội dung trợ giảng/câu hỏi có ID, nguồn concept, cặp VI/EN và review riêng. Sửa nguồn/đổi môn/tách/khôi phục làm review liên quan hết hiệu lực.

Lesson Pack thực tế giữ kind `biliclass-draft` để đọc tương thích, schema_version=3; nhận v1/v2/v3. Gói có manifest/hash, `lesson.json`, bản nguồn và WAV/metadata phù hợp. Review được đặt lại khi nhập; ID đoạn/trợ giảng/câu hỏi được ánh xạ sang bản sao. Không mang database lớp hoặc token. Giới hạn 100 MB nén, 200 MB mở rộng, 1.000 entry; export và import dùng cùng giới hạn.

`classroom.db` có `sessions`, `participants`, `rounds`, `answers`, `submissions`, `session_network`. Session giữ snapshot bài. Token tham gia/reconnect lưu digest. Round giữ trạng thái/deadline, ngôn ngữ, recheck và mẫu số khi đóng. Network lưu IP/cổng để mở lại cùng origin khi có thể; đổi mạng dùng QR mới và mã khôi phục của từng người.

Định nghĩa chỉ số thực thi: concept cần >=2 câu ban đầu và >=10 người để phân loại; 80%/60% là ngưỡng hiển thị. Gợi ý level chỉ xét >=2 cặp tương đương cùng concept do giáo viên gắn `comparison_group`, mỗi cặp cùng >=10 người và tham gia >=80%, không gồm recheck. Cả hai ngôn ngữ >=80% mới gợi ý tăng; Việt >=75% nhưng Anh <60% gợi ý giảm; ngoài ra giữ. Đây là heuristic thử nghiệm, không phải thang đo năng lực được thẩm định.
