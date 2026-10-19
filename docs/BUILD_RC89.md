# RC89 — Gọn đầu trang

Bỏ hàng đầu trang cao 70 px trong vùng nội dung. “ANH ↔ VIỆT” và “Lưu
trên máy” chuyển thành thông tin trên thanh tiêu đề Windows, cùng tên và
phiên bản ứng dụng. Giữ thanh tiêu đề/nút thu nhỏ, phóng to và đóng chuẩn
của Windows. Áp dụng chung Trang chủ, chuyển đổi, tạo giọng, thư viện,
lớp học và cài đặt. Nút về bản trình chiếu của màn sửa chuyển vào phần
thông tin bài, không mất thao tác quay lại.

Bao gồm toàn bộ thay đổi [RC88](BUILD_RC88.md), cả sửa Hủy bài đang chọn
khi PowerPoint đang mở nhưng chưa trình chiếu. Source RC88 `29906d6`
có CI đạt. Gói RC88 đã build/kiểm hash ZIP cục bộ làm nền runtime cho RC89;
chưa công bố hoặc cài gói này cho giáo viên. RC89 biên dịch lại toàn bộ
mã ứng dụng và QML hiện tại từ commit đã kiểm tra, giữ model/dependency
đã được xác minh bằng manifest.

Qt kiểm tra nội dung bắt đầu từ mép trên ở cả sáu trang chính, thông tin
trên tiêu đề và ba cụm tính năng Trang chủ căn giữa. Kiểm tra lại màn xem
bài giảng ở ba cỡ cửa sổ, đủ trạng thái ngôn ngữ, và cấu hình chuyển đổi ở
bốn cỡ cửa sổ. Không có cảnh báo QML. Các báo cáo/ảnh và dữ liệu cá nhân
chỉ lưu cục bộ, không commit.
