#FLASK =============================================
from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
#ПРОЧЕЕ =============================================
import logging
import webbrowser
import time
import os
#КАСТОМ =============================================
from app.controllers import reload
from app.controllers import init_controller
from app.controllers import CreateController
from app.controllers import LoginuserController
from app.controllers import DeleteController
from app.controllers import AddSslController
from app.controllers import SettingsController
from app.ipdestroyer import IpDestroyer
from app.controllers import IpController
from app.controllers import UserController
from app.controllers import FtpController
from app.controllers import DomainsController
from app.controllers import SaveDomainController
from app.controllers import BDController
from app.admin import ParserController
from app.admin import AutoSSLUpdater
from app.admin import PageAdmin
from app import config

from app.kloger import KLoger

path_to_app = config.PATH_TO_APP

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


# Фласк
app = Flask(__name__)
app.secret_key = "djiruhytvuy5vf5w4uuerjwtc09w3othp4weitcui34"
bootstrap = Bootstrap5(app)

# ERROR HANDLERS

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.errorhandler(500)
def page_wrong(e):
    return redirect(url_for('login'))

# ROUTES

@app.route('/')
def index():
    session['ip'] = request.remote_addr
    init_logger(request.remote_addr)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    session['ip'] = request.remote_addr
    init_logger(request.remote_addr)
    return render_template('login.html')

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if not login_check(2):
        return redirect('/pes')

    return render_template('dashboard.html',
        username = session['username'])

@app.route('/add_domain', methods=['GET','POST'])
def add_domain():
    if not login_check(2):
        return redirect('/pes')

    return render_template('add_domain.html')

@app.route('/create_domain', methods=['GET', 'POST'])
def create_domain():
    if not login_check(2):
        return redirect('/pes')

    return render_template('create_domain.html')

@app.route('/save_domain', methods=['GET', 'POST'])
def save_domain():
    if not login_check(2):
        return redirect('/pes')

    return render_template('save_domain.html')

@app.route('/all_domain', methods=['GET','POST'])
def all_domain():
    if not login_check(2):
        return redirect('/pes')

    return render_template('all_domain.html')

@app.route('/add_ssl', methods=['GET', 'POST'])
def add_ssl():
    if not login_check(2):
        return redirect('/pes')
    
    return render_template('add_ssl.html')

@app.route('/all_ssl', methods=['GET','POST'])
def all_ssl():
    if not login_check(2):
        return redirect('/pes')

    return render_template('all_ssl.html')

@app.route('/del_domain', methods=['GET','POST'])
def del_domain():  
    if not login_check(2):
        return redirect('/pes')

    return render_template('del_domain.html')

@app.route('/servers', methods=['GET','POST'])
def server():
    if not login_check(0):
        return redirect('/pes')

    return render_template('servers.html')

@app.route('/perenos', methods=['GET', 'POST'])
def perenos():
    if not login_check(0):
        return redirect('/pes')

    return render_template('perenos.html')

@app.route('/ip_unban', methods=['GET', 'POST'])
def ip_unban():
    if not login_check(2):
        return redirect('/pes')

    return render_template('ip_unban.html')

@app.route('/ip_ban', methods=['GET', 'POST'])
def ip_ban():
    if not login_check(2):
        return redirect('/pes')

    return render_template('ip_unban.html')

@app.route('/add_ftp', methods = ['GET', 'POST'])
def add_ftp():
    if not login_check(2):
        return redirect('/pes')
        
    return render_template('add_ftp.html')

@app.route('/users', methods = ['GET', 'POST'])
def users():
    if not login_check(0):
        return redirect('/pes')
        
    return render_template('users.html')

@app.route('/manuals')
def manuals():
    return render_template('manuals.html') 

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('access', None)
    return redirect(url_for('login'))

@app.route('/bd')
def bd():
    if not login_check(0):
        return redirect('/pes')
        
    return render_template('bd.html')

@app.route('/info/<page_name>', methods = ['GET', 'POST'])
def info_page(page_name):
    if not login_check(3):
        return redirect('/pes')
    
    return render_template(f'page.html', page_name=page_name) 


# API

@app.route('/api/login', methods=['GET', 'POST'])
def api_login():

    username = request.form['username']
    password = request.form['password']

    logincontroller = LoginuserController(username, password, session['ip'])
    validate = logincontroller.check_user()

    if validate != '':

        session['username'] = username
        session['access'] = validate
        loger.warning(f'Logined by: {session["username"]}')
        return "1"

    loger.warning(f'Wrong password for {session["ip"]}; user: {username}')
    return 'Неверное имя пользователя или пароль!'

@app.route('/api/add_domain', methods=['GET', 'POST'])
def api_add_domain():

    sitetype = request.form['sitetype']
    old_site_name = request.form["old_site_name"]
    new_site_name = request.form["new_site_name"]
    withssl = request.form['ssl']
    apache = request.form['apache']

    need_config = request.form['need_config']
    need_new_folder = request.form['need_new_folder']
    need_bd = request.form['need_bd']

    if (sitetype == '0'):
        controller = CreateController(new_site_name, 'minisite.grampus-server.ru', '', session['ip'])
        error = controller.duplicate(True, withssl, apache, need_config, need_new_folder, need_bd)
    elif(sitetype == '1'):
        controller = CreateController(new_site_name, old_site_name, '', session['ip'])
        error = controller.duplicate(False, withssl, apache, need_config, need_new_folder, need_bd)
    elif(sitetype == '2'):
        controller = CreateController(new_site_name, old_site_name, '', session['ip'])
        error = controller.duplicate(True, withssl, apache, need_config, need_new_folder, need_bd)
    else:
        error = 'Функция временно отключена :('

    loger.critical(error)

    return error

@app.route('/api/create_domain', methods=['GET', 'POST'])
def api_create_domain():
    sitetype = request.form['sitetype']
    site_name = request.form['site_name']
    sitewar = request.form['sitewar']
    withssl = request.form['withssl']
    archive_type = request.form['archive-type']
    archive = request.files.get('archive')


    errors = ''
    controller = CreateController(site_name, 'CreatingNewSite', archive, session['ip'])
    errors = controller.create_new(int(sitetype), int(sitewar), int(withssl), int(archive_type))
    return errors

@app.route('/api/save_domain', methods=['GET', 'POST'])
def api_save_domain():

    site_names = request.form['input']

    errors = ''
    controller = SaveDomainController(site_names, session['ip'])
    errors = controller.cycle()
    return errors

@app.route('/api/ssl/add', methods=['GET', 'POST'])
def api_add_ssl():
    if not login_check(2):
        return redirect('/pes')
    
    errors = ''
    site_name = request.form['site_name']
    certbot = request.form['certbot']
    wp_cli = request.form['wp_cli']
    nginx = request.form['nginx']

    controller = AddSslController(site_name, session['ip'])
    errors += controller.addssl(certbot, wp_cli, nginx)
    return errors

@app.route('/api/ssl/remove', methods=['GET', 'POST'])
def api_remove_ssl():
    if not login_check(2):
        return redirect('/pes')
    
    errors = ''
    site_name = request.form['site_name']
    certbot = request.form['certbot']
    wp_cli = request.form['wp_cli']
    nginx = request.form['nginx']

    controller = AddSslController(site_name, session['ip'])
    errors += controller.removessl(certbot, wp_cli, nginx)
    return errors

@app.route('/api/ssl/autoupdate', methods=['GET', 'POST'])
def api_autoupdate_ssl():
    if not login_check(0):
        return redirect('/pes')

    errors = ''
    controller = AutoSSLUpdater()
    errors += controller.parse()
    errors += controller.update()
    return errors

@app.route('/api/delete_domain', methods=['GET', 'POST'])
def api_delete_domain():
    if not login_check(2):
        return redirect('/pes')
    
    site_name = request.form['site_name']
    deletecontroller = DeleteController(site_name)
    errors = deletecontroller.site_delete()
    return errors

@app.route('/api/servers', methods=['GET', 'POST'])
def api_servers():

    settings = SettingsController(session['ip'])
    settings.check_domains()

    return ''

@app.route('/api/ip_destroy', methods=['GET', 'POST'])
def api_ip_destroy():

    api = request.form['apikey']
    url = request.form['url']
    destroyer = IpDestroyer(api, url)
    destroyer.parse()

    return ''

@app.route('/api/ip_unban', methods=['GET', 'POST'])
def api_ip_unban():

    ip = request.form['ip']
    ipcontroller = IpController(ip)
    ipcontroller.unban()

    return ''

@app.route('/api/ip_ban', methods=['GET', 'POST'])
def api_ip_ban():
    ip = request.form['ip']
    ipcontroller = IpController(ip)
    ipcontroller.ban()

    return ''

@app.route('/api/ftp/add', methods=['GET', 'POST'])
def api_add_ftp():
    if not login_check(2):
        return redirect('/pes')
    site_name = request.form['site_name']

    ft = FtpController(site_name)
    errors = ft.give_ftp()
    return errors

@app.route('/api/ftp/remove', methods=['GET', 'POST'])
def api_remove_ftp():
    if not login_check(2):
        return redirect('/pes')
    site_name = request.form['site_name']

    ft = FtpController(site_name)
    errors = ft.delete_ftp()
    return errors

@app.route('/api/user/create', methods=['GET', 'POST'])
def api_user_create():
    if not login_check(0):
        return redirect('/pes')
    
    errors = ''
    username = request.form['user_login']
    password = request.form['user_password']
    access = request.form['user_access']

    usercontroller = UserController()
    errors += usercontroller.create_user(username, password, access)
    return errors

@app.route('/api/user/delete', methods=['GET', 'POST'])
def api_user_delete():
    if not login_check(0):
        return redirect('/pes')
    
    errors = ''
    username = request.form['user_login']

    usercontroller = UserController()
    errors += usercontroller.delete_user(username)
    return errors

