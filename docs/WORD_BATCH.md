# Chuyển đổi nhiều file Word

Tính năng mới của RC172; không nằm trong bộ cài RC171 đã phát hành.
Không thay đổi tag/bộ cài RC167, RC169, RC170 hoặc RC171.

## Cách dùng

1. Vào **Chuyển đổi bài giảng → Word**, chọn hoặc kéo thả nhiều file `.docx`.
2. Tool tự tích và khóa **Dịch toàn bộ**. Khung chọn đoạn/câu được thay bằng
   danh sách file; chưa gọi dịch vụ cho tới khi bấm **Chuyển đổi bài giảng**.
3. Chọn chung môn, cấp/lớp, kiểu song ngữ và định dạng. Tên bài lấy theo từng file.
4. Tool xử lý lần lượt, tự lưu cạnh từng nguồn với hậu tố **(Song ngu VI-EN)**
   và đưa kết quả vào thư viện chung. Không ghi đè nguồn hoặc một bản xuất khác
   đã bị sửa; dùng cơ chế xuất Word hiện có.
5. Kết quả giữ trên màn hình. Có thể **Mở Word**, **Mở thư mục**, chọn lượt khác
   hoặc **Về bài giảng**. Không tự trở lại màn hình tải file.

Chọn một file từ hộp tải vẫn dùng luồng một bài: chọn riêng nội dung hoặc
bật/tắt Dịch toàn bộ như trước. Một lượt chọn nhiều file chỉ dịch toàn bộ;
không mở từng file trong hàng đợi để bôi đen. Có thể bỏ file khỏi danh sách
trước khi chạy; các file còn lại trong lượt vẫn dùng Dịch toàn bộ.

## Dừng, thử lại và dữ liệu

- **Dừng** chờ bước đang chạy kết thúc, giữ checkpoint rồi cho **Tiếp tục**.
- File hỏng/không hỗ trợ được ghi lỗi riêng; file tiếp theo vẫn được xử lý.
- Hết hạn mức, lỗi cấu hình dịch hoặc thiếu chỗ lưu sẽ tạm dừng danh sách,
  tránh tiếp tục gửi cả loạt yêu cầu không thực hiện được.
- Thử lại chỉ chạy bài chưa xong/bị lỗi; bài đã xong được bỏ qua. Cấu hình được
  chốt khi bắt đầu, khóa trong lúc tiếp tục/thử lại để giữ kết quả nhất quán.
- Khởi động lại có thể lấy lại hàng đợi đã lưu. **Hủy các bài đang chọn** bỏ
  danh sách, không xóa file nguồn hoặc các bài đã tạo trong thư viện.
- Hai file giống hệt nội dung ở hai thư mục vẫn có đầu ra cạnh đúng từng nguồn.
  Hàng đợi không sửa checkpoint chọn vùng đang có từ luồng một file.

Nhận tối đa 100 file một lượt, giữ giới hạn 50 MB mỗi `.docx`. Chỉ xử lý một
file một thời điểm, không tạo bản xem trước nặng cho mọi file cùng lúc. Kho
Word giữ từng checkpoint riêng; hàng đợi là JSON nhỏ trong
`word_documents/batches/`, con trỏ gần nhất là `last_word_batch` trong cài đặt
cục bộ. Dùng khóa hàng đợi và kiểm tra revision khi có nhiều cửa sổ.

Chữ nằm trong ảnh, công thức, trường tự động và phần đang khóa tiếp tục được
giữ nguyên theo cơ chế Word hiện có; Dịch toàn bộ áp dụng phần chữ có thể sửa.

## Kiểm tra

Dùng `.venv` dự án sau khi nạp môi trường nguồn:

```powershell
. ./reports/rc155/source-env.ps1
& ./.venv/Scripts/python.exe -m pytest tests/test_word_batch.py tests/test_word_preview.py tests/test_word_formatting.py tests/test_word_selection.py tests/test_word_document.py -q
& ./.venv/Scripts/python.exe -m scripts.qt_word_batch_smoke reports/word-batch
& ./.venv/Scripts/python.exe -m scripts.qt_word_smoke reports/word-single-regression
& ./.venv/Scripts/python.exe -m scripts.qt_batch_queue_smoke reports/powerpoint-batch-regression
```

Dùng tài liệu, dịch vụ và kho dữ liệu giả lập; không gọi API hay thay thư viện
cá nhân. Kiểm tra đủ bốn kiểu xuất, trùng nội dung khác nguồn, file hỏng,
nguồn được sửa, dừng/tiếp tục, khôi phục lượt dở, thử lại, đầy ổ lúc xuất,
revision cũ và file nguồn giữ nguyên byte. Qt kiểm tra hàng đợi sáng/tối,
ba kích thước cửa sổ và luồng Word một file/PowerPoint hiện có.
