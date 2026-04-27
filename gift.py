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
    {"name": "🎄 Новогодний мишка", "id": 5956217000635139069},
    {"name": "❤️ Сердце валентинка", "id": 5801108895304779062},
    {"name": "🧸 Мишка 14 февраля", "id": 5800655655995968830},
    {"name": "🌸 Мишка 8 марта", "id": 5866352046986232958},
    {"name": "🍀 Мишка Патрик", "id": 5893356958802511476},
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
    text = "🎁 ВЫБЕРИ ПОДАРОК 🎁\n\n"
    for i, g in enumerate(db, 1):
        text += f"{i}. {g['name']}\n"
    return text

user_state = {}
client = None

async def clean_previous(event, uid, keep_last=False):
    if uid not in user_state:
        return
    targets = []
    if "prev_msgs" in user_state[uid]:
        targets.extend(user_state[uid]["prev_msgs"])
    if "user_msgs" in user_state[uid]:
        targets.extend(user_state[uid]["user_msgs"])
    if not keep_last and "last_msg" in user_state[uid]:
        targets.append(user_state[uid]["last_msg"])
    if targets:
        try:
            await client.delete_messages('me', targets)
        except:
            pass
    if not keep_last:
        user_state[uid]["prev_msgs"] = []
        user_state[uid]["user_msgs"] = []
        if "last_msg" in user_state[uid]:
            user_state[uid]["prev_msgs"].append(user_state[uid]["last_msg"])

async def send_main_menu():
    try:
        res = await client(functions.payments.GetStarsStatusRequest(peer='me'))
        bal = getattr(res.balance, 'amount', res.balance)
    except:
        bal = "ERR"
    
    header = "✨✨✨ STAR GIFTS MANAGER v7.5 ✨✨✨\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    content = f"💎 БАЛАНС: {bal} STARS 💎\n\n📋 КОМАНДЫ:\n  🎁 .gift  – Отправить подарок\n  📜 .list  – Список подарков\n  ➕ .set   – Добавить подарок\n  ❌ .unset – Удалить подарок"
    footer = f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👨‍💻 DEV: {get_dev()}"
    
    msg = await client.send_message(
        'me', 
        f"{header}{wrap(content)}{footer}", 
        buttons=[[Button.text("🎁 .gift", resize=True)], [Button.text("💎 .bal", resize=True)]]
    )
    return msg.id

