# Kế hoạch kết nối ChatGPT và chuyển đổi bài giảng

Ngày đối chiếu: 03/10/2026. Trạng thái: **đã triển khai OAuth và luồng JSON → PowerPoint trong mã nguồn; chưa xác nhận kết nối trên tài khoản thật**. Hướng dẫn và bằng chứng hiện tại: [BROWSER_AI.md](BROWSER_AI.md). Release RC12 chưa chứa thay đổi này.

Đã có PKCE/state/nonce, kiểm tra ID token ký số, lưu DPAPI, refresh/revoke, catalog/Responses stream, validator tham chiếu nguồn, chia/cache từng phần, hỏi trước khi gửi lại lượt chưa rõ kết quả, dựng nguồn/mẫu, nhận diện ảnh nguồn và lời đọc theo level. Giao diện Qt với AI giả lập đã chạy qua PowerPoint thật và xác nhận cả bài. Đăng nhập thật chưa thành công: người dùng báo trang lỗi trước callback, chưa rõ thông báo cụ thể; mốc 0 và nghiệm thu hai giáo viên vẫn chưa đạt. Nhận JSON thủ công, chọn nhiều model và đánh giá chất lượng trên giáo án thật còn ở kế hoạch; luồng thủ công hiện vẫn nhận PPTX.

Người dùng đã xác nhận chấp nhận kết nối chính thức dùng hạn mức ChatGPT, không cần API key hoặc billing API riêng. Kết nối này vẫn gọi Responses API bằng quyền OAuth; không đồng nghĩa với việc điều khiển trang ChatGPT web.

## 1. Quyết định kiến trúc

AI xử lý nội dung song ngữ; BiliClass xử lý tệp PowerPoint, bản xem trước, giọng đọc và trợ giảng. Nguồn thầy cô đưa vào luôn được giữ nguyên tại máy.

OpenAI hiện tài liệu hóa Sign in with ChatGPT cho ứng dụng nguồn mở và dự án cá nhân chạy tại máy; Plus/Pro đủ điều kiện có thể cho ứng dụng dùng hạn mức gói. Phải kiểm tra quyền thực tế của tài khoản và ứng dụng, không chỉ dựa vào nhãn Plus. [Quickstart](https://developers.openai.com/siwc/quickstart), [hướng dẫn tích hợp](https://developers.openai.com/cookbook/articles/sign-in-with-chatgpt).

Thay luồng điều khiển DOM của chatgpt.com bằng kết nối chính thức sau khi thử nghiệm thành công. Giữ lựa chọn gửi/nhận thủ công và ngoại tuyến để bài cũ còn sử dụng được. Không thêm luồng thanh toán API riêng trong đợt này.

### Những điểm cần chỉnh so với tài liệu tham khảo

- Kết nối hiện chưa hỗ trợ Code Interpreter hoặc Files upload API. Không thiết kế luồng chính chờ AI tạo một file PPTX để tải về; gửi nội dung/ảnh hoặc tệp dạng inline được model chấp nhận, nhận JSON và dựng PowerPoint tại máy. Trường `background` cũng chưa được hỗ trợ; app vẫn có thể xử lý stream trong worker, không khóa giao diện. [Giới hạn hiện tại](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations).
- Prompt nền dùng `instructions` hoặc thông điệp developer theo yêu cầu của kết nối này. Không gửi thông điệp `role: system` bị từ chối. Prompt và `source_refs` hỗ trợ kiểm tra nhưng không chứng minh bản dịch đúng; cần validator độc lập và thầy cô xem lại.
- Bố cục tiếng Anh do renderer quyết định cuối cùng. AI có thể đề xuất; app phải tự kiểm tra vị trí, khoảng trống, cỡ chữ và đối tượng nguồn trước khi đặt chữ.
- Không nhất thiết gửi cả PPTX, PDF và manifest cho mọi lượt. Giữ PPTX gốc tại máy; ưu tiên chữ/manifest và các ảnh slide cần đối chiếu. PPTX/DOCX được xử lý như nguồn chữ, còn PDF có thể đưa cả chữ và ảnh trang vào ngữ cảnh model. Chia bài để tránh gửi lại toàn bộ ảnh nhiều lần. [Cách xử lý file](https://developers.openai.com/api/docs/guides/file-inputs).
- Free, hết hạn gói hoặc thiếu quyền không được xem là có thể tự chuyển đổi hoàn toàn như Plus. Nếu kết nối không cấp quyền xử lý, báo rõ và cho chọn gửi/nhận thủ công hoặc ngoại tuyến; không tự chạy lại bằng tài khoản khác.

## 2. Tận dụng phần đã có

| Phần hiện có | Cách dùng trong kiến trúc mới |
|---|---|
| `app/source_deck.py` | Sửa bản sao gói OOXML, kiểm tra hash nguồn, giữ các phần không cần thay đổi. |
| `app/source_support.py` | Kiểm tra vùng trống; thêm trang hỗ trợ khi slide kín hoặc có đối tượng/hiệu ứng khó xử lý. |
| `app/powerpoint_review.py` | Render và so sánh slide bằng Microsoft PowerPoint thật. |
| `app/presentation_policy.py`, `app/level_conversion.py` | Dùng chung chính sách level/bố cục cho AI, xuất slide và trợ giảng. |
| `app/lesson_templates.py`, `app/lesson_design.py` | Dựng bài mới theo mẫu; bản xem trước và xuất file phải dùng cùng renderer. |
| `app/chatgpt_handoff.py` | Giữ nhận PPTX thủ công cũ; bổ sung gói nguồn và nhận JSON có kiểm tra. |
| `app/browser_accounts.py`, `app/browser_ai_ui.py` | Tách hồ sơ đăng nhập web cũ khỏi tài khoản OAuth mới; giữ giao diện quản lý đăng nhập ngắn. |
| `app/browser_automation.py`, `app/browser_capabilities.py` | Rút khỏi luồng chuyển đổi mặc định sau khi provider chính thức đạt kiểm thử. |

Đây là nền tảng để nâng cấp, chưa phải bằng chứng giữ được mọi animation, trigger hoặc font. Cần thử các tệp thật và trình chiếu thật. Không cần viết lại toàn bộ renderer hoặc chuyển toàn bộ thao tác sửa file sang COM; dùng COM trước hết để render/kiểm tra.

## 3. Cài đặt → Browser AI

Trước khi kết nối, có một nút **Tiếp tục với ChatGPT**. Windows mở Edge với hồ sơ riêng của BiliClass, tự đóng khi xong/hủy; chuyển đổi chạy ngầm không mở browser; thầy cô tự đăng nhập và đồng ý cho BiliClass dùng hạn mức gói. App tự nhận callback và lưu kết nối thành công, không có bước Lưu riêng.

Sau kết nối, hiện tài khoản, trạng thái quyền xử lý và các thao tác **Đổi/thêm tài khoản**, **Ngắt kết nối**, **Xem hạn mức**. Cho phép lưu nhiều tài khoản nếu cần, nhưng chỉ một tài khoản được chọn cho mỗi yêu cầu. Hiển thị thông báo dùng hạn mức gói một lần sau lần cấp quyền đầu tiên. [Hướng dẫn giao diện](https://developers.openai.com/siwc/ui-ux-guidelines).

Không đặt prompt, template, level hoặc tiến trình chuyển đổi trong tab này. Không thêm tab cài đặt mới và giữ nguyên Chung, Song ngữ, Giọng đọc, Mascot.

Về kỹ thuật, dùng OAuth PKCE, callback loopback, kiểm tra danh tính và quyền trước khi kích hoạt tài khoản. Token lưu qua kho bảo vệ của Windows, ngoài thư viện bài, log, gói xuất và Git; refresh tuần tự cho từng tài khoản, cập nhật nguyên tử. Không lấy cookie từ hồ sơ Edge cũ để tạo kết nối mới. [Đăng nhập](https://developers.openai.com/siwc/token-sharing-open-source/sign-in), [tài khoản và phiên](https://developers.openai.com/siwc/token-sharing-open-source/profiles-and-sessions).

## 4. Một luồng tạo bài ngắn

```text
Nhập tài liệu
  → chọn L0–L4 + kiểu sắp xếp + giữ PowerPoint / theo mẫu
  → Chuyển đổi
  → Xem bản trình chiếu, kiểm tra chỗ cần chú ý
  → Xác nhận cả bài → Dùng để dạy
```

Tên bài được gợi ý từ tệp; môn/khối chỉ yêu cầu khi chưa đủ thông tin để định hướng. Mặc định L2, bố cục Tự động, PPTX chọn giữ bài gốc. Với tài liệu khác, chọn mẫu BiliClass. Khi chọn mẫu, hiện ảnh slide lớn có nội dung thực hoặc ví dụ rõ ràng, có thể lật qua các loại slide trước khi chuyển đổi.

Model mặc định **Tự động**, lấy danh sách khả dụng của tài khoản và chọn theo khả năng đã kiểm thử. Không hard-code tên hoặc suy ra chất lượng chỉ từ tên/order của model. Chọn model thủ công và yêu cầu thêm nằm trong **Tùy chọn thêm** ở màn tạo bài. [Danh sách model và xử lý kết quả](https://developers.openai.com/siwc/token-sharing-open-source/models-and-inference).

App hiển thị các bước Đọc nguồn → Xử lý song ngữ → Tạo slide → Xem trước, cùng nút Dừng/Tiếp tục khi phù hợp. Không yêu cầu thầy cô tự viết prompt, upload lại hoặc tải kết quả trong luồng kết nối chính thức.

## 5. Xử lý theo loại đầu vào

| Đầu vào | Xử lý mặc định |
|---|---|
| PPTX tiếng Việt | Tạo phần Anh theo level; giữ hình/đối tượng và thêm hỗ trợ vào bản sao. |
| PPTX đã Việt–Anh | Nhận diện các cặp là bản nháp cần xác nhận; giữ cặp thầy cô đã duyệt, bổ sung phần thiếu. Không tự coi hai khối chữ là bản dịch tương đương. |
| PPTX tiếng Anh | Giữ Anh nguồn, bổ sung hỗ trợ Việt theo lựa chọn; không ép hạ lượng Anh chỉ vì level thấp. |
| PPTX trộn ngôn ngữ | Phân loại từng khối, xác định hướng dịch, đánh dấu phần chưa rõ. |
| PPTX chứa ảnh trang sách | Giữ ảnh nếu chọn giữ bài; đọc chữ/ảnh để thêm hỗ trợ. Nếu muốn chia thành slide mới thì chọn theo mẫu. |
| DOCX/TXT/PDF có chữ | Nhận thứ tự, tiêu đề, bảng và nguồn hình; tạo nội dung bài theo mẫu. |
| Ảnh/PDF scan | Đọc ảnh/OCR, giữ liên kết vùng ảnh; chữ, công thức hoặc bảng không rõ phải được xác nhận, không đoán. |
| PPT/DOC cũ hoặc file khác | Kiểm tra có bộ chuyển đổi phù hợp; báo đúng định dạng chưa hỗ trợ. Không quảng bá hỗ trợ mọi loại tệp. |

Nhận diện ngôn ngữ/môn chỉ là gợi ý. Nguồn thiếu, mờ hoặc mâu thuẫn được báo ngay khi ảnh hưởng đến bài; không mở thêm màn cấu hình nếu dữ liệu đã rõ.

## 6. Luồng giữ PowerPoint gốc

1. Lưu bản nguồn không thay đổi và hash; đọc thứ tự slide, shape, bảng, ghi chú, công thức và liên kết media.
2. Tạo `SlideManifest` với định danh ổn định: hash nguồn, ID/part slide, ID shape, đường dẫn nhóm hoặc tọa độ ô bảng, hash chữ nguồn. Không dùng riêng số thứ tự đoạn vì thêm một đối tượng có thể làm lệch toàn bộ ánh xạ.
3. Render ảnh các slide cần đối chiếu. Có PowerPoint thì dùng render native; không có thì vẫn đọc chữ nhưng phải báo thiếu kiểm tra trực quan. Không hứa ảnh xem trước/điều khiển slideshow native hoạt động trên máy thiếu PowerPoint.
4. Gửi chính sách level, bố cục, nguồn và thuật ngữ phù hợp; nhận `BilingualPatch` gồm nội dung VI/EN, hỗ trợ theo level, ghi chú lời đọc, `source_refs` và vấn đề cần xem lại.
5. Kiểm tra schema, ID/hash nguồn, số liệu/công thức, phần thiếu và cấu hình yêu cầu. Chỉ nhận dữ liệu; không thực thi code, lệnh shell hoặc thao tác tệp tùy ý AI trả về. Kết quả sai schema/thiếu nguồn không được ghép âm thầm.
6. Dựng PPTX nháp bằng renderer hiện có. Đủ chỗ thì thêm hỗ trợ; thiếu chỗ thì thêm slide hỗ trợ ngay sau slide tương ứng. Không tự che ảnh hoặc co toàn bộ chữ xuống cỡ khó đọc để ép vừa.
7. Render bản nháp, so sánh với nguồn và kiểm tra tràn chữ. Thầy cô có thể sửa phần song ngữ rồi render lại mà không phải xin AI tạo lại cả file.
8. Xác nhận toàn bài gắn với đúng revision/hash của PPTX. Sau đó xuất PPTX + gói bài, tạo/cache lời đọc và ánh xạ mascot theo slide thật. Sửa nội dung sau xác nhận sẽ làm mất trạng thái duyệt của phần thay đổi.

AI không thay đổi master, theme, media hoặc animation. Renderer giữ các phần nguồn không cần sửa; khi thêm trang hoặc đổi chữ phải kiểm tra lại các tham chiếu/hiệu ứng liên quan. PNG không kiểm chứng được animation; kiểm thử hiệu ứng cần trình chiếu thật.

## 7. Level và bố cục là hai lựa chọn độc lập

| Level | Chính sách nội dung |
|---|---|
| L0 | Việt là chính; thêm thuật ngữ Anh trọng tâm có trong nguồn. |
| L1 | Thêm thuật ngữ và câu chỉ dẫn lớp học ngắn, không thêm dữ kiện bài học mới. |
| L2 | Thêm câu Anh dễ cho ý/khái niệm/câu hỏi trọng tâm, giữ giải thích Việt. |
| L3 | Việt–Anh ở các phần chính, có thể xen kẽ hỗ trợ; giữ điều kiện và thuật ngữ nhất quán. |
| L4 | Anh là chính trong bản dạy; Việt nằm trong Rescue/ghi chú và bản nguồn được giữ trong dự án. |

Dùng chính sách chung với luồng hiện có, không đưa level 5 của mô-đun nền ra màn chuyển đổi L0–L4. L4 cần xem trước rõ phần Việt chuyển sang hỗ trợ; không âm thầm xóa Việt hoặc bản gốc.

Bố cục gồm Tự động, Từ khóa, Trong ngoặc, Cặp dòng, Hai cột, Anh chính + Việt hỗ trợ. Khi giữ thiết kế gốc, lựa chọn bố cục là ưu tiên có ràng buộc: nếu không vừa vùng trống, app chuyển sang trang hỗ trợ và thông báo. Không cam kết mọi bố cục đều giữ đúng vị trí từng đối tượng.

## 8. Luồng tạo bài theo mẫu

Chuẩn hóa nguồn thành các khối có liên kết trang/slide/vùng ảnh → AI tạo `BilingualLesson` JSON → kiểm tra nguồn/schema → renderer mẫu tạo bản nháp → xem/duyệt → PPTX và gói bài.

Tận dụng ba nhóm mẫu đã có: Chuẩn lớp học, Trực quan, Luyện tập & tương tác. Nâng chất lượng bản xem trước và việc đặt nội dung thật trước khi thêm nhiều mẫu mới. Các loại slide như khái niệm, hình, bảng/công thức, ví dụ, luyện tập, tổng kết chỉ được tạo khi nguồn có nội dung tương ứng.

Không bắt AI vẽ lại ảnh/biểu đồ bằng suy đoán. Hình xuất từ nguồn phải có liên kết tới nguồn và được thầy cô kiểm tra. Nếu nguồn chưa đủ tạo một phần bài, báo thiếu hoặc bỏ phần đó để thầy cô quyết định; không chèn một lời giải hay đáp án tự nhận là có trong tài liệu.

## 9. Prompt, kiểm tra và kho kiến thức

Prompt tự dựng từ nguồn, môn/khối, chính sách level/bố cục, chế độ giữ thiết kế/mẫu, schema và thuật ngữ thầy cô đã duyệt. Yêu cầu thêm không được làm mất ràng buộc giữ nguồn, giữ số liệu/công thức hoặc yêu cầu liên kết nguồn.

Nguồn bài của thầy cô là căn cứ nội dung chính. Thuật ngữ ưu tiên dữ liệu thầy cô duyệt → nền đã có → online khi cần và được cho phép. Nguồn tra cứu bổ sung phải được ghi riêng; không tự trộn một sự kiện trên mạng vào bài rồi gắn nhãn như thuộc nguồn thầy cô.

Mỗi khối mới có `source_refs`, loại biến đổi và vấn đề cần kiểm tra. Thiếu nguồn thì `SOURCE_MISSING`; không đưa khối đó vào lời đọc/quiz như thông tin đã xác nhận. Giáo viên xác nhận kiến thức và ý nghĩa, không dựa vào `review_required: false` do AI tự khai.

Màn xem trước ưu tiên chỗ mới/sửa, đoạn diễn giải và phần thiếu nguồn. Dịch trực tiếp vẫn là bản nháp, không đánh dấu xanh như đã được chứng minh đúng. Chốt cả bài một lần; chỉ mở chỉnh sửa chi tiết ở vị trí cần xử lý. Voice/quiz chưa sẵn sàng không chặn một bản PowerPoint đã được duyệt để dạy.

Mascot, Rescue và quiz chỉ sử dụng nội dung đã xác nhận của đúng revision bài. Thông báo kỹ thuật hoặc nghi vấn nguồn không được đọc thành lời bài giảng. Kho chỉ học từ phần thầy cô duyệt, có nguồn và phiên bản; không tự coi đáp án AI là kiến thức đã duyệt.

## 10. Tác vụ, hạn mức và dự phòng

Tách provider chính thức, gửi/nhận thủ công và ngoại tuyến. Mỗi yêu cầu ghim tài khoản/model/cấu hình đã chọn. Model catalog được cập nhật khi đổi tài khoản; thiếu quyền, hết quota hoặc lỗi model phải được báo, không chuyển billing hoặc tài khoản âm thầm.

Lưu tiến trình tại máy theo hash nguồn, cấu hình, phiên bản prompt/schema, glossary và model. Chia thành nhóm slide vừa khả năng model, cache phần hoàn tất để không dịch lại khi tiếp tục. Chỉ áp dụng kết quả sau sự kiện hoàn tất, không coi chữ đã stream một phần là bài đầy đủ. Lỗi trong hoặc sau stream phải giữ trạng thái riêng để tránh gửi trùng.

Khi mất mạng/hết quota, giữ bản nháp và cho thầy cô xem hạn mức hoặc chọn luồng khác. Không suy ra thời gian quota reset từ riêng mã lỗi. Ngoại tuyến có thể dùng bản dịch đã duyệt và model đã cài, nhưng không được coi có chất lượng/khả năng tương đương kết nối ChatGPT. [Xử lý lỗi chính thức](https://developers.openai.com/siwc/token-sharing-open-source/errors-and-recovery).

Luồng thủ công mới có thể nhận JSON cùng schema; vẫn giữ nhận PPTX cho bài đã tạo bằng luồng cũ. Không tự chuyển các tác vụ web đang chờ sang provider mới rồi gửi nguồn lần nữa; thầy cô chọn tiếp tục cũ hoặc tạo yêu cầu mới.

## 11. Thứ tự triển khai và điều kiện nghiệm thu

| Mốc | Công việc | Điều kiện qua mốc |
|---|---|---|
| 0. Kiểm chứng kết nối | OAuth trên tài khoản thật; catalog; một yêu cầu chữ; ảnh/PDF inline nhỏ; JSON có schema. Kiểm tra điều kiện phân phối ứng dụng. | Nhận kết quả hoàn tất bằng hạn mức ChatGPT, không key/billing riêng; biết model/input nào dùng được. |
| 1. Đăng nhập đơn giản | Provider, kho token, refresh/revoke, tab Browser AI ngắn, lỗi quyền/quota. | Đóng/mở app vẫn dùng kết nối; đăng xuất đúng tài khoản; token không lọt vào Git/log/gói bài. |
| 2. PPTX Việt giữ gốc | Manifest → patch JSON → renderer → so sánh → duyệt cả bài → voice/mascot. | Một bài thật đi hết luồng từ nút Chuyển đổi đến trình chiếu; gốc không thay đổi, chữ không tràn. |
| 3. PPTX đa dạng | Cặp song ngữ, Anh, trộn ngôn ngữ, nhóm/bảng/công thức, media/hiệu ứng; đủ L0–L4/bố cục. | Các trường hợp đã có bộ tệp kiểm thử và kết quả render/trình chiếu được kiểm tra. |
| 4. Nguồn khác và mẫu | Word/PDF/ảnh, đọc nguồn và báo phần mờ; JSON bài mới; bản xem trước mẫu rõ. | Các nhóm đầu vào đã công bố đều có bài thử; ảnh/scan lỗi không bị biến thành kiến thức đoán. |
| 5. Chạy thử và phát hành | Hai giáo viên test, sửa các lỗi còn lại; đóng gói tại mốc ổn định. | Tests liên quan + Qt smoke + Office thật đạt; ghi rõ commit/version và phạm vi đã kiểm chứng. |

Ưu tiên mốc 0–2 để đạt hiệu quả với PowerPoint đang có trước. Không mở rộng kho kiến thức mọi môn hoặc làm thêm nhiều template khi luồng này chưa dùng tốt.

Mốc 0 cần kiểm tra quyền thực tế trước khi hứa hoạt động cho mọi máy. Repository hiện chưa có giấy phép nguồn mở ở cấp dự án; repo public không tự đồng nghĩa đã có giấy phép nguồn mở. Không tự đổi giấy phép hoặc quyền hiển thị kho; xử lý điều kiện phân phối riêng khi cần.

Bộ thử ban đầu nên có PPTX ngắn/dài, slide kín, bản đã Việt–Anh, bảng/công thức, nhóm/SmartArt/biểu đồ, video/audio/animation và nguồn scan xấu; lấy bài thật của hai giáo viên làm tiêu chí sử dụng. Kiểm tra hash nguồn, phần media không đổi, ID/slide map, revision phê duyệt, thiếu nguồn, hủy/tiếp tục và hết quyền giữa lượt. Chỉ công bố phạm vi đã thử; không hứa mọi môn/mọi định dạng/mọi hiệu ứng đều chính xác.

Trong khi phát triển chạy bản nguồn để test nhanh. Chỉ build `.exe` một lần sau mốc đã kiểm chứng; code/tài liệu commit và push riêng, không đưa giáo án cá nhân, token, cache, model hoặc executable vào Git.
