# RC146 — Tự lưu PowerPoint có giọng và hiện loa sớm

Sau khi tạo đủ giọng đã chọn, ứng dụng tự xuất PowerPoint có âm thanh
nhúng cạnh file đầu vào đã ghi nhớ. File gốc, bài trong thư viện và WAV
giữ nguyên. Nếu thư mục cũ không còn hoặc không ghi được, bản xuất nằm
trong thư mục `exports` của dữ liệu BiliClass; giao diện báo rõ đường
dẫn và có **Mở thư mục**. Nút **Tải PowerPoint có giọng** vẫn mở hộp
chọn nơi lưu như trước.

Việc xuất chạy nền, kiểm lại revision, bản giọng, nguồn và WAV trước
khi ghi. Chỉ bản đủ giọng được xuất; bài đã xóa hoặc chỉnh sửa không
nhận bản xuất cũ. Công bố file bằng thao tác không ghi đè: tên đã có
được giữ, kể cả file xuất mà giáo viên sửa bằng PowerPoint. Thông báo
hoàn tất lặp lại không tạo thêm bản nếu nội dung đầu ra và âm thanh
không đổi. Thay WAV hoặc sửa bản xuất tạo tên mới. Chưa triển khai
đồng bộ các sửa tay ngoài PowerPoint về nội dung quản lý trong tool.

Loa trên slide được vẽ trước khi hỏi trạng thái hiệu ứng và khởi tạo
trình phát của Office. Nhờ đó, chuẩn bị media chậm không còn chặn bước
vẽ đầu tiên. Các lệnh Office bị từ chối tạm thời có thử lại có giới hạn
2,5 giây; lỗi khác không bị nuốt hoặc lặp vô hạn. Thông báo lỗi mở/
điều khiển PowerPoint dùng tiếng Việt, chi tiết kỹ thuật giữ trong log.
Không chứng nhận xử lý được mọi hộp thoại/lỗi Office.

81 pytest nhóm xuất file, Office, loa và quản lý bài đạt; nhóm giọng/
phiên dạy có 73 ca đạt (có giao nhau). Qt tự lưu kiểm file nhúng ba loa,
nguồn/WAV không đổi, không cần bấm Tải, không lặp bản xuất, nút mở thư
mục và hộp Lưu như cũ; sáng/tối ở 1080 và 1366 px, không cảnh báo QML.
Qt kết quả giọng hiện có tiếp tục đạt ở ba kích thước, cả Anh và Việt.
411 ca portable và corpus cấu trúc tại máy đạt; Ruff toàn kho và
compileall đạt. Các số nhóm kiểm thử có giao nhau, không cộng thành
một số kiểm thử độc lập.

Qt với PowerPoint thật trên fixture riêng: loa hiện 0,157 giây sau
khi quan sát được cửa sổ trình chiếu; chuyển slide hai loa → im lặng
→ một loa → im lặng đúng. Không gửi chuột/phím toàn hệ thống. Phép đo
kiểm soát riêng trên bản sao bài 16 slide, cố ý trì hoãn Player 3 giây:
vẽ đầu tiên sau Run giảm từ 4,390 xuống 1,094 giây. Đây là thí nghiệm
có trì hoãn, không phải cam kết tốc độ trên mọi máy/bài.

Giữ bốn tab Cài đặt. Không thêm hàng đợi hoặc chạy đồng thời; không
thay đổi cách đọc file độc lập ngoài tool/Mascot theo yêu cầu người dùng.
Tự lưu mới áp dụng sau tạo giọng, không tuyên bố đồng bộ file bên ngoài
hay chứng nhận toàn bộ nghĩa dịch, OCR, công thức và bố cục.