async def send_stars_request_with_retry(invoice, event, retry_count=0):
    try:
        form = await client(functions.payments.GetPaymentFormRequest(invoice=invoice))
        await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=invoice))
        return True
    except FloodWaitError as e:
        wait_time = e.seconds
        await event.respond(wrap(f"⏳ Лимит! Жди {wait_time} сек..."))
        await asyncio.sleep(wait_time)
        if retry_count < 2:
            return await send_stars_request_with_retry(invoice, event, retry_count + 1)
        else:
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

    if low_text == ".bal" or low_text == "💎 .bal":
        await clean_previous(event, uid)
        return await send_main_menu()
    
    if low_text == ".list" or low_text == "📜 .list":
        await clean_previous(event, uid)
        db = load_db()
        await event.respond(wrap(list_gifts_text(db)))
        await send_main_menu()
        return

    if low_text.startswith(".set "):
        await clean_previous(event, uid)
        if len(args) >= 3:
            name = " ".join(args[1:-1])
            try:
                g_id = int(args[-1])
                db = load_db()
                existing = [g for g in db if g['name'].lower() == name.lower()]
                if existing:
                    await event.respond(wrap(f"❌ Подарок '{name}' уже есть!"))
                else:
                    db.append({"name": name, "id": g_id})
                    save_db(db)
                    await event.respond(wrap(f"✅ ДОБАВЛЕН!\n\n{name}\n🆔 ID: {g_id}"))
            except ValueError:
                await event.respond(wrap("❌ ID должен быть числом!"))
        else:
            await event.respond(wrap("❌ .set Название ID\nПример: .set 🎁 Новый 123"))
        await send_main_menu()
        return

    if low_text.startswith(".unset "):
        await clean_previous(event, uid)
        if len(args) == 2:
            try:
                num = int(args[1])
                db = load_db()
                if 1 <= num <= len(db):
                    removed = db.pop(num - 1)
                    save_db(db)
                    await event.respond(wrap(f"✅ УДАЛЁН #{num}:\n{removed['name']}"))
                else:
                    await event.respond(wrap(f"❌ Номер от 1 до {len(db)}"))
            except ValueError:
                await event.respond(wrap("❌ .unset НОМЕР"))
        else:
            await event.respond(wrap("❌ .unset НОМЕР"))
        await send_main_menu()
        return

    if low_text == ".gift" or low_text == "🎁 .gift":
        await clean_previous(event, uid)
        user_state[uid] = {
            "step": "target",
            "target": None,
            "gift": None,
            "qty": 1,
            "anon": False,
            "comment": None,
            "prev_msgs": [],
            "user_msgs": []
        }
        m = await event.respond(
            "🎯 ШАГ 1/5 - КТО ПОЛУЧАЕТ? 🎯\n" + wrap("Введите @username или ID получателя:"), 
            buttons=Button.clear()
        )
        user_state[uid]["last_msg"] = m.id
        user_state[uid]["prev_msgs"] = [m.id]
        return

    if uid not in user_state:
        return
    
    st = user_state[uid]
    
    if "user_msgs" not in st:
        st["user_msgs"] = []
    st["user_msgs"].append(event.id)

    if st["step"] == "target":
        await clean_previous(event, uid, keep_last=True)
        st.update({"target": text, "step": "choice"})
        db = load_db()
        menu = "🎨 ШАГ 2/5 - ВЫБОР ПОДАРКА 🎨\n" + wrap(list_gifts_text(db))
        btns = []
        for i in range(len(db)):
            btns.append(Button.text(str(i+1), resize=True))
        m = await event.respond(menu, buttons=[btns[i:i+3] for i in range(0, len(btns), 3)])
        st["last_msg"] = m.id
        st["prev_msgs"].append(m.id)

    elif st["step"] == "choice" and text.isdigit():
        db = load_db()
        idx = int(text) - 1
        if 0 <= idx < len(db):
            await clean_previous(event, uid, keep_last=True)
            st.update({"gift": db[idx], "step": "qty"})
            m = await event.respond(
                "🔢 ШАГ 3/5 - КОЛИЧЕСТВО 🔢\n" + wrap(f"Выбрано: {db[idx]['name']}\nСколько подарков отправить?"), 
                buttons=[[Button.text("1"), Button.text("3"), Button.text("5"), Button.text("10")]]
            )
            st["last_msg"] = m.id
            st["prev_msgs"].append(m.id)
        else:
            await clean_previous(event, uid, keep_last=True)
            m = await event.respond(wrap(f"❌ Введите число от 1 до {len(db)}"))
            st["last_msg"] = m.id
            st["prev_msgs"].append(m.id)

    elif st["step"] == "qty" and text.isdigit():
        qty = int(text)
        await clean_previous(event, uid, keep_last=True)
        st.update({"qty": qty, "step": "anon"})
        m = await event.respond(
            "🙈 ШАГ 4/5 - АНОНИМНОСТЬ 🙈\n" + wrap("Отправить анонимно?\n\nОтветьте: Да или Нет"), 
            buttons=[[Button.text("ДА"), Button.text("НЕТ")]]
        )
        st["last_msg"] = m.id
        st["prev_msgs"].append(m.id)

    elif st["step"] == "anon":
        await clean_previous(event, uid, keep_last=True)
        is_anon = "да" in low_text
        st.update({"anon": is_anon, "step": "comment"})
        
        m = await event.respond(
            "💬 ШАГ 5/5 - КОММЕНТАРИЙ 💬\n" + wrap("Введите комментарий или нажмите кнопку ПРОПУСТИТЬ"), 
            buttons=[[Button.text("ПРОПУСТИТЬ")]]
        )
        st["last_msg"] = m.id
        st["prev_msgs"].append(m.id)

    elif st["step"] == "comment":
        await clean_previous(event, uid, keep_last=True)
        if "пропустить" not in low_text:
            st["comment"] = text
        
        confirm_text = f"📋 ПРОВЕРЬТЕ ДАННЫЕ 📋\n\n🎁 Подарок: {st['gift']['name']}\n🔢 Количество: {st['qty']}\n👤 Получатель: {st['target']}\n🙈 Анонимно: {'ДА' if st['anon'] else 'НЕТ'}"
        
        if st.get("comment"):
            confirm_text += f"\n💬 Комментарий: {st['comment']}"
        confirm_text += "\n\n✅ ВСЁ ВЕРНО?\n\nОтветьте: ДА или НЕТ"
        
        m = await event.respond(
            wrap(confirm_text),
            buttons=[[Button.text("✅ ДА"), Button.text("❌ НЕТ, ЗАНОВО")]]
        )
        st["last_msg"] = m.id
        st["prev_msgs"].append(m.id)
        st["step"] = "confirm"

    elif st["step"] == "confirm":
        await clean_previous(event, uid, keep_last=True)
        if "✅" in text or "да" in low_text:
            await execute_gift(event, uid)
        else:
            user_state.pop(uid, None)
            await send_main_menu()

async def execute_gift(event, uid):
    s = user_state[uid]
    
    status_msg = await event.respond(wrap("🚀 ОТПРАВКА ПОДАРКОВ... 🚀"))
    
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
                break
            
            if s["qty"] > 1 and i < s["qty"] - 1:
                await asyncio.sleep(2)
        
        result_text = f"✅ ОТПРАВЛЕНО\n\n🎁 {s['gift']['name']}\n🔢 x{success_count}/{s['qty']}\n👤 {s['target']}\n🙈 Аноним: {'ДА' if s['anon'] else 'НЕТ'}"
        
        if s.get("comment") and not s["anon"]:
            result_text += f"\n💬 Комментарий: {s['comment']}"
        
        if fail_count > 0:
            result_text += f"\n\n⚠️ Не отправлено: {fail_count}"
        
        result_msg = await event.respond(wrap(result_text))
        
        await asyncio.sleep(10)
        
        try:
            await client.delete_messages('me', [result_msg.id])
        except:
            pass
        
    except Exception as e:
        error_msg = await event.respond(wrap(f"❌ ОШИБКА\n\n{str(e)}"))
        await asyncio.sleep(10)
        try:
            await client.delete_messages('me', [error_msg.id])
        except:
            pass
    
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
    
    # === ИЗМЕНЕНИЯ ЗДЕСЬ ===
    # Явные запросы для авторизации через терминал
    await client.start(
        phone=lambda: input("📱 Введите ваш номер телефона (например, +1234567890): "),
        code_callback=lambda: input("💬 Введите код из Telegram: "),
        password=lambda: input("🔑 Введите пароль 2FA (если нет - просто нажмите Enter): ")
    )
    # =======================

    if not ss:
        with open(SESSION_FILE, "w") as f:
            f.write(client.session.save())
    
    await send_main_menu()
    
    me = await client.get_me()
    print(f"✨ Star Gifts Manager v7.5 ✨")
    print(f"👤 Аккаунт: {me.first_name}")
    print(f"📦 Подарков: {len(load_db())}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━")
    
    try:
        await client.run_until_disconnected()
    except KeyboardInterrupt:
        print(f"\n👋 Завершение...")
    finally:
        print(f"✅ Бот остановлен")

def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()
