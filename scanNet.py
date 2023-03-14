import socket
from multiprocessing import Pool

# Define el rango de direcciones IP a escanear
ip_base = "172.16.1."
# Define el rango de puertos a escanear
port_range = range(1, 1025)

def scan_port(port):
    # Crea una lista para almacenar los resultados
    results = []
    
    # Itera sobre las direcciones IP y los puertos a escanear
    for ip in range(1, 255):
        # Crea un objeto socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            # Establece el tiempo de espera de conexión en 1 segundo
            client.settimeout(1)
            
            # Intenta conectarse al puerto especificado en la dirección IP actual
            try:
                client.connect((ip_base + str(ip), port))
                
                # Envía un mensaje de solicitud al servicio
                client.sendall(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
                
                # Recibe la respuesta del servicio
                response = client.recv(4096)

                # Analiza la respuesta para determinar el servicio que está en ejecución
                if b"HTTP" in response:
                    service = "HTTP"
                elif b"SSH" in response:
                    service = "SSH"
                elif b"SMTP" in response:
                    service = "SMTP"
                else:
                    service = "Unknown"
                
                # Guarda el resultado en la lista de resultados
                result = {
                    "ip": ip_base + str(ip),
                    "port": port,
                    "service": service
                }
                results.append(result)

            except:
                pass

    return results

if __name__ == '__main__':
    # Crea un grupo de procesos para escanear los puertos
    with Pool(processes=4) as pool:
        # Escanea los puertos en paralelo utilizando los procesos del grupo
        results = pool.map(scan_port, port_range)

    # Concatena los resultados de los escaneos de cada puerto
    results = [item for sublist in results for item in sublist]

    # Imprime los resultados una vez que se completa el escaneo
    for result in results:
        print(result)
