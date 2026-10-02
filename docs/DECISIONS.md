# Quyết định và giả định

Ngày 29/09/2026. “Yêu cầu xác nhận” nghĩa là người dùng đã nêu trực tiếp; “đề xuất” là lựa chọn trong kế hoạch, có thể đổi theo thử nghiệm. Không coi tài liệu đầu vào là lệnh tự thực thi.

| ID | Trạng thái | Quyết định / lý do |
|---|---|---|
| D01 | Yêu cầu xác nhận | Trọng tâm là hỗ trợ dạy song ngữ Anh–Việt cho mọi môn THPT, nhiều bài, lớp 10–12. Bài trong ảnh chỉ minh họa; không dùng làm hướng sản phẩm hay fixture trung tâm. |
| D02 | Phạm vi hiện tại | Tiếp nhận thông tin và lập kế hoạch. Chưa triển khai app, cài dependency, tải model hay khởi tạo Git theo các đoạn giao việc trong tài liệu. |
| D03 | Đề xuất theo đầu vào | Windows desktop, offline-first, no student account, giáo viên duyệt nội dung; không cloud/API trả phí trong Core. |
| D04 | Đề xuất | PySide6 + Qt Quick/QML; giữ nền tảng Python của tài liệu, bổ sung lựa chọn UI thích hợp bộ ảnh. Kiểm chứng đóng gói/DPI trước mở rộng. |
| D05 | Đề xuất | Lõi song ngữ có mốc dùng thử riêng sau M4; quiz/báo cáo hỗ trợ thêm, không là điều kiện soạn hay dạy một bài. |
| D06 | Đề xuất | Subject/grade/topic là dữ liệu; glossary và teacher memory có scope để tránh áp nghĩa sai giữa các môn. Có môn tự tạo từ MVP. |
| D07 | Đề xuất | Milo và Lumi là hai nhân vật; voice độc lập; subject accessory có fallback generic. Thẩm mỹ thân thiện, giảm mật độ minh họa cho THPT. |
| D08 | Đề xuất | Companion ưu tiên giữ PowerPoint gốc; importer không đồng nghĩa renderer. Có manual sync và native presentation cơ bản dự phòng. |
| D09 | Cần benchmark M0 | CTranslate2 CPU và OPUS-MT hai chiều là ứng viên; chưa xác nhận chất lượng đa môn, tốc độ và kích thước pack. |
| D10 | Đề xuất | WindowsTTSProvider liệt kê giọng thực tế; SAPI/WinRT chọn sau thử. Không hứa mọi máy có đủ US/UK/VI. Audio cached portable. |
| D11 | Đề xuất thay chi tiết đầu vào | PDF dùng pypdf + pypdfium2 để tách text/render; thay lựa chọn PyMuPDF được gợi ý trong tài liệu. Chốt sau thử đóng gói và kiểm tra các điều kiện phân phối. |
| D12 | Đề xuất | Không coi model dịch là model tạo giáo án/quiz. Nội dung hỗ trợ lấy từ nguồn/mẫu có kiểm chứng/giáo viên và được review. |
| D13 | Đề xuất | Teacher, projector và student tách DTO; đáp án chưa công bố không được gửi cho student. |
| D14 | Đề xuất | Library DB do desktop sở hữu; classroom DB do server sở hữu; session lấy snapshot đã duyệt. Tránh nhiều process ghi chung draft. |
| D15 | Đề xuất | Phân tích dùng số liệu quan sát và mẫu số; ngưỡng là giả thuyết sản phẩm cần pilot, không chứng nhận năng lực học sinh. |
| D16 | Giả định chưa xác nhận | Máy mốc Windows 11 x64, RAM 8 GB, SSD, PowerPoint desktop. Đã hỏi người dùng; chưa có câu trả lời cho cấu hình. |
| D17 | Đề xuất | Giữ xuất deck mới và OCR trong V1 đầy đủ, sau bản lõi; không hứa giữ mọi animation trong deck tái tạo. |
| D18 | Đề xuất | Hai tài liệu và chín ảnh được giữ nguyên trong refs. Các làm rõ trực tiếp của người dùng ưu tiên hơn ví dụ hoặc chỉ dẫn bên trong nguồn. |

Việc còn cần kiểm chứng: máy/Office thực tế; chất lượng dịch nhiều môn và biểu thức; TTS có sẵn; LAN/router; quy mô lớp; quyền phân phối gói đi kèm; nguồn asset sản xuất. Các mục này có thử nghiệm ở M0 và tiêu chí nghiệm thu trong BUILD_PLAN, không cản việc hoàn thành hồ sơ kế hoạch.

