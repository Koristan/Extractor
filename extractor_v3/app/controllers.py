# IMPORTS
import os, shutil
import shlex, subprocess
from subprocess import Popen, PIPE
import time
import hashlib
from flask import request
import re

import mysql.connector
from transliterate import translit
import pyunycode
import logging
from werkzeug.utils import secure_filename
import zipfile

from . import config

# CONST
alphabet = config.ALPHABET
dbuser = config.DBUSER
dbpassword = config.DBPASSWORD
host = config.HOST
usertype = config.USERTYPE
path_to_app = config.PATH_TO_APP
database = config.DATABASE
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

class CreateController:
    def __init__(self, site_name, old_site_name, file, ip) -> None:
        
        self.ip = ip
        self.site_name = site_name
        self.old_site_name = old_site_name
        self.folder_already_exists = False
        self.file = file
        # DEFAULT
        self.old_site_domain = old_site_name
        self.old_site_folder = old_site_name
        self.site_domain = site_name
        self.site_folder = site_name

        self.apache_vers = ''
        if isrus(old_site_name):
            self.old_site_folder = check_punycode_domain(self.old_site_folder)
            self.old_site_domain = pyunycode.convert(site_name)

        if isrus(site_name):
            self.site_folder = translit(self.site_folder, 'ru', reversed=True).replace('\'', '')
            self.site_domain = pyunycode.convert(self.site_domain)
            loger.warning(f'Russian site name... New folder: {self.site_folder}; New domain: {self.site_domain}')

        loger.warning(f'Old site name: {self.old_site_name};\nNew site domain: {self.site_domain}\nNew site folder: {self.site_folder}')

        
    def create_apache_nginx(self, iswar, isssl, withssl, apache_version):

        # DEFAULT
        file = ''
        site = 'sites-dev'
        loger.critical(f'\n\nsosiska v {apache_version} teste\n\n')
        self.apache_vers = 'apache2-php8.0' if apache_version == '' else apache_version

        ssl_avaliable = False
        # APACHE
        loger.warning(f'\nStarting creating APACHE; iswar: {iswar}, issssl: {isssl}\n')

        if iswar: # sites-enabled
            site = 'sites-enabled'
            with open(f'{path_to_app}/app/resources/config/apache-war.config', 'r') as f:
                file = f.read()

            if isssl and int(withssl) == 0:
                file = file.replace('#', '')

        else: # sites-dev
            with open(f'{path_to_app}/app/resources/config/apache.config', 'r') as f:
                file = f.read()

            file = file.replace('#', '')

        file = file.replace("DOMAIN", self.site_domain)
        file = file.replace("FOLDER", self.site_folder)
        
        with open(f'/etc/{self.apache_vers}/{site}/{self.site_folder}', 'w') as f: # DIFFERENCE BETWEEN apache2 AND apache2-php8.0
            f.write(file + "\n# DON'T TOUCH #")

        # NGINX
        loger.warning(f'\nStarting creating NGINX; iswar: {iswar}, issssl: {isssl}\n')

        if iswar: # sites-enabled
            with open((f'{path_to_app}/app/resources/config/nginx-war.config'), 'r') as f:
                file = f.read()

            try:
                with open(f'/etc/letsencrypt/live/{self.site_domain}/fullchain.pem', 'r') as f:
                    ssl_avaliable = True
            except Exception as e:
                ssl_avaliable = False

            if isssl and ssl_avaliable and int(withssl) == 0:
                file = file.replace('#', '')

        else: # sites-dev

            with open((f'{path_to_app}/app/resources/config/nginx.config'), 'r') as f:
                file = f.read()

            file = file.replace('#', '')

        file = file.replace("DOMAIN", self.site_domain)
        file = file.replace("FOLDER", self.site_folder)
        
        with open(f'/etc/nginx/{site}/{self.site_folder}', 'w') as f:
            f.write(file)
    

    def copy_folder(self):

        errors = ''
        loger.warning(f'\nStarting copying site on /hosting/{self.site_folder}\n')

        if os.path.exists(f"/hosting/{self.site_folder}"):
            self.folder_already_exists = True
            loger.warning('\nSite already exists! Skip step\n')
            errors += 'Папка не была создана, уже существует!\n'
        else: 
            try:
                shutil.copytree(f"/hosting/{self.old_site_folder}", f'/hosting/{self.site_folder}')
                loger.warning('Copy good')
            except Exception as e:
                loger.critical(f'ERROR: {e}')
                errors += 'Шаблона для копирования не существует!'

        # TERRIBLE!
        os.system(f'cd /hosting; chown -R 33:33 /hosting/{self.site_folder.strip()}/')
        loger.warning(f"chown on /hosting/{self.site_folder}/")
        return errors


    def create_new_folder(self, empty, archive_type):

        errors = ''
        loger.warning(f'Starting creating on /hosting/{self.site_folder}, isempty: {empty}')

        if int(empty) == 1:
            try:
                if os.path.exists(f"/hosting/{self.site_folder}"):
                    loger.warning('Site already exists! Skip step')
                    self.folder_already_exists = True
                    errors += 'Папка не была создана, уже существует!\n'

                else: 
                    shutil.copytree(f"{path_to_app}/app/resources/wordpress", f'/hosting/{self.site_folder}')
                    loger.warning('Copy good')

            except Exception as e:
                loger.critical(f'Error: {e} | Already exists?')
                errors += f'Проблема с созданием сайта\n'
        else:

            try:

                if os.path.exists(f"/hosting/{self.site_folder}"):
                    loger.warning('Site already exists! Skip step')
                    self.folder_already_exists = True
                    errors += 'Папка не была создана, уже существует!\n'

                else: 
                    os.mkdir(f'/hosting/{self.site_folder}')
                    loger.warning('Copy good')

            except Exception as e:
                loger.critical(f'Error: {e} | Already exists?')
                errors += f'Проблема с созданием сайта\n'

            try:
                if os.path.exists(f"/hosting/{self.site_folder}") and self.folder_already_exists == False:
                    errors += self.copy_archive(archive_type)
                else:
                    errors += 'Папка существует, данные не перенесены!'
            except Exception as e:
                loger.critical(f'Error: {e}')
                errors += f'Проблема с копированием архива\n'
        # TERRIBLE!
        os.system(f'cd /hosting; chown -R 33:33 /hosting/{self.site_folder.strip()}/')
        loger.warning(f"chown on /hosting/{self.site_folder}/")

        return errors

    def copy_archive(self, archive_type):

        if str(self.file) == '':
            return ""
        # loger.critical(self.file)
        unpack_path = f'{path_to_app}/temp/{self.site_folder}'

        filename = secure_filename(self.file.filename)
        errors = ''
        try: 
            self.file.save(f'/hosting/{self.site_folder}/{filename}')
        except Exception as e:
            loger.warning(f'{e} | Archive is empty?')
            errors += 'Файл не загружен\n'
            return errors

        if archive_type == 0:
            self.unpack_duplicator_archive(filename, unpack_path)
        else:
            self.unpack_extractor_archive(filename, unpack_path)

        return errors


    def unpack_duplicator_archive(self, filename, unpack_path):
        with zipfile.ZipFile(f'/hosting/{self.site_folder}/{filename}', 'r') as zip_ref:
            if not os.path.exists(unpack_path):
                os.makedirs(unpack_path)
            zip_ref.extractall(unpack_path)

        for i in os.listdir(unpack_path):
            if (filename[:10] in i):
                shutil.copy(f'{unpack_path}/{i}', f'/hosting/{self.site_folder}/installer.php')

    def unpack_extractor_archive(self, filename, unpack_path):
        with zipfile.ZipFile(f'/hosting/{self.site_folder}/{filename}', 'r') as zip_ref:
            zip_ref.extractall(unpack_path)

        path_to_temp_file = f'{unpack_path}{path_to_app}/temp/'
        path_to_temp_file += f"{os.listdir(path_to_temp_file)[0]}/"
        path_to_sql = path_to_temp_file + str(os.listdir(path_to_temp_file)[1])
        path_to_temp_file += f"{os.listdir(path_to_temp_file)[0]}/"

        exceptions = ['php', 'html', 'htaccess']
        for file_object in os.listdir(path_to_temp_file):
            try:
                if any(exp in file_object for exp in exceptions):
                    shutil.copy(f"{path_to_temp_file}{file_object}", f'/hosting/{self.site_folder.strip()}/{file_object}')
                else:
                    shutil.copytree(f"{path_to_temp_file}{file_object}", f'/hosting/{self.site_folder.strip()}/{file_object}')
            except:
                loger.warning(f'{file_object} already available')
        loger.warning(f'mysql -h {host} -u {dbuser} {self.site_folder} < {path_to_sql}') 
        subprocess.run(f'mysql -h {host} -u {dbuser} -p{dbpassword} {self.site_folder} < {path_to_sql}', shell=True)
        loger.warning(f'insert OK')

        loger.warning('Remove ZIP file')
        os.remove(f'/hosting/{self.site_folder}/{filename}')

    def create_sql(self, new = False):

        errors = ''

        loger.warning(f'Starting create sql (new = {new}, self.apache_vers  = {self.apache_vers})')
        loger.warning('Creating user...')
        native_type = 'caching_sha2_password' if self.apache_vers == 'apache2-php8.0' else 'mysql_native_password'
        try:
            query = f"CREATE USER '{self.site_folder}'@'{usertype}' IDENTIFIED WITH {native_type} BY '{self.site_folder}';GRANT USAGE ON *.* TO '{self.site_folder}'@'{usertype}';ALTER USER '{self.site_folder}'@'{usertype}' REQUIRE NONE WITH MAX_QUERIES_PER_HOUR 0 MAX_CONNECTIONS_PER_HOUR 0 MAX_UPDATES_PER_HOUR 0 MAX_USER_CONNECTIONS 0;CREATE DATABASE IF NOT EXISTS `{self.site_folder}`;GRANT ALL PRIVILEGES ON `{self.site_folder}`.* TO '{self.site_folder}'@'{usertype}';"
            sql_command(query)
            loger.warning('OK')

        except Exception as e:
            query = f""
            loger.error(f'Exception: {e} / already exists?')
            errors += f"Проблема с новой учетной записью в БД (Возможно пользователь уже существует)\n"

        if new == False:
        # Change WP_CONFIG
            loger.warning('Start replacing WP_CONFING')
            try:

                file = ''
                with open(f'/hosting/{self.site_folder}/wp-config.php', 'r') as f:
                    file = f.read()

                file = file.replace(f'{self.old_site_folder}', f'{self.site_folder}')
                # file = file.replace(f'{self.site_folder}', f'{self.site_domain}', -1)
                true_file = ''

                # Delete useless
                for i in file.split('\n'):
                    if ('WP_SITEURL' in i):
                       continue
                   
                    true_file += i + '\n'

                with open(f'/hosting/{self.site_folder}/wp-config.php', 'w') as f:
                    f.write(true_file)
                
                loger.warning('OK')

            except Exception as e:
                loger.error(f'ERROR: {e}')
                errors += 'Проблема в WP CONFIG'

            time.sleep(3)

            # EXPORT - IMPORT BD
            loger.warning('Start copying DB...')
            try:
                subprocess.run(f'mysqldump -h {host} -u {dbuser} -p{dbpassword} {self.old_site_folder} > {path_to_app}/temp/{self.old_site_folder}-db.sql', shell=True)
                loger.warning(f'dump OK')

                time.sleep(2)

                subprocess.run(f'mysql -h {host} -u {dbuser} -p{dbpassword} {self.site_folder} < {path_to_app}/temp/{self.old_site_folder}-db.sql', shell=True)
                loger.warning(f'insert OK')

            except Exception as e:
                loger.error(f'ERROR: {e}')
                errors += f'{e} = (Проблема с экспортом/импортом БД)'

            # WP search-replace
            loger.warning(f'Starting replacing tables on /hosting/{self.site_folder}')
            try:

                command = f'cd /hosting/{self.site_folder}; wp search-replace \'{self.old_site_domain}\' \'{self.site_domain}\' --precise --all-tables --allow-root'
                # ПРОСТОЙ СПОСОБ

               
                loger.critical(command)
                os.system(command)
                
            except Exception as e:
                loger.error(f'ERROR: {e}')
                errors += f'{e} = (Ошибка в wp search-replace)'

        return errors



    # CERTBOTONLY
    def apache_nginx_confirm(self):

        errors = ''
        ssl_avaliable = False

        loger.warning('Starting confirmer')

        try:
            with open(f'/etc/letsencrypt/live/{self.site_domain}/fullchain.pem', 'r') as f:
                ssl_avaliable = True
                errors += 'SSL уже есть!\n'

        except Exception as e:
            ssl_avaliable = False
            loger.critical(f'ERORR: {e} | Dont exists')

        if ssl_install_constaint(self.site_folder, self.ip): 
            if not ssl_avaliable:
                try: 
                    command = shlex.split(f'certbot certonly --noninteractive --agree-tos --webroot -w /var/www -d {self.site_domain} -d www.{self.site_domain}')
                    proc = subprocess.run(command, capture_output=True)
            
                    loger.warning(f'OK? | {proc}')
                    
                    # if ('Successfully received' in str(proc.stdout)):
                    #     errors += f"SSL поставленна успешнно!"
                    # else:
                    errors += f"Вывод: {proc.stdout} \nОшибки: {proc.stderr} \n"
 
                except subprocess.CalledProcessError as e:
                    loger.warning(f'\n\n\nWP ERROR: {e.output}\n\n\n')
                    errors += str(e.output)
        else:
            errors += 'Вы не можете больше ставить SSL на этот сайт сегодня\n'

        return errors

     # CYCLES
    def duplicate(self, iswar, withssl, apache_version, need_config, need_new_folder, need_bd):

        errors = ''
        
        if need_config: self.create_apache_nginx(iswar, False, withssl, apache_version)
        time.sleep(1)

        if need_new_folder: errors += self.copy_folder()
        time.sleep(1)

        if need_bd: errors += self.create_sql()

        if (iswar and need_config):
            errors += self.apache_nginx_confirm()
            self.create_apache_nginx(iswar, True, withssl, apache_version)
        
        errors += reload()

        return errors

    def create_new(self, empty, iswar, withssl, archive_type, apache_version = ''):

        errors = ''

        if iswar == 0:
            self.create_apache_nginx(True, False, withssl, apache_version) 
        else:
            self.create_apache_nginx(False, False, withssl, apache_version) 
        time.sleep(1)

        errors += self.create_sql(True)
        time.sleep(1)

        errors += self.create_new_folder(empty, archive_type)
        errors += reload()

        return errors


