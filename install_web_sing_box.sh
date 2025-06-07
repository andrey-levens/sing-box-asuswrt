#!/bin/sh

# Переменные
SCRIPT_DIR="/jffs/addons/sing-box-script"
APP_URL="https://raw.githubusercontent.com/andrey-levens/sing-box-asuswrt/master/app.py"
APP_FILE="$SCRIPT_DIR/app.py"
STARTUP_SCRIPT="/jffs/scripts/services-start"
PYTHON_PATH="/opt/bin/python3"
FLASK_PKG="flask"
STARTUP_CMD="sleep 60 && $PYTHON_PATH $APP_FILE >> $SCRIPT_DIR/app.log 2>&1"

# Создание каталога при необходимости
mkdir -p "$SCRIPT_DIR"

# Загрузка app.py, если не существует, иначе спросить
if [ -f "$APP_FILE" ]; then
    echo "Файл app.py уже существует в $SCRIPT_DIR."
    echo "Перезаписать? (y/n): "
    read overwrite
    if [ "$overwrite" = "y" ]; then
        curl -fsSL "$APP_URL" -o "$APP_FILE"
        echo "Файл перезаписан."
    else
        echo "Пропущено обновление app.py."
    fi
else
    curl -fsSL "$APP_URL" -o "$APP_FILE"
    echo "Файл app.py загружен."
fi

# Проверка наличия Python и Flask
if ! command -v $PYTHON_PATH >/dev/null 2>&1; then
    echo "Устанавливается python3..."
    opkg update && opkg install python3
fi

if ! $PYTHON_PATH -c "import flask" >/dev/null 2>&1; then
    echo "Устанавливается Flask..."
    $PYTHON_PATH -m ensurepip
    $PYTHON_PATH -m pip install --upgrade pip
    $PYTHON_PATH -m pip install flask
else
    echo "Flask уже установлен. Обновить? (y/n): "
    read update_flask
    if [ "$update_flask" = "y" ]; then
        $PYTHON_PATH -m pip install --upgrade flask
    fi
fi

# Добавление команды запуска в services-start
if [ -f "$STARTUP_SCRIPT" ]; then
    if grep -Fq "$STARTUP_CMD" "$STARTUP_SCRIPT"; then
        echo "Команда запуска уже присутствует в services-start."
    else
        echo "Добавить команду запуска в $STARTUP_SCRIPT? (y/n): "
        read add_startup
        if [ "$add_startup" = "y" ]; then
            echo "$STARTUP_CMD" >> "$STARTUP_SCRIPT"
            chmod +x "$STARTUP_SCRIPT"
            echo "Команда добавлена."
        fi
    fi
else
    echo "#!/bin/sh" > "$STARTUP_SCRIPT"
    echo "$STARTUP_CMD" >> "$STARTUP_SCRIPT"
    chmod +x "$STARTUP_SCRIPT"
    echo "Создан services-start с командой запуска."
fi

# Запуск app.py в фоне
nohup $PYTHON_PATH "$APP_FILE" >> "$SCRIPT_DIR/app.log" 2>&1 &

echo "✅ Установка завершена."
echo "🌐 Веб-панель доступна по адресу: http://<IP_роутера>:5000"
