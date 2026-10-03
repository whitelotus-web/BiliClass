# Giữ thiết kế PowerPoint khi thêm song ngữ

Mã nguồn ngày 03/10/2026 giữ PPTX làm đầu ra chính của **Giữ bài giảng của tôi**. Không cần chọn template. Nguồn lưu riêng theo hash, không ghi đè. Những thay đổi này chưa có trong release rc12.

1. Chọn PPTX tại **Tạo bài học mới**, kiểm tra đánh giá VI/EN/song ngữ/trộn, chọn môn/khối, L0–L4 và cách chuyển đổi.
2. **Dịch phần còn thiếu** tạo nháp tối đa 50 đoạn/lượt, giữ cặp có sẵn và đoạn khóa/duyệt. Kiểm tra rồi duyệt từng đoạn; trợ giảng, câu Anh dễ và quiz cần duyệt riêng.
3. **So sánh gốc / song ngữ** hiển thị hai bản cạnh nhau bằng Microsoft PowerPoint trên Windows. Đây là ảnh tĩnh; kiểm tra animation/trigger/audio/video trong PowerPoint thật.
4. **PPTX** lưu bản mới; **Trình chiếu song ngữ** điều khiển PowerPoint và mascot theo mapping slide nguồn, kể cả trang hỗ trợ.

| Cách chuyển đổi | Kết quả |
|---|---|
| Bổ sung theo L0–L4 | L0–L3 giữ chữ gốc, thêm panel hỗ trợ ở vùng trống; slide kín/có hiệu ứng/đối tượng xoay dùng trang hỗ trợ kế tiếp và giữ nguyên XML slide gốc. L4 thay chữ trên bản xuất bằng Anh; Việt giữ trong dự án cho VI Rescue. |
| Giữ nguyên + trợ giảng | PPTX xuất là bản sao nguyên file nguồn; phù hợp bài đã song ngữ/đặc biệt phức tạp. Không cần duyệt để sao chép nguyên file, nhưng mascot/audio/lớp chỉ dùng nội dung đã duyệt. |
| Slide Việt/Anh kế tiếp | Bản gốc đi kèm bản dịch trên cùng thiết kế. Slide chỉ hình hoặc chữ hai ngôn ngữ giống nhau không bị nhân đôi. |

Theo level: L0 dùng từ khóa, L1 thêm câu lớp học, L2 câu Anh dễ, L3 bản Anh đầy đủ, L4 English + VI Rescue. Tất cả nội dung bổ sung cần duyệt. L2 thiếu câu dễ thì lấy câu đầu bản Anh đã duyệt và báo rõ; không tự đơn giản hóa kiến thức. L0/L1 thiếu thuật ngữ/câu hỗ trợ thì báo thiếu.

Nguồn đã song ngữ giữ cặp hiện có ở L0–L3, không thêm bản dịch trùng. Giữ thiết kế cũng đồng nghĩa không tự xóa phần Anh sẵn có để giảm level. Nguồn chỉ Anh giữ chữ Anh và bổ sung phần Việt đã duyệt.

## Giới hạn

- Nhận diện/ghép cặp là gợi ý, không chứng minh cùng nghĩa. Bảng giữ dấu | phân cột; giáo viên kiểm tra trước duyệt.
- Chỉnh các phần OOXML cần thiết, giữ tài nguyên/theme nguồn. Biểu đồ bản sao có dữ liệu riêng. Chữ chart/SmartArt/công thức nhúng/hình có chữ và media liên kết ngoài chưa được dịch đầy đủ.
- Panel dùng khoảng trống theo bounding box và ước lượng chữ. Master/hình nền phức tạp vẫn cần đối chiếu; không bảo đảm mọi slide không tràn. Trang hỗ trợ dùng nền/theme nguồn cùng panel chữ, không tự thiết kế lại bài.
- L4/cặp slide kế tiếp có giới hạn giảm cỡ chữ; quá dài hoặc không khớp ô nguồn thì báo để rút gọn, nhập lại hoặc dùng template.
- PPTX chỉ ảnh lớn được thử OCR và gợi ý template. Không OCR toàn bộ chữ trong mọi hình của slide vốn có text.

App cache bản tạm theo nội dung/cấu hình/hash; sửa bài làm cache cũ hết hiệu lực. Xuất OOXML không cần Office; so sánh và trình chiếu cần Office. Không cần build lại exe cho từng lần thử bài.

Gói .biliclass lưu nguồn, VI/EN, level/mode, trợ giảng/quiz/audio và thuật ngữ/giọng/mascot tham chiếu. Người nhận duyệt lại; tham chiếu không tự thay Cài đặt hoặc thuật ngữ máy nhận. Xem [quy trình chung](INPUT_WORKFLOW.md).

Kiểm chứng: Office mở/render cả năm level trên fixture có chữ, bảng, biểu đồ sửa được; render slide giữ nguyên trong nhánh trang hỗ trợ giống hệt nguồn. Qt smoke xác nhận đánh giá đầu vào, điều khiển và màn so sánh. Chưa nghiệm thu mọi bài thật/hiệu ứng phức tạp.
