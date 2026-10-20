pragma Singleton
import QtQuick

QtObject {
    property bool dark: false
    readonly property color canvas: dark ? "#101827" : "#f3f7fc"
    readonly property color surface: dark ? "#182438" : "#ffffff"
    readonly property color field: dark ? "#111d2e" : "#fbfdff"
    readonly property color raised: dark ? "#1e2d43" : "#f2f7ff"
    readonly property color ink: dark ? "#e6edf7" : "#112650"
    readonly property color muted: dark ? "#afbed2" : "#667997"
    readonly property color blue: dark ? "#87b6ff" : "#0869f9"
    readonly property color accent: dark ? "#1764db" : "#0869f9"
    readonly property color accentText: "#ffffff"
    readonly property color line: dark ? "#34465e" : "#dfe8f4"
    readonly property color selected: dark ? "#223a5c" : "#eaf3ff"
    readonly property color hover: dark ? "#21334e" : "#edf5ff"
    readonly property color disabled: dark ? "#a4b5cd" : "#96a6bc"
    readonly property color disabledSurface: dark ? "#202d40" : "#edf1f7"
    readonly property color icon: dark ? "#c0d2ee" : "#526f98"
    readonly property color success: dark ? "#79dbb8" : "#168567"
    readonly property color warning: dark ? "#f2be77" : "#a66318"
    readonly property color danger: dark ? "#ff9ca5" : "#c92d37"
    // Preserve the established light shades while sharing their dark roles.
    readonly property var darkColors: ({
        "#102c56": "#e6edf7",
        "#102e54": "#e6edf7",
        "#112650": "#e6edf7",
        "#152d4d": "#e6edf7",
        "#16314f": "#e6edf7",
        "#355478": "#afbed2",
        "#41648c": "#afbed2",
        "#486385": "#afbed2",
        "#526888": "#afbed2",
        "#526987": "#afbed2",
        "#667997": "#afbed2",
        "#687b94": "#afbed2",
        "#687e9b": "#afbed2",
        "#075acb": "#87b6ff",
        "#0869f9": "#87b6ff",
        "#0869ff": "#87b6ff",
        "#1855a6": "#87b6ff",
        "#008f89": "#79dbb8",
        "#138578": "#79dbb8",
        "#168567": "#79dbb8",
        "#19745c": "#79dbb8",
        "#8a5a00": "#f2be77",
        "#986019": "#f2be77",
        "#9c651b": "#f2be77",
        "#9e6423": "#f2be77",
        "#a44727": "#f2be77",
        "#a66318": "#f2be77",
        "#a66b24": "#f2be77",
        "#ab5b20": "#f2be77",
        "#ab611f": "#f2be77",
        "#ad651d": "#f2be77",
        "#b14828": "#f2be77",
        "#ba581a": "#f2be77",
        "#c05b31": "#f2be77",
        "#d59020": "#f2be77",
        "#a63d2f": "#ff9ca5",
        "#b42318": "#ff9ca5",
        "#b42d38": "#ff9ca5",
        "#c63434": "#ff9ca5",
        "#c92d37": "#ff9ca5",
        "#8a99b0": "#7f91ab",
        "#8c9eb8": "#7f91ab",
        "#96a6bc": "#7f91ab",
        "#637f9f": "#5a7190",
        "#8ca3bf": "#5a7190",
        "#bdcbdc": "#5a7190",
        "#a8cdff": "#34465e",
        "#aebed2": "#34465e",
        "#b0c4e0": "#34465e",
        "#b7d5f8": "#34465e",
        "#b8c9df": "#34465e",
        "#b9c9de": "#34465e",
        "#bed5f4": "#34465e",
        "#c6d5e9": "#34465e",
        "#cbdcf4": "#34465e",
        "#ccdef7": "#34465e",
        "#d4e4fc": "#34465e",
        "#d6e4f6": "#34465e",
        "#d8e4f3": "#34465e",
        "#dce5f0": "#34465e",
        "#dce7f5": "#34465e",
        "#dce8f8": "#34465e",
        "#dfe8f4": "#34465e",
        "#e0e8f3": "#34465e",
        "#e0e8f4": "#34465e",
        "#e4ecf6": "#34465e",
        "#e5edf7": "#34465e",
        "#e6edf7": "#34465e",
        "#d8e9ff": "#223a5c",
        "#dcecff": "#223a5c",
        "#dfebfb": "#223a5c",
        "#e0edff": "#223a5c",
        "#e6f0ff": "#223a5c",
        "#e6f1ff": "#223a5c",
        "#e7f1ff": "#223a5c",
        "#e7f2ff": "#223a5c",
        "#e8f1ff": "#223a5c",
        "#e8f2ff": "#223a5c",
        "#eaf2ff": "#223a5c",
        "#eaf3ff": "#223a5c",
        "#edf4fd": "#21334e",
        "#edf4ff": "#21334e",
        "#edf5ff": "#21334e",
        "#eef5ff": "#21334e",
        "#f0f4fa": "#21334e",
        "#f0f5fc": "#21334e",
        "#f2f7fe": "#21334e",
        "#f2f7ff": "#21334e",
        "#f2f8ff": "#21334e",
        "#f4f8fe": "#21334e",
        "#f4f8ff": "#21334e",
        "#f6f9fd": "#21334e",
        "#f7faff": "#21334e",
        "#f8fafd": "#21334e",
        "#f8fbff": "#21334e",
        "#fafcff": "#21334e",
        "#fafdff": "#21334e",
        "#f3f7fc": "#101827",
        "#f4f7fc": "#101827",
        "#f5f8fc": "#101827",
        "#f5f8fd": "#101827",
        "#e8eef5": "#202d40",
        "#e8eef7": "#202d40",
        "#e8eff9": "#202d40",
        "#edf1f7": "#202d40",
        "#fbfdff": "#111d2e",
        "#e9eef5": "#0b1321",
        "#ffffff": "#182438",
        "#eefafcff": "#ee182438",
        "#e8f6f0": "#17352f",
        "#eaf7f4": "#17352f",
        "#eef8f4": "#17352f",
        "#eef9f3": "#17352f",
        "#d2eade": "#315b4d",
        "#f2e9db": "#352c22",
        "#f7f3ed": "#352c22",
        "#fbf5eb": "#352c22",
        "#fff0df": "#352c22",
        "#fff7eb": "#352c22",
        "#fff8f4": "#352c22",
        "#e9c5ae": "#6c5140",
        "#fee4e2": "#38232d",
        "#ffe4e7": "#38232d",
        "#fff0ee": "#38232d",
        "#fff6f7": "#38232d",
        "#fffafa": "#38232d",
        "#f0b4ae": "#704650",
        "#f1b8be": "#704650",
        "#0053d2": "#0d50b7",
        "#0055d8": "#0d50b7",
        "#147aff": "#2877e8"
})
    function adapt(light) {
        if (!dark) return light
        return darkColors[String(light).toLowerCase()] || light
    }
}
