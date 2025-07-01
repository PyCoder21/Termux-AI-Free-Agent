#!/bin/bash

# --- Цвета для красивого вывода ---
BLUE='\033[1;34m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
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

# --- Начало установки ---

# 1. Проверка POLLINATIONS_API_TOKEN
echo -e "${YELLOW}--- Шаг 1: Проверка токена Pollinations ---${NC}"
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
echo "" # Newline for spacing

# 2. Проверка и установка chafa
echo -e "${YELLOW}--- Шаг 2: Проверка и установка утилиты chafa ---${NC}"
if ! command -v chafa &> /dev/null; then
    echo "Утилита chafa не найдена. Устанавливаю..."
    pkg install chafa -y
    echo -e "${GREEN}chafa успешно установлена.${NC}"
else
    echo -e "${GREEN}chafa уже установлена.${NC}"
fi
echo "" # Newline for spacing

# 3. Установка зависимостей Python
echo -e "${YELLOW}--- Шаг 3: Установка зависимостей Python ---${NC}"
pip install pexpect requests langchain-community langchain-core langchain-openai prompt_toolkit rich sympy numexpr pollinations pollinations.ai
echo "" # Newline for spacing

# --- Завершение ---
echo -e "${GREEN}====================================="
echo -e "    Установка успешно завершена!    "
echo -e "=====================================${NC}"
echo "Теперь вы можете запустить агент, выполнив команду: python ai.py"
echo ""
