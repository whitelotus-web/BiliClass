# RC169: Word song ngữ và dịch vụ dự phòng

Ngày 25/10/2026 · Nhánh `codex/word-bilingual-rc169`.
Đây là bản mã nguồn để giáo viên dùng thử; chưa tạo bộ cài RC169.
Tag/bộ cài RC167 và nhánh RC168 được giữ nguyên.

## Dùng thử Word

1. Vào **Chuyển đổi bài giảng → Word → Chọn file Word**, chọn `.docx`.
2. Tích câu/đoạn muốn dịch. Muốn chọn một phần, bôi đen chữ rồi bấm
   **Thêm vùng bôi đen**. Tiếp tục chọn những phần rời nhau ở nơi khác.
   Danh sách bên phải giữ các vùng đã chọn; có thể bỏ từng vùng.
3. Chọn môn, khối lớp và kiểu trình bày. Bấm **Xem bản dịch · N vùng**.
4. Xem cặp Việt–Anh bên phải, sửa bản Anh nếu cần. Chỉ khi đã xem trước
   đúng cấu hình mới có thể bấm **Lưu Word song ngữ**.
5. Màn hoàn tất giữ lại **Mở Word đã lưu**, **Mở thư mục** và
   **Về thư viện**. Vào **Bài giảng → Word** để mở lại hoặc tiếp tục bài.

Hai màn chuyển đổi dùng chung tiêu đề **Chuyển đổi bài giảng song ngữ**,
hai tab **PowerPoint / Word** ở ngay dưới. Tab Word có khung tải/kéo thả
và khung **Cấu hình bài giảng** theo phong cách PowerPoint; luồng xử lý,
vùng chọn và checkpoint của hai công cụ vẫn độc lập.

Giao diện Word ngày 26/10 dùng cùng một trang cuộn: **Tải tệp → Cấu hình →
Nội dung gốc / Bản dịch xem trước**. Cấu hình hiện cả khi chưa chọn tệp;
các lựa chọn này được giữ khi tải tài liệu mới. Khi mở lại tài liệu đã lưu,
tool khôi phục cấu hình và vùng chọn của chính bài đó. Khung tải thu gọn
sau khi nhận file, có nút **Chọn vùng dịch ↓**; các nút xem/lưu/dừng vẫn ở
thanh dưới. Ảnh minh họa Word dùng tài sản được giáo viên cung cấp.

## Thư viện dùng chung

- **Tất cả** gồm cả PowerPoint và Word. Mỗi bài có icon P/W và nhãn loại tệp,
  dùng chung tìm kiếm, môn/khối, sắp xếp, phân trang, kiểu danh sách/thẻ.
- **Chưa có giọng** và **Đã có giọng** có dòng phân loại **PowerPoint**;
  không tính Word là bài chưa có giọng. Tab **Word** cùng cấp lọc tài liệu Word.
- Word có **Mở Word** hoặc **Xem / tiếp tục**, **Sửa song ngữ**, tải `.docx`.
  Khi chọn lẫn hai loại, **Tạo giọng PowerPoint** chỉ nhận các PowerPoint;
  tải nhiều bài thành ZIP giữ `.pptx`/`.docx` tương ứng.
- Thùng rác và Hoàn tác xóa nhận cả hai loại. Xóa vĩnh viễn Word chỉ dọn thư
  mục do tool quản lý; giữ file gốc và các bản đã xuất ngoài thư viện.
- Danh sách Word đọc từ summary trên luồng nền; không dựng ảnh bằng PowerPoint,
  không quét lại toàn bộ âm thanh PowerPoint chỉ vì sửa/chọn vùng Word.

| Kiểu | Kết quả |
| --- | --- |
| Anh ngay dưới Việt | Giữ chữ Việt, thêm bản Anh dưới phần được chọn; mặc định xanh và in nghiêng |
| Việt–Anh hai cột | Đoạn gốc bên trái, bản Anh của phần được chọn bên phải, dùng bảng Word |
| Từ khóa tiếng Anh | Giữ chữ Việt, thêm thuật ngữ trong ngoặc; chọn mức Ít/Vừa phải/Chuyên sâu |
| Tiếng Anh 100% ở vùng chọn | Chỉ thay phần được chọn bằng tiếng Anh; phần còn lại giữ nguyên |

Chế độ từ khóa dùng kho theo môn, không cần API key để chú thích thuật ngữ
đã có. Khi chưa có từ khóa đủ căn cứ, giữ nguyên nguồn và báo để xem lại.
Có thể sửa, bỏ hoặc thêm từ khóa ở bản xem trước. Đây là chỉnh sửa cho vùng
đang chọn, không tự biến từ mới thành kiến thức đã duyệt cho toàn bộ thư viện.

Nút **Dừng** giữ tài liệu và tiến độ. **Tiếp tục chuyển đổi** dùng lại kết quả
đã đạt, không gửi lại các đoạn đã hoàn tất trong cùng cấu hình. Không đóng
màn kết quả hoặc chuyển tự động sang công cụ tạo giọng.

## Giữ tài liệu và bố cục

- Chỉ nhận `.docx` chỉnh sửa được, tối đa 50 MB. `.doc`, tệp có mật khẩu,
  tệp ký số hoặc macro cần được lưu thành bản `.docx` thông thường trước.
- Nội dung ở trái là bản đọc để chọn chữ, không phải bản dựng từng trang giống
  Microsoft Word. Có thể chọn theo câu hoặc đoạn; số dòng hiển thị thay đổi
  theo độ rộng cửa sổ. Vùng chọn dùng định danh đoạn và vị trí chữ, không dùng
  số dòng và không thay tất cả những câu giống nhau trong tài liệu.
- Xuất bằng cách sửa bản sao gói Word gốc. Giữ các phần không chọn, ảnh,
  bảng, style, đầu/chân trang và công thức OMML; công thức không bị dịch như chữ.
  Vùng chọn chạm công thức hoặc đối tượng được mở rộng để giữ trọn đối tượng.
- Đoạn có trường động, bookmark, thay đổi đang theo dõi hoặc content control
  được khóa chọn và có lý do. Textbox, đầu/chân trang, chữ nằm trong ảnh chưa
  là vùng dịch ở lần nâng cấp này. Không có OCR Word hoặc add-in Word.
- Thêm bản Anh có thể làm tăng số trang. Hai cột được kiểm tra với đoạn và ô
  bảng thông thường; tài liệu nhiều section, cột báo, hình nổi hoặc bố cục phức
  tạp cần mở Word đối chiếu trước khi sử dụng. Không cam kết giữ nguyên phân
  trang cho mọi mẫu tài liệu.
- Số liệu và token công thức được kiểm tra trước khi lưu. Đây là kiểm tra
  cấu trúc/nội dung bảo vệ, không chứng nhận mọi câu đúng nghĩa chuyên môn.

## Lưu, mở lại và khôi phục

Mỗi tài liệu có bản nguồn cố định và checkpoint riêng trong
`<thư viện>/word_documents/<id>/`, tách khỏi bản ghi và luồng xử lý PowerPoint.
Thư viện Word được mang theo khi sao lưu/khôi phục hoặc chuyển nơi lưu dữ liệu;
không mang key dịch vào bản sao lưu.

Khi lưu, tool giữ bản trong thư viện và cố gắng xuất thêm
`<tên gốc>_BiliClass_song-ngu.docx` cạnh nguồn. Nếu không ghi được cạnh nguồn,
tool báo rõ và vẫn giữ kết quả trong thư viện. Không sửa tệp gốc.

Xuất lại được dựng từ bản nguồn cố định, không chèn tiếp lên bản song ngữ trước.
Mở lại chính bản nguồn hoặc bản xuất do tool quản lý sẽ quay về cùng tài liệu.
Nếu giáo viên đã sửa bản xuất bên ngoài, tạo tên khác thay vì ghi đè. Nếu nguồn
được sửa sau khi tải, yêu cầu chọn lại nguồn trước khi dịch/lưu.

