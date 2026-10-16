# Rà soát và kế hoạch tối ưu RC55 — 16/10/2026

Rà soát sau khi phát hành [RC55](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc55),
nguồn `9a43c4b1f4fd9b106d70eb0aef7f84eb7d802c44`. Bản cài đang mở độc lập
qua Explorer. Đây là kiểm tra trên máy phát triển hiện tại; chưa chứng nhận
Windows sạch, máy ít RAM, mạng trường học hoặc chất lượng mọi bài giảng.

## Kết quả đã kiểm tra

| Phần | Kết quả và giới hạn |
| --- | --- |
| Bộ kiểm thử nguồn | Lượt toàn bộ: 869/871 qua trong 501 giây. Hai fixture cũ lệch hợp đồng hiện tại đã sửa, chạy lại 18 test liên quan đều qua; không gọi lượt đầu là 871/871 xanh. Không đổi mã chạy EXE vì các sửa sau phát hành chỉ ở test/tài liệu. |
| Google Dịch | Kiểm tra API giả lập: lưu nhiều key, chuyển key có giới hạn, cache, đồng hồ, xuất bài không cần giọng. Không gửi thêm yêu cầu Google thật. |
| Mẫu mới | Khôi phục bài từng dừng ở 55% bằng bản dịch đã lưu: 78 slide, PowerPoint render 78/78, không còn lỗi tràn chữ trong lượt cuối. Ba trang còn chuỗi ký tự lạ từ nguồn; bài giữ trạng thái cần sửa/kiểm tra. |
| Thư viện | Qt kiểm tra 24 bài, chọn xuyên trang/lọc, tải đúng ID, xóa vào thùng rác, hủy xóa vĩnh viễn, khôi phục/xóa nhóm. Hai kích thước 1080/1366, một hàng công cụ, ô chọn 16 px, không QML warning. |
| Kiểu xem và ảnh | Một nút icon đổi danh sách/thẻ, ảnh native 16:9; đổi tab/kiểu xem giữ cache, không khởi động lại worker cho ảnh đã có. Cache phiên giới hạn 80 ảnh. |
| Giọng và bước dạy | Qt kiểm tra ba bản Anh/Việt/Song ngữ, sáu giọng nghe thử, lưu bản đúng giọng/tốc độ, khóa tạo trùng, đổi tốc độ mở bản mới, bước chuẩn bị dạy và không tự duyệt bài có lỗi. Âm thanh ở phép kiểm tra giao diện là mẫu/fixture. |
| Runtime giọng | EXE đã cài thực sự tổng hợp WAV Anh, Việt, câu trộn, đổi tốc độ và dùng lại cache; không phát toàn bộ bài giảng trong phép thử này. |
| Mascot | Bật/tắt và nhãn đồng bộ; lưu môn cập nhật phụ kiện; các nút đọc khóa khi chưa có phiên slide. Không tự bắt đầu đọc khi tạo giọng xong. Phiên dạy Qt + PowerPoint thật với 3 slide đã qua: mascot đọc cache đúng trang, đổi trang/dừng/đóng show ngắt giọng, trang trống khóa đọc, mở lại được; nguồn không đổi. |
| Lớp học và Báo cáo | EXE chạy server con, học sinh thử qua loopback, WebSocket có xác thực, ACK câu trả lời, báo cáo lưu đúng. Qt kiểm tra chọn bài/chặn bài chưa chuẩn bị và tìm báo cáo. Chưa kiểm tra điện thoại/mạng Wi-Fi thật. |
| Thuật ngữ & kiến thức | Tìm không dấu, trạng thái không có kết quả, tab dữ liệu; đọc mã nguồn đối chiếu nơi kho thuật ngữ được dùng. Có khoảng trống tích hợp dịch, nêu bên dưới. |
| Cài/cập nhật/dữ liệu | SHA-256/CRC toàn ZIP, digest GitHub, manifest khi cài và Qt EXE không có đường dẫn Python nguồn. RC34/RC54 nhận RC55 đúng dung lượng/checksum. Giữ nguyên 16 bài cũ/992 WAV, thêm một bài khôi phục; không đổi bộ đếm dịch. |

