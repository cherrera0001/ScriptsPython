#Este código Python realiza una búsqueda de hosts en Shodan que comparten el mismo favicon que un sitio web especificado 
#por el usuario. A continuación, trata de obtener la dirección IP real detrás de Cloudflare del host que coincide con el 
#favicon mediante el uso de una técnica de resolución de DNS inversa.
#A continuación, explicaré en detalle las partes del código:
#    import - Importa los módulos necesarios para que el programa funcione, incluyendo mmh3 para generar un hash del favicon, 
#             requests para hacer solicitudes HTTP, codecs para codificar y decodificar datos y shodan para acceder a la API de Shodan.
#
#    SHODAN_API_KEY - La clave de API de Shodan utilizada para hacer consultas a la API de Shodan.
#
#    main() - La función principal del programa. Verifica si se proporciona un nombre de host, busca el favicon en el sitio 
#              web especificado, genera un hash del favicon, realiza una consulta a la API de Shodan para encontrar hosts con 
#                el mismo hash de favicon y finalmente obtiene la dirección IP real del host detrás de Cloudflare.
#
#    get_favicon(favicon_url) - La función que se encarga de descargar el favicon del sitio web especificado.
#
#    if __name__ == '__main__': - La línea de código que inicia la ejecución del programa.

#En resumen, este código es un ejemplo de cómo se puede utilizar la API de Shodan y técnicas de resolución de 
#DNS inversa para obtener la dirección IP real detrás de Cloudflare de un sitio web y encontrar hosts que comparten el 
#mismo favicon. Sin embargo, es importante tener en cuenta que esta técnica no siempre funciona y que puede haber otras medidas 
#de protección que impidan que se descubra la dirección IP real del servidor de origen.


import mmh3
import requests
import codecs
import sys
import shodan


SHODAN_API_KEY = "YOUR_API_KEY"

def main():
    if len(sys.argv) < 2:
        print("[!] Error!")
        print(f"[-] Use: python3 {sys.argv[0]} <hostname>")
        sys.exit()

    # Buscar favicon en el host especificado
    favicon_url = f"http://{sys.argv[1]}/favicon.ico"
    favicon_data = get_favicon(favicon_url)

    favicon = codecs.encode(favicon_data, "base64")
    hash_favicon = mmh3.hash(favicon)

    # Realizar consulta a Shodan para encontrar hosts con el mismo favicon
    api = shodan.Shodan(SHODAN_API_KEY)
    query = f"http.favicon.hash:{hash_favicon}"
    results = api.search(query)

    # Obtener dirección IP real del host detrás de Cloudflare
    for result in results["matches"]:
        ip = result["ip_str"]
        headers = {"Host": sys.argv[1]}
        url = f"http://{ip}/favicon.ico"
        try:
            response = requests.get(url, headers=headers, verify=False, proxies={"http": "http://127.0.0.1:8080"})
            if response.status_code == 200 and response.content == favicon_data:
                print(f"[+] Hostname: {sys.argv[1]}")
                print(f"[+] IP address: {ip}")
                break
        except:
            pass

def get_favicon(favicon_url):
    try:
        response = requests.get(favicon_url, verify=False, proxies={"http": "http://127.0.0.1:8080"})
        if response.status_code == 200:
            return response.content
    except:
        pass

if __name__ == '__main__':
    main()