class LoginuserController:
    def __init__(self, username, password, ip) -> None:
        
        self.ip = ip
        self.username = username
        self.password = password
        self.hash_password = hashlib.sha256(password.encode()).hexdigest()
        loger.warning(f'Start working LOGINCONTROLLER for {ip}\n.')


    def check_user(self):
        query = f'SELECT * FROM Users WHERE username = "{self.username}"'
        try:
            data = self._sql_command(query)
            for i in data:
                if i[2] == self.hash_password:
                    loger.warning(f'User {self.ip} logined!')
                    return str(i[3])

        except Exception as e:
            loger.error(f'ERROR: {e}')
        loger.warning(f'Access denied to {self.ip}')

    # Unique sql command
    def _sql_command(self, query):
        cnx = mysql.connector.connect(user=dbuser, password=dbpassword, host=host)

        cursor = cnx.cursor()
        cursor.execute(f'USE dbname;')

        cursor.execute(query)

        result = cursor.fetchall()
        # loger.warning(f'Fetch result: {result}')
        cnx.close()
        return result


class UserController:
    def __init__(self) -> None:
        loger.warning('Starting USER CONTROLLER...')

    def create_user(self, username, password, access):
        errors = ''
        query = "INSERT INTO Users (username, password, access) VALUES (%s, %s, %s);"
        hash_password = hashlib.sha256(password.encode()).hexdigest()
        loger.warning(f'Creating new User, username: {username} ; hash_password: {hash_password}, access: {access}')
        val = (username, hash_password, int(access))

        errors += self._sql_command(query, val)
        return errors
        
    def delete_user(self, username):
        errors = ''
        query = f"DELETE FROM Users WHERE Users.username = '{username}'"
        loger.warning(f'Deleting user {username}')
        errors += self._sql_command(query)
        return errors

    def list_user(self):
        query = f'SELECT * FROM Users'

        result = self._sql_command(query)
        return result

    def _sql_command(self, query, val=''):
        try:
            cnx = mysql.connector.connect(user=dbuser, password=dbpassword, host=host)
        except Exception as e:
            loger.critical(f'Connection error: {e}, close connect;')
            data = "Проблема подключения"
        
        loger.warning(f'Sql command: {query}')
        cursor = cnx.cursor()

        cursor.execute(f'USE dbname;')
        try:
            cursor.execute(query, val)
            loger.warning('OK')
        except Exception as e:
            cursor.execute(query, val, multi=True)
            loger.warning(f'Multi=True Activated: Exception: {e}')

        try:
            rows = cursor.fetchall()
            data = []
            for i in rows:
                temp = {
                    "username": i[1],
                    "access": i[3],
                }
                data.append(temp)
        
            if (len(data) == 0):
                data = ''

        except Exception as e:
            data = ''
            loger.warning(f'Nothing to fetch? | {e}')

        cursor.close()
        cnx.commit()
        cnx.close()

        return data


