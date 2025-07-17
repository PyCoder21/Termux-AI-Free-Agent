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
echo -e "${GREEN}Скрипт установки Termux-AI-Free-Agent${NC}\n"

echo ""

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
    echo "python ~/Termux-AI-Free-Agent/proxy.py" >> "$PREFIX/var/service/gptchatbot/run"
    chmod +x "$PREFIX/var/service/gptchatbot/run"
    sv-enable gptchatbot
    echo -e "${GREEN}Сервис gptchatbot создан и включен.${NC}"
else
    echo -e "${YELLOW}Сервис gptchatbot уже существует.${NC}"
fi

pkg install tur-repo python-torch python-torchaudio python-torchvision -y
pkg install python-tiktoken -y
echo ""

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
