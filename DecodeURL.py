import requests
import urllib.parse

url = 'https://example.com/path?foo=bar&baz=qux%21&empty&no_value='

parsed_url = urllib.parse.urlparse(url)
query_list = urllib.parse.parse_qsl(parsed_url.query)

decoded_query_list = [(key, urllib.parse.unquote(value)) for key, value in query_list]

print('Variables y parámetros:')
for key, value in decoded_query_list:
    print(key, ':', value)

# Configurar los proxies
proxies = {
    'http': 'http://user:password@proxy_address:port',
    'https': 'https://user:password@proxy_address:port'
}

# Construir la URL decodificada y enviar la petición al proxy
decoded_url = urllib.parse.urlunparse(parsed_url._replace(query=urllib.parse.urlencode(decoded_query_list)))
response = requests.get(decoded_url, proxies=proxies)

print(response.content)
