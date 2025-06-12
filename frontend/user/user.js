document.getElementById("submit").addEventListener("click", async () => {
    const select = document.getElementById("cyberSelect");
    const reportType = select.value;

    // Örnek: device_name hardcoded ya da kullanıcıdan alınabilir
    const deviceName = prompt("Cihaz adını giriniz:");
    if (!deviceName) {
        alert("Lütfen cihaz adı girin!");
        return;
    }

    const resultDiv = document.getElementById("result");
    resultDiv.textContent = "Yükleniyor...";

    try {
        // URL'yi oluşturuyoruz
        const url = `http://127.0.0.1:5000/${reportType}?device_name=${encodeURIComponent(deviceName)}`;
        const response = await fetch(url); // Asenkron veri isteği

        if (!response.ok) {
            const errorText = await response.text();
            resultDiv.textContent = `Hata: ${errorText}`;
            return;
        }

        const data = await response.json(); // JSON verisini alıyoruz

        resultDiv.textContent = JSON.stringify(data, null, 2);

        // Eğer 'device-tracker' ise, Excel dosyası olarak indirme işlemi yap
        if (reportType === "device-tracker") {
            console.log(data)
            await exportToExcel(data); // Excel'e dönüştürme işlemini bekliyoruz
        }


    } catch (error) {
        resultDiv.textContent = `İstek sırasında hata: ${error.message}`;
    }
});

async function exportToExcel(data) {
    const geo_info = data['geo_info'];

    const data_dict = {
        "alive": data["alive"],
        "ip": data["ip"],
        "geo_info_city": geo_info["city"],
        "geo_info_country": geo_info["country"],
        "geo_info_ip": geo_info["ip"],
        "geo_info_loc": geo_info["loc"],
        "geo_info_org": geo_info["org"],
        "geo_info_postal": geo_info["postal"],
        "geo_info_readme": geo_info["readme"],
        "geo_info_region": geo_info["region"],
        "geo_info_timezone": geo_info["timezone"],
        "open_ports": data["open_ports"].join(", ")
    };

    const ws = XLSX.utils.json_to_sheet([data_dict]);

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Device Report");

    XLSX.writeFile(wb, "device_report.xlsx");
}
