document.addEventListener("DOMContentLoaded", function() {
    const themeSelector = document.getElementById("theme-selector");

    // ローカルストレージにテーマを保存・復元
    if (localStorage.getItem("theme")) {
        document.body.className = localStorage.getItem("theme");
        themeSelector.value = localStorage.getItem("theme");
    }

    themeSelector.addEventListener("change", function() {
        document.body.className = this.value;
        localStorage.setItem("theme", this.value);
    });
});
