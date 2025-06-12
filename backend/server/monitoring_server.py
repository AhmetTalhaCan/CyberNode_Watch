import json
import logging
import os
from flask import Flask, request, jsonify
import mysql.connector as mysql
from datetime import datetime
from flask_cors import CORS
import psutil
import requests

# Log ayarları
logging.basicConfig(filename='server.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# config.json dosyasını okuma
def load_config():
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, "r") as file:
            config = json.load(file)
        
        required_keys = ["server_host", "server_port", "db_host", "db_port", "db_user", "db_password", "db_name"]
        for key in required_keys:
            if key not in config:
                logging.error(f"config.json dosyasında '{key}' eksik!")
                raise KeyError(f"'{key}' yapılandırma dosyasından eksik")
        
        return config
    except FileNotFoundError:
        logging.error("config.json dosyası bulunamadı!")
        raise
    except json.JSONDecodeError:
        logging.error("config.json dosyası geçersiz formatta!")
        raise
    except KeyError as e:
        logging.error(f"Yapılandırma hatası: {e}")
        raise

# Yapılandırmayı yükleyelim
config = load_config()

# Veritabanı bağlantısı oluştur
def get_db_connection():
    try:
        return mysql.connect(
            host=config['db_host'],
            port=config['db_port'],
            user=config['db_user'],
            password=config['db_password'],
            database=config['db_name']
        )
    except mysql.Error as e:
        logging.error(f"Veritabanı bağlantı hatası: {str(e)}")
        raise

def get_global_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        response.raise_for_status()
        data = response.json()
        ip_address = data.get("ip", None)
        return ip_address
    except requests.RequestException as e:
        print(f"IP alınırken hata: {e}")
        return None

# Kullanım örneği:
ip_address = get_global_ip()
print(f"Global IP adresi: {ip_address}")

# Flask uygulaması
app = Flask(__name__)
CORS(app)

@app.route('/receive_device_info', methods=['POST'])
def receive_device_info():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Veri alınamadı"}), 400

        required_fields = ["system_info", "memory_info", "cpu_info", "disk_info", "os_info", "installed_software", "uptime", "boot_time"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"'{field}' alanı eksik"}), 400    

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM devices WHERE ip_address = %s", (ip_address,))
        device_exists = cursor.fetchone()

        if device_exists:
            desktopName = data['desktopName']

            # SYSTEM INFO
            system_info = data['system_info']
            cursor.execute("""
                INSERT INTO system_info (desktopName, `system`, node_name, `release`, version, machine, processor)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                desktopName,
                system_info["system"],
                system_info["node_name"],
                system_info["release"],
                system_info["version"],
                system_info["machine"],
                system_info["processor"]
            ))

            # MEMORY INFO
            memory_info = data['memory_info']
            cursor.execute("""
                INSERT INTO memory_info (desktopName, total_memory, available_memory, used_memory, memory_percent)
                VALUES (%s, %s, %s, %s, %s)
                """, (
                desktopName,
                memory_info["total_memory"],
                memory_info["available_memory"],
                memory_info["used_memory"],
                memory_info["memory_percent"]
            ))

            # CPU INFO
            cpu_info = data['cpu_info']
            cursor.execute("""
                INSERT INTO cpu_info (desktopName, cpu_percent)
                VALUES (%s, %s)
            """, (
                desktopName,
                cpu_info["cpu_percent"]
            ))

            # DISK INFO
            disk_info = data['disk_info']
            cursor.execute("""
                INSERT INTO disk_info (desktopName, total_disk, used_disk, free_disk, disk_percent)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                desktopName,
                disk_info["total_disk"],
                disk_info["used_disk"],
                disk_info["free_disk"],
                disk_info["disk_percent"]
            ))

            # OS INFO
            os_info = data['os_info']
            cursor.execute("""
                INSERT INTO os_info (desktopName, os_name, os_version, os_release)
                VALUES (%s, %s, %s, %s)
            """, (
                desktopName,
                os_info["os_name"],
                os_info["os_version"],
                os_info["os_release"]
            ))

            # INSTALLED SOFTWARE
            installed_software_list = data['installed_software']

            for software in installed_software_list:
                name = software[0][:50]
                version = software[1][:50]

                cursor.execute("SELECT COUNT(*) FROM software_info WHERE name = %s AND desktopName = %s", (name, desktopName))
                (count,) = cursor.fetchone()
                if count == 0:
                    cursor.execute("""
                        INSERT IGNORE INTO software_info (desktopName, name, version)
                        VALUES (%s, %s, %s)
                        """, (
                        desktopName,
                        name,
                        version
                    ))

            conn.commit()

            return jsonify({"message": "Tüm veriler başarıyla kaydedildi"}), 200

    except mysql.Error as e:
        print(f"Veritabanı işlemi hatası: {e}")
        return jsonify({"error": "Veritabanı işlemi hatası"}), 500
    except Exception as e:
        print(f"Bilinmeyen bir hata oluştu: {e}")
        return jsonify({"error": "Bilinmeyen bir hata oluştu"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)