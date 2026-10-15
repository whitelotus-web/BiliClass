# BiliClass RC42 — bố cục tự chọn, xem trước và giọng đọc riêng

Mốc tại máy ngày 16/10/2026. Luồng mặc định tiếp tục dùng Google Cloud
Translation cho chữ, dựng/kiểm tra PowerPoint và tạo giọng trên máy. Không
gửi prompt hay bài giảng qua ChatGPT/Gemini trong luồng này.

## Hai lựa chọn khi tạo bài

- **Song ngữ Việt–Anh** giữ mã dữ liệu `parallel_columns` để tương thích bài
  cũ. Bộ dựng chọn cặp dọc cho tiêu đề/vùng hẹp hoặc công thức phù hợp, cột
  cạnh nhau cho vùng đủ rộng. Khung nhiều đoạn quá chật có trang tiếp nối
  vẫn chứa hai ngôn ngữ. Không yêu cầu giáo viên đoán trước bài dài/ngắn.
- **Tiếng Anh 100%** thay chữ chỉnh sửa được trong hộp gốc, giữ tọa độ hộp
  và tài nguyên. Điều chỉnh chữ để vừa khung. Chữ trong ảnh, biểu đồ và
  đối tượng không trích được chưa được OCR/dịch; không cam kết toàn bộ
  hình ảnh đã thành tiếng Anh.

`sentence_pairs` vẫn đọc/chuyển được cho cấu hình cũ nhưng không còn là lựa
chọn mới trên giao diện Google. Không đổi hàng loạt dữ liệu bài đã lưu.

## Mẫu mới tại máy

Ba phong cách đóng gói sẵn: Chuẩn lớp học (xanh), Trực quan (teal), Luyện tập
(ấm). Dùng chung bố cục chữ có lề, phân cấp tiêu đề, đường phân cột, footer
và chuyển trang fade bằng click. Nút Xem PowerPoint mẫu dựng bằng chính
bộ dựng đầu ra, không cần key hay dịch vụ thiết kế để xem mẫu.

Đây là mẫu định sẵn, không phải AI sáng tác giáo án/ảnh hay tự hiểu mọi sơ
đồ để thiết kế lại. Google vẫn cần cho phần dịch chưa có cache. Hình thông
thường từ PPTX có trang hình riêng; hiệu ứng, biểu đồ/đối tượng nhúng gốc
không được tái dựng vào mẫu mới. Không khẳng định đẹp hơn mọi mẫu nguồn.

## Kết quả, xem slide và mascot

Xem slide và điều hướng nằm trước phần Tạo giọng đọc không bắt buộc.
Ẩn bảng chẩn đoán khỏi màn chính; mở ở Thao tác khác → Thông tin kiểm tra.
Không còn nút Tự sửa bài giảng trên màn chính. Mỗi lần chuyển mới render và
thử sửa cục bộ tối đa ba lượt trước khi lưu. Không lặp vô hạn hoặc tự duyệt
bài. Bài cũ chưa qua bước này được thử kiểm tra/sửa một lần khi mở.

Ảnh xem trước dùng worker riêng, xác minh tệp một lần cho mỗi phiên bản,
kiểm tra thay đổi tệp/PNG và dùng lại cache chính xác. Bấm nhanh nhiều trang
ưu tiên yêu cầu cuối. Cache miss render trang cần xem và các trang kề trong
một lần mở Office. Xem trước không phải bằng chứng QA; không đọc lại toàn
PPTX/font/catalog/audio trên mỗi lần đổi trang. Tách xem trước khỏi phiên
trình chiếu để tránh hai luồng mở/đóng cùng bài bằng COM.

Nút Hướng dẫn cân giữa sidebar, tên giáo viên tự xuống dòng đầy đủ. Bỏ hai
nút Nghe câu mẫu/Xem trên slide ở thẻ mascot: chọn Milo/Lumi cập nhật khung
xem trước, nghe giọng ở tab Giọng đọc. Bỏ zoom, thêm chớp mắt và chuyển tư
thế chào, chuyển động nhẹ; giảm chuyển động/ra khỏi vùng xem thì dừng.
Phụ kiện và nhãn môn dùng chung ở màn dạy, xem trước và trợ giảng nổi.
Đây là các tư thế/sprite, không phải mô hình nhân vật có khớp/đuôi 3D.

## Giọng đọc sau khi lưu bài

Giáo viên chọn Anh, Việt hoặc Việt + Anh rồi tạo bằng giọng đa ngôn ngữ và
tốc độ đã lưu. Công việc chạy nền; bỏ đoạn trùng, dùng lại WAV hợp lệ,
dừng/tiếp tục phần chưa có. Mở bài không tự tổng hợp/phát âm thanh. Đổi
giọng/tốc độ/nội dung dùng chữ ký cache mới. Cảnh báo hình học không chặn
toàn bộ voice; bộ lọc lời đọc vẫn loại nội dung kỹ thuật/chưa xác định.

Khi trình chiếu, mascot dùng lời đọc của slide hiện tại; đọc Anh hỗ trợ
tạm dừng/tiếp tục, đổi slide dừng hàng đợi cũ. Phần chữ ẩn/công thức/hình
không chắc vẫn có giới hạn. Voice lưu ở thư viện BiliClass, **chưa nhúng tự
động vào PowerPoint tải về**. Không chứng nhận phát âm/thuật ngữ mọi môn.

