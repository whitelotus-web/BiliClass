# BiliClass RC29 — hướng dẫn dùng thử

Màn chuyển đổi hiện thời gian xử lý **giờ:phút:giây**. Đồng hồ đứng lại khi
tạm dừng; tiếp tục sẽ cộng thời gian đã lưu. Nếu báo tạm dừng thì chờ ở màn
hình đó không làm bài tự hoàn thành. Tool lưu bài đang làm và cuộc trò chuyện
để kiểm tra/tiếp tục, không tự gửi lại toàn bộ tài liệu. Không có đếm ngược
chính xác vì dịch vụ web không cung cấp thời điểm hoàn tất. PowerPoint được
lưu trước; tạo giọng đọc là bước riêng nếu thầy cô cần.

## Cài lần đầu

1. Mở [Release RC29](https://github.com/whitelotus-web/BiliClass/releases/tag/v1.0.0rc29), tải **BiliClass-RC29-Windows.zip** trong Assets.
2. Giải nén toàn bộ bằng Windows; không chạy ứng dụng ngay trong cửa sổ ZIP.
3. Chạy **Setup.cmd**. Bộ cài kiểm tra checksum, cài vào `%LOCALAPPDATA%/Programs/BiliClass/<version>` và tạo mục Start menu, không cần quyền quản trị.
4. Mở BiliClass từ Start menu, vào **Cài đặt → Browser AI**, chọn **ChatGPT hoặc Gemini**, bấm **Thêm tài khoản** để đăng nhập. Mỗi máy tự đăng nhập; không sao chép profile của người khác. Có thể thêm nhiều tài khoản độc lập cho từng dịch vụ và tích chọn tài khoản cụ thể để chuyển đổi, hoặc dùng Tự chọn tài khoản đang kết nối.
5. Chọn/nghe thử giọng trong tab Giọng đọc và kéo tốc độ, sau đó bấm Lưu giọng và tốc độ.

Yêu cầu: Windows 10/11 64-bit; Google Chrome; Microsoft PowerPoint desktop để giữ trình chiếu, animation và điều khiển slide. Cần Internet khi chuyển đổi bằng ChatGPT. Bộ cài đã có sáu giọng VieNeu đa ngôn ngữ, một giọng đọc cả Việt và Anh, mẫu và ảnh xem trước; không cần Python, API key hay tải model riêng.

Portable: chạy `BiliClass/BiliClass.exe` trong thư mục đã giải nén. Giữ nguyên `_internal`, `models`, `licenses`. Không mở đồng thời bản nguồn và bản cài với cùng thư viện.

Trong Cài đặt, Browser AI ở vị trí thứ hai, Song ngữ ở cuối. Nút **Mở tài khoản** trên mỗi profile mở đúng phiên Chrome đã lưu, không tạo tài khoản mới; khi đóng cửa sổ hoặc bấm Kiểm tra và lưu, tool xác minh lại phiên. Hoàn tất tác vụ/profile đang mở trước khi mở tài khoản khác.

Lựa chọn ChatGPT/Gemini áp dụng cho bài mới. Bài đã gửi tiếp tục đúng dịch vụ và profile cũ, không gửi lại sang dịch vụ khác khi bạn đổi cài đặt. Trước lượt gửi/sửa, tool chọn và xác nhận model/suy luận mạnh nhất trong các lựa chọn đọc được và được phép dùng. Không thấy hoặc không xác nhận được lựa chọn thì báo cần kiểm tra tài khoản, không tự gửi bằng Fast/Instant. Gemini chưa công bố gói tin cậy trong giao diện thì hiện Chưa rõ gói, không đoán Pro từ nút nâng cấp. Tệp gửi Gemini tối đa 100 MB; quyền tải tệp/Canvas/Slides tùy tài khoản. [Chi tiết Browser AI](BROWSER_SERVICES.md).

Logo tải ở **Chung** cũng hiện cạnh tên giáo viên ở chân thanh bên. Không có logo thì hiện chữ cái tên; thay/bỏ logo cập nhật ngay. Tùy chọn hiện hồ sơ trên bài giảng chỉ điều khiển phần hồ sơ trong bài. Thông báo bản quyền được căn giữa dưới phiên bản ở thanh bên, không được tự thêm vào tài liệu hoặc prompt của giáo viên:

```text
© 2026 Nguyễn Diệu Linh
Giáo viên Tin học - Trường THPT Vân Cốc
All rights reserved.
```

“All rights reserved.” thông báo bảo lưu quyền, không phải thủ tục đăng ký bản quyền. [WIPO giải thích về ký hiệu © và bảo hộ tự động](https://www.wipo.int/en/web/copyright/faq-copyright). Các giấy phép thành phần bên thứ ba vẫn nằm trong thư mục `licenses` của bản cài.

## Tạo bài giảng

Trong **Bài giảng**, mỗi bài có giờ/ngày tạo và các nút Mở bài, Sửa, Xóa. Chọn Mới tạo nhất/Tạo lâu nhất/Mới cập nhật để sắp xếp. Sửa cho đổi thông tin bài hoặc mở biên tập nội dung trợ giảng. Đổi tên không thay ngày tạo hay yêu cầu duyệt lại nội dung; đổi môn vẫn cần duyệt lại.

Xóa đưa bài vào thùng rác. Mở **Chia sẻ & quản lý → Thùng rác** để khôi phục, giữ nguồn, âm thanh và báo cáo. Kết thúc trình chiếu/tiết học trước khi xóa. Với bài cũ không còn phiên bản đầu tiên, ngày lưu sớm nhất còn giữ được hiển thị thay cho việc đoán chính xác ngày tạo.

1. Vào Bài giảng → tạo bài mới; kéo thả hoặc chọn tài liệu. Hỗ trợ PPTX, DOCX, PDF, TXT, PNG/JPG; cũng có thể dán nội dung. PowerPoint `.ppt` cũ cần lưu lại thành `.pptx`.
2. Điền tên bài, chọn môn; **Khác** cho phép nhập tên môn. Chọn cấp học để danh sách khối lớp đổi theo Tiểu học 1–5, THCS 6–9, THPT 10–12.
3. Chọn một kiểu chuyển đổi: **Hai cột song ngữ** (Việt trái/Anh phải), **Song ngữ từng câu** (Việt trên/Anh dưới), **Tích hợp từ khóa** (Việt xen thuật ngữ Anh), **Tiếng Anh 100%** (chữ slide bằng Anh; lời đọc Việt lưu riêng trong ghi chú).
4. Với PPTX, **Giữ bài giảng đầu vào** yêu cầu chỉnh bản sao của đúng PowerPoint nguồn, giữ số lượng/thứ tự slide và đối tượng tối đa. **Tạo theo mẫu mới** dùng nội dung nguồn trong mẫu Chuẩn lớp học, Trực quan hoặc Luyện tập & tương tác. Các mẫu có ảnh bố cục và ví dụ bốn phương pháp.
5. Ghi lưu ý thêm nếu cần. Nút hiện/ẩn prompt cho xem chính xác yêu cầu chuẩn bị gửi.
6. Bấm **Chuyển đổi bài giảng** một lần. BiliClass tự xử lý tài liệu, biên soạn, kiểm tra và lưu bài giảng. Tiến trình đạt 100% thì mở bài và **dừng ở bước bài giảng song ngữ**. Bạn có thể tải PowerPoint ngay, xem bài rồi dùng để dạy mà không tạo voice. [Giữ phiên và mở bài nhanh hơn](SESSION_AND_SPEED.md).
7. Nếu cần giọng, chọn **Tiếng Anh**, **Tiếng Việt** hoặc **Việt + Anh**, rồi bấm **Tạo giọng đọc** ngay trên màn bài giảng. Đây là bước riêng chạy trên máy, không gửi lại tài liệu; dùng giọng đa ngôn ngữ và tốc độ đã lưu trong Cài đặt. Có tiến độ riêng và nút Dừng; dừng/lỗi giữ các WAV đã tạo. Bấm tiếp tục chỉ tạo phần còn thiếu. Mở lại bài không tự chạy bước này. Thư viện đánh dấu Chỉ bài giảng song ngữ, Có giọng Tiếng Anh/Tiếng Việt/Việt + Anh, hoặc Giọng đọc chưa đủ/cần cập nhật.
8. Xem bài và cảnh báo trước khi **Dùng để dạy**. Bản dịch, công thức, hình và hiệu ứng cần đối chiếu với nguồn. Có voice không có nghĩa là đã duyệt nội dung; quiz vẫn là bản nháp cần duyệt riêng. Slide có lỗi cần sửa chặn xác nhận dạy và tạo voice cho tới khi hoàn thiện.

Thời gian phụ thuộc kích thước tệp, mạng và tài khoản Free/Plus. Khi web yêu cầu xác minh/đăng nhập hoặc hết hạn mức, tool báo để bạn xử lý; không bảo đảm mọi yêu cầu đều chạy hoàn toàn không can thiệp. Không gửi trùng yêu cầu đã gửi chỉ vì mất kết nối. Hạn mức không có số dư tin cậy thì không hiển thị số tự đoán.

RC26 nhận diện thông báo gián đoạn luồng trả lời ngay cả khi web vẫn hiện đang tạo. Tool tự tải lại đúng cuộc trò chuyện tối đa hai lần cho mỗi lượt đã gửi; số lần được lưu qua lần mở app. Không gửi lại prompt/tài liệu để khôi phục. Nếu web vẫn gián đoạn, bài và tiến trình được giữ; không báo hoàn tất hoặc làm mất phiên đăng nhập chỉ vì lỗi mạng.

## Dạy với PowerPoint, giọng và mascot

Màn slide có **Trở lại thư viện**, **Tải PowerPoint** và **Dùng để dạy**. Tải PowerPoint lưu nguyên tệp đang xem vào vị trí bạn chọn, giữ hình/hiệu ứng trong tệp đó; không tự tạo lại mẫu mới hoặc nhúng các WAV vừa tạo. Voice lưu riêng trong thư viện để BiliClass đọc với mascot. Muốn mở file bằng PowerPoint hoặc sửa/gửi gói bài, dùng **Thao tác khác**. Không ghi đè file trong thư viện nguồn.

**Dùng để dạy** mở bài kết quả bằng PowerPoint toàn màn hình. PowerPoint thực thi các hiệu ứng trong tệp; BiliClass theo slide thực tế để đọc Anh/Việt và cung cấp trợ giảng.

Mascot nổi trên nền trong suốt. Kéo để đổi vị trí, nhấp để mở/thu các nút đọc, tiến/lùi slide và trợ giảng. Có thể mở lại từ thanh bên nếu đã ẩn. Bài không có voice vẫn trình chiếu và dùng quiz/điều khiển slide; nút đọc chỉ bật cho ngôn ngữ đã chọn ở bước tạo giọng. Âm thanh dùng đúng giọng/tốc độ lúc tạo, không cần gọi ChatGPT mỗi khi đọc. Muốn đổi giọng hoặc tốc độ của bài đã tạo âm thanh, lưu cấu hình mới rồi bấm Tạo lại giọng đọc.

**Đọc tiếng Anh** đọc hàng đợi từ chữ English thực trên slide, gồm tiêu đề và thân bài xác định được, không chỉ EN trong ghi chú. Có Tạm dừng/Tiếp tục, Dừng và Đọc lại; đổi slide/bước hoạt ảnh thì dừng. Phần ảnh, công thức hoặc hoạt ảnh chưa xác minh được sẽ báo cần kiểm tra và không tự đọc. Không có English thì báo rõ.

RC25 kiểm tra/render từng slide, sửa cỡ chữ bị tràn và đồng nhất font tiêu đề trên bản sao bằng PowerPoint. Tiêu đề Việt ở trên, Anh ngay dưới, cùng font, Anh nhỏ hơn và in nghiêng. Hai cột thân bài được đối chiếu riêng; hình khoa học có thể dùng một vùng riêng cạnh hai cột. Chỉ dịch tiêu đề hoặc thêm lời Anh trong ghi chú chưa được coi là dịch đủ nội dung.

Nếu còn lỗi có thể xử lý, tool yêu cầu sửa trong cùng cuộc trò chuyện tối đa ba lượt, chỉ nhận bản có kiểm tra cải thiện và không mất tài nguyên gốc. Dừng khi không cải thiện, cần đăng nhập/xác minh hoặc hết hạn mức; giữ bản tốt nhất và tiến trình để tiếp tục, không gửi lại yêu cầu chưa rõ xác nhận. Bài đã lưu có nút **Tự sửa bài giảng**. Bản sửa tạo phiên bản mới, giữ bản trước, không tự duyệt bài hoặc quiz. Lỗi cần sửa chặn xác nhận Dùng để dạy; các phần cần rà soát vẫn cần giáo viên đối chiếu. Chi tiết lỗi được nhóm theo loại và số slide trong **Xem chi tiết**.

## Quiz và báo cáo

Câu hỏi cần kiểm tra nguồn, câu Việt/Anh, lựa chọn và đáp án trước khi duyệt. Trong Lớp học, chọn lớp/IP LAN và mở câu; học sinh cùng mạng quét QR bằng trình duyệt. Cho phép đổi đáp án trước khi đóng. Chỉ công bố đáp án khi giáo viên chọn. Kết thúc phiên để lưu báo cáo, có xuất CSV. Dữ liệu học sinh không được đẩy lên GitHub.

Nếu điện thoại không vào được: kiểm tra cùng mạng, đúng IP, Firewall mạng riêng và router có chặn các thiết bị truy cập nhau không. Khi mạng/cổng đổi, dùng QR mới.

## Cập nhật, sao lưu và chuyển máy

App tự kiểm tra GitHub khi mở; có **Kiểm tra cập nhật**. Khi có bản mới, chọn **Cập nhật**, chờ app tải/xác minh/cài rồi tự mở lại. Bản mới được đặt cạnh bản cũ. Thư viện bài học giữ tại `%LOCALAPPDATA%/BiliClass`; không xóa thư mục này khi cập nhật.

**Xuất gói bài** tạo `.biliclass` để chuyển một bài cho giáo viên khác. Bản nhận cần duyệt lại trước khi dạy. Gói có giới hạn kích thước; bài lớn cần chia nhỏ hoặc chuyển nguồn/kết quả riêng.

`.biliclass` là gói riêng của BiliClass, gồm bài, nguồn và dữ liệu trợ giảng/quiz/audio có thể chuyển. Đây là chức năng chia sẻ tùy chọn, không cần dùng để tạo hoặc dạy bài thông thường. Nhận gói ở **Thư viện → Chia sẻ & quản lý**; gửi gói ở **Màn slide → Thao tác khác**. Người chỉ cần file để dạy dùng **Tải PowerPoint**.

**Sao lưu thư viện** và **Khôi phục bản sao** phục vụ chuyển dữ liệu cá nhân; khôi phục tạo thư mục mới. Model/ứng dụng cài riêng; đăng nhập ChatGPT lại trên máy mới. GitHub dùng để chia sẻ code và bộ cài, không tự đồng bộ thư viện hoặc tài khoản.

Muốn sửa code, xem phần Phát triển trong [README](../README.md); thử từ mã nguồn không cần dựng `.exe` mỗi lần.