@app.route('/api/user/list', methods=['GET', 'POST'])
def api_user_list():
    if not login_check(0):
        return redirect('/pes')

    usercontroller = UserController()
    result = usercontroller.list_user()
    return result


@app.route('/api/parser', methods=['GET', 'POST'])
def api_parser():
    if not login_check(0):
        return redirect('/pes')

    parsecontroller = ParserController()
    site_count = parsecontroller.parse()
    return str(site_count)

@app.route('/api/domains/get', methods=['GET', 'POST'])
def api_domains_get():
    if not login_check(2):
        return redirect('/pes')
    
    search_input = request.form['search']
    sort_revert = request.form['sort_revert']
    domainscontroller = DomainsController()
    all_domain = domainscontroller.get_domains(search_input, sort_revert)

    return all_domain


@app.route('/api/bd/save',  methods=['GET', 'POST'])
def api_bd_save():
    if not login_check(0):
        return redirect('/pes')
    
    site_name = request.form['site_name']
    controller = BDController(site_name)
    errors = controller.save_bd()
    return errors


@app.route('/api/bd/load',  methods=['GET', 'POST'])
def api_bd_load():
    if not login_check(0):
        return redirect('/pes')
    
    site_name = request.form['site_name']
    bd_file = request.files.get('bd_file')

    controller = BDController(site_name)
    errors = controller.load_bd(bd_file)
    return errors


@app.route('/api/bd/replace',  methods=['GET', 'POST'])
def api_bd_replace():
    if not login_check(0):
        return redirect('/pes')
    
    errors = ''

    site_name = request.form['site_name']
    new_site_name = request.form['new_site_name']
    http_text = request.form['http_text']

    controller = BDController(site_name, new_site_name)
    errors = controller.wp_cli_bd(http_text)
    return errors


@app.route('/api/bd/delete_user',  methods=['GET', 'POST'])
def api_bd_delete_user():
    if not login_check(0):
        return redirect('/pes')
    
    site_name = request.form['site_name']
    controller = BDController(site_name)
    errors = controller.drop_user()
    return errors


@app.route('/api/bd/delete_database',  methods=['GET', 'POST'])
def api_bd_delete_database():
    if not login_check(0):
        return redirect('/pes')
    
    site_name = request.form['site_name']
    controller = BDController(site_name)
    errors = controller.drop_database()
    return errors

@app.route('/api/page/get_list', methods=['GET', 'POST'])
def api_page_get_list():
    if not login_check(0):
        return redirect('/pes')
    
    controller = PageAdmin()
    page_list = controller.load_page_list()

    return page_list


@app.route('/api/page/add_new', methods=['GET', 'POST'])
def api_page_add_new():
    if not login_check(0):
        return redirect('/pes')
    
    page_name = request.form['page_name']
    textarea = request.form['textarea']

    controller = PageAdmin()
    page_list = controller.save_page(page_name, textarea)

    return page_list
@app.route('/api/page/delete_page', methods=['GET', 'POST'])
def api_page_delete_page():
    if not login_check(0):
        return redirect('/pes')
    
    page_name = request.form['page_name']

    controller = PageAdmin()
    page_list = controller.delete_page(page_name)

    return page_list


@app.route('/api/page/load_page', methods=['GET', 'POST'])
def api_page_load_page():
    if not login_check(0):
        return redirect('/pes')
    
    page_name = request.form['page_name']

    controller = PageAdmin()
    page_list = controller.load_page(page_name)

    return page_list


@app.route('/api/chown', methods=['GET', 'POST'])
def api_chown():
    if not login_check(0):
        return redirect('/pes')
    
    site_name = request.form['site_name']
    os.chdir('/hosting')
    os.system(f'chown -R 33:33 /hosting/{site_name}')

    return 'ok'

@app.route('/api/reload_server', methods=['GET', 'POST'])
def api_reload_server():
    if not login_check(0):
        return redirect('/pes')
    
    errors = _reload()

    return errors

# OTHER FUNCTIONS
def login_check(level_access):

    session['ip'] = request.remote_addr
    loger.warning(f'CHECKING {session["ip"]}')

    try:
        if int(session['access']) > level_access:
            loger.warning(f'{session["ip"]} low access level!')
            return False
        
        if session['username'] == '':
            loger.warning(f'{session["ip"]} user is not logined')
            return False
    except Exception as e:
        loger.warning(f'{session["ip"]} access denied | {e}')
        return False
    
    return True

def init_logger(ip):
    file_ip_handler = logging.FileHandler(f'{path_to_app}/logs/{ip}.log', mode='a')
    file_ip_handler.setFormatter(formatter)
    loger.addHandler(file_ip_handler)

    init_controller(ip)

if __name__ == '__main__':
    
    app.run(debug=False, host='0.0.0.0', port=8197)



def _reload():
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