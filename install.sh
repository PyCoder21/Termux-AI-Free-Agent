#!/bin/bash

# --- Цвета для красивого вывода ---
BLUE='\033[1;34m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
NC='\033[0m' # No Color

# Очистка экрана
clear

# --- Большой заголовок ---
echo -e "${BLUE}"
echo '############################################################'
echo '#                                                          #'
echo '#                  У С Т А Н О В К А                       #'
echo '#                                                          #'
echo '############################################################'
echo -e "${NC}"
echo -e "${GREEN}Скрипт установки FreeSeekR1-Agent${NC}\n"

# --- Выбор режима установки ---
echo -e "${YELLOW}Выберите режим установки:${NC}"
echo "1) Только Pollinations API"
echo "2) Только Termux-services (reverse proxy)"
echo "3) Оба варианта"
echo -e "${RED}4) Отмена${NC}"
echo ""

read -p "Введите номер выбора (1-4): " choice

case $choice in
    1)
        echo -e "${GREEN}Выбран режим: Только Pollinations API${NC}"
        pollinations_only=true
        termux_services_only=false
        ;;
    2)
        echo -e "${GREEN}Выбран режим: Только Termux-services${NC}"
        pollinations_only=false
        termux_services_only=true
        ;;
    3)
        echo -e "${GREEN}Выбран режим: Оба варианта${NC}"
        pollinations_only=false
        termux_services_only=false
        ;;
    4)
        echo -e "${RED}Установка отменена${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Неверный выбор, выход${NC}"
        exit 1
        ;;
esac

echo ""

# --- Установка Pollinations API ---
if ! $termux_services_only; then
    echo -e "${YELLOW}--- Шаг 1: Настройка Pollinations API ---${NC}"
    if [ -z "$POLLINATIONS_API_TOKEN" ]; then
        echo "Переменная POLLINATIONS_API_TOKEN не установлена."
        read -p "Пожалуйста, введите ваш токен Pollinations: " token
        # Используем printf для безопасной записи токена
        printf "\nexport POLLINATIONS_API_TOKEN=%q\n" "$token" >> ~/.bashrc
        echo -e "${GREEN}Токен добавлен в ~/.bashrc. Перезапустите терминал или выполните 'source ~/.bashrc'${NC}"
        export POLLINATIONS_API_TOKEN="$token"
    else
        echo -e "${GREEN}Токен POLLINATIONS_API_TOKEN найден.${NC}"
    fi
    echo ""
fi

# --- Установка Termux-services ---
if ! $pollinations_only; then
    echo -e "${YELLOW}--- Шаг 2: Настройка Termux-services ---${NC}"
    if ! command -v sv &> /dev/null; then
        echo "Утилита sv (termux-services) не найдена. Устанавливаю..."
        pkg install termux-services -y
        echo -e "${GREEN}termux-services успешно установлен.${NC}"
    else
        echo -e "${GREEN}termux-services уже установлен.${NC}"
    fi
    
    # Создаем структуру папок для сервиса
    if [ ! -d "$PREFIX/var/service" ]; then
        mkdir -p "$PREFIX/var/service"
    fi
    
    # Создаем сервис для gptchatbot
    if [ ! -d "$PREFIX/var/service/gptchatbot" ]; then
        mkdir -p "$PREFIX/var/service/gptchatbot"
        echo "#!/usr/bin/bash" > "$PREFIX/var/service/gptchatbot/run"
        echo "python ~/FreeSeekR1-Agent/proxy.py" >> "$PREFIX/var/service/gptchatbot/run"
        chmod +x "$PREFIX/var/service/gptchatbot/run"
        sv-enable gptchatbot
        echo -e "${GREEN}Сервис gptchatbot создан и включен.${NC}"
    else
        echo -e "${YELLOW}Сервис gptchatbot уже существует.${NC}"
    fi
    echo ""
fi

# --- Общие зависимости ---
echo -e "${YELLOW}--- Шаг 3: Установка общих зависимостей ---${NC}"

# Проверка и установка chafa
if ! command -v chafa &> /dev/null; then
    echo "Утилита chafa не найдена. Устанавливаю..."
    pkg install chafa -y
    echo -e "${GREEN}chafa успешно установлена.${NC}"
else
    echo -e "${GREEN}chafa уже установлена.${NC}"
fi

# Установка зависимостей Python
echo "Устанавливаю Python зависимости..."
pip install pexpect requests langchain-community langchain-core langchain-openai prompt_toolkit rich sympy numexpr pollinations pollinations.ai
echo ""

# --- Завершение ---
echo -e "${GREEN}====================================="
echo -e "    Установка успешно завершена!    "
echo -e "=====================================${NC}"

if ! $termux_services_only; then
    echo "Для использования Pollinations API запустите: python ai.py"
fi

if ! $pollinations_only; then
    echo "Сервис reverse proxy был настроен и будет автоматически запускаться при старте Termux."
fi

echo ""