Đo kiểm nút nghe mẫu trên EXE: 13–26 ms từ bấm đến hàm phát; lưu khi đang
nghe thử khoảng 22 ms. Đây không phải độ trễ âm thanh tới loa hoặc thời gian
sinh câu tùy ý. Heartbeat Qt lớn nhất khoảng 101 ms trong phép thử này;
luồng chuyển đổi Google giả lập có khoảng ngắt lớn nhất 500 ms, còn dư địa tối ưu.

API key không xuất hiện dưới dạng byte nguyên văn trong 469 tệp đang được
Git quản lý (đối chiếu hai key thật trong bộ nhớ, không ghi giá trị vào log).
Repo mã nguồn hiện công khai; kho cấu hình key riêng trả 404 khi truy cập ẩn
danh. Không đưa thư viện, câu trả lời học sinh, báo cáo riêng, model hoặc EXE
vào commit nguồn. Sáu WAV được theo dõi là mẫu nghe chung của sản phẩm.
Đây không thay thế kiểm toán toàn bộ lịch sử Git.

## Các vấn đề còn lại

1. **Ưu tiên cao — thuật ngữ chưa đi vào dịch Google.** Luồng hiện tại gọi
   `Translator.translate(texts)` trong `google_conversion.py`; chưa dùng
   `Library.glossary`/`knowledge_translation` và cache chưa phân biệt môn hay
   phiên bản thuật ngữ. Cùng một từ có thể được dịch theo nghĩa chung, dù giáo
   viên đã lưu thuật ngữ riêng. Cần giải quyết trước khi quảng bá “dịch theo môn”.
2. **Ưu tiên cao — chất lượng mẫu có công thức/hình phức tạp.** Không tràn chữ
   không đồng nghĩa bố cục/ngữ nghĩa đúng. Bài thật còn ký tự nguồn cần xử lý,
   nhiều cảnh báo lời đọc/ảnh và các trang chỉ có công thức còn khung giải thích
   trống. Nhóm công thức gắn hình có thể mất mối liên hệ vị trí khi dàn lại;
   chưa chứng nhận mọi sơ đồ hoặc hiệu ứng. Cần bộ bài mẫu chuẩn và so ảnh nguồn.
