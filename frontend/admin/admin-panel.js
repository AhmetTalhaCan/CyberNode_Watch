document.addEventListener("DOMContentLoaded", async () => {
    try {
        // API'ye istek gönder
        const response = await fetch("http://127.0.0.1:5000/get-devices");

        if (!response.ok) {
            throw new Error("Veri alınamadı.");
        }

        // JSON verisini al
        const data = await response.json();

        // Veriyi panelde göster
        displayAdminData(data);

    } catch (error) {
        console.error("Veri çekilirken hata oluştu:", error);
    }

    // Yeni kullanıcı ekleme butonuna tıklanınca formu göster
    document.getElementById("add-user-btn").addEventListener("click", () => {
        document.getElementById("add-user-form").classList.remove("hidden");
    });

    document.getElementById("delete-user-btn").addEventListener("click", () => {
        document.getElementById("delete-user-form").classList.remove("hidden");
    });

    // İptal butonuna tıklayınca formu gizle ve sıfırla
    document.getElementsByClassName("cancel-user")[0].addEventListener("click", () => {
        document.getElementById("add-user-form").classList.add("hidden");
        document.getElementById("device-name").value = '';
        document.getElementById("ip-address").value = '';
    });

    document.getElementsByClassName("cancel-user")[1].addEventListener("click", () => {
        document.getElementById("delete-user-form").classList.add("hidden");
        document.getElementById("device-name").value = '';
        document.getElementById("ip-address").value = '';
    });

    // Kullanıcı eklemek için formu gönder
    document.getElementById("submit-user").addEventListener("click", async () => {
        const deviceName = document.getElementById("add-device-name").value;
        const ipAddress = document.getElementById("ip-address").value;

        if (!deviceName || !ipAddress) {
            alert("Lütfen tüm alanları doldurun.");
            return;
        }

        const newUser = {
            desktopName: deviceName,
            ip_address: ipAddress
        };

        try {
            // API'ye yeni kullanıcıyı gönder
            const response = await fetch("http://127.0.0.1:5000/add-device", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(newUser)
            });

            if (!response.ok) {
                throw new Error("Kullanıcı eklenemedi.");
            }

            // Yeni kullanıcı eklenirse formu gizle ve tabloyu güncelle
            document.getElementById("add-user-form").classList.add("hidden");
            document.getElementById("device-name").value = '';
            document.getElementById("ip-address").value = '';

            // Yeni kullanıcı ekledikten sonra güncel verileri tekrar çek
            const data = await response.json();
            displayAdminData(data);
        } catch (error) {
            console.error("Yeni kullanıcı eklenirken hata oluştu:", error);
        }
    });

    document.getElementById("delete-user").addEventListener("click", async () => {
        const deviceName = document.getElementById("delete-device-name").value;

        if (!deviceName) {
            alert("Lütfen silinecek cihazın adını girin.");
            return;
        }

        try {
            // Cihazı silmek için DELETE isteği gönder
            const response = await fetch(`http://127.0.0.1:5000/delete-device/${deviceName}`, {
                method: "DELETE",
            });

            if (!response.ok) {
                throw new Error("Cihaz silinemedi.");
            }

            // Cihaz silindikten sonra formu gizle ve inputu sıfırla
            document.getElementById("delete-user-form").classList.add("hidden");
            document.getElementById("device-name").value = '';

            // Cihaz silindikten sonra güncel verileri tekrar çek
            const data = await response.json();
            displayAdminData(data);
        } catch (error) {
            console.error("Cihaz silinirken hata oluştu:", error);
        }
    });
});

// Cihazı silme fonksiyonu
async function deleteDevice(desktopName) {
    try {
        const response = await fetch(`http://127.0.0.1:5000/delete-device/${desktopName}`, {
            method: "DELETE",
        });

        if (!response.ok) {
            throw new Error("Cihaz silinemedi.");
        }

        // Cihaz silindikten sonra güncel verileri tekrar çek
        const data = await response.json();
        displayAdminData(data);
    } catch (error) {
        console.error("Cihaz silinirken hata oluştu:", error);
    }
}

// Veriyi HTML'e yerleştir
function displayAdminData(devices) {
    const table = document.getElementById("users-table");

    // Tabloyu temizle
    table.innerHTML = "";

    // Tablo başlıkları
    const headerRow = document.createElement("tr");
    headerRow.innerHTML = `
        <th>ID</th>
        <th>Desktop Name</th>
        <th>Ip Address</th>
    `;
    table.appendChild(headerRow);

    // Verileri tabloya ekle
    devices.forEach(device => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${device.id}</td>
            <td>${device.desktopName}</td>
            <td>${device.ip_address}</td>
        `;
        table.appendChild(row);
    });
}
