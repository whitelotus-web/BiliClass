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
    if not state.get("running") and state.get("phase") == "error":
        message = ERROR_COPY.get(state.get("errorCode"),
                                 "Chuyển đổi đang tạm dừng do kết nối gián đoạn. Bài đang làm đã được giữ để tiếp tục.")
        label = "Cần xác minh tài khoản" if state.get("needsLogin") else "Chuyển đổi tạm dừng"
    elif state.get("phase") == "completed":
        label, message = STAGE_COPY["completed"]
    elif not state.get("running"):
        label, message = "Sẵn sàng chuyển đổi", "Bài giảng đã được chuẩn bị theo cấu hình đã chọn."
    return {**state, "displayMessage": message, "displayStage": label}
