import argparse
import requests
import logging
from urllib.parse import urljoin, urlparse
import codecs
import mmh3
import shodan
import dns.resolver
import os
import subprocess

# Configuración inicial de logging
logging.basicConfig(level=logging.INFO)

# Definir claves API directamente en el script
SECURITYTRAILS_API_KEY = 'tu-key'
SHODAN_API_KEY = 'tu-key'

def main():
    if not SECURITYTRAILS_API_KEY or not SHODAN_API_KEY:
        logging.error('Las claves API de Shodan y SecurityTrails deben estar definidas en las variables de entorno.')
        return

    parser = argparse.ArgumentParser(prog='domainSecurityScan', description='Realiza un análisis de seguridad en un dominio proporcionando.')
    parser.add_argument('-u', '--url', type=str, required=True, help='URL del dominio a analizar.')
    parser.add_argument('-t', '--topresults', type=int, default=10, help='Número máximo de resultados a mostrar en Shodan, por defecto es 10.')
    parametros = parser.parse_args()

    session = requests.Session()  # Uso de sesiones para optimizar las solicitudes HTTP
    domain = parametros.url.split("//")[-1].split("/")[0]

    logging.info(f'Analizando dominio: {domain}')

    # Verificar si el dominio existe
    if not domain_exists(domain):
        logging.error(f'El dominio {domain} no existe o no se puede resolver.')
        return

    # Obtener subdominios
    subdomains = get_subdomains(domain)
    if subdomains:
        try:
            with open(f'/tmp/{domain}_subdomains.txt', 'w') as f:
                for sub in subdomains:
                    full_url = f"{sub}.{domain}"
                    f.write(full_url + '\n')
                    logging.info(full_url)
        except PermissionError:
            logging.error(f'No se puede escribir en /tmp/. Verifique los permisos de escritura.')

    # Obtener favicon y hash
    absoluteIconPath = getFavIconPath(session, parametros.url)
    if absoluteIconPath:
        logging.info(f'FavIconPath: {absoluteIconPath}')
        favicon, hash = getfavicon(absoluteIconPath)
        if hash:
            logging.info(f'hash: {hash}')
            shodanQuery(hash, parametros.topresults, session)
            discover_real_ip(domain)
        else:
            logging.warning('No se encontró favicon.')
    else:
        logging.warning('No se encontró favicon.')

def domain_exists(domain):
    try:
        dns.resolver.resolve(domain, 'A')
        return True
    except dns.resolver.NXDOMAIN:
        return False
    except dns.resolver.NoAnswer:
        return False
    except dns.resolver.Timeout:
        return False
    except Exception:
        return False

def get_subdomains(domain):
    subdomains = set()
    page = 1

    while True:
        url = f'https://api.securitytrails.com/v1/domain/{domain}/subdomains?page={page}'
        headers = {'apikey': SECURITYTRAILS_API_KEY}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                subdomains.update([f"{sub}.{domain}" for sub in data['subdomains']])
                if not data.get('has_more'):
                    break
                page += 1
            else:
                logging.error(f'Error al obtener subdominios: {response.status_code}')
                break
        except requests.RequestException as e:
            logging.error(f'Error en la solicitud a SecurityTrails: {e}')
            break

    # Usar Sublist3r como fuente adicional
    try:
        result = subprocess.run(['sublist3r', '-d', domain, '-o', f'/tmp/{domain}_sublist3r.txt'], capture_output=True, text=True)
        with open(f'/tmp/{domain}_sublist3r.txt', 'r') as f:
            for line in f:
                subdomains.add(line.strip())
    except FileNotFoundError:
        logging.error('Sublist3r no encontrado. Asegúrese de que esté instalado y en el PATH.')
    except Exception as e:
        logging.error(f'Error al ejecutar Sublist3r: {e}')

    return subdomains

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
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme if parsed_url.scheme else 'https'
    base_url = f"{scheme}://{parsed_url.netloc}"

    for path in favicon_paths:
        try:
            icon_url = urljoin(base_url, path)
            response = session.get(icon_url, headers=headers, timeout=10, verify=False)
            if response.status_code == 200:
                logging.info(f'Favicon encontrado en: {icon_url}')
                return icon_url
        except requests.RequestException as e:
            logging.error(f'Error al obtener favicon: {e}')
    logging.warning('No se encontró favicon en las rutas probadas')
    return None

def getfavicon(absoluteIconPath):
    try:
        response = requests.get(absoluteIconPath, timeout=10, verify=False)
        favicon = codecs.encode(response.content, 'base64')
        hash = mmh3.hash(favicon)
        return favicon, hash
    except requests.RequestException as e:
        logging.error(f'Error al obtener hash de favicon: {e}')
        return None, None

def shodanQuery(hash, topresults, session):
    if SHODAN_API_KEY:
        api = shodan.Shodan(SHODAN_API_KEY)
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

def discover_real_ip(domain):
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

if __name__ == '__main__':
    main()
