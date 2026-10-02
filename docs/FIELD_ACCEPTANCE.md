# Phiếu nghiệm thu thực địa BiliClass RC2

Phiếu này dùng để hoàn tất các mục còn mở trong [TASKS.md](TASKS.md). Kết quả trên máy phát triển ở [APP_RESULTS.md](APP_RESULTS.md) là mốc so sánh, không thay cho kết quả tại lớp. Bài “Lực ma sát” trong ảnh thiết kế chỉ là ví dụ; chọn bài thật của giáo viên ở nhiều môn THPT.

## Ghi thông tin môi trường

| Mục | Điền khi thử |
|---|---|
| Ngày, người thử, trường/phòng |  |
| Windows, CPU/RAM, màn hình laptop, DPI |  |
| Máy chiếu/TV, Extend hay Duplicate, Presenter View |  |
| PowerPoint, voice/OCR EN/VI sẵn có |  |
| Router/hotspot, Internet bật/tắt, client isolation, số điện thoại Android/iPhone |  |
| Phiên bản app, hash `BiliClass.exe`, hai gói dịch đã cài |  |

## Kịch bản cần ghi kết quả

Mỗi dòng ghi **Đạt / Lỗi / Chưa thử**, thời gian hoặc số đo nếu có, ảnh/log/tệp kết quả, và cách tái hiện lỗi. Dùng bài riêng của giáo viên; không đưa tài liệu/học sinh có dữ liệu nhạy cảm vào báo cáo chia sẻ.

| Ca | Cách thử và tiêu chí quan sát | Kết quả/bằng chứng |
|---|---|---|
| Cài sạch | Trên Windows không cài Python: mở `dist/rc2/Setup.cmd`, cài hai `.bclanguage` từ USB, mở app, dịch VI→EN và EN→VI; gỡ app, thư viện còn. |  |
| Nâng cấp | Với RC1 đã có bài: đóng RC1, cài RC2, mở bài cũ/chỉnh sửa/lưu; gỡ RC2 và xác nhận bài còn. |  |
| Đa môn | Ít nhất năm bài ngắn phủ khối 10–12 và nhóm công thức, thuật ngữ khoa học, diễn giải, bảng dữ liệu, môn tự tạo; thử hai chiều dịch, sửa/duyệt, L1→L2, memory đúng môn. Giáo viên đánh dấu từng lỗi thuật ngữ/nghĩa/số. |  |
| Nguồn/PowerPoint | So hash nguồn trước/sau, chuyển tiến/lùi/nhảy slide, animation/video, Presenter View và chế độ thủ công khi mất đồng bộ; kiểm tra ghi chú/đáp án không lên màn chiếu. |  |
| Lớp song ngữ | Tắt Internet nhưng giữ LAN; chuẩn bị bài có/không quiz, phát âm EN, giải thích/ví dụ đã duyệt, VI Rescue, đổi layout/level, hoàn tất một tiết. Ghi thời gian chuẩn bị và RAM/khởi động. |  |
| Điện thoại thật | Ít nhất năm Android/iPhone trên cùng Wi-Fi: vào QR, trả lời/đổi đáp án, mất mạng rồi trở lại, khôi phục bằng mã; không tăng mẫu số khi gửi lại và không lộ đáp án trước công bố. |  |
| Tải lớp | Tối thiểu 40 kết nối, thử 50; đo riêng thời gian điện thoại→server và server→dashboard p95, mục tiêu phần server→dashboard ≤500 ms. Router/hotspot phải nhận đủ số máy. |  |
| Mạng đổi | Đổi IP, chiếm cổng cũ rồi khôi phục phiên; quét QR mới và nhập mã khôi phục, giữ chỗ/đáp án. Kiểm tra cả trường hợp router bật client isolation. |  |
| Báo cáo | Đóng/công bố câu hỏi, giải thích lại và recheck; xem mẫu số, xuất CSV, khởi động lại vẫn mở kết quả. |  |
| Hiển thị/âm thanh | DPI 100% và 125%, Extend/Duplicate, rút/cắm máy chiếu, loa lớp, giọng và OCR Việt nếu Windows có gói ngôn ngữ. Ghi rõ trường hợp chưa có backend. |  |

## Quyết định sau buổi thử

Ghi lỗi **chặn dạy** (không thể tiếp tục tiết hoặc mất dữ liệu) riêng và sửa trước khi đánh dấu V1. Với lỗi dịch, lưu câu nguồn, bản dịch máy, bản sửa được giáo viên duyệt, môn/khối và level để phân loại. Ghi `Chưa thử` cho mọi ca thiếu thiết bị/người thử; không suy ra `Đạt` từ test loopback hoặc ảnh màn hình giả lập.

Mục tiêu hiệu năng và kịch bản gốc ở [BUILD_PLAN.md](BUILD_PLAN.md). Cập nhật bằng chứng vào [APP_RESULTS.md](APP_RESULTS.md) và chỉ sau đó đánh dấu các ô nghiệm thu thực địa trong [TASKS.md](TASKS.md).
