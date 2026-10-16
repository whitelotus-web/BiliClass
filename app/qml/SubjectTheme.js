.pragma library

function forSubject(subject) {
    const value = String(subject).toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/đ/g, "d")
    function theme(id, label, color, paper, symbol) { return {id: id, label: label, color: color, paper: paper, symbol: symbol} }
    if (/toan|math/.test(value)) return theme("math", "Thước hình học", "#255cb3", "#edf3ff", "π")
    if (/vat li|vat ly|physics/.test(value)) return theme("physics", "Mô hình nguyên tử", "#176eaa", "#edf8ff", "E")
    if (/\bhoa hoc\b|chem/.test(value)) return theme("chemistry", "Bình thí nghiệm", "#8252a2", "#f8efff", "H₂O")
    if (/sinh|biology/.test(value)) return theme("biology", "Chiếc lá", "#248564", "#edfaf3", "DNA")
    if (/dia phuong/.test(value)) return theme("local", "Dấu địa điểm", "#b35d44", "#fff2e9", "⌖")
    if (/tin hoc|computer|cong nghe|technology/.test(value)) return theme("technology", "Máy tính", "#236781", "#eaf7fb", "</>")
    if (/tieng anh|english|ngoai ngu|language|dan toc/.test(value)) return theme("language", "Thẻ hội thoại", "#ad5b32", "#fff3e8", "Aa")
    if (/ngu van|literature|tieng viet/.test(value)) return theme("literature", "Quyển sách", "#91546f", "#fff0f6", "Aa")
    if (/lich su|history/.test(value) && /dia li|dia ly/.test(value)) return theme("geography", "Địa cầu và lịch sử", "#267e89", "#edfafb", "GEO")
    if (/lich su|history/.test(value)) return theme("history", "Cuộn tư liệu", "#97673c", "#fff7e9", "SỬ")
    if (/dia li|dia ly|geography/.test(value)) return theme("geography", "Quả địa cầu", "#267e89", "#edfafb", "GEO")
    if (/am nhac|music/.test(value)) return theme("music", "Nốt nhạc", "#8c4eaa", "#f8f0ff", "♫")
    if (/my thuat|mi thuat|nghe thuat|art/.test(value)) return theme("art", "Bảng màu", "#ad5575", "#fff1f5", "✦")
    if (/quoc phong/.test(value)) return theme("defence", "Chiếc khiên", "#557345", "#f2f7e9", "★")
    if (/the chat|sport|physical/.test(value)) return theme("sport", "Quả bóng", "#a16c22", "#fff7e5", "PE")
    if (/cong dan|dao duc|phap luat|kinh te/.test(value)) return theme("civics", "Cán cân", "#6d61a0", "#f3f0ff", "⚖")
    if (/trai nghiem|huong nghiep/.test(value)) return theme("experience", "La bàn khám phá", "#bd672d", "#fff5e8", "⌖")
    if (/khoa hoc|science|tu nhien/.test(value)) return theme("science", "Kính lúp khám phá", "#248564", "#edfaf3", "S")
    return theme("general", "Quyển sách", "#2269b6", "#edf5ff", "B")
}
