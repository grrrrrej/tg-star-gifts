<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Star Gifts Sender (CLI) - README</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif; line-height: 1.6; margin: 20px; max-width: 900px; margin-left: auto; margin-right: auto; color: #333; background-color: #f8f8f8; }
        h1, h2, h3, h4, h5, h6 { color: #222; margin-top: 1.5em; margin-bottom: 0.5em; }
        h1 { border-bottom: 2px solid #eee; padding-bottom: 0.3em; }
        h2 { border-bottom: 1px solid #eee; padding-bottom: 0.2em; }
        pre, code { font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace; background-color: #eee; padding: 2px 4px; border-radius: 4px; }
        pre { display: block; padding: 1em; overflow-x: auto; background-color: #e8e8e8; border-radius: 6px; }
        table { width: 100%; border-collapse: collapse; margin: 1em 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        strong { font-weight: bold; }
        em { font-style: italic; }
        a { color: #0366d6; text-decoration: none; }
        a:hover { text-decoration: underline; }
        ul { padding-left: 20px; }
        .badge { vertical-align: middle; margin-right: 5px; }
    </style>
</head>
<body>
    <p>
        <img class="badge" src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python">
        <img class="badge" src="https://img.shields.io/badge/license-GPL--3.0-green.svg" alt="License">
        <img class="badge" src="https://img.shields.io/badge/library-Telethon-orange.svg" alt="Telethon">
        <img class="badge" src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20Termux%20%7C%20iOS-lightgrey.svg" alt="Platform">
    </p>

    <h1>🌟 Telegram Star Gifts Sender (CLI)</h1>

    <hr>

    <h2>⚠️ ДИСКЛЕЙМЕР ОТ РАЗРАБОТЧИКА / СОЗДАТЕЛЯ СКРИПТА ⚠️</h2>

    <p><strong>Я, как разработчик и/или создатель данного скрипта, не несу никакой ответственности за его использование. Вы используете данный инструмент полностью на свой страх и риск.</strong></p>

    <p><strong>Вся ответственность за любые последствия, возникающие в результате использования этого программного обеспечения (включая, но не ограничиваясь, блокировками аккаунтов, непредвиденными тратами Telegram Stars, нарушением правил Telegram или любыми другими проблемами), лежит исключительно на пользователе.</strong></p>

    <p><strong>Использование данного скрипта осуществляется на добровольной основе и по личному желанию пользователя. Убедитесь, что вы понимаете и принимаете все риски перед использованием.</strong></p>

    <hr>

    <h2>🚫 Важное предупреждение: ЗАПРЕЩЕНО КОММЕРЧЕСКОЕ ИСПОЛЬЗОВАНИЕ</h2>

    <p>Данный софт является <strong>полностью бесплатным</strong>. Продажа этого скрипта или его частей в любых каналах, чатах или на площадках (Lolz, FunPay, Telegram и др.) <strong>строго запрещена</strong>.</p>

    <p><strong>Если вы купили этот скрипт — вас обманули.</strong></p>

    <hr>

    <h2>✨ О проекте</h2>

    <p>Профессиональный консольный инструмент для автоматизации отправки Звездных подарков (Star Gifts) в Telegram. Этот скрипт позволяет массово дарить подарки, использовать кастомные ID и работать в анонимном режиме, предлагая удобный CLI-интерфейс.</p>

    <h3>🌟 Особенности</h3>
    <ul>
        <li><strong>Автоматизированная отправка:</strong> Быстрая и эффективная отправка Telegram Star Gifts.</li>
        <li><strong>Гибкий выбор подарков:</strong> Возможность выбора из стандартных или добавления кастомных подарков.</li>
        <li><strong>Анонимный режим:</strong> Отправляйте подарки анонимно.</li>
        <li><strong>Настраиваемое количество:</strong> Отправляйте несколько подарков одному получателю.</li>
        <li><strong>Поддержка ников и ID:</strong> Удобный ввод получателя по нику или Telegram ID.</li>
        <li><strong>Кроссплатформенность:</strong> Оптимизировано для работы на Windows, Linux, Termux (Android) и iSH / a-Shell (iOS).</li>
    </ul>

    <hr>

    <h2>🚀 Быстрая установка и запуск</h2>

    <h3>🐍 Требования</h3>
    <ul>
        <li>Python 3.8+</li>
        <li>Подключение к интернету</li>
    </ul>

    <hr>

    <h3>💻 Для Windows (рекомендуемый способ: без WSL)</h3>

    <p>Это самый простой способ запуска на Windows, идеально подходящий для пользователей VS Code.</p>

    <ol>
        <li><strong>Установите Python:</strong>
            <ul>
                <li>Загрузите Python 3.8+ с <a href="https://www.python.org/downloads/windows/">официального сайта</a>.</li>
                <li><strong>ОБЯЗАТЕЛЬНО</strong> при установке поставьте галочку <code>Add Python to PATH</code>.</li>
            </ul>
        </li>
        <li><strong>Загрузите проект:</strong>
            <ul>
                <li><strong>Вариант 1 (рекомендуется):</strong> Откройте командную строку (CMD) или PowerShell, перейдите в папку, куда хотите сохранить проект, и выполните:
<pre><code>git clone https://github.com/grrrrrej/tg-star-gifts.git
cd tg-star-gifts</code></pre>
                </li>
                <li><strong>Вариант 2:</strong> Скачайте ZIP-архив проекта с GitHub (кнопка <code>Code</code> -> <code>Download ZIP</code>), распакуйте его в удобную папку и перейдите в нее.</li>
            </ul>
        </li>
        <li><strong>Создайте и активируйте виртуальное окружение (рекомендуется):</strong>
<pre><code>python -m venv venv</code></pre>
            <ul>
                <li><strong>Для CMD:</strong>
<pre><code>venv\Scripts\activate.bat</code></pre>
                </li>
                <li><strong>Для PowerShell:</strong>
<pre><code>.\venv\Scripts\Activate.ps1</code></pre>
                </li>
            </ul>
            <p>Вы увидите <code>(venv)</code> в начале командной строки, что означает, что виртуальное окружение активно.</p>
        </li>
        <li><strong>Установите зависимости:</strong>
<pre><code>pip install telethon rich</code></pre>
        </li>
        <li><strong>Запустите скрипт:</strong>
<pre><code>python main.py</code></pre>
        </li>
    </ol>

    <h4>🖥️ Интеграция с VS Code:</h4>
    <ol>
        <li>Откройте папку проекта (<code>tg-star-gifts</code>) в VS Code (<code>File</code> &gt; <code>Open Folder</code>).</li>
        <li>Откройте терминал в VS Code (<code>Terminal</code> &gt; <code>New Terminal</code>).</li>
        <li>VS Code может предложить выбрать интерпретатор Python; выберите тот, что находится в папке <code>venv</code> (<code>.\venv\Scripts\python.exe</code>).</li>
        <li>Активируйте виртуальное окружение (как описано выше).</li>
        <li>Установите зависимости (<code>pip install telethon rich</code>).</li>
        <li>Запустите скрипт через терминал (<code>python main.py</code>) или с помощью кнопки "Run" (зеленый треугольник) в VS Code.</li>
    </ol>

    <hr>

    <h3>🐧 Для Linux (Ubuntu/Debian) / 🪟 Для Windows (с WSL)</h3>

    <p>Если вы используете Linux или Windows Subsystem for Linux (WSL):</p>
<pre><code>sudo apt update && sudo apt install python3 python3-pip git curl
curl -O https://raw.githubusercontent.com/grrrrrej/tg-star-gifts/main/setup.sh
chmod +x setup.sh
./setup.sh</code></pre>
    <p>Затем выберите опцию <code>1</code> в появившемся меню для установки/обновления зависимостей.</p>

    <hr>

    <h3>📱 Для Android (Termux)</h3>
<pre><code>pkg update && pkg upgrade
pkg install python git curl
curl -O https://raw.githubusercontent.com/grrrrrej/tg-star-gifts/main/setup.sh
chmod +x setup.sh
./setup.sh</code></pre>

    <hr>

    <h3>🍎 Для iOS (iSH / a-Shell)</h3>

    <h4>iSH (рекомендуется для iOS)</h4>
    <ol>
        <li><strong>Установите iSH Shell</strong> из App Store.</li>
        <li><strong>Подготовка системы (один раз):</strong>
<pre><code>apk update && apk upgrade
apk add python3 py3-pip git curl</code></pre>
        </li>
        <li><strong>Скачивание менеджера:</strong>
<pre><code>curl -O https://raw.githubusercontent.com/grrrrrej/tg-star-gifts/main/setup.sh
chmod +x setup.sh</code></pre>
        </li>
        <li><strong>Запуск менеджера:</strong>
<pre><code>./setup.sh</code></pre>
            <p>Выберите опцию <code>1</code> для установки/обновления зависимостей, затем <code>2</code> для запуска.</p>
        </li>
    </ol>

    <h4>a-Shell (альтернатива для iOS)</h4>

    <p>a-Shell не использует <code>apk</code> и может требовать ручной установки <code>curl</code> или использования <code>fetch</code>.</p>
    <ol>
        <li><strong>Скачайте проект:</strong>
<pre><code>fetch https://raw.githubusercontent.com/grrrrrej/tg-star-gifts/main/main.py
fetch https://raw.githubusercontent.com/grrrrrej/tg-star-gifts/main/setup.sh # (опционально, для просмотра зависимостей)</code></pre>
        </li>
        <li><strong>Установите зависимости:</strong>
            <ul>
                <li>a-Shell обычно поставляется с Python и pip.</li>
                <li>Возможно, вам потребуется установить <code>telethon</code> и <code>rich</code> вручную:
<pre><code>pip install telethon rich</code></pre>
                </li>
            </ul>
        </li>
        <li><strong>Запустите скрипт:</strong>
<pre><code>python main.py</code></pre>
        </li>
    </ol>

    <hr>

    <h2>🎮 Управление скриптом</h2>

    <p>Скрипт работает в интерактивном режиме. Просто следуйте подсказкам в консоли:</p>

    <table>
        <thead>
            <tr>
                <th>Действие</th>
                <th>Инструкция</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>🎯 Выбор цели</strong></td>
                <td>Введите <code>@username</code> или <code>ID</code> пользователя</td>
            </tr>
            <tr>
                <td><strong>🎁 Выбор подарка</strong></td>
                <td>Введите цифру из предложенного списка</td>
            </tr>
            <tr>
                <td><strong>✨ Кастомный подарок</strong></td>
                <td>Используйте команду <code>/set [ID_ПОДАРКА] [Название]</code> (вводя ее вместо номера подарка)</td>
            </tr>
            <tr>
                <td><strong>🚪 Выход</strong></td>
                <td>Просто нажмите <code>Enter</code> (оставьте поле пустым)</td>
            </tr>
        </tbody>
    </table>

    <hr>

    <h2>🛠 Удобный менеджер <code>setup.sh</code></h2>

    <p>После скачивания <code>setup.sh</code> вы получите красивое меню для управления скриптом (актуально для Linux, Termux, iSH, WSL):</p>
<pre><code>./setup.sh</code></pre>

    <table>
        <thead>
            <tr>
                <th>Опция</th>
                <th>Действие</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><code>1</code></td>
                <td>🚀 Установить / Обновить зависимости</td>
            </tr>
            <tr>
                <td><code>2</code></td>
                <td>▶️ Запустить скрипт</td>
            </tr>
            <tr>
                <td><code>3</code></td>
                <td>🔄 Обновить из GitHub</td>
            </tr>
            <tr>
                <td><code>4</code></td>
                <td>🗑 Удалить скрипт и данные</td>
            </tr>
            <tr>
                <td><code>5</code></td>
                <td>ℹ️ Информация о версии</td>
            </tr>
            <tr>
                <td><code>6</code></td>
                <td>📂 Показать текущую папку</td>
            </tr>
            <tr>
                <td><code>7</code></td>
                <td>🚪 Выход</td>
            </tr>
        </tbody>
    </table>

    <hr>

    <h2>🔄 Обновление</h2>
    <ul>
        <li><strong>Через менеджер (рекомендуется для Linux, Termux, iSH, WSL):</strong>
<pre><code>./setup.sh</code></pre>
            <p>Выберите опцию <code>1</code> или <code>3</code>.</p>
        </li>
        <li><strong>Напрямую через <code>pip</code> (для всех платформ, если используется <code>venv</code>):</strong>
<pre><code>pip install --upgrade git+https://github.com/grrrrrej/tg-star-gifts.git</code></pre>
        </li>
    </ul>

    <hr>

    <h2>📂 Создаваемые файлы</h2>

    <p>Скрипт хранит данные локально в папке, из которой вы его запускаете:</p>

    <table>
        <thead>
            <tr>
                <th>Файл</th>
                <th>Описание</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><code>session.txt</code></td>
                <td>Данные вашей авторизации (сессия Telegram). <strong>НИКОМУ не показывайте этот файл!</strong> Он является вашим ключом доступа к аккаунту.</td>
            </tr>
            <tr>
                <td><code>custom_gifts.txt</code></td>
                <td>Ваши личные подарки, добавленные через <code>/set</code>.</td>
            </tr>
        </tbody>
    </table>

    <hr>

    <h2>🔐 Безопасность и предупреждения</h2>
    <ul>
        <li><strong><code>session.txt</code>:</strong> После первого входа создается файл <code>session.txt</code>. Это ваш ключ доступа. <strong>Никому не передавайте его</strong>, иначе посторонние получат полный доступ к вашему Telegram-аккаунту.</li>
        <li><strong>Баланс:</strong> Отправка подарков стоит реальных звезд Telegram. Всегда проверяйте сумму перед подтверждением.</li>
        <li><strong>Лимиты:</strong> Не превышайте разумные объемы отправки во избежание временных ограничений (Flood Wait) со стороны серверов Telegram.</li>
        <li><strong>API_ID / API_HASH:</strong> Убедитесь, что <code>API_ID</code> и <code>API_HASH</code> в вашем коде актуальны. Вы можете получить их на <a href="https://my.telegram.org/">my.telegram.org</a>.</li>
    </ul>

    <hr>

    <h2>❓ Частые вопросы (FAQ)</h2>
    <ul>
        <li><strong>Проблема:</strong> "command not found: python" или "python3"
            <ul>
                <li><strong>Решение:</strong> Убедитесь, что Python установлен и добавлен в PATH. В Linux/Termux/iSH используйте <code>python3</code>.</li>
            </ul>
        </li>
        <li><strong>Проблема:</strong> "pip: command not found"
            <ul>
                <li><strong>Решение:</strong> Установите <code>pip</code>: <code>python -m ensurepip</code> или <code>sudo apt install python3-pip</code> (Linux), <code>pkg install python</code> (Termux), <code>apk add py3-pip</code> (iSH).</li>
            </ul>
        </li>
        <li><strong>Проблема:</strong> "curl: command not found"
            <ul>
                <li><strong>Решение:</strong> Установите <code>curl</code>: <code>sudo apt install curl</code> (Linux), <code>pkg install curl</code> (Termux), <code>apk add curl</code> (iSH).</li>
            </ul>
        </li>
        <li><strong>Проблема:</strong> Медленно работает на iOS (iSH)
            <ul>
                <li><strong>Решение:</strong> iSH эмулирует Linux, поэтому скорость ниже. Просто подождите дольше при установке и отправке.</li>
            </ul>
        </li>
        <li><strong>Проблема:</strong> "RuntimeError: You must enable 'Add Python to PATH' during installation"
            <ul>
                <li><strong>Решение:</strong> Переустановите Python, обязательно отметив опцию <code>Add Python to PATH</code>.</li>
            </ul>
        </li>
        <li><strong>Проблема:</strong> Скрипт не видит сессию / <code>session.txt</code>
            <ul>
                <li><strong>Решение:</strong> Файлы сохраняются в той папке, откуда запущен скрипт. Убедитесь, что вы запускаете его из корректной директории.</li>
            </ul>
        </li>
    </ul>

    <hr>

    <h2>📜 Лицензия (GNU GPL v3.0)</h2>

    <p>Это программное обеспечение распространяется под лицензией <strong>GNU General Public License v3.0</strong>.</p>

    <p><strong>Что разрешено:</strong></p>
    <ul>
        <li>✅ Свободно использовать, изменять и распространять код.</li>
        <li>✅ Использовать в личных и некоммерческих проектах.</li>
    </ul>

    <p><strong>Что ОБЯЗАТЕЛЬНО:</strong></p>
    <ul>
        <li>🔒 Сохранять авторские права и уведомление о лицензии.</li>
        <li>🔒 Распространять производные работы <strong>только под той же лицензией (GPLv3)</strong>.</li>
        <li>🔒 Указывать изменения, внесенные вами в код.</li>
        <li>🔒 Делать исходный код доступным для всех.</li>
    </ul>

    <p><strong>Что ЗАПРЕЩЕНО:</strong></p>
    <ul>
        <li>❌ <strong>ПРОДАЖА</strong> — код не может быть продан или использован в коммерческих продуктах без открытия исходников.</li>
        <li>❌ Удаление или скрытие авторства (<code>@blackpean</code>).</li>
    </ul>

    <h3>Отказ от ответственности:</h3>
    <p>Автор не несет ответственности за возможные блокировки аккаунтов или случайные траты Telegram Stars. Вы используете скрипт на свой страх и риск.</p>

    <p>📖 <a href="https://www.gnu.org/licenses/gpl-3.0.html">Полный текст лицензии: GNU GPL v3.0</a></p>

    <hr>

    <h2>📞 Обратная связь и поддержка</h2>

    <p>По всем вопросам, багам или предложениям:</p>
    <ul>
        <li>Telegram: <code>@blackpean</code></li>
        <li>GitHub: <a href="https://github.com/grrrrrej">grrrrrej</a></li>
    </ul>

    <hr>

    <h2>⭐ Поддержка проекта</h2>

    <p>Если вам нравится этот инструмент:</p>
    <ul>
        <li>Поставьте ⭐ на <a href="https://github.com/grrrrrej/tg-star-gifts">GitHub-репозитории</a>.</li>
        <li>Поделитесь им с друзьями.</li>
        <li>Сообщите о багах в разделе <a href="https://github.com/grrrrrej/tg-star-gifts/issues">Issues</a> на GitHub.</li>
    </ul>

    <hr>

    <p>Developed with ❤️ for Telegram community.<br>
    © 2025 @blackpean | GNU GPL v3.0 | Commercial use prohibited</p>
</body>
</html>
