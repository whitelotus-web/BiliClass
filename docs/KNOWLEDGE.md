# Kho kiến thức và bộ nhớ giáo viên

Trang **Kho kiến thức** hoạt động offline, có tìm kiếm, lọc môn/cấp, nguồn gốc và nhập gói `.biliknowledge`. Gói tích hợp đầu tiên có 26 mục tra cứu và 4 nguồn tham khảo chính thức. Đây là gói khởi đầu về thuật ngữ giáo dục/danh mục môn THPT, chưa phải kho kiến thức đầy đủ cho mọi môn.

Thứ tự dịch: đoạn khóa giữ nguyên; thuật ngữ riêng khớp chính xác → đoạn giáo viên đã duyệt cùng môn → kiến thức nền → dữ liệu online đã lưu có nguồn → model offline. Nếu có nhiều bản giáo viên duyệt, hiện lựa chọn. Nội dung mới luôn là nháp cần duyệt. Dữ liệu online chưa có chức năng tìm/tải trực tiếp; chỉ có thể nhập trong gói, gắn `source_type=online_reference`.

Tool học dần bằng cách dùng lại các đoạn đã duyệt và thuật ngữ riêng. Sửa nguồn khiến trạng thái duyệt hết hiệu lực; các đoạn nháp không được dùng làm bộ nhớ đã duyệt. Đây là tích lũy/tra cứu dữ liệu trên máy, chưa có huấn luyện lại trọng số model, đồng bộ bộ nhớ giữa hai giáo viên hay tự thu thập Internet.

Nguồn Bộ GD&ĐT năm 2026 trong gói thuộc chính sách đánh giá và bảo đảm chất lượng, không thay thế chương trình môn học. Metadata nguồn, bản dịch và diễn giải do BiliClass biên soạn đều cần đối chiếu tài liệu gốc. Không sao chép toàn văn sách hoặc văn bản vào gói này.

Gói kiến thức là ZIP gồm `manifest.json`, `sources.json`, `entries.json`. Import kiểm tra schema, kích thước và liên kết nguồn rồi thay một gói trong giao dịch SQLite. Không ghi đè thuật ngữ riêng. Có thể cập nhật dữ liệu bằng gói mới mà không đóng gói lại EXE sau khi ứng dụng hỗ trợ định dạng này. RC12 chưa hỗ trợ gói kiến thức; chức năng hiện có trong bản mã nguồn.

Tạo gói bằng môi trường dự án:

```powershell
.\.venv\Scripts\python.exe scripts/build_knowledge_pack.py app/assets/knowledge/vn_education_foundation_2026.json output/vn-education-foundation-2026.biliknowledge
```

SQLite chuyển lên schema 3, có sao lưu trước khi chuyển từ schema 2. Sau chuyển đổi, RC12 không đọc được schema mới; dùng bản mã nguồn mới hoặc bản phát hành tiếp theo. Dữ liệu cá nhân và gói ZIP tạo ra không được đưa vào Git.
