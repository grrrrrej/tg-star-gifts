import asyncio, os, json, binascii
from telethon import TelegramClient, events, functions, types, Button
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

# --- КОНФИГУРАЦИЯ ---
HEX_DEV = "40626c61636b7065616e"
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
SESSION_FILE = "session.txt"
GIFTS_DB = "gifts_base.json"

DEVICE_MODEL = "HP Laptop 15-da0xxx"
SYSTEM_VERSION = "Windows 11 Pro x64"
APP_VERSION = "7.8 x64"
LANG_CODE = "ru"

def get_dev():
    try: return binascii.unhexlify(HEX_DEV).decode()
    except: return "@unknown"

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
        with open(GIFTS_DB, "w", encoding="utf-8") as f:
            json.dump(init_gifts, f, ensure_ascii=False, indent=4)
        return init_gifts
    try:
        with open(GIFTS_DB, "r", encoding="utf-8") as f: return json.load(f)
    except: return init_gifts

user_state = {}
client = None

async def clear_all_current(uid):
    """Удаляет вообще все накопленные сообщения текущей сессии выбора"""
    if uid not in user_state: return
    st = user_state[uid]
    ids = set()
    if "prev_msgs" in st: ids.update(st["prev_msgs"])
    if "user_msgs" in st: ids.update(st["user_msgs"])
    if "last_msg" in st: ids.add(st["last_msg"])
    if ids:
        try: await client.delete_messages('me', list(ids))
        except: pass
    # Очищаем списки после удаления
    st["prev_msgs"] = []
    st["user_msgs"] = []

async def send_main_menu():
    try:
        res = await client(functions.payments.GetStarsStatusRequest(peer='me'))
        bal = getattr(res.balance, 'amount', res.balance)
    except: bal = "0"
    
    header = "✨✨✨ STAR GIFTS MANAGER v7.8 ✨✨✨\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    content = f"💎 БАЛАНС: {bal} STARS 💎\n\n📋 КОМАНДЫ:\n  🎁 .gift  – Отправить подарок\n  📜 .list  – Список подарков\n  ➕ .set   – Добавить подарок\n  ❌ .unset – Удалить подарок"
    footer = f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👨‍💻 DEV: {get_dev()}"
    
    msg = await client.send_message('me', f"{header}{wrap(content)}{footer}", 
        buttons=[[Button.text("🎁 .gift", resize=True)], [Button.text("💎 .bal", resize=True)]])
    return msg.id

