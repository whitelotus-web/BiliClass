"""Deterministic protection for numbers, explicit formula/code spans and curated terms."""

import re
from collections import Counter

PROTECTED = re.compile(
    r"`[^`\n]+`|\$[^$\n]+\$|\\\([^\n]*?\\\)|"
    r"https?://[^\s]+|"
    r"(?<!\w)(?:[A-Z][a-z]?[0-9⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉]*){2,}(?!\w)|"
    r"(?:[A-Za-zα-ωΑ-Ω][\w²³⁴⁵⁶⁷⁸⁹^]*|\d+(?:[.,]\d+)*)\s*[=<>≤≥≈]\s*[A-Za-zα-ωΑ-Ω0-9_().²³⁴⁵⁶⁷⁸⁹]+(?:\s*[+\-*/×÷^]\s*[A-Za-zα-ωΑ-Ω0-9_().²³⁴⁵⁶⁷⁸⁹]+)*|"
    r"\d+(?:[.,:/–-]\d+)*(?:\s*(?:%|°[CF]|kg|km|cm|mm|m/s|m²|m³|mol|Hz|kWh))?"
)
NUMBERS = re.compile(r"\d+(?:[.,:/–-]\d+)*")


def protected_parts(text, terms=(), source_language="vi"):
    source, target = ("vi", "en") if source_language == "vi" else ("en", "vi")
    positions = [(m.start(), m.end(), m.group(), "symbol") for m in PROTECTED.finditer(text)]
    mapping = {}
    for term in terms:
        if term.get("locked") and term.get(source) and term.get(target):
            mapping.setdefault(term[source], set()).add(term[target])
    # Longest term first; overlapping terms and ambiguous reverse senses are not guessed.
    for word, options in sorted(mapping.items(), key=lambda pair: -len(pair[0])):
        if len(options) != 1:
            continue
        for match in re.finditer(r"(?<!\w)" + re.escape(word) + r"(?!\w)", text):
            if not any(match.start() < end and start < match.end() for start, end, *_ in positions):
                positions.append((match.start(), match.end(), next(iter(options)), "term"))
    positions.sort()
    chunks, cursor = [], 0
    for start, end, replacement, kind in positions:
        if cursor < start:
            chunks.append({"text": text[cursor:start], "protected": False})
        chunks.append({"text": replacement, "original": text[start:end], "protected": True, "kind": kind})
        cursor = end
    if cursor < len(text):
        chunks.append({"text": text[cursor:], "protected": False})
    return chunks


def review_warnings(vi, en):
    if not vi.strip() or not en.strip():
        return []
    issues = []
    if Counter(NUMBERS.findall(vi)) != Counter(NUMBERS.findall(en)):
        issues.append("Số liệu hai ngôn ngữ khác nhau. Kiểm tra số, ngày, tỷ lệ và cách viết thập phân.")
    for marker in re.findall(r"`[^`\n]+`|\$[^$\n]+\$|\\\([^\n]*?\\\)", vi):
        if marker not in en:
            issues.append("Biểu thức hoặc đoạn mã được đánh dấu chưa khớp: " + marker[:100])
    return issues