class DeleteController:
    def __init__(self, site_name) -> None:
        self.site_name = site_name
        self.site_domain = site_name

        if isrus(site_name):
            self.site_domain = pyunycode.convert(self.site_name)
            self.site_name = check_punycode_domain(self.site_name)

            loger.warning(f'Russian site name... New site domain: {self.site_domain}, new site folder: {self.site_name}')


    def drop_database(self):
        errors = ''
        try:
            query = f'DROP DATABASE `{self.site_name}`'
            sql_command(query)    
        except Exception as e:
            loger.error(f'Exception {e}')
            errors += 'Ошибка удаления базы данных\n'

        try:
            query = f"DROP USER '{self.site_name}'@'{usertype}';"
            sql_command(query)
        except Exception as e:
            loger.error(f'Exception {e}')
            errors += 'Ошибка удаления пользователя\n'

        return errors

    def drop_files(self):
        errors = ''
        loger.warning(f'Delete folder /hosting/{self.site_name}...')
        try:
            shutil.rmtree(f'/hosting/{self.site_name}')
            loger.warning(f'OK')
        except Exception as e:
            loger.error(f'ERROR: {e} / Already deleted?')
        

        loger.warning(f'Delete file /etc/apache2-php8.0/sites-dev/{self.site_name}...')
        try:
            os.remove(f'/etc/apache2-php8.0/sites-dev/{self.site_name}')
            loger.warning(f'OK')
        except Exception as e:
            loger.error(f'ERROR: {e} / Already deleted?')
        

        loger.warning(f'Delete file /etc/apache2-php8.0/sites-enabled/{self.site_name}...')
        try:
            os.remove(f'/etc/apache2-php8.0/sites-enabled/{self.site_name}')
            loger.warning(f'OK')
        except Exception as e:
            loger.error(f'ERROR: {e} / Already deleted?')
       
        loger.warning(f'Delete file /etc/apache2-php7.3/sites-dev/{self.site_name}...')
        try:
            os.remove(f'/etc/apache2-php7.3/sites-dev/{self.site_name}')
            loger.warning(f'OK')
        except Exception as e:
            loger.error(f'ERROR: {e} / Already deleted?')
        

        loger.warning(f'Delete file /etc/apache2-php7.3/sites-enabled/{self.site_name}...')
        try:
            os.remove(f'/etc/apache2-php7.3/sites-enabled/{self.site_name}')
            loger.warning(f'OK')
        except Exception as e:
            loger.error(f'ERROR: {e} / Already deleted?')

        loger.warning(f'Delete file /etc/nginx/sites-dev/{self.site_name}...')
        try:
            os.remove(f'/etc/nginx/sites-dev/{self.site_name}')
            loger.warning(f'OK')
        except Exception as e:
            loger.error(f'ERROR: {e} / Already deleted?')
        

        loger.warning(f'Delete file /etc/nginx/sites-enabled/{self.site_name}...')
        try:
            os.remove(f'/etc/nginx/sites-enabled/{self.site_name}')
            loger.warning(f'OK')
        except Exception as e:
            loger.error(f'ERROR: {e} / Already deleted?')

        try:
            command = shlex.split(f'sh {path_to_app}/app/resources/delete_ssl.sh {self.site_domain}')
            a = subprocess.check_output(command, stderr=subprocess.STDOUT)  
            loger.warning(f'\n\n\certbot delete returncode: {a}\n\n\n')
        except subprocess.CalledProcessError as e:
            loger.warning(f'\n\n\nERROR: {e.output}\n\n\n')
            errors += str(e.output)

        return errors


    def site_delete(self):
        errors = ''
        loger.warning('Drop User and Database...')
        try:
            errors += self.drop_database()
            loger.warning('OK')
        except Exception as e:
            loger.warning(f'Error: {e}')
            errors += 'Критическая ошибка удаления БД!'

        loger.warning('Drop files...')
        try:
            errors += self.drop_files()
            loger.warning('OK')
        except Exception as e:
            loger.warning(f'Error: {e}')
            errors += 'Критическая ошибка удаления файлов!'
    
        return errors


