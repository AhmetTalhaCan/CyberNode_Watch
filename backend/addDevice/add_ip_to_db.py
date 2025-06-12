import mysql.connector
import platform
import os
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Config verisini doğrudan buraya yazıyoruz
config = {
    "server_host": "0.0.0.0",
    "server_port": 5000,
    "db_host": "biomrg5uorif5yzexef3-mysql.services.clever-cloud.com",
    "db_port": 3306,
    "db_user": "us7i8fe3s5nxpeoz",
    "db_password": "QvIoI1LDJft3x04qwgbZ",
    "db_name": "biomrg5uorif5yzexef3",
    "log_file": "server.log"
}

# Flask Uygulaması
app = Flask(__name__)
CORS(app)

# Veritabanına bağlanma
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host=config["db_host"],
            port=config["db_port"],
            user=config["db_user"],
            password=config["db_password"],
            database=config["db_name"]
        )
        return connection
    except mysql.connector.Error as e:
        logging.error(f"Veritabanına bağlanırken hata: {e}")
        return None

# PowerShell komutunu çalıştırarak public IP'yi al
def fetch_public_ip():
    try:
        ps_command = (
            "nslookup myip.opendns.com resolver1.opendns.com | "
            "Where-Object { $_ -match 'Address: ' } | Select-Object -Last 1"
        )
        result = subprocess.run(
            ["powershell", "-Command", ps_command],
            capture_output=True, text=True, check=True
        )
        output = result.stdout.strip()
        ip = output.replace("Address: ", "").strip()
        return ip
    except Exception as e:
        logging.error(f"IP alma hatası: {e}")
        return None

# Veritabanına cihaz ekleme
def insert_device_into_db(desktop_name, ip_address):
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Aynı desktopName'in var olup olmadığını kontrol et
            check_query = "SELECT COUNT(*) FROM devices WHERE desktopName = %s"
            cursor.execute(check_query, (desktop_name,))
            result = cursor.fetchone()

            # Eğer aynı desktopName varsa, ekleme yapma
            if result[0] > 0:
                logging.warning(f"Cihaz zaten mevcut: {desktop_name}")
                return  # Aynı cihaz zaten var, işlemi sonlandır
            
            # Cihaz ekleme işlemi
            insert_query = "INSERT INTO devices (desktopName, ip_address) VALUES (%s, %s)"
            cursor.execute(insert_query, (desktop_name, ip_address))
            connection.commit()
            logging.info(f"Cihaz başarıyla eklendi: {desktop_name} - {ip_address}")
        
        except mysql.connector.Error as e:
            logging.error(f"Veritabanına cihaz eklerken hata: {e}")
        
        finally:
            cursor.close()
            connection.close()

# Cihaz Ekleme API
@app.route('/add-device', methods=['POST'])
def add_device():
    data = request.json
    desktop_name = data.get('desktopName')
    ip_address = data.get('ip_address')

    if not desktop_name or not ip_address:
        return jsonify({"error": "Desktop Name ve IP Address gereklidir!"}), 400

    insert_device_into_db(desktop_name, ip_address)
    return jsonify({"message": "Cihaz başarıyla eklendi!"}), 201

# Cihaz Silme API
@app.route('/delete-device/<device_name>', methods=['DELETE'])
def delete_device(device_name):
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()
            delete_query = "DELETE FROM devices WHERE desktopName = %s"
            cursor.execute(delete_query, (device_name,))
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({"message": "Cihaz başarıyla silindi!"}), 200
        except mysql.connector.Error as e:
            logging.error(f"Veritabanında cihaz silme hatası: {e}")
            return jsonify({"error": "Veritabanı hatası"}), 500
    return jsonify({"error": "Veritabanına bağlantı sağlanamadı!"}), 500

# Cihazları Listeleme API
@app.route('/get-devices', methods=['GET'])
def get_devices():
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM devices")
            devices = cursor.fetchall()
            cursor.close()
            connection.close()
            return jsonify(devices), 200
        except mysql.connector.Error as e:
            logging.error(f"Veritabanı hata: {e}")
            return jsonify({"error": "Veritabanı hatası"}), 500
    return jsonify({"error": "Veritabanına bağlantı sağlanamadı!"}), 500

# Başlangıçta cihaz bilgilerini veritabanına ekle
def initial_device_setup():
    ip_data = fetch_public_ip()
    if ip_data:
        desktop_name = f"{platform.node()}-{os.getlogin()}"
        insert_device_into_db(desktop_name, ip_data)
    else:
        logging.error("Public IP alınamadı.")

if __name__ == "__main__":
    initial_device_setup()  # Sunucu başlatıldığında cihazı ekle
    app.run(debug=True, host=config["server_host"], port=config["server_port"])