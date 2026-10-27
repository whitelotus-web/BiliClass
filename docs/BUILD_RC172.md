# BiliClass 1.0.0rc172

Mốc ngày 27/10/2026 trên `codex/word-format-preview-rc171`. Không sửa tag hoặc
thay asset RC155/RC167/RC169/RC170/RC171. Không đổi dependency, bộ giọng hoặc OCR.

- Thêm hàng đợi Word độc lập: nhiều file chỉ Dịch toàn bộ, cấu hình chung,
  xử lý tuần tự, tự lưu cạnh từng nguồn, dừng/tiếp tục/thử lại và giữ bảng kết quả.
  Xem [cách dùng và giới hạn](WORD_BATCH.md).
- Demo song ngữ ở cột phải cạnh Khối lớp và Đặt lại định dạng; nhãn ngoài
  khung, cùng cỡ/cùng hàng Khối lớp, đỉnh khung thẳng ô chọn lớp.
- Hủy bài không còn hiện mã HTML. Kiểm hủy/mở lại ở bôi đen, tích chọn,
  nền đọc sáng/tối; nguồn và thư viện được giữ.
- Nền đọc có icon trăng/mặt trời độc lập với theme tool; nhớ lần chọn
  gần nhất, không đổi nội dung hoặc định dạng file xuất.
- Dùng IShellLinkW và Known Folders cho Desktop/Start với đường dẫn có dấu.
  Chỉ sửa pin taskbar có đích BiliClass trong đúng gốc cài có marker; giữ
  pin/app khác và bản EXE cũ. Không tự ghim thêm chương trình.
- Cho chạy lại bộ cài vào phiên bản đã có nếu mọi hash khớp, chỉ hoàn tất
  marker/biểu tượng. Không chép đè tệp phiên bản đã sửa; không xóa thư viện.
  Lỗi auto-update hiện thông báo và đường dẫn install.log, tránh chỉ đóng im lặng.

Kiểm nguồn: bộ Word, hàng đợi Word và Qt một/nhiều file; hàng đợi PowerPoint
và giọng hiện có; installer Windows, shortcut Unicode, pin RC155 giả lập,
updater và gói cài. Kiểm luồng RC155 → RC171/RC172 và RC171 → RC172 bằng
bộ cài thử riêng. Các file/key/thư viện cá nhân và báo cáo không vào Git.

Runtime dựa trên manifest RC171 đã kiểm SHA-256; biên dịch lại toàn bộ module
ứng dụng. Trước công bố kiểm gói ZIP/manifest, cài/gỡ ở thư mục Unicode riêng,
shortcut từ EXE đóng gói trong thư mục giả lập, pipeline giọng Việt–Anh,
giao diện Word từ runtime đóng gói và dữ liệu thử được giữ khi gỡ.

Tham khảo API Windows: [IShellLinkW](https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nn-shobjidl_core-ishelllinkw),
[Known Folders](https://learn.microsoft.com/en-us/windows/win32/shell/known-folders).
