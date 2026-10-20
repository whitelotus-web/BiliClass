# RC116 — Bố cục gọn, xem trước trực quan và lưu cạnh file gốc

Tab Chung bỏ thẻ “Xem trước hồ sơ” trùng thông tin thanh bên. Form thầy cô
và phần chọn giao diện đặt cạnh nhau trên cửa sổ rộng, tự xếp dọc khi hẹp;
hai lựa chọn sáng/tối co theo vùng hiển thị. Các tab hiện có được giữ nguyên.

Logo có trạng thái rõ ràng: chưa có thì hiện nút tải; có rồi thì hiện ảnh
đang dùng, trạng thái đã lưu và hai nút thay/bỏ. Dùng chung cách hiển thị
logo với thanh bên. Bỏ ô chọn hiển thị hồ sơ trên bài giảng vì không áp dụng
cho luồng chuyển PowerPoint giữ thiết kế gốc. Lưu thông tin vẫn giữ giá trị
cấu hình chế độ xem cũ; không tự bật/tắt hay chèn hồ sơ vào PowerPoint.

Tab Giọng đọc đặt nghe cả cặp, dừng nghe, lưu và trạng thái trong cùng thẻ
với cấu hình, ngay dưới tốc độ đọc. Phóng to cửa sổ không kéo các nút xuống
đáy trang; trên cửa sổ thấp có thể cuộn tới các nút. Giữ nguyên lựa chọn,
lời nghe thử, cơ chế lưu giọng và bản thu cũ.

Thông tin BiliClass căn giữa theo một cột: thương hiệu, Copyright, phiên bản,
kiểm tra cập nhật. Nội dung dài tự xuống dòng.

Tab Mascot giới hạn nội dung 1.180 px và căn giữa khi phóng to. Các nhóm
phím đọc và phím di chuyển có khoảng cách cố định, không giãn theo cửa sổ.
Thanh tiêu đề dùng một lớp chữ Segoe UI thường, vẽ ở tọa độ pixel nguyên;
không chồng lớp chữ tiêu đề của nền tảng. Giữ khung, menu hệ thống, phím
thu/phóng/đóng, AppUserModelID và biểu tượng Windows.

Thư viện dành cùng độ rộng cho nhãn trạng thái, ngày tạo và nút mở. Ngày
tạo thẳng cột khi trạng thái hay độ dài tên bài khác nhau. Giữ chọn nhiều,
kéo chọn, bộ lọc và bố cục cửa sổ hẹp.

Màn tạo giọng ghép thông tin bài và nút mở/tải với ảnh thu nhỏ 16:9 ở bên
phải. Hết hàng trống chỉ dành cho ảnh. Loa demo EN/VI/hai loa theo lựa chọn
ngôn ngữ và vị trí trái/giữa/phải dưới, cả ảnh nhỏ lẫn ảnh phóng to. Dùng
ảnh loa và khung cắt của bản xuất; không tạo audio hay sửa PowerPoint khi
đổi demo. Giữ một dòng quy trình; bỏ hướng dẫn trùng dưới ô chọn bài.

Màn chuyển đổi sau khi chọn PowerPoint thu gọn khối tải lên thành trạng
thái đã chọn, nút chọn bài khác/bỏ tệp và ảnh slide gốc. Xem trước chạy ở
worker, render bản sao riêng bằng PowerPoint; có thể hủy khi đổi/bỏ file,
bỏ qua kết quả cũ đến muộn và không chặn bước chọn cấu hình. Mọi ô lựa
chọn chuyển đổi/thiết kế/mẫu có viền mảnh ngay cả khi chưa chọn. Nút xem
mẫu mở ảnh PNG trong ứng dụng; không khởi chạy file mẫu PowerPoint.