Menu **⋮ → Khôi phục bản xuất trước** khôi phục cả tệp và cấu hình/bản dịch
tương ứng trong thư viện. Chỉ giữ một bản xuất trước; không sửa các bản ngoài
thư viện khi hoàn tác. Thùng rác bài giảng hỗ trợ cả Word và PowerPoint.

## Dịch vụ dự phòng

Trong **Cài đặt → Dịch thuật**, dịch vụ được chọn là ưu tiên. Bài/hàng đợi mới
chụp danh sách các dịch vụ đã có cấu hình, theo thứ tự: ưu tiên trước, sau đó
Google → Apps Script → Gemini → DeepL, bỏ trùng và bỏ bên chưa thiết lập.
Chính sách này dùng cho cả PowerPoint mới và Word; không tự đổi lựa chọn chính.

- Lỗi kết nối, key/cấu hình, model, hạn mức hoặc nhà cung cấp: thử dịch vụ kế
  tiếp còn cấu hình; phần đã đạt được giữ, chỉ gửi phần thiếu. Dịch vụ dự phòng
  dùng hạn mức riêng đã cấu hình, không đăng ký hoặc nâng gói thanh toán.
- Cảnh báo màu nhẹ trong thao tác và trạng thái từng dịch vụ trong Cài đặt.
  Không có key là trạng thái trung tính. Chỉ ghi kết nối thành công sau phản hồi
  API thật; có key/lưu cấu hình/cache không được coi là kết nối thành công.
- Không tự gửi câu kiểm tra định kỳ. Dùng phản hồi thực tế hoặc **Thử kết nối**.
  Cấu hình thay đổi làm mất hiệu lực cảnh báo cũ. Có khoảng tạm bỏ qua dịch vụ
  vừa lỗi để hàng đợi không thử lại liên tục; có thể thử kết nối lại chủ động.
- Mất mạng toàn máy được nhận diện: dừng giữ tiến độ. Hết mọi lựa chọn:
  tạm dừng và nêu lý do. Không tự chuyển vì người dùng bấm Dừng, bản dịch sai
  số liệu, lỗi nguồn, lỗi bố cục hoặc lỗi ghi tệp.
- Checkpoint RC167/RC168 chưa có chính sách dự phòng vẫn dùng dịch vụ đã ghim.
  Không thay URL/model giữa chừng bằng lựa chọn mới trong Cài đặt.

Thuật ngữ và kiểm tra số liệu dùng chung. Prompt, giao thức, cache, key và bộ
đếm vẫn riêng theo dịch vụ. Một bài có thể có nhiều dịch vụ thực tế; metadata
ghi lại các dịch vụ đã dùng. Cần đọc lại bản dịch trước khi dùng để dạy.

## Kiểm chứng trên máy phát triển

- Kiểm thử Word: chọn trùng/chồng, câu thập phân, emoji/dấu tổ hợp, bảng,
  công thức, nội dung lặp, sửa số liệu, nguồn thay đổi, xuất lặp, sửa tệp ngoài,
  hoàn tác, sao lưu và khôi phục.
- Kiểm thử dịch vụ: chỉ thử bên có cấu hình, lỗi/quota/cooldown, giữ phần đạt,
  dừng/mất mạng, cấu hình cũ và cache/hạn mức riêng. API trong các ca này là
  fixture, không phải đánh giá chất lượng dịch thật của nhà cung cấp.
- Qt dùng thư viện tạm: luồng Word, bốn kiểu xuất, sửa/xóa vùng, giao diện sáng
  và tối, dừng/tiếp tục, mở lại thư viện và quay về PowerPoint.
- Mẫu Word của cả bốn kiểu đã mở bằng Microsoft Word không yêu cầu sửa tệp,
  xuất PDF và xem từng trang. Kiểm tra này chứng minh bố cục mẫu kiểm thử,
  không đại diện mọi tài liệu của giáo viên.

Không dùng thư viện cá nhân, key thật, tài liệu học sinh hoặc kết quả tạo ra
làm dữ liệu Git. Không thêm mô hình, phụ thuộc chạy nền hoặc bộ cài trong mốc này.