class AddSslController:
    def __init__(self, site_name, ip) -> None:
        
        self.ip = ip
        self.site_name = site_name

        # DEFAULT
        self.site_domain = site_name
        self.site_folder = site_name

        if isrus(site_name):
            self.site_folder = check_punycode_domain(self.site_name)
            self.site_domain = pyunycode.convert(self.site_name)
            loger.warning(f'Russian site name... New folder: {self.site_folder}; New domain: {self.site_domain}')

        loger.warning(f'New site domain: {self.site_domain}\nNew site folder: {self.site_folder}')

        self.domain = ''
        splited_domain = self.site_domain.split('.')

        for i in range(len(splited_domain)):
            if i != len(splited_domain) - 1:
                self.domain += splited_domain[i]
            else:
                break

    def addssl(self, certbot, wp_cli, nginx):
        
        certbot = True if certbot == 'true' else False
        wp_cli = True if wp_cli == 'true' else False
        nginx = True if nginx == 'true' else False
        
        errors = ''
        if certbot:
            if ssl_install_constaint(self.site_folder, self.ip) == False: return 'Вы не можете больше ставить SSL на этот сайт сегодня'
            loger.warning(f'Splitted domain: {self.domain}\nStarting certbot')

            try: 
                command = shlex.split(f'certbot certonly --noninteractive --agree-tos --webroot -w /var/www -d {self.site_domain} -d www.{self.site_domain}')
                proc = subprocess.run(command, capture_output=True)
        
                loger.warning(f'OK? | {proc}')
                if (proc != 0):
                    errors += "Вывод: " + str(proc.stdout) + '\n' + 'Ошибки:' + str(proc.stderr) + '\n'
 
            except subprocess.CalledProcessError as e:
                loger.warning(f'\n\n\nWP ERROR: {e.output}\n\n\n')
                errors += str(e.output)

        if wp_cli:
            loger.warning(f'wp search-replace "http://{self.domain}" "https://{self.domain}" --precise --all-tables --allow-root on /hosting/{self.site_folder}')
            try:
                os.chdir(f'/hosting/{self.site_folder}')

                command = shlex.split(f'wp search-replace "http://{self.domain}" "https://{self.domain}" --precise --all-tables --allow-root')
                proc = subprocess.run(command, shell=False)
                loger.warning(f'returncode: {proc.returncode}')
                if (proc.returncode != 0):
                    errors += 'Ошибка замены ссылок - обратитесь к программисту!\n'

            except Exception as e:
                errors += 'Ошибка WP search-replace (В замене ссылок в бд)'
                loger.critical(f'Error: {e}')

        if nginx:
            try:
                with open(f'/etc/nginx/sites-enabled/{self.site_folder}', 'r') as f:
                    file = f.read()

                file = file.replace('#', '')

                with open(f'/etc/nginx/sites-enabled/{self.site_folder}', 'w') as f:
                    f.write(file)
                loger.warning('OK')

            except Exception as e:
                loger.critical('File not replaced... ' + str(e))
                errors += 'Ошибка замены конфигов\n'

        errors += reload() + '\n'

        return errors


    def removessl(self, certbot, wp_cli, nginx):
        
        certbot = True if certbot == 'true' else False
        wp_cli = True if wp_cli == 'true' else False
        nginx = True if nginx == 'true' else False


        loger.critical(f'cert: {certbot} {type(certbot)}')


        errors = ''
        if wp_cli:
            loger.warning(f'wp search-replace "https://{self.domain}" "http://{self.domain}" --precise --all-tables --allow-root on /hosting/{self.site_folder}')
            try:
                os.chdir(f'/hosting/{self.site_folder}')

                command = shlex.split(f'wp search-replace "https://{self.domain}" "http://{self.domain}" --precise --all-tables --allow-root')
                proc = subprocess.run(command, shell=False)
                loger.warning(f'returncode: {proc.returncode}')
                if (proc.returncode != 0):
                    errors += 'Ошибка замены ссылок - обратитесь к программисту!\n'

            except Exception as e:
                errors += 'Ошибка WP search-replace (В замене ссылок в бд)'
                loger.critical(f'Error: {e}')

        if nginx:
            try:

                php_version = 'proxy_http_php80'
                with open(f'/etc/nginx/sites-enabled/{self.site_folder}', 'r') as f:
                    file = f.read()
                    if 'proxy_http_php73' in file:
                        php_version = 'proxy_http_php73'


                with open(f'{path_to_app}/app/resources/config/nginx-war.config', 'r') as f:
                    file = f.read()
                    file.replace('proxy_htpp_php73', php_version)

                file = file.replace("DOMAIN", self.site_domain)
                file = file.replace("FOLDER", self.site_folder)

                with open(f'/etc/nginx/sites-enabled/{self.site_folder}', 'w') as f:
                    f.write(file)
                loger.warning('OK')

            except Exception as e:
                loger.critical('File not replaced... ' + e)
                errors += 'Ошибка замены конфигов\n'
        

        if certbot:
            try:
                command = shlex.split(f'sh {path_to_app}/app/resources/delete_ssl.sh {self.site_domain}')
                a = subprocess.check_output(command, stderr=subprocess.STDOUT)  
                loger.warning(f'\n\n\certbot delete returncode: {a}\n\n\n')
            except subprocess.CalledProcessError as e:
                loger.warning(f'\n\n\nERROR: {e.output}\n\n\n')
                errors += str(e.output)


        return errors