@events.register(events.NewMessage(chats='me'))
async def message_handler(event):
    me = await client.get_me()
    uid = me.id
    text = event.text.strip()
    low_text = text.lower()

    # Обработка команды баланса
    if low_text in [".bal", "💎 .bal"]:
        await client.delete_messages('me', [event.id])
        m_id = await send_main_menu()
        await asyncio.sleep(10)
        try: await client.delete_messages('me', [m_id])
        except: pass
        return

    # Старт процесса подарка
    if low_text in [".gift", "🎁 .gift"]:
        if uid in user_state: await clear_all_current(uid)
        user_state[uid] = {
            "step": "target", "target": None, "gift": None, "qty": 1,
            "anon": False, "comment": None, "prev_msgs": [], "user_msgs": [event.id]
        }
        m = await event.respond("🎯 ШАГ 1/5\n" + wrap("Введите @username или ID получателя:"), buttons=Button.clear())
        user_state[uid]["last_msg"] = m.id
        return

    if uid not in user_state: return
    
    st = user_state[uid]
    st["user_msgs"].append(event.id)

    if st["step"] == "target":
        st["target"] = text
        st["step"] = "choice"
        db = load_db()
        await clear_all_current(uid)
        btns = [Button.text(str(i+1), resize=True) for i in range(len(db))]
        m = await event.respond("🎨 ШАГ 2/5 - ВЫБОР ПОДАРКА\n" + wrap("\n".join([f"{i+1}. {g['name']}" for i,g in enumerate(db)])), 
                               buttons=[btns[i:i+3] for i in range(0, len(btns), 3)])
        st["last_msg"] = m.id

    elif st["step"] == "choice" and text.isdigit():
        db = load_db()
        idx = int(text) - 1
        if 0 <= idx < len(db):
            st["gift"] = db[idx]
            st["step"] = "qty"
            await clear_all_current(uid)
            m = await event.respond(f"🔢 ШАГ 3/5\n{wrap('Сколько подарков отправить?')}", 
                                   buttons=[[Button.text("1"), Button.text("3"), Button.text("5"), Button.text("10")]])
            st["last_msg"] = m.id

    elif st["step"] == "qty" and text.isdigit():
        st["qty"] = int(text)
        st["step"] = "anon"
        await clear_all_current(uid)
        m = await event.respond("🙈 ШАГ 4/5\n" + wrap("Отправить анонимно?"), 
                               buttons=[[Button.text("ДА"), Button.text("НЕТ")]])
        st["last_msg"] = m.id

    elif st["step"] == "anon":
        st["anon"] = "да" in low_text
        await clear_all_current(uid)
        if st["anon"]:
            st["comment"] = None
            st["step"] = "confirm"
            conf = f"📋 ИТОГ ПЕРЕД ОТПРАВКОЙ 📋\n\n🎁 Подарок: {st['gift']['name']}\n🔢 Кол-во: {st['qty']}\n👤 Кому: {st['target']}\n🙈 Анонимно: ДА"
            m = await event.respond(wrap(conf + "\n\n✅ ВСЁ ВЕРНО?"), buttons=[[Button.text("✅ ДА"), Button.text("❌ ОТМЕНА")]])
        else:
            st["step"] = "comment"
            m = await event.respond("💬 ШАГ 5/5\n" + wrap("Введите комментарий:"), buttons=[[Button.text("ПРОПУСТИТЬ")]])
        st["last_msg"] = m.id

    elif st["step"] == "comment":
        if "пропустить" not in low_text: st["comment"] = text
        st["step"] = "confirm"
        await clear_all_current(uid)
        conf = f"📋 ИТОГ ПЕРЕД ОТПРАВКОЙ 📋\n\n🎁 Подарок: {st['gift']['name']}\n🔢 Кол-во: {st['qty']}\n👤 Кому: {st['target']}\n🙈 Анонимно: НЕТ\n💬 Текст: {st['comment'] or '-'}"
        m = await event.respond(wrap(conf + "\n\n✅ ВСЁ ВЕРНО?"), buttons=[[Button.text("✅ ДА"), Button.text("❌ ОТМЕНА")]])
        st["last_msg"] = m.id

    elif st["step"] == "confirm":
        if "✅" in text or "да" in low_text:
            await execute_gift(event, uid)
        else:
            await clear_all_current(uid)
            user_state.pop(uid, None)
            await send_main_menu()

async def execute_gift(event, uid):
    s = user_state[uid]
    await clear_all_current(uid)
    status = await event.respond(wrap("🚀 Запуск процесса отправки..."))
    success = 0
    
    try:
        peer = await client.get_entity(s["target"])
        for _ in range(s["qty"]):
            try:
                msg_obj = None
                if not s["anon"] and s["comment"]:
                    msg_obj = types.TextWithEntities(s["comment"], [])
                
                inv = types.InputInvoiceStarGift(peer=peer, gift_id=s["gift"]["id"], hide_name=s["anon"], message=msg_obj)
                form = await client(functions.payments.GetPaymentFormRequest(invoice=inv))
                await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=inv))
                success += 1
            except FloodWaitError as e: await asyncio.sleep(e.seconds)
            except: break
            await asyncio.sleep(1.5)
        
        res = await event.respond(wrap(f"✅ ГОТОВО\n\nОтправлено: {success} из {s['qty']}\nПолучатель: {s['target']}"))
        await asyncio.sleep(10)
        try: await client.delete_messages('me', [status.id, res.id])
        except: pass
    except Exception as e:
        err = await event.respond(wrap(f"❌ ОШИБКА: {e}"))
        await asyncio.sleep(10)
        try: await client.delete_messages('me', [status.id, err.id])
        except: pass
    
    user_state.pop(uid, None)
    await send_main_menu()

async def main():
    global client
    if not os.path.exists(SESSION_FILE): open(SESSION_FILE, 'w').close()
    with open(SESSION_FILE, 'r') as f: ss = f.read().strip()

    client = TelegramClient(StringSession(ss), API_ID, API_HASH, device_model=DEVICE_MODEL)
    client.add_event_handler(message_handler)

    print("🔑 Авторизация...")
    await client.start(
        phone=lambda: input("📱 Номер: "),
        code_callback=lambda: input("💬 Код: "),
        password=lambda: input("🔑 2FA: ")
    )

    with open(SESSION_FILE, 'w') as f: f.write(client.session.save())
    
    me = await client.get_me()
    print(f"🚀 Бот запущен! Аккаунт: {me.first_name}")
    
    # Показываем меню и удаляем через 10 сек
    m_id = await send_main_menu()
    await asyncio.sleep(10)
    try: await client.delete_messages('me', [m_id])
    except: pass

    await client.run_until_disconnected()

def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    run()
