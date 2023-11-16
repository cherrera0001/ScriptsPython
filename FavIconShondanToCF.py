import mmh3
import requests
import codecs
import sys
import shodan
from urllib.parse import urlparse

# Clave de API para Shodan y configuración del proxy
SHODAN_API_KEY = "xPauT6WwgMaXt4uIXv25LATSEegLF6AE"
PROXY = "http://127.0.0.1:8080"  # Ajusta esta dirección a tu configuración de proxy

def is_valid_url(url):
    # Valida si la URL proporcionada tiene un formato adecuado
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_favicon(favicon_url, session):
    # Descarga el favicon del sitio web y maneja excepciones
    try:
        proxies = {
            "http": PROXY,
            "https": PROXY
        }
        response = session.get(favicon_url, verify=False, proxies=proxies, timeout=20)
        if response.status_code == 200:
            return response.content
        else:
            print(f"[!] No se pudo obtener el favicon: Estado HTTP {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"[!] Error al obtener el favicon: {e}")
        return None

def main():
    # Proceso principal del script
    if len(sys.argv) < 2 or not is_valid_url(sys.argv[1]):
        print("[!] Error!")
        print(f"[-] Use: python3 {sys.argv[0]} <url>")
        sys.exit()

    parsed_url = urlparse(sys.argv[1])
    hostname = parsed_url.hostname
    scheme = parsed_url.scheme
    port = f":{parsed_url.port}" if parsed_url.port else ""
    favicon_url = f"{scheme}://{hostname}{port}/favicon.ico"

    session = requests.Session()  # Usando sesiones para conexiones persistentes
    session.proxies = {
        "http": PROXY,
        "https": PROXY
    }

    favicon_data = get_favicon(favicon_url, session)
    if favicon_data is None:
        sys.exit()

    # Codificar el favicon en base64 y calcular su hash MurmurHash3
    favicon = codecs.encode(favicon_data, "base64")
    hash_favicon = mmh3.hash(favicon)
    print(f"[+] Favicon hash: {hash_favicon}")

    # Realizar consulta a Shodan con el hash del favicon
    try:
        api = shodan.Shodan(SHODAN_API_KEY)
        query = f"http.favicon.hash:{hash_favicon}"
        print(f"[+] Shodan query: {query}")
        results = api.search(query)
        # Imprimir resultados detallados de Shodan
        print("[+] Resultados de Shodan:", results)
    except Exception as e:
        print(f"[!] Error al buscar en Shodan: {e}")
        sys.exit()

    # Puedes agregar más código aquí para manejar o procesar los resultados de Shodan

if __name__ == '__main__':
    main()
