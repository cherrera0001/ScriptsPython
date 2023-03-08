#Explicación
#En donde: 
#<url> es la URL del sitio web que deseas analizar.
#<topresults> es el número máximo de resultados que deseas mostrar en la consulta de Shodan (por defecto, es 10).
#<shodankey> es tu clave de API de Shodan (opcional). Si proporcionas una clave, se almacenará en el archivo de 
#configuración para su uso posterior. Si no proporcionas una clave, se realizará una búsqueda manual en Shodan.

#Forma de uso
#python faviconfrenzy.py -u <url> -t <topresults> -ak <shodankey>

import argparse
import configparser
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
from PIL import Image
import codecs
import mmh3
import sys
import shodan


def main():
    # Definir los argumentos de línea de comandos
    parser = argparse.ArgumentParser(prog='faviconfrenzy', description='Search for the provided URL FavIcon, calculate the hash and send it to Shodan for analysis.')
    parser.add_argument('-u', '--url',  type=str, nargs='?', help='URL to search for the FavIcon.', required=True)
    parser.add_argument('-ak', '--addshodankey', dest='shodankey', type=str, nargs='?', help='Store or replace the Shodan key in config file.')
    parser.add_argument('-t', '--topresults', type=int, nargs='?', default=10, help='Max numer of results to show, default is 10.')
    parametros = parser.parse_args()

    # Buscar el favicon y calcular su hash
    url = parametros.url 
    absoluteIconPath = getFavIconPath(url)
    if absoluteIconPath:
        print('[+] url:', url)
        print('[+] FavIconPath:', absoluteIconPath)
        favicon, hash = getfavicon(absoluteIconPath)
        if hash:
            print('[+] hash:', hash)

            # Realizar consulta en Shodan utilizando el hash del favicon
            shodanQuery(hash, parametros.topresults)

            # Almacenar la clave de Shodan en el archivo de configuración
            if parametros.shodankey:
                config = configparser.ConfigParser()
                config['SHODAN'] = {'key':parametros.shodankey}
                with open('faviconfrenzy.ini', 'w') as configfile:
                    config.write(configfile)
                    print('\n[!] Shodan Key Stored succesfully')
        else:
            print('[!] No favicon found, Sorry!')
    else:
        print('[!] No favicon found, Sorry!')


def getFavIconPath(url):
    # Definir los headers para la solicitud HTTP
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language':'es-CL,en-US;q=0.7,en;q=0.3',
        'Accept-Encoding':'gzip, deflate, br',
        'Connection':'keep-alive',
        'Upgrade-Insecure-Requests':'1'
    }

    try:
        # Realizar solicitud HTTP para obtener el favicon
        print('[!] Trying to get favicon from Header Link in HTML')
        page = requests.get(url=url, headers=headers)
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')
            link = soup.find('link',rel='icon')
            if (link):
                absoluteIconPath = urljoin(url, link['href'])
                       else:
                print('[!] No icon link in HTML')
                print('[!] Trying to get favicon from root path ')
                u = urlparse(url)
                u = u._replace(path='favicon.ico')
                url = urlunparse(u)
                page = requests.get(url=url, headers=headers)
                if page.status_code == 200:
                    absoluteIconPath = url
                else:
                    print('[!] No favicon in root path')
                    print('[!] Trying to get favicon from /html_public/favicon.ico ')
                    u = urlparse(url)
                    u = u._replace(path='html_public/favicon.ico')
                    url = urlunparse(u)
                    page = requests.get(url=url, headers=headers)
                    if page.status_code == 200:
                        absoluteIconPath = url
                    else:
                        print('[!] No favicon in /html_public/favicon.ico')
    except Exception as ex:
        print('[!] getFavIconPath Error:', str(ex))
        absoluteIconPath = None
    return absoluteIconPath


def getfavicon(absoluteIconPath):
    try:
        # Descargar el favicon y calcular su hash
        response = requests.get(absoluteIconPath)
        favicon = codecs.encode(response.content,'base64')
        hash = mmh3.hash(favicon)
    except Exception as ex:
        print('getfaviconhash Error:', str(ex))
        favicon = None
        hash = None
    return favicon, hash


def shodanQuery(hash, topresults):
    # Realizar consulta en Shodan utilizando el hash del favicon
    api_key = get_shodan_key()
    if api_key:
        api = shodan.Shodan(api_key)
        if hash:
            query = 'http.favicon.hash:{}'.format(hash)
            count = api.count(query)['total']
            if count == 0:
                print('[!] No Shodan result')
            else:
                print(f'\n[+]Retrieving {topresults} results from {count} findings.')
                try:
                    for count, hosts in enumerate(api.search_cursor(query), start=1):
                        print(f'\n  [{count}] Title: ', hosts['http']['title'])
                        print('     [+] Host   : ', hosts['http']['host'])
                        print('     [+] Ip     : ', hosts['ip_str'])
                        print('     [+] Isp    : ', hosts['isp'])
                        print('     [+] Port   : ', str(hosts['port']))
                        print('     [+] Org    : ', hosts['org'])
                        print('     [+] Domains: ', hosts['domains'])
                        if len(hosts['http']['components']) > 0:
                            print('     [+] Components :') 
                        for component in hosts['http']['components']:
                            print('       [+]' , component)
                        if count >= topresults:
                            break
                except Exception as ex:
                    print('[!] Shodan Error:', str(ex))
        else:
            print('[!] No icon found.')
    else:
        print('[!] Shodan API key not found.')


def get_shodan_key():
    # Obtener la clave de Shodan desde el archivo de configuración
    config = configparser.ConfigParser()
    config.read('faviconfrenzy.ini')
    if config.has_option(section='SHODAN', option='key'):
        return config['SHODAN']['key']
    else:
        return None


if __name__ == '__main__':
    main()
