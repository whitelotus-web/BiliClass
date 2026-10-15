# Tối ưu lõi BiliClass — RC35

Ngày 15/10/2026. Đây là mốc triển khai từ
[kế hoạch tối ưu](OPTIMIZATION_PLAN_2026-10-15.md), không phải nghiệm thu tất cả
các ý tưởng nghiên cứu hoặc mọi bài giảng của mọi môn.

## Đã thay đổi

- **Voice:** giữ WAV gốc theo nội dung/giọng/model; biến thể tốc độ lấy từ WAV
  gốc bằng WSOLA. Giữ nguyên khóa WAV và audio cũ, cùng một giọng đọc VI/EN.
  Hai yêu cầu đồng thời không chạy mô hình hai lần cho cùng đoạn.
- **Nhập/mở bài:** worker dùng kết nối SQLite riêng; bản ghi bài hoàn chỉnh được
  công bố một lần, không có bản VI-only trung gian. Request ID và transaction
  ngăn tạo trùng khi khôi phục giữa lúc đã lưu bài và chưa ghi xong journal.
  Hash/chuẩn bị preview nằm ngoài luồng giao diện; tránh đọc file hai lần trong
  cùng phép kiểm chứng. Inspection nội bộ chỉ dùng lại khi khớp hash file đã lưu.
- **Nguồn:** sao chép có giới hạn sang tệp tạm, xác minh hash rồi đổi tên. Khi
  gặp bản sao cắt cụt mang tên hash cũ, nhập lại từ nguồn nguyên vẹn sẽ phục hồi;
  thất bại không công bố tệp nguồn mới dở dang.
- **Bản dịch/bố cục:** kiểm tra cỡ chữ thật thay vì giả định 18 pt; nhận diện
  đối tượng có nhánh tương thích để không bỏ sót chữ/công thức. Tăng kiểm tra
  thiếu thân bài/dòng. Tiêu đề chế độ từ khóa vẫn Việt trên/Anh dưới; hỗ trợ
  thống nhất font/in nghiêng cho cặp tiêu đề nằm trong hai hộp riêng. Vùng đã
  là English chỉ giữ nguyên XML khi phản hồi đã xác nhận giữ nguyên nội dung.
- **Kiểm tra:** câu Anh có ký hiệu nguồn “Đ” không bị coi là vùng Việt. Chỉ phân
  loại riêng chuỗi vốn có khi đối chiếu đúng đoạn và tọa độ với nguồn; không
  miễn kiểm tra lỗi tràn hoặc nội dung mới sai. URL/mã rác không được đọc ở cả
  hai ngôn ngữ.
- **Tự sửa:** xử lý giãn dòng cố định quá lớn trong hộp đã đo được tràn; hỗ trợ
  placeholder ngang. Mọi sửa đổi phải render lại và không thêm lỗi trước khi
  được nhận. Cache ảnh/đo chữ đã xác minh được truyền giữa các lượt kiểm tra;
  việc mở preview một slide không làm rơi cache của các slide khác.
- **Dung lượng:** kiểm tra chỗ trống trước khi chuẩn bị yêu cầu, dùng browser
  và suy luận voice. Hết dung lượng là lỗi lưu trữ, không phải mất đăng nhập;
  không tự gửi lại hoặc đổi tài khoản để xử lý lỗi này. WAV đã có vẫn phát được.
- **Mở browser:** lọc tên tiến trình trước khi đọc command line, tránh truy vấn
  chi tiết mọi ứng dụng Windows để tìm chủ profile. Vẫn chặn profile Chrome
  đang mở; không chiếm phiên hoặc đóng browser của người dùng.
- **Số đo:** bản ghi tiến độ có thời gian riêng của ghép, kiểm tra, render,
  lưu nguồn và nhập thư viện. Chỉ là dữ liệu kỹ thuật tại máy, không hiển thị
  thao tác nội bộ lên màn loading và không đưa tài liệu/profile vào Git.

## Đo thực tế và giới hạn

Đo voice bằng tiến trình source riêng, không chạy cùng test/Office: VieNeu v3
Turbo ONNX fp32, bốn luồng, một preset Mai Anh đọc cả Việt và Anh, WAV 48 kHz.
Cache hệ điều hành không được xóa trước phép đo. Đây là mẫu nhỏ trên máy hiện tại,
không phải thống kê p50/p95 hoặc cam kết trên máy giáo viên khác.

| Thao tác | Thời gian |
|---|---:|
| Đoạn đầu, tiến trình mới | 8,6002 s |
| Trong đó nạp engine | 5,6747 s |
| Đoạn mới tiếp theo, engine đã nạp | 2,4688 s |
| Tạo biến thể nhanh từ WAV gốc | 0,0434 s |
| Dùng lại đúng biến thể đã có | 0,0003 s |

Một phép đo trước đó chạy đồng thời nhiều kiểm thử mất khoảng 151 s cho lần đầu;
không dùng số đó làm tốc độ bình thường. Nó cho thấy tải máy/ổ đĩa ảnh hưởng lớn.
Máy có GTX 950 2 GB; RC35 vẫn dùng CPU, chưa bật GPU/quantization hoặc thay model
mà chưa chứng minh tương thích và chất lượng.

Trên bản nháp Bài 6 đã nhận từ trước, bước kiểm tra/tự sửa local cuối mất khoảng
105,47 s, giữ 79 slide, còn **17 FAIL / 62 CHECK**. Có 19 thao tác chuẩn hóa tiêu đề
và các lượt sửa giãn dòng/cỡ chữ; một số cảnh báo cũ được phân loại lại bằng đối
chiếu nguồn. Đây **không phải** thời gian chuyển đổi cả bài từ đầu và **không phải**
bài đã hoàn thiện. Còn lỗi tràn, nội dung/cột chưa đủ và chuỗi cần đối chiếu.
Kết quả thử nằm riêng trong reports; không ghi đè nguồn hoặc sửa thư viện cá nhân.

Trong lúc kiểm thử, ổ C hết chỗ, phát sinh lỗi `ENOSPC`. Những lượt kiểm thử đó
không được tính là đạt. Các lượt xác minh tiếp theo dùng thư mục tạm trên F.
Trước khi dùng tác vụ mới trên thư viện đặt ở C cần đủ chỗ trống; không tự di
chuyển hoặc xóa thư viện, model, profile và các tài liệu cá nhân.

## Cách nghiệm thu

- Kiểm thử venv: cache/đổi tốc độ, tranh chấp/hủy, nhập nguyên tử và khôi phục,
  lưu nguồn dở, thiếu dung lượng, bốn kiểu song ngữ, độ phủ bản dịch, chất lượng
  slide, cache render và các luồng browser mô phỏng.
- Qt thật: giữ UI phản hồi khi worker nhập đang chờ, dừng giữa hai bước và chỉ
  tạo voice khi giáo viên yêu cầu; lỗi voice không xóa hoặc tự duyệt bài.
- PowerPoint thật: render/đo chữ trước và sau sửa; giữ bản tốt hơn, không tự ghi
  PASS cho kiến thức, chữ trong hình hoặc hiệu ứng chưa xác minh.
- Gói ứng dụng: xây lại toàn bộ module app, đối chiếu version/commit, kiểm tra
  ZIP/checksum và khởi động Qt bằng dữ liệu thử riêng.

Số ca và kết quả đóng gói thực tế được ghi tiếp ở [STATE](STATE.md).

Ở mốc này bộ browser chưa qua đầy đủ: ca chuyển đổi song song qua, ca
Chrome lưu/khôi phục phiên timeout ngay ở điều hướng tab khởi động.
Tám ca bảo vệ profile/cấu hình qua. Timeout cũng xuất hiện với profile
mới, đường dẫn ngắn trên F; chưa có bằng chứng kết luận chỉ do ổ C đầy.
Không nới timeout hoặc bỏ assertion để công bố bộ kiểm tra đạt. Chưa
phát hành RC35 qua cập nhật tự động khi phần xác minh này còn chưa đạt.

## Phần còn lại của kế hoạch

P1 chưa qua điều kiện Bài 6 hết FAIL, chưa có số đo chuyển đổi web từ đầu mới để
khẳng định nhanh hơn bao nhiêu. Mở rộng dàn bố cục theo vùng, thử GPU/streaming,
benchmark int8 trên CPU phù hợp và thử Midscene vẫn là việc tiếp theo. Không cài
thêm studio/engine/browser mới chỉ để tăng số công cụ; các tab Cài đặt và quy
trình PPTX trước, voice tùy chọn sau vẫn giữ nguyên.
