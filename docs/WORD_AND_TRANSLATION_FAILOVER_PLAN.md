# Đề xuất dịch dự phòng và Word song ngữ

Ngày 25/10/2026. Bản thiết kế ban đầu; phần triển khai và phạm vi thực tế đã
được ghi tại [RC169: Word và dịch vụ dự phòng](WORD_RC169.md). Mốc trước nâng cấp là RC168 commit
`1d452f087556e74a1f43b9a1b389179d94b46ede`; RC167 tiếp tục được giữ nguyên.

## 1. Dịch dự phòng và thông báo nhẹ

Dịch vụ đã chọn là ưu tiên đầu tiên. Khi không dùng được vì cấu hình, tài khoản,
hạn mức hoặc sự cố nhà cung cấp, tự thử các dịch vụ khác đã có cấu hình hợp lệ,
theo thứ tự hiện trên tab Dịch thuật và bỏ qua dịch vụ vừa thất bại. Không có key
thì bỏ qua, hiển thị trạng thái trung tính, không coi là lỗi nghiêm trọng.

- Cài đặt hiển thị bốn trạng thái: Chưa thiết lập, Chưa kiểm tra, Dùng được qua
  lần kiểm tra gần nhất, Tạm chưa dùng được. Lưu thời điểm kiểm tra; không coi
  việc có key hoặc lưu key thành công là chứng cứ dịch vụ đang hoạt động.
- Dùng phản hồi từ lượt dịch thực tế hoặc nút Thử kết nối. Không tự gửi các câu
  dịch định kỳ lúc máy rảnh để kiểm tra, tránh tiêu hao hạn mức của cả bốn bên.
- Khi chuyển dịch vụ, báo một lần trong thao tác: “Gemini hiện chưa dùng được.
  Đã chuyển sang Google để tiếp tục.” Chi tiết lý do ở Cài đặt/Chi tiết xử lý;
  không bật hộp thoại chắn công việc hoặc lặp lại cảnh báo từng đoạn/từng bài.
- Lỗi riêng của tài khoản được ghi là tài khoản/cấu hình chưa dùng được, không
  khẳng định toàn bộ nhà cung cấp đã ngừng hoạt động.
- Mỗi dịch vụ thử có giới hạn, tôn trọng thời gian chờ và bộ đếm riêng. Lưu thời
  gian tạm bỏ qua để cả hàng đợi không thử lại dịch vụ hỏng ở từng bài.
- Khi mất Internet toàn máy, dừng giữ tiến độ thay vì thử vòng qua cả bốn bên.
  Khi tất cả dịch vụ có cấu hình đều không dùng được, tạm dừng và giữ việc dở.
- Dừng do người dùng, lỗi nguồn, sai số liệu/công thức, kết quả không đạt kiểm
  tra nội dung hoặc lỗi lưu tệp không được coi là tín hiệu tự chuyển dịch vụ.

### Giữ đúng tiến độ và chi phí

Cần bổ sung lớp điều phối trên các adapter hiện có, không dùng việc đổi lựa
chọn Cài đặt giữa chừng làm cơ chế chuyển. Bài mới chụp danh sách ưu tiên,
profile URL/model và giới hạn của các dịch vụ dự phòng khi bắt đầu. Bài dở cũ
chưa có chính sách này tiếp tục theo cơ chế đã ghim, không tự đổi ý nghĩa.

Ghi nhận kết quả đạt theo từng vùng, gắn với hash nguồn, lựa chọn vùng, môn/lớp,
chế độ, phiên bản thuật ngữ và dịch vụ thực tế. Phần đã đạt qua A được giữ;
chỉ phần còn thiếu chuyển sang B. Cache, key, hạn mức và model của từng adapter
vẫn riêng biệt. Metadata xuất bài ghi được các dịch vụ thực sự đã dùng thay vì
gắn nhãn A cho toàn bộ một bài có cả A và B.

Tính năng này dùng hạn mức của dịch vụ dự phòng đã cấu hình, không tự đăng ký
gói hoặc bật thanh toán. Cài đặt cần nói rõ dịch vụ chính và việc dùng dự phòng.
Không sửa tùy chọn dịch chính toàn ứng dụng chỉ vì một lượt bài gặp sự cố.

## 2. Vị trí và trải nghiệm Word

