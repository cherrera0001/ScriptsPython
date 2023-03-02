import requests
import urllib.parse


# URL a analizar
url = "AQUI_TU_URL"

parsed_url = urllib.parse.urlparse(url)
query_list = urllib.parse.parse_qsl(parsed_url.query)

decoded_query_list = [(key, urllib.parse.unquote(value)) for key, value in query_list]

print('Variables y parámetros:')
for key, value in decoded_query_list:
    print(key, ':', value)

# Enviar petición al proxy con los parámetros decodificados
proxy_url = 'http://127.0.0.1:8080'
proxy_params = dict(decoded_query_list)
response = requests.get(proxy_url, params=proxy_params)

print(response.content)
