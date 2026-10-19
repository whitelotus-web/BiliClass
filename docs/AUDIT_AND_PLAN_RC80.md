# Rà soát RC80 và kế hoạch tối ưu BiliClass

Ngày 19/10/2026. Phạm vi: RC80, mã ứng dụng tại `694c653`, HEAD tài liệu
trước rà soát `0e098fb`. Đây là đánh giá và kế hoạch, chưa triển khai các
thay đổi chức năng bên dưới.

## 1. Đánh giá chung

Luồng chuyển đổi, lưu bài, tạo giọng riêng, xuất PowerPoint và gắn Mascot đã
có nền kiểm thử tốt. Phần cần ưu tiên là sự thống nhất giữa các lối mở bài,
trạng thái đọc và thông báo. Giao diện dễ nhận diện, nhưng các màn vẫn mang
dấu vết của nhiều phiên bản luồng sử dụng khác nhau.

Mục tiêu sử dụng nên thống nhất:

**Tải PowerPoint lên → Chuyển đổi → Tạo giọng nếu cần → Mở PowerPoint cùng Mascot.**

Việc xác nhận câu hỏi/đáp án để mở lớp học là một công việc riêng. Không để
trạng thái duyệt câu hỏi khiến giáo viên hiểu rằng file PowerPoint hoặc
giọng đọc đang lỗi. Cảnh báo bố cục thật phải giữ lại, có vị trí và cách xử lý.

Trong các ca đã chạy lần này chưa có kiểm thử lõi thất bại. Điều đó không
chứng nhận mọi bản dịch, phát âm, bố cục hoặc thao tác PowerPoint thực tế.

## 2. Đã kiểm tra đến đâu

| Hạng mục | Bằng chứng lần này | Giới hạn |
|---|---|---|
| Mã giao diện | Kiểm kê 35 tệp QML, 500 định nghĩa điều khiển; 352 định nghĩa thuộc nhóm nút/vùng bấm | Có thành phần dùng lại, Repeater và luồng ẩn; không phải 500 nút hiện đồng thời hay đã bấm thủ công toàn bộ |
| Kiểm thử lõi | **915 passed**, một cảnh báo thư viện phụ thuộc | Tách hai nhóm Browser AI/Browser Translation khỏi lượt lõi; không đăng nhập tài khoản thật |
| Giao diện | **50 trạng thái**, cửa sổ 1080×700, 1366×850, 1920×1080; bảy tab Cài đặt; không cảnh báo QML | Dùng thư viện, PPTX và key giả cô lập; lời đọc ở các bài thử không phải chứng nhận phát âm |
| Luồng Qt bổ sung | **8/8 đạt**: cấu hình chuyển đổi, Google Dịch, kiểm tra/usage, lưu file, lớp học, dữ liệu/giọng, tạo giọng, độ phản hồi chuyển đổi | Google dùng fixture; âm thanh tạo giọng dùng WAV thử; lớp học thử tại máy |
| Tỷ lệ hiển thị | Qt Windows với `QT_SCALE_FACTOR=1.5`: màn chính có vùng làm việc 1280×693; khung app tối thiểu 1080×721 | Mô phỏng tỷ lệ logic trong tiến trình thử; chưa thay DPI Windows hay nghiệm thu EXE trên từng màn hình thật |
| Điều khiển đọc cũ | Probe bằng Bridge thật, worker native ghi lệnh và cache player được chặn | Chứng minh đường gọi/trạng thái; không thay thế thao tác chuột thực trên loa PowerPoint |
| Bản phát hành | Đối chiếu nguồn RC80, tài liệu build và bản đã cài | Kết quả native Office/TTS thật của mốc phát hành được tham khảo, không ghi là vừa kiểm lại trong lượt này |

Bằng chứng trên máy ở `reports/audit-rc80/`: `core-tests.log`, `qt-flows.json`,
`ui-inventory.json`, các PNG, `dpi150/ui-inventory.json`,
`source-controls.csv`, `source-summary.json`. Các tệp này không vào Git.

Luồng Qt phản hồi với tiến độ giả lập ghi nhận khoảng ngắt UI tối đa 47 ms,
dừng khoảng 47 ms và không kiểm WAV trên luồng giao diện. Đây là phép đo
fixture, không phải tốc độ chuyển đổi hoặc tổng hợp giọng của bài thật.

