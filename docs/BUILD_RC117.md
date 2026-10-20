# RC117 — Nạp bài nhanh và đồng bộ màn cấu hình

Sau khi chọn PowerPoint, màn Chuyển đổi dùng cùng cách trình bày với màn
Tạo giọng: tên bài/thông tin ở trái, ảnh slide 16:9 và nút xem trước ở phải,
chọn bài khác/hủy ở đầu trang. Bỏ khung “Đã chọn PowerPoint”; giữ cấu hình
bên dưới và thanh thực hiện cố định. Kéo tệp mới vào vẫn thay được bài.

Hai ô “Cấu hình đã chọn” dùng chung thành phần hiển thị các nhãn ngắn:

- Chuyển đổi: ngôn ngữ đầu ra, giữ thiết kế gốc hoặc tên mẫu, môn, cấp/lớp.
- Tạo giọng: ngôn ngữ, giọng thực sự dùng, tốc độ, số/vị trí loa, số slide
  có lời. Khi chỉ chọn Việt hoặc Anh chỉ hiện tên giọng của ngôn ngữ đó;
  cả hai mới hiện tên cặp. Phần đếm của cả hai ngôn ngữ hiện riêng Việt/Anh.

Các nhãn tự xuống hàng khi hẹp; bỏ giải thích dài, bước tiếp theo và mô tả
OCR khỏi ô tổng hợp. Vẫn nằm cạnh nút thực hiện, đứng yên khi cuộn, cập
nhật theo lựa chọn. Bài chỉ có một ngôn ngữ giữ quy tắc khóa ngôn ngữ thiếu,
nhưng nút bị khóa mờ rõ hơn và có lời giải thích ngắn ngay dưới lựa chọn.

Nạp bài cho Tạo giọng kiểm tra SHA256 và tìm bản nhập trước trước khi phân
tích slide. Bản có cùng bytes dùng lại lời đã sửa và bản thu; file đổi
nội dung vẫn phải phân tích mới. Bản mới chỉ mở PPTX một lần để đọc chữ,
ghi chú và dữ liệu lời/hiệu ứng; không chạy kiểm tra dàn trang của luồng
chuyển đổi trên file giữ nguyên. Chữ OCR đã có dữ liệu từ lần trích mới
được dùng ngay; bài cũ thiếu dữ liệu vẫn chạy bước khôi phục. Kiểm tra ZIP,
giới hạn dung lượng/slide/chữ, hash nguồn và bản sao vẫn được giữ. Không
ghi lại các thiết lập đường dẫn xuất khi giá trị không đổi.

Trong lúc đọc hiện tên bài cùng trạng thái chuẩn bị lời đọc. Công việc
chạy ở worker; ảnh slide được chuẩn bị riêng, không chặn cấu hình giọng.

Đo trên bản sao riêng của bài 48 slide, 70.906.619 byte, không thay dữ liệu
cá nhân: cProfile trước/sau cho lần đầu 8,625 → 4,407 giây và lần chọn lại
3,911 → 1,962 giây. Đây là thời gian đọc/nhập, không bao gồm render ảnh
slide bằng Office. Luồng Qt thật sau sửa đo 2,532 giây lần đầu và 1,500
giây chọn lại; khoảng cách lớn nhất giữa các nhịp GUI dưới một giây.
Các phép đo phụ thuộc máy, cache và kích thước bài; không phải cam kết
thời gian cho mọi PowerPoint.

Kiểm tra: 121 ca nguồn đạt, gồm tái nhập không phân tích lại, giữ sửa lời
và audio cũ, đổi bytes phải phân tích mới, ghi chú Việt/Anh, khôi phục OCR
bài cũ, kiểm tra nguồn/đường dẫn xuất và luồng chuyển đổi. Stub dịch ảnh
trong phép thử giữ token thuật ngữ khóa như dịch vụ thật; không đổi quy
tắc bảo vệ nội dung sản phẩm. Ruff và khoảng trắng đạt. Qt kiểm tra bố
cục 1080/1366/1920 sáng/tối, DPI 100%/150%, ô tổng hợp cố định/cập nhật,
9 tổ hợp loa demo, chọn/tải/hủy file bằng hộp Windows thật, bảo toàn SHA256
nguồn, màn hoàn tất giọng và khả năng phản hồi khi nạp bài. Các phép thử
chức năng dùng thư viện tạm.
