import os
import hashlib
import json
import requests
import mysql.connector as mysql
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# config.json dosyasını okuma
def load_config():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, "config.json")

        with open(config_path, "r") as file:
            config = json.load(file)
        
        required_keys = ["db_host", "db_port", "db_user", "db_password", "db_name", "virustotal_api_key"]
        for key in required_keys:
            if key not in config:
                raise KeyError(f"'{key}' yapılandırma dosyasından eksik")
        
        return config
    except Exception as e:
        logging.error(f"Yapılandırma hatası: {e}")
        raise

# Dosyanın SHA-256 hash'ini hesapla
def get_file_sha256(filepath):
    try:
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        logging.warning(f"Dosya okunamadı: {filepath}, Hata: {e}")
        return None

# VirusTotal hash sorgusu
def query_virustotal(file_hash, api_key):
    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
    headers = {
        "x-apikey": api_key
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        logging.info(f"VirusTotal'da sonuç bulunamadı: {file_hash}")
        return None
    else:
        logging.error(f"VirusTotal API hatası ({response.status_code}): {response.text}")
        return None

# Yazılımları tarayan fonksiyon
def check_software_with_virustotal(installed_software, api_key, max_scan=10):
    search_paths = ["C:\\Program Files", "C:\\Program Files (x86)"]
    suspicious_software = []
    scanned_hashes = set()
    scanned_files = 0

    for name, version in installed_software:
        name_lower = name.lower()
        found = False

        for base_path in search_paths:
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    if file.lower().endswith(".exe") and name_lower in file.lower():
                        full_path = os.path.join(root, file)
                        file_hash = get_file_sha256(full_path)

                        if file_hash and file_hash not in scanned_hashes:
                            logging.info(f"{full_path} dosyası taranıyor...")
                            scanned_hashes.add(file_hash)
                            scanned_files += 1

                            result = query_virustotal(file_hash, api_key)
                            if result:
                                stats = result.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                                if stats.get("malicious", 0) > 0:
                                    logging.warning(f"[!] Şüpheli Yazılım Tespit Edildi: {full_path}")
                                    suspicious_software.append({
                                        "file_path": full_path,
                                        "sha256": file_hash,
                                        "malicious_count": stats["malicious"],
                                        "vt_permalink": f"https://www.virustotal.com/gui/file/{file_hash}"
                                    })
                            found = True
                            break

                if found or scanned_files >= max_scan:
                    break
            if scanned_files >= max_scan:
                break

        if scanned_files >= max_scan:
            logging.info("Maksimum tarama sınırına ulaşıldı.")
            break

    return suspicious_software

# Flask API endpointe'leri
app = Flask(__name__)
CORS(app)

@app.route('/software-threat-scanner', methods=['GET'])
def software_threat_scanner():
    try:
        # Kullanıcıdan gelen cihaz ismi (veya başka parametreler) al
        device_name = request.args.get('device_name')
        if not device_name:
            return jsonify({"error": "Cihaz adı parametre olarak verilmelidir"}), 400

        # Yapılandırmayı yükle
        config = load_config()
        api_key = config.get("virustotal_api_key")

        # Veritabanına bağlan
        db = mysql.connect(
            host=config['db_host'],
            port=config['db_port'],
            user=config['db_user'],
            password=config['db_password'],
            database=config['db_name']
        )
        cursor = db.cursor()

        # Yazılım verilerini al
        cursor.execute("SELECT id, desktopName, name, version FROM software_info WHERE desktopName LIKE %s", ('%' + device_name + '%',))
        rows = cursor.fetchall()
        installed_software = [(row[2], row[3]) for row in rows]

        # Virustotal kontrolü
        if not api_key:
            return jsonify({"error": "API anahtarı config.json'da tanımlı değil!"}), 500

        suspicious = check_software_with_virustotal(installed_software, api_key)

        # Sonuçları JSON formatında dön
        if suspicious:
            return jsonify(suspicious), 200
        else:
            return jsonify({"message": "Şüpheli yazılım tespit edilmedi."}), 200

    except Exception as e:
        logging.error(f"API Hatası: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # API'yi başlat
    app.run(host='0.0.0.0', port=5000)