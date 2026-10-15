# RC41 — Việt và Anh trên cùng slide

Ngày 16/10/2026. Yêu cầu mới thay thế phương án RC40 dùng một trang Việt rồi
một trang Anh. Google Dịch chỉ nhận phần văn bản; BiliClass dựng bản song ngữ
tại máy từ gói PowerPoint gốc. Browser ChatGPT/Gemini tiếp tục được ẩn.

## Bố cục

- Hai cột Việt–Anh trong vùng chữ gốc; tiêu đề Việt trên, Anh dưới, cùng font,
  Anh nhỏ hơn và in nghiêng. Khung hẹp, bảng và vùng công thức nằm sát hình
  dùng từng cặp trong cùng khung để tránh hai cột quá hẹp.
- Giữ tài nguyên nền, hình, theme, layout và tài nguyên nhúng. Căn lại vùng
  chữ trong giới hạn trang và vùng hình kế bên; bỏ tab tuyệt đối khi chia cột,
  căn lại khoảng dòng, lề và cỡ chữ. Không dựng lại toàn bài trên nền trắng.
- Khung nhiều đoạn quá chật được chia theo cặp ý sang trang tiếp nối; mỗi
  trang vẫn có cả hai ngôn ngữ cùng hình và tiêu đề. Giữ công thức đi cùng
  câu giải thích trước nó; không tách thân câu hỏi trắc nghiệm sang trang mới.
  Một đoạn/công thức không thể chia an toàn vẫn cần kiểm tra nếu không vừa.
- Đáp án chỉ gồm số/đơn vị không cần nhân đôi. Loại bản chữ phụ trùng hoàn
  toàn khi có bằng chứng hình học và không thuộc hiệu ứng nguồn.
- Giữ XML công thức và số liệu. Sao chép hành vi hoạt hình của cột Việt sang
  cột Anh trong cùng container thời gian, cấp ID clock riêng; cặp trong cùng
  khung mở rộng đúng phạm vi đoạn. Không thêm một click độc lập cho bản Anh.
- Lưu ánh xạ từng trang về slide nguồn. Các cặp được kiểm tra bằng đoạn XML
  nhìn thấy, có loại run trong suốt; ghi chú không được dùng thay bằng chứng
  bản Anh trên slide. Xóa hoặc ẩn bản Anh phải làm kiểm tra thất bại.
- Giữ các manifest cũ để đọc bài đã lưu. Bài RC40 có sẵn không tự bị thay thế.
  Lưu/tải PowerPoint trước, tạo voice vẫn là bước tùy chọn riêng.

## Kiểm chứng

Nguồn thật 48 slide, khoảng 71 MB, được dựng và render toàn bộ bằng PowerPoint.
Bản kiểm tra có 51 trang, gồm ba trang tiếp nối từ nguồn 10, 17 và 22; không
có trang tách riêng ngôn ngữ. Đã đối chiếu ảnh toàn bài và các khung nhiều
chữ/công thức. 99 phần tài nguyên giữ nguyên byte; các cặp chữ được kiểm tra
trên cùng trang. Kết quả đo không còn FAIL về chữ tràn, vẫn giữ CHECK.

Lượt rộng cuối chạy 124 ca liên quan thành công, gồm kiểm tra chữ trong suốt,
đáp án số, công thức và phân trang. Sau khi thu gọn khung nhãn ngắn đã chạy
lại 22 ca liên quan. Đây là các tập chồng nhau, không cộng thành số ca độc lập. Qt smoke
dùng API fixture kiểm tra lưu key, chuyển PPTX qua API chữ, tiến độ/đồng hồ,
tải bài và bước voice riêng ở hai kích thước cửa sổ, không cảnh báo QML.

Lượt chạy luồng Google với cache dịch sẵn mất khoảng 24 giây để lưu bài,
khoảng 42 giây khi tính cả render kiểm tra toàn bộ. Đây là phép đo tại máy,
không phải tốc độ lần đầu gọi API hoặc cam kết cho mọi giáo án. Các lượt
căn chữ sau đó không gửi lại tài liệu hay dịch lại toàn bài.

## Giới hạn cần giữ rõ

Chữ trong ảnh, nhãn SmartArt/biểu đồ và bitmap fallback chưa được OCR/dịch.
Khung ngắn không thể chia có thể cần cỡ chữ tới 14pt; báo cáo vẫn cảnh báo
chữ nhỏ. Từ chuyên môn do Google dịch cần giáo viên đối chiếu theo ngữ cảnh.
Giữ/sao chép timing không chứng nhận mọi trạng thái click, trigger hay hình
khoa học. Không tự duyệt bài, không xóa CHECK để tạo cảm giác đã hoàn thiện.

Key, bài giảng thật, bản dịch cache, ảnh render, thư viện và EXE không đưa vào
Git. RC41 là mốc mã nguồn/bản thử tại máy; bộ cài trên GitHub Releases được
quản lý riêng, không tự nhận đã phát hành qua nút cập nhật.
