# RC168 · Mức đã kiểm chứng của bộ dịch ngày 25/10/2026

Kết luận: đủ cơ sở để tiếp tục cho giáo viên dùng thử; **chưa phải bộ dịch được
chứng nhận đúng mọi bài/mọi môn**, chưa thay mốc ổn định tạm RC167 và chưa tạo
bộ cài mới cho đợt nâng cấp này.

## Đã hoàn thành trong mã nguồn

- Bốn lựa chọn dịch riêng biệt. Chỉ dịch vụ được chọn hoạt động, không tự đổi
  dịch vụ khi lỗi. Google cũ, key/cache/bộ đếm và checkpoint được giữ.
- Thuật ngữ tự chạy nền: bỏ khung thiết lập, ô tích và nút lưu. Bài mới tự chọn
  ngữ cảnh, dùng từ điển nền/câu đã duyệt và tra cứu thêm khi cần.
- Kho mở rộng từ 495 lên **1.152 khái niệm**, tương ứng **2.774 mục theo môn**
  cho 30 lựa chọn môn/hoạt động giáo dục. Môn tích hợp dùng nhóm thành phần.
  Kho là tham chiếu Việt–Anh do BiliClass biên soạn, không phải từ điển chính
  thức của Bộ và không đủ để gọi là toàn bộ kiến thức chương trình.
- Tối đa ba lượt tra cứu mới mỗi bài; dùng lại mục đã biết để có thể tiếp tục
  học thêm các mục phía sau ở lượt bài mới. Mục chưa xác minh không được biến
  thành thuật ngữ khóa, đáp án chuẩn hoặc bản duyệt của giáo viên.
- Kiểm tra số liệu, token, công thức, trường hợp còn rõ nhiều văn bản Việt;
  thử sửa phần không đạt có giới hạn, giữ phần đã đạt, không nhận một bản còn
  thiếu như bài hoàn tất. Không có vòng lặp tự học hoặc gọi dịch vụ vô hạn.

## Kiểm tra dịch thật với mẫu tự biên soạn

Đã gửi các câu ngắn thuộc Toán, Sinh học và Tin học qua cấu hình bốn dịch vụ
hiện có trên máy. Không gửi bài giảng cá nhân. Bản mẫu gồm tiêu đề và câu về:
xác suất có điều kiện; quá trình dịch mã sử dụng thông tin RNA; xác thực danh
tính trước khi cấp quyền truy cập. Ghi nhận được cả tiêu đề dịch tại máy và
câu dịch bằng API; một số kết quả dùng lại cache đã kiểm tra.

Hai lỗi đã tái hiện và sửa:

1. Google/Apps Script từng trả “Cell use …” vì danh từ “cell” bị khóa số ít.
   Bỏ khóa mặc định trong câu cho danh từ đếm được này; lần thử sau trả
   “Cells use …”. Thuật ngữ vẫn dịch chính xác khi đứng riêng, khóa của giáo
   viên vẫn được ưu tiên.
2. Gemini từng chỉ dịch “xác suất” và để phần còn lại bằng tiếng Việt. Bộ kiểm
   tra mới từ chối kết quả đó, thử sửa một lần rồi vẫn chặn nếu chưa đạt. Sau
   khi sửa cách xử lý cụm dài để không khóa riêng “xác suất” trong “xác suất có
   điều kiện”, Gemini trả cả câu tiếng Anh về conditional probability.

Lần kiểm tra sau sửa nhận đủ kết quả tiếng Anh cho cả ba mẫu qua cả bốn dịch
vụ. Không quy đổi thành phần trăm chính xác, không suy rộng từ ba mẫu thành
chất lượng mọi môn. Các báo cáo API là dữ liệu máy cục bộ ngoài Git.

## Kiểm tra tự động và giao diện

Bộ kiểm tra gồm dữ liệu/nguồn, cô lập môn, thuật ngữ đứng riêng, ưu tiên khóa
giáo viên, tên riêng, công thức, ngữ pháp đếm được, phát hiện thiếu bản Anh,
thử sửa có giới hạn, cache/bộ đếm, nâng gói không mất dữ liệu, dừng/tiếp tục,
hàng đợi cũ/mới và sao lưu. Qt smoke dùng API giả lập cùng tệp PPTX thật,
không phải kiểm chứng chất lượng API thật trên toàn bộ slide.

Dung lượng gói tham chiếu khoảng **0,98 MB**; phần tăng trong DB khoảng
**1,03 MB**, không tải thêm mô hình. Cách chạy kiểm tra và số đo có giới hạn
phạm vi ở [tài liệu thuật ngữ](TRANSLATION_KNOWLEDGE_RC168.md).

## Chưa xác minh đầy đủ

- Ngữ nghĩa của mọi bài thuộc mọi môn/lớp, mọi dạng thuật ngữ chuyên sâu.
- Nội dung trong ảnh, chữ bị chia qua nhiều khung, câu rất dài và bố cục dày.
- Đơn vị tiếng Việt nằm trong vùng công thức bất biến; tự sửa đáp án sai từ
  nguồn. Những vùng này cần giữ nguồn và đối chiếu, không đoán rồi chứng nhận.
- Chuyển đổi lại và duyệt toàn bộ bài Apps Script 16 slide đã kiểm tra trước
  đây sau tất cả sửa đổi mới. Bài hoàn thành cũ không tự thay bằng bản dịch mới.

Không cần giáo viên nhập tay trước toàn bộ từ điển. Tuy nhiên, việc tool tự
tra cứu và ghi nhớ không thay thế khâu xem lại nội dung bài trước khi dạy/nộp.
