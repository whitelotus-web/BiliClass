# BiliClass: bốn kiểu chuyển đổi và kế hoạch thu gọn

Ngày 09/10/2026. Đây là định hướng mới cho mã nguồn, chưa phải bộ cài RC12.

## Quy trình chính

Nhập giáo án/tài liệu → chọn **Kiểu chuyển đổi** → chọn giữ PowerPoint gốc hoặc mẫu BiliClass → Chuyển đổi → xem trình chiếu → xác nhận Dùng để dạy.

Thông tin ngắn: tên bài, môn, khối; cấp học nằm trong tùy chọn thêm. Browser AI gửi prompt và bản sao tài liệu qua web ChatGPT đã đăng nhập, nhận PPTX, đọc ghi chú và chuẩn bị âm thanh. Không có lựa chọn API/OAuth/model dịch offline trong luồng nhập mới. Gửi/nhận thủ công vẫn là phương án phục hồi khi web gặp lỗi.

## Bốn cấu hình duy nhất cho bài mới

| Kiểu chuyển đổi | Chữ trên slide | Lời đọc trợ lý |
| --- | --- | --- |
| Hai cột song ngữ | Việt trái – Anh phải; dịch đầy đủ 1:1 từng ý | Cặp Việt–Anh bám slide |
| Song ngữ từng câu | Việt trên – Anh ngay dưới từng câu/bước | Cặp Việt–Anh bám slide |
| Tích hợp từ khóa | Câu Việt xen thuật ngữ Anh; lần đầu Việt (English), lần sau có thể dùng thuật ngữ Anh | Việt đọc ý chính; Anh đọc thuật ngữ/cụm ngắn đã tích hợp |
| Tiếng Anh 100% | Thay toàn bộ chữ Việt bằng Anh tại vị trí tương ứng; không có vùng Việt cứu trợ trên slide | Anh đọc nội dung; Việt tương ứng lưu riêng trong ghi chú |

Không chọn level và bố cục độc lập nữa. Bài cũ và gói đang xử lý vẫn đọc được theo cấu hình cũ; không tự chuyển đổi bài đã duyệt. Trường level/layout nội bộ trong bài mới chỉ là bộ chuyển tiếp cho các thành phần cũ, không là lựa chọn bổ sung và không thay đổi phương pháp trong prompt.

Prompt triển khai ở `app/conversion_formats.py`, theo bốn phương pháp người dùng cung cấp. Các yêu cầu chung bảo toàn kiến thức, công thức, số liệu, hình ảnh và hoạt ảnh được ghép với đúng một phương pháp.

## Giữ giáo án gốc

- PPTX: đúng số lượng/thứ tự slide, mỗi slide gốc tương ứng một slide đầu ra. Không thêm slide hỗ trợ, không tự tóm tắt hoặc bỏ nội dung. Quy tắc số slide cũng áp dụng nếu chọn mẫu cho một PPTX.
- Chỉnh chữ trong đối tượng gốc khi có thể, bảo toàn tối đa hoạt ảnh, Trigger, liên kết, video/âm thanh. Không biến cả slide thành ảnh.
- Slide kín/chữ Việt trong ảnh/hiệu ứng không giữ được: ghi rõ slide và hạn chế trong CHECK/báo cáo. Không âm thầm thu chữ quá nhỏ hoặc tuyên bố đã bảo toàn 100%.
- Word/PDF/ảnh/nội dung dán: dựng thành slide theo trình tự tài liệu và mẫu, không ép giữ số trang thành số slide.
- Tool so sánh số slide nguồn/kết quả khi nhận PPTX từ yêu cầu mới và cảnh báo nếu khác. Đây chưa phải kiểm chứng tự động độ đúng bản dịch hoặc bảo toàn hoạt ảnh.

## Voice, mascot và câu hỏi

Ghi chú gốc được giữ, khối `BILICLASS_NOTES:` thêm ở cuối chứa lời đọc với dòng `VI:` và `EN:`. Tool lấy khối cuối để tránh đọc lẫn ghi chú cũ. `CHECK:` và `QUIZ:` không được trộn vào âm thanh.

Các slide trọng tâm có thể có một câu hỏi bám nguồn trong dòng `QUIZ:` chứa JSON: `kind=single`, `vi`, `en`, các `options` có `vi/en`, đáp án `correct=A/B/C/D` và `rationale_vi/rationale_en`. Không đủ căn cứ thì bỏ câu hỏi, ghi CHECK. Không thêm slide quiz vào PowerPoint gốc.

Tool nhận câu hỏi hợp lệ vào đúng slide ở trạng thái nháp, bỏ câu không hợp lệ và báo vị trí cần kiểm tra. Xác nhận cả PowerPoint không tự duyệt câu hỏi; giáo viên duyệt trong Trợ giảng & Quiz trước khi sử dụng với lớp. Dữ liệu đáp án không phải lời đọc slide.

Trình chiếu dùng Microsoft PowerPoint trên máy, mascot trong suốt kéo tự do và giọng đọc theo slide thực tế. Nhận file không tự sửa file trả về. Khi nội dung thay đổi cần xem/xác nhận bản mới.

## Những phần giữ nguyên

Theo yêu cầu người dùng: **Cài đặt Chung, Giọng đọc, Mascot, Browser AI giữ cấu trúc hiện tại**. Chỉ hướng dẫn ở Song ngữ đổi thành bốn phương pháp. Không tự kết luận các cấu hình giọng/tài khoản đều đã nghiệm thu trên mọi máy.

Giữ thư viện bài, nguồn, ghi chú, giọng đọc offline/cache, trình chiếu PowerPoint, mascot, câu hỏi đã duyệt, sao lưu/khôi phục và cập nhật ứng dụng. Lớp học và báo cáo vẫn cần cho hoạt động trắc nghiệm; không gỡ chỉ vì chúng không nằm trong nút Chuyển đổi.

## Kế hoạch loại bỏ phần thừa

| Phần | Xử lý | Điều kiện trước khi xóa mã/gỡ khỏi bộ cài |
| --- | --- | --- |
| Level L0–L4 + bộ chọn bố cục riêng | Đã gỡ khỏi nhập bài mới; hướng dẫn Song ngữ chỉ còn bốn kiểu | Giữ bộ đọc cho bài/gói cũ; không viết lại bài giáo viên |
| Bộ chọn Browser/offline và chế độ giữ/bổ sung/slide Việt–Anh kế tiếp | Đã gỡ khỏi nhập bài mới | Luồng Browser là mặc định; bài cũ vẫn mở được |
| Bộ chọn level/bố cục trong editor của PPTX nhận về | Đã ẩn; hiện tên phương pháp, tránh đổi cấu hình mà tưởng file PPTX cũng đã thay đổi | Muốn đổi phương pháp thì chuyển đổi/nhận PPTX mới |
| Kết nối ChatGPT OAuth/Responses cũ | Gỡ khỏi sản phẩm ở đợt sau | Kiểm tra yêu cầu đang dở, bỏ lựa chọn cũ và phụ thuộc thật sự không còn dùng; không xóa hồ sơ người dùng |
| Engine dịch offline + tải model dịch/OCR phục vụ chuyển đổi mới | Đưa ra khỏi bộ cài chính ở đợt sau | Kiểm tra đường gọi editor/pack/đọc bài cũ; giọng đọc offline và model voice phải giữ |
| Thuật ngữ/kho kiến thức/menu dữ liệu dày | Đề xuất gom thành phần dữ liệu trợ giảng nâng cao | Giữ nội dung thầy cô đã duyệt và quyền xuất/sao lưu; chỉ gỡ giao diện trùng, không xóa dữ liệu |
| Gợi ý level trong báo cáo/hướng dẫn cũ | Thay bằng cách chọn một trong bốn phương pháp ở đợt sau | Không suy ra năng lực học sinh bằng ánh xạ máy móc level sang kiểu bố cục |
| Lớp học, QR và báo cáo | Giữ là tính năng tùy chọn khi dạy | Câu hỏi/đáp án cần duyệt; tách khỏi bước chuyển đổi để không tăng thao tác nhập bài |

Không xóa module/model/data hàng loạt trong đợt này. Cần rà đường gọi và thử mở thư viện/gói bài cũ trước khi gỡ phụ thuộc khỏi bản phát hành.

## Kiểm tra và giới hạn

Kiểm thử phải phủ bốn prompt độc lập, cấu hình lưu/mở lại, nguồn không đổi, PPTX tiếng Anh có lời đọc Việt riêng, câu hỏi liên kết slide/chưa duyệt, dữ liệu CHECK/QUIZ không vào voice và cảnh báo đổi số slide. Smoke Qt kiểm tra bốn lựa chọn → gói gửi → nhận file → xem trước Office → xác nhận bài → giữ câu hỏi nháp.

Web ChatGPT có thể đổi giao diện, mất phiên hoặc giới hạn tài khoản. Nghiệm thu luồng/gói bằng fixture không chứng minh chất lượng AI của bốn bài thật. Cần thử thực tế từng phương pháp bằng tài liệu giáo viên rồi phát hành bộ cài riêng cho máy thứ hai.

Kết quả ngày 09/10: 49 kiểm thử chuyển đổi/handoff/dispatch và 87 kiểm thử browser/Chrome/PowerPoint/readiness/pack/content đã qua; Qt handoff, Qt Browser fixture/Office và trình chiếu PowerPoint/mascot/giọng Anh thật đã qua. Cấu trúc và lưu Cài đặt qua với chế độ `--layout-only` (bỏ phát voice có ghi rõ phạm vi). Ca Cài đặt đầy đủ vượt thời gian chờ khi nghe thử giọng Việt VieNeu Hải Đăng; giữ cấu trúc tab, ghi nhận vấn đề runtime, chưa chứng nhận voice Việt ổn định.