Trong **Chuyển đổi bài giảng** có hai tab **PowerPoint** và **Word**. Trong
**Thư viện bài giảng** có hai tab nội dung **PowerPoint** và **Word**. Bộ lọc
giọng đọc và thao tác trình chiếu/mascot thuộc phần PowerPoint, không áp dụng
nhầm cho tài liệu Word. Giữ thành phần, màu sáng/tối, chữ, khoảng cách và kiểu
nút hiện tại; không tạo một giao diện mang phong cách khác.

Luồng Word đề xuất:

1. Chọn `.docx`; hiển thị nội dung có thể bôi đen, bảng/đoạn có định danh.
2. Bôi đen vùng cần dịch, bấm **Thêm vùng dịch**. Vùng được đánh dấu giữ lại
   trong khi tiếp tục chọn ở nơi khác. Có thể tích chọn cả đoạn để thao tác nhanh.
3. Danh sách bên cạnh ghi **Đã chọn N vùng**, có bỏ một vùng/bỏ chọn tất cả.
   Vùng trùng/chồng được gộp, không dịch hoặc chèn lặp hai lần.
4. Chọn môn/lớp và một trong bốn cách trình bày, xem ví dụ ngắn trước khi chạy.
5. Bấm **Chuyển đổi N vùng đã chọn**; hiển thị tiến độ cùng nút Dừng cố định.
6. Giữ màn hình hoàn thành với **Mở Word**, **Mở thư mục**, **Về thư viện Word**,
   **Chọn tài liệu khác**. Không tự quay về màn hình chưa tải tệp.

| Chế độ | Kết quả chỉ ở vùng được chọn |
| --- | --- |
| Việt–Anh hai cột | Tiếng Việt bên trái, bản Anh tương ứng bên phải |
| Từ khóa tiếng Anh | Giữ câu Việt, thêm thuật ngữ tiếng Anh trong ngoặc sau từ khóa |
| Tiếng Anh 100% | Thay riêng phần đã chọn bằng tiếng Anh, phần khác giữ nguyên |
| Anh dưới Việt | Giữ phần Việt, thêm bản Anh ngay bên dưới, mặc định in nghiêng màu xanh |

Ưu tiên **Anh dưới Việt** làm chế độ mặc định. Hai cột dùng các khối/bảng song
song theo đoạn, không dùng cột báo của Word vì nội dung có thể chảy sang cột
khác rồi mất cặp Việt–Anh. Nếu chỉ chọn một phần đoạn thì bản Anh chỉ bao gồm
phần đó; bản xem trước phải thể hiện rõ, không âm thầm dịch cả đoạn.

Từ khóa lấy theo môn và ngữ cảnh từ kho thuật ngữ chung; không dịch mọi từ rồi
mở ngoặc dày đặc. Mặc định chú thích lần đầu của thuật ngữ trong đoạn; không
chèn lặp vào phần đã có tiếng Anh hoặc biến/công thức. Không tìm được thuật
ngữ đủ căn cứ thì giữ nguồn và ghi nhận để xem lại, không bịa thuật ngữ.

## 3. Chọn vùng và giữ tệp Word

“Dòng” trên màn hình không phải định danh ổn định. Word lưu đoạn và các mảnh
chữ có định dạng; số dòng còn phụ thuộc khổ giấy, font, lề và nội dung thêm vào.
Vì vậy lưu vị trí vùng chữ trong đoạn/ô bảng cùng hash của nội dung nguồn.
Chuyển đúng offset UTF-16 từ Qt sang vị trí ký tự của Python, giữ cả dấu tiếng
Việt và emoji. Không chuẩn hóa chuỗi rồi dùng offset của bản cũ để sửa XML.

- Dùng bản sao `.docx`, đối chiếu nguồn trước khi ghi; không ghi đè bản gốc.
- Chỉ sửa các nút chữ/vùng được chọn. Giữ các phần khác của gói tài liệu:
  style, số thứ tự, bảng, ảnh, quan hệ tệp, công thức, đầu/chân trang và khổ giấy.
  Không dựng lại toàn bộ tệp từ văn bản thuần hoặc gán lại cả paragraph.text.
- Vùng đi qua nhiều mảnh định dạng phải được ánh xạ, tách/ghép có kiểm chứng.
  Công thức và đối tượng nhúng không phải văn bản thường; không sửa nửa công
  thức hoặc bóc mất chúng để dịch.