3. **Hạn mức vẫn là ước tính cục bộ.** Hai key hiện chưa có Project ID được xác
   minh nên giữ bộ đếm chung lịch sử. Tên/Gmail khác nhau không tự xác nhận hai
   hạn mức độc lập. Đồng bộ cấu hình hiện là snapshot, không cộng trực tiếp
   lượng dùng giữa hai máy. API key đơn thuần không đọc được số dư Cloud.
   [Quota Google](https://docs.cloud.google.com/translate/quotas),
   [giá/credit](https://cloud.google.com/products/translate/pricing),
   [quyền đọc quota](https://docs.cloud.google.com/service-usage/docs/reference/rest/v1beta1/services.consumerQuotaMetrics/list).
4. **Nợ kiểm thử và định dạng mã.** Lượt toàn bộ phát hiện hai fixture cũ:
   thiếu `source.file`/`path` trong mẫu bài sửa và gọi `cache_clear` ở wrapper
   đã được tách khỏi cache model. Đã cập nhật fixture, bổ sung kiểm tra đường
   dẫn sửa local và xác minh model chỉ khởi tạo một lần; 18 test liên quan qua.
   Không thay mã ứng dụng để che lỗi kiểm thử.

   Ruff còn 275 cảnh báo trong 43 tệp, phần lớn
   dấu chấm phẩy/import; không có F821/F822/E999. Trong cùng nhóm tệp, RC54 có
   257 cảnh báo. Script `qt_narration_preparation_smoke.py` hết thời gian vì gọi
   `_run_web_conversion` đang chủ động trả về khi Google Dịch được bật. Các
   kiểm tra Google/result/voice hiện tại thay thế đã qua; script cũ cần cập nhật,
   không được gọi là toàn bộ smoke đều xanh.
5. **Hiệu năng chưa đo đủ quy mô lớn.** Cache ảnh nhanh trong phiên, nhưng mở
   lại ứng dụng còn xác minh nguồn/cache. Chưa benchmark 1.000 bài, bài 100 slide
   có nhiều WAV, máy RAM 8 GB hoặc 40 điện thoại cùng lớp. Không hứa tỷ lệ tăng
   tốc voice khi chưa có số đo trên các cấu hình này.

## Kế hoạch tối ưu đề xuất

| Thứ tự | Việc làm | Điều kiện hoàn thành |
| --- | --- | --- |
| 1 | Đưa thuật ngữ giáo viên vào trước dịch; thuật ngữ kiến thức có nguồn là gợi ý; thêm phiên bản/môn vào khóa cache. | Thuật ngữ đã duyệt được giữ đúng; đổi thuật ngữ không dùng nhầm cache cũ; từ cùng chữ ở hai môn không ảnh hưởng nhau. |
| 2 | Hoàn thiện dàn trang công thức/hình, bỏ khung rỗng, nhận biết tiêu đề ngắn; hỗ trợ sửa từng trang cần kiểm tra. | Bộ đối chiếu ít nhất 20 bài/5 môn; không mất nội dung, không tràn/đè; ghi rõ ảnh/công thức chưa xác minh và giữ cổng duyệt. |
| 3 | Đo voice theo ba giai đoạn nạp model/sinh WAV/nhúng PowerPoint; đo câu đầu, cache, tổng thời gian và RAM; so một/hai worker. | Có bảng đo bài 20/50/100 slide trên máy 8/16 GB; cache không sinh lại; dừng không phát muộn; chỉ bật thêm worker khi số đo cho thấy có lợi. |
| 4 | Tách tên key khỏi nhóm quota rõ hơn; thêm luồng xác minh dự án và tùy chọn Cloud Monitoring có quyền OAuth; đồng bộ metadata tên. | Không nhân đôi 500.000 ký tự cho key cùng dự án; phân biệt ước tính tại máy/quota Cloud; chuyển nhóm không làm mất lịch sử. |
| 5 | Cache bìa theo nội dung nguồn, chỉ tải ảnh đang thấy; benchmark tìm/lọc 1.000 bài và tách danh sách SQL nếu cần. | Chuyển tab/kiểu xem không render lại ảnh hợp lệ; đo bộ nhớ/độ trễ; không giữ vô hạn ảnh hoặc mở nhiều PowerPoint cùng lúc. |
| 6 | Cập nhật smoke cũ sang Google, tách test browser đang ẩn, dọn Ruff theo module; giảm kích thước trách nhiệm của ui.py/Main.qml. | Kiểm thử chức năng hiện tại chạy riêng và xanh; legacy có nhãn rõ; mã sửa mới không tăng cảnh báo; có kiểm thử tự động trước release. |
| 7 | Thử nghiệm phát hành trên máy sạch và lớp thật. | RC34 nâng cấp giữ thư viện/giọng; máy không có Python/Codex chạy độc lập; thử PowerPoint, màn chiếu và 20–40 điện thoại cùng Wi-Fi, phục hồi sau mất mạng. |

Nên làm mục 1 và 2 trước khi thêm chức năng mới. Mục 3–5 cần benchmark rồi mới
chọn kỹ thuật; không tự tăng số luồng hoặc tải tất cả model vào RAM.

Một lần gọi chẩn đoán trình chiếu từ stdin thất bại vì Windows spawn không
đọc được `<stdin>`; chạy lại đúng entry file có guard đã qua. Đây là lỗi
cách gọi phép thử, không phải lỗi mở trình chiếu của ứng dụng.

Bằng chứng chi tiết ở máy phát triển: `reports/rc55/audit/`,
`reports/rc55/library-views/`, `reports/rc55/real-recovery/`,
`reports/rc55-installed/`, `reports/rc55/updater.json` và `reports/rc55/restart.json`.
Báo cáo riêng và ảnh bài giáo viên không được đưa lên repo công khai.
