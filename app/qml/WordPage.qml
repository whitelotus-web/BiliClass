import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

Item {
    id: page
    required property var appBridge
    readonly property var word: appBridge.wordDocuments
    readonly property var documentState: word.state
    property string shownIdentity: ""
    readonly property bool available: !appBridge.busy && !appBridge.narrationBusy
    readonly property bool compact: height < 700
    signal showPowerPoint()
    signal showLibrary()
    property var modeCodes: ["below", "columns", "keywords", "english"]
    property real previewZoom: 0
    property var densityCodes: ["few", "normal", "deep"]
    property string selectedFont: ""
    readonly property string recentFont: page.word.formattingDefaults.font || ""
    readonly property var fontNames: {
        const names = page.word.fontFamilies
        const saved = page.selectedFont
        const recent = page.recentFont
        let result = saved && names.indexOf(saved) < 0 ? [saved].concat(names) : names
        if (recent && result.indexOf(recent) < 0) result = [recent].concat(result)
        return ["Theo phông gốc"].concat(result)
    }
    readonly property string sourceFontLabel: !page.documentState.id ? "Phông trong tài liệu" : !page.word.sourceFonts.length ? "Theo vùng gốc" : page.word.sourceFonts.length === 1 ? page.word.sourceFonts[0] : "Nhiều phông: " + page.word.sourceFonts.join(", ")
    function draftTitle() { return lessonTitle.text.trim() || page.documentState.source_title || page.documentState.title || "" }
    function draftFont() { return page.selectedFont }
    readonly property bool englishItalic: textStyle.italic
    readonly property bool englishBold: textStyle.bold
    function restoreStyle(options) {
        textStyle.bold = !!options.bold
        textStyle.italic = options.italic === undefined || options.italic
        textStyle.underline = !!options.underline
        textStyle.strike = !!options.strike
        textStyle.script = options.script || "normal"
    }
    function restoreFormattingDefaults() {
        const options = page.word.formattingDefaults
        englishColor.colorCode = options.color || "original"
        restoreStyle(options)
        page.selectedFont = options.font || ""
        englishSize.pointSize = options.font_size || 0
        englishFont.currentIndex = page.selectedFont ? Math.max(0, englishFont.model.indexOf(page.selectedFont)) : 0
    }
    function rememberFormatting() { page.word.rememberFormatting(page.draftOptions()) }
    Component.onCompleted: { restoreFormattingDefaults(); grade.currentIndex = Math.max(0, grade.model.indexOf("11")) }
    property string selectionMode: "highlight"
    property string selectionScope: "paragraphs"
    readonly property bool highlightSelection: selectionMode === "highlight"
    readonly property bool resultVisible: !page.documentState.working && page.documentState.can_export && (page.documentState.phase === "completed" || page.documentState.phase === "review")
    onSelectionModeChanged: { if (highlightPopup) highlightPopup.close(); if (continuousText) continuousText.deselect() }
    onVisibleChanged: if (!visible) { if (highlightPopup) highlightPopup.close(); if (sourceDialog) sourceDialog.close() }
    onWidthChanged: if (highlightPopup) highlightPopup.close()
    onHeightChanged: if (highlightPopup) highlightPopup.close()
    function offerHighlightedText() {
        if (!page.visible || !page.available || !page.highlightSelection || !page.documentState.id || !continuousText.selectedText.trim()) return
        highlightPopup.documentIdentity = page.documentState.id
        highlightPopup.rangeStart = continuousText.selectionStart
        highlightPopup.rangeEnd = continuousText.selectionEnd
        highlightPopup.excerpt = continuousText.selectedText.replace(/[\u2029\uFDD0\uFDD1]/g, "\n").replace(/\uFFFC/g, "[Hình]")
        const caret = continuousText.cursorRectangle
        const container = highlightPopup.parent
        const point = continuousText.mapToItem(container, caret.x, caret.y)
        highlightPopup.x = Math.max(12, Math.min(point.x + 8, container.width - highlightPopup.width - 12))
        const below = point.y + caret.height + 8
        highlightPopup.y = Math.max(12, Math.min(below + highlightPopup.height <= container.height - 12 ? below : point.y - highlightPopup.height - 8, container.height - highlightPopup.height - 12))
        highlightPopup.open()
    }
    function openDocument(url) {
        word.openConfiguredFile(url, {options: draftOptions(), subject: subject.currentText, grade: grade.currentText, title: lessonTitle.text.trim()})
    }
    function showDocument() {
        const flick = wordScroll.contentItem
        flick.cancelFlick()
        flick.contentY = Math.max(0, Math.min(documentPanels.y - 12, flick.contentHeight - flick.height))
    }
    property real sourceScrollFraction: 0
    function rememberSourceScroll() {
        const flick = page.highlightSelection ? textScroll.contentItem : sources
        sourceScrollFraction = flick.contentY / Math.max(1, flick.contentHeight - flick.height)
    }
    function restoreSourceScroll() {
        const flick = page.highlightSelection ? textScroll.contentItem : sources
        flick.contentY = Math.max(0, page.sourceScrollFraction * Math.max(0, flick.contentHeight - flick.height))
    }
    function expandSource() { highlightPopup.close(); rememberSourceScroll(); sourceDialog.open() }
    function clearSourceSelections() { highlightPopup.close(); page.word.clearSelection() }
    readonly property bool configurationMatches: modeCodes[mode.currentIndex] === (page.documentState.options.mode || "below")
        && englishColor.colorCode === (page.documentState.options.color || "original")
        && page.englishItalic === (page.documentState.options.italic === undefined ? true : page.documentState.options.italic)
        && page.englishBold === (page.documentState.options.bold || false)
        && textStyle.underline === !!page.documentState.options.underline && textStyle.strike === !!page.documentState.options.strike
        && textStyle.script === (page.documentState.options.script || "normal")
        && page.draftFont() === (page.documentState.options.font || "")
        && englishSize.pointSize === (page.documentState.options.font_size || 0)
        && densityCodes[density.currentIndex] === (page.documentState.options.density || "normal")
        && subject.currentText === (page.documentState.subject || "Toán") && grade.currentText === (page.documentState.grade || "11")
        && page.draftTitle() === (page.documentState.title || "")
    function draftOptions() { return {mode: modeCodes[mode.currentIndex], color: englishColor.colorCode, italic: page.englishItalic, bold: page.englishBold, underline: textStyle.underline, strike: textStyle.strike, script: textStyle.script, font: page.draftFont(), font_size: englishSize.pointSize, density: densityCodes[density.currentIndex]} }
    function syncLoaded() {
        if (!page.documentState.id || shownIdentity === page.documentState.id) return
        highlightPopup.close()
        shownIdentity = page.documentState.id
        mode.currentIndex = Math.max(0, modeCodes.indexOf(page.documentState.options.mode || "below"))
        englishColor.colorCode = page.documentState.options.color || "original"
        density.currentIndex = Math.max(0, densityCodes.indexOf(page.documentState.options.density || "normal"))
        page.restoreStyle(page.documentState.options)
        page.selectedFont = page.documentState.options.font || ""
        englishSize.pointSize = page.documentState.options.font_size || 0
        englishFont.currentIndex = page.selectedFont ? Math.max(0, englishFont.model.indexOf(page.selectedFont)) : 0
        lessonTitle.text = page.documentState.title || ""
        subject.currentIndex = Math.max(0, appBridge.conversionSubjects.indexOf(page.documentState.subject || "Toán"))
        education.currentIndex = education.model.indexOf(page.documentState.education_level || "THPT")
        grade.currentIndex = Math.max(0, grade.model.indexOf(page.documentState.grade || "11"))
        page.previewZoom = 0
    }
    Connections { target: page.word; function onChanged() { if (!page.available) highlightPopup.close(); page.syncLoaded() }
        function onConfigurationRestored() { page.shownIdentity = ""; page.syncLoaded() }
    }
    FileDialog { id: choose; objectName: "wordFileDialog"; title: "Chọn bài giảng Word"; nameFilters: ["Bài giảng Word (*.docx)"]; onAccepted: page.openDocument(selectedFile.toString()) }
    Pane {
        id: highlightPopup; objectName: "wordHighlightPopup"; z: 100; visible: false
        parent: sourceDialog.visible ? expandedSourceHost : page
        property string documentIdentity: ""
        property int rangeStart: 0
        property int rangeEnd: 0
        property string excerpt: ""
        width: Math.min(340, page.width - 24); padding: 10
        function open() { visible = true }
        function close() { if (visible) { visible = false; continuousText.deselect() } }
        Accessible.name: "Xác nhận vùng văn bản cần dịch"
        background: Rectangle { color: AppTheme.surface; radius: 10; border.color: AppTheme.blue }
        contentItem: ColumnLayout { spacing: 8
            Label { text: highlightPopup.excerpt.slice(0, 180); textFormat: Text.PlainText; color: AppTheme.muted; font.pixelSize: 11; wrapMode: Text.WordWrap; maximumLineCount: 3; elide: Text.ElideRight; Layout.fillWidth: true }
            RowLayout { Layout.fillWidth: true; spacing: 8
                WordAction { objectName: "wordAcceptHighlight"; text: "Chọn đoạn này để dịch"; primary: true; Layout.fillWidth: true; enabled: page.available
                    onClicked: {
                        if (page.word.previewHtml) page.word.addPreviewSelection(highlightPopup.documentIdentity, continuousText.getText(0, continuousText.length), highlightPopup.rangeStart, highlightPopup.rangeEnd)
                        else page.word.addTextSelection(highlightPopup.documentIdentity, highlightPopup.rangeStart, highlightPopup.rangeEnd)
                        highlightPopup.close()
                    }
                }
                WordAction { objectName: "wordDismissHighlight"; text: "Hủy"; onClicked: highlightPopup.close() }
            }
        }
    }
    Dialog {
        id: sourceDialog; objectName: "wordExpandedDialog"; parent: Overlay.overlay
        anchors.centerIn: parent; width: Math.min(1440, parent.width - 32); height: parent.height - 32
        modal: true; dim: true; padding: 12; closePolicy: Popup.CloseOnEscape
        background: Rectangle { color: AppTheme.surface; radius: 12; border.color: AppTheme.line }
        header: RowLayout {
            spacing: 10
            Label { text: "Chọn phần văn bản cần dịch"; color: AppTheme.ink; font.pixelSize: 17; font.bold: true; leftPadding: 16; Layout.fillWidth: true }
            Hint { text: "Đã chọn " + (page.documentState.selected_count || 0) + " vùng" }
            WordAction { objectName: "wordExpandedClearAll"; text: "Bỏ tất cả"; enabled: page.available && page.documentState.selected_count > 0; onClicked: page.clearSourceSelections() }
            WordAction { objectName: "wordCollapseSource"; text: "Xong / Thu gọn"; primary: true; onClicked: sourceDialog.close(); Layout.rightMargin: 12; Layout.topMargin: 8 }
        }
        contentItem: Item { id: expandedSourceHost; objectName: "wordExpandedSourceHost" }
        onOpened: Qt.callLater(page.restoreSourceScroll)
        onAboutToHide: { highlightPopup.close(); page.rememberSourceScroll() }
        onClosed: Qt.callLater(page.restoreSourceScroll)
    }
    Dialog {
        id: keywordDialog; property string regionIdentity: ""; title: "Thêm từ khóa vào vùng chọn"; modal: true
        anchors.centerIn: parent; width: Math.min(440, page.width - 30); standardButtons: Dialog.Ok | Dialog.Cancel
        onAccepted: page.word.addKeyword(regionIdentity, keywordVi.text, keywordEn.text)
        contentItem: ColumnLayout { spacing: 10
            Label { text: "Từ tiếng Việt có trong vùng đã chọn"; color: AppTheme.ink; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            TextField { id: keywordVi; objectName: "wordAddKeywordVi"; Layout.fillWidth: true; maximumLength: 160 }
            Label { text: "Thuật ngữ tiếng Anh"; color: AppTheme.ink }
            TextField { id: keywordEn; objectName: "wordAddKeywordEn"; Layout.fillWidth: true; maximumLength: 160 }
        }
    }
    component Hint: Label { color: AppTheme.muted; font.pixelSize: 12; wrapMode: Text.WordWrap; textFormat: Text.PlainText }
    component SelectionRadio: ChoiceRadioButton {
        implicitHeight: 32
        leftPadding: 0; rightPadding: 4; spacing: 5
    }
    component SelectionScope: CheckBox {
        opacity: enabled ? 1 : .45; implicitHeight: 30; leftPadding: 0; rightPadding: 6
        indicator: Rectangle { x: 0; y: (parent.height - height) / 2; width: 16; height: 16; radius: 3; color: parent.checked ? AppTheme.blue : AppTheme.surface; border.color: parent.visualFocus || parent.checked ? AppTheme.blue : AppTheme.muted
            Text { anchors.centerIn: parent; text: "✓"; color: "white"; font.pixelSize: 12; visible: parent.parent.checked }
        }
        contentItem: Text { leftPadding: 22; text: parent.text; color: AppTheme.ink; font.pixelSize: 12; verticalAlignment: Text.AlignVCenter }
    }
    component Choice: ComboBox {
        implicitHeight: 38; font.pixelSize: 12; leftPadding: 0; rightPadding: 0
        contentItem: Label { text: parent.displayText; color: AppTheme.ink; font: parent.font; verticalAlignment: Text.AlignVCenter; leftPadding: 10; rightPadding: 28; elide: Text.ElideRight }
        background: Rectangle { color: AppTheme.field; radius: 8; border.color: parent.activeFocus ? AppTheme.blue : AppTheme.line }
    }
    ColumnLayout {
        anchors.fill: parent; spacing: page.compact ? 8 : 12
        ContentScrollView {
        id: wordScroll; objectName: "wordWorkflowScroll"; Layout.fillWidth: true; Layout.fillHeight: true
        outerGutter: true; contentWidth: availableWidth
        ColumnLayout {
        width: wordScroll.availableWidth; spacing: page.compact ? 8 : 12
        RowLayout { Layout.fillWidth: true
            Label { objectName: "wordPageHeading"; text: "Chuyển đổi bài giảng song ngữ"; color: AppTheme.ink; font.pixelSize: page.compact ? 24 : 27; font.weight: Font.Bold; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        }
        RowLayout { Layout.fillWidth: true
            ConversionDocumentTab { objectName: "wordTabPowerPoint"; onClicked: page.showPowerPoint() }
            ConversionDocumentTab { objectName: "wordTabWord"; word: true; selected: true }
            Item { Layout.fillWidth: true }
        }
        Hint { objectName: "wordWorkflowGuide"; text: "Chọn Word → Chọn cấu hình song ngữ → Chọn vùng cần dịch → Xem và lưu Word."; font.pixelSize: 13; Layout.fillWidth: true }
        WordUpload {
            objectName: "wordSourceArea"; Layout.fillWidth: true; busy: !page.available; reading: !!page.documentState.working
            fileName: page.documentState.id ? page.documentState.title + ".docx" : ""
            paragraphCount: (page.documentState.paragraphs || []).length
            onChooseFile: choose.open()
            onFileDropped: function(url) { page.openDocument(url) }
            onShowDocument: page.showDocument()
        }
        Rectangle {
            objectName: "wordConfiguration"; Layout.fillWidth: true
            implicitHeight: configuration.implicitHeight + (page.compact ? 18 : 26)
            color: AppTheme.surface; radius: 14; border.color: AppTheme.line
            ColumnLayout {
            id: configuration; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: page.compact ? 9 : 13; spacing: page.compact ? 6 : 10
            Label { text: "Cấu hình bài giảng"; color: AppTheme.ink; font.pixelSize: 15; font.weight: Font.DemiBold }
            GridLayout {
            Layout.fillWidth: true; columns: page.width >= 680 ? 4 : 2; columnSpacing: 12; rowSpacing: 8
            ColumnLayout { Layout.fillWidth: true; Layout.preferredWidth: 3; spacing: 4
                Hint { text: "Tên bài học" }
                TextField { id: lessonTitle; objectName: "wordTitle"; placeholderText: "Tên theo file Word"; maximumLength: 200; color: AppTheme.ink; implicitHeight: 38; Layout.fillWidth: true; enabled: page.available
                    background: Rectangle { color: AppTheme.field; radius: 8; border.color: parent.activeFocus ? AppTheme.blue : AppTheme.line } }
            }
            ColumnLayout { Layout.fillWidth: true; Layout.preferredWidth: 2; spacing: 4
                Hint { text: "Môn học" }
                Choice { id: subject; objectName: "wordSubject"; model: page.appBridge.conversionSubjects; currentIndex: Math.max(0, page.appBridge.conversionSubjects.indexOf("Toán")); Layout.fillWidth: true; enabled: page.available }
            }
            ColumnLayout { Layout.fillWidth: true; Layout.preferredWidth: 1; spacing: 4
                Hint { text: "Cấp học" }
                Choice { id: education; objectName: "wordEducation"; model: ["THPT", "THCS", "Tiểu học"]; Layout.fillWidth: true; enabled: page.available; onActivated: grade.currentIndex = 0 }
            }
            ColumnLayout { Layout.fillWidth: true; Layout.preferredWidth: 1; spacing: 4
                Hint { text: "Khối lớp" }
                Choice { id: grade; objectName: "wordGrade"; model: page.appBridge.educationGrades(education.currentText); currentIndex: 1; Layout.fillWidth: true; enabled: page.available }
            }
            }
            RowLayout {
            objectName: "wordFormattingToolbar"; Layout.fillWidth: true; spacing: 6
            ColumnLayout { Layout.fillWidth: true; Layout.minimumWidth: mode.implicitWidth; Layout.alignment: Qt.AlignTop; spacing: 4
                Hint { text: "Kiểu chuyển đổi" }
                ButtonGroup { id: conversionModes }
                RowLayout {
                    id: mode; objectName: "wordMode"; Layout.fillWidth: true; spacing: 4
                    property int currentIndex: 0
                    readonly property var model: ["Anh ngay dưới Việt", "Việt–Anh hai cột", "Từ khóa tiếng Anh", "Tiếng Anh 100% ở vùng chọn"]
                    readonly property var shortLabels: page.width < 950 ? ["Dưới", "Hai cột", "Từ khóa", "100% Anh"] : ["Anh dưới Việt", "Việt–Anh hai cột", "Từ khóa tiếng Anh", "100% Anh"]
                    readonly property string currentText: model[currentIndex] || model[0]
                    Repeater { model: mode.model
                        SelectionRadio {
                            required property int index; required property string modelData
                            id: conversionRadio
                            objectName: "wordMode_" + index; text: mode.shortLabels[index]
                            implicitHeight: 38; rightPadding: 0
                            Layout.fillWidth: true
                            Accessible.name: modelData
                            ToolTip.visible: hovered; ToolTip.text: modelData
                            contentItem: Text { text: conversionRadio.text; leftPadding: 22; font.pixelSize: 12; font.weight: Font.DemiBold; color: AppTheme.ink; verticalAlignment: Text.AlignVCenter; wrapMode: Text.NoWrap }
                            checked: mode.currentIndex === index; ButtonGroup.group: conversionModes
                            enabled: page.available; onClicked: mode.currentIndex = index
                        }
                    }
                }
            }
                ColumnLayout { Layout.alignment: Qt.AlignBottom; Layout.minimumWidth: 60; Layout.maximumWidth: 60; spacing: 4
                    WordColorPicker { id: englishColor; objectName: "wordEnglishColor"; visible: mode.currentIndex !== 2; Layout.preferredWidth: 60; enabled: page.available; onChosen: page.rememberFormatting() }
                    Choice { id: density; objectName: "wordKeywordDensity"; visible: mode.currentIndex === 2; model: ["Ít", "Vừa", "Sâu"]; currentIndex: 1; Layout.preferredWidth: 60; enabled: page.available
                        Accessible.name: "Mức từ khóa tiếng Anh"; ToolTip.visible: hovered; ToolTip.text: "Mức từ khóa tiếng Anh: " + ["Ít", "Vừa phải", "Chuyên sâu"][currentIndex]
                        contentItem: Label { text: density.displayText; color: AppTheme.ink; font: density.font; verticalAlignment: Text.AlignVCenter; leftPadding: 8; rightPadding: 24; elide: Text.ElideRight }
                    }
                }
            ColumnLayout { Layout.alignment: Qt.AlignBottom; spacing: 4
                WordTextStyle { id: textStyle; objectName: "wordTextStyle"; compact: true; Layout.minimumWidth: implicitWidth; enabled: page.available; onChosen: page.rememberFormatting() }
            }
            ColumnLayout { Layout.alignment: Qt.AlignBottom; spacing: 4
                RowLayout { spacing: 4
                Choice { id: englishFont; objectName: "wordEnglishFont"; model: page.fontNames; Layout.preferredWidth: page.width < 950 ? 110 : 160; Layout.minimumWidth: Layout.preferredWidth; Layout.maximumWidth: Layout.preferredWidth
                    Accessible.name: page.selectedFont ? "Phông tiếng Anh: " + page.selectedFont : "Phông gốc: " + page.sourceFontLabel
                    displayText: page.selectedFont || page.sourceFontLabel
                    enabled: page.available
                    onModelChanged: currentIndex = page.selectedFont ? Math.max(0, model.indexOf(page.selectedFont)) : 0
                    onActivated: { page.selectedFont = currentIndex > 0 ? currentText : ""; page.rememberFormatting() }
                    ToolTip.visible: fontHover.hovered; ToolTip.text: page.selectedFont || page.sourceFontLabel + "\nChọn phông khác trực tiếp, hoặc Theo phông gốc để giữ phông riêng từng vùng."
                    HoverHandler { id: fontHover }
                }
                WordFontSize { id: englishSize; objectName: "wordFontSize"; sourceSize: page.word.sourceFontSize; Layout.preferredWidth: 60; enabled: page.available; onChosen: page.rememberFormatting() }
                }
            }
            }
            }
        }
        Rectangle {
            visible: !!page.documentState.message; Layout.fillWidth: true
            implicitHeight: message.implicitHeight + 20; radius: 9
            color: page.documentState.phase === "paused" ? AppTheme.warningSurface : AppTheme.selected
            border.color: page.documentState.phase === "paused" ? AppTheme.warningLine : AppTheme.line
            Hint { id: message; anchors.fill: parent; anchors.margins: 10; text: page.documentState.message || ""; color: page.documentState.phase === "paused" ? AppTheme.warningInk : AppTheme.ink }
        }
        Hint { visible: (page.documentState.notices || []).length > 0; text: (page.documentState.notices || []).slice(-1).join(""); color: AppTheme.warning; font.pixelSize: 11; Layout.fillWidth: true }
        Hint { visible: !!page.documentState.id; text: page.documentState.preview_notice || "Xem định dạng, hình và bảng từ file gốc. Phân trang, hình nổi và công thức phức tạp cần đối chiếu trong Word."; Layout.fillWidth: true; font.pixelSize: 11 }
        RowLayout {
            id: documentPanels; objectName: "wordDocumentPanels"; Layout.fillWidth: true; spacing: 12
            Layout.preferredHeight: page.documentState.id ? Math.max(320, Math.min(560, page.height * .58)) : 210
            Layout.minimumHeight: Layout.preferredHeight; Layout.maximumHeight: Layout.preferredHeight
            Rectangle {
                id: sourcePanel; objectName: "wordSourcePanel"
                Layout.fillWidth: true; Layout.fillHeight: true; Layout.preferredWidth: 1.3; color: AppTheme.surface; radius: 11; border.color: AppTheme.line
                states: State {
                    when: sourceDialog.visible
                    ParentChange { target: sourcePanel; parent: expandedSourceHost; x: 0; y: 0; width: expandedSourceHost.width; height: expandedSourceHost.height }
                }
                ColumnLayout { anchors.fill: parent; anchors.margins: 12; spacing: 8
                    RowLayout { Layout.fillWidth: true
                        Label { text: "Nội dung gốc"; font.bold: true; color: AppTheme.ink; Layout.fillWidth: true }
                        WordAction { objectName: "wordExpandSource"; text: "⛶ Phóng to để chọn"; visible: !sourceDialog.visible; enabled: page.available && !!page.documentState.id; implicitHeight: 30; onClicked: page.expandSource() }
                    }
                    ButtonGroup { id: selectionMethods }
                    ButtonGroup { id: selectionScopes }
                    Flow { Layout.fillWidth: true; spacing: 4
                        SelectionRadio { objectName: "wordSelectByHighlight"; text: "Bôi đen văn bản"; checked: page.highlightSelection; ButtonGroup.group: selectionMethods; enabled: page.available; onClicked: page.selectionMode = "highlight" }
                        Column { spacing: 0
                            SelectionRadio { objectName: "wordSelectByCheckbox"; text: "Tích chọn đoạn/câu"; checked: !page.highlightSelection; ButtonGroup.group: selectionMethods; enabled: page.available; onClicked: page.selectionMode = "checkbox" }
                            Row { leftPadding: 23; spacing: 8
                                Rectangle { width: 2; height: 26; color: !page.highlightSelection ? AppTheme.blue : AppTheme.line }
                                SelectionScope { objectName: "wordScopeParagraphs"; text: "Theo đoạn"; checked: page.selectionScope === "paragraphs"; ButtonGroup.group: selectionScopes; enabled: page.available && !page.highlightSelection; onClicked: page.selectionScope = "paragraphs" }
                                SelectionScope { objectName: "wordScopeSentences"; text: "Theo câu"; checked: page.selectionScope === "sentences"; ButtonGroup.group: selectionScopes; enabled: page.available && !page.highlightSelection; onClicked: page.selectionScope = "sentences" }
                            }
                        }
                    }
                    RowLayout { Layout.fillWidth: true
                        WordAction { objectName: "wordSelectAll"; text: page.highlightSelection ? "Bôi đen tất cả" : "Chọn tất cả"; enabled: page.available && !!page.documentState.id
                            onClicked: {
                                if (page.highlightSelection) { continuousText.forceActiveFocus(); continuousText.selectAll(); Qt.callLater(page.offerHighlightedText) }
                                else page.word.selectAll(page.selectionScope)
                            }
                        }
                        WordAction { objectName: "wordClearSelection"; text: "Bỏ chọn"; enabled: page.available && page.documentState.selected_count > 0; onClicked: page.word.clearSelection() }
                        WordAction { objectName: "wordConfirmHighlight"; visible: page.highlightSelection && continuousText.selectedText.length > 0; text: "Thêm vùng"; enabled: page.available; onClicked: page.offerHighlightedText() }
                    }
                    Hint { visible: page.highlightSelection; text: "Bôi đen rồi nhả chuột để chọn vùng dịch. Các vùng đã xác nhận được giữ ở bên phải."; font.pixelSize: 11; Layout.fillWidth: true }
                    RowLayout { visible: page.highlightSelection && !!page.documentState.id; spacing: 4
                        WordAction { objectName: "wordZoomOut"; text: "−"; implicitHeight: 27; onClicked: page.previewZoom = Math.max(.4, paper.scale - .1) }
                        WordAction { objectName: "wordZoomFit"; text: page.previewZoom === 0 ? "Vừa khung" : Math.round(paper.scale * 100) + "%"; implicitHeight: 27; onClicked: page.previewZoom = 0 }
                        WordAction { objectName: "wordZoomIn"; text: "+"; implicitHeight: 27; onClicked: page.previewZoom = Math.min(1.5, paper.scale + .1) }
                    }
                    ListView {
                        id: sources; objectName: "wordSourceList"; visible: !page.highlightSelection; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 9
                        model: { const revision = page.documentState; return page.word.items(page.selectionScope) }
                        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                        Hint { visible: !page.documentState.id; anchors.centerIn: parent; width: parent.width - 24; horizontalAlignment: Text.AlignHCenter; text: "Tải file Word ở trên để xem nội dung và chọn phần cần dịch." }
                        delegate: Rectangle {
                            id: sourceRow; required property var modelData; required property int index
                            width: ListView.view.width - 12; height: sourceContents.implicitHeight + 16; radius: 8
                            color: "white"; border.color: modelData.selected ? AppTheme.blue : "#d5dbe4"; border.width: modelData.selected ? 2 : 1
                            ColumnLayout { id: sourceContents; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 8; spacing: 3
                                RowLayout { Layout.fillWidth: true
                                    CheckBox { objectName: "wordSelect_" + sourceRow.index; checked: sourceRow.modelData.selected; enabled: page.available && sourceRow.modelData.editable
                                        onClicked: page.word.toggle(sourceRow.modelData.paragraph, sourceRow.modelData.start, sourceRow.modelData.end, checked) }
                                    Hint { text: sourceRow.modelData.location; color: "#53647c"; font.pixelSize: 10; Layout.fillWidth: true }
                                }
                                TextArea {
                                    id: sourceText; objectName: "wordSourceText_" + sourceRow.index; Layout.fillWidth: true; implicitHeight: contentHeight + 12
                                    text: sourceRow.modelData.html || sourceRow.modelData.text; textFormat: sourceRow.modelData.html ? TextEdit.RichText : TextEdit.PlainText; readOnly: true; selectByMouse: true; persistentSelection: true; wrapMode: TextEdit.Wrap
                                    color: "#202020"; selectedTextColor: "white"; selectionColor: "#1769d5"; font.pixelSize: 13
                                    background: Rectangle { color: "transparent" }
                                }
                                WordAction { objectName: "wordAddRange_" + sourceRow.index; text: "Thêm vùng bôi đen"; visible: sourceText.selectedText.length > 0; enabled: page.available && sourceRow.modelData.editable
                                    onClicked: {
                                        if (sourceRow.modelData.html) page.word.addPreviewRange(page.documentState.id, sourceRow.modelData.paragraph, sourceRow.modelData.start, sourceRow.modelData.end, sourceText.getText(0, sourceText.length), sourceText.selectionStart, sourceText.selectionEnd)
                                        else page.word.addRange(sourceRow.modelData.paragraph, sourceRow.modelData.start, sourceText.selectionStart, sourceText.selectionEnd)
                                    } }
                                Hint { visible: !sourceRow.modelData.editable; text: sourceRow.modelData.reason; font.pixelSize: 10; Layout.fillWidth: true }
                            }
                        }
                    }
                    ContentScrollView {
                        id: textScroll; objectName: "wordContinuousScroll"; visible: page.highlightSelection
                        Layout.fillWidth: true; Layout.fillHeight: true; implicitWidth: 0; implicitHeight: 0
                        bottomPadding: page.previewZoom > 0 ? 18 : 0
                        contentWidth: Math.max(availableWidth, paper.width * paper.scale + 16)
                        contentHeight: Math.max(availableHeight, paper.height * paper.scale + 16)
                        Item {
                        width: textScroll.contentWidth; height: textScroll.contentHeight
                        Rectangle {
                        id: paper; objectName: "wordPreviewPaper"; width: page.documentState.id ? page.word.previewPageWidth : Math.max(100, textScroll.availableWidth - 16)
                        height: Math.max(continuousText.implicitHeight, page.documentState.id ? width * 1.414 : 90)
                        scale: page.documentState.id ? page.previewZoom || Math.min(1, (textScroll.availableWidth - 16) / width) : 1
                        transformOrigin: Item.TopLeft; x: (parent.width - width * scale) / 2; y: 8
                        color: "white"; border.color: "#d5dbe4"; border.width: 1
                        TextArea {
                            id: continuousText; objectName: "wordContinuousText"; width: paper.width
                            text: page.highlightSelection ? page.word.previewHtml || page.word.selectionText : ""; textFormat: page.word.previewHtml ? TextEdit.RichText : TextEdit.PlainText
                            placeholderText: "Tải file Word ở trên để bôi đen phần cần dịch."
                            readOnly: true; selectByMouse: true; persistentSelection: true; wrapMode: TextEdit.Wrap
                            Keys.onEscapePressed: function(event) { if (highlightPopup.visible) highlightPopup.close(); else event.accepted = false }
                            enabled: page.available && !!page.documentState.id; color: "#202020"
                            selectedTextColor: "white"; selectionColor: "#1769d5"; font.family: "Times New Roman"; font.pointSize: 12
                            topPadding: page.documentState.id ? page.word.previewMargins[0] : 12; rightPadding: page.documentState.id ? page.word.previewMargins[1] : 12
                            bottomPadding: page.documentState.id ? page.word.previewMargins[2] : 12; leftPadding: page.documentState.id ? page.word.previewMargins[3] : 12
                            background: Item { }
                            PointHandler {
                                acceptedButtons: Qt.LeftButton
                                onActiveChanged: {
                                    if (active) {
                                        highlightPopup.close()
                                        continuousText.cursorPosition = continuousText.positionAt(point.position.x, point.position.y)
                                        continuousText.forceActiveFocus()
                                    }
                                    else Qt.callLater(page.offerHighlightedText)
                                }
                            }
                        }
                        }
                        }
                    }
                }
            }
            Rectangle {
                Layout.fillWidth: true; Layout.fillHeight: true; Layout.preferredWidth: 1; color: AppTheme.surface; radius: 11; border.color: AppTheme.line
                ColumnLayout { anchors.fill: parent; anchors.margins: 12; spacing: 8
                    RowLayout { Layout.fillWidth: true
                        Label { objectName: "wordSelectedCount"; text: page.documentState.id ? "Đã chọn " + (page.documentState.selected_count || 0) + " vùng" : "Bản dịch xem trước"; font.bold: true; color: AppTheme.ink; Layout.fillWidth: true }
                        WordAction { objectName: "wordClearAllRanges"; text: "Bỏ tất cả"; enabled: page.available && page.documentState.selected_count > 0; visible: !!page.documentState.id; implicitHeight: 30; onClicked: page.clearSourceSelections() }
                    }
                    Hint { text: !page.documentState.id ? "Bản dịch sẽ hiện tại đây sau khi chọn vùng và chuyển đổi." : page.documentState.can_export ? "Xem phần Việt và chỉnh bản Anh trước khi lưu." : page.documentState.selected_count ? "Tiếp tục chọn vùng hoặc bấm Chuyển đổi ở thanh dưới để xem bản Anh." : page.highlightSelection ? "Bôi đen bên trái, nhả chuột rồi bấm Chọn đoạn này để dịch." : "Tích chọn đoạn/câu hoặc thêm vùng bôi đen ở bên trái."; Layout.fillWidth: true }
                    ListView {
                        objectName: "wordReviewList"; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 10; model: page.documentState.regions
                        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                        delegate: Rectangle {
                            id: selectedRow; required property var modelData; required property int index
                            width: ListView.view.width - 12; height: selectedContents.implicitHeight + 20; radius: 8; color: AppTheme.field; border.color: AppTheme.line
                            ColumnLayout { id: selectedContents; anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 10; spacing: 5
                                RowLayout { Layout.fillWidth: true
                                    Hint { text: "Vùng " + (selectedRow.index + 1); font.pixelSize: 10; Layout.fillWidth: true }
                                    WordAction { objectName: "wordRemoveRange_" + selectedRow.index; text: "Bỏ vùng"; implicitHeight: 28; enabled: page.available; onClicked: page.word.removeRange(selectedRow.modelData.id) }
                                }
                                Label { text: selectedRow.modelData.vi; textFormat: Text.PlainText; color: AppTheme.ink; font.pixelSize: 13; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                TextArea {
                                    objectName: "wordEnglishDraft_" + selectedRow.index; visible: !!selectedRow.modelData.en && page.documentState.options.mode !== "keywords"; Layout.fillWidth: true; implicitHeight: contentHeight + 16
                                    text: selectedRow.modelData.display_en || ""; textFormat: TextEdit.PlainText; wrapMode: TextEdit.Wrap; selectByMouse: true; color: englishColor.inkColor; font.pointSize: englishSize.pointSize || Number(page.word.sourceFontSize) || 11; font.italic: page.englishItalic; font.bold: page.englishBold; font.underline: textStyle.underline; font.strikeout: textStyle.strike; font.family: page.draftFont() || "Be Vietnam Pro"; enabled: page.available
                                    onTextChanged: if (activeFocus) page.word.setDraft(selectedRow.modelData.id, text)
                                    background: Rectangle { color: AppTheme.surface; radius: 6; border.color: AppTheme.line }
                                }
                                Repeater { model: selectedRow.modelData.annotations || []
                                    RowLayout { id: keywordRow; required property var modelData; required property int index; Layout.fillWidth: true
                                        Hint { text: (modelData.vi || "Từ khóa") + " →"; Layout.preferredWidth: 110; font.pixelSize: 11 }
                                        TextField { objectName: "wordKeyword_" + selectedRow.index + "_" + keywordRow.index; text: keywordRow.modelData.en; color: AppTheme.blue; font.pixelSize: 12; Layout.fillWidth: true; enabled: page.available
                                            onTextEdited: page.word.setKeywordDraft(selectedRow.modelData.id, keywordRow.index, text)
                                            placeholderText: "Để trống để bỏ từ khóa"
                                            background: Rectangle { color: AppTheme.surface; radius: 6; border.color: AppTheme.line } }
                                    }
                                }
                                WordAction { visible: page.documentState.options.mode === "keywords" && !!selectedRow.modelData.en; text: "+ Thêm từ khóa"; enabled: page.available
                                    onClicked: { keywordDialog.regionIdentity = selectedRow.modelData.id; keywordVi.text = ""; keywordEn.text = ""; keywordDialog.open() } }
                            }
                        }
                    }
                }
            }
        }
        }
        }
        ProgressBar { objectName: "wordProgress"; visible: page.documentState.working; Layout.fillWidth: true; from: 0; to: 100; value: page.documentState.percent || 0; indeterminate: value <= 0 }
        Flow {
            objectName: "wordResultActions"; visible: page.resultVisible; Layout.fillWidth: true; spacing: 8
            WordAction { objectName: "wordSave"; text: "Lưu Word song ngữ"; primary: page.word.draftsPending || page.documentState.phase === "review"; enabled: page.available && page.configurationMatches && (page.word.draftsPending || page.documentState.phase === "review"); onClicked: page.word.save() }
            WordAction { objectName: "wordOpenOutput"; visible: !!page.documentState.output_sha256; text: "Mở Word đã lưu"; primary: page.documentState.phase === "completed"; enabled: page.available; onClicked: page.word.openOutput(page.documentState.id) }
            WordAction { objectName: "wordOpenFolder"; visible: !!page.documentState.output_sha256; text: "Mở thư mục"; enabled: page.available; onClicked: page.word.openFolder(page.documentState.id) }
            WordAction { id: more; objectName: "wordMore"; visible: !!page.documentState.output_sha256; text: "⋮"; enabled: page.available; onClicked: moreMenu.popup()
                Menu { id: moreMenu; MenuItem { objectName: "wordUndo"; text: "Khôi phục bản xuất trước"; enabled: !!page.documentState.has_previous; onTriggered: page.word.restorePrevious() } }
            }
            WordAction { objectName: "wordGoLibrary"; text: "Về bài giảng"; enabled: page.available; onClicked: page.showLibrary() }
        }
        Hint { visible: page.word.draftsPending; text: "Có chỉnh sửa bản dịch/từ khóa. Bấm Lưu Word song ngữ để áp dụng."; Layout.fillWidth: true }
        Hint { visible: !!page.documentState.id && !page.configurationMatches; text: "Cấu hình đã đổi. Bấm Chuyển đổi để cập nhật và tự lưu."; Layout.fillWidth: true }
        RowLayout {
            objectName: "wordFooterPrimaryRow"; Layout.fillWidth: true; spacing: 16
            ConfigurationSummary {
                objectName: "wordConfigurationSummary"; Layout.fillWidth: true; Layout.minimumWidth: 0
                entries: [{key: "mode", text: mode.currentText, emphasis: true},
                    {key: "subject", text: subject.currentText + " · " + education.currentText + " " + grade.currentText},
                    {key: "format", text: textStyle.description + " · " + (englishColor.original ? "Màu gốc" : "#" + englishColor.colorCode) + " · " + (page.draftFont() || "Phông gốc") + " · " + (englishSize.pointSize ? englishSize.pointSize + " pt" : "Cỡ gốc")},
                    {key: "selection", text: (page.documentState.selected_count || 0) + " vùng đã chọn"}]
            }
            WordAction { objectName: "wordStop"; visible: page.documentState.working; text: "■ Dừng"; danger: true; onClicked: page.word.stop() }
            WordAction { objectName: "wordPreview"; text: page.documentState.working ? "Đang xử lý…" : page.documentState.phase === "paused" ? "Tiếp tục chuyển đổi" : page.documentState.phase === "completed" ? "Chuyển đổi lại" : "Chuyển đổi bài giảng"; primary: true; implicitHeight: 44
                enabled: page.available && page.documentState.selected_count > 0; onClicked: page.word.preview(page.draftOptions(), subject.currentText, grade.currentText, page.draftTitle()) }
        }
    }
}
