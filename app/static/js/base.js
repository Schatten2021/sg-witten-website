if (window.matchMedia) {
    if (window.matchMedia("(prefers-color-scheme: light").matches) {
        document.getElementsByTagName("html")[0].dataset.bsTheme = "light"
    }
}