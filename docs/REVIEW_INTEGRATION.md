# Tiếp nhận góp ý trước triển khai

29/09/2026. Nguồn nguyên bản: `refs/inputs/review-input.txt`. Người dùng yêu cầu tham khảo phần bổ sung và bắt đầu triển khai. Các nội dung được tích hợp như sau; không sao chép nhận định trong tài liệu thành lịch sử yêu cầu của người dùng.

| Nhóm góp ý | Cách áp dụng |
|---|---|
| Phạm vi cấp học | `education_level`, `grade`, `subject` là dữ liệu cấu hình. Người dùng trước đó trực tiếp ưu tiên THPT; tài liệu mới đề xuất THCS–THPT. Đã hỏi làm rõ, tạm giữ ưu tiên THPT nhưng không khóa engine ở lớp 10–12. |
| Gate M0 | Giữ bốn spike: PowerPoint/overlay, dịch/TTS CPU, LAN, Qt/QML/đóng gói. Tách kết quả kỹ thuật local khỏi kiểm thử thực địa chưa có thiết bị. |
| Pipeline | Import → Parse → Concept Model → Bilingual Engine → Lesson Intelligence → Teacher Review → Lesson Pack → Readiness Check. |
| Lesson Intelligence | Hợp đồng concept có explanation VI/EN, easy EN, examples, prompts, questions, rescue, vocabulary, quiz, misconceptions và audio scripts/cache refs. Nội dung chưa có không tự bịa. |
| Mascot | Action assistant theo ngữ cảnh bài; Milo/Lumi dùng chung năng lực, voice độc lập. |
| LevelPolicy | Quy tắc deterministic L0–L5 có test riêng; chọn loại nội dung, không dùng tỷ lệ EN. |
| Memory và glossary | Tối thiểu teacher + subject; UI thêm/sửa/xóa/khóa. CSV là bước mở rộng. |
| Duyệt bài | Trạng thái sản phẩm DRAFT → REVIEW_REQUIRED → READY_TO_TEACH; trạng thái job/cache quản lý riêng. |
| Readiness | Kiểm tra source, review, explanation, voice/cache; chỉ xét quiz/network nếu giáo viên dùng quiz. Warning cho phép teacher override có ghi nhận; file hỏng/đáp án không hợp lệ vẫn phải xử lý. |
| M2/M7 | M2 gồm PPTX, DOCX, PDF có text, TXT. M7 thêm ảnh/PDF scan OCR, tình huống nhập nâng cao và xuất deck song ngữ. |
| ResponseProvider | Analytics nhận normalized response có source; WebQuizProvider trước, BiliCard là extension sau V1. |
| Quiz | Không gửi đáp án trước reveal; giữ reconnect/idempotency/session/load tests. |
| Offline | Không cloud/API trả phí; tải gói benchmark là công việc chuẩn bị có chủ đích, app không tự tải khi dạy. |
| Máy tham chiếu | Hướng tới Windows 10/11 x64, CPU tương đương i5 thế hệ 8+, RAM 8 GB. Máy phát triển hiện đo được i7-8700, RAM 32 GB, Windows 10; không suy kết quả thành benchmark máy 8 GB. |
| Tiến độ | Bắt đầu M0; M1 chỉ sau khi ghi kết quả bốn spike và quyết định đi tiếp. Không tuyên bố mọi kiểm tra đã pass chỉ vì có source code. |

M0 có mã thử nghiệm chạy được trong `biliclass_m0/`. Đây là bộ kiểm chứng và giao diện workbench; không phải app sản phẩm đầy đủ hay mốc M1 đã hoàn thành.
