# Quy trình mới ngày 09/10/2026

Luồng nhập mới chỉ có một bộ chọn **Kiểu chuyển đổi** gồm bốn phương pháp, dùng ChatGPT Browser. Xem [hợp đồng chuyển đổi và kế hoạch thu gọn](FOUR_FORMAT_WORKFLOW.md). Các phần level/offline dưới đây ghi lại luồng cũ còn giữ để đọc bài/gói đã lưu, không phải các lựa chọn trong bước nhập mới.

# Nhập bài và chuyển đổi theo level (luồng cũ)

Trạng thái: mã nguồn ngày 03/10/2026, chưa đóng trong release rc12. App bố trí và dịch nội dung giáo viên cung cấp; không tự xác nhận kiến thức đúng hoặc có sẵn đủ kiến thức mọi môn.

## Luồng chính: cấu hình ngắn, chuyển đổi, trình chiếu

1. Chọn tài liệu hoặc dán nội dung; tên bài được gợi ý từ tên tệp. Điền môn/khối, chọn L0–L4 (mặc định L2) và kiểu sắp xếp Việt–Anh.
2. Với PPTX, chọn **Giữ PowerPoint gốc** hoặc **Theo mẫu BiliClass**. Tài liệu khác dùng mẫu; **Xem slide mẫu** có ví dụ với hình và từng loại slide.
3. Thiết lập trong **Cài đặt → Browser AI → Đăng nhập ChatGPT** bằng tài khoản Free/Plus trên Edge riêng. Phiên tự lưu; có thể thêm tài khoản, ưu tiên Plus hoặc cố định Free để thử. Bấm **Chuyển đổi bằng ChatGPT**: app gửi prompt và tài liệu gốc theo cấu hình, nhận PPTX rồi chuẩn bị giọng đọc; giáo viên xem và xác nhận trước khi dạy. Khả năng tạo tệp/model theo tài khoản trên web; hết quota hoặc cần xác minh thì dừng, không tự đổi tài khoản. [Phạm vi kiểm tra](BROWSER_AI.md). Có **Gửi/nhận PowerPoint thủ công** trong Tùy chọn thêm.
4. Xem slide hoặc **Xem toàn bộ bài**. Kiểm tra nội dung, số liệu, công thức và bố cục.
5. Bấm **Dùng để dạy** và xác nhận cả bài một lần. Nội dung AI và hỗ trợ gắn nguồn vẫn là nháp trước xác nhận; quiz và kho kiến thức không được tự duyệt. Nguồn gốc giữ nguyên; PPTX nhận thủ công cũng giữ nguyên byte. Lời đọc English và mascot dùng phần hỗ trợ theo level.

**BiliClass ngoại tuyến** dùng model dịch/OCR tại máy; các mô tả batch/model/OCR phía dưới áp dụng cho lựa chọn này. **Chỉnh sửa chi tiết** chỉ mở khi cần. Bài JSON có thể sửa rồi dựng lại tại máy mà không gửi AI lại; PPTX nhận thủ công cần nhận file mới khi sửa chữ.

Luồng tự động xử lý toàn bộ phần thiếu, không dừng ở 50 đoạn/lượt như nút dịch trong trình biên tập. Nội dung dài được chia theo giới hạn model và nối lại trong đúng vùng nguồn; giữ dấu phân hàng/cột bảng và biểu thức được bảo vệ. Bản có sẵn, đoạn khóa và đoạn đã duyệt không bị tự dịch lại. Cặp tiêu đề Việt–Anh có một dấu `|` được nhận diện; bảng PowerPoint vẫn giữ lưới.

Kết quả chuyển đổi **chưa tự được duyệt**. Bản xem trước dùng một bản sao xuất riêng, không ghi trạng thái duyệt vào thư viện. Thiếu ngôn ngữ, model chưa có hoặc bộ nhớ giáo viên có nhiều bản xung đột thì app báo vị trí cần xử lý trong Chỉnh sửa chi tiết. Không cho chốt bài thiếu cặp; tệp nguồn, phiên bản bài và checksum bản trình chiếu phải khớp lúc xác nhận. Sửa bài xong cần chuyển đổi/xem lại rồi xác nhận bản mới. Kiểm tra nhanh số liệu chỉ là hỗ trợ, không xác nhận ý nghĩa hay độ đúng kiến thức.

Xem trước bằng ảnh và trình chiếu điều khiển trực tiếp cần Microsoft PowerPoint trên máy. Nếu không render được ảnh, bản `.pptx` vẫn được tạo để mở bằng ứng dụng phù hợp. Quiz/audio không phải điều kiện để chốt nội dung bài.

## Hai cách tạo bản trình chiếu trên màn hình chính

**Giữ bài giảng của tôi** dành cho PPTX đã soạn: giữ bố cục/đối tượng và thêm hỗ trợ song ngữ. **Tạo bài với BiliClass** dành cho văn bản, DOCX, PDF, ảnh hoặc PPTX muốn bố trí lại theo mẫu. Cả hai dùng chung đoạn VI/EN, trợ giảng và quiz đã duyệt.

