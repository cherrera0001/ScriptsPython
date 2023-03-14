#Test to scan all ip on range net.

import socket

# define el rango de direcciones IP a escanear
ip_range = "192.168.1."

# define el rango de puertos a escanear
port_range = range(1, 1025)

# crea una lista para almacenar los resultados
results = []

# itera sobre las direcciones IP y los puertos a escanear
for ip in range(1, 255):
    for port in port_range:
        # crea un objeto socket
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # establece el tiempo de espera de conexión en 1 segundo
        client.settimeout(1)
        
        # intenta conectarse al puerto especificado en la dirección IP actual
        try:
            client.connect((ip_range + str(ip), port))
            
            # envía un mensaje de solicitud al servicio
            client.sendall(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
            
            # recibe la respuesta del servicio
            response = client.recv(4096)

        # analiza la respuesta para determinar el servicio que está en ejecución
        if "HTTP" in response:
           service = "HTTP"
        elif "SSH" in response:
            service = "SSH"
        elif "SMTP" in response:
            service = "SMTP"
        else:
            service = "Unknown"
            
            # guarda el resultado en la lista de resultados
            result = {
                "ip": ip_range + str(ip),
                "port": port,
                "service": service
            }
            results.append(result)
            
            client.close()
            
        except:
            pass

# imprime los resultados
for result in results:
    print(result)

