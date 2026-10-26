# BiliClass 1.0.0rc170

Mốc cập nhật Word ngày 26/10/2026, nhánh `codex/word-preview-rc170`.
Giữ nguyên tag và bộ cài RC167/RC169.

- Word có bản xem định dạng/ảnh/bảng, phóng to chọn nội dung, vùng đọc cao
  theo cửa sổ và cuộn lồng nhau. Font/Size gốc hoặc tùy chỉnh, tô sáng chữ,
  các nút định dạng gọn. Cấu hình chia trái/phải, chọn/hủy bài dưới hướng dẫn
  thống nhất với PowerPoint và tạo giọng đọc.
- Sửa điểm nghẽn chọn font: danh sách hệ thống được lấy một lần, truyền bản
  sao cho QML thay vì đọc lại hàng nghìn lần. Chọn vùng không dựng lại tài
  liệu hiển thị hoặc trả lại toàn bộ đoạn từ gói Word mỗi lần.
- Dấu xanh vùng chọn chỉ thuộc bộ hiển thị. Vùng chồng nhau được gộp, giữ
  thứ tự nguồn; đoạn liền nhau hiển thị thành một nhóm. Bấm nhóm tìm lại
  vị trí nguồn. Dịch toàn bộ có khóa thao tác chọn riêng và khôi phục vùng
  thủ công khi bỏ tích, chưa gửi dịch trước khi bấm chuyển đổi.
- File nguồn không được ghi đè. Bản kết quả vẫn lưu cạnh nguồn với hậu tố
  `(Song ngu VI-EN)`; kiểm thử giữ nguyên font/định dạng/nội dung phần không
  được chọn, ảnh và cấu trúc Word. Bản xem không cam kết phân trang giống
  Microsoft Word cho mọi đối tượng nổi, công thức hoặc SmartArt.

Nguồn được kiểm bằng `.venv`: kiểm thử Word/xuất/định dạng/vùng chọn,
Qt Word ở màn hình laptop và desktop sáng/tối, kiểm bố cục PowerPoint và
giọng đọc với một/nhiều file, không dùng API thật hay dữ liệu cá nhân trong
fixture. Bộ dựng phải kiểm hash runtime RC169, biên dịch lại toàn bộ module
app và lấy QML/tài nguyên hiện tại, không thay dependency/model trong mốc này.

Trước công bố, gói Windows phải qua kiểm SHA-256/manifest/ZIP, cài trong
thư mục kiểm thử riêng, chạy Qt và pipeline giọng Việt–Anh từ runtime đã
cài; kiểm updater từ RC167 và RC169 nhận đúng RC170. Mã nguồn, commit,
hash bộ cài và ZIP được ghi trong BUILD_INFO/SHA256 của thư mục bàn giao.
Thư viện, cấu hình/key dịch và tài liệu cá nhân không nằm trong bộ cài.

Việc phát hiện file nguồn được sửa trong Office và cập nhật lại vùng chọn
mới là đề xuất; RC170 không âm thầm thay nguồn hoặc tự sửa tài liệu.