class SettingsController:
    def __init__(self, ip) -> None:
        self.domain = ''
        self.ip = ip
        
        loger.warning(f'Start working SettingsController for {self.ip}')


    def write_domains(self):
        with open(f'{path_to_app}/logs/domain.txt', 'w') as f:
            f.write(f' ')

        for i in os.listdir('/etc/nginx/sites-enabled'):
            
            file = ''
            loger.warning('Copying domains... ')

            try:
                with open(f'/etc/nginx/sites-enabled/{i}', 'r') as f:
                    file = f.read()

                file_splitted = file.split('\n')
                for j in file_splitted:
                    if ('server_name' in j):
                        self.domain = j.split(' ')
                        break

                with open(f'{path_to_app}/logs/domain.txt', 'a') as f:
                    f.write(f'site name: {i} | site domain: {self.domain[1]}\n')
                loger.warning('OK')

            except Exception as e:
                loger.critical(f'ERROR: {e}')
                return "Ошибка, чекайте логи"
            
            return "Успешно"
            

    def check_domains(self):

        try:
            cnx = mysql.connector.connect(user=dbuser, password=dbpassword, host='192.168.1.151')
        except Exception as e:
            loger.critical(f"ERROR: {e}")
            return 'Ошибка подключения БД'
        
        loger.warning("Check Domains")
        val = list()

        with open(f'{path_to_app}/logs/DomainsStats.log', 'w', encoding="utf-8") as f:
            f.write(f'Domains created by {self.ip}\n')
        
        query = 'TRUNCATE dbname.Domains;'
        sql_command(cnx, query)

        for i in os.listdir('/hosting'):

            query = 'INSERT INTO dbname.Domains (domainname, lastdata, ifssl) VALUES (%s, %s, %s);'
            try:
                pop = Popen(f'stat -c "%y" /hosting/{i}', shell=True, stdout=PIPE).stdout
                stat = (str(pop.read()).split(" ")[0]).replace('\'b', '')
            except:
                stat = ''

            ssl_avaliable = False

            try:
                with open(f'/etc/letsencrypt/renewal/{i}.conf') as f:
                    ssl_avaliable = True
            except:
                pass

            
            val = (i, stat, ssl_avaliable)

            sql_command(cnx, query, val)

            with open(f'{path_to_app}/logs/DomainsStats.log', 'a', encoding="utf-8") as f:
                f.write(f'Domain Name: {i} | Last Update: {stat} | Have SSL: {ssl_avaliable}\n')

        cnx.commit()
        cnx.close()
        return self.domain
    
    # Unique SQL
    def _sql_command(self, cnx, query, val=''):
        loger.warning(f'Sql command: {query}')
        cursor = cnx.cursor()
        if val == '':
            try:
                cursor.execute(query)
                loger.warning('OK')
            except Exception as e:
                cursor.execute(query, multi=True)
                loger.warning(f'Multi=True Activated: Exception: {e}')
        else:
            try:
                cursor.execute(query, val)
                loger.warning('OK')
            except Exception as e:
                cursor.execute(query, val, multi=True)
                loger.warning(f'Multi=True Activated: Exception: {e}')
        cursor.close()



class FtpController:
    def __init__(self, site_domain) -> None:
        self.site_domain = site_domain

        if isrus(self.site_domain):
            self.site_domain = pyunycode.convert(self.site_domain)

        self.site_short_domain = ''
        self.splited_domain = self.site_domain.split('.')

        for i in range(len(self.splited_domain)):
            if i != len(self.splited_domain) - 1:
                self.site_short_domain += self.splited_domain[i]
            else:
                break
        
        
    def give_ftp(self):

        command = shlex.split(f'sh {path_to_app}/app/resources/ftp.sh {self.site_domain} {self.site_short_domain}')
        loger.critical(f'\n{command}\n')
        a = subprocess.run(command)
        file = ''
        if (a.returncode == 0):
            with open(f'{path_to_app}/app/resources/ftp_hosts_example.txt', 'r') as f:
                file = f.read()
            
            file = file.replace('DOMAIN', self.site_short_domain)
        else:
            file = 'Ошибка!'
            
        return file
    
    def delete_ftp(self):
        
        strokes = []
        
        file = ''
        with open('/etc/passwd', 'r') as f:
            file = f.read()
            
        file = file.split('\n')
        changed_file = ''
        
        for stroke in file:
            if (self.site_domain in stroke):
                strokes.append(stroke)
                continue
            changed_file += stroke + '\n'
            
        with open('/etc/passwd', 'w') as f:
            f.write(changed_file)
            
        file = ''
        with open('/etc/passwd-', 'r') as f:
            file = f.read()
            
        file = file.split('\n')
        changed_file = ''
        
        for stroke in file:
            if (self.site_domain in stroke):
                strokes.append(stroke)
                continue
            changed_file += stroke + '\n'
            
        with open('/etc/passwd-', 'w') as f:
            f.write(changed_file)
            
        return strokes[0] + '\n' + strokes[1]



class IpController:
    def __init__(self, ip):
        self.ip = ip

    def unban(self):
        loger.error(f'Unban user {self.ip}..')

        a = subprocess.check_output(f'f2b-remote --unban --subnet --ip {self.ip}', shell=True)
        loger.error(f"first command: {a}")
        
        a = subprocess.check_output(f'f2b-remote --unban --ip {self.ip}', shell=True)
        loger.error(f"Second command: {a}")

    def ban(self):
        loger.error(f'Ban user {self.ip}..')

        a = subprocess.check_output(f'f2b-remote --subnet --ip {self.ip}', shell=True)
        loger.error(f"Command output: {a}")


class DomainsController:
    def __init__(self) -> None:
        pass 


    def get_domains(self, search='', sort_revert=False):

        not_json_fetch = self.sql_fetch(search, sort_revert)
        return_data = []
        for element in not_json_fetch:

            temp_data = {
            "site_name": element[1],
            "site_folder": element[2],
            "file_name": element[3],
            "decoded_name": element[4],
            "site_hosting": element[5],
            "site_php": element[6],
            "ssl_avaliable": element[7],
            "site_weight": element[8],
            }
            return_data.append(temp_data)
        
        return return_data
    
      
    def sql_fetch(self, search, sort_revert):
        cnx = mysql.connector.connect(user=dbuser, password=dbpassword, host=host,)
        cursor = cnx.cursor()

        cursor.execute(f'USE dbname;')
        loger.critical(f'\n\n{sort_revert == "true"} | {sort_revert}\n\n')
        query_asc = 'DESC' if sort_revert == 'true' else 'ASC'
        query_add = f"WHERE (site_name LIKE '%{search}%' OR site_folder LIKE '%{search}%' OR decoded_name LIKE '%{search}%' OR site_php LIKE '%{search}%')"
        query = f'SELECT * FROM Domains {query_add} ORDER BY site_weight {query_asc}'
        loger.warning(f'{query}')
        cursor.execute(query)

        result = cursor.fetchall()
        cursor.close()
        cnx.close()
        return result


class SaveDomainController():
    def __init__(self, names, ip) -> None:

        loger.warning(f'Start working SaveDomain for {ip}')
        self.site_names = names.split('\n')


    def copy_site(self, site_folder):
        loger.warning('copying site...')
        try:
            shutil.copytree(f'/hosting/{site_folder}', f'{path_to_app}/temp/{site_folder}/{site_folder}')
            loger.warning('OK')
        except Exception as e:
            loger.critical(f'Error: {e}')


    def dump_db(self, site_folder):
        loger.warning('Start copying DB...')
        try:
            subprocess.run(f'mysqldump -h {host} -u {dbuser} -p{dbpassword} {site_folder} > {path_to_app}/temp/{site_folder}/{site_folder}-db.sql', shell=True)
            loger.warning(f'dump OK')
        except Exception as e:
            loger.critical(f"Error: {e}")


    def mybackup(self, arch, folder_list, mode):
        # Счетчики
        num = 0
        # Создание нового архива
        z = zipfile.ZipFile(arch, mode, zipfile.ZIP_DEFLATED, True)
        # Получаем папки из списка папок.
        for add_folder in folder_list:
            # Список всех файлов и папок в директории add_folder
            for root, dirs, files in os.walk(add_folder):
                for file in files:
                    path = os.path.join(root, file)
                    z.write(path)
                    print(num, path)
                    num += 1
        z.close()



    def cycle(self):

        for name in self.site_names:

            if (name == ''):
                continue

            name = name.replace("https://", '')
            name = name.replace("http://", '')
            name = name.replace("/", '')
            name = name.replace(' ', '')
            name = name.replace('\r', '')
            site_folder = name
            site_domain = name

            if isrus(name):
                site_folder = check_punycode_domain(site_folder)
                site_domain = pyunycode.convert(name)
              
                
            loger.warning(f'site folder: {site_folder}\n')
            loger.warning(f'site name: {site_domain}\n\n')

            self.copy_site(site_folder)
            self.dump_db(site_folder)
        
        self.mybackup(f'{path_to_app}/static/files/{site_folder}.zip', [f'{path_to_app}/temp/{site_folder}'], 'w')
        return f'static/files/{site_folder}.zip'


class BDController:
    def __init__(self, site_name, new_site_name='') -> None:
        self.site_folder = site_name
        self.site_domain = site_name

        self.new_site_folder = new_site_name
        self.new_site_domain = new_site_name

        if isrus(site_name):
            self.site_folder = check_punycode_domain(self.site_folder)
            self.site_domain = pyunycode.convert(self.site_domain)

        if isrus(new_site_name) and new_site_name != '':
            self.new_site_folder = check_punycode_domain(new_site_name)
            self.new_site_domain = pyunycode.convert(new_site_name)


    def save_bd(self):

        errors = ''

        try:
            subprocess.run(f'mysqldump -h {host} -u {dbuser} -p{dbpassword} {self.site_folder} > {path_to_app}/static/files/{self.site_folder}-db.sql', shell=True)
            loger.warning(f'dump OK')

        except Exception as e:
            loger.error(f'ERROR: {e}')
            errors += f'{e} = (Проблема с экспортом БД)'

        return {
            'errors': errors,
            'bd': f'static/files/{self.site_folder}-db.sql'
        }
    
    def load_bd(self, bd_file):

        errors = ''

        unpack_path = f'{path_to_app}/temp/{self.site_folder}'
        filename = secure_filename(bd_file.filename)
        try:
            bd_file.save(f'{unpack_path}-db.sql')


            subprocess.run(f'mysql -h {host} -u {dbuser} -p{dbpassword} {self.site_folder} < {unpack_path}-db.sql', shell=True)
            loger.warning(f'insert OK')

        except Exception as e:
            loger.error(f'ERROR: {e}')
            errors += f'{e} = (Проблема с импортом БД)'

        return errors
    

    def wp_cli_bd(self, http_text):

        errors = ''

        http = 'http' if http_text == 'true' else 'https'
        https = 'https' if http_text == 'true' else 'http'
        old_site_option_value = self.get_wp_options_url().split('/')[2]
        loger.critical(f'OLD SITE OPTION VALUE: {old_site_option_value}')
        try:
            loger.warning(f'wp search-replace "{http}://{self.site_domain}" "{https}://{self.site_domain}" --precise --all-tables --allow-root')
            os.chdir(f'/hosting/{self.site_folder}')
            command = shlex.split(f'wp search-replace "{http}://{self.site_domain}" "{https}://{self.site_domain}" --precise --all-tables --allow-root')
            a = subprocess.check_output(command, stderr=subprocess.STDOUT)  
            loger.warning(f'WP-CLI output: {a}')

        except subprocess.CalledProcessError as e:
            loger.warning(f'\n\n\nWP ERROR: {e.output}\n\n\n')
            errors += str(e.output)

        if self.new_site_domain != '':
            try:
                os.chdir(f'/hosting/{self.site_folder}')
                command = shlex.split(f'wp search-replace "{old_site_option_value}" "{self.new_site_domain}" --precise --all-tables --allow-root')
                a = subprocess.check_output(command, stderr=subprocess.STDOUT)  
                loger.warning(f'WP-CLI output: {a}')

            except subprocess.CalledProcessError as e:
                loger.warning(f'\n\n\nWP ERROR: {e.output}\n\n\n')
                errors += str(e.output)

        return errors
    
    def drop_database(self):
        errors = ''
        try:
            query = f'DROP DATABASE `{self.site_domain}`'
            sql_command(query)    
        except Exception as e:
            loger.error(f'Exception {e}')
            errors += 'Ошибка удаления базы данных\n'

        return errors
    
    def drop_user(self):
        errors = ''
        try:
            query = f"DROP USER '{self.site_domain}'@'{usertype}';"
            sql_command(query)
        except Exception as e:
            loger.error(f'Exception {e}')
            errors += 'Ошибка удаления пользователя\n'

        return errors

    def get_wp_options_url(self):
        try:
            cnx = mysql.connector.connect(user=dbuser, password=dbpassword, host=host, database=self.site_folder)
        except Exception as e:
            loger.critical(f'Connection error: {e}, close connect;')
            return
            
        query = f'SELECT option_value FROM wp_options where option_name = "siteurl"'
        loger.warning(f'Sql command: {query}')
        cursor = cnx.cursor()

        try:
            cursor.execute(query)
            result = cursor.fetchone()
            loger.warning('OK')
        except Exception as e:
            cursor.execute(query, multi=True)
            loger.warning(f'Multi=True Activated: Exception: {e}')

        cursor.close()
        cnx.close()
        return result[0]

    

