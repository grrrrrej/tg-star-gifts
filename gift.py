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
APP_VERSION = "6.5.1 x64"
LANG_CODE = "ru"

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
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

async def clear_session_messages(uid, extra_ids=None):
    if uid not in user_state: return
    ids = set()
    st = user_state[uid]
    if "prev_msgs" in st: ids.update(st["prev_msgs"])
    if "user_msgs" in st: ids.update(st["user_msgs"])
    if "last_msg" in st: ids.add(st["last_msg"])
    if extra_ids: ids.update(extra_ids)
    if ids:
        try: await client.delete_messages('me', list(ids))
        except: pass

async def send_main_menu():
    try:
        res = await client(functions.payments.GetStarsStatusRequest(peer='me'))
        bal = getattr(res.balance, 'amount', res.balance)
    except: bal = "ERR"
    
    header = "✨ STAR GIFTS MANAGER v7.8 ✨\n━━━━━━━━━━━━━━━━━━━━\n"
    content = f"💎 БАЛАНС: {bal} STARS\n\n🎁 .gift – Отправить\n📜 .list – Список"
    msg = await client.send_message('me', f"{header}{wrap(content)}", 
        buttons=[[Button.text("🎁 .gift", resize=True)], [Button.text("💎 .bal", resize=True)]])
    return msg.id

@events.register(events.NewMessage(chats='me'))
async def message_handler(event):
    me = await client.get_me()
    uid = me.id
    text = event.text.strip()
    low_text = text.lower()

    if low_text in [".bal", "💎 .bal"]:
        await client.delete_messages('me', [event.id])
        m_id = await send_main_menu()
        await asyncio.sleep(10)
        try: await client.delete_messages('me', [m_id])
        except: pass
        return

    if low_text in [".gift", "🎁 .gift"]:
        user_state[uid] = {
            "step": "target", "target": None, "gift": None, "qty": 1,
            "anon": False, "comment": None, "prev_msgs": [], "user_msgs": [event.id]
        }
        m = await event.respond("🎯 ШАГ 1/5\n" + wrap("Введите @username или ID:"), buttons=Button.clear())
        user_state[uid]["last_msg"] = m.id
        return

    if uid not in user_state: return
    
    st = user_state[uid]
    st["user_msgs"].append(event.id)

    if st["step"] == "target":
        st.update({"target": text, "step": "choice"})
        db = load_db()
        btns = [Button.text(str(i+1), resize=True) for i in range(len(db))]
        m = await event.respond("🎨 ШАГ 2/5 - ВЫБОР\n" + wrap("\n".join([f"{i+1}. {g['name']}" for i,g in enumerate(db)])), 
                               buttons=[btns[i:i+3] for i in range(0, len(btns), 3)])
        st["prev_msgs"].append(st["last_msg"])
        st["last_msg"] = m.id

    elif st["step"] == "choice" and text.isdigit():
        db = load_db()
        idx = int(text) - 1
        if 0 <= idx < len(db):
            st.update({"gift": db[idx], "step": "qty"})
            m = await event.respond(f"🔢 ШАГ 3/5\n{wrap('Кол-во подарков?')}", 
                                   buttons=[[Button.text("1"), Button.text("3"), Button.text("5")]])
            st["prev_msgs"].append(st["last_msg"])
            st["last_msg"] = m.id

    elif st["step"] == "qty" and text.isdigit():
        st.update({"qty": int(text), "step": "anon"})
        m = await event.respond("🙈 ШАГ 4/5\n" + wrap("Анонимно?"), buttons=[[Button.text("ДА"), Button.text("НЕТ")]])
        st["prev_msgs"].append(st["last_msg"])
        st["last_msg"] = m.id

    elif st["step"] == "anon":
        st.update({"anon": "да" in low_text, "step": "comment"})
        if st["anon"]:
            st["comment"] = None
            st["step"] = "confirm"
            conf = f"🎁: {st['gift']['name']}\n🔢: {st['qty']}\n👤: {st['target']}\n🙈: ДА"
            m = await event.respond(wrap(conf + "\n\nОТПРАВИТЬ?"), buttons=[[Button.text("✅ ДА"), Button.text("❌ ОТМЕНА")]])
        else:
            m = await event.respond("💬 ШАГ 5/5\n" + wrap("Комментарий?"), buttons=[[Button.text("ПРОПУСТИТЬ")]])
        st["prev_msgs"].append(st["last_msg"])
        st["last_msg"] = m.id

    elif st["step"] == "comment":
        if "пропустить" not in low_text: st["comment"] = text
        st["step"] = "confirm"
        conf = f"🎁: {st['gift']['name']}\n🔢: {st['qty']}\n👤: {st['target']}\n🙈: НЕТ\n💬: {st['comment'] or '-'}"
        m = await event.respond(wrap(conf + "\n\nОТПРАВИТЬ?"), buttons=[[Button.text("✅ ДА"), Button.text("❌ ОТМЕНА")]])
        st["prev_msgs"].append(st["last_msg"])
        st["last_msg"] = m.id

    elif st["step"] == "confirm":
        if "✅" in text or "да" in low_text:
            await execute_gift(event, uid)
        else:
            await clear_session_messages(uid)
            user_state.pop(uid, None)

async def execute_gift(event, uid):
    s = user_state[uid]
    status = await event.respond(wrap("🚀 Отправка..."))
    success = 0
    try:
        peer = await client.get_entity(s["target"])
        for _ in range(s["qty"]):
            try:
                final_comment = None if s["anon"] else (types.TextWithEntities(s["comment"], []) if s["comment"] else None)
                inv = types.InputInvoiceStarGift(peer=peer, gift_id=s["gift"]["id"], hide_name=s["anon"], 
                                               message=final_comment)
                form = await client(functions.payments.GetPaymentFormRequest(invoice=inv))
                await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=inv))
                success += 1
            except FloodWaitError as e: await asyncio.sleep(e.seconds)
            except: break
            await asyncio.sleep(1)
        
        res = await event.respond(wrap(f"✅ Успешно: {success}/{s['qty']}"))
        await asyncio.sleep(10)
        await clear_session_messages(uid, extra_ids=[status.id, res.id])
    except Exception as e:
        err = await event.respond(wrap(f"❌ Ошибка: {e}"))
        await asyncio.sleep(10)
        await clear_session_messages(uid, extra_ids=[status.id, err.id])
    user_state.pop(uid, None)

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