## 3. Vấn đề cần ưu tiên xử lý

P1: ảnh hưởng thao tác, tính nhất quán hoặc khả năng nhìn/bấm. P2: cải thiện
độ rõ ràng và chất lượng giao diện. P3: bảo trì và đo lường dài hạn.

### A01 — Bộ nút đọc cũ trong tool chưa đồng bộ với Mascot · P1

**Đã xác nhận bằng đường gọi và probe.** Ở màn bài giảng khi đang trình chiếu,
vẫn có bộ Đọc Anh/Việt/chung, Tạm dừng, Dừng đọc, Đọc lại. Bộ này lấy trạng
thái cache player. Mascot lấy trạng thái phiên dạy, gồm cả native PowerPoint.

Khi giả lập native đang đọc, màn tool vẫn ghi **Đã dừng**, nút Tạm dừng bị
khóa. `pauseEnglish()`/`resumeEnglish()` gọi cache player, không gửi lệnh
native; `stopSpeech()` không dừng native và trạng thái native vẫn `reading`.
Nút Anh cũ gọi `read()` thay vì `toggleRead()`.

Nguồn: [Main.qml](../app/qml/Main.qml), nhóm điều khiển quanh dòng 1243–1256;
[ui.py](../app/ui.py), `stopSpeech`, `pauseEnglish`, `resumeEnglish`;
[teaching_session.py](../app/teaching_session.py), `reader`, `toggleRead`, `stop`.

**Đề xuất:** dùng chung bộ điều khiển và trạng thái cho tool, Mascot, phím và
loa. Giữ cách bấm loa → tạm dừng → đọc tiếp; đổi ngôn ngữ dừng bản trước.
Loại bộ nút cũ trùng chức năng. Tách thao tác dừng cache nội bộ khỏi lệnh dừng
âm thanh người dùng, tránh gây vòng gọi trong xử lý sự kiện native.

### A02 — Các lối mở PowerPoint còn khác nhau · P1

**Đã xác nhận trong mã.** Thư viện và thẻ hoàn tất giọng dùng luồng mở/gắn
Mascot trực tiếp. Nút mở trước khi tạo giọng và màn kết quả vẫn đi qua
`prepareTeaching()` → `wholeLessonReview`. Dialog cũ khóa mở khi còn FAIL.
Nút trong menu “Mở trong PowerPoint” lại là luồng xem file riêng.

Nguồn: [Main.qml](../app/qml/Main.qml), `prepareTeaching`,
`voiceTeachWithoutNarration`, `useConvertedLessonButton`, `wholeLessonReview`;
[ui.py](../app/ui.py), `openTeachingLibraryLesson`, `openNarratedPowerPoint`,
`useConvertedLesson`, `openConvertedDeck`.

**Đề xuất:** mọi nút **Mở PowerPoint** chính dùng một đường mở cùng bài/bản
giọng và gắn Mascot. Xác nhận nội dung để dùng lớp học nằm riêng. Giữ cảnh báo
bố cục thật, giải thích khi không thể xuất/mở an toàn. Nếu cần luồng chỉ xem
file thì đặt rõ **Xem file PowerPoint**, trong menu phụ.

### A03 — “Sẵn sàng dạy” đang dùng hai nghĩa · P1

**Đã xác nhận trong mã và màn thử.** Bài chưa duyệt có thể mở PowerPoint cùng
Mascot, nhưng Trang chủ tính “Cần hoàn thiện” từ tổng bài trừ số đã duyệt;
thanh trạng thái vẫn ghi “Chưa chốt để dạy”. Bộ lọc cũng dựa trạng thái duyệt
cũ. Giáo viên có thể tưởng chuyển đổi hoặc voice chưa xong.

Nguồn: [HomeLibraryOverview.qml](../app/qml/HomeLibraryOverview.qml),
[LessonStateStrip.qml](../app/qml/LessonStateStrip.qml),
[library_view.py](../app/library_view.py), [lesson_state.py](../app/lesson_state.py).

