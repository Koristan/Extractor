import jinja2
from flask import Flask, render_template, request, redirect, url_for
from flask_login import current_user, login_required, LoginManager
# Кастомные классы
# from logic.src.copyrighter import CopyProject
# from logic.src.apache2 import Apache2Creator
# from logic.src.nginx import NginxCreator
# from logic.src.all_domain import AllDomain
# from logic.src.add_role import AddRole


app = Flask(__name__)

alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ,()<>#$%^:;*_!"\'/?'
logined_user = ''
# Фиктивные данные для проверки авторизации
users = [
    {'username': 'user1', 'password': 'passwd1'},
    {'username': 'user2', 'password': 'passwd2'},
    {'username': 'user3', 'password': 'passwd3'},
    {'username': '1', 'password': '1'},
]

@app.route('/')
def home():
    # return 'Добро пожаловать на главную страницу!'
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    global logined_user
    logined_user = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Проверка введенных данных
        for user in users:
            if user['username'] == username and user['password'] == password:
                # Успешная авторизация
                logined_user = username
                return redirect(url_for('dashboard'))

        # Неверные данные, отображение ошибки
        error = 'Неверное имя пользователя или пароль'
        return render_template('login.html', error=error)

    # Отображение страницы авторизации
    return render_template('login.html')



@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    error = ''
    global logined_user
    if (logined_user == ''):
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            site_name = request.form['site_name']
            new_site_name = request.form['new_site_name']
            site_type = request.form.get('site_type')
        except:
            error='Неверный.'
        try:
            if (site_type == "1"):
                if (site_name != '' and new_site_name != '' and match(site_name) and match(new_site_name)):
                    duplicator = CopyProject(site_name, new_site_name)
                    ngcr = NginxCreator(new_site_name)
                    apa2 = Apache2Creator(new_site_name)

                    ngcr.create_nginx_file()
                    apa2.create_apache_file()
                    duplicator.copy()
                    error = "Успешно - шаблон"
                else:
                    error = "Неверные данные"
            if (site_type == "0"):
                if (new_site_name != '' and match(new_site_name)):
                    duplicator = CopyProject('minisite.grampus-server.ru', new_site_name)
                    ngcr = NginxCreator(new_site_name)
                    apa2 = Apache2Creator(new_site_name)

                    ngcr.create_nginx_file()
                    apa2.create_apache_file()
                    duplicator.copy()
                    error = "Успешно - минисайт"
                else:
                    error = "Неверные данные"
        except Exception as e:
            error = f'Ошибка: {e}'
    
    return render_template('dashboard.html',
                           username = logined_user,
                           error=error)


@app.route('/all_domain', methods=['GET', 'POST'])
def domains():
    all_dom = AllDomain()
    if request.method == 'POST':
        search_filter = request.form['search_input']
        domains = all_dom.check_filtered_catalog(search_filter)
        print(domains)
    else:
        domains = all_dom.check_domains()

    return render_template('all_domain.html',
                           domains = domains)

@app.route('/add_role', methods=['GET', 'POST'])
def roles():
   add_role = AddRole()
   if request.method == 'POST':
       print(roles)
   else:
       roles = add_role.check_roles()

   return render_template('add_role.html',
                          roles = roles)


def match(text):
    for i in text:
        if i in alphabet:
            return False
    return True

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')