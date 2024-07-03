# ScriptsPython
En este repositorio iré dejando deversos script que pueden ser de utilidad de todos.

1. FaviconFrenzy.py
FaviconFrenzy es un script en Python diseñado para buscar el favicon de una URL proporcionada, calcular su hash y enviarlo a shodan para su análisis. Además, el script puede descubrir la dirección IP real detrás de servicios de protección como Cloudflare.

Descripción: 
 - Obtiene el favicon de una URL proporcionada y calcula su hash utilizando mmh3.
 - Utiliza el hash del favicon para buscar en Shodan posibles coincidencias y obtener información detallada sobre los servidores que usan el mismo favicon.
 - Intenta resolver la dirección IP real del dominio, incluso si está protegido por servicios como Cloudflare.

Uso: 

Parámetros
-u, --url (requerido): URL para buscar el FavIcon.
-ak, --addshodankey: Almacena o reemplaza la clave Shodan en el archivo de configuración.
-t, --topresults: Número máximo de resultados a mostrar de Shodan (por defecto es 10).

Ejemplo de Uso:

python3 faviconfrenzy.py -u https://ejemplo.com -ak TU_CLAVE_SHODAN

Ejemplo de resultado:

INFO:root:Favicon encontrado en: https://ejemplo.com/favicon.ico
INFO:root:url: https://ejemplo.com
INFO:root:FavIconPath: https://ejemplo.com/favicon.ico
INFO:root:hash: 123456789
INFO:root:Clave Shodan almacenada con éxito
Resultado 1:
IP: 192.168.0.1
Port: 80
Hostnames: ['ejemplo.com']
Location: {'country_name': 'United States', 'city': 'New York'}
------------------------------------------------------------
Possible real IP address: 203.0.113.5

   
