document.addEventListener("DOMContentLoaded", function () {
    const themeSelector = document.getElementById("theme-selector");
    const body = document.body;

    // ローカルストレージから前回のテーマを取得
    const savedTheme = localStorage.getItem("selectedTheme");

    if (savedTheme) {
        body.classList.add(savedTheme);
        themeSelector.value = savedTheme;
    } else {
        body.classList.add("theme-orange");  // デフォルトでオレンジテーマ適用
        themeSelector.value = "theme-orange";
    }

    // テーマ変更時の処理
    themeSelector.addEventListener("change", function () {
        body.classList.remove("theme-orange", "theme-blue", "theme-pink");

        const selectedTheme = themeSelector.value;
        body.classList.add(selectedTheme);

        // ローカルストレージに保存
        localStorage.setItem("selectedTheme", selectedTheme);
    });
});
