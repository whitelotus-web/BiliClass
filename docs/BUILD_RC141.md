# RC141 — Dịch và bố cục bài giảng Toán

Lượt rà soát các bài Toán mới phát hiện câu chữ Việt nằm trong
đối tượng Office Math bị coi là công thức thuần, nên một số đáp án
không được dịch. Bộ trích xuất nay tách các run văn bản thường để
dịch và dàn dòng; giữ các cây công thức, biến, phân số và ma trận.
Bản nguồn bất biến được giữ để đối chiếu. Cỡ chữ Office Math được
đọc đúng, thay vì dùng mặc định 18 pt rồi phóng lớn nhầm chữ 48 pt.

Số lượng được hiện cho bộ dịch hiểu ngữ pháp, nhưng giá trị và XML
vẫn khóa bằng ID. Cache tách theo giá trị thực, tránh dùng chung
ngữ pháp số ít/số nhiều cho hai câu có placeholder giống nhau.
Có một lần phục hồi giới hạn nếu dịch làm mất khóa; không lặp lại
cả bài. Biến đếm hình học cũng có ngữ cảnh, không đổi công thức.
Không thay cơ chế khóa toàn bộ công thức Hóa học.

Bổ sung nhãn Activity/Example/Worksheet, Definition/Contents/Answer,
các mệnh đề hình học nguyên văn và cách dùng plane/face/incidence.
Không suy luận đáp án đúng/sai hay sửa giả thiết trong nguồn. Thuật
ngữ giáo viên khóa được ưu tiên. Đối chiếu thuật ngữ hình học với
[OpenStax](https://openstax.org/books/calculus-volume-3/pages/2-5-equations-of-lines-and-planes-in-space).

Khung song ngữ dành chỗ cho nhãn Hoạt động/Ví dụ, dừng trước hàng
kế tiếp và chia lại hai cột trước hình minh họa. Dải đáp án so chi
phí xuống dòng giữa cột và xếp Việt–Anh để giữ cỡ chữ tốt hơn. Chữ
thường tách từ Office Math giữ màu/font gốc và được Office đo lại.
Bộ căn chữ nhận cả freeform có văn bản chỉnh sửa được; trước đây
loại tiêu đề này được báo tràn nhưng bị bỏ qua khi tự sửa. Giữ
nguyên đường bao, ảnh, ký hiệu và các điều kiện bảo vệ công thức.

Chọn vị trí lỗi hoặc mở phần chi tiết tự chuyển ảnh đến đúng slide
ở cả hai công cụ. OCR thấy chữ trong ảnh nhỏ trên trang có chữ
chỉnh sửa được vẫn được đưa vào danh sách cần đối chiếu. Nhận xét
đã kiểm chứng về đề gốc có loại CHECK riêng, không sửa đề/đáp án.
Không coi ảnh đã render hoặc 0 FAIL là chứng nhận đúng nội dung.

Đã dựng và xem 89 ảnh PowerPoint của bốn bản thử 18/20/13/38 slide;
không FAIL trong các phép kiểm tra tràn chữ/bố cục hiện có. 2.017
run ký hiệu toán học có trong đầu ra và media nguồn được giữ theo
hash. Chữ raster và ý nghĩa chuyên môn chưa thể chứng nhận chỉ từ
các phép kiểm tra này. Một số trang dày chữ vẫn cần người xem lại.
Các lỗi giả thiết phát hiện từ nguồn được ghi riêng theo slide,
không tự sửa đề hay đánh dấu giáo viên đã duyệt.

231 pytest liên quan trong `.venv` đạt; sau bổ sung lưu lại kế hoạch
cặp và vùng ảnh, 40 ca thư viện/hoàn thiện/chẩn đoán đạt. Hai nhóm có
giao nhau, không cộng thành số ca riêng. Qt chẩn đoán đạt 16 trạng
thái sáng/tối, thu gọn/mở rộng, hai cỡ màn và cả hai công cụ; kiểm
mở chi tiết/chọn lỗi chuyển đúng ảnh, tương phản tối thiểu 6,31:1.
Qt chuyển đổi giữ cấu hình/loading tại chỗ, dừng/tiếp tục/hủy và xem
kết quả qua với API fixture, Office thật; không cảnh báo QML. Có log
Windows điều chỉnh kích thước cửa sổ theo màn hình. Ruff và compileall
đạt. Không khẳng định đã nghe/chấm toàn bộ giọng đọc hay thử máy yếu.

Ba bản trong thư viện được cập nhật theo revision, giữ ID và nguồn
cũ/lịch sử: hai bản chưa có giọng nhận bản dịch và bố cục đã kiểm;
bản vừa tạo giọng chỉ sửa bố cục, giữ nguyên lời và 147 khóa âm thanh.
Bản có giọng cũ còn lại được giữ; bản dịch thử cải thiện nằm riêng.
Giữ giọng cũ không có nghĩa đã cập nhật giọng theo mọi câu dịch mới.
Đối chiếu SHA-256 trước/sau của 3.090 WAV đạt; các bài khác không đổi.
Kế hoạch cặp Việt–Anh và danh sách ảnh được lưu lại cùng bản kiểm tra,
tránh dùng ánh xạ cũ sau khi thay bản sửa.
Thư viện, bản sao thử, âm thanh, ảnh và báo cáo cá nhân ở ngoài Git.

Chưa phát hành RC141 tại thời điểm kiểm chứng mã nguồn này. Gói là
artifact riêng, chỉ dựng sau commit đã kiểm tra. Không thêm hàng đợi,
không triển khai đồng bộ chỉnh/sửa PowerPoint bên ngoài trong đợt này.