# GLOBAL FUNCTIONS

# Russian symbols check
def isrus(site_name):
    for i in site_name:
        if i in alphabet:
            return True
    return False

# SQL command execute
def sql_command(query, val=''):

    try:
        cnx = mysql.connector.connect(user=dbuser, password=dbpassword, host=host)
    except Exception as e:
        loger.critical(f'Connection error: {e}, close connect;')
        return
        
    loger.warning(f'Sql command: {query}')
    cursor = cnx.cursor()

    try:
        cursor.execute(query, val)
        loger.warning('OK')
    except Exception as e:
        cursor.execute(query, val, multi=True)
        loger.warning(f'Multi=True Activated: Exception: {e}')

    cursor.close()
    cnx.close()

# Check punycode from BD
def check_punycode_domain(site_name):
    try:
        cnx = mysql.connector.connect(user=dbuser, password=dbpassword, host=host, database=database)
    except Exception as e:
        loger.critical(f'Connection error: {e}, close connect;')
        return
    
    query = f'SELECT site_folder FROM Domains WHERE decoded_name LIKE "{site_name}"'
    loger.warning(query)
    cursor = cnx.cursor()

    try:
        cursor.execute(query)
        result = cursor.fetchone()
        loger.warning(f'OK: {result}')
    except Exception as e:
        loger.warning(f'Error: {e}')

    cursor.close()
    cnx.close()

    try:
        if len(result) == 0:
            return_val = translit(site_name, 'ru', reversed=True).replace('\'', '')
        else:
            return_val = result[0]
    except:
        return_val = translit(site_name, 'ru', reversed=True).replace('\'', '')
    return return_val


# Reload Server
def reload():
    loger.warning('\n\nReloading server...\n\n')

    errors = ''

    try:
        command = shlex.split('nginx -t')
        a = subprocess.check_output(command, stderr=subprocess.STDOUT)  
        loger.warning(f'\n\n\nRelaod returncode: {a}\n\n\n')
    except subprocess.CalledProcessError as e:
        loger.warning(f'\n\n\nERROR: {e.output}\n\n\n')
        errors += str(e.output)

    return errors


def ssl_install_constaint(site_name, ip):

    loger.warning('ssl constraing start')
    ignore_list = [
        '0.0.0.0'
    ]

    for i in ignore_list:
        if i == ip:
            loger.warning(f'ip {ip} igoner!')
            return True

    log_path = f'{path_to_app}/logs/ssl_constraint.txt'
    file = ''

    # Проверка наличия лога
    try: 
        with open(log_path, 'r') as f:
            for row in f.read().split('\n'):

                add_info = ''

                if (ip in row) and (site_name in row):
                    if ('second try' in row):
                        return False      
                    else:
                        add_info = ' second try'
                file += row + add_info + '\n'

        with open(log_path, 'w') as f:
            f.write(file)

    except:
        with open(log_path, 'w') as f:
            f.write('StartSSlConstraint\n')

    with open(log_path, 'a') as f:
        f.write(f'{ip} | {site_name}\n')

    return True
        

def check_for_ns(site_domain):

    loger.warning('CHECK NS AND ADDRESSES')
    try: 
        command = shlex.split(f'nslookup -type=any {site_domain}')
        proc = subprocess.run(command, capture_output=True)

        loger.warning(f'OK? | {proc}')
        
        address = '255.255.255.255'
        loger.warning(f'Output: {proc.stdout}')
        if (address in proc.stdout):
            return True
            
    except subprocess.CalledProcessError as e:
        loger.warning(f'\n\n\nWP ERROR: {e.output}\n\n\n')
        return False

    return False

def init_controller(ip):
    file_ip_handler = logging.FileHandler(f'{path_to_app}/logs/{ip}.log', mode='a')
    file_ip_handler.setFormatter(formatter)
    loger.addHandler(file_ip_handler)
