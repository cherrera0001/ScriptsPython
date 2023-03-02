import requests
import urllib.parse

# URL a analizar
url = "URL"

# Dividir la URL en sus componentes
parsed_url = urllib.parse.urlparse(url)

# Obtener los parámetros de la URL
query_list = urllib.parse.parse_qsl(parsed_url.query)

# Decodificar los valores de los parámetros
decoded_query_list = [(key, urllib.parse.unquote(value)) for key, value in query_list]

# Imprimir los atributos y valores de la URL
print('Variables y parámetros:')
for key, value in decoded_query_list:
    print(key, ':', value)

# Volver a armar la URL con los mismos componentes
new_url = urllib.parse.urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, urllib.parse.urlencode(query_list), parsed_url.fragment))

# Imprimir la nueva URL
print('Nueva URL:')
print(new_url)

# Configurar los proxies
proxies = {
  'http': 'http://127.0.0.1:8080',
  'https': 'https://127.0.0.1:8080'
}

# Hacer una solicitud HTTP a través del proxy
response = requests.get(new_url, proxies=proxies, verify=False)

print(response.content)
