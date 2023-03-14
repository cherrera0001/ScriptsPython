import socket
from multiprocessing import Pool
from tqdm import tqdm

# Define el rango de direcciones IP a escanear
ip_base = "192.168.1."
# Define el rango de puertos a escanear
port_range = range(1, 1025)

def scan_port(port):
    results = []

    for ip in range(1, 255):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.settimeout(1)

            try:
                client.connect((ip_base + str(ip), port))
                client.sendall(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
                response = client.recv(4096)

                if b"HTTP" in response:
                    service = "HTTP"
                elif b"SSH" in response:
                    service = "SSH"
                elif b"SMTP" in response:
                    service = "SMTP"
                else:
                    service = "Unknown"

                result = {
                    "ip": ip_base + str(ip),
                    "port": port,
                    "service": service
                }
                results.append(result)

                print(f"IP: {result['ip']}, Port: {result['port']}, Service: {result['service']}")

            except:
                pass

    return results

if __name__ == '__main__':
    results = []

    with Pool(processes=4) as pool:
        for result in tqdm(pool.imap_unordered(scan_port, port_range), total=len(port_range)):
            results.extend(result)
