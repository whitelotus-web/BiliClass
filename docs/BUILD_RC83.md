# RC83 — Điều khiển PowerPoint và phản hồi Mascot

Gồm thay đổi RC82 nội bộ, thêm:

- Bấm nhân vật/vùng trống hoặc nút dạy đưa bàn phím về đúng cửa sổ bài
  đang gắn. Dò cả editor để F5 hoạt động trước trình chiếu. Kiểm PID,
  HWND, lớp và tên tệp chính xác; không bắt phím ở ứng dụng khác. Kiểm
  cửa sổ phản hồi có thời hạn, không gọi Office COM trong GUI.
- Trước/Sau chuyển thẳng slide và có giới hạn đầu/cuối. Phím mũi tên
  giữ điều hướng từng hiệu ứng. Bộ đếm lấy trạng thái thật từ Office.
- Chỉ hiện nút đọc ngôn ngữ có giọng trên slide; ẩn thanh âm lượng khi
  không có giọng. Mascot và loa slide vẫn dùng cùng native player.
- Dấu ? hiện bảng phím khi rê chuột, không mở thêm nội dung trong bảng.
  Nhãn Space ␣, Enter ↵, Ctrl + Space ␣; phản ánh cả phím tự gán.
- Lệnh đi thẳng tới hàng đợi helper, bỏ vòng chờ chuyển tiếp 100 ms.
  Chỉ dừng player đang phát khi đổi slide. Tín hiệu riêng cho trạng thái
  Office tránh cập nhật toàn Settings/Thư viện theo mỗi hiệu ứng; phiên
  đã gắn không tự đổi đoạn đang duyệt của bài trong ứng dụng.
- Lưu ngoại hình Mascot nguyên nhóm ở worker, có Đang lưu, thử lại và
  báo lỗi; không chờ khóa SQLite trên GUI. Nền trong vẫn lưu gộp ở nền.
- Có ghi stack cục bộ nếu event loop không phản hồi trên 5 giây, chỉ
  stack, không ghi biến cục bộ/lời bài/API key. Dừng theo dõi trước dọn
  worker khi thoát; log này không thuộc Git hoặc gói phát hành.

## Kiểm chứng nguồn

933 core đạt; thêm test ngắt phiên/loại sự kiện Office cũ đạt trong lượt
48 test liên quan. Có một warning Starlette/httpx có sẵn. Lint/compile đạt.

Harness chuột/bàn phím Windows thật với Office và bài dùng một lần có
hiệu ứng, WAV im lặng: F5 từ editor, khôi phục focus, đọc/tạm dừng/đổi
ngôn ngữ, âm lượng, phím ứng dụng khác không bị bắt, nút/đếm theo slide,
14 lần chuyển và 12 lần kéo bảng đạt. Chuyển trung bình 0,057 s, tối đa
0,125–0,141 s qua các lượt; khoảng tick GUI tối đa 0,078 s; không phát tín hiệu làm mới toàn
Bridge hoặc warning QML trong chuỗi này.

Các số trên đo trên bài mẫu ở máy hiện tại; bài nhiều ảnh/hiệu ứng có thể
chậm hơn, chưa chứng nhận hết nguyên nhân treo ngắt quãng ở RC81. Không
đóng ứng dụng hay bài PowerPoint của người dùng. 9 luồng Qt liên quan đạt,
gồm hover tooltip, kéo/thu bảng, chuyển bài, Settings, lớp cửa sổ và Office
thật. Helper thoát theo parent bị mất trong 0,266 s, nguồn không đổi.
GUI 30 môn đạt; desktop nguồn hiện Mascot, thu nhỏ giữ và đóng thoát cả
hai trong 0,329 s. Lưu Mascot và kéo 71 mức nền trong khi SQLite đang
khóa không chặn GUI; khoảng tick tối đa 0,031 s trong lượt này. Kết quả
bộ cài sẽ được bổ sung sau xác minh gói mới. Kiểm phát âm và máy chiếu vật
lý không thuộc harness WAV im lặng.
