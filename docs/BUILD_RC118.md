# RC118 — Mở bài nhất quán và bảng Mascot gọn hơn

Bản này gồm các thay đổi RC117 về tốc độ nạp PowerPoint, màn cấu hình
chuyển đổi và ô tổng hợp cấu hình cố định. Giữ tự lưu kết quả vào thư viện.
Hai tab Chuyển đổi/Tạo giọng là công cụ xử lý và xem trước; Mascot lấy
bài từ Bài giảng hoặc file ngoài. Không thêm bước bấm lưu thủ công.

## Mở và đổi bài

- Mở từ Mascot chuyển về Bài giảng, không giữ màn kết quả Tạo giọng.
  Mở từ màn công cụ giữ nguyên màn đang dùng.
- Bấm mở lại cùng bài/bản giọng đưa PowerPoint ra trước, giữ slide hiện tại.
  Nguồn, phiên bản nội dung hoặc bản thu thay đổi vẫn phải chuẩn bị lại.
- Đổi bài được khi sẵn sàng hoặc đang chiếu. Chuẩn bị bài mới trước;
  lỗi/hủy chuẩn bị giữ bài đang dạy. Khi bài mới hợp lệ, dừng giọng,
  đóng đúng bản PowerPoint do tool mở, đợi đóng xong rồi mới mở bài mới.
- Mở bảng chọn hoặc hủy hộp file không kết thúc bài hiện tại.
- Khóa thao tác mở/đổi khi Office đang mở, đóng hoặc chuyển trạng thái
  trình chiếu. Backend có cùng chốt kiểm tra; bấm F5/Kết thúc liên tiếp
  không xếp thêm lệnh. Sự kiện muộn của worker cũ không đổi binding mới.
- Kết thúc chỉ dừng trình chiếu/giọng, giữ bài sẵn sàng để chiếu lại.
  Đóng phiên mới gỡ binding. Không đóng các file PowerPoint khác.

## Giao diện

Bỏ hẳn Tự động/Đang hiện/Toàn slide khỏi bảng Mascot và bỏ API chọn
thủ công. Luôn theo dõi hiệu ứng bên trong: phần mới hiện được ưu tiên;
slide không có hiệu ứng dùng toàn slide. Không thêm lựa chọn nâng cao
ở Cài đặt; giữ tỉ lệ bảng với Mascot 60–160 px.

Thư viện thay nhãn Đã lưu bài/Sẵn sàng trình chiếu bằng tình trạng giọng
đã kiểm tra: Chưa có giọng, Giọng chưa đủ, Có giọng Việt/Anh/cả hai,
Đang kiểm tra hoặc Chưa kiểm tra giọng. Tính các bản thu hoàn tất độc lập
với bản đang chọn; không dùng xác nhận nội dung làm bằng chứng có giọng.
Báo thiếu nội dung/bố cục riêng khi cần; ngày tạo giữ cùng cột. Màu nền
và chữ dùng đúng vai trò sáng/tối.

Vào tab Tạo giọng mở phần cấu hình, kể cả bấm lại chính tab đó khi đang
xem kết quả. Kết quả tự hiện sau tác vụ tạo giọng, không tự hiện lại chỉ
vì đổi tab hoặc nhận thông báo thư viện. Đổi cấu hình giọng nằm ở đầu
màn kết quả, cạnh nút về thư viện.

## Kiểm chứng nguồn

187 ca pytest liên quan đạt: nhập/nạp lại, ghi chú song ngữ, dàn trang,
giọng theo hiệu ứng, trạng thái/bản thu, nguồn xuất và chuyển phiên Office.
Có ca riêng cho mở lại cùng bài, hủy, lỗi chuẩn bị, bấm liên tiếp,
đổi khi chiếu và tín hiệu muộn của worker cũ.

Qt thật kiểm tra theme/DPI 100% và 150%, đủ các nhãn giọng không bị cắt,
60–160 px không còn ba nút cách đọc, cấu hình cố định và 9 tổ hợp demo loa.
Qt + Office dùng thư viện tạm, bản WAV thử, kiểm tra mở từ thư viện/Mascot/
các công cụ, sẵn sàng/F5/kết thúc/chiếu lại, đổi khi đang chiếu, hủy file,
phát native/pause/resume, binding độc lập với bài đang duyệt và nguồn
không đổi. Màn kết quả kiểm tra chuyển tab và quay lại cấu hình.
Không coi các phép thử này là chứng nhận máy chiếu hoặc nhiều màn hình.

Kiểm tra thư viện dạng dòng/thẻ và các hộp tải/sửa tên đã đạt. Tên kiểu
nút nội bộ MainAction được tách khỏi Action của Qt để tránh nhận nhầm
wrapper khi đóng/mở popup; bài kiểm tra giữ nguyên thao tác click thực.
Bài kiểm tra đợi popup đóng xong và đóng các worker trước dọn cửa sổ.

## Gói và cài đặt đã kiểm tra

Nguồn dựng: `4e34e62b709a71da3f8908fe94f9287908831f9d`. Biên dịch lại
module app, dùng runtime/model RC117 đã xác minh hash. Gói có 4.662 tệp
ứng dụng và 54 tệp QML/qmldir khớp nguồn. Kiểm từng tệp trong ZIP, SHA256
ZIP và digest asset GitHub; bản cài cũng đối chiếu EXE và toàn bộ QML.

- Phát hành: https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc118
- ZIP: `BiliClass-RC118-Windows.zip`, 1.249.984.085 byte.
- SHA256: `38499c8405e0061a714f69b0e35e950941dc83cc909d3483cc3b297367a3de08`.
- Bản đóng gói mở đúng tab Tạo giọng 1366×850 với thư viện tạm; không có
  cảnh báo QML. Không dùng thư viện cá nhân cho thử chức năng.
- RC116 đóng bình thường; cài tại `F:/Applications/BiliClass/1.0.0rc118`,
  mở qua Explorer độc lập với agent. Main/Mascot đạt ba lần phản hồi
  liên tiếp sau khởi động; biểu tượng/taskbar và shortcut trỏ đúng RC118.
- Đối chiếu trước/sau: 20 bản ghi bài cùng hash nội dung/nguồn, 1.658 WAV
  tham chiếu, lựa chọn giọng, logo và khóa API mã hóa không đổi. PowerPoint
  và RC80 chạy riêng vẫn được giữ.
