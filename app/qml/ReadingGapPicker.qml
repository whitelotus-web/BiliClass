import QtQuick
import QtQuick.Controls

ComboBox {
    id: picker
    required property var bridge
    textRole: "label"
    valueRole: "milliseconds"
    model: [
        {label: "0 giây", milliseconds: 0},
        {label: "0,2 giây", milliseconds: 200},
        {label: "0,4 giây", milliseconds: 400},
        {label: "0,6 giây", milliseconds: 600},
        {label: "0,8 giây", milliseconds: 800},
        {label: "1,1 giây", milliseconds: 1100},
        {label: "1,5 giây", milliseconds: 1500},
        {label: "2 giây", milliseconds: 2000}
    ]
    currentIndex: Math.max(0, model.findIndex(item => item.milliseconds === bridge.readingGapMs))
    onActivated: bridge.setReadingGapMs(currentValue)
    Accessible.name: "Khoảng nghỉ giữa các đoạn đọc"
    ToolTip.visible: hovered
    ToolTip.delay: 600
    ToolTip.text: "Áp dụng từ lần đọc tiếp theo bằng Mascot. Không cần tạo lại giọng. Tải lại PowerPoint để cập nhật loa trong file."
}
