# RC78 — Hoàn tất chuyển đổi và thu gọn Cài đặt

RC78 gộp các sửa đổi giao diện sau RC77 và sửa luồng tài liệu → chuyển
đổi → tạo giọng → dạy cùng Mascot.

- Màn hình xử lý giữ bước hiện tại, tiến độ, thời gian. Bỏ thông tin lặp;
  chỉ hiện cấu hình Google khi lỗi key/hạn mức cần xử lý. Nút Hủy màu đỏ
  mở xác nhận; xác nhận mới dừng và xóa lượt đang tạo. Lượt đã hủy không
  tiếp tục khi mở lại. Nếu lưu vừa hoàn tất, chỉ bài cùng request ID vào
  Thùng rác; không xóa file nguồn, bài khác, key hoặc hoàn lại bộ đếm.
- Trạng thái/đồng hồ cập nhật sau khi lưu. Sự kiện muộn từ lượt cũ không
  hạ tiến độ hoặc kéo trạng thái về đang chạy. Tự mở bước Giọng đọc; khi
  quay lại màn hình hoàn tất có nút mở lại đúng bài, không dịch lại.
- Thẻ lựa chọn giữ bố cục khi đổi thiết kế. Bỏ ghi chú thừa ở footer.
- Trang chủ có đúng bốn bước: Tải bài giảng, Chuyển đổi bài giảng,
  Tạo giọng đọc bài giảng, Dạy cùng Mascot; nút dẫn đến đúng chức năng.
- Tiêu đề luôn là Cài đặt, mô tả riêng theo từng tab. Google Dịch giữ
  nhập/lưu nhiều key, hướng dẫn/lấy key, đổi tên/xóa và bộ đếm từng key.
  Bỏ toàn bộ nhận/gửi key qua GitHub, cả module thực thi; giữ key DPAPI
  và lịch sử sử dụng hiện có. Không thay đổi hạn mức đã lưu khi thêm key.
- Phím đọc trong Mascot chia khu vực gán phím và sơ đồ mũi tên cỡ lớn,
  mô tả rõ lùi/tiến hiệu ứng hoặc slide và âm lượng ±5%. Cửa sổ hẹp xếp
  thành hai hàng; giữ nguyên cơ chế gán một/hai phím và phát/tạm dừng.
- Sửa khung công thức do BiliClass tạo khi có khoảng trống bên dưới;
  tính tọa độ đúng trong group, giữ XML công thức và cỡ chữ. Không dùng
  COM để viết lại nội dung công thức. Chỉ nhận bản sửa khi Office render
  kiểm tra lại và không phát sinh lỗi mới; không tự duyệt nội dung.

## Kiểm chứng

Qt Google dùng API fixture, PowerPoint thật, không gửi bài/key giáo viên
ra ngoài. Kiểm bấm Hủy/mở xác nhận/tiếp tục/xác nhận xóa, phản hồi đến
muộn, chặn xác nhận lượt cũ, tạo lượt mới dùng cache; không dịch lại khi
mở bài hoàn tất. Qt Settings kiểm cả bảy tiêu đề/mô tả; Qt Home kiểm
đúng nhãn và đường đi, không tự tổng hợp giọng hay bật trình chiếu.

Bài thật 51 slide được kiểm trên bản sao: khung English có công thức
ở slide 33 tràn chữ; tăng chiều cao trong khoảng trống đã xác minh.
PowerPoint kiểm lại từ 1 FAIL/50 CHECK thành 0 FAIL/51 CHECK. Toàn bộ
ZIP part ngoài XML slide 33 giữ nguyên; XML công thức giữ nguyên.
CHECK vẫn cần giáo viên đối chiếu; đây không phải duyệt nội dung tự động.

Lượt core cuối: 898 ca đạt, một warning dependency Starlette/httpx.
Nhóm Browser AI: 103 ca đạt lần đầu; một fixture điều hướng ERR_ABORTED
đạt khi chạy lại, cùng 14/14 ca Browser Translation. Lỗi này không phải
lỗi API Google của bài giáo viên. Log riêng trong reports/rc78.
13 luồng Qt Windows đạt, không QML warning; gồm Google hoàn tất/hủy,
Settings bảy tab, Home, phím tắt, lớp học, thư viện và phiên dạy. Sơ đồ
phím kiểm bố cục tại 1080/1366/1920. Native speaker export/roundtrip,
8 bài corpus và helper parent-exit đạt. Lượt integration cuối:
`reports/verification/20261019-000015/result.json`. Thông tin gói được
bổ sung sau kiểm chứng bản độc lập.
Giới hạn thực địa và thao tác chuột trực tiếp trên loa PPTX độc lập
của RC77 vẫn như [BUILD_RC77](BUILD_RC77.md); RC78 không chứng nhận lại
các thao tác đó chỉ từ kiểm thử Player API.