**Đề xuất:** hiển thị riêng **Bài đã lưu**, **Giọng X/Y slide**, **Cảnh báo cần
xem** và **Câu hỏi đã duyệt**. Không gọi mọi bài chưa duyệt là bài cần sửa.
Trang chủ, thư viện, màn giọng, nút tải và Mascot phải dùng cùng định nghĩa.

### A04 — Nút trợ giảng trông dùng được nhưng thường chưa có nội dung · P1

**Đã xác nhận trong mã.** Giải thích/Ví dụ/Câu hỏi trên Mascot bật theo khả
năng điều khiển trình chiếu. Thực tế `assistant_response()` cần đoạn và nội
dung hỗ trợ đã duyệt; bài vừa chuyển có thể chỉ trả thông báo chưa chuẩn bị.
Các nút này hiện không tự sinh giải thích mới khi bấm.

Nguồn: [CompanionControls.qml](../app/qml/CompanionControls.qml),
[content.py](../app/content.py), [teaching_session.py](../app/teaching_session.py).

**Đề xuất:** đọc VI/EN/hai ngôn ngữ là nhóm chính. Công cụ trợ giảng phải
thể hiện đúng nội dung đang có của slide; chưa có thì hiện một chỉ dẫn ngắn
và đường chuẩn bị nội dung. Việc tự tạo nội dung trợ giảng mới là một hạng mục
riêng, phải xác định nguồn tạo và cách kiểm chứng trước khi bật cho giáo viên.

### A05 — Thông báo cũ đi theo sang màn không liên quan · P1

**Đã thấy trên ảnh thử.** Sau nhập PPTX rồi chuyển sang Google Dịch, footer
vẫn hướng dẫn kiểm tra lời đọc cho PowerPoint. Trạng thái lỗi/cảnh báo cuối
cũng có thể nằm lại qua nhiều màn.

Nguồn: [Main.qml](../app/qml/Main.qml), `applicationStatusMessage`.

**Đề xuất:** thông báo gắn với tác vụ/bài đang xử lý. Thành công ngắn có thể
tự thu gọn; lỗi còn cần xử lý phải giữ đường quay lại đúng bài và hành động
cụ thể. Không dùng footer toàn cục làm nơi chứa mọi cảnh báo lâu dài.

### A06 — “Hủy bài đang chọn” mang màu xóa nhưng chỉ bỏ chọn · P1

**Đã xác nhận.** Nút đỏ này ở màn giọng giữ bài và WAV; “Hủy chuyển đổi” lại
xóa bài đang tạo sau xác nhận. Cùng chữ Hủy nhưng hậu quả khác nhau.

Nguồn: [ui.py](../app/ui.py), `dismissNarrationLesson`, `_clear_narration_selection`;
[Main.qml](../app/qml/Main.qml), `dismissVoiceLesson`, `cancelConversionDialog`.

**Đề xuất:** dùng **Bỏ chọn bài** với nút phụ trung tính; **Dừng tạo giọng**
giữ âm thanh đã tạo; **Hủy và xóa bài đang tạo** có xác nhận ở bước chuyển đổi.
Phản hồi sau thao tác nói rõ dữ liệu được giữ hay xóa.

### A07 — Cửa sổ chưa thích ứng đủ với DPI/màn nhỏ · P1

**Đã đo.** Ở tỷ lệ logic 150%, khung tối thiểu cao 721 so với vùng làm việc
693. Trên màn phụ thử, vùng làm việc chỉ 960×573, nhỏ hơn cả chiều rộng và
chiều cao tối thiểu. Ở 1080×700, Lớp học nằm dưới vùng cuộn thanh điều hướng.

Nguồn: [Main.qml](../app/qml/Main.qml), `minimumWidth`, `minimumHeight`,
`sidebarNavigation`; bằng chứng `dpi150/ui-inventory.json`.

**Đề xuất:** giới hạn cửa sổ theo vùng làm việc của màn đang dùng; bố cục có
điểm chuyển cột và cuộn rõ ràng. Thu chân thanh bên, đưa thông tin bản quyền
đầy đủ vào Thông tin BiliClass. Đảm bảo các mục chính, nút lưu/tạo/hủy truy
cập được ở 100%, 125%, 150% và khi kéo qua màn phụ.

### A08 — Có thể chạy nhiều phiên/bản trên cùng thư viện · P1

**Đã quan sát tiến trình và rà điểm vào.** Trên máy có nhiều phiên RC73,
RC77, RC80 cùng tồn tại; điểm vào chưa có bộ chuyển yêu cầu sang phiên đang
mở theo thư viện. Shortcut mới không loại cửa sổ cũ đã chạy.

**Đề xuất:** một phiên cho một thư viện; mở lần nữa thì đưa phiên hiện tại
ra trước và chuyển yêu cầu mở bài. Cập nhật phải nhận diện bản cũ đang bận.
Kiểm tra đóng app và helper, phân biệt rõ thu nhỏ với thoát. Không tự tắt
cưỡng bức ứng dụng hay PowerPoint của giáo viên. Chưa kết luận có lỗi mất
dữ liệu hoặc deadlock từ việc chỉ quan sát các tiến trình này.

## 4. Bố cục và chi tiết cần tinh chỉnh

| Mã | Điểm quan sát | Hướng tối ưu | Mức |
|---|---|---|---|
| B01 | Trang chủ ưu tiên banner, bốn bước và mô tả tính năng; bài gần đây nằm thấp, kể cả ở cửa sổ lớn | Người mới thấy hướng dẫn; người đã có bài thấy bài gần đây và việc đang làm sớm hơn | P2 |
| B02 | Ở thư viện hẹp, nhóm nút chiếm nhiều ngang, tên bài dài chỉ còn ít chữ; nhiều nút nhóm bị khóa vẫn chiếm chỗ | Ưu tiên tên bài; Mở PowerPoint là nút chính; đưa tác vụ ít dùng vào menu; thao tác nhiều bài hiện theo ngữ cảnh chọn | P2 |
| B03 | Bộ chọn bài trong màn giọng/Mascot là danh sách dài, không có tìm kiếm | Tìm không dấu, hiện môn/khối và bản giọng; ưu tiên bài đang gắn, bài vừa dùng | P2 |
| B04 | Cài đặt có nhiều phần cuộn dài; một số mục tự lưu, một số phải bấm Lưu; trạng thái chưa lưu không đồng đều | Giữ bảy tab hiện có; quy tắc lưu rõ ở mỗi nhóm; báo thay đổi chưa lưu; nút lưu dễ tìm | P2 |
| B05 | Radio, SpinBox, TextField và nút dùng lẫn kiểu Basic mặc định với kiểu bo góc BiliClass | Dùng chung thành phần điều khiển, kích thước và trạng thái hover/focus/disabled; chuẩn hóa icon | P2 |
| B06 | Nhiều chữ phụ 9–11 px; màu `#667997` trên nền `#f3f7fc` có tương phản khoảng 4,11:1; `#687e9b` khoảng 3,87:1 | Chữ thao tác chính 14–15 px, chữ phụ thường từ 12 px; tăng tương phản chữ thường; trạng thái không chỉ dựa màu | P2 |
| B07 | Một số nút chính có border focus luôn trong suốt; quy tắc focus khác nhau giữa các component | Focus bàn phím nhìn thấy rõ; rà Tab/Shift+Tab/Enter/Escape và các hộp thoại | P2 |
| B08 | Ba ảnh mẫu đang minh họa bố cục văn bản gần giống nhau; khác màu rõ hơn khác công dụng | Chọn thumbnail đại diện: bài chữ cân đối, bài ảnh lớn, bài câu hỏi; giữ xem mẫu thật | P2 |
| B09 | Màn hoàn tất giọng vẫn có nhiều cấu hình, thông tin và nút phụ quanh kết quả | Ưu tiên kết quả + xem/nghe thử slide hiện tại; Mở PowerPoint và Tải PowerPoint dễ thấy; audio ZIP trong menu phụ | P2 |
| B10 | F1 còn nói DOCX/PDF/dán trong luồng Google hiện chỉ nhận PPTX; hướng dẫn còn nói tích kèm giọng/xác nhận cũ; bảng phím nhắc nút Dừng đọc trên Mascot đã bỏ | Viết lại theo giao diện thực tế; có kiểm tra đồng bộ tên nút, định dạng và đường đi | P1 |
| B11 | Xóa key là thao tác ngay; các mục hỗ trợ/câu hỏi cũng có chỗ xóa ngay | Xác nhận ngắn hoặc khả năng hoàn tác theo loại dữ liệu; không để bấm nhầm mất cấu hình đang dùng | P2 |
| B12 | Bộ đếm key là số tại máy nhưng dòng Còn X/Y dễ bị hiểu thành số dư từ dịch vụ | Giữ giao diện gọn; thêm nhãn/tooltip ngắn “Bộ đếm tại máy”, không thêm lại khối giải thích dài | P2 |
| B13 | Màn báo cáo chưa có dữ liệu vẫn hiện bộ chọn trống, nhóm xuất/xóa bị khóa và tiêu đề chọn phiên | Một trạng thái trống rõ cùng nút Mở lớp học; chỉ hiện công cụ báo cáo khi có phiên | P2 |
| B14 | Giọng có thời gian và số đoạn nhưng chưa có đo mới từng chặng cho bài thật | Đo nạp model, tạo WAV, cache và nhúng file; hiển thị chặng rõ; chỉ đưa ước lượng sau khi có dữ liệu đủ | P2 |

Không cần đổi thương hiệu, font Be Vietnam Pro hay xây lại toàn bộ giao diện.
Giữ các thành phần đã ổn, sửa chỗ mất nhất quán và chỗ cản thao tác trước.

## 5. Các phần đã ổn, cần giữ và kiểm thử chống tái lỗi

| Khu vực / nhóm nút | Kết quả hoặc bằng chứng | Điều cần giữ |
|---|---|---|
| Trang chủ: lời chào, bốn bước, chuyển màn | Kiểm mã và ảnh Qt | Lấy tên hồ sơ, mặc định Thầy cô; đúng thứ tự bốn bước |
| Chọn/kéo thả PPTX, tên bài, môn/cấp/khối | Qt cấu hình chuyển đổi đạt | Giới hạn đầu vào, tên lấy từ tệp, cấp/khối phù hợp |
| Kiểu chuyển đổi, giữ gốc/mẫu mới, thẻ mẫu | Qt nhiều kích thước đạt | Không đổi kích thước lựa chọn chỉ do đổi chế độ; tóm tắt cùng khung trắng |
| Chuyển đổi: tiến độ, Hủy, Tiếp tục, lỗi key | Qt Google fixture đạt | Hủy có xác nhận và đúng lượt; không chạy lại lượt đã hủy; không gửi dịch trùng khi chỉ cần khôi phục |
| Tạo giọng: ngôn ngữ, người đọc, tốc độ, vị trí loa | Qt workspace đạt | Mặc định Anh/lựa chọn gần nhất; vị trí cố định cả bài; đổi vị trí dùng lại WAV |
| Lời đọc thiếu, sửa lời, slide không đọc, nghe thử | Qt workspace đạt | Tách khỏi chữ trên slide; không đổi slide khi lời chưa lưu; OCR không tự đi vào lời đọc |
| Dừng/tạo tiếp, dùng bản có sẵn/tạo lại | Qt workspace đạt | Giữ phần đã tạo; dùng cache đúng cấu hình; không tự duyệt hoặc tự phát |
| Tải PPTX có/không giọng, ZIP âm thanh, tên gợi ý | Qt lưu file và workspace đạt | Tên có sẵn, đúng bản ngôn ngữ/giọng, nguồn riêng được giữ |
| Thư viện: tìm/lọc/sắp xếp, chọn nhiều, thùng rác | Lõi và kiểm mã/ảnh | Xóa bài vào thùng rác; xóa vĩnh viễn có xác nhận; không mất lựa chọn khi chỉ đổi kiểu xem |
| Mascot: chọn/gắn bài, F5, tiến/lùi, loa | Lõi mới và bằng chứng native của RC80 | Một bài được gắn rõ; tiến/lùi hiệu ứng rồi slide; chỉ hiện loa có giọng |
| Mascot: bánh răng, cỡ bảng, nền trong, nhãn môn | Qt/ảnh và bằng chứng hit test RC80 | Vào đúng tab, không mất gắn bài; nền trong không làm trong chữ/nút; không nhãn môn dưới chân |
| Phím: Anh/Việt/chung, đổi phím, mũi tên | Lõi mới; native RC80 tham khảo | Chỉ chặn phím trong trình chiếu đúng bài; ngoài PowerPoint không cướp phím |
| Hồ sơ, logo, giọng mặc định, lớp học mặc định | Qt dữ liệu/giọng đạt | Lưu đúng nhóm; không làm thay bản giọng đã tạo của bài khác |
| Google Dịch: nhập/lưu/đổi tên, bộ đếm, key kế tiếp | Qt Google và lõi đạt | Key mã hóa ở máy, không đồng bộ GitHub, không đưa vào gói bài/backup |
| Dữ liệu: backup, khôi phục, đổi ổ, chẩn đoán | Lõi và Qt dữ liệu đạt | Khôi phục vào nơi riêng; kiểm tra trước chuyển; giữ dữ liệu nếu thất bại |
| Lớp học: QR, câu hỏi, đóng/hiện đáp án, mất kết nối | Qt lớp học thử đạt | Đáp án ẩn trước công bố; trả lời đã xác nhận còn sau kết nối lại |
| Báo cáo: chọn phiên, tìm, kết quả, CSV | Qt lớp học thử đạt; rà màn trống | Có mẫu số rõ; khảo sát không chấm đúng/sai; không suy ra mức hiểu từ lượt nghe |
| Cập nhật, Properties EXE, mở độc lập | Lõi updater và bằng chứng phát hành RC80 | Phiên bản/nguồn/hash khớp; không gộp dữ liệu cá nhân vào bộ cài; mở EXE độc lập |

## 6. Kế hoạch triển khai có thứ tự

### Đợt 1 — Đồng bộ luồng dạy và trạng thái

Xử lý A01–A06 và B10. Tạo một đường mở bài và một nguồn trạng thái đọc cho
mọi bề mặt điều khiển. Rà lại tên nút, cảnh báo và nội dung F1 cùng thay đổi.

**Bàn giao:** giáo viên tải bài, chuyển đổi, tạo giọng rồi mở dạy bằng cùng
cách hiểu ở mọi màn. Bài chưa có voice vẫn mở PowerPoint được. Câu hỏi cần
duyệt được giải thích riêng. Các nút trợ giảng phản ánh đúng nội dung có sẵn.

**Nghiệm thu:** mở cùng bài từ thư viện, màn giọng, kết quả và Mascot phải
ra cùng file/bản giọng và liên kết. Bấm cùng ngôn ngữ để phát/tạm dừng/tiếp
tục; đổi ngôn ngữ chỉ có một nguồn phát; bấm từ tool cũng cập nhật Mascot và
ngược lại. Đổi slide/bài không phát tiếp âm thanh slide cũ. Không còn thông
báo tác vụ cũ hoặc chỉ dẫn nút không tồn tại. Kiểm cảnh báo bố cục và luồng
hủy đúng hậu quả dữ liệu, không bỏ qua lỗi thật để làm trạng thái xanh.

### Đợt 2 — Cửa sổ, bố cục và khả năng đọc

Xử lý A07, B01–B08, B13. Giữ các tab, thu chân thanh bên, chuẩn hóa input,
radio, spinner, nút và focus. Dành không gian cho tên bài. Phân tầng cấu hình
thường dùng với tùy chọn nâng cao.

**Bàn giao:** một bộ thành phần giao diện nhất quán; các màn chính có hành
động rõ và phần phụ không lấn át nội dung.

**Nghiệm thu:** cả luồng chạy được ở 1080×700, 1366×768/850 và 1920×1080;
thử DPI 100/125/150%, màn phụ, tên bài/tên giáo viên dài, thư viện trống và
nhiều bài. Không mất nút cuối trang; không bắt cuộn thanh bên để tìm mục
chính nếu có thể bố trí vừa. Dùng Tab/Shift+Tab/Enter/Escape hoàn thành luồng;
focus và lý do nút bị khóa phải đọc được. Ảnh mẫu phân biệt công dụng thật.

### Đợt 3 — Hoàn tất giọng, kiểm tra đầu ra và hiệu năng có đo

Xử lý B09, B14; mở rộng bộ bài thử cho chữ, bảng, công thức, ảnh/OCR,
hiệu ứng, slide sát mép và nhiều ngôn ngữ. Giữ công thức/ảnh và nội dung,
chỉ nhận sửa bố cục khi kiểm chứng cải thiện. Khi không thể tự sửa hết,
thông báo chính xác phần nào và đường xem, không gọi chung mọi CHECK là lỗi.

**Bàn giao:** màn hoàn tất ưu tiên xem/nghe thử, mở dạy và tải đúng file;
tiến độ phân chặng; có bảng đo trước/sau để chọn tối ưu có ích.

**Nghiệm thu:** bài nhỏ/vừa/lớn và lần chạy nguội/nóng; ít nhất 10 lượt đo
cùng cấu hình khi công bố tăng tốc. Kiểm sửa một đoạn chỉ tạo lại phần cần,
dừng/tạo tiếp không làm lại toàn bài, chữ OCR trong ảnh không tự được đọc.
PowerPoint tải ra có loa đúng vị trí, không toolbar media khi rê loa; phát,
tạm dừng, đọc tiếp, đổi loa bằng chuột thực. Kiểm cả mở độc lập và gắn Mascot.

### Đợt 4 — Một phiên ứng dụng, dữ liệu và phát hành

Xử lý A08, B11–B12. Rà mở lại/đóng app, sao lưu, khôi phục, thay ổ, lỗi
thiếu quyền/hết chỗ và cập nhật. Chuẩn hóa quy trình build/phát hành có thể
lặp lại từ mã đã lưu, các helper phát hành cần thiết được quản lý phù hợp.
Tách dần `ui.py`/`Main.qml` theo chức năng khi sửa phần liên quan; không viết
lại toàn hệ thống trong một lần.

**Bàn giao:** mở lần nữa không tạo hai Mascot cùng thư viện; phiên bản đang
dùng dễ nhận biết; lỗi dữ liệu có cách phục hồi; tài liệu khớp bộ cài.

**Nghiệm thu:** cập nhật từ bản cũ, đang bận/đang lưu, đóng bình thường và
khởi động lại; không bỏ lại helper ngoài ý muốn, không tắt PowerPoint người
dùng. Cài/gỡ giữ thư viện; ZIP/hash/Properties/phiên bản khớp. Không đưa key,
thư viện, model tải, báo cáo hay EXE vào commit nguồn. Phiên dạy dài và lớp
học qua Wi-Fi thật cần một vòng nghiệm thu riêng trước phát hành rộng.

**Quyết định cần chốt:** API GitHub ngày rà soát trả `private: false`,
`visibility: public` cho `whitelotus-web/BiliClass`, khác mô tả kho riêng tư
trong quy ước làm việc. Không tự đổi visibility hoặc làm hỏng updater. Cần
chọn rõ chính sách mã nguồn và kho phát hành; xem xét tách nguồn riêng tư
khỏi bản phát hành công khai nếu đó là mong muốn của chủ dự án.

## 7. Những phần chưa được chứng nhận trong lượt này

- Chưa bấm chuột thực trên mọi loa của toàn bộ PPTX tải độc lập, mọi bản
  Office, máy chiếu hoặc màn hình trình chiếu mở rộng.
- Chưa nghe và duyệt phát âm/nghĩa của toàn bộ giọng, thuật ngữ và công thức.
- Chưa chạy API Google có tính phí hay đăng nhập Browser AI bằng tài khoản thật.
- Chưa nghiệm thu lớp học đông qua router/điện thoại thật hay phiên RC80 mới
  kéo dài nhiều giờ. Bằng chứng phiên dài của mốc trước có phạm vi riêng.
- Chưa thực hiện các thao tác xóa/khôi phục để thử trên thư viện giáo viên.
  Kiểm thử dùng dữ liệu riêng; tiến trình BiliClass đang dùng được giữ nguyên.

Không nên đóng gói lại chỉ để chứa báo cáo này. Bản tối ưu tiếp theo cần
hoàn thành các thay đổi được chọn, chạy kiểm thử thích hợp, rồi mới build
một lần tại mốc đã kiểm chứng và mở EXE độc lập để giáo viên thử.
