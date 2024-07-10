import argparse
import configparser
import requests
import logging
from urllib.parse import urljoin, urlparse
import codecs
import mmh3
import shodan
import dns.resolver
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

# Configuración inicial de logging
logging.basicConfig(filename='faviconfrenzy.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s:%(message)s')

def main():
    parser = argparse.ArgumentParser(prog='faviconfrenzy', description='Busca el favicon de una URL proporcionada, calcula su hash y lo envía a Shodan para análisis.')
    parser.add_argument('-u', '--url', type=str, required=True, help='URL para buscar el FavIcon.')
    parser.add_argument('-ak', '--addshodankey', dest='shodankey', type=str, help='Almacena o reemplaza la clave Shodan en el archivo de configuración.')
    parser.add_argument('-t', '--topresults', type=int, default=10, help='Número máximo de resultados a mostrar, por defecto es 10.')
    parametros = parser.parse_args()

    # Agregar esquema por defecto si falta
    url = parametros.url
    if not urlparse(url).scheme:
        url = 'http://' + url

    session = requests.Session()  # Uso de sesiones para optimizar las solicitudes HTTP
    icon_paths = get_favicon_paths(session, url)
    if icon_paths:
        for path in icon_paths:
            if verify_favicon(session, path):
                logging.info(f'Favicon encontrado en: {path}')
                favicon, hash = get_favicon(session, path)
                if hash:
                    logging.info(f'hash: {hash}')
                    if parametros.shodankey:
                        store_shodan_key(parametros.shodankey)
                    shodan_query(hash, parametros.topresults)
                    discover_real_ip(url)
                    break
                else:
                    logging.warning('No se encontró hash para el favicon.')
    else:
        logging.warning('No se encontró favicon.')

