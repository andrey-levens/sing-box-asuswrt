#!/bin/sh

APP_DIR="/jffs/addons/sing-box-script"
APP_FILE="app.py"
APP_URL="https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/YOUR_BRANCH/app.py"
SERVICE_FILE="/jffs/scripts/services-start"
PYTHON_PATH=$(which python3)

echo "📦 Установка app.py в $APP_DIR..."

# Проверка Python
if [ -z "$PYTHON_PATH" ]; then
    echo "❌ Python3 не найден. Установите через Entware: opkg install python3"
    exit 1
fi

# Проверка curl или wget
if command -v wget > /dev/null; then
    DOWNLOADER="wget -O"
elif command -v curl > /dev/null; then
    DOWNLOADER="curl -o"
else
    echo "❌ Требуется curl или wget. Установите через Entware."
    exit 1
fi

# Создание директории
mkdir -p "$APP_DIR"

# Скачивание app.py
echo "⬇️  Скачиваем $APP_FILE..."
$DOWNLOADER "$APP_DIR/$APP_FILE" "$APP_URL"

if [ ! -s "$APP_DIR/$APP_FILE" ]; then
    echo "❌ Ошибка загрузки $APP_FILE"
    exit 1
fi

chmod +x "$APP_DIR/$APP_FILE"

# Добавление в автозапуск
if ! grep -q "$APP_FILE" "$SERVICE_FILE" 2>/dev/null; then
    echo "📝 Добавляем автозапуск..."
    mkdir -p "$(dirname "$SERVICE_FILE")"
    if [ ! -f "$SERVICE_FILE" ]; then
        echo "#!/bin/sh" > "$SERVICE_FILE"
    fi
    echo "(sleep 60 && $PYTHON_PATH $APP_DIR/$APP_FILE >> $APP_DIR/app.log 2>&1) &" >> "$SERVICE_FILE"
    chmod +x "$SERVICE_FILE"
else
    echo "✅ Уже добавлен в автозапуск."
fi

# Запуск сейчас
echo "🚀 Запускаем $APP_FILE..."
($PYTHON_PATH "$APP_DIR/$APP_FILE" >> "$APP_DIR/app.log" 2>&1 &)

echo "🎉 Готово! Скрипт установлен и запущен."
