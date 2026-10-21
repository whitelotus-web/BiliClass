# RC138 — Sửa lỗi PowerPoint thực tế và chỉ rõ vị trí cần xử lý

Các ô chọn ngôn ngữ giọng đọc, kiểu chuyển đổi, thiết kế và mẫu bài
nhận bấm ở cả phần mô tả và khoảng trống. Nút Xem mẫu lên cùng hàng
mô tả, giữ kích thước 100 × 30; bấm xem trước không đổi lựa chọn.
Bàn phím và khóa thao tác trong lúc xử lý được giữ nguyên. Khung
tự tính chiều cao theo nội dung thay cho khoảng trống cố định lớn.

Khởi động thông thường vào Trang chủ. CLI ứng dụng vốn mặc định
Home; công cụ mở bản độc lập nay cũng mặc định Home. Bộ cài xóa
tham số trang cũ trong shortcut khi cập nhật. Mascot vẫn ẩn lúc
khởi động theo RC137. Không đổi các tab Cài đặt hay thêm hàng đợi.

Một bài Toán thực tế dừng ở 175/180 đoạn: năm đoạn thiếu chính là
❶–❺ đứng riêng. Giọng Việt nay nhận lời đọc “Số một.” … “Số năm.”;
không sửa chữ trên slide hay định danh cache. Các số khoanh tròn
khác đến 50 được chuyển thành lời tương ứng. Công thức, phân số,
chỉ số dưới và các câu không có loại ký hiệu này giữ nguyên.
Tiếp tục sử dụng lại WAV hiện có, chỉ tạo phần thiếu.

Thông báo làm việc dùng cách gọi giọng Việt/Anh, không đưa tên
bộ máy tổng hợp hoặc chẩn đoán SDK lên giao diện. Bài còn dở có
nút Tiếp tục tạo giọng; lỗi thông báo giữ phần đã tạo và hướng dẫn
tiếp tục. Thông tin giấy phép và ghi công của phụ thuộc vẫn được
giữ trong mã nguồn và tài liệu giấy phép.

PowerPoint hợp lệ có thể thiếu placeholder thân ghi chú. Bộ dựng
bài nay bổ sung riêng phần này, không đụng đến hình thu nhỏ, footer
hay các phần còn lại của ghi chú. Các bộ đọc dùng chung cách đọc
ghi chú rỗng an toàn. Lỗi thực tế ở slide 31–33 của một bài Toán
38 slide đã được tái hiện; bản sửa chạy đến lưu đủ 38 slide, giữ
nguyên tệp gốc và dùng lại bản dịch, không gọi API mới. Cả 38 trang
được PowerPoint dựng ảnh; không còn FAIL về phép đo tự động, vẫn
có CHECK cho hình, công thức, hiệu ứng và nội dung cần đối chiếu.

