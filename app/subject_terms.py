"""Small school terminology baseline, scoped by subject, never a full syllabus."""
import unicodedata


def subject_key(subject):
    flat = ''.join(c for c in unicodedata.normalize('NFD', subject.casefold().replace('đ', 'd'))
                   if not unicodedata.combining(c))
    flat = ' '.join(flat.split())
    return {'vat li':'vat ly', 'dia li':'dia ly', 'mi thuat':'my thuat', 'hoa':'hoa hoc',
            'sinh':'sinh hoc', 'toan hoc':'toan'}.get(flat, flat)


TERMS = {
    'vat ly': {'quãng đường':'distance traveled', 'độ dịch chuyển':'displacement', 'vận tốc':'velocity',
        'tốc độ':'speed', 'gia tốc':'acceleration', 'khối lượng':'mass', 'động năng':'kinetic energy',
        'thế năng':'potential energy', 'cơ năng':'mechanical energy', 'trọng lực':'gravitational force',
        'lực căng':'tension', 'công suất':'power', 'điện trở':'electrical resistance',
        'cường độ dòng điện':'electric current', 'hiệu điện thế':'potential difference',
        'chu kỳ':'period', 'tần số':'frequency', 'công':'work',
        'định luật i newton':"Newton's first law", 'định luật 1 newton':"Newton's first law",
        'con lắc đơn':'simple pendulum', 'con lắc lò xo':'spring–mass oscillator',
        'dao động tắt dần':'damped oscillation', 'dao động điều hòa':'simple harmonic motion',
        'dao động điều hoà':'simple harmonic motion', 'biên độ':'amplitude'},
    'toan': {'hàm số':'function', 'tập xác định':'domain', 'tập giá trị':'range',
        'phương trình':'equation', 'bất phương trình':'inequality', 'hệ phương trình':'system of equations',
        'đạo hàm':'derivative', 'tích phân':'integral', 'số nguyên':'integer', 'số thực':'real number',
        'số hữu tỉ':'rational number', 'số vô tỉ':'irrational number', 'cấp số cộng':'arithmetic sequence',
        'cấp số nhân':'geometric sequence', 'xác suất':'probability', 'tiếp tuyến':'tangent'},
    'hoa hoc': {'nguyên tử':'atom', 'phân tử':'molecule', 'nguyên tố hóa học':'chemical element',
        'liên kết hóa học':'chemical bond', 'phản ứng hóa học':'chemical reaction',
        'hóa trị':'valence', 'số oxi hóa':'oxidation state', 'nồng độ mol':'molar concentration',
        'dung dịch':'solution', 'dung môi':'solvent', 'chất tan':'solute'},
    'sinh hoc': {'tế bào':'cell', 'màng sinh chất':'plasma membrane', 'nhân tế bào':'cell nucleus',
        'quang hợp':'photosynthesis', 'hô hấp tế bào':'cellular respiration',
        'nhiễm sắc thể':'chromosome', 'nguyên phân':'mitosis', 'giảm phân':'meiosis',
        'hệ sinh thái':'ecosystem', 'quần thể':'population', 'quần xã':'community'},
    'tin hoc': {'cơ sở dữ liệu':'database', 'hệ điều hành':'operating system', 'thuật toán':'algorithm',
        'ngôn ngữ lập trình':'programming language', 'mạng máy tính':'computer network',
        'phần cứng':'hardware', 'phần mềm':'software', 'bộ nhớ':'memory',
        'khóa chính':'primary key', 'khóa ngoại':'foreign key', 'biến':'variable'},
    'lich su': {'cách mạng công nghiệp':'Industrial Revolution', 'cách mạng tư sản':'bourgeois revolution',
        'chiến tranh thế giới':'World War', 'phong trào giải phóng dân tộc':'national liberation movement',
        'chủ nghĩa thực dân':'colonialism', 'chủ nghĩa đế quốc':'imperialism'},
    'dia ly': {'vĩ độ':'latitude', 'kinh độ':'longitude', 'dân số':'population',
        'mật độ dân số':'population density', 'khí hậu':'climate', 'thời tiết':'weather',
        'đô thị hóa':'urbanization', 'biến đổi khí hậu':'climate change'},
    'ngu van': {'nhân vật trữ tình':'lyrical subject', 'người kể chuyện':'narrator',
        'ngôi kể':'narrative perspective', 'biện pháp tu từ':'rhetorical device',
        'ẩn dụ':'metaphor', 'hoán dụ':'metonymy', 'luận điểm':'claim', 'luận cứ':'supporting evidence'},
    'am nhac': {'cao độ':'pitch', 'trường độ':'duration', 'nhịp điệu':'rhythm',
        'giai điệu':'melody', 'hòa âm':'harmony', 'khóa nhạc':'clef'},
    'my thuat': {'phối cảnh':'perspective', 'bố cục':'composition', 'sắc độ':'tone',
        'màu bổ túc':'complementary colors', 'đường nét':'line'},
    'cong nghe': {'bản vẽ kỹ thuật':'technical drawing', 'hình chiếu':'projection',
        'mạch điện':'electrical circuit', 'truyền động':'power transmission', 'gia công':'machining'},
    'giao duc kinh te va phap luat': {'cung cầu':'supply and demand', 'lạm phát':'inflation',
        'thất nghiệp':'unemployment', 'quyền công dân':'civil rights', 'trách nhiệm pháp lý':'legal liability'},
}
