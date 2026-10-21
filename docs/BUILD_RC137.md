# RC137 — Hủy bài sạch trạng thái và Mascot theo lúc dạy

Bao gồm toàn bộ sửa thuật ngữ Hóa, lời đọc và nhãn số Toán của
RC136. Sau Hủy bài đang chọn trong màn chuyển đổi Google, tool
bỏ yêu cầu tạm dừng/lỗi khỏi tác vụ hiện tại, đặt tiến độ và đồng hồ
về 0, xóa thông báo lỗi và ẩn nút Tiếp tục cũ. Đổi sang một tệp hợp
lệ khác cũng bỏ tác vụ cũ; chọn lại luôn bắt đầu từ cấu hình mới.
Không xóa tệp nguồn, cache bản dịch, khóa API, hạn mức, bài đã lưu
hay WAV. Yêu cầu chưa lưu bị đánh dấu không tự tiếp tục khi mở app.
Nút Dừng trong lúc chạy vẫn giữ tác vụ để tiếp tục như trước.

Đối chiếu bên Tạo giọng: Hủy bài sau khi lỗi/dừng đưa phần chọn bài
về trạng thái rỗng, phát đủ tín hiệu cập nhật lời đọc và bản xem trước,
không giữ thông báo lỗi của bài trước. Giữ bài/plan/âm thanh trong
thư viện. Nếu đang tạo giọng, chờ dừng đoạn hiện tại rồi mới bỏ chọn.

Theo lựa chọn của người dùng, Mascot ẩn lúc khởi động. Lần đầu mở
bài giảng từ tool tự hiện; đã từng hiện hoặc chủ động mở trong phiên
thì các lần đổi/mở bài sau không tự bật lại. Nút Mở trợ giảng nổi
vẫn mở bất cứ lúc nào. Vị trí, kích thước và các tab Cài đặt giữ nguyên.

Xác minh trong `.venv`: 189 pytest đạt, gồm lưu/hủy tác vụ ở trạng thái dở và đã lưu,
Qt chuyển đổi chạy/dừng/tiếp tục rồi hủy/chọn lại, Qt tạo giọng lỗi rồi
hủy, Qt vòng đời Mascot và luồng Office thật. Kiểm tra dùng dữ liệu
thử; không xóa bài hay âm thanh của thầy cô.

Gói được dựng một lần từ `4475211b21142bb4d9f1a927348aa0303c7886cf`:
`BiliClass-RC137-Windows.zip`, 1.258.042.513 byte, SHA-256
`0fdd4d4ac5e0f7ddae4f3f25da732776a8fbd8841eb4dbef9b2f4f7d4ec4a789`.
55 QML khớp commit; bytecode UI, desktop, chuyển đổi Google, thuật
ngữ và giọng trong EXE khớp nguồn. ZIP và 4.675 tệp ứng dụng được
đối chiếu; smoke bản đóng gói ở hai màn chuyển đổi/tạo giọng đạt.

Cài tại `F:/Applications/BiliClass/1.0.0rc137`, mở qua Explorer độc
lập với Codex. Cửa sổ chính phản hồi, Mascot ẩn lúc khởi động,
shortcut Desktop/Start và icon/taskbar đúng phiên bản. Đối chiếu
trước/sau xác nhận bài, nguồn, 1.355 WAV, hồ sơ/logo, khóa API mã
hóa và tùy chọn giọng được giữ nguyên. Bỏ khỏi tác vụ chờ đúng
lượt Toán mà người dùng đã bấm Hủy; giữ nguồn và cache đã dịch.

Đã phát hành [v1.0.0rc137](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc137)
với ZIP và checksum riêng. Digest/size từ GitHub khớp gói đã kiểm tra.
