# RC79 — Mascot tự theo môn của bài

RC79 gồm toàn bộ thay đổi của [RC78](BUILD_RC78.md) và bỏ hai bộ chọn
chế độ/môn phụ kiện trong Cài đặt Mascot. Phụ kiện tự theo bài đang gắn
với phiên dạy; khi chưa gắn thì theo bài đang chọn, cuối cùng là môn
trong hồ sơ. Vẫn có bật/tắt phụ kiện. Thiết lập fixed của bản cũ không
ghi đè môn thực tế; lưu cấu hình mới ghi auto, không sửa bài giảng.

53 ca liên quan giọng/phiên dạy/phím tắt đạt. Qt result/Mascot và phím
tắt Windows đạt; gồm tự đổi phụ kiện, ba cỡ bố cục phím và lưu lựa chọn.
Giữ bằng chứng 898 core/13 luồng Qt/native Office của mốc RC78; RC79
không tính đó là lượt chạy lại toàn bộ. Bản RC78 nội bộ đã qua cài/gỡ cô
lập, mẫu và hai ngôn ngữ VieNeu thật; không phát hành riêng RC78.

Kiểm Qt Settings nguồn qua `--check-voice-ui` đạt với 30 môn/phụ kiện,
nghe mẫu và lưu giọng, hủy preview đến muộn; không cảnh báo QML. Không
gọi Google hoặc suy luận model trong luồng này.

Gói cuối, kiểm tra frozen Settings và cài đặt được ghi sau khi hoàn tất.