Nhãn số khoanh tròn là ký hiệu dùng chung, không nhân đôi thành
hai bản ngôn ngữ hay kéo dài hình chứa nhãn. Tiêu đề giữ căn trên
của bản gốc để chữ trắng không bị đẩy ra khỏi dải nền màu. Các
tiêu đề hình học khớp toàn câu được chuẩn hóa riêng môn Toán;
“Các tính chất thừa nhận” dùng “Basic axioms”, không dùng bản dịch
“Recognizational properties”. Thuật ngữ giáo viên khóa vẫn ưu tiên.
Tham khảo cách dùng axioms/postulates trong tài liệu hình học
[NCERT/IIT Kanpur](https://sathee.iitk.ac.in/ncert-books/ncert-books-theory/class-09/nbt-math-09/math-09-chapter-05-introduction-to-euclids-geometry/)
và pyramid/tetrahedron trong
[OpenStax](https://openstax.org/books/calculus-volume-1/pages/6-2-determining-volumes-by-slicing).

Bài nguồn vừa nhập để tạo giọng được giữ như bản đang chuẩn bị,
không hiện lẫn với sản phẩm trong thư viện chính. Có thể chọn lại
bản dở trong màn Giọng đọc. Tạo đủ giọng công bố cùng ID bài;
nhập lại đúng tệp đã chuyển đổi dùng lại sản phẩm sẵn có. Không
xóa bản nguồn, bài dở hoặc âm thanh riêng của giáo viên.

Cả màn hoàn tất chuyển đổi và màn tạo giọng có mục Xem vị trí:
liệt kê slide, lý do, trích đoạn và hành động tiếp theo; lỗi bố cục
được xếp trước cảnh báo cần đối chiếu. Bấm Xem slide mở đúng trang.
Lỗi dịch giữ được định danh đoạn sẽ chỉ slide nguồn thật; không
suy đoán theo phần trăm. Lỗi tạo giọng liệt kê slide, ngôn ngữ và
đoạn thiếu. Không đưa mã khóa bảo vệ số hay tên bộ máy lên thông báo.

Vòng sửa bố cục hiện có chạy tối đa ba lượt, đo và dựng lại ảnh,
chỉ giữ trang có bằng chứng tốt hơn; tiến độ nay nêu các slide đang
được sửa. Cảnh báo chồng lấn từ hộp bao chưa phải bằng chứng chữ
thật sự bị che, nên không tự xóa chữ/hình dựa trên cảnh báo này.
Không cam kết tự chứng nhận mọi bài hoặc nghĩa chuyên môn.

Kiểm chứng trong môi trường dự án: 402 pytest đạt; Qt Home,
chuyển đổi Google chạy/dừng/tiếp tục/hủy, cấu hình chuyển đổi ở
1080/1366/1920, thư viện và vòng đời Mascot đạt. Qt vùng bấm thử
cả mô tả, khoảng trống, phím Space, trạng thái khóa và nút xem
mẫu riêng ở hai kích thước, hai giao diện sáng/tối; không cảnh
báo QML. Qt lỗi tạo giọng kiểm tra thông báo, slide/đoạn lỗi và nút
tiếp tục. Qt chẩn đoán thử đúng trang ở cả chuyển đổi và giọng đọc,
1080/1366; Qt thư viện thử giữ bản dở rồi công bố cùng ID sau tạo giọng.
Ruff cho các tệp Python thay đổi và compileall đạt. Ruff toàn kho
còn các cảnh báo kiểu viết/import và biến không dùng có từ trước;
không coi đây là một lượt kiểm tra lint toàn kho đã đạt.

Năm WAV sửa lỗi được tạo bằng bộ giọng thật, mono PCM16 48 kHz,
có dữ liệu khác không, dài 0,72–0,8 giây mỗi đoạn. Đối chiếu các
khóa cache cho phép giữ 175 tệp cũ khi hoàn tất bài này. Chất lượng
nghe chủ quan toàn bộ bài và cấu hình máy yếu cần thử thực tế.

Dung lượng bản RC137 dùng làm nền: ZIP 1.258.042.513 byte; ứng dụng
giải nén khoảng 2,1 GB, gồm khoảng 1,1 GB model. Đo riêng một lượt
giọng Việt và Anh bằng một worker trên i7-8700/RAM 32 GB: đỉnh RSS
của cây tiến trình khoảng 1.762 MB, private memory khoảng 2.551 MB;
chưa cộng giao diện và PowerPoint. Đây là mẫu ngắn trên máy phát
triển, không xác nhận máy RAM 4/8 GB chạy mượt. Máy ít RAM dùng
một worker theo cơ chế hiện có; model chỉ nạp khi cần tạo giọng.

Luồng tự lưu cạnh tệp gốc và đồng bộ sau sửa/lưu PowerPoint bên
ngoài chưa có trong mốc này. Khi mở từ tool, phiên dạy vẫn dùng
bản sao riêng; chưa coi việc bấm Save ở phiên đó là cập nhật thư
viện. Cần hoàn thiện và thử lưu bằng PowerPoint thật trước khi
đổi hành vi này; không công bố đã hỗ trợ đồng bộ hai chiều.
