import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Flow {
    id: strip
    property var state: ({})
    spacing: 10
    Repeater {
        model: [
            {label: strip.state.saved ? "Đã lưu bài" : "Chưa lưu", ok: !!strip.state.saved},
            {label: strip.state.content_ready ? "Đã duyệt nội dung" : "Cần kiểm tra nội dung", ok: !!strip.state.content_ready},
            {label: strip.state.audio_label || "Chưa tạo giọng", ok: !!strip.state.audio_ready},
            {label: strip.state.prepared ? "Đã chốt để dạy" : "Chưa chốt để dạy", ok: !!strip.state.prepared}
        ]
        delegate: Label {
            required property var modelData
            text: (modelData.ok ? "✓ " : "○ ") + modelData.label
            textFormat: Text.PlainText
            font.pixelSize: 11
            color: modelData.ok ? "#19745c" : "#667997"
            Accessible.name: text
        }
    }
}
