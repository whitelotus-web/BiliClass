import QtQuick.Dialogs

FileDialog {
    options: AppTheme.dark ? FileDialog.DontUseNativeDialog : 0
    property url suggestedFile
    property var suggestionProvider: null
    fileMode: FileDialog.SaveFile

    function openSuggested() {
        // Native Windows dialogs copy the initial name when open() is called.
        // visibleChanged fires too late to populate their filename control.
        selectedFile = typeof suggestionProvider === "function" ? suggestionProvider() : suggestedFile
        open()
    }
}
