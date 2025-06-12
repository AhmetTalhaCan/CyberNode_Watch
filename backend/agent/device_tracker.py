import socket
import subprocess
import requests
import json
import mysql.connector
import logging
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# Logging ayarı
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Yapılandırmayı yükle
def load_config():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, "config.json")

        with open(config_path, "r") as file:
           config = json.load(file)

        required_keys = ["db_host", "db_port", "db_user", "db_password", "db_name"]
        for key in required_keys:
            if key not in config:
                raise KeyError(f"'{key}' yapılandırma dosyasında eksik.")

        return config
    except Exception as e:
        logging.error(f"Yapılandırma hatası: {e}")
        raise

# Veritabanından IP'yi çek
def get_device_ip(config, device_name):
    try:
        db = mysql.connector.connect(
            host=config['db_host'],
            port=config['db_port'],
            user=config['db_user'],
            password=config['db_password'],
            database=config['db_name']
        )
        cursor = db.cursor(buffered=True)
        cursor.execute("SELECT ip_address FROM devices WHERE desktopName = %s", (device_name,))
        row = cursor.fetchone()
        return row[0] if row else None

    except mysql.connector.Error as err:
        logging.error(f"Veritabanı hatası: {err}")
        return None

    finally:
        try:
            cursor.close()
            db.close()
        except:
            pass

# IP aktif mi?
def is_host_alive(ip):
    try:
        param = "-n" if os.name == "nt" else "-c"
        result = subprocess.run(["ping", param, "1", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except:
        return False

# Port taraması
def scan_ports(ip, port_range=(1, 1024)):
    open_ports = []
    for port in range(port_range[0], port_range[1] + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.3)
            result = sock.connect_ex((ip, port))
            if result == 0:
                try:
                    sock.send(b'HEAD / HTTP/1.1\r\n\r\n')
                    banner = sock.recv(100).decode(errors="ignore")
                except:
                    banner = ""
                try:
                    service = socket.getservbyport(port, "tcp")
                except:
                    service = "unknown"
                open_ports.append({
                    "port": port,
                    "service": service,
                    "banner": banner.strip()
                })
    return open_ports

# IP konum bilgisi al
def get_ip_info(ip):
    try:
        res = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        return res.json()
    except:
        return {"error": "Konum bilgisi alınamadı"}

# Ana takip işlemi
def track_device(ip):
    alive = is_host_alive(ip)
    geo = get_ip_info(ip)
    ports = scan_ports(ip) if alive else []

    return {
        "ip": ip,
        "alive": alive,
        "geo_info": geo,
        "open_ports": ports
    }

# Flask uygulaması
app = Flask(__name__)
CORS(app)

@app.route('/device-tracker', methods=['GET'])
def device_tracker():
    device_name = request.args.get('device_name')
    if not device_name:
        return jsonify({"error": "device_name parametresi gerekli"}), 400
    
    try:
        config = load_config()
        ip = get_device_ip(config, device_name)
        if not ip:
            return jsonify({"error": "Bu cihaz adına ait IP bulunamadı."}), 404
        
        result = track_device(ip)
        return jsonify(result)
    
    except Exception as e:
        logging.error(f"Hata: {e}")
        return jsonify({"error": "Sunucu hatası"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
