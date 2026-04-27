import asyncio, os, json, binascii
from telethon import TelegramClient, events, functions, types, Button
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

HEX_DEV = "40626c61636b7065616e"
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
SESSION_FILE = "session.txt"
GIFTS_DB = "gifts_base.json"

DEVICE_MODEL = "HP Laptop 15-da0xxx"
SYSTEM_VERSION = "Windows 11 Pro x64"
APP_VERSION = "6.5.1 x64"
LANG_CODE = "ru"
SYSTEM_LANG_CODE = "ru-RU"

def get_dev():
    try:
        return binascii.unhexlify(HEX_DEV).decode()
    except Exception:
        return "@unknown"

def wrap(text):
    return f"```\n{text}\n```"

init_gifts = [
    {"name": "🎄 Елка", "id": 5922558454332916696},
    {"name": "🧸 Мишка", "id": 5956217000635139069},
    {"name": "❤️ Сердце", "id": 5801108895304779062},
    {"name": "🎁 14 февраля", "id": 5800655655995968830},
    {"name": "🌸 8 марта", "id": 5866352046986232958},
    {"name": "🍀 Патрик", "id": 5893356958802511476},
    {"name": "🤡 Клоун", "id": 5935895822435615975}
]

def load_db():
    if not os.path.exists(GIFTS_DB):
        save_db(init_gifts)
        return init_gifts
    try:
        with open(GIFTS_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return init_gifts

def save_db(data):
    with open(GIFTS_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def list_gifts_text(db):
    text = "📦 Доступные подарки:\n\n"
    for i, g in enumerate(db, 1):
        text += f"{i}. {g['name']} (ID: {g['id']})\n"
    return text

user_state = {}
client = None

async def clean_chat(event, uid):
    targets = [event.id]
    if uid in user_state and "last_msg" in user_state[uid]:
        targets.append(user_state[uid]["last_msg"])
    try:
        await client.delete_messages('me', targets)
    except:
        pass

async def send_main_menu():
    try:
        res = await client(functions.payments.GetStarsStatusRequest(peer='me'))
        bal = getattr(res.balance, 'amount', res.balance)
    except:
        bal = "ERR"
    
    header = (
        f"✨ STAR GIFTS MANAGER v7.5\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💎 Баланс: {bal} Stars\n\n"
        f"📋 Команды:\n"
        f"  • .gift  – Мастер подарков\n"
        f"  • .list  – Список подарков\n"
        f"  • .set   – Добавить подарок\n"
        f"  • .unset – Удалить подарок"
    )
    
    footer = f"👨‍💻 Dev: {get_dev()}"
    
    msg = await client.send_message(
        'me', 
        f"{wrap(header)}\n{footer}", 
        buttons=[[Button.text(".gift", resize=True)], [Button.text(".bal", resize=True)]]
    )
    return msg.id

async def send_stars_request_with_retry(invoice, event, retry_count=0):
    try:
        form = await client(functions.payments.GetPaymentFormRequest(invoice=invoice))
        await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=invoice))
        return True
    except FloodWaitError as e:
        wait_time = e.seconds
        await event.respond(wrap(f"⏳ Лимит Telegram! Ожидание {wait_time} сек. (попытка {retry_count + 1}/3)..."))
        await asyncio.sleep(wait_time)
        if retry_count < 2:
            return await send_stars_request_with_retry(invoice, event, retry_count + 1)
        else:
            await event.respond(wrap("❌ Превышены лимиты Telegram. Попробуйте позже."))
            return False
    except Exception as e:
        if retry_count < 2:
            await asyncio.sleep(3)
            return await send_stars_request_with_retry(invoice, event, retry_count + 1)
        else:
            raise e

