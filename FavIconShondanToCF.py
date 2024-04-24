#Script de Python diseñado para hacer lo siguiente:
# 1. Verifica que una URL proporcionada sea válida.
# 2. Descarga el favicon de esa URL.
# 3. Codifica el favicon en base64 y calcula su hash MurmurHash3.
# 4. Usa el hash del favicon para buscar en Shodan por otros servicios web que usen el mismo favicon.
# 5. Para usar el script correctamente, necesitas tener Python instalado en tu sistema, junto con las bibliotecas requests, codecs, sys, mmh3, shodan, y urllib. 
# Aquí está el proceso general que debes seguir para ejecutar el script:
# Asegúrate de que todas las dependencias estén instaladas. Si no lo están, puedes instalarlas usando pip (el gestor de paquetes de Python):
# pip install requests mmh3 shodan
# Asegúrate de que la clave API de Shodan que está en el script (key_shodan) sea válida y activa.
# Asegúrate de que la configuración del proxy (http://192.168.1.87:8084) sea la correcta para tu red. Si no estás detrás de un proxy, puedes eliminar o comentar las líneas relevantes del script.
# Guarda el script en tu computadora.
# Ejecuta el script desde la línea de comandos, proporcionando la URL del sitio que quieres verificar:
# python3 FavIconShondanToCF.py https://web-A-certificar.com


import mmh3
import requests
import codecs
import sys
import shodan
from urllib.parse import urlparse

# Clave de API para Shodan y configuración del proxy
SHODAN_API_KEY = "Aquí api key shodan"
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
