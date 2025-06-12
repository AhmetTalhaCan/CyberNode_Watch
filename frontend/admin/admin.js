document.getElementById("login-form").addEventListener("submit", function (event) {
    event.preventDefault();  // Formun gönderilmesini engelle

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const errorMessage = document.getElementById("error-message");

    // Admin ve User giriş bilgilerini kontrol et
    if (username === "admin@example.com" && password === "admin123") {
        // Admin giriş yaptı, admin paneline yönlendir
        window.location.href = "admin-panel.html";  // Admin Paneline yönlendir
    } else if (username === "user@example.com" && password === "user123") {
        // User giriş yaptı, user paneline yönlendir
        window.location.href = "user-panel.html";  // User Paneline yönlendir
    } else {
        // Yanlış kullanıcı adı veya şifre
        errorMessage.textContent = "Hatalı kullanıcı adı veya şifre!";
    }
});
