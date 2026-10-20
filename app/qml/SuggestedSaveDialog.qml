import QtQuick.Dialogs

FileDialog {
    property url suggestedFile
    property var suggestionProvider: null
    fileMode: FileDialog.SaveFile

    function openSuggested() {
        // Native Windows dialogs copy the initial name when open() is called.
        // visibleChanged fires too late to populate their filename control.
        const target = typeof suggestionProvider === "function" ? suggestionProvider() : suggestedFile
        if (target) {
            const url = target.toString()
            const slash = url.lastIndexOf("/")
            if (slash >= 0) currentFolder = url.substring(0, slash + 1)
        }
        selectedFile = target
        open()
    }
}
