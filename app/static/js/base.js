if (window.matchMedia) {
    if (window.matchMedia("(prefers-color-scheme: light").matches) {
        document.getElementsByTagName("html")[0].dataset.bsTheme = "light";
    }
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", e => {
        document.getElementsByTagName("html")[0].dataset.bsTheme = e.matches ? "dark" : "light";
    });
}