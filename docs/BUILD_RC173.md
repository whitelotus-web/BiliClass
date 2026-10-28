# BiliClass RC173 — 28/10/2026

Sửa lỗi quan sát trên máy đang chạy RC155: log `install.log` dừng vì tiến
trình phiên bản cũ chưa thoát. Không phải lỗi tải gói hoặc mất thư viện.

- Ứng dụng mới chỉ bàn giao cho bộ cài sau khi đóng thư viện và các worker.
- Bộ cài đặt bản mới cạnh bản cũ, kiểm hash và cập nhật shortcut trước khi
  chờ tiến trình cũ. Một worker RC155 còn chạy không hủy việc cài đã tải xong.
  Nếu bản cũ vẫn chưa thoát sau khoảng chờ, báo rõ bản mới đã cài và cách mở;
  không ép tắt tiến trình đang dùng, không ghi đè thư viện hoặc file cũ.
- Word không chuyển toàn bộ danh sách đoạn/câu qua QML mỗi lần đổi trạng
  thái. Dùng lại phần DOCX đã phân tích cho dữ liệu chọn và bản xem trước.
- Bản xem chỉ khởi tạo bộ đọc ảnh raster hỗ trợ, tra style bằng bảng chỉ mục
  và không quét toàn văn bản khi chưa có vùng chọn. Không sửa DOCX gốc.
- Bỏ hai nhãn ANH↔VIỆT và Lưu trên máy ở thanh tiêu đề theo yêu cầu.

Đo cục bộ với file Word 447 đoạn đã dùng trong dự án: tải/hiện khoảng 0,9–1,5
giây sau khi môi trường sẵn sàng; khoảng gián đoạn vòng GUI lớn nhất 0,25–0,33
giây, không có cảnh báo QML, hash nguồn không đổi. Đây là một file và máy hiện
tại, không cam kết thời gian cho mọi kích thước tài liệu hoặc ổ đĩa.

Kiểm Word một/nhiều file, định dạng/chọn vùng, giao diện Home/caption, installer
Windows với tiến trình cũ còn sống và handoff sau khi đóng cơ sở dữ liệu.
Model/dependency giữ từ RC172 đã xác minh; tất cả mã ứng dụng được dựng lại.
Bộ cài RC173 là release mới, không sửa tag hoặc asset RC172/RC167.
