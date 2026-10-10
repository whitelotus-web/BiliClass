# Vận hành Browser AI sau khi tham khảo VeoSuite

Ngày 10/10/2026. Tham khảo mã nguồn `VeoSuite_V3` trên máy này; chỉ đọc phần browser, không thay đổi VeoSuite hoặc dùng hồ sơ đăng nhập của ứng dụng đó.

## Những điểm áp dụng cho BiliClass

| Phần tham khảo trong VeoSuite | Cách áp dụng |
| --- | --- |
| `services/browser_profile_identity.py`, `browser_lifecycle.py` | Mỗi tài khoản giữ một Chrome profile riêng của BiliClass. Trước mở, kiểm tra có Chrome đang dùng đúng thư mục đó không. Nếu bận, giữ nguyên profile và endpoint đang hoạt động; không gắn vào hoặc đóng tiến trình khác. |
| `services/browser_ai.py`: kiểm tra phiên và cooldown | Đăng nhập, kết nối tạm gián đoạn và hết lượt dùng là ba trạng thái riêng. Một lần kiểm tra đăng nhập thành công không chứng minh hạn mức đã được cấp lại. |
| `docs/browser_pool_20260927.md` | Timer mỗi phút chọn tối đa một profile cần kiểm tra, chỉ khi tool rảnh. Phiên bình thường kiểm tra sau hai giờ; lỗi mạng/browser sau năm phút. Không tự mở lại profile cần đăng nhập hoặc xác minh. Bấm Chuyển đổi có thể kết thúc kiểm tra nền rồi tiếp tục bài, không yêu cầu đăng nhập lại chỉ vì đang kiểm tra. |
| `services/browser_ai_worker.py`: mở browser nền | Chrome dùng renderer thật, đặt cửa sổ ngoài toàn bộ vùng màn hình và ẩn cửa sổ thuộc tiến trình do BiliClass mở. Bỏ thu nhỏ cửa sổ; bật các cờ giữ renderer/timer nền hoạt động để thao tác composer/menu/tải tệp ổn định hơn. Đăng nhập vẫn là Chrome thường cho người dùng thao tác. |
| `services/browser_reasoning.py` | Quan sát toggle Think, menu Tools và mức suy luận ở composer/model. Chọn mức cao nhất trong các mục đang hiện, được phép dùng; bỏ mục nâng cấp/không được phép. Đọc lại trạng thái chọn, không bấm nút trong nội dung bài/chat. Có lựa chọn nhưng chưa xác nhận được thì dừng trước gửi; không có lựa chọn riêng thì giữ mặc định web và ghi đúng như vậy. |
| Worker lưu kết quả và trạng thái gửi | Giữ journal BiliClass đã có: account, URL, trạng thái gửi, số câu trả lời và hash PPTX. Tiếp tục bài đã gửi bằng đúng tài khoản/cuộc trò chuyện; không đổi tài khoản khi chưa rõ đã gửi hay chưa. Tệp đã nhận và kiểm tra có thể nhập tiếp dù phiên web hết hạn/hết lượt. |

## Luồng sử dụng

1. **Browser AI:** thêm tài khoản, đăng nhập trong Chrome riêng, bấm kiểm tra/lưu. Giữ cấu trúc Cài đặt đã được thống nhất; không thêm bảng điều khiển browser mới.
2. **Bài giảng:** chọn tài liệu, một trong bốn kiểu chuyển đổi, giữ thiết kế gốc hoặc mẫu BiliClass rồi bấm Chuyển đổi.
3. Chọn tài khoản còn dùng được theo thứ tự ưu tiên gói hiện tại trên web. Lỗi mạng chỉ tạm hoãn tài khoản cho bài mới; giữ phiên đã lưu. Bài đã gửi luôn giữ tài khoản cũ.
4. Xác nhận phiên/model/suy luận, kiểm tra prompt và đầy đủ đính kèm rồi gửi. Chờ kết quả hoặc phục hồi có giới hạn theo journal.
5. Tải và kiểm tra PPTX, lưu bài và chuẩn bị lời đọc Anh–Việt. Giáo viên xem trước, xác nhận rồi trình chiếu bằng PowerPoint cùng mascot, voice và nội dung trợ giảng đã duyệt.

## Hạn mức và lỗi

- Chỉ thông báo hạn mức của giao diện web mới tạo cooldown; câu trong tài liệu hay chữ “try again later” riêng lẻ không phải bằng chứng hết lượt.
- Nếu thông báo có thời gian tương đối như “try again in 2 hours”, lưu thời điểm có thể thử lại. Nếu không có, tạm hoãn 30 phút. Khoảng 30 phút là chính sách thử lại của BiliClass, không phải lịch cấp lượt do ChatGPT xác nhận.
- Đến thời điểm thử lại vẫn giữ dấu đã gặp hạn mức, chỉ cho phép thử. Kiểm tra phiên không xóa dấu này; nhận được một PPTX mới hợp lệ mới xóa cooldown. Nhập lại tệp đã tải không chứng minh hạn mức được cấp lại.
- Hết phiên/cần xác minh thì cảnh báo đăng nhập hoặc xác minh lại. Profile đang bận, hủy tác vụ hoặc mạng tạm gián đoạn không bị báo thành mất đăng nhập.
- Sau khi gửi, không chuyển tài khoản để vượt hạn mức. Giữ bài để tiếp tục; không tự giải xác minh.

## Phạm vi

Không đưa pool browser chạy song song, profile clone, token/cookie của VeoSuite, dịch vụ browser trả phí hoặc API key vào BiliClass. BiliClass vẫn dùng worker Qt hiện có và điều khiển giao diện web của Chrome cài trên máy. Chưa có số dư hạn mức chính thức để hiển thị; không suy đoán Free/Plus từ model hay danh tính Chrome/Google.

Các phép thử browser dùng Chrome thật với trang/tệp fixture chặn mạng hoặc localhost; không gửi tài liệu thật lên ChatGPT. Chúng xác minh cơ chế profile, lựa chọn điều khiển, gửi/nhận và phục hồi, không bảo đảm giao diện ChatGPT luôn giữ nguyên hoặc chất lượng bản dịch của mọi tài liệu.

Đã qua 98 ca nhóm browser/account/dispatch/Chrome/handoff, 22 ca health/reasoning chạy sau bổ sung nhường probe (có một ca QThread mới), ba ca chặn xóa/khóa/cooldown sau sửa cuối. Qt Browser AI nhận PPTX/lời đọc fixture, xem trước bằng Office thật, kiểm tra quota không bị xóa qua health probe và xóa đúng từng profile; không QML warning. Ruff và diff sạch. Mã nguồn mới chưa được đóng gói thành bộ cài mới.
