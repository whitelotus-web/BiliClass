.pragma library

function forSubject(subject) {
    const value = subject.toLowerCase()
    if (/toán|toan|math/.test(value)) return {symbol: "π", color: "#255cb3", paper: "#edf3ff"}
    if (/vật lý|vat ly|physics/.test(value)) return {symbol: "E", color: "#176eaa", paper: "#edf8ff"}
    if (/hóa|hoá|hoa hoc|chem/.test(value)) return {symbol: "H₂O", color: "#8252a2", paper: "#f8efff"}
    if (/sinh|biology|khoa học|science/.test(value)) return {symbol: "DNA", color: "#248564", paper: "#edfaf3"}
    if (/tin|computer|công nghệ|technology/.test(value)) return {symbol: "</>", color: "#236781", paper: "#eaf7fb"}
    if (/anh|english|ngoại ngữ|language/.test(value)) return {symbol: "EN", color: "#ad5b32", paper: "#fff3e8"}
    if (/văn|van|literature|tiếng việt/.test(value)) return {symbol: "Aa", color: "#91546f", paper: "#fff0f6"}
    if (/sử|history/.test(value)) return {symbol: "SỬ", color: "#97673c", paper: "#fff7e9"}
    if (/địa|geography/.test(value)) return {symbol: "GEO", color: "#267e89", paper: "#edfafb"}
    if (/nhạc|music/.test(value)) return {symbol: "♫", color: "#8c4eaa", paper: "#f8f0ff"}
    if (/mỹ thuật|mĩ thuật|art/.test(value)) return {symbol: "✦", color: "#ad5575", paper: "#fff1f5"}
    if (/thể|sport|physical/.test(value)) return {symbol: "PE", color: "#a16c22", paper: "#fff7e5"}
    return {symbol: "B", color: "#2269b6", paper: "#edf5ff"}
}
