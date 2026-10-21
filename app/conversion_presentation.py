"""Teacher-facing conversion copy; transport diagnostics stay in job records."""

STAGE_COPY = {
    "translate": ("Biên soạn bài giảng", "Đang hoàn thiện từng phần nội dung song ngữ."),
    "assemble": ("Hoàn thiện bài giảng", "Đang hoàn thiện bản PowerPoint song ngữ."),
    "session": ("Chuẩn bị bài giảng", "Đang chuẩn bị bài giảng theo cấu hình đã chọn."),
    "model": ("Chuẩn bị nội dung", "Đang chuẩn bị xử lý nội dung bài học."),
    "upload": ("Xử lý tài liệu", "Đang xử lý tài liệu gốc và yêu cầu của thầy cô."),
    "waiting": ("Biên soạn bài giảng song ngữ", "Đang biên soạn nội dung và bố cục bài giảng song ngữ."),
    "download": ("Nhận tệp bài giảng", "Đang nhận bản PowerPoint song ngữ và chuẩn bị kiểm tra."),
    "quality": ("Kiểm tra bài giảng", "Đang kiểm tra nội dung, bố cục và lời đọc của từng slide."),
    "refine": ("Điều chỉnh bài giảng", "Đang điều chỉnh các phần cần hoàn thiện."),
    "refine_wait": ("Hoàn thiện nội dung", "Đang hoàn thiện nội dung và cách trình bày."),
    "refine_download": ("Cập nhật bài giảng", "Đang cập nhật bản bài giảng đã điều chỉnh."),
    "refine_quality": ("Rà soát bài giảng", "Đang rà soát nội dung và bố cục sau điều chỉnh."),
    "import": ("Chuẩn bị trình chiếu", "Đang chuẩn bị bài giảng để trình chiếu và sử dụng trợ giảng."),
    "audio": ("Chuẩn bị giọng đọc", "Đang chuẩn bị giọng đọc cho bài giảng."),
    "save": ("Lưu bài giảng", "Đang lưu bài giảng vào thư viện của thầy cô."),
    "completed": ("Đã lưu bài giảng", "Bài giảng đã được lưu. Thầy cô có thể xem và kiểm tra trước khi dạy."),
}

ERROR_COPY = {
    'source_document': 'Chưa đọc được một định dạng trong tài liệu nguồn. API key vẫn được giữ; cập nhật tool rồi tiếp tục bài.',
    'api_conversion': 'Chưa hoàn thiện được PowerPoint. Phần dịch đã xong được giữ lại; đây không phải thông báo thiếu API key.',
    'api_layout': 'Một vùng chữ chưa vừa trang chiếu. Cần rút ngắn tên bài hoặc tách ý nguồn; phần đã dịch được giữ lại.',
    'api_busy': 'Bài đang chạy trong cửa sổ BiliClass khác. Mở cửa sổ đó để theo dõi; không cần gửi lại.',
    'api_settings': 'Kiểm tra cấu hình Google Dịch trong Cài đặt. Các phần đã hoàn tất được giữ lại.',
    'api_key': 'API key chưa hợp lệ hoặc dự án chưa bật dịch vụ/thanh toán. Kiểm tra trong Cài đặt → Google Dịch.',
    'api_budget': 'Các key đã đạt giới hạn cục bộ hoặc chưa dùng được. Kiểm tra hạn mức và thanh toán Google Cloud; các phần đã dịch được giữ lại.',
    'api_network': 'Kết nối Google Dịch gián đoạn sau các lần thử lại. Phần đã dịch được giữ để tiếp tục.',
    'api_rate': 'Dịch vụ đang giới hạn tần suất. Phần đã dịch được giữ để tiếp tục sau.',
    'api_quota': 'Hạn mức Google Cloud của dự án chưa cho phép tiếp tục. Kiểm tra trong Cài đặt → Google Dịch.',
    'api_result': 'Một phần bản dịch chưa hợp lệ. Phần đã hoàn tất được giữ lại; chưa đánh dấu bài đã hoàn thiện.',
    'api_request': 'Google Dịch chưa chấp nhận yêu cầu. Kiểm tra cấu hình dự án và API key.',
    'api_resume': 'Bài trước đang dở. Bấm Tiếp tục để dùng lại các phần đã dịch và hoàn thiện bài.',
    "storage": "Ổ đĩa lưu dữ liệu không đủ dung lượng để tiếp tục. Giải phóng dung lượng rồi tiếp tục; bài và các phần đã lưu vẫn được giữ.",
    "conversation": "Không mở lại được phiên xử lý của bài. Phần đã hoàn tất được giữ nguyên; mở tài khoản để kiểm tra trước khi tiếp tục.",
    "file_transfer": "Chưa nhận được tệp PowerPoint do đường tải bị gián đoạn. Bài gốc và cấu hình đã được giữ; bài chưa hoàn tất.",
    "download": "Chưa lưu được tệp bài giảng đã tạo. Kết quả và bài đang làm được giữ để tiếp tục nhận tệp.",
    "translation_result": "Một phần nội dung chưa có kết quả hợp lệ. Các phần đã xong được giữ để tiếp tục.",
    "timeout": "Chưa nhận được kết quả sau khoảng theo dõi. Bài đang làm đã được giữ; bấm Tiếp tục để kiểm tra kết quả và tiếp tục xử lý.",
    "network": "Kết nối xử lý gián đoạn sau các lần khôi phục. Tác vụ đã tạm dừng và giữ bài; cần tiếp tục hoặc mở tài khoản để kiểm tra kết quả.",
    "model": "Chưa xác nhận được lựa chọn model và suy luận phù hợp. Mở tài khoản trong Browser AI để kiểm tra; bài chưa được gửi bằng cấu hình thấp hơn.",
    "login": "Kết nối tài khoản đã hết hạn. Đăng nhập lại để tiếp tục; tài liệu đã được giữ.",
    "verification": "Tài khoản cần xác minh. Mở tài khoản để hoàn tất xác minh, sau đó BiliClass sẽ tiếp tục.",
    "auth_response": "Chưa xác nhận được kết nối tài khoản. Mở tài khoản để đăng nhập lại.",
    "limit": "Tài khoản đã hết lượt sử dụng. Bài đang làm được giữ để tiếp tục khi có lượt mới.",
    "receipt": "Chuyển đổi đang tạm dừng vì chưa xác nhận được yêu cầu. Bài đang làm đã được giữ để kiểm tra và tiếp tục.",
    "submission": "Chuyển đổi đang tạm dừng. Cần kiểm tra yêu cầu trước khi tiếp tục để tránh tạo bài trùng.",
    "no_file": "Chưa tạo được tệp PowerPoint hoàn chỉnh. Bài đang làm được giữ để kiểm tra và tiếp tục.",
    "upload": "Chưa xử lý được tài liệu đầu vào. Kiểm tra kết nối rồi thử lại; tài liệu đã được giữ.",
    "attachments": "Tài liệu đầu vào đã thiếu hoặc thay đổi. Chọn lại tài liệu trước khi chuyển đổi.",
    "record": "Bản ghi của bài đang làm không còn hợp lệ. Cần kiểm tra trước khi tiếp tục.",
    "result": "Tệp kết quả không còn hợp lệ. Cần nhận lại bài giảng trước khi sử dụng.",
    "cancelled": "Đã dừng chuyển đổi. Các phần đã hoàn tất được giữ lại.",
    "busy": "Tài khoản đang được sử dụng. Đóng cửa sổ tài khoản trước khi tiếp tục chuyển đổi.",
}


def display_state(state):
    """Do not suggest work is running after retries have stopped."""
    label, message = STAGE_COPY.get(state.get("stage"), STAGE_COPY["session"])
    if state.get("running") and state.get("stopping"):
        if state.get('stopRequested'):
            label, message = "Đang dừng chuyển đổi", "Đang dừng bước hiện tại. Các phần đã xử lý được giữ lại để tiếp tục."
        else:
            label, message = "Đang hủy chuyển đổi", "Đang dừng bước hiện tại trước khi xóa bài đang tạo."
    elif state.get("phase") == "discarded":
        label, message = "Đã hủy bài đang tạo", "Chọn tài liệu để bắt đầu một bài giảng mới."
    elif state.get("phase") == "cancelled":
        label, message = "Đã dừng chuyển đổi", ERROR_COPY["cancelled"]
    elif not state.get("running") and state.get("phase") == "error":
        message = ERROR_COPY.get(state.get("errorCode"),
                                 "Chuyển đổi đang tạm dừng do kết nối gián đoạn. Bài đang làm đã được giữ để tiếp tục.")
        label = "Cần xác minh tài khoản" if state.get("needsLogin") else "Chuyển đổi tạm dừng"
        context = state.get('issueContext') or {}
        if context.get('source_slides'):
            message += ' Slide nguồn: ' + ', '.join(map(str, context['source_slides'])) + '.'
        if context.get('excerpt'):
            message += ' Vùng nội dung: “' + context['excerpt'] + '”.'
    elif state.get("phase") == "completed":
        label, message = STAGE_COPY["completed"]
    elif not state.get("running"):
        label, message = "Sẵn sàng chuyển đổi", "Bài giảng đã được chuẩn bị theo cấu hình đã chọn."
    return {**state, "displayMessage": message, "displayStage": label}
