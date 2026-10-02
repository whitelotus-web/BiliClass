# Giữ thiết kế PowerPoint khi thêm song ngữ

Bản mã nguồn hiện tại mặc định giữ thiết kế khi nhập `.pptx`. Luồng chính: **Nhập bài → dịch và duyệt → Xem bài song ngữ**. Không cần chọn bộ mẫu hoặc loại slide.

Đây là bước đầu: hiện thêm bản Anh ở slide kế tiếp. Thêm chữ Anh vào vùng trống cùng slide và so sánh gốc/song ngữ chưa có; xem [đối chiếu hướng phát triển](POWERPOINT_DIRECTION.md).

1. Trong **Tạo bài học mới**, chọn PowerPoint, nhập tên bài/môn/khối và chọn L0–L4. **Slide Việt / Anh kế tiếp** là cách trình chiếu mặc định.
2. Kiểm tra văn bản trích xuất, dịch rồi duyệt từng cặp Việt–Anh. Bảng giữ số dòng và dấu `|` phân cột. Chữ trong ảnh, biểu đồ và công thức nhúng cần đối chiếu riêng; app chưa tự dịch những phần này.
3. Bấm **Xem bài song ngữ** để mở bản tạo trong thư mục tạm bằng ứng dụng PowerPoint trên máy, hoặc **PPTX** để lưu bản mới. Bấm **Trình chiếu song ngữ** để chiếu và điều khiển từ BiliClass; điều khiển này cần Microsoft PowerPoint trên Windows.

Với cách mặc định, thứ tự là slide Việt 1 → bản Anh 1 → slide Việt 2 → bản Anh 2. Bản Anh dùng hình, bảng, biểu đồ, nền và vị trí đối tượng của slide tương ứng. Slide chỉ có hình hoặc có nội dung hai ngôn ngữ giống nhau không bị nhân đôi. Nút theo dõi slide và chuyển tới đoạn trong BiliClass vẫn liên kết với số slide gốc.

Hai lựa chọn khác: **Việt + từ khóa Anh** chỉ thêm thuật ngữ đã chuẩn bị cạnh chữ Việt; **Chỉ bản Anh** thay văn bản Việt bằng bản Anh trên bố cục gốc. Level tiếp tục theo quy tắc của bài, bao gồm câu Anh dễ đã được duyệt ở L2. Ngôn ngữ trình chiếu quyết định phần chữ hiện trên slide; level không tự tạo kiến thức hay bản dịch đúng.

Bản nguồn được lưu riêng và kiểm tra hash trước khi tạo bản song ngữ. Nội dung dịch dùng các ô chữ có sẵn; app có thể giảm cỡ chữ trong giới hạn, nhưng sẽ báo nếu vẫn quá dài. Khi đó rút gọn và duyệt lại, hoặc bỏ **Giữ thiết kế gốc** để dùng bố cục BiliClass. Hiệu ứng và đối tượng gốc được giữ trong gói PowerPoint; vẫn cần xem lại trên máy dạy, nhất là khi đổi độ dài chữ hoặc có âm thanh/video liên kết ngoài.

Bài cũ vẫn giữ cách trình bày đã chọn. Muốn chuyển bài PowerPoint cũ, bật **Giữ thiết kế gốc** trong màn soạn bài. Nếu các đoạn đã gộp/sửa nguồn nên không còn khớp ô chữ, app yêu cầu nhập lại bản gốc hoặc dùng bố cục BiliClass. Gói bài chia sẻ lưu lựa chọn này; người nhận vẫn cần kiểm tra và duyệt lại nội dung.

Xem lại cùng một bài không cần tạo lại `.exe`: app dùng bản PowerPoint tạm đã kiểm tra khi nội dung/cấu hình không đổi, và tạo bản khác khi sửa bài. Bản thử từ mã nguồn chưa nằm trong rc12. Chạy nhanh theo [TRY_IT.md](TRY_IT.md).

Kiểm tra trên máy phát triển: bộ mẫu thử có chữ, bảng và biểu đồ sửa được; PowerPoint mở và render được cả 6 slide song ngữ. Ba slide Việt có render giống hệt bản nguồn. Kiểm thử cũng xác nhận biểu đồ của bản Anh có riêng phần dữ liệu nhúng, giữ nguyên dữ liệu gốc; nguồn, theme và media không bị sửa. Kết quả này không thay thế việc nghiệm thu bài thật của giáo viên.
