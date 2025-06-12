
# CyberNode Watch

**CyberNode Watch**, ağınızdaki istemci cihazlardan sistem verilerini toplayan, yazılım tehditlerini analiz eden ve kullanıcı dostu bir arayüz ile durumu görselleştiren bir siber güvenlik izleme platformudur.

---

## 🔧 Proje Yapısı

```
CyberNode_Watch/
│
├── backend/
│   ├── addData/
│   │   ├── config.json
│   │   └── send_system_data.py
│   ├── addDevice/
│   │   └── add_ip_to_db.py
│   ├── agent/
│   │   ├── config.json
│   │   ├── device_tracker.py
│   │   ├── network_behavior.py
│   │   └── software_threat_scanner.py
│   └── server/
│       ├── config.json
│       ├── monitoring_server.py
│       └── server.log
│
├── frontend/
│   ├── admin/
│   ├── user/
│   ├── index.html
│   └── style.css
│
├── config.txt
└── README.md
```

---

## 🔍 Özellikler

- ✅ **Ajanlar**: İstemcilerden sistem bilgileri, kurulu yazılımlar, ağ trafiği gibi veriler toplar.
- 🛡️ **Yazılım Tehdit Taraması**: VirusTotal API ile yazılım listelerini tarar.
- 🌐 **Web Arayüzü**: Cihaz durumlarını görselleştiren kullanıcı dostu HTML/CSS arayüz.
- 📡 **Gerçek Zamanlı İzleme**: Ağ davranışlarını canlı olarak analiz eder.

---

## 🚀 Kurulum

### 1. Gereksinimler

- Python 3.9+
- Flask
- `psutil`, `requests`, `scapy`

### 2. Ortam Kurulumu

```bash
git clone https://github.com/AhmetTalhaCan/CyberNode_Watch.git
cd CyberNode_Watch
pip install -r requirements.txt  # Eğer requirements dosyanız varsa
```

### 3. Sunucuyu Başlat

```bash
cd backend/server
python monitoring_server.py
```

### 4. Ajanı Başlat

```bash
cd backend/agent
python device_tracker.py
```

---

## 🌐 Web Arayüzü

Arayüz dosyaları `frontend/` klasöründe bulunur. `index.html` dosyasını doğrudan tarayıcıda açarak kullanılabilir.

---

## 🧪 Test Edilen Özellikler

- [x] Sistem bilgisi toplama
- [x] Ağ davranışı izleme
- [x] Yazılım tehdit kontrolü (VirusTotal)
- [x] Web arayüzü ile görselleştirme

---

## 📚 Kaynaklar

- [VirusTotal API](https://www.virustotal.com/gui/home/search)
- [Scapy Documentation](https://scapy.readthedocs.io)
- [Flask Documentation](https://flask.palletsprojects.com)

---

## 👨‍💻 Geliştirici

**Ahmet Talha Can**  
Bilgisayar Mühendisliği  
Konya Teknik Üniversitesi
