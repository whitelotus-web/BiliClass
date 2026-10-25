# Kiểm tra kết nối trong Dịch thuật

Sau khi lưu LanguageApp, Gemini hoặc DeepL, bấm **Thử kết nối**. Tool gửi một
câu ngắn, không lấy bản dịch từ cache, để kiểm tra dịch vụ ngay lúc đó. Thao tác
chạy nền, tính một ít hạn mức, không đổi dịch vụ đã chọn hay bài đang dở.
Đọc được danh sách model hoặc lưu được key chưa có nghĩa là đã dịch được.

## LanguageApp báo không tìm thấy doPost

Đây là lỗi của bản Apps Script đang triển khai, không phải lỗi nội dung bài.
Google có thể trả HTTP 200 nhưng nội dung là trang HTML báo lỗi.

1. Trong BiliClass: Cài đặt → Dịch thuật → Apps Script → Hướng dẫn thiết lập
   → Sao chép mã.
2. Mở đúng dự án Apps Script đã tạo. Dán toàn bộ mã vào `Code.gs`, thay mã thử
   mặc định `myFunction`, rồi lưu. Không dán hàm doPost vào bên trong myFunction.
3. Giữ thuộc tính tập lệnh `BILICLASS_ACCESS_CODE` trùng với mã đã lưu trong tool.
4. Triển khai → Quản lý bản triển khai → chọn bản hiện dùng → Chỉnh sửa (bút)
   → Phiên bản mới → Triển khai. Chỉ lưu mã mà không cập nhật phiên bản chưa đủ.
5. Kiểm tra Thực thi bằng **Tôi**, Ai có quyền truy cập **Mọi người**.
6. Giữ URL `/exec` nếu cập nhật bản hiện tại; nếu tạo bản triển khai khác thì
   dán URL mới vào tool. Bấm Lưu cấu hình → Thử kết nối.

Bài đang dở ghim URL cũ. Nếu tạo URL mới, cần khôi phục URL cũ hoặc chọn lại
file để bắt đầu lượt mới; không tự trộn hai bản dịch vụ trong cùng checkpoint.
Tài khoản trường có thể bị quản trị viên chặn quyền triển khai công khai.

## Gemini báo HTTP 402 / hết số dư trả trước

Máy chủ xác nhận dự án gắn với key đã hết số dư trả trước. Key vẫn có thể đọc
danh sách model nhưng không được tạo bản dịch. Đổi model không chuyển gói dự án.

Nếu chỉ muốn miễn phí: vào [Google AI Studio](https://aistudio.google.com/api-keys),
kiểm tra dự án của key. Tạo/chọn một dự án thuộc Free không gắn thanh toán nếu
tài khoản được phép, tạo key của dự án đó rồi nhập vào tool và Thử kết nối.
Không cần gửi key qua chat. Tool không tự nạp tiền, gắn thẻ hay nâng gói.

Nếu dùng gói trả phí, quản lý số dư trên AI Studio là việc của chủ tài khoản.
Khả năng dùng Free và hạn mức thực tế phụ thuộc tài khoản/model/khu vực.
Xem [Google Gemini billing](https://ai.google.dev/gemini-api/docs/billing).

## Dịch được nhưng chất lượng chưa đạt

Kết nối thành công chỉ chứng minh dịch vụ nhận và trả câu thử. Bài Toán cần
đối chiếu thuật ngữ và công thức, đặc biệt khi có chữ bình thường nằm xen
trong công thức Office Math, lỗi chính tả nguồn hoặc vùng chữ quá dày.

RC168 bổ sung thuật ngữ góc lượng giác, đường tròn lượng giác, giá trị lượng
giác, tia đầu/cuối, góc bẹt và hệ thức Chasles. Các mệnh đề nối công thức có
giới hạn rõ được dịch tại máy để dấu `+`, `=`, nhãn `sđ` không bị đổi thành
dấu phẩy hoặc từ nối. Hai cách diễn đạt một vòng tròn đầy đủ phân biệt rõ
độ dài chu vi với số đo góc theo độ/radian.

Thuật ngữ do giáo viên khóa vẫn được ưu tiên. Không tự sửa đáp án/công thức
đã sai ở nguồn và không tự ghi lại bài đã hoàn thành. Chuyển đổi lại bằng bản
mới nếu muốn áp dụng các sửa đổi; giữ bản trước để đối chiếu.
