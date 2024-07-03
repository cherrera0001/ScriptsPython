import argparse
import configparser
import requests
import logging
from urllib.parse import urljoin
import codecs
import mmh3
import shodan
import dns.resolver

# Configuración inicial de logging
logging.basicConfig(level=logging.INFO)

def main():
    parser = argparse.ArgumentParser(prog='faviconfrenzy', description='Busca el favicon de una URL proporcionada, calcula su hash y lo envía a Shodan para análisis.')
    parser.add_argument('-u', '--url',  type=str, required=True, help='URL para buscar el FavIcon.')
    parser.add_argument('-ak', '--addshodankey', dest='shodankey', type=str, help='Almacena o reemplaza la clave Shodan en el archivo de configuración.')
    parser.add_argument('-t', '--topresults', type=int, default=10, help='Número máximo de resultados a mostrar, por defecto es 10.')
    parametros = parser.parse_args()

    session = requests.Session()  # Uso de sesiones para optimizar las solicitudes HTTP
    absoluteIconPath = getFavIconPath(session, parametros.url)
    if absoluteIconPath:
        logging.info(f'url: {parametros.url}')
        logging.info(f'FavIconPath: {absoluteIconPath}')
        favicon, hash = getfavicon(absoluteIconPath)
        if hash:
            logging.info(f'hash: {hash}')
            if parametros.shodankey:
                store_shodan_key(parametros.shodankey)
            shodanQuery(hash, parametros.topresults, session)
            discover_real_ip(parametros.url)
        else:
            logging.warning('No se encontró favicon.')
    else:
        logging.warning('No se encontró favicon.')

def getFavIconPath(session, url):
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    favicon_paths = ['', 'favicon.ico', 'html_public/favicon.ico']
    for path in favicon_paths:
        try:
            icon_url = urljoin(url, path) if path else url
            response = session.get(icon_url, headers=headers, timeout=10)
            if response.status_code == 200:
                logging.info(f'Favicon encontrado en: {icon_url}')
                return icon_url
        except requests.RequestException as e:
            logging.error(f'Error al obtener favicon: {e}')
    logging.warning('No se encontró favicon en las rutas probadas')
    return None

def getfavicon(absoluteIconPath):
    try:
        response = requests.get(absoluteIconPath, timeout=10)
        favicon = codecs.encode(response.content, 'base64')
        hash = mmh3.hash(favicon)
        return favicon, hash
    except requests.RequestException as e:
        logging.error(f'Error al obtener hash de favicon: {e}')
        return None, None

def shodanQuery(hash, topresults, session):
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
    config = configparser.ConfigParser()
    config['SHODAN'] = {'key': shodankey}
    try:
        with open('faviconfrenzy.ini', 'w') as configfile:
            config.write(configfile)
            logging.info('Clave Shodan almacenada con éxito')
    except IOError as e:
        logging.error(f'Error al almacenar clave Shodan: {e}')

def get_shodan_key():
    config = configparser.ConfigParser()
    try:
        config.read('faviconfrenzy.ini')
        return config.get('SHODAN', 'key', fallback=None)
    except configparser.Error as e:
        logging.error(f'Error al leer clave Shodan: {e}')
        return None

if __name__ == '__main__':
    main()
                                                   
