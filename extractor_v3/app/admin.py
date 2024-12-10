import os, shutil
import shlex, subprocess
import logging
import json
import pyunycode
import mysql.connector
import requests
import time
from pathlib import Path

from . import config

# CONST
alphabet = config.ALPHABET
dbuser = config.DBUSER
dbpassword = config.DBPASSWORD
host = config.HOST
usertype = config.USERTYPE
path_to_app = config.PATH_TO_APP
database = 'db name'
# LOGGER 
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler(f'{path_to_app}/logs/controller.log', mode='a')

formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s",
                              "%Y-%m-%d %H:%M:%S")

stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

loger = logging.getLogger(__name__)
loger.setLevel(logging.WARNING)
loger.addHandler(stream_handler)
loger.addHandler(file_handler)

class ParserController:
    def __init__(self) -> None:
        pass

    def parse(self, auto=False):

        site_counter = 0
        return_data = []
        # Проходимся по списку всех БОЕВЫХ nginx
        for file_name in os.listdir('/etc/nginx/sites-enabled/'):
            try:
                file_text = ''
                # Открываем каждый файл и записываем его в переменную
                with open(f'/etc/nginx/sites-enabled/{file_name}', 'r') as file:
                    file_text = file.read()

                row_servername = ''
                row_root = ''
                row_php = ''

                # Парсим строки
                for row in file_text.split('\n'):
                    if ('server_name' in row):
                        row_servername = row

                    if ('root' in row):
                        row_root = row

                    if ('proxy_http' in row):
                        row_php = row

                # Код строго привязан с конфигами, соответственно все параметры меняются.
                site_name = row_servername.split(' ')[-2]
                site_folder = row_root.split('/')[2]   
                site_php = row_php.split('_')[-1].replace(';', '')
                # Паникод переделываем в русское название
                decoded_name = ''
                if ('xn--p1ai' in site_name):
                    decoded_name = pyunycode.convert(site_name)
                    
                # Получаем хостинг
                site_hosting = ''
                if auto:
                    site_hosting_api = requests.get(f'http://ip-api.com/json/{site_name}?fields=status,message,isp,org,as,hosting,query').json()
                    if site_hosting_api['status'] == 'success': site_hosting = site_hosting['isp']

                # Размер файла
                site_weight = folderSize(f"/hosting/{site_folder}")

                # Проверяем наличие SSL
                ssl_avaliable = False
                try:
                    with open(f'/etc/letsencrypt/live/{site_name}/fullchain.pem', 'r') as f:
                        ssl_avaliable = True
                except Exception as e:
                    ssl_avaliable = False

                temp_data = (site_name, site_folder, file_name, decoded_name, site_hosting, site_php, ssl_avaliable, site_weight)
                return_data.append(temp_data)

                site_counter += 1
                # if (site_counter > 3):
                #     break

            except Exception as e:
                loger.warning(f'error: {e}')

        self.unique_sql_command('INSERT INTO Domains (site_name, site_folder, file_name, decoded_name, site_hosting, site_php, ssl_avaliable, site_weight) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', return_data)

        return site_counter
    

    def unique_sql_command(self, query, val):

        try:
            cnx = mysql.connector.connect(user=dbuser, password=dbpassword, host=host, database=database)
        except Exception as e:
            loger.critical(f'Connection error: {e}, close connect;')
            return
        
        loger.warning(f'Sql command: {query}')
        cursor = cnx.cursor()

        try:
            cursor.execute('TRUNCATE TABLE Domains;')
            cursor.executemany(query, val)
            loger.warning('OK')
        except Exception as e:
            loger.warning(f'Error: {e}')

        cursor.close()
        cnx.commit()
        cnx.close()


class AutoSSLUpdater:
    def __init__(self) -> None:
        self.ssl_list = []

    def parse(self):

        errors = ''
        path_to = '/etc/letsencrypt/live'
        counter = 0
        for ssl in os.listdir(path_to): 
            try:
                with open(f'{path_to}/{ssl}/fullchain.pem', 'r') as f:

                    creation_time = os.stat(f'{path_to}/{ssl}/fullchain.pem').st_mtime
                    current_time = time.time()
                    delta_time = current_time - creation_time
                    loger.warning(f'Creation time: {creation_time}; Current time: {current_time}')

                    # 80 days
                    if delta_time > 6912000:
                        self.ssl_list.append(ssl)
                        counter += 1
                        loger.warning(f'{counter}. Certifi appended: {ssl}')

            except Exception as e:
                loger.critical(f'certifi exception: {e}')
                errors += f'Ошибка с SSL {ssl}\n'
        
        return errors
    
    def update(self):

        errors = ''
        count = 0
        for ssl in self.ssl_list:
            loger.warning(f'Trying to set certifi on {ssl}')
            try: 
                command = shlex.split(f'certbоt renew --cert-name {ssl} --dry-run')
                proc = subprocess.run(command, shell=False)
        
                loger.warning(f'OK? | {proc}')
                if (proc.returncode != 0):
                    errors += f"Ошибка постановки SSL на {ssl}: " + str(proc.returncode) + '\n'

            except Exception as e: 
                errors += e
                loger.error(f"ERROR: {e}")

            count += 1
            if count > 5: break
            
    
        return errors
    
    
class PageAdmin:
    def __init__(self) -> None:
        pass

    def save_page(self, page_name, text=''):
        
        if '.html' not in page_name:
            page_name = page_name + '.html' if '.html' not in page_name else page_name

        loger.warning(f'Saving page {page_name} on path {path_to_app}/templates/pages/{page_name}')
        with open(f'{path_to_app}/templates/pages/{page_name}', 'w') as f:
            f.write(text)

        return ''

    def delete_page(self, page_name):
        page_name = page_name + '.html' if '.html' not in page_name else page_name
        loger.warning('Trying to remove page...')
        os.remove(f'{path_to_app}/templates/pages/{page_name}')
        return ''

    def load_page(self, page_name):
        loger.warning(f'Open page {page_name} on path {path_to_app}/templates/pages/{page_name}')
        page_name = page_name + '.html' if '.html' not in page_name else page_name
        return_text = ''
        try:
            with open(f'{path_to_app}/templates/pages/{page_name}', 'r') as f:
                return_text = f.read()
        except Exception as e:
            loger.critical(f'Errors at opening file... {page_name}')
            return_text = f'pes'

        return return_text
    
    def load_page_list(self):
        loger.warning('Get the page list...')

        page_list = []
        for i in os.listdir(f'{path_to_app}/templates/pages/'):
            page_list.append(i.replace('.html', ''))

        return page_list
    
    
def folderSize(path):
    command = shlex.split(f'du -sh {path}')
    a = subprocess.check_output(command)
    fsize_readable = str(a).split("'")[1].split("\\")[0]
    fsize = 1.0
    match fsize_readable[-1]:
        case 'G':
            fsize = float(fsize_readable[0:-1]) * 1024
        case 'M':
            fsize = float(fsize_readable[0:-1])
        case 'K':
            fsize = round(float(fsize_readable[0:-1]) / 1024, 1)


    loger.warning(f'Object: {fsize}')
    return fsize