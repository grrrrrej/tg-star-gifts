Понимаю, тебе нужен максимально удобный и полный гайд, который можно скопировать целиком одним блоком без потери форматирования.

Чтобы текст не обрезался и его было удобно копировать, я поместил основное содержимое в специальное окно кода. Нажми кнопку **"Copy"** (или значок в правом верхнем углу блока кода), и всё содержимое сохранится в буфер обмена.

### Как создать файл:
1. Нажми кнопку **Copy** на блоке ниже.
2. Открой любой текстовый редактор (Блокнот, VS Code или Termux `nano`).
3. Вставь текст (**Ctrl+V**).
4. Сохрани файл как **`README.md`**.

---

```markdown
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)
![Telethon](https://img.shields.io/badge/library-Telethon-orange.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20Termux%20%7C%20iOS-lightgrey.svg)

# 🌟 Telegram Star Gifts Sender (CLI)

---

## ⚠️ ДИСКЛЕЙМЕР ОТ РАЗРАБОТЧИКА
**Я, как разработчик и/или создатель данного скрипта, не несу никакой ответственности за его использование. Вы используете данный инструмент полностью на свой страх и риск.**

Вся ответственность за любые последствия (блокировки аккаунтов, траты Telegram Stars, нарушение правил или любые другие проблемы) лежит исключительно на пользователе.

---

## 🚫 ЗАПРЕЩЕНО КОММЕРЧЕСКОЕ ИСПОЛЬЗОВАНИЕ
Данный софт является **полностью бесплатным**. Продажа этого скрипта или его частей на любых площадках (Lolz, FunPay, Telegram и др.) **строго запрещена**.

> **Если вы купили этот скрипт — вас обманули.**

---

## ✨ О проекте
Профессиональный консольный инструмент для автоматизации отправки Звездных подарков (Star Gifts). Массовая отправка, кастомные ID, анонимный режим и удобный CLI.

### 🌟 Особенности
* **Автоматизация:** Быстрая отправка Telegram Star Gifts.
* **Кастомные подарки:** Добавление своих ID подарков через команды.
* **Анонимность:** Возможность скрывать отправителя.
* **Кроссплатформенность:** Windows, Linux, Termux (Android) и iOS.

---

## 🚀 Быстрая установка и запуск

### 🐍 Требования
* Python 3.8+
* Подключение к интернету

---

### 💻 Для Windows (рекомендуемый способ)
1. **Установите Python:** Скачайте с [python.org](https://www.python.org/downloads/windows/). **ОБЯЗАТЕЛЬНО** поставьте галочку `Add Python to PATH`.
2. **Загрузите проект:**
   ```bash
   git clone [https://github.com/grrrrrej/tg-star-gifts.git](https://github.com/grrrrrej/tg-star-gifts.git)
   cd tg-star-gifts
   ```
3. **Виртуальное окружение:**
   ```bash
   python -m venv venv
   # Для активации (CMD): venv\Scripts\activate.bat
   # Для активации (PowerShell): .\venv\Scripts\Activate.ps1
   ```
4. **Установите зависимости:**
   ```bash
   pip install telethon rich
   ```
5. **Запуск:** `python main.py`

---

### 🐧 Для Linux / 📱 Android (Termux)
```bash
pkg update && pkg upgrade # для Termux
sudo apt update && sudo apt install python3 python3-pip git curl # для Linux
curl -O [https://raw.githubusercontent.com/grrrrrej/tg-star-gifts/main/setup.sh](https://raw.githubusercontent.com/grrrrrej/tg-star-gifts/main/setup.sh)
chmod +x setup.sh
./setup.sh
```
*Выберите опцию **1** для установки зависимостей.*

---

### 🍎 Для iOS (iSH)
1. Установите **iSH Shell** из App Store.
2. Выполните:
   ```bash
   apk update && apk upgrade
   apk add python3 py3-pip git curl
   curl -O [https://raw.githubusercontent.com/grrrrrej/tg-star-gifts/main/setup.sh](https://raw.githubusercontent.com/grrrrrej/tg-star-gifts/main/setup.sh)
   chmod +x setup.sh
   ./setup.sh
   ```

---

## 🎮 Управление скриптом

| Действие | Инструкция |
| :--- | :--- |
| **🎯 Цель** | Введите `@username` или `ID` |
| **🎁 Подарок** | Выберите цифру из списка |
| **✨ Свой ID** | Используйте `/set [ID] [Название]` |
| **🚪 Выход** | Нажмите `Enter` (пустое поле) |

---

## 🛠 Менеджер `setup.sh`
* `1` — Установить/Обновить зависимости
* `2` — Запустить скрипт
* `3` — Обновить из GitHub
* `4` — Удалить данные

---

## 🔐 Безопасность
* **`session.txt`**: Ваш ключ доступа. **НИКОМУ НЕ ПОКАЗЫВАЙТЕ.**
* **API_ID / API_HASH**: Получите свои данные на [my.telegram.org](https://my.telegram.org).

---

## 📜 Лицензия (GNU GPL v3.0)
* ✅ Свободное использование и изменение.
* 🔒 Обязательно сохранение авторства (`@blackpean`).
* ❌ **ПРОДАЖА ЗАПРЕЩЕНА.**

---

## 📞 Поддержка
* **Telegram:** `@blackpean`
* **GitHub:** [grrrrrej](https://github.com/grrrrrej)

---
Developed with ❤️ for Telegram community.
© 2025 @blackpean | GNU GPL v3.0 | Commercial use prohibited
```