## Bằng chứng và giới hạn còn lại

- Sửa lỗi bỏ sót thân bài trong nhóm có tọa độ con nằm ngoài slide nhưng
  vị trí hiển thị thực vẫn nằm trong trang. Sửa bước tự fit đọc nhầm tên ZIP
  part khi có trang tiếp nối và khi Office đổi tên part. Giữ sửa thành công
  trên từng trang, trả lại trang không cải thiện; vẫn kiểm tra không phát
  sinh lỗi mới trước khi nhận sửa.
- Font nhúng chưa cài trên Windows có thể chỉ chứa bộ glyph/style nguồn.
  Khi thêm chữ/italic, dùng Arial cho cả Việt–Anh ở vùng được dịch để tránh
  ký tự hỏng; giữ font toán/ký hiệu và tài nguyên nguồn.
- Kiểm tra hồi quy bao gồm ba chế độ nội bộ, tài nguyên nguồn, vị trí English
  only, nhóm biến đổi, cache bị sửa cùng kích thước/mtime, sửa part, lọc lời
  đọc, hủy/tiếp tục và lựa chọn tốc độ. Qt kiểm tra bố cục kết quả, hai lựa
  chọn, F1 giữa sidebar, tên đầy đủ, đổi trang liên tục, mascot và nút voice.
  Tập kiểm tra rộng đạt 143 ca; sau chỉnh lề/font trang mẫu chạy lại 18 ca
  liên quan và 37 ca mẫu/lời đọc. Các tập chồng nhau, không cộng tổng ca.
  Qt Google dùng API fixture; Qt giọng đọc/trình chiếu dùng engine thật.
- Sáu mẫu PowerPoint (ba theme × hai lựa chọn) đã render thực bằng Office,
  không FAIL; CHECK vẫn giữ vì render không chứng nhận nội dung.
- Bài 6 thật: 79 trang nguồn → 87 trang. Lượt chuyển với cache dịch sẵn mất
  khoảng 130 giây gồm render/QA; một lượt tinh chỉnh tiếp mất khoảng 68 giây.
  Giữ nguyên 356 phần tài nguyên. Phần dịch thân bài đã bổ sung, font hỏng
  được khắc phục, nhưng kiểm tra cuối vẫn **17 trang FAIL về tràn chữ**.
  Không được quảng cáo bài này đã sẵn sàng dạy hoặc mọi bài tự hoàn thiện.
- Đo cache trên bài RC41: cơ chế cũ khoảng 1,17–1,24 giây/trang; cơ chế mới
  lần đầu khoảng 0,48 giây, đổi trang có ảnh khoảng 3–4 ms, ảnh đã đọc khoảng
  0,2–0,3 ms. Đây là lấy ảnh cache, không phải tổng thời gian vẽ UI hoặc
  render trang chưa có ảnh, và không phải benchmark lần đầu gọi Google.
- Tạo WAV thực trên máy: câu Việt ngắn lần đầu khoảng 19,4 giây (gồm nạp
  model), câu Anh tiếp khoảng 2 giây; gọi lại cache khoảng 0–16 ms. WAV,
  thay tốc độ và cache đạt kiểm tra; phát âm vẫn cần nghe thử.
- Qt + PowerPoint + VieNeu + MCI đã thử thật: đọc tiêu đề và thân bài Anh,
  pause/resume, đổi slide dừng âm thanh, slide chỉ có Việt không tự đọc Anh,
  nguồn không bị sửa. Một ca đầu phát hiện chồng thao tác xem trước/trình
  chiếu; sau tách hai thao tác, ca chạy lại đạt.

Bài giảng thật, key, cache, báo cáo, audio và EXE nằm ngoài Git. RC42 là bản
thử độc lập tại máy; không tự coi là bộ cài đã phát hành trên GitHub Releases
hoặc đã thử trên Windows sạch.

## Bản độc lập đã mở tại máy

- Phiên bản `1.0.0rc42`, mã nguồn `1964f3dd925bbe50bb185a8cefba80e90ec24ea5`.
- EXE SHA-256 `a21ca0e6258d83d6ee57ef1451f5df2a6850c0249210ac93a4b86971462073ae`.
- Biên dịch 94 module ứng dụng, dùng runtime/model RC34 không đổi qua
  junction. Đã thử EXE ở màn tạo bài 1366×850 và Google Dịch 1080×700,
  đúng phiên bản/icon, không cảnh báo QML và thoát bình thường.
- Mở độc lập bằng shortcut **BiliClass RC42** ở desktop. Đóng RC41 đúng
  cách trước khi thay cửa sổ; không ép dừng Office hay app khác.
- Sau khi mở, cửa sổ đáp ứng đủ 15 lần đo. 15 bản ghi bài và 638 WAV
  không đổi giữa hai snapshot trước/sau lần khởi động này; không tự tiếp
  tục yêu cầu chuyển đổi cũ. Số liệu này không bao gồm các bản nháp được
  tạo có chủ đích trong các ca chuyển thử trước đó.
