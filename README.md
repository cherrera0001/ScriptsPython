# ScriptsPython

En este repositorio iré dejando deversos script que pueden ser de utilidad de todos.

1. FaviconFrenzy.py
 FaviconFrenzy es un script en Python diseñado para buscar el favicon de una URL proporcionada, calcular su hash y enviarlo a shodan para su análisis. Además, el script puede descubrir la dirección IP real detrás de servicios de protección como Cloudflare.

 Descripción: 
  - Obtiene el favicon de una URL proporcionada y calcula su hash utilizando mmh3.
  - Utiliza el hash del favicon para buscar en Shodan posibles coincidencias y obtener información detallada sobre los servidores que usan el mismo favicon.
  - Intenta resolver la dirección IP real del dominio, incluso si está protegido por servicios como Cloudflare.

 
 Parámetros
 
 -u, --url (requerido): URL para buscar el FavIcon.
 -ak, --addshodankey: Almacena o reemplaza la clave Shodan en el archivo de configuración.
 -t, --topresults: Número máximo de resultados a mostrar de Shodan (por defecto es 10).

 Ejemplo de Uso:
 
    python3 faviconfrenzy.py -u https://ejemplo.com -ak TU_CLAVE_SHODAN

 Ejemplo de resultado:

   ![image](https://github.com/cherrera0001/ScriptsPython/assets/19656010/b026ff35-2685-416b-8c77-1fe8f82ccccb)

 Requisitos:

   pip install requests mmh3 shodan dnspython

 Notas:

 - Asegúrate de tener una clave API de Shodan válida.
 - El script intenta resolver la IP real del dominio utilizando consultas DNS, lo cual puede no siempre ser exitoso dependiendo de las configuraciones del DNS y servicios de protección como Cloudflare.


2. complete_scan.py

   Este script realiza un análisis completo de seguridad para un dominio especificado. Las funcionalidades clave incluyen:

   - Utiliza crt.sh y SecurityTrails para obtener una lista de subdominios del dominio proporcionado.
   - Busca información en Shodan sobre los subdominios, como direcciones IP, puertos abiertos y otros datos relevantes.
   - Intenta resolver la IP real de los subdominios para detectar la IP original detrás de servicios de protección como Cloudflare.
  -  Escanea los puertos de los subdominios para detectar servicios abiertos.
  
   Ejemplo de uso:
    Para ejecutar el script, usa el siguiente comando, donde https://ejemplo.com es el dominio que quieres analizar:
 
     export SHODAN_API_KEY="tu_clave_api_de_shodan"
     export SECURITYTRAILS_API_KEY="tu_clave_api_de_securitytrails"
     python3 complete_scan.py -u https://ejemplo.com > result.txt

  

  