Ô “Cấu hình đã chọn” của chuyển đổi và tạo giọng nằm trong thanh cố định,
cạnh nút thực hiện. Cuộn nội dung không làm ô này trôi đi; nội dung tự
xuống dòng theo độ rộng, thanh tự tăng chiều cao và vùng cuộn chừa chỗ.
Thông tin giọng/ngôn ngữ/tốc độ/vị trí loa cập nhật ngay theo lựa chọn.

Các hộp mở/lưu/chọn thư mục dùng hộp thoại Windows ở cả hai chế độ màu.
Gợi ý lưu một bài ưu tiên thư mục và tên file gốc đã tải lên; giữ hậu tố
ngôn ngữ/giọng, thêm số khi trùng để không ghi đè nguồn. Đường dẫn chỉ lưu
trong cấu hình cục bộ, tách khỏi nội dung bài và gói chia sẻ; liên kết theo
bài để lần nhập khác không đổi thư mục của bản cũ. Bài cũ chưa có đường
dẫn hoặc thư mục không truy cập được dùng vị trí tải dự phòng. Lưu nhiều
bài ZIP tiếp tục dùng thư mục tải chung.

Kiểm tra nguồn: 66 ca liên quan nhập/chuyển đổi, đường dẫn lưu, giọng,
nghe thử và tùy chọn thư viện đạt; Ruff và kiểm tra khoảng trắng đạt.
Qt kiểm tra lưu cấu hình giọng và bảo toàn bản thu cũ đạt. Qt Cài đặt dùng
font thật ở 1080/1366/1920, sáng/tối, DPI 100% và 150%; kiểm tra hình học,
nút trong thẻ và khả năng cuộn, trạng thái tải/thay/bỏ logo, lưu hồ sơ,
sao lưu/khôi phục thư viện tạm. Qt chuyển đổi kiểm tra 48 cấu hình bố cục
ở mỗi mức DPI, gồm ô tóm tắt cố định khi cuộn. Qt theme kiểm tra thumbnail,
9 tổ hợp loa/ngôn ngữ/vị trí, ảnh mẫu và bảng Mascot 60–160 px; Qt thư viện
kiểm tra ngày tạo thẳng cột, chọn nhiều/kéo chọn và lọc. Hộp mở/lưu Windows
thật kiểm tra tên Unicode có dấu #, hủy không mất lựa chọn, thư mục lưu
đúng và SHA256 file gốc không đổi. Qt màn hoàn tất giọng và thao tác quay
lại cấu hình đạt. Khung Windows kiểm tra chữ tiêu đề một lớp sáng/tối,
DPI 100%/150%, thu/phóng/khôi phục và biểu tượng cửa sổ/taskbar đạt.
Không dùng thư viện cá nhân cho các phép thử chức năng.

Bản phát hành dùng nguồn `c955ef45f6e06eae70a97fdfcaf0217cff3afd50`,
runtime/model RC115 đã đối chiếu SHA256; biên dịch lại toàn bộ module app.
Gói có 4.660 tệp ứng dụng, 52 tệp QML/qmldir khớp nguồn; ZIP đã đối chiếu
từng tệp và digest GitHub sau tải lên. Bản đóng gói mở Cài đặt 1366×850
với thư viện tạm, không có cảnh báo QML.

- Phát hành: https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc116
- ZIP: `BiliClass-RC116-Windows.zip`, 1.249.981.021 byte.
- SHA256: `ea403cf0527d913e452ea20f5ba8a7d019d3af4cc0a00cf1542bd8056d7b16dc`.
- Cài tại `F:/Applications/BiliClass/1.0.0rc116`; đóng RC115 bình thường,
  mở RC116 qua Explorer độc lập với phiên agent. Cửa sổ chính và Mascot
  đáp ứng, icon/taskbar và shortcut trỏ đúng bản mới.
- Đối chiếu trước/sau: 18 bản ghi bài, nguồn bài, 1.658 WAV tham chiếu,
  cấu hình giọng, logo và khóa API mã hóa không đổi. PowerPoint đang mở
  và bản RC80 chạy riêng không bị đóng.
