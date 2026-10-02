"""30 authored bilingual pairs: 60 direction-specific cases, no single lesson focus.

Targets are reviewer references, not exact-match translation scores.
"""

PAIRS = [
    ("classroom", "Các em hãy giải thích câu trả lời của mình.", "Please explain your answer."),
    ("classroom", "Thảo luận theo nhóm trong 3 phút.", "Discuss in groups for 3 minutes."),
    (
        "classroom",
        "So sánh hai cách giải và nêu điểm khác nhau.",
        "Compare the two solutions and describe their differences.",
    ),
    ("classroom", "Em có thể nêu một ví dụ khác không?", "Can you give another example?"),
    ("classroom", "Đọc đoạn văn rồi xác định ý chính.", "Read the paragraph and identify the main idea."),
    ("mathematics", "Giải phương trình 2x + 3 = 7.", "Solve the equation 2x + 3 = 7."),
    ("mathematics", "Tam giác có 3 cạnh.", "A triangle has 3 sides."),
    (
        "mathematics",
        "Tính giá trị của biểu thức khi x = 5.",
        "Calculate the value of the expression when x = 5.",
    ),
    (
        "mathematics",
        "Đạo hàm mô tả tốc độ biến thiên của hàm số.",
        "The derivative describes the rate of change of a function.",
    ),
    (
        "mathematics",
        "Xác suất của một sự kiện nằm trong khoảng từ 0 đến 1.",
        "The probability of an event lies between 0 and 1.",
    ),
    ("science", "Điện trở được đo bằng đơn vị ohm.", "Resistance is measured in ohms."),
    ("science", "Ghi lại nhiệt độ sau mỗi 2 phút.", "Record the temperature every 2 minutes."),
    (
        "science",
        "Bảo toàn số nguyên tử khi cân bằng phương trình hóa học.",
        "Conserve the number of atoms when balancing a chemical equation.",
    ),
    ("science", "Công thức hóa học của nước là H2O.", "The chemical formula of water is H2O."),
    ("science", "Phân biệt khối lượng và trọng lượng.", "Distinguish between mass and weight."),
    ("biology", "Tế bào là đơn vị cơ bản của sự sống.", "The cell is the basic unit of life."),
    (
        "biology",
        "Quan sát hình và xác định cấu trúc của tế bào.",
        "Observe the image and identify the structures of the cell.",
    ),
    (
        "biology",
        "So sánh sự sinh trưởng và phát triển của sinh vật.",
        "Compare growth and development in organisms.",
    ),
    ("biology", "Cây sử dụng ánh sáng trong quá trình quang hợp.", "Plants use light during photosynthesis."),
    ("biology", "Giải thích vai trò của DNA trong di truyền.", "Explain the role of DNA in inheritance."),
    (
        "humanities",
        "Phân tích nguyên nhân và kết quả của sự kiện.",
        "Analyze the causes and consequences of the event.",
    ),
    (
        "humanities",
        "Xác định thông điệp của tác giả trong đoạn văn.",
        "Identify the author's message in the passage.",
    ),
    (
        "humanities",
        "Sử dụng bằng chứng từ tài liệu để bảo vệ quan điểm.",
        "Use evidence from the document to support your argument.",
    ),
    (
        "humanities",
        "So sánh dữ liệu dân số của năm 2020 và 2025.",
        "Compare the population data for 2020 and 2025.",
    ),
    (
        "humanities",
        "Chú giải giúp người đọc hiểu các ký hiệu trên bản đồ.",
        "The legend helps readers understand the symbols on a map.",
    ),
    (
        "technology",
        "Thuật toán là một dãy các bước để giải quyết vấn đề.",
        "An algorithm is a sequence of steps for solving a problem.",
    ),
    ("technology", "Không chia sẻ mật khẩu với người khác.", "Do not share your password with others."),
    (
        "technology",
        "Giá trị của biến thay đổi sau mỗi lần lặp.",
        "The value of the variable changes after each iteration.",
    ),
    (
        "terminology",
        "Nghĩa của từ phụ thuộc vào ngữ cảnh sử dụng.",
        "The meaning of a word depends on its context.",
    ),
    (
        "long_sentence",
        "Khi so sánh hai biểu đồ, hãy chú ý đến đơn vị, khoảng thời gian và nguồn dữ liệu trước khi đưa ra kết luận.",
        "When comparing two charts, pay attention to units, time periods, and data sources before drawing a conclusion.",
    ),
]
