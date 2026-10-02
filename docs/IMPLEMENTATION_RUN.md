# Triển khai theo yêu cầu hoàn tất kế hoạch

Cập nhật 30/09/2026. Yêu cầu trực tiếp được giữ xuyên suốt: làm tiếp các nhóm tính năng theo kế hoạch, ưu tiên Anh–Việt đa môn THPT; sau đó dùng thử để tối ưu.

Đã triển khai lần lượt nền tảng và backup, nhập/duyệt/gói bài, memory và bảo vệ nội dung, trợ giảng/PowerPoint/màn hình lớp, lớp học LAN, báo cáo, OCR/xuất PPTX, mascot/onboarding, bộ cài và gói ngôn ngữ. Mã nguồn và bộ kiểm tra ở `app/`, `scripts/`, `tests/`; bản Windows ở `dist/BiliClass`.

Trong kiểm tra tích hợp đã sửa: câu trả lời bị tạo lại nút gây mất focus; lựa chọn không khóa ngay khi mất mạng; phiên khôi phục đổi cổng làm mất phiên trình duyệt; kết quả tác vụ hủy đến muộn; lỗi native OCR cần cách ly; phụ thuộc đóng gói và Uvicorn formatter khi chạy `.exe` không có console.

Theo dõi kết quả hiện hành tại `APP_RESULTS.md`, khả năng/giới hạn tại `STATE.md`, các điều kiện chưa nghiệm thu tại `TASKS.md`. Các mục cài sạch, thiết bị lớp học thật và giáo viên đánh giá không được tự đánh dấu đạt. Không có lịch tự chạy nền hoặc tin nhắn gửi người khác được tạo.