| Đầu vào | Gợi ý | Giáo viên quyết định |
|---|---|---|
| PPTX tiếng Việt | Giữ bài, bổ sung theo level | Chọn L0–L4, tạo nháp phần Anh rồi duyệt. |
| PPTX đã Việt–Anh | Giữ nguyên + trợ giảng | Xác nhận cặp nhận diện; giữ nguyên hoặc bổ sung. L0–L3 không tự xóa phần Anh có sẵn. |
| PPTX tiếng Anh | Giữ bài, bổ sung tiếng Việt | Tạo nháp phần Việt. Anh gốc không bị giảm khi chọn level thấp. |
| PPTX trộn Việt/Anh | Giữ nguyên + trợ giảng | Kiểm tra hướng dịch từng đoạn; không coi mọi khối cùng slide là cặp tương đương. |
| PPTX chỉ ảnh trang sách | OCR, dùng template | Kiểm tra chữ, chia ý và chọn mẫu. |
| DOCX/TXT/PDF có text | Tạo bài theo template | Kiểm tra thứ tự, bổ sung VI/EN, chọn L0–L4. |
| PNG/JPG/PDF scan | OCR, dùng template | Chuẩn bị model một lần, sửa chữ/dấu/bảng/công thức trước dịch. |
| Chưa rõ ngôn ngữ | Báo chưa xác định | Chọn Việt/Anh cho phần chưa nhận diện hoặc sửa nguồn. |

Nhận diện là gợi ý: tiêu đề ngắn, tên riêng, chữ không dấu hoặc ngôn ngữ khác có thể sai. Cặp có nhãn VI:/EN: hoặc dòng rõ ràng được đưa vào hai ô nhưng chưa duyệt. Số/công thức trung tính giữ ở cả hai ô. Nguồn được lưu theo hash, không ghi đè.

## Công cụ chi tiết của luồng ngoại tuyến

1. Chọn tệp, chờ **Đánh giá đầu vào**, kiểm tra môn/khối, luồng, cách chuyển đổi và L0–L4. Nhập tay vẫn dùng được.
2. Tạo bài rồi **Dịch phần còn thiếu**: tối đa 50 đoạn/lượt, chỉ điền ô ngôn ngữ trống của đoạn chưa duyệt/chưa khóa. Cặp có sẵn không bị viết lại.
3. Kiểm tra thuật ngữ, số liệu, ngữ nghĩa rồi **Duyệt đoạn**. Bản nháp từ memory cũng cần duyệt trong bài mới. Dịch máy giới hạn 2.000 ký tự/350 token mỗi đoạn; tách đoạn dài hoặc nhập bản dịch. **Dừng tác vụ** hủy áp dụng loạt đang chạy; revision đổi cũng chặn ghi kết quả cũ.
4. Chuẩn bị/duyệt thuật ngữ, câu lớp học, câu Anh dễ, lời giải thích và quiz. Khi dùng template, chọn **Theo level L0–L4** để dùng cùng quy tắc nội dung.
5. So sánh PowerPoint hoặc xem trước template, kiểm tra hiệu ứng trong PowerPoint thật. Xuất **PPTX** và/hoặc **Gói bài**, chuẩn bị audio rồi dùng mascot khi dạy.

Ưu tiên dịch: thuật ngữ giáo viên → bản dịch đã duyệt cùng môn → mục kho nền/online đã nhập trên máy → model offline. Không truy vấn web trong lượt dịch. Có nhiều bản duyệt khác nhau thì yêu cầu chọn riêng.

| Level | Hỗ trợ đã duyệt |
|---|---|
| L0 | Từ khóa Anh cạnh nội dung Việt. |
| L1 | Từ khóa và câu lớp học. |
| L2 | Câu Anh dễ; thiếu thì lấy câu đầu bản Anh đã duyệt và báo rõ, không tự viết lại cho dễ. |
| L3 | Bản Anh đầy đủ cùng nội dung Việt. |
| L4 | English, tiếng Việt trong dự án cho VI Rescue. |

## OCR và giới hạn

**Chuẩn bị OCR Việt–Anh (tải một lần)** trong Cài đặt dữ liệu tải model công khai có checksum. Sau đó nhận ảnh/PDF trên máy, không gửi tài liệu ra dịch vụ. Model nằm ngoài Git. Chưa có bộ này thì OCR Anh có thể dùng gói Windows đã cài; OCR Việt yêu cầu bộ cục bộ.

Đã chạy ảnh/PDF scan Việt bằng engine thật, nhưng vẫn sai một số dấu. Ảnh mờ, nhiều cột, bảng, ký hiệu, công thức và chữ viết tay có thể thiếu/sai. Giáo viên phải sửa chữ OCR trước duyệt, tạo đáp án hoặc chuyển bài.

Định dạng hiện hỗ trợ: PPTX, DOCX, PDF, TXT, PNG/JPG. PPT/DOC cũ cần lưu thành PPTX/DOCX; HEIC cần đổi PNG/JPG. Tệp nguồn tối đa 50 MB, có thêm giới hạn trang/độ dài. Tài liệu mã hóa, lỗi cấu trúc hoặc scan quá lớn cần đổi định dạng/chia nhỏ. Có thể nhập nội dung mọi môn; không bảo đảm dịch đúng mọi môn hoặc mọi file.

Gói bài giữ thuật ngữ và giọng/mascot làm **tham chiếu của bài**. Người nhận kiểm tra/duyệt lại; tham chiếu không tự thay Cài đặt/thuật ngữ máy nhận.
