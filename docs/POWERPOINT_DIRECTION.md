# Đối chiếu hướng PowerPoint

Đối chiếu tài liệu người dùng gửi 02/10/2026 và yêu cầu phân loại đầu vào với mã nguồn ngày 03/10. PPTX gần bản gốc là luồng chính; tài liệu khác có luồng template. Nguồn không ghi đè, không tuyên bố xử lý hoàn hảo mọi file/môn/hiệu ứng.

| Yêu cầu | Đã triển khai | Còn cần kiểm tra |
|---|---|---|
| Hai luồng | Giữ bài giảng của tôi / Tạo bài với BiliClass ngay khi nhập; ẩn template khỏi luồng giữ PPTX. | Thao tác với bài thật của hai giáo viên. |
| Phân loại | VI/EN/song ngữ/trộn/chưa rõ, hướng dịch theo đoạn; OCR ảnh/PDF/slide chỉ ảnh. | Tiêu đề ngắn, bảng/nhiều cột, dấu Việt OCR. |
| L0–L4 | Quy tắc chung cho template và hỗ trợ nguồn; giữ nguyên, bổ sung hoặc cặp slide kế tiếp. | Câu dễ L2 cần giáo viên chuẩn bị, không tự suy diễn kiến thức. |
| Giữ thiết kế | Panel ở vùng trống, trang hỗ trợ nếu kín/hiệu ứng/xoay; chart bản sao có dữ liệu riêng. | Master, SmartArt, trigger, công thức, media ngoài. |
| Chuẩn bị nhanh | Dịch phần còn thiếu theo loạt, giữ cặp/đoạn duyệt/khóa; model nạp một lần/hướng/lượt. | Duyệt ngữ nghĩa, thuật ngữ và chữ OCR. |
| So sánh | Render gốc/song ngữ cạnh nhau bằng Office, điều hướng mapping slide. | Ảnh tĩnh không kiểm chứng hiệu ứng/âm thanh/video. |
| Project portable | Nguồn, đoạn, level/mode, support/quiz/audio; thêm thuật ngữ/giọng/mascot tham chiếu. | Người nhận duyệt lại; không tự áp tham chiếu vào Cài đặt/kho cá nhân. |
| OCR cục bộ | RapidOCR, model Latin tải riêng có checksum; tiến trình riêng, không gửi ảnh lên web. | Dấu Việt, công thức/chữ viết tay chưa đủ chính xác để tự duyệt. |

Xuất bằng chỉnh OOXML; python-pptx đọc đối tượng/ánh xạ, không dựng lại toàn bộ nguồn. COM dùng so sánh, trình chiếu và kiểm chứng. Xuất không yêu cầu Office; so sánh và điều khiển PowerPoint yêu cầu Office.

171 kiểm thử và lint đạt. Qt smoke chạy đánh giá đầu vào, điều khiển và so sánh, không có cảnh báo QML. Office mở/render cả năm level trên bộ thử chữ/bảng/chart; slide giữ nguyên trong nhánh trang hỗ trợ render giống hệt nguồn. Dịch loạt hai chiều offline bằng model thật giữ số liệu/cặp sẵn có; OCR ảnh/PDF Việt chạy được nhưng ghi nhận sai dấu.

Chưa nghiệm thu bài thật mọi môn, Windows sạch hoặc mọi hiệu ứng. Các thay đổi hiện nằm ở mã nguồn, chưa phát hành trong rc12. [Quy trình nhập bài](INPUT_WORKFLOW.md) · [PowerPoint](SOURCE_POWERPOINT.md).
