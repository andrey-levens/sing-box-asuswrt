from flask import Flask, request, render_template_string, redirect, flash, session
import json
import os
import configparser
import platform
import subprocess
import time

app = Flask(__name__)
app.secret_key = 'sing-box-web'

# Путь к файлу конфигурации в той же директории, где находится скрипт
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.ini')
# Имя JSON-файла по умолчанию в директории скрипта
DEFAULT_JSON_NAME = 'my-ruleset.json'

# Загрузка или инициализация конфигурации
def load_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        if 'SETTINGS' in config:
            return config['SETTINGS'].get('json_path', ''), config['SETTINGS'].get('password', '')
    return '', ''

# HTML-шаблоны (без изменений)
SETUP_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Начальная настройка sing-box (rules)</title>
    <!-- Materialize CSS -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css" rel="stylesheet">
    <!-- Material Icons -->
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
        body { background-color: #f5f5f5; }
        .container { margin-top: 20px; }
        .card { background-color: #ffffff; }
        .btn { background-color: #2196F3; }
        .btn:hover { background-color: #1976D2; }
        .error { color: #d32f2f; }
        .success { color: #388e3c; }
        .card-title { text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-content">
                <span class="card-title">Начальная настройка sing-box (rules)</span>
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <p class="{{ category }}">{{ message }}</p>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                <form method="post" action="/setup">
                    <div class="input-field">
                        <input id="json_path" name="json_path" type="text" value="{{ default_path }}" required>
                        <label for="json_path">Укажите название JSON-файла с правилами</label>
                        <span class="helper-text">
                            Например rules.json
                        </span>
                    </div>
                    <div class="input-field">
                        <input id="password" name="password" type="password" required>
                        <label for="password">Задайте пароль для веб-панели</label>
                    </div>
                    <button class="btn waves-effect waves-light" type="submit">Сохранить настройки</button>
                </form>
            </div>
        </div>
    </div>
    <!-- Materialize JS -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script>
</body>
</html>
'''

EDITOR_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>sing-box (rules)</title>
    <!-- Materialize CSS -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css" rel="stylesheet" />
    <!-- Material Icons -->
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet" />
    <style>
        body {
            background-color: #f5f5f5;
        }
        .container {
            margin-top: 20px;
        }
        .card {
            background-color: #ffffff;
        }
        .btn {
            background-color: #2196F3;
        }
        .btn:hover {
            background-color: #1976D2;
        }
        .error {
            color: #d32f2f;
        }
        .success {
            color: #388e3c;
        }
        table.responsive-table th {
            background-color: #e3f2fd;
            color: #0d47a1;
        }
        table.responsive-table td {
            background-color: #ffffff;
        }
        .delete-icon {
            cursor: pointer;
            color: #d32f2f;
        }
        .delete-icon:hover {
            color: #b71c1c;
        }
        .add-form .input-field {
            margin-top: 0;
        }
        .list-item {
            display: flex;
            align-items: center;
            justify-content: flex-start;
            padding: 8px;
            margin-right: 12px;
            margin-bottom: 8px;
        }
        .list-item input {
            width: 180px;
            margin-right: 8px;
        }
        .horizontal-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .section-header {
            font-size: 1.6rem;
            font-weight: bold;
            color: #0d47a1;
            margin-bottom: 12px;
        }
        details {
            margin-bottom: 16px;
        }
        summary {
            cursor: pointer;
            display: flex;
            align-items: center;
            font-size: 1.6rem;
            font-weight: bold;
            color: #0d47a1;
            padding: 8px 0;
        }
        summary i {
            margin-right: 8px;
        }
        details[open] summary i:before {
            content: "expand_less";
        }
        summary i:before {
            content: "expand_more";
        }
        .button-group {
            display: flex;
            flex-direction: column;
            gap: 10px;
            align-items: flex-start;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-content">
                <h3 class="center-align" style="font-weight: bold; font-size: 2.4rem; margin-bottom: 30px;">
                    Адреса маршрутизации sing-box (rules)
                </h3>
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <p class="{{ category }}">{{ message }}</p>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                {% if not authenticated %}
                    <form method="post" action="/login">
                        <div class="input-field">
                            <input id="password" name="password" type="password" required />
                            <label for="password">Пароль</label>
                        </div>
                        <button class="btn waves-effect waves-light" type="submit">Войти</button>
                    </form>
                {% else %}
                    <form id="main-form" method="post" action="/save" class="add-form">
                        <div class="row">
                            <h5>Добавить новую запись</h5>
                            <div class="input-field col s12 m4">
                                <input id="new_ip_cidr" name="new_ip_cidr" type="text" />
                                <label for="new_ip_cidr">По IP (IP CIDR)</label>
                            </div>
                            <div class="input-field col s12 m4">
                                <input id="new_domain_suffix" name="new_domain_suffix" type="text" />
                                <label for="new_domain_suffix">По домену (Domain Suffix)</label>
                            </div>
                            <div class="input-field col s12 m4">
                                <input id="new_domain_keyword" name="new_domain_keyword" type="text" />
                                <label for="new_domain_keyword">По части домена (Domain Keyword)</label>
                            </div>
                            <div class="col s12">
                                <div class="button-group">
                                    <button class="btn waves-effect waves-light" type="submit" name="action" value="add">Добавить</button>
                                    <button id="restart-btn" formaction="/restart" class="btn waves-effect waves-light red" type="submit">
                                        Перезапустить sing-box
                                    </button>
                                </div>
                            </div>
                        </div>
                    </form>
                    <form method="post" action="/save">
                        <div class="row">
                            <h5 class="section-header">Текущие записи:</h5>
                            <div class="col s12">
                                <details>
                                    <summary><i class="material-icons"></i>По IP (IP CIDR)</summary>
                                    <div class="horizontal-list">
                                        {% for value in ip_cidr %}
                                            <div class="list-item">
                                                <input type="text" name="ip_cidr_{{ loop.index0 }}" value="{{ value }}" />
                                                <button type="submit" name="action" value="delete_ip_cidr_{{ loop.index0 }}" class="delete-icon" style="background:none; border:none; padding:0;">
                                                    <i class="material-icons">close</i>
                                                </button>
                                            </div>
                                        {% endfor %}
                                    </div>
                                </details>
                            </div>
                            <div class="col s12">
                                <details>
                                    <summary><i class="material-icons"></i>По домену (Domain Suffix)</summary>
                                    <div class="horizontal-list">
                                        {% for value in domain_suffix %}
                                            <div class="list-item">
                                                <input type="text" name="domain_suffix_{{ loop.index0 }}" value="{{ value }}" />
                                                <button type="submit" name="action" value="delete_domain_suffix_{{ loop.index0 }}" class="delete-icon" style="background:none; border:none; padding:0;">
                                                    <i class="material-icons">close</i>
                                                </button>
                                            </div>
                                        {% endfor %}
                                    </div>
                                </details>
                            </div>
                            <div class="col s12">
                                <details>
                                    <summary><i class="material-icons"></i>По части домена (Domain Keyword)</summary>
                                    <div class="horizontal-list">
                                        {% for value in domain_keyword %}
                                            <div class="list-item">
                                                <input type="text" name="domain_keyword_{{ loop.index0 }}" value="{{ value }}" />
                                                <button type="submit" name="action" value="delete_domain_keyword_{{ loop.index0 }}" class="delete-icon" style="background:none; border:none; padding:0;">
                                                    <i class="material-icons">close</i>
                                                </button>
                                            </div>
                                        {% endfor %}
                                    </div>
                                </details>
                            </div>
                        </div>
                    </form>
                    <p><a href="/logout" class="btn-flat waves-effect">Выйти</a></p>
                {% endif %}
            </div>
        </div>
    </div>
    <!-- Materialize JS -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script>
    <script>
        document.getElementById('restart-btn').addEventListener('click', function(e) {
            if (confirm('Вы уверены, что хотите перезапустить sing-box?')) {
                e.preventDefault();
                this.disabled = true;
                this.innerText = 'Перезапуск...';
                setTimeout(function() {
                    document.getElementById('main-form').action = '/restart';
                    document.getElementById('main-form').submit();
                    setTimeout(function() {
                        window.location.reload();
                    }, 5000);
                }, 500);
            }
        });
    </script>
</body>
</html>
'''

@app.route('/restart', methods=['POST'])
def restart_singbox():
    if not session.get('authenticated'):
        flash('Сначала войдите в систему', 'error')
        return redirect('/')

    try:
        # Выполняем команду sbs stop
        stop_result = subprocess.run(['sbs', 'stop'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f"Команда: sbs stop\nВывод: {stop_result.stdout}\nОшибка: {stop_result.stderr}\nКод возврата: {stop_result.returncode}")
        if stop_result.returncode != 0:
            flash(f'Ошибка при остановке sing-box: {stop_result.stderr} (код возврата: {stop_result.returncode})', 'error')
            return redirect('/')

        # Проверяем статус после остановки
        status_result = subprocess.run(['sbs', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f"Статус после остановки:\nВывод: {status_result.stdout}\nОшибка: {status_result.stderr}\nКод возврата: {status_result.returncode}")

        # Задержка 3 секунды
        time.sleep(3)

        # Выполняем команду sbs start
        start_result = subprocess.run(['sbs', 'start'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f"Команда: sbs start\nВывод: {start_result.stdout}\nОшибка: {start_result.stderr}\nКод возврата: {start_result.returncode}")
        if start_result.returncode == 0:
            flash('sing-box успешно перезапущен', 'success')
        else:
            flash(f'Ошибка при запуске sing-box: {start_result.stderr} (код возврата: {start_result.returncode})', 'error')

        # Проверяем статус после запуска
        status_result = subprocess.run(['sbs', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f"Статус после запуска:\nВывод: {status_result.stdout}\nОшибка: {status_result.stderr}\nКод возврата: {status_result.returncode}")

    except FileNotFoundError:
        flash('Команда "sbs" не найдена. Проверьте, установлена ли она и доступна ли в PATH.', 'error')
        print('Ошибка: команда "sbs" не найдена в PATH.')
    except Exception as e:
        flash(f'Не удалось выполнить команду: {str(e)}', 'error')
        print(f'Исключение: {str(e)}')

    return redirect('/')

@app.route('/', methods=['GET'])
def index():
    json_path, password = load_config()
    if not json_path or not password:
        return redirect('/setup')

    if not session.get('authenticated'):
        return render_template_string(EDITOR_TEMPLATE, authenticated=False)

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        rule = data.get('rules', [{}])[0]
        ip_cidr = rule.get('ip_cidr', [])
        domain_suffix = rule.get('domain_suffix', [])
        domain_keyword = rule.get('domain_keyword', [])
        return render_template_string(
            EDITOR_TEMPLATE,
            authenticated=True,
            ip_cidr=ip_cidr,
            domain_suffix=domain_suffix,
            domain_keyword=domain_keyword
        )
    except Exception as e:
        flash(f"Ошибка чтения JSON-файла: {str(e)}", 'error')
        return render_template_string(EDITOR_TEMPLATE, authenticated=True, ip_cidr=[], domain_suffix=[],
                                      domain_keyword=[])

@app.route('/login', methods=['POST'])
def login():
    json_path, password = load_config()
    if not json_path or not password:
        return redirect('/setup')

    input_password = request.form.get('password')
    if input_password == password:
        session['authenticated'] = True
        return redirect('/')
    else:
        flash('Неверный пароль', 'error')
        return redirect('/')

@app.route('/save', methods=['POST'])
def save():
    json_path, password = load_config()
    if not json_path or not password:
        return redirect('/setup')

    if not session.get('authenticated'):
        flash('Сначала войдите в систему', 'error')
        return redirect('/')

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        rule = data.get('rules', [{}])[0]
        ip_cidr = rule.get('ip_cidr', []).copy()
        domain_suffix = rule.get('domain_suffix', []).copy()
        domain_keyword = rule.get('domain_keyword', []).copy()

        action = request.form.get('action')
        if not action:
            flash('Действие не указано', 'error')
            return redirect('/')

        if action == 'add':
            new_ip_cidr = request.form.get('new_ip_cidr', '').strip()
            new_domain_suffix = request.form.get('new_domain_suffix', '').strip()
            new_domain_keyword = request.form.get('new_domain_keyword', '').strip()

            if new_ip_cidr and new_ip_cidr not in ip_cidr:
                ip_cidr.append(new_ip_cidr)
            if new_domain_suffix and new_domain_suffix not in domain_suffix:
                domain_suffix.append(new_domain_suffix)
            if new_domain_keyword and new_domain_keyword not in domain_keyword:
                domain_keyword.append(new_domain_keyword)

        elif action.startswith('delete_ip_cidr_'):
            index = int(action.split('_')[-1])
            if index < len(ip_cidr):
                ip_cidr.pop(index)

        elif action.startswith('delete_domain_suffix_'):
            index = int(action.split('_')[-1])
            if index < len(domain_suffix):
                domain_suffix.pop(index)

        elif action.startswith('delete_domain_keyword_'):
            index = int(action.split('_')[-1])
            if index < len(domain_keyword):
                domain_keyword.pop(index)

        elif action == 'save':
            new_ip_cidr = []
            new_domain_suffix = []
            new_domain_keyword = []
            for key, value in request.form.items():
                if key.startswith('ip_cidr_') and value.strip() and value.strip() not in new_ip_cidr:
                    new_ip_cidr.append(value.strip())
                elif key.startswith('domain_suffix_') and value.strip() and value.strip() not in new_domain_suffix:
                    new_domain_suffix.append(value.strip())
                elif key.startswith('domain_keyword_') and value.strip() and value.strip() not in new_domain_keyword:
                    new_domain_keyword.append(value.strip())
            if new_ip_cidr:
                ip_cidr = new_ip_cidr
            if new_domain_suffix:
                domain_suffix = new_domain_suffix
            if new_domain_keyword:
                domain_keyword = new_domain_keyword

        data['rules'][0] = {
            'ip_cidr': ip_cidr,
            'domain_suffix': domain_suffix,
            'domain_keyword': domain_keyword
        }

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        flash('JSON-файл успешно сохранен', 'success')
    except json.JSONDecodeError as e:
        flash(f'Неверный формат JSON: {str(e)}', 'error')
    except Exception as e:
        flash(f'Ошибка сохранения JSON-файла: {str(e)}', 'error')

    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    flash('Вы вышли из системы', 'success')
    return redirect('/')

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'GET':
        json_path, password = load_config()
        if json_path and password:
            return redirect('/')
        return render_template_string(SETUP_TEMPLATE, default_path=DEFAULT_JSON_NAME)

    json_path = request.form.get('json_path')
    password = request.form.get('password')

    if not json_path or not password:
        flash('Путь к файлу и пароль не могут быть пустыми', 'error')
        return render_template_string(SETUP_TEMPLATE, default_path=DEFAULT_JSON_NAME)

    if not os.path.isabs(json_path) or json_path == DEFAULT_JSON_NAME:
        json_path = os.path.normpath(os.path.join(os.path.dirname(__file__), DEFAULT_JSON_NAME))
    else:
        json_path = os.path.normpath(json_path)

    if not os.path.exists(json_path):
        flash(f'JSON-файл не найден по пути: {json_path}', 'error')
        return render_template_string(SETUP_TEMPLATE, default_path=DEFAULT_JSON_NAME)

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json.load(f)
    except json.JSONDecodeError as e:
        flash(f'Указанный файл не является валидным JSON: {str(e)}', 'error')
        return render_template_string(SETUP_TEMPLATE, default_path=DEFAULT_JSON_NAME)
    except Exception as e:
        flash(f'Ошибка чтения JSON-файла: {str(e)}', 'error')
        return render_template_string(SETUP_TEMPLATE, default_path=DEFAULT_JSON_NAME)

    config = configparser.ConfigParser()
    config['SETTINGS'] = {
        'json_path': json_path,
        'password': password
    }
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        flash('Настройки успешно заданы', 'success')
        return redirect('/')
    except Exception as e:
        flash(f'Ошибка сохранения конфигурации: {str(e)}', 'error')
        return render_template_string(SETUP_TEMPLATE, default_path=DEFAULT_JSON_NAME)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)