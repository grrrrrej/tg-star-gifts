# 🌟 Telegram Star Gifts Sender (CLI)

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)
![Telethon](https://img.shields.io/badge/library-Telethon-orange.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20Termux%20%7C%20iOS-lightgrey.svg)

> 🚫 **СТРОГО ЗАПРЕЩЕНО КОММЕРЧЕСКОЕ ИСПОЛЬЗОВАНИЕ**  
> Данный софт является **полностью бесплатным**. Продажа этого скрипта или его частей в любых каналах, чатах или на площадках (Lolz, FunPay, Telegram и др.) **запрещена**.  
> **Если вы купили этот скрипт — вас обманули.**

---

## 📖 О проекте

Профессиональный консольный инструмент для автоматизации отправки **Звездных подарков (Star Gifts)** в Telegram. Скрипт позволяет массово дарить подарки, использовать кастомные ID и работать в анонимном режиме. Оптимизировано для работы на всех платформах: **Windows, Linux, Termux (Android), iSH / a-Shell (iOS)**.

---

## 📜 Лицензия (GNU GPL v3.0)

Это программное обеспечение распространяется под лицензией **GNU General Public License v3.0**.

### Что разрешено:
- ✅ Свободно использовать, изменять и распространять код
- ✅ Использовать в личных и некоммерческих проектах

### Что ОБЯЗАТЕЛЬНО:
- 🔒 Сохранять авторские права и уведомление о лицензии
- 🔒 Распространять производные работы **только под той же лицензией (GPLv3)**
- 🔒 Указывать изменения, внесенные вами в код
- 🔒 Делать исходный код доступным для всех

### Что ЗАПРЕЩЕНО:
- ❌ **ПРОДАЖА** — код не может быть продан или использован в коммерческих продуктах без открытия исходников
- ❌ Удаление или скрытие авторства (`@blackpean`)

### Отказ от ответственности:
Автор не несет ответственности за возможные блокировки аккаунтов или случайные траты Telegram Stars. Вы используете скрипт на свой страх и риск.

📖 **Полный текст лицензии:** [GNU GPL v3.0](https://www.gnu.org/licenses/gpl-3.0.html)

---

## ⚠️ Важные предупреждения

1. **🔐 Безопасность:** После первого входа создается файл `session.txt`. Это ваш ключ доступа. **Никому не передавайте его**, иначе посторонние получат полный доступ к вашему Telegram.
2. **💰 Баланс:** Отправка подарков стоит реальных звезд Telegram. Всегда проверяйте сумму перед подтверждением.
3. **⏱ Лимиты:** Не превышайте разумные объемы отправки во избежание временных ограничений (Flood Wait) со стороны серверов Telegram.

---

## 🚀 Установка и запуск

### 📱 Для Android (Termux)

```bash
pkg update && pkg upgrade
pkg install python git
curl -O https://raw.githubusercontent.com/grrrrrej/tg-star-gifts/main/setup.sh
chmod +x setup.sh
./setup.sh
```

### 🍎 Для iOS (iSH / a-Shell)

**iSH** и **a-Shell** используют Alpine Linux. Выполните:

```bash
apk update && apk upgrade
apk add python3 py3-pip git curl
curl -O https://raw.githubusercontent.com/grrrrrej/tg-star-gifts/main/setup.sh
chmod +x setup.sh
./setup.sh
```

#### ⚡ Установка в одну строку (iOS):
```bash
apk add python3 py3-pip git curl && curl -O https://raw.githubusercontent.com/grrrrrej/tg-star-gifts/main/setup.sh && chmod +x setup.sh && ./setup.sh
```

> **💡 Важно для iOS:**  
> iSH работает медленнее обычного терминала. Если при установке библиотек (`pip install`) кажется, что всё зависло — просто подождите пару минут, процесс завершится.

### 🪟 Для Windows (CMD / PowerShell / WSL)

**Вариант 1: Через WSL (рекомендуется)**
```bash
sudo apt update && sudo apt install python3 python3-pip git curl
curl -O https://raw.githubusercontent.com/grrrrrej/tg-star-gifts/main/setup.sh
chmod +x setup.sh
./setup.sh
```

**Вариант 2: Через командную строку (если установлен Python и Git)**
```cmd
curl -O https://raw.githubusercontent.com/grrrrrej/tg-star-gifts/main/setup.sh
python setup.sh
```

### 🐧 Для Linux (Ubuntu/Debian)

```bash
sudo apt update && sudo apt install python3 python3-pip git curl
curl -O https://raw.githubusercontent.com/grrrrrej/tg-star-gifts/main/setup.sh
chmod +x setup.sh
./setup.sh
```

---

## 🛠 Удобный менеджер (setup.sh)

После скачивания `setup.sh` вы получите красивое меню для управления скриптом:

```bash
./setup.sh
```

### Меню менеджера:

| Опция | Действие |
| :--- | :--- |
| **1** | 🚀 Установить / Обновить зависимости |
| **2** | ▶️ Запустить скрипт |
| **3** | 🔄 Обновить из GitHub |
| **4** | 🗑 Удалить скрипт и данные |
| **5** | ℹ️ Информация о версии |
| **6** | 📂 Показать текущую папку |
| **7** | 🚪 Выход |

---

## 🎮 Управление скриптом

Программа работает в интерактивном режиме. Просто следуйте подсказкам на экране.

| Действие | Инструкция |
| :--- | :--- |
| **🎯 Выбор цели** | Введите `@username` или `ID` пользователя |
| **🎁 Выбор подарка** | Введите цифру из предложенного списка |
| **✨ Кастомный подарок** | Используйте команду `/set [ID_ПОДАРКА] [Название]` |
| **🚪 Выход** | Просто нажмите **Enter** (оставьте поле пустым) |

---

## 🔄 Обновление

### Через менеджер (рекомендуется):
```bash
./setup.sh
# Выберите опцию 1 или 3
```

### Или напрямую через pip:
```bash
pip install --upgrade git+https://github.com/grrrrrej/tg-star-gifts.git
```

---

## 📂 Создаваемые файлы

Скрипт хранит данные локально в папке, из которой вы его запускаете:

| Файл | Описание |
| :--- | :--- |
| `session.txt` | Данные вашей авторизации (сессия). **Никому не показывайте!** |
| `custom_gifts.txt` | Ваши личные подарки, добавленные через `/set` |

---

## 🛡 Защита авторских прав

В коде используется защищенный идентификатор автора (`ID_KEY`). Удаление или подмена авторских прав (`@blackpean`) **запрещена** программной логикой и условиями лицензии GPLv3.

---

## ❓ Частые вопросы (FAQ)

### ❓ Скрипт не запускается: "command not found: tg-gifts"
**Решение:** Установите скрипт через менеджер (опция 1) или перезапустите терминал.

### ❓ Ошибка: "pip: command not found"
**Решение:** Установите pip:
- **Termux:** `pkg install python`
- **iOS:** `apk add py3-pip`
- **Linux:** `sudo apt install python3-pip`

### ❓ Ошибка: "curl: command not found"
**Решение:** Установите curl:
- **Termux:** `pkg install curl`
- **iOS:** `apk add curl`
- **Linux:** `sudo apt install curl`

### ❓ Медленно работает на iOS
**Решение:** iSH эмулирует Linux, поэтому скорость ниже. Просто подождите дольше при установке и отправке.

### ❓ Могу ли я продавать этот скрипт?
**НЕТ!** Коммерческое использование **строго запрещено** лицензией GPL v3.0 и условиями проекта.

---

## 📞 Обратная связь

По всем вопросам, багам или предложениям:

- **Telegram:** [@blackpean](https://t.me/blackpean)
- **GitHub:** [grrrrrej](https://github.com/grrrrrej)

---

## ⭐ Поддержка проекта

Если вам нравится этот инструмент:
- Поставьте ⭐ на GitHub
- Поделитесь с друзьями
- Сообщите о багах в Issues

---

*Developed with ❤️ for Telegram community.*  
*© 2025 @blackpean | GNU GPL v3.0 | Commercial use prohibited*
