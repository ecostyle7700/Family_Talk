document.addEventListener("DOMContentLoaded", function () {
    var socket = io();  // WebSocket接続を確立

    // 投稿フォームの要素を取得
    var form = document.querySelector("form");
    var textarea = document.querySelector("textarea");
    var posterSelect = document.querySelector("#poster");

    // フォーム送信時の処理（通常のフォーム送信を防ぎ、WebSocket で送信）
    form.addEventListener("submit", function (event) {
        event.preventDefault();  // デフォルトのフォーム送信を無効化

        var message = textarea.value.trim();
        var poster = posterSelect.value;

        if (message) {
            // WebSocket 経由でメッセージを送信
            socket.emit("new_message", {
                poster: poster,
                content: message
            });

            textarea.value = "";  // 送信後に入力欄をクリア
        }
    });

    // 新しいメッセージを受信したときの処理
    socket.on("receive_message", function (data) {
        var chatBox = document.querySelector(".chat-box");

        // 新しいメッセージを追加
        var messageDiv = document.createElement("div");
        messageDiv.classList.add("message");

        var strong = document.createElement("strong");
        strong.textContent = data.poster + " ";
        
        var contentSpan = document.createElement("span");
        contentSpan.textContent = data.content;

        var timestampSpan = document.createElement("span");
        timestampSpan.classList.add("timestamp");
        timestampSpan.textContent = data.timestamp;

        messageDiv.appendChild(strong);
        messageDiv.appendChild(contentSpan);
        messageDiv.appendChild(timestampSpan);
        
        chatBox.prepend(messageDiv); // 新しいメッセージを上部に追加
    });
});
