# Mẫu PowerPoint Universal 2026 — RC47

Trong **Tạo bài giảng → Tạo theo mẫu mới**, ba lựa chọn Chuẩn lớp học, Trực quan
và Luyện tập & tương tác dùng bộ PPTX Universal 2026 do giáo viên cung cấp.
Mỗi phong cách có 23 bố cục. Tool sao chép bố cục phù hợp rồi điền nội dung;
không xuất nguyên 23 trang mẫu và không lấy placeholder làm kiến thức bài học.
Nút **Xem PowerPoint mẫu** tạo bài minh hoạ bằng cùng engine với bài thực tế.
Các lần xem lại dùng bản mẫu đã tạo nếu tệp và cấu hình vẫn khớp hash.

## Luồng xử lý

1. Giữ bản sao nguồn và đúng bộ mẫu của lượt chuyển đổi, kèm SHA-256 và ánh xạ
   layout trong cấu hình. Tiếp tục lượt cũ không âm thầm thay mẫu sau cập nhật.
2. Chỉ gửi phần chữ cần dịch tới Google Translation như trước. Bảng dùng từng
   ô riêng; các dòng câu hỏi/đáp án có mã riêng. Công thức trung lập ngôn ngữ
   và số thứ tự không gửi dịch. Không dùng ChatGPT/Gemini web.
3. Dàn trang tại máy, giữ ranh giới slide nguồn. Tự chọn bố cục theo tiêu đề,
   đoạn lý thuyết, mục tiêu, quy trình, so sánh, hình, công thức, bảng, hoạt
   động nhóm, bài tập, câu hỏi hoặc tóm tắt. Chỉ dùng quiz bốn đáp án khi nguồn
   có đủ bốn lựa chọn và vừa khung; không đoán đáp án đúng. Lời giải chỉ được
   phân loại khi nguồn ghi rõ. Các trường hợp thiếu cấu trúc dùng khung chữ
   tổng quát, giữ đủ nội dung.
4. Việt–Anh nằm cùng trang. Tiêu đề Việt trên, Anh nghiêng phía dưới. Phần thân
   chọn cột hoặc khung xếp dọc theo diện tích; đoạn dài dùng khung rộng và trang
   tiếp nối. Tiếng Anh 100% loại bỏ ô Việt và dịch các nhãn thiết kế có sẵn.
5. Giữ ảnh, công thức native và biểu đồ chỉnh sửa được; giữ bảng native và phân
   trang theo hàng nếu dài. Hình nguồn gắn với nhóm nội dung của slide đó thay
   vì dồn thành phụ lục cuối bài. Nhiều công thức có thể cần trang tiếp nối.
   Speaker Notes có một cặp VI:/EN: riêng cho nội dung mỗi trang, dùng cho bước
   tạo giọng đọc sau đó.
6. Ghi sơ đồ layout riêng trong thư mục công việc và chạy kiểm tra/hiệu chỉnh
   PowerPoint hiện có trước khi lưu vào thư viện. Ghi nhận CHECK cần đối chiếu,
   không đổi thành PASS chỉ vì tệp mở được.

**Thêm bìa và trang kết thúc** mặc định tắt, giáo viên có thể bật. Số slide vẫn
có thể tăng khi nội dung dài; phiên bản này không có cam kết giữ nguyên số
slide trong chế độ mẫu mới. Chế độ **Giữ thiết kế PowerPoint gốc**, mẫu riêng
BCL_TITLE/BCL_CONTENT, và lượt chuyển đổi RC45–46 giữ renderer tương thích.

## Giới hạn cần hiểu đúng

- 23 bố cục là vật liệu thiết kế; không phải mọi bài đều có đủ dữ liệu để dùng
  mọi bố cục. Giao diện giữ hai lựa chọn ngôn ngữ hiện tại. Không thêm chế độ
  tự trích thuật ngữ KEYWORDS chỉ vì manifest có trang mẫu này.
- Không tự tạo kiến thức, lời giải, thời gian hoạt động hay trang reveal.
  Quiz là bố cục trình bày; chưa có trigger/nút tương tác trong file xuất.
- Mẫu mới không bảo toàn hoạt ảnh, video, OLE hoặc tương tác của file gốc.
  Chữ trong ảnh, nhãn biểu đồ, sơ đồ phức tạp và công thức lẫn văn xuôi vẫn cần
  đối chiếu. Không bảo đảm dịch được toàn bộ hình hoặc tài liệu bất kỳ.
- Một ô bảng quá dài không thể vừa trang sẽ có thông báo rõ để tách ô; không
  cắt bỏ nội dung. Kiểm tra hình học không thay cho kiểm duyệt kiến thức.
- Arial thay Aptos khi điền mẫu để tránh lỗi glyph nghiêng trên Office 2019.
  Trang trí, màu sắc, master và các đối tượng nền vẫn theo thiết kế đã cung cấp.

## Cập nhật trên máy khác

Lấy commit RC47 trên `main` bằng quy trình cập nhật Git đang dùng. Nếu có thay
đổi cục bộ, lưu/commit chúng trước rồi cập nhật; không dùng reset/clean cưỡng ép.
Ba PPTX và manifest nằm trong `app/assets/templates/universal2026` và được đưa
vào Git cùng mã nguồn. Script build hiện có đóng gói cả `app/assets`, vì vậy máy
khác không cần bộ ZIP trong Downloads hoặc đường dẫn tuyệt đối của máy này.

Chạy nguồn bằng môi trường dự án hoặc build lại bản ứng dụng bằng quy trình của
máy đó. `git pull` không tự thay EXE đang cài. Dữ liệu bài giảng, model, API key,
file chạy và báo cáo kiểm thử không nằm trong commit.

## Kiểm chứng

Kiểm thử tự động: `tests/test_universal_templates.py` và các bài kiểm thử Google
conversion, mẫu riêng, giữ thiết kế, cấu hình đầu vào và template rules.
Tổng cộng 126 kiểm thử liên quan đã qua bằng môi trường ảo dự án.
Kiểm tra Qt: `scripts/qt_universal_templates_smoke.py` kiểm tra ba lựa chọn,
hai ngôn ngữ, nút xem mẫu thật, lưu tuỳ chọn bìa và hai cỡ cửa sổ; kiểm tra kết
quả/mascot hiện có tiếp tục chạy. Không gửi tài liệu cá nhân hay gọi API thật.

Đã render cả 69 trang mẫu đầu vào bằng Microsoft PowerPoint. Bản kiểm tra mẫu
ngắn và nhóm có hình/bảng dài/công thức/biểu đồ được đo tràn chữ và render lại
bằng Office, không còn lỗi FAIL trên các bản kiểm tra này. CHECK về cỡ nhãn
trang trí, công thức và đối chiếu hình vẫn được giữ. Chi phí dựng bố cục thử
nghiệm khoảng 0,1–0,4 giây/bài nhỏ, chưa gồm dịch,
OCR hoặc mở/kiểm tra Office; không phải cam kết thời gian cho mọi bài.
