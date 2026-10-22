# RC147 — Chọn nhiều bài và xử lý lần lượt

Cả Chuyển đổi và Tạo giọng nhận nhiều PowerPoint qua hộp chọn file hoặc
kéo thả. Tối đa 100 file, 200 MB mỗi file; một cấu hình chung cho mỗi
lượt, tên bài theo file. Chỉ một bài xử lý tại một thời điểm, dùng lại
các bộ chuyển đổi/tạo giọng hiện có. Quy trình một bài được giữ.

Danh sách ghi tiến độ riêng từng bài. Dừng giữ checkpoint; Tiếp tục bỏ
qua bài đã hoàn tất và dùng lại đoạn giọng hợp lệ. Lỗi riêng một bài
không chặn bài sau; Thử lại bài lỗi chỉ chạy các bài thất bại. Lỗi chung
về dung lượng, key, hạn mức hoặc kết nối dịch dừng cả lượt. Không tự
thử vô hạn. Nhật ký danh sách đã bắt đầu được ghi nguyên khối trên máy;
mở lại tool vẫn vào Trang chủ và có lối trở lại hàng đợi đang dở.

Mỗi bài thành công tự lưu PowerPoint cạnh đúng file đầu vào. Không ghi
đè; thư mục dự phòng và bản xuất dùng lại áp dụng như RC146. Hai bản
đầu vào giống hệt nhau ở hai thư mục vẫn xuất đúng nơi của từng bản,
kể cả khi tiếp tục từ checkpoint cũ. Nguồn thay đổi hoặc bài trong thư
viện đã sửa không nhận kết quả cũ. Bỏ danh sách giữ bài và âm thanh.
Khóa theo thư viện ngăn hai cửa sổ cùng chạy hàng đợi; bản trạng thái
cũ không ghi đè tiến độ mới. Nhật ký/đường dẫn riêng không đưa lên Git.

Hai công cụ dùng chung khung danh sách, Dừng/Tiếp tục/Thử lại, Xem bài
và Mở thư mục. Cấu hình được chốt sau khi chạy; hiển thị cấu hình đã
lưu khi tiếp tục. Cập nhật tiến độ gộp theo nhịp ngắn để không dựng lại
danh sách quá dày; danh sách dài theo bài đang chạy. Giữ bốn tab Cài
đặt và quy trình nghe/dừng, tải file, Mascot hiện có.

Chưa thêm xử lý nhiều bài đồng thời, ghép tự động chuyển đổi → tạo
giọng, thêm file vào lượt đang chạy hoặc đồng bộ sửa tay ngoài tool.
Danh sách nháp chưa bấm chạy chưa lưu qua lần mở ứng dụng; chọn lượt
mới khi dừng thay danh sách hiện tại, giữ sản phẩm. Kiểm chứng dùng
thư viện/PowerPoint và WAV mẫu riêng; không sửa bài hay âm thanh gốc.
Không chứng nhận mọi bản dịch, OCR, bố cục hoặc chất lượng âm thanh.

Hướng dẫn: [USER_GUIDE.md](USER_GUIDE.md#chọn-nhiều-file-và-xử-lý-lần-lượt).

13 ca hàng đợi đạt: thứ tự, lỗi cục bộ/lỗi chung, khóa hai cửa sổ,
revision cũ, nhật ký hỏng, ổ đĩa đầy khi ghi checkpoint, dừng lúc lưu,
nguồn bị sửa, tạo/xuất PowerPoint thật với dịch/WAV fixture, tiếp tục
giọng giữ WAV và tiếp tục xuất đúng nguồn. Nhóm hồi quy 66 ca, nhóm
portable 422 ca và corpus cấu trúc tại máy đạt; các nhóm có giao nhau
và có ca bổ sung sau lượt portable, không cộng thành một tổng độc lập.
Ruff toàn kho và compileall đạt.

Qt hàng đợi kiểm hai công cụ sáng/tối tại 1080/1366 px, lỗi ở bài giữa,
dừng/tiếp tục, khôi phục và chỉ thử lại bài lỗi; 25 mục theo bài cuối
đang chạy. Nhịp GUI tối đa quan sát 0,219 giây trong lượt kiểm;
không cảnh báo QML. Hai Qt hồi quy
riêng cho tự lưu và kết quả/nghe-dừng một bài tiếp tục đạt. WAV fixture
kiểm điều phối/nhúng file, không đo chất lượng model giọng. Có kiểm
chế độ OpenFiles và nhận URL trong QML; chưa tự động bấm hộp chọn file
Windows bằng chuột/phím toàn hệ thống.

Đã phát hành từ `5572f03fd6c180f9aa25af7b119f19d949c687f2`; [Source checks GitHub](https://github.com/whitelotus-web/BiliClass/actions/runs/39747264522) đạt cho đúng commit gói.
[Gói RC147](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc147) có 1,258,134,623 byte, SHA-256
`fc0f76bc9a37a1fab86f834cee781dbbb25294594c0080a9ea200ca45eb41f61`. 59 tệp QML/qmldir và bytecode ứng dụng khớp nguồn;
toàn bộ ZIP, digest/tag và phát hiện bản cập nhật công khai đạt.
Đã cài, mở Trang chủ từ Explorer; Mascot khởi động ẩn. Hồ sơ,
cấu hình/key, nguồn và 1752 WAV tham chiếu giữ nguyên.