- Ghi tệp tạm, kiểm tra cấu trúc và mở/render thử rồi mới công bố kết quả.
  Thêm tiếng Anh có thể tăng số trang; không hứa luôn giữ nguyên số trang cũ.
- Bản xem để chọn nội dung không tự được coi là ảnh trang in chính xác. Kết
  quả cần được duyệt qua Word/render Word, đặc biệt với bảng và nội dung dày.
- Bản đầu nhận `.docx`. `.doc` cũ cần bước chuyển định dạng riêng, có kiểm tra
  phần mềm hỗ trợ; không đổi tên đuôi để coi là `.docx`.

## 4. Tách khỏi PowerPoint và quản lý lưu trữ

Đề xuất phát triển trên nhánh mới từ mốc đã kiểm tra, tách các module Word:
đọc/ánh xạ vùng, lựa chọn, tạo bản song ngữ, kiểm tra, tiến độ và thư viện.
Không đưa Word vào tuyến DOCX → PowerPoint hiện tại hoặc vào bộ giọng/mascot.
Chỉ dùng chung adapter dịch, thuật ngữ, bảo vệ số/công thức, giao diện cơ bản
và lớp điều phối dự phòng đã kiểm chứng.

Kho Word có thư mục/chỉ mục công việc riêng trên ổ F, không đổi schema bài
PowerPoint đang dùng. Lưu bản song ngữ và ghi nhận trong tab Word theo cơ chế
xuất cạnh nguồn của tool; mở lại một bài không tạo thêm bản sao. Khi tạo lại,
chỉ thay bản xuất do tool quản lý sau khi bản mới đạt, hoặc chọn tên mới nếu
tệp đã được giáo viên sửa. Bản cũ chưa được thay an toàn thì vẫn giữ.

Mỗi công việc có checkpoint gồm hash nguồn, vùng chọn, chế độ và kết quả từng
vùng. Dừng/đóng tool vẫn tiếp tục được từ phần đã đạt. Dữ liệu Word phải được
thêm vào cơ chế sao lưu/khôi phục/dọn tệp của ứng dụng, không đưa vào Git.

## 5. Thứ tự và điều kiện nghiệm thu

1. Dịch dự phòng + trạng thái nhẹ: kiểm tra A lỗi → B có cấu hình, bỏ bên thiếu
   key, không lặp vô hạn, không đổi bài cũ, không gửi lại phần đã đạt, hủy đúng.
2. Module Word độc lập: chọn nhiều vùng rời nhau, một phần đoạn, nhiều đoạn,
   ô bảng, dấu Việt, emoji, vùng trùng, source thay đổi và checkpoint sau dừng.
3. Xuất Anh dưới Việt và Anh 100% ở vùng chọn; sau đó hai cột và từ khóa, luôn
   dùng cùng bộ chọn vùng đã kiểm chứng. Chỉ coi hoàn thành khi đủ cả bốn chế độ.
4. Thư viện Word, mở/xuất, tạo lại, sao lưu/khôi phục, xóa/khôi phục và dọn tệp.
5. Qt smoke sáng/tối/laptop; render tài liệu thật có bảng, hình, số thứ tự,
   công thức và đầu/chân trang; chạy lại hồi quy PowerPoint hiện tại.

Không đóng gói bộ cài trong giai đoạn này. Đưa bản nguồn mới cho giáo viên thử
sau khi các kiểm tra đạt, rồi mới xét mốc đóng gói tiếp theo.

## Căn cứ thiết kế

- Mã hiện tại: `app/translation_provider.py`, `app/google_conversion.py`,
  `app/batch_jobs.py`, `app/library.py`, `app/library_catalog.py`,
  `app/qml/Main.qml`. Router hiện tại cố ý ghim dịch vụ, chưa có chuyển dự phòng;
  thư viện PowerPoint có kiểm tra giọng đọc nên không nhận lẫn Word.
- [Cấu trúc đoạn/run/text trong WordprocessingML](https://learn.microsoft.com/en-us/office/open-xml/word/how-to-open-and-add-text-to-a-word-processing-document).
- [Chọn vùng chữ trong Qt TextEdit](https://doc.qt.io/qt-6/qml-qtquick-textedit.html).
