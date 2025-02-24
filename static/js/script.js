document.addEventListener("DOMContentLoaded", function () {
    const themeSelector = document.getElementById("theme-selector");

    // ローカルストレージから前回のテーマを取得
    const savedTheme = localStorage.getItem("selectedTheme");
    if (savedTheme) {
        document.body.classList.add(savedTheme);
        themeSelector.value = savedTheme.replace("-theme", "");
    }

    // テーマ変更時の処理
    themeSelector.addEventListener("change", function () {
        document.body.classList.remove("theme-orange", "theme-blue", "theme-pink");

        const selectedTheme = themeSelector.value;
        if (selectedTheme !== "default") {
            document.body.classList.add("theme-" + selectedTheme);
        }

        // ローカルストレージに保存
        localStorage.setItem("selectedTheme", "theme-" + selectedTheme);
    });
});
