import QtQuick.Dialogs

FileDialog {
    property url suggestedFile
    fileMode: FileDialog.SaveFile

    function openSuggested() {
        // Native Windows dialogs copy the initial name when open() is called.
        // visibleChanged fires too late to populate their filename control.
        selectedFile = suggestedFile
        open()
    }
}