def get_favicon_paths(session, url):
    """
    Obtiene las posibles rutas de favicons desde una URL.

    Args:
        session (requests.Session): La sesión de requests.
        url (str): La URL del sitio web.

    Returns:
        list: Lista de posibles URLs de favicons.
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Asegurar que se lanza una excepción para errores HTTP
    except requests.RequestException as e:
        logging.error(f'Error al obtener la página principal: {e}')
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    icon_paths = set()
    for link in soup.find_all('link', rel=['icon', 'shortcut icon', 'apple-touch-icon']):
        if 'href' in link.attrs:
            icon_paths.add(urljoin(url, link['href']))

    # Agregar rutas comunes y variaciones de favicons
    common_paths = [
        'favicon.ico', 'FAVICON.ICO', 'favicon.svg', 'FAVICON.SVG', 'favicon-512.png', 'favicon-512.PNG',
        'favicon-192.png', 'favicon-192.PNG', 'apple-touch-icon.png', 'apple-touch-icon.PNG',
        'static/favicon.ico', 'static/FAVICON.ICO', 'static/favicon.svg', 'static/FAVICON.SVG',
        'static/favicon-512.png', 'static/FAVICON-512.PNG', 'static/favicon-192.png', 'static/FAVICON-192.PNG',
        'static/apple-touch-icon.png', 'static/APPLE-TOUCH-ICON.PNG', 'assets/img/favicon.ico', 'assets/img/FAVICON.ICO',
        'assets/img/favicon.svg', 'assets/img/FAVICON.SVG', 'assets/img/favicon-512.png', 'assets/img/FAVICON-512.PNG',
        'assets/img/favicon-192.png', 'assets/img/FAVICON-192.PNG', 'assets/img/apple-touch-icon.png', 'assets/img/APPLE-TOUCH-ICON.PNG'
    ]

    for path in common_paths:
        icon_paths.add(urljoin(url, path))

    return list(icon_paths)

def verify_favicon(session, icon_url):
    """
    Verifica si el archivo en la URL proporcionada es un favicon válido.

    Args:
        session (requests.Session): La sesión de requests.
        icon_url (str): La URL del posible favicon.

    Returns:
        bool: True si el archivo es un favicon válido, False en caso contrario.
    """
    try:
        response = session.get(icon_url, timeout=10)
        response.raise_for_status()  # Asegurar que se lanza una excepción para errores HTTP
        img = Image.open(BytesIO(response.content))
        if img.format in ['ICO', 'PNG', 'SVG']:
            logging.info(f'Favicon válido encontrado en: {icon_url}')
            return True
        return False
    except Exception as e:
        logging.error(f'Error al verificar favicon: {e}')
        return False

def get_favicon(session, absoluteIconPath):
    """
    Obtiene el favicon desde la URL proporcionada y calcula su hash.

    Args:
        session (requests.Session): La sesión de requests.
        absoluteIconPath (str): La URL del favicon.

    Returns:
        tuple: Contenido del favicon en base64 y su hash.
    """
    try:
        response = session.get(absoluteIconPath, timeout=10)
        response.raise_for_status()  # Asegurar que se lanza una excepción para errores HTTP
        favicon = codecs.encode(response.content, 'base64')
        hash = mmh3.hash(favicon)
        return favicon, hash
    except requests.RequestException as e:
        logging.error(f'Error al obtener hash de favicon: {e}')
        return None, None

def shodan_query(hash, topresults):
    """
    Realiza una consulta a Shodan utilizando el hash del favicon.

    Args:
        hash (int): El hash del favicon.
        topresults (int): Número máximo de resultados a mostrar.
    """
    api_key = get_shodan_key()
    if api_key:
        api = shodan.Shodan(api_key)
        query = f'http.favicon.hash:{hash}'
        try:
            results = api.search(query, limit=topresults)
            if not results['matches']:
                logging.warning('No se encontraron resultados en Shodan')
            else:
                for count, host in enumerate(results['matches'], start=1):
                    print(f'Resultado {count}:')
                    print(f'IP: {host["ip_str"]}')
                    print(f'Port: {host["port"]}')
                    print(f'Hostnames: {host.get("hostnames")}')
                    print(f'Location: {host["location"]}')
                    print('-' * 60)
        except shodan.APIError as e:
            logging.error(f'Error en consulta Shodan: {e}')
    else:
        logging.warning('Clave API de Shodan no encontrada')

def discover_real_ip(url):
    """
    Descubre la IP real detrás de un dominio.

    Args:
        url (str): La URL del sitio web.
    """
    domain = url.split("//")[-1].split("/")[0]
    try:
        answers = dns.resolver.resolve(domain, 'A')
        for rdata in answers:
            print(f'Possible real IP address: {rdata}')
    except dns.resolver.NXDOMAIN:
        logging.warning(f'No se pudo resolver el dominio {domain}')
    except dns.resolver.NoAnswer:
        logging.warning(f'No se encontró respuesta para el dominio {domain}')
    except dns.resolver.Timeout:
        logging.warning(f'Tiempo de espera agotado para el dominio {domain}')
    except Exception as e:
        logging.error(f'Error al buscar IP real: {e}')

def store_shodan_key(shodankey):
    """
    Almacena la clave API de Shodan en un archivo de configuración.

    Args:
        shodankey (str): La clave API de Shodan.
    """
    config = configparser.ConfigParser()
    config['SHODAN'] = {'key': shodankey}
    try:
        with open('faviconfrenzy.ini', 'w') as configfile:
            config.write(configfile)
            logging.info('Clave Shodan almacenada con éxito')
    except IOError as e:
        logging.error(f'Error al almacenar clave Shodan: {e}')

def get_shodan_key():
    """
    Obtiene la clave API de Shodan desde el archivo de configuración.

    Returns:
        str: La clave API de Shodan, o None si no se encuentra.
    """
    config = configparser.ConfigParser()
    try:
        config.read('faviconfrenzy.ini')
        return config.get('SHODAN', 'key', fallback=None)
    except configparser.Error as e:
        logging.error(f'Error al leer clave Shodan: {e}')
        return None

if __name__ == '__main__':
    main()
