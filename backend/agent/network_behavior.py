from scapy.all import sniff, IP, TCP, UDP, ICMP, Ether, Raw
from datetime import datetime

def packet_callback(pkt):
    print("="*80)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Yeni Paket Alındı")

    if Ether in pkt:
        print(f"MAC => {pkt[Ether].src} → {pkt[Ether].dst} | Tip: {pkt[Ether].type}")

    if IP in pkt:
        ip_layer = pkt[IP]
        print(f"IP => {ip_layer.src} → {ip_layer.dst} | Protokol: {ip_layer.proto}")

    if TCP in pkt:
        tcp_layer = pkt[TCP]
        print(f"TCP => Port {tcp_layer.sport} → {tcp_layer.dport} | Flags: {tcp_layer.flags}")

    elif UDP in pkt:
        udp_layer = pkt[UDP]
        print(f"UDP => Port {udp_layer.sport} → {udp_layer.dport}")

    elif ICMP in pkt:
        print("ICMP paketi tespit edildi.")

    if Raw in pkt:
        payload = pkt[Raw].load
        try:
            printable = payload.decode(errors="ignore")
            print(f"Veri: {printable[:100]}...")
        except:
            print("Veri çözümlenemedi.")

    print("="*80)

def start_sniffing():
    print("🔍 Ağ izleniyor... (Ctrl+C ile durdur)")
    sniff(prn=packet_callback, store=False)

if __name__ == "__main__":
    start_sniffing()
