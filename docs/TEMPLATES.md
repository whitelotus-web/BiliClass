# Mẫu bài giảng song ngữ

Khi nhập PowerPoint, cách mặc định hiện tại là **giữ thiết kế gốc và thêm song ngữ**: xem [SOURCE_POWERPOINT.md](SOURCE_POWERPOINT.md). Bộ mẫu dưới đây dành cho văn bản/tài liệu khác, hoặc khi giáo viên bỏ **Giữ thiết kế gốc**. Các nút chọn mẫu và loại slide được ẩn khi giữ thiết kế PowerPoint.

Bản mã nguồn có ba bộ mẫu: **Chuẩn lớp học**, **Trực quan**, **Luyện tập & tương tác**. Mỗi bộ có 14 slide tham khảo sửa được trong PowerPoint. Xem mẫu tại **Tạo bài học mới → Xem mẫu bài giảng**, hoặc mở bài rồi bấm **Mẫu**. **Dùng mẫu này** chọn kiểu dạy cho bài; **Mở PowerPoint mẫu** mở bộ tham khảo.

Thư viện khối gồm tên bài, mục tiêu, khởi động, từ khóa, khái niệm, giải thích, hình và chú thích, so sánh, công thức/quy tắc, ví dụ theo bước, luyện tập, hỏi lớp, kiểm tra hiểu bài và tổng kết. Trong vùng biên tập, **Loại slide** cho chọn khối phù hợp với đoạn đang xem. Phân loại khi nhập chỉ là gợi ý theo dấu hiệu văn bản. Đổi loại slide giữ cặp dịch và trạng thái duyệt, nhưng làm hết hiệu lực bản chuẩn bị để kiểm tra lại bố cục.

Nội dung gốc và thứ tự các đoạn được giữ. Mẫu không tự bổ sung mục tiêu, lời giải hoặc quiz và không ép bài có đủ 14 phần. Trình tự gợi ý trong cấu hình là tài liệu hướng dẫn, chưa tự sắp lại bài. File tham khảo chứa chỗ điền nội dung trong ngoặc vuông; chúng chưa phải bài giảng để dạy ngay.

App và trình xuất PPTX dùng chung khung 16:9, vùng chữ, màu và cỡ chữ từ `app/lesson_templates.py`. Trang dài được chia theo các cặp dòng tương ứng. Ý đơn lẻ quá dài sẽ báo cần tách đoạn, không tự cắt mất chữ khi xuất. Phép ước lượng chữ là bảo thủ; vẫn cần xem trước vì PowerPoint và Qt có thể ngắt dòng khác nhau.

Khối hình có thể lấy ảnh thường đầu tiên từ slide PPTX liên kết; nếu chưa có ảnh thì bài vẫn dùng vùng chữ rộng. Bản xuất còn giữ các slide ảnh nguồn theo cách đã có. Công thức dạng đối tượng, biểu đồ, video và hiệu ứng nguồn chưa được tái dựng đầy đủ. Level và bốn bố cục song ngữ tiếp tục theo quy tắc hiện tại; chọn template không thay đổi thiết lập Cài đặt.

File tham khảo được tạo từ cùng cấu hình, không phải nguồn kiến thức môn học:

- [Chuẩn lớp học](../app/assets/templates/standard-classroom.pptx)
- [Trực quan](../app/assets/templates/visual-classroom.pptx)
- [Luyện tập & tương tác](../app/assets/templates/practice-classroom.pptx)

Tạo lại kế hoạch mẫu bằng môi trường dự án:

```powershell
.\.venv\Scripts\python.exe scripts/build_template_plans.py reports/template-build/plans.json
```

`scripts/build_template_decks.mjs` dùng Node.js và `@oai/artifact-tool` được cung cấp qua biến `ARTIFACT_TOOL_NODE_MODULES`, tạo ba file nháp trong thư mục staging. Chạy kiểm tra cấu trúc, font, khung chữ và render trước khi thay file tham khảo. App dùng bộ mẫu tích hợp, không cần Node.js khi chạy.
