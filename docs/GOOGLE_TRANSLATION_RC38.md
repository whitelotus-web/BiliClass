# RC38 — dịch văn bản qua Google, dựng PowerPoint tại máy

Ngày 15/10/2026. Luồng mặc định chuyển sang Google Cloud Translation Basic
NMT v2. Browser AI được tạm ẩn, dừng kiểm tra phiên nền và không tự tiếp tục
yêu cầu ChatGPT/Gemini cũ. Mã browser và các bài đã lưu được giữ để tương thích.

## Cách dùng

1. Bật Cloud Translation API và thanh toán trong Google Cloud, tạo API key
   được phép gọi dịch vụ này. Đây không phải đăng nhập Gemini/ChatGPT.
2. Trong **Cài đặt → Google Dịch**, mỗi dòng nhập `Tên dự án | API_KEY`.
   Có thể chỉ nhập key; các dòng đó dùng chung nhóm **Mặc định**. Key cùng
   dự án phải dùng cùng tên nhóm. Không tự nhận diện dự án qua chuỗi key.
3. Lưu cấu hình, chọn tài liệu/kiểu trình bày rồi bấm Chuyển đổi bài giảng.
   Chỉ phần chữ được gửi tới endpoint Google; không tải cả PowerPoint lên.
4. Bài song ngữ được lưu trước, có thể tải về ngay. Giọng VI, EN hoặc cả hai
   vẫn là một bước tùy chọn riêng, chạy bằng bộ giọng tại máy.

## Key, hạn mức và chi phí

- Nhập tối đa 50 key, dùng theo thứ tự đã lưu. Key cùng nhóm dùng chung bộ
  đếm, không tạo lại hạn mức khi xóa/thêm key. Nhóm/dự án khác có bộ đếm riêng.
- Giới hạn cục bộ mặc định 500.000 ký tự/nhóm/tháng UTC, có thể đặt thấp hơn.
  Dự trù trước khi gửi bằng giao dịch SQLite, kể cả hai worker/hai tiến trình;
  tính cả HTML bảo vệ số liệu. Không gửi một cụm vượt ngân sách của nhóm.
- Khi có phản hồi xác định key/quota không dùng được, chuyển sang key kế tiếp.
  Key đang bị chặn có thể được cho phép thử lại sau khi sửa cấu hình Google.
- Lỗi mạng chưa rõ có tính phí hay chưa vẫn giữ phần đã dự trù; không đổi sang
  tài khoản khác để gửi lặp lượt chưa rõ. Thử lại có giới hạn trên cùng key và
  chỉ khi ngân sách còn đủ. Không có vòng chờ/retry vô hạn.
- Đây **không phải số dư miễn phí của Google**. Tool không đọc được thanh toán
  và mức sử dụng từ ứng dụng, máy hoặc thư viện khác. 500.000 ký tự là mức
  tín dụng miễn phí theo điều kiện Google, không phải hạn mức riêng mỗi key.
  Việc bật nhiều key/dự án không bảo đảm có thêm tín dụng. Đặt quota phù hợp
  trong Google Cloud; ngân sách của BiliClass không thay được quota phía Google.
- Key dùng Windows DPAPI theo người dùng hiện tại; không trả key cho binding
  QML, không ghi key vào URL/log/library.db/gói bài/bản sao lưu. Chuyển máy phải
  nhập lại key. Ô nhập được xóa sau khi lưu; danh sách chỉ hiển thị đuôi key.

Tham khảo: [giá và tín dụng](https://cloud.google.com/products/translate/pricing),
[quota](https://docs.cloud.google.com/translate/quotas),
[REST v2](https://docs.cloud.google.com/translate/docs/reference/rest/v2/translate),
[key trong HTTP header](https://docs.cloud.google.com/docs/authentication/api-keys-use).

## Tốc độ và tính toàn vẹn

- Gom tối đa 4.500 ký tự/100 chuỗi một yêu cầu; hai worker song song. Chỉ xếp
  hai cụm vào hàng đợi một lúc, không đẩy toàn bài khi đã có lỗi.
- Loại nội dung lặp; cache bản dịch theo nguồn/hướng dịch/model. Ghi cache
  theo cụm trong một giao dịch thay vì mỗi câu một lần. Lượt tiếp tục tái dùng
  phần đã hợp lệ; không cần dịch lại toàn bộ bài.
- Bảo vệ số liệu, token công thức OOXML và đoạn LaTeX; kiểm tra đủ token,
  số liệu, số chuỗi, ký tự điều khiển. Giữ xuống dòng và khoảng cách khi Google
  bỏ khoảng trắng đầu/cuối. Nội dung tài liệu không được thực thi như chỉ dẫn.
- Khóa hệ điều hành theo job tránh hai cửa sổ cùng xử lý một bài. Mã yêu cầu
  dùng lại khi nhập thư viện, checkpoint hoàn thành ghi nguyên tử để tránh bài trùng.
- Đọc nguồn, dịch, dựng/kiểm tra file và ghi bài ở worker. Bộ đếm thời gian
  dùng đồng hồ Qt riêng; phần trăm theo lượng chữ đã nhận và các mốc cục bộ.
- Timeout HTTP 20 giây; lỗi mạng/tần suất thử lại tối đa hai lần với khoảng
  nghỉ có thể hủy. Dừng không cần đợi cả bài; request đang trong HTTP có thể
  cần đợi hết khoảng chờ trước khi worker thoát. Không cưỡng bức tắt thread.

## Giới hạn trình bày cần nói rõ

Google NMT dịch chữ; không soạn thêm kiến thức/quiz, không hiểu yêu cầu prompt
giảng dạy như ChatGPT. Luồng này có ba kiểu: hai cột, từng cặp và English.
Tạm ẩn tích hợp từ khóa và ô prompt/lưu ý vốn yêu cầu mô hình tạo nội dung.

PowerPoint có chữ chỉnh sửa được và đủ chỗ dùng bộ dựng OOXML đã có, giữ
media/theme/hiệu ứng ở các vùng đã qua preflight. Bài phức tạp hoặc bản dịch
không vừa được dàn lại bằng mẫu có phân trang, kèm thông báo phạm vi. Mẫu giữ
ảnh PowerPoint thông thường trên trang hình riêng để tránh che chữ, có thể
đổi số slide. Không cam kết giữ hiệu ứng/biểu đồ/OLE ở nhánh mẫu mới.

Chữ trong ảnh, nhãn biểu đồ, công thức và nội dung OCR vẫn cần đối chiếu.
Không coi dịch chữ xong là đã kiểm chứng toàn bộ kiến thức/bố cục; không tự
duyệt bài hoặc biến CHECK thành PASS. Bài được kiểm tra bằng bộ đọc/kiểm tra
slide hiện tại và vẫn giữ chức năng tải về/giọng đọc/duyệt để dạy.

## Kiểm chứng

70 kiểm thử liên quan qua (gồm Google, giọng đọc, cấu hình và tiến độ). Qt
Settings tám kiểm tra qua; luồng Google sáu nhóm kiểm tra qua ở hai kích
thước, không QML warning. Hồi quy Qt về nghẽn âm thanh vẫn qua: 200 thông
báo tiến độ, không broad refresh/WAV check trên UI, Dừng khoảng 343 ms.
Đây là các ca dữ liệu riêng/fixture, không phải benchmark dịch thực tế.

- Kiểm thử backend dùng key giả và HTTP fixture; bao gồm mã hóa, nhóm quota,
  dự trù đồng thời, chuyển key, cache, hủy, bảo vệ số liệu, HTTP và che lỗi.
- Kiểm thử pipeline tạo PPTX thật từ chữ/PPTX gốc, Notes VI/EN, giữ nguồn,
  không tạo voice/tự duyệt, phát hiện nguồn đổi, khóa job và nhập không trùng.
- Qt Settings và Qt luồng Google chạy bằng thư viện tạm. Lưu nhiều key,
  ẩn browser, đồng hồ/%, dịch fixture → PPTX cục bộ, tải về không voice, kiểm
  tra hai cỡ cửa sổ. Không gửi tài liệu/thông tin tài khoản thật của giáo viên.

Chưa có API key thật để kiểm tra dịch Google và đo thời gian bài thực tế.
Không sử dụng thời gian fixture để tuyên bố nhanh gấp bao nhiêu hoặc mọi môn
đã hoàn thiện. Bản thử độc lập và EXE/model/cache/reports không vào Git.