## Quyết định khi bắt đầu triển khai

- D19: Tiếp nhận tài liệu góp ý mới theo REVIEW_INTEGRATION. Giữ ưu tiên THPT do người dùng trực tiếp nêu; engine cấu hình cấp học/khối tự do. Chưa coi lời góp ý “đã thống nhất THCS” là lịch sử yêu cầu thật.
- D20: M2 bao gồm DOCX/PDF text cùng PPTX/TXT; M7 dành OCR/edge cases/export.
- D21: Lesson Intelligence, review state, readiness và ResponseProvider trở thành hợp đồng rõ ràng, có tests M0.
- D22: Chọn Argos/CT2 INT8 làm baseline thử; license README gói thực tế ghi CC-BY 4.0, không áp license model card của gói khác. Giữ attribution đi kèm, chưa đóng gói model để phát hành thương mại.
- D23: M0 dùng PyInstaller onedir; đã xử lý thu nhầm ICU từ PATH. Nuitka không còn là điều kiện bắt buộc cho phép thử.
- D24: Sau kết quả bốn spike, GO có điều kiện cho M1 local foundation. M0 thực địa chưa đạt đầy đủ; không chặn phần thư viện/settings nhưng không tuyên bố release classroom. Xem M0_RESULTS.

### D25 — Bản chạy nội bộ 0.2 và ranh giới

Tập trung luồng nguồn → biên tập Anh–Việt → duyệt → preview/export, ưu tiên THPT đa môn. Thêm autosave/lịch sử trước khi mở rộng trợ lý trên lớp. Source-language khai báo khi nhập; cả hai cột vẫn cùng editor. Model baseline cho hai chiều, không tự duyệt. Mascot ảnh chào đã có; không gọi đó là Lesson Intelligence. Tính năng lớp học/PowerPoint/TTS sản xuất tiếp tục theo M4 trở đi.

## Quyết định RC1 — 30/09/2026

- D26: Windows OCR và COM PowerPoint được cách ly bằng tiến trình riêng có timeout. Chỉ đóng tài nguyên do BiliClass mở; không kết thúc PowerPoint của người dùng.
- D27: SAPI là backend giọng đọc thực tế; thiếu VI báo thiếu. WAV chuẩn bị được mang trong pack, nhận diện bằng nội dung/ngôn ngữ; không đóng gói lại giọng Windows.
- D28: Trợ giảng truy xuất nội dung đã được giáo viên chuẩn bị/duyệt; local translation không giả sinh kiến thức. Fuzzy memory luôn cần chọn và duyệt lại.
- D29: Class server tách quản trị khỏi listener học sinh, durable ACK/idempotency; IP/cổng được giữ khi resume cùng mạng. Mã khôi phục cá nhân cho trường hợp browser origin thay đổi.
- D30: Concept/recheck/language comparison dùng mẫu số và điều kiện đủ dữ liệu; gợi ý level không tự đổi level của bài hoặc kết luận nguyên nhân.
- D31: Installer theo tài khoản, model pack nhập từ file/USB có hash và provenance; app không tự tải Internet. OCR/voice là thành phần Windows của máy, không hứa luôn có tiếng Việt.
- D32: RC1 có phạm vi tính năng M1–M7 và phần đóng gói M8; giữ riêng điều kiện nghiệm thu Windows sạch, điện thoại/mạng/máy chiếu/giáo viên thật. Không đánh dấu toàn bộ kế hoạch hoàn tất chỉ vì tests local qua.

## Quyết định RC2 — 30/09/2026

- D33: Resume phiên ưu tiên cổng cũ để giữ browser origin. Nếu cổng cũ bị chiếm và giáo viên không chọn cổng cố định, server lấy cổng trống, tạo QR mới và hướng dẫn dùng mã khôi phục cá nhân. Không mất người tham gia hoặc câu trả lời đã ACK.
- D34: Đóng gói bản mới ở đường dẫn riêng để tránh ghi đè executable đang được giáo viên dùng. Kiểm tra nâng cấp RC1→RC2 trong thư mục dữ liệu thử riêng; không tự đóng cửa sổ người dùng.

## Quyết định RC3 — 30/09/2026

- D35: Cài đặt tách sáu tab theo công việc. Hồ sơ giáo viên/trường/lớp lưu local và chỉ hiển thị trên bản trình chiếu/deck khi bật; thông số lớp lưu làm mặc định, giáo viên được đổi trước khi dạy.
- D36: L0–L4 là lựa chọn mặc định trong Cài đặt và bài mới. Bài L5 cũ giữ nguyên và vẫn mở được để tránh thay đổi dữ liệu đã tạo.