@events.register(events.NewMessage(chats='me'))
async def message_handler(event):
    me = await client.get_me()
    uid = me.id
    text = event.text.strip()
    low_text = text.lower()
    args = text.split()

    if low_text == ".bal":
        await clean_chat(event, uid)
        return await send_main_menu()
    
    if low_text == ".list":
        await clean_chat(event, uid)
        db = load_db()
        await event.respond(wrap(list_gifts_text(db)))
        await send_main_menu()
        return

    if low_text.startswith(".set "):
        await clean_chat(event, uid)
        if len(args) >= 3:
            name = " ".join(args[1:-1])
            try:
                g_id = int(args[-1])
                db = load_db()
                existing = [g for g in db if g['name'].lower() == name.lower()]
                if existing:
                    await event.respond(wrap(f"❌ Подарок '{name}' уже существует!"))
                else:
                    db.append({"name": name, "id": g_id})
                    save_db(db)
                    await event.respond(wrap(f"✅ Подарок добавлен:\n{name}\nID: {g_id}"))
            except ValueError:
                await event.respond(wrap("❌ ID должен быть числом!"))
        else:
            await event.respond(wrap("❌ Использование:\n.set Название ID\n\nПример: .set 🎁 Новый 123456789"))
        await send_main_menu()
        return

    if low_text.startswith(".unset "):
        await clean_chat(event, uid)
        if len(args) == 2:
            try:
                num = int(args[1])
                db = load_db()
                if 1 <= num <= len(db):
                    removed = db.pop(num - 1)
                    save_db(db)
                    await event.respond(wrap(f"✅ Удалён подарок #{num}:\n{removed['name']}"))
                else:
                    await event.respond(wrap(f"❌ Номер должен быть от 1 до {len(db)}"))
            except ValueError:
                await event.respond(wrap("❌ Введите номер подарка для удаления\nПример: .unset 3"))
        else:
            await event.respond(wrap("❌ Использование:\n.unset НОМЕР\n\nПосмотреть номера: .list"))
        await send_main_menu()
        return

    if low_text == ".gift":
        await clean_chat(event, uid)
        user_state[uid] = {
            "step": "target",
            "target": None,
            "gift": None,
            "qty": 1,
            "anon": False,
            "comment": None
        }
        m = await event.respond(wrap("🎁 Шаг 1/4 – Получатель\n\nВведите @username или ID:"), buttons=Button.clear())
        user_state[uid]["last_msg"] = m.id
        return

    if uid not in user_state:
        return
    
    st = user_state[uid]

    if st["step"] == "target":
        await clean_chat(event, uid)
        st.update({"target": text, "step": "choice"})
        db = load_db()
        menu = "🎁 Шаг 2/4 – Выбор подарка\n\n" + list_gifts_text(db)
        btns = []
        for i in range(len(db)):
            btns.append(Button.text(str(i+1), resize=True))
        m = await event.respond(wrap(menu), buttons=[btns[i:i+3] for i in range(0, len(btns), 3)])
        st["last_msg"] = m.id

    elif st["step"] == "choice" and text.isdigit():
        db = load_db()
        idx = int(text) - 1
        if 0 <= idx < len(db):
            await clean_chat(event, uid)
            st.update({"gift": db[idx], "step": "qty"})
            m = await event.respond(wrap(f"🎁 Шаг 3/4 – Количество\n\nВыбрано: {db[idx]['name']}\nВведите число:"), 
                                    buttons=[[Button.text("1"), Button.text("3"), Button.text("5")]])
            st["last_msg"] = m.id
        else:
            await clean_chat(event, uid)
            m = await event.respond(wrap(f"❌ Неверный номер. Введите число от 1 до {len(db)}"))
            st["last_msg"] = m.id

    elif st["step"] == "qty" and text.isdigit():
        qty = int(text)
        if qty > 50:
            await clean_chat(event, uid)
            m = await event.respond(wrap("⚠️ Предупреждение: большое количество подарков\nTelegram может временно ограничить аккаунт.\n\nПродолжить?"), 
                                    buttons=[[Button.text("✅ Да"), Button.text("❌ Нет")]])
            st["last_msg"] = m.id
            st["pending_qty"] = qty
            st["step"] = "confirm_large_qty"
        else:
            await clean_chat(event, uid)
            st.update({"qty": qty, "step": "anon"})
            m = await event.respond(wrap("🎁 Шаг 4/4 – Анонимность\n\nСкрыть ваше имя?"), 
                                    buttons=[[Button.text("Да"), Button.text("Нет")]])
            st["last_msg"] = m.id

    elif st["step"] == "confirm_large_qty":
        await clean_chat(event, uid)
        if "да" in low_text:
            st.update({"qty": st["pending_qty"], "step": "anon"})
            m = await event.respond(wrap("🎁 Шаг 4/4 – Анонимность\n\nСкрыть ваше имя?"), 
                                    buttons=[[Button.text("Да"), Button.text("Нет")]])
            st["last_msg"] = m.id
        else:
            user_state.pop(uid, None)
            await send_main_menu()
        return

    elif st["step"] == "anon":
        await clean_chat(event, uid)
        is_anon = "да" in low_text
        st.update({"anon": is_anon, "step": "comment"})
        
        if is_anon:
            await execute_gift(event, uid)
        else:
            m = await event.respond(wrap("💬 Комментарий к подарку\n\nВведите текст или нажмите кнопку:"), 
                                    buttons=[[Button.text("Пропустить")]])
            st["last_msg"] = m.id

    elif st["step"] == "comment":
        await clean_chat(event, uid)
        if "пропустить" not in low_text:
            st["comment"] = text
        await execute_gift(event, uid)

async def execute_gift(event, uid):
    s = user_state[uid]
    status_msg = await event.respond(wrap("🚀 Отправка подарков..."))
    
    success_count = 0
    fail_count = 0
    
    try:
        peer = await client.get_entity(s["target"])
        
        for i in range(s["qty"]):
            comment_obj = None
            if not s["anon"] and s.get("comment"):
                comment_obj = types.TextWithEntities(s["comment"], [])
            
            inv = types.InputInvoiceStarGift(
                peer=peer, 
                gift_id=s["gift"]["id"], 
                hide_name=s["anon"],
                message=comment_obj
            )
            
            try:
                success = await send_stars_request_with_retry(inv, event)
                if success:
                    success_count += 1
                else:
                    fail_count += 1
                    break
            except Exception as e:
                fail_count += 1
                await event.respond(wrap(f"❌ Ошибка при отправке #{i+1}:\n{str(e)}"))
                break
            
            if s["qty"] > 1 and i < s["qty"] - 1:
                await asyncio.sleep(2)
        
        if success_count > 0:
            result_text = (
                f"✅ ОТПРАВЛЕНО\n\n"
                f"🎁 Подарок: {s['gift']['name']}\n"
                f"📦 Кол-во: {success_count}/{s['qty']}\n"
                f"👤 Кому: {s['target']}\n"
                f"👻 Анонимно: {'Да' if s['anon'] else 'Нет'}"
            )
            if s.get("comment") and not s["anon"]:
                result_text += f"\n💬 Комментарий: {s['comment']}"
            if fail_count > 0:
                result_text += f"\n\n⚠️ Не отправлено: {fail_count}"
            
            await event.respond(wrap(result_text))
        else:
            await event.respond(wrap("❌ НЕ УДАЛОСЬ ОТПРАВИТЬ\n\nПроверьте баланс Stars или повторите позже."))
        
    except Exception as e:
        await event.respond(wrap(f"❌ КРИТИЧЕСКАЯ ОШИБКА\n\n{str(e)}"))
    
    try:
        await client.delete_messages('me', [status_msg.id])
    except:
        pass
    
    user_state.pop(uid, None)
    await send_main_menu()

async def main():
    global client
    ss = ""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            ss = f.read().strip()
    
    client = TelegramClient(
        StringSession(ss),
        API_ID,
        API_HASH,
        device_model=DEVICE_MODEL,
        system_version=SYSTEM_VERSION,
        app_version=APP_VERSION,
        lang_code=LANG_CODE,
        system_lang_code=SYSTEM_LANG_CODE
    )
    
    client.add_event_handler(message_handler)
    
    await client.start()
    if not ss:
        with open(SESSION_FILE, "w") as f:
            f.write(client.session.save())
    
    await send_main_menu()
    
    me = await client.get_me()
    print(f"Star Gifts Manager запущен")
    print(f"Аккаунт: {me.first_name}")
    print(f"Подарков в базе: {len(load_db())}")
    
    await client.run_until_disconnected()

def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()        'me', 
        f"{wrap(header)}\n{footer}", 
        buttons=[[Button.text(".gift", resize=True)], [Button.text(".bal", resize=True)]]
    )
    return msg.id

async def send_stars_request_with_retry(invoice, event, retry_count=0):
    """Отправка запроса с обработкой FloodWait"""
    try:
        form = await client(functions.payments.GetPaymentFormRequest(invoice=invoice))
        await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=invoice))
        return True
    except FloodWaitError as e:
        wait_time = e.seconds
        await event.respond(wrap(f"⏳ Лимит Telegram! Ожидание {wait_time} сек. (попытка {retry_count + 1}/3)..."))
        await asyncio.sleep(wait_time)
        if retry_count < 2:
            return await send_stars_request_with_retry(invoice, event, retry_count + 1)
        else:
            await event.respond(wrap("❌ Превышены лимиты Telegram. Попробуйте позже."))
            return False
    except Exception as e:
        if retry_count < 2:
            await asyncio.sleep(3)
            return await send_stars_request_with_retry(invoice, event, retry_count + 1)
        else:
            raise e

@events.register(events.NewMessage(chats='me'))
async def message_handler(event):
    me = await client.get_me()
    uid = me.id
    text = event.text.strip()
    low_text = text.lower()
    args = text.split()

    if low_text == ".bal":
        await clean_chat(event, uid)
        return await send_main_menu()
    
    if low_text == ".list":
        await clean_chat(event, uid)
        db = load_db()
        await event.respond(wrap(list_gifts_text(db)))
        await send_main_menu()
        return

    if low_text.startswith(".set "):
        await clean_chat(event, uid)
        if len(args) >= 3:
            name = " ".join(args[1:-1])
            try:
                g_id = int(args[-1])
                db = load_db()
                existing = [g for g in db if g['name'].lower() == name.lower()]
                if existing:
                    await event.respond(wrap(f"❌ Подарок '{name}' уже существует!\nИспользуйте другое название."))
                else:
                    db.append({"name": name, "id": g_id})
                    save_db(db)
                    await event.respond(wrap(f"✅ Подарок добавлен:\n{name}\nID: {g_id}"))
            except ValueError:
                await event.respond(wrap("❌ ID должен быть числом!"))
        else:
            await event.respond(wrap("❌ Использование:\n.set Название ID\n\nПример: .set 🎁 Новый 123456789"))
        await send_main_menu()
        return

    if low_text.startswith(".unset "):
        await clean_chat(event, uid)
        if len(args) == 2:
            try:
                num = int(args[1])
                db = load_db()
                if 1 <= num <= len(db):
                    removed = db.pop(num - 1)
                    save_db(db)
                    await event.respond(wrap(f"✅ Удалён подарок #{num}:\n{removed['name']}"))
                else:
                    await event.respond(wrap(f"❌ Номер должен быть от 1 до {len(db)}"))
            except ValueError:
                await event.respond(wrap("❌ Введите номер подарка для удаления\nПример: .unset 3"))
        else:
            await event.respond(wrap("❌ Использование:\n.unset НОМЕР\n\nПосмотреть номера: .list"))
        await send_main_menu()
        return

    if low_text == ".gift":
        await clean_chat(event, uid)
        user_state[uid] = {
            "step": "target",
            "target": None,
            "gift": None,
            "qty": 1,
            "anon": False,
            "comment": None
        }
        m = await event.respond(wrap("🎁 Шаг 1/4 – Получатель\n\nВведите @username или ID:"), buttons=Button.clear())
        user_state[uid]["last_msg"] = m.id
        return

    if uid not in user_state:
        return
    
    st = user_state[uid]

    if st["step"] == "target":
        await clean_chat(event, uid)
        st.update({"target": text, "step": "choice"})
        db = load_db()
        menu = "🎁 Шаг 2/4 – Выбор подарка\n\n" + list_gifts_text(db)
        btns = []
        for i in range(len(db)):
            btns.append(Button.text(str(i+1), resize=True))
        m = await event.respond(wrap(menu), buttons=[btns[i:i+3] for i in range(0, len(btns), 3)])
        st["last_msg"] = m.id

    elif st["step"] == "choice" and text.isdigit():
        db = load_db()
        idx = int(text) - 1
        if 0 <= idx < len(db):
            await clean_chat(event, uid)
            st.update({"gift": db[idx], "step": "qty"})
            m = await event.respond(wrap(f"🎁 Шаг 3/4 – Количество\n\nВыбрано: {db[idx]['name']}\nВведите число:"), 
                                    buttons=[[Button.text("1"), Button.text("3"), Button.text("5")]])
            st["last_msg"] = m.id
        else:
            await clean_chat(event, uid)
            m = await event.respond(wrap(f"❌ Неверный номер. Введите число от 1 до {len(db)}"))
            st["last_msg"] = m.id

    elif st["step"] == "qty" and text.isdigit():
        qty = int(text)
        if qty > 50:
            await clean_chat(event, uid)
            m = await event.respond(wrap("⚠️ Предупреждение: большое количество подарков\n"
                                        "Telegram может временно ограничить аккаунт.\n\n"
                                        "Продолжить?"), 
                                    buttons=[[Button.text("✅ Да"), Button.text("❌ Нет")]])
            st["last_msg"] = m.id
            st["pending_qty"] = qty
            st["step"] = "confirm_large_qty"
        else:
            await clean_chat(event, uid)
            st.update({"qty": qty, "step": "anon"})
            m = await event.respond(wrap("🎁 Шаг 4/4 – Анонимность\n\nСкрыть ваше имя?"), 
                                    buttons=[[Button.text("Да"), Button.text("Нет")]])
            st["last_msg"] = m.id

    elif st["step"] == "confirm_large_qty":
        await clean_chat(event, uid)
        if "да" in low_text:
            st.update({"qty": st["pending_qty"], "step": "anon"})
            m = await event.respond(wrap("🎁 Шаг 4/4 – Анонимность\n\nСкрыть ваше имя?"), 
                                    buttons=[[Button.text("Да"), Button.text("Нет")]])
            st["last_msg"] = m.id
        else:
            user_state.pop(uid, None)
            await send_main_menu()
        return

    elif st["step"] == "anon":
        await clean_chat(event, uid)
        is_anon = "да" in low_text
        st.update({"anon": is_anon, "step": "comment"})
        
        if is_anon:
            await execute_gift(event, uid)
        else:
            m = await event.respond(wrap("💬 Комментарий к подарку\n\nВведите текст или нажмите кнопку:"), 
                                    buttons=[[Button.text("Пропустить")]])
            st["last_msg"] = m.id

    elif st["step"] == "comment":
        await clean_chat(event, uid)
        if "пропустить" not in low_text:
            st["comment"] = text
        await execute_gift(event, uid)

async def execute_gift(event, uid):
    s = user_state[uid]
    status_msg = await event.respond(wrap("🚀 Отправка подарков..."))
    
    success_count = 0
    fail_count = 0
    
    try:
        peer = await client.get_entity(s["target"])
        
        for i in range(s["qty"]):
            comment_obj = None
            if not s["anon"] and s.get("comment"):
                comment_obj = types.TextWithEntities(s["comment"], [])
            
            inv = types.InputInvoiceStarGift(
                peer=peer, 
                gift_id=s["gift"]["id"], 
                hide_name=s["anon"],
                message=comment_obj
            )
            
            try:
                success = await send_stars_request_with_retry(inv, event)
                if success:
                    success_count += 1
                else:
                    fail_count += 1
                    break
            except Exception as e:
                fail_count += 1
                await event.respond(wrap(f"❌ Ошибка при отправке #{i+1}:\n{str(e)}"))
                break
            
            if s["qty"] > 1 and i < s["qty"] - 1:
                await asyncio.sleep(2)
        
        if success_count > 0:
            result_text = (
                f"✅ ОТПРАВЛЕНО\n\n"
                f"🎁 Подарок: {s['gift']['name']}\n"
                f"📦 Кол-во: {success_count}/{s['qty']}\n"
                f"👤 Кому: {s['target']}\n"
                f"👻 Анонимно: {'Да' if s['anon'] else 'Нет'}"
            )
            if s.get("comment") and not s["anon"]:
                result_text += f"\n💬 Комментарий: {s['comment']}"
            if fail_count > 0:
                result_text += f"\n\n⚠️ Не отправлено: {fail_count}"
            
            await event.respond(wrap(result_text))
        else:
            await event.respond(wrap("❌ НЕ УДАЛОСЬ ОТПРАВИТЬ\n\nПроверьте баланс Stars или повторите позже."))
        
    except Exception as e:
        await event.respond(wrap(f"❌ КРИТИЧЕСКАЯ ОШИБКА\n\n{str(e)}"))
    
    try:
        await client.delete_messages('me', [status_msg.id])
    except:
        pass
    
    user_state.pop(uid, None)
    await send_main_menu()

async def main():
    global client
    ss = ""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            ss = f.read().strip()
    
    client = TelegramClient(
        StringSession(ss),
        API_ID,
        API_HASH,
        device_model=DEVICE_MODEL,
        system_version=SYSTEM_VERSION,
        app_version=APP_VERSION,
        lang_code=LANG_CODE,
        system_lang_code=SYSTEM_LANG_CODE
    )
    
    client.add_event_handler(message_handler)
    
    await client.start()
    if not ss:
        with open(SESSION_FILE, "w") as f:
            f.write(client.session.save())
    
    await send_main_menu()
    
    me = await client.get_me()
    print(f"✨ Star Gifts Manager запущен")
    print(f"👤 Аккаунт: {me.first_name}")
    print(f"📦 Подарков в базе: {len(load_db())}")
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
