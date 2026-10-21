# RC129 — Đồng bộ Xem mẫu và căn lại khung chữ đã dịch

Năm nút Xem mẫu của kiểu chuyển đổi và bộ mẫu dùng chung thành phần
100 × 30 px logic, cỡ chữ 11, giữ vị trí bên phải và hành động xem mẫu.
Thẻ chuyển đổi hẹp có nút xem mẫu thêm 2 px để đủ chỗ cho nút.

Từ việc kiểm tra các bài chuyển đổi và bộ giọng gần đây, bổ sung:

- Khối trên đầu trang có hơn hai đoạn và trên 100 ký tự được xử lý
  như thân bài để chia cột, tránh xếp cả khối câu hỏi thành tiêu đề.
- Khi PowerPoint đo được chữ tràn, khung đã dịch có tên gốc cũng
  được nới vào khoảng trống xác minh từ sơ đồ chuyển đổi. Không nới
  khung gốc chưa có bằng chứng đã dịch, khung có chuyển động/trigger,
  vùng bị che, hoặc ra ngoài dải nền. Giữ nguyên nội dung và cỡ chữ
  tối thiểu của bộ căn chỉnh.
- Giảm giãn dòng về một dòng trước khi giảm cỡ chữ. Khung có chữ căn
  đều tràn ngang chuyển sang căn trái để tránh khoảng cách chữ lớn.
- Bổ sung thuật ngữ Vật lý cho định luật I Newton, con lắc đơn/lò xo,
  dao động điều hòa/tắt dần và biên độ. Thuật ngữ giáo viên vẫn ưu tiên;
  dấu vân tay cache có thay đổi theo thuật ngữ, không dùng nhầm bản cũ.
- Phiên bản hoàn thiện bố cục tăng lên 5. Các bài có lỗi được thử lại
  một lượt hữu hạn qua luồng hoàn thiện hiện có. Tệp gốc/lịch sử giữ lại;
  WAV chỉ được dùng lại nếu lời đọc, khóa và số lần xuất hiện vẫn khớp.

Kiểm bằng `.venv`: 102 pytest liên quan đạt. Qt thật ở bốn cỡ cửa sổ
1080/1366/1920, có/không tệp và mẫu, xác minh cả năm nút bằng nhau và
chữ không bị cắt; các điều khiển/footer vẫn tới được. Không cảnh báo QML.

Rà soát riêng tám bản chuyển đổi/nhập, kiểm 1.183 WAV được tham chiếu:
không mất, hỏng, quá ngắn dưới 0,15 giây hay gần im lặng theo phép đo.
Đây là kiểm tệp/tín hiệu; chưa nghe và thẩm định phát âm mọi đoạn.

Chạy toàn bộ vòng hoàn thiện bằng PowerPoint trên bản sao ba bài
20/70/79 slide: số slide FAIL lần lượt giảm 2→0, 47→5 và 15→4.
Chữ trích xuất, media và Notes giữ nguyên chính xác; giọng Anh của
hai bài có âm thanh vẫn ready với 121/214 đoạn, không tổng hợp lại.
Đã xem ảnh đại diện trước/sau. Lỗi còn lại gồm công thức, khung chật
và kiểm tra nội dung song ngữ; không đổi nhãn lỗi thành đạt để che đi.
Không coi kết quả này là chứng nhận mọi bản dịch/công thức hoàn hảo.

Bài giảng, snapshot thư viện, ảnh đối chiếu, âm thanh và báo cáo thử
giữ trong thư mục bỏ qua Git. Việc kiểm thử không sửa thư viện cá nhân.
