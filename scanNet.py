import socket
from multiprocessing import Pool
from tqdm import tqdm

# Define el rango de direcciones IP a escanear
ip_base = "192.168.1."
# Define el rango de puertos a escanear
port_range = range(1, 1025)
# Define el rango de IPs a escanear
ip_range = range(1, 255)
# Tiempo de espera para la conexión
timeout = 1

def check_service(response):
    if b"HTTP" in response:
        return "HTTP"
    elif b"SSH" in response:
        return "SSH"
    elif b"SMTP" in response:
        return "SMTP"
    else:
        return "Unknown"

def scan_ip_port(ip, port):
    results = []
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.settimeout(timeout)
            client.connect((f"{ip_base}{ip}", port))
            client.sendall(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
            response = client.recv(4096)
            service = check_service(response)
            result = {
                "ip": f"{ip_base}{ip}",
                "port": port,
                "service": service
            }
            results.append(result)
            print(f"IP: {result['ip']}, Port: {result['port']}, Service: {result['service']}")
    except socket.timeout:
        pass  # Omitir tiempo de espera de conexión
    except socket.error as e:
        pass  # Omitir otros errores de socket
    return results

def scan_port(port):
    results = []
    for ip in ip_range:
        results.extend(scan_ip_port(ip, port))
    return results

if __name__ == '__main__':
    results = []

    with Pool(processes=4) as pool:
        for result in tqdm(pool.imap_unordered(scan_port, port_range), total=len(port_range)):
            results.extend(result)
