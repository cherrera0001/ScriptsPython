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

 Necesario antes de usar:
 
    pip install requests beautifulsoup4 pillow mmh3 shodan dnspython 
 
 Ejemplo de Uso:

 
    python3 faviconfrenzy.py -u https://ejemplo.com -ak TU_CLAVE_SHODAN
    

 Ejemplo de resultado:

   ![image](https://github.com/cherrera0001/ScriptsPython/assets/19656010/b026ff35-2685-416b-8c77-1fe8f82ccccb)

 Requisitos:

   pip install requests mmh3 shodan dnspython
  

 Notas:

 - Asegúrate de tener una clave API de Shodan válida.
 - El script intenta resolver la IP real del dominio utilizando consultas DNS, lo cual puede no siempre ser exitoso dependiendo de las configuraciones del DNS y servicios de protección como Cloudflare.

---------------------------------------------------------------------------------------------------------------------------
2. domainSecurityScan.py

   Este script realiza un análisis completo de seguridad para un dominio especificado. Las funcionalidades clave incluyen:

   - Utiliza crt.sh y SecurityTrails para obtener una lista de subdominios del dominio proporcionado.
   - Busca información en Shodan sobre los subdominios, como direcciones IP, puertos abiertos y otros datos relevantes.
   - Intenta resolver la IP real de los subdominios para detectar la IP original detrás de servicios de protección como Cloudflare.
   -  Escanea los puertos de los subdominios para detectar servicios abiertos.
  
   Ejemplo de uso:
    Para ejecutar el script, usa el siguiente comando, donde https://ejemplo.com es el dominio que quieres analizar:
 
         python3 domainSecurityScan.py -u https://ejemplo.com > result.txt


---------------------------------------------------------------------------------------------------------------------------
  3. FavIconShondanToCF.py

     Este script está diseñado para realizar varias tareas relacionadas con la verificación y análisis de una URL específica. Sus funciones incluyen:

   - Verificación de la validez de una URL proporcionada.
   - Descarga del favicon (ícono) del sitio web de la URL.
   - Codificación del favicon en base64 y cálculo de su hash utilizando MurmurHash3.
   - Búsqueda en Shodan utilizando el hash del favicon para encontrar otros servicios web que utilicen el mismo favicon.
   - Ejecución del script desde la línea de comandos con los parámetros adecuados.

  ¿Cómo usar el script?
    Asegúrate de que todas las dependencias estén instaladas:
     
     pip install requests mmh3 shodan

   - Verifica que la clave API de Shodan (SHODAN_API_KEY) en el script sea válida y activa.
   - Configura el proxy en el script si es necesario. Si no estás detrás de un proxy, comenta o elimina las líneas relevantes.
   - Guarda el script en tu computadora.
   - Ejecuta el script desde la línea de comandos proporcionando la URL del sitio a verificar

         python3 FavIconShondanToCF.py https://web-A-certificar.com
   - El script validará la URL, descargará el favicon, calculará su hash, y realizará una búsqueda en Shodan usando el hash del favicon.
   - Este proceso te ayudará a identificar otros servicios web que compartan el mismo favicon, lo que puede ser útil en tareas de reconocimiento y análisis de seguridad.


  ---------------------------------------------------------------------------------------------------------------------------
  4. RequestSlow.py
     Este script está diseñado para realizar pruebas de ataques de DDoS (Denegación de Servicio Distribuido) utilizando diferentes métodos como HTTP, TCP y UDP. Las principales funcionalidades del script incluyen:

   - Configuración y envío de solicitudes HTTP para mantener vivos los sockets.
   - Realización de inundaciones TCP y UDP para simular ataques de DDoS.
   - Uso de múltiples hilos (threads) para enviar múltiples paquetes simultáneamente.
   - Configuración de intervalos y límites de tasa para las solicitudes HTTP.

   ¿Cómo usar el script?
    Asegúrate de tener Python instalado en tu sistema. Guarda el script en tu computadora. Ejecuta el script desde la línea de comandos proporcionando los parámetros adecuados. 
    Ejemplo de uso:
                   
            python3 ddos_test.py <ip_objetivo> <puerto_objetivo> --http --tcp --udp --socket_count 100 --thread_count 10 --duration 120 --packet_size 1024 --timer 10 --rate_limit 5
        
Los parámetros que puedes configurar son:

   ip: Dirección IP del objetivo.
   port: Número de puerto del objetivo.
   --http: Activa el ataque de inundación HTTP.
   --tcp: Activa el ataque de inundación TCP.
   --udp: Activa el ataque de inundación UDP.
   --socket_count: Número de sockets a usar para la inundación HTTP.
   --thread_count: Número de hilos para la inundación TCP/UDP.
   --duration: Duración de la inundación TCP/UDP en segundos.
   --packet_size: Tamaño de los paquetes TCP/UDP en bytes.
   --timer: Intervalo en segundos entre señales de keep-alive.
   --rate_limit: Límite de tasa para las solicitudes HTTP por segundo.
   
   El script registrará la información relevante y errores durante su ejecución para monitorear el progreso y solucionar problemas.
   
   Importante: Este script es solo para fines educativos y de prueba en entornos controlados y con el consentimiento del propietario del objetivo. El uso indebido de este script para realizar ataques de DDoS en sistemas no autorizados es ilegal.
   
   ---------------------------------------------------------------------------------------------------------------------------
 5. scanNet.sh

   Este script de Shell está diseñado para realizar un escaneo de puertos en un rango de direcciones IP dentro de una red local. 
   Utiliza nc (netcat) para comprobar la respuesta de los puertos y parallel para ejecutar múltiples tareas en paralelo, mejorando la eficiencia del escaneo. Detecta servicios comunes como HTTP, SSH y SMTP.

   Instalación:

    sudo apt-get install parallel netcat

   Dar persmisos de ejecución:
  
     chmod +x scanNet.sh

   Ejecutar:
  
      ./scanNet.sh

   - check_service: Función que determina el tipo de servicio basado en la respuesta obtenida del puerto.
   - scan_ip_port: Función que escanea un puerto específico en una IP determinada y llama a check_service para identificar el servicio.
   - Ejecución en paralelo: El script utiliza parallel para ejecutar scan_ip_port en múltiples combinaciones de IPs y puertos simultáneamente, escaneando eficientemente todo el rango especificado.
   - Parámetros de red: ip_base define la subred a escanear, mientras que port_range_start y port_range_end definen el rango de puertos a escanear.
   - ip_base: Define la subred a escanear (e.g., "192.168.1").
   - port_range_start y port_range_end: Definen el rango de puertos a escanear (del 1 al 1024).
   - 
---------------------------------------------------------------------------------------------------------------------------
   
   6. scanNet.py
    
   Este script está diseñado para escanear puertos en un rango de direcciones IP dentro de una red local.
   Utiliza múltiples procesos para mejorar la eficiencia del escaneo y detectar servicios comunes como HTTP, SSH y SMTP.
   Aquí se explican sus componentes   principales y cómo usarlo.

   Instalación necesaria:

         pip install tqdm

   Ejecución:
    
         python3 port_scanner.py


   - Función check_service: Esta función separa la lógica de identificación del servicio, mejorando la claridad del código.
   - Función scan_ip_port: Esta función maneja el escaneo de un puerto específico en una IP dada, incluyendo el manejo de excepciones específicas para socket.timeout y socket.error.
   - Función scan_port: Esta función recorre el rango de IPs para un puerto dado, llamando a scan_ip_port.
   - Uso de tqdm: Ahora tqdm se usa para mostrar el progreso del escaneo de puertos, lo que proporciona una retroalimentación visual clara del progreso del script.
   - ip_base: Define la subred a escanear (e.g., "192.168.1.").
   - port_range: Define el rango de puertos a escanear (del 1 al 1024).
   - ip_range: Define el rango de IPs dentro de la subred a escanear (del 1 al 254).
   - timeout: Tiempo de espera para cada intento de conexión.

