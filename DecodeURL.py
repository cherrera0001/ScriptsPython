import requests
import urllib.parse

# Recibir la URL a analizar
url = input("Ingrese la URL a analizar: ")

# Decodificar la URL
parsed_url = urllib.parse.urlparse(url)
query_list = urllib.parse.parse_qsl(parsed_url.query)
decoded_query_list = [(key, urllib.parse.unquote(value)) for key, value in query_list]

# Armar la nueva URL decodificada
new_url = urllib.parse.urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, urllib.parse.urlencode(decoded_query_list), parsed_url.fragment))

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

# Imprimir la respuesta del proxy
print(response.content)

