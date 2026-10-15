# RC40 — giữ thiết kế PowerPoint khi dịch bằng Google

Ngày 15/10/2026. Bản trước chỉ cho đi luồng native khi toàn bộ bài vượt qua
preflight. Một ảnh lớn, nhóm, hiệu ứng hoặc vùng chữ chật có thể khiến cả bài
bị dựng lại trên mẫu trắng, tách ảnh sang cuối và mất hiệu ứng. Bộ đọc thường
của python-pptx còn bỏ qua một số hộp chữ/công thức trong `mc:AlternateContent`,
khiến có trang chỉ dịch được tiêu đề.

## Cách hoạt động

- Chọn **Giữ thiết kế PowerPoint gốc**: không tự chuyển cả bài sang mẫu trắng.
  Các phần media, theme, master, layout và tài nguyên nhúng được chép nguyên.
- Slide đủ chỗ vẫn dùng bố cục song ngữ cùng trang. Slide chật, nhóm hoặc có
  hiệu ứng cần giữ nguyên dùng trang Việt gốc, rồi trang Anh cùng thiết kế.
  Đây là lựa chọn được người dùng xác nhận; số trang có thể tăng.
- Đọc nhánh Choice của hộp chữ hiện đại đúng một lần; bảo vệ XML công thức,
  trường và số mũ khi gửi phần ngôn ngữ cho Google. Nhánh tương thích và ảnh
  gốc được giữ, không nhận là đã dịch chữ nằm trong bitmap.
- Trang Anh giữ ID, vị trí, thứ tự đối tượng và timing của nguồn. Công thức
  được co cùng khung chữ thay vì chỉ co chữ thường, tránh phân số chạm viền.
  Một số khung nguồn vượt mép được tăng lề trong ở phần dịch để giữ chữ trong
  vùng nhìn thấy; không dời ảnh hay sửa trang Việt nguyên bản.
- Giữ độ trong suốt của các run ẩn trong nguồn; không áp màu chữ thường lên
  mã ẩn rồi làm chúng hiện ra. Chữ trong run có alpha bằng 0 không được coi
  là chữ nhìn thấy hoặc đưa vào lời đọc. Chừa thêm lề cho hình nằm sát phần
  cuối dòng để bản dịch dài hơn không chạy vào hình dù vẫn vừa hộp chữ.
- Nếu có PowerPoint desktop, đo phần chữ mới và căn tối đa hai lượt, chỉ sửa
  XML định dạng chữ. Không lưu lại toàn bộ file qua Office. Nếu thiếu Office,
  vẫn xuất bản native theo ước lượng và giữ trạng thái cần rà soát.
- Sơ đồ trang nguồn/ngôn ngữ được lưu cùng bài và dùng lại khi kiểm tra/sửa.
  Kiểm tra độ phủ vẫn phát hiện trang Anh thiếu chữ. Không bỏ lỗi bằng cách
  đánh dấu mọi trang đã hoàn thiện. Khung tràn có sẵn và trang Việt nguyên XML
  được ghi rõ nguồn gốc; lỗi tràn mới do PowerPoint đo vẫn là FAIL.
- Giữ hai giai đoạn: lưu/tải bài song ngữ trước; tạo giọng là bước tùy chọn.

## Kiểm chứng và giới hạn

Đã đối chiếu một bản kết quả trắng với đúng tệp nguồn còn lưu, rồi thử lại
nguồn thật 48 slide. Bản giữ thiết kế có 94 trang, bao gồm các cặp Việt–Anh.
Đã mở/render toàn bộ bằng PowerPoint, so sánh tài nguyên nguồn và timing.
Thời gian của ca thật có cache dịch không đại diện cho mọi bài hoặc lần đầu.

Lần kiểm chứng cuối đã render 94/94 trang, không còn FAIL về tràn chữ được đo.
99 phần tài nguyên giữ nguyên byte, 47 trang nguồn giữ nguyên XML, 81 cây
timing ở các trang tương ứng khớp bản gốc. Đây là bằng chứng bảo toàn dữ liệu
và đo bố cục, không phải chứng nhận mọi click/trigger hoặc nội dung đã đúng.
Giữ nguyên trạng thái CHECK và không tự duyệt bài. Một lượt rộng qua 109 ca;
sau khi bổ sung căn khoảng trống đã chạy lại 32 ca liên quan và Qt smoke.
Các lượt kiểm thử chồng nhau không được cộng thành số ca độc lập.
Đối chiếu ảnh cuối phát hiện thêm lỗi chữ chạm hình và mã trong suốt bị lộ;
đã bổ sung kiểm thử riêng, chạy lại 49 ca liên quan và Qt smoke trước bản chạy
cuối. Bản build trước lượt đối chiếu này không bàn giao để dùng thử.

Kiểm thử tổng hợp bao phủ bài có slide đơn giản lẫn ảnh/hiệu ứng, Choice và
fallback cùng ID, công thức không đổi, nhóm có tọa độ con, ảnh không có chữ,
trang Anh bị xóa nội dung, sơ đồ trang sai, thiếu Office và giới hạn căn chữ.
Qt smoke dùng API fixture và dữ liệu tạm, kiểm tra tiến độ/đồng hồ, tải bài,
voice riêng, nhiều key và hai kích thước cửa sổ; không thay thế thử API thật.

Chữ trong ảnh, nhãn biểu đồ/SmartArt chưa được dịch bằng OCR; bitmap fallback
cũ có thể vẫn chứa tiếng Việt. Việc giữ XML hiệu ứng không chứng nhận ý nghĩa
khoa học hoặc mọi trạng thái click/trigger. Chữ nhỏ, mã rác có sẵn trong nguồn
và nội dung cần giáo viên đối chiếu vẫn có cảnh báo. Không tự duyệt bài hay
tự tạo voice. Bài nguồn, bản kết quả, key, báo cáo và EXE nằm ngoài Git.

RC40 là mốc mã nguồn và bản thử độc lập tại máy. Bộ cài tự cập nhật trên GitHub
Releases là một mốc phát hành riêng.

## Bản thử độc lập cuối

- Phiên bản `1.0.0rc40`; mã nguồn `d951dfc758f4af9938455325d0e71c939d2d0e5d`.
- SHA-256 EXE: `f92c192b886702f50f53171cca836efc4d4af1884abd5e13aaae41aba08c4a1e`.
- Biên dịch lại 90 module ứng dụng; dùng lại runtime/model RC34 không đổi.
  Đây là bản thử tại máy, chưa phải gói Windows đã phát hành qua cập nhật.
- EXE đã kiểm tra ở màn tạo bài 1366×850 và Google Dịch 1080×700: đúng phiên
  bản, có icon Windows, mở/thoát đúng và không có cảnh báo QML. Chưa thay thế
  kiểm tra cài đặt trên Windows sạch.
