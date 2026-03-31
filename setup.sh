#!/bin/bash

# Telegram Star Gifts Sender - Установщик и менеджер
# Автор: @blackpean
# Лицензия: GNU GPL v3.0

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода заголовка
print_header() {
    clear
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║      🌟 Telegram Star Gifts Sender - Установщик          ║"
    echo "║      🚫 Коммерческое использование ЗАПРЕЩЕНО             ║"
    echo "║      © @blackpean | GNU GPL v3.0                         ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Функция для вывода меню
show_menu() {
    echo -e "${GREEN}Выберите действие:${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  1) 🚀 Установить / Обновить зависимости"
    echo "  2) ▶️  Запустить скрипт"
    echo "  3) 🔄 Обновить из GitHub"
    echo "  4) 🗑  Удалить скрипт"
    echo "  5) ℹ️  Информация о версии"
    echo "  6) 📂 Показать текущую папку"
    echo "  7) 🚪 Выход"
    echo ""
    echo -n "Введите номер (1-7): "
}

# Функция проверки системы
check_env() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 не найден!${NC}"
        exit 1
    fi
    if ! command -v git &> /dev/null; then
        echo -e "${YELLOW}⚠️ Git не найден. Устанавливаю...${NC}"
        # Для iSH (Alpine)
        if command -v apk &> /dev/null; then apk add git; fi
    fi
}

# Функция установки
install_script() {
    echo -e "${BLUE}🚀 Установка/Обновление...${NC}"
    check_env
    pip3 install --upgrade pip
    pip3 install --upgrade git+https://github.com/grrrrrej/tg-star-gifts.git
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Всё готово! Теперь можно запускать через меню или командой: tg-gifts${NC}"
    else
        echo -e "${RED}❌ Ошибка при установке.${NC}"
    fi
}

# Функция запуска
run_script() {
    if command -v tg-gifts &> /dev/null; then
        tg-gifts
    else
        echo -e "${RED}❌ Скрипт не найден. Сначала выберите пункт 1.${NC}"
    fi
}

# Функция удаления
uninstall_script() {
    echo -n "Удалить скрипт и сессии? (y/N): "
    read -r confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        pip3 uninstall tg-star-gifts -y
        rm -f session.txt custom_gifts.txt
        echo -e "${GREEN}🗑 Удалено.${NC}"
    fi
}

# Основной цикл
main() {
    while true; do
        print_header
        show_menu
        read -r choice
        case $choice in
            1) install_script ;;
            2) run_script ;;
            3) install_script ;; # Обновление — это та же переустановка через pip
            4) uninstall_script ;;
            5) 
                echo -e "${BLUE}Версия системы:${NC}"
                python3 --version
                pip3 show tg-star-gifts | grep Version || echo "Скрипт не установлен"
                ;;
            6) 
                echo -e "${BLUE}Текущая папка:${NC} $(pwd)"
                ls -F
                ;;
            7) exit 0 ;;
            *) echo -e "${RED}❌ Ошибка выбора.${NC}" ;;
        esac
        echo -e "\n${YELLOW}Нажмите Enter...${NC}"
        read -r
    done
}

main
