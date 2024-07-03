import argparse
import requests
import logging
import shodan
import dns.resolver

# Configuración inicial de logging
logging.basicConfig(level=logging.INFO)

# Define aca las variables o claves para consumo de tus apis.
SHODAN_API_KEY = "tu_clave_api_de_shodan"
SECURITYTRAILS_API_KEY = "tu_clave_api_de_securitytrails"


def main():
    parser = argparse.ArgumentParser(prog='complete_scan', description='Realiza un análisis completo de seguridad para un dominio especificado.')
    parser.add_argument('-u', '--url',  type=str, required=True, help='Dominio para realizar el análisis.')
    parser.add_argument('-t', '--topresults', type=int, default=10, help='Número máximo de resultados a mostrar de Shodan, por defecto es 10.')
    parametros = parser.parse_args()

    domain = parametros.url.replace('https://', '').replace('http://', '').replace('/', '')
    subdomains = get_subdomains(domain)
    if subdomains:
        logging.info(f'Subdominios encontrados para {domain}: {subdomains}')
        scan_subdomains(subdomains, parametros.topresults)
    else:
        logging.warning(f'No se encontraron subdominios para {domain}')

def get_subdomains(domain):
    subdomains = set()

    # Obtener subdominios desde crt.sh
    crtsh_url = f"https://crt.sh/?q=%25.{domain}&output=json"
    try:
        response = requests.get(crtsh_url)
        if response.status_code == 200:
            data = response.json()
            for entry in data:
                subdomains.update(entry['name_value'].split("\n"))
    except Exception as e:
        logging.error(f'Error obteniendo subdominios de crt.sh: {e}')

    # Obtener subdominios desde SecurityTrails
    securitytrails_url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
    headers = {
        'APIKEY': SECURITYTRAILS_API_KEY
    }
    try:
        response = requests.get(securitytrails_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            subdomains.update(data['subdomains'])
    except Exception as e:
        logging.error(f'Error obteniendo subdominios de SecurityTrails: {e}')

    return subdomains

def scan_subdomains(subdomains, topresults):
    for subdomain in subdomains:
        logging.info(f'Escaneando subdominio: {subdomain}')
        discover_real_ip(subdomain)
        shodan_query(subdomain, topresults)

def discover_real_ip(domain):
    try:
        answers = dns.resolver.resolve(domain, 'A')
        for rdata in answers:
            logging.info(f'Posible IP real para {domain}: {rdata}')
    except dns.resolver.NXDOMAIN:
        logging.warning(f'No se pudo resolver el dominio {domain}')
    except dns.resolver.NoAnswer:
        logging.warning(f'No se encontró respuesta para el dominio {domain}')
    except dns.resolver.Timeout:
        logging.warning(f'Tiempo de espera agotado para el dominio {domain}')
    except Exception as e:
        logging.error(f'Error al buscar IP real para {domain}: {e}')

def shodan_query(domain, topresults):
    api_key = SHODAN_API_KEY
    if api_key:
        api = shodan.Shodan(api_key)
        query = f'hostname:{domain}'
        try:
            results = api.search(query, limit=topresults)
            if not results['matches']:
                logging.warning(f'No se encontraron resultados en Shodan para {domain}')
            else:
                for count, host in enumerate(results['matches'], start=1):
                    logging.info(f'Resultado {count}:')
                    logging.info(f'IP: {host["ip_str"]}')
                    logging.info(f'Port: {host["port"]}')
                    logging.info(f'Hostnames: {host.get("hostnames")}')
                    logging.info(f'Location: {host["location"]}')
                    logging.info('-' * 60)
        except shodan.APIError as e:
            logging.error(f'Error en consulta Shodan para {domain}: {e}')
    else:
        logging.warning('Clave API de Shodan no encontrada')

if __name__ == '__main__':
    main()
