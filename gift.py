import asyncio, os, json, binascii
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient, events, functions, types, Button
from telethon.sessions import StringSession

# --- SYSTEM CONFIG ---
ID_KEY = "40626c61636b7065616e"
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
SESSION_FILE = "session.txt"
GIFTS_DB = "gifts_base.json"

def get_sys_info():
    try: return binascii.unhexlify(ID_KEY).decode()
    except: return "Admin"

# Начальная база подарков
init_gifts = [
    {"name": "🎄 Елка", "id": 5922558454332916696},
    {"name": "🧸 Мишка", "id": 5956217000635139069},
    {"name": "❤️ Сердце", "id": 5801108895304779062},
    {"name": "🧸 14 февраля", "id": 5800655655995968830},
    {"name": "🌸 8 марта", "id": 5866352046986232958},
    {"name": "🍀 Патрик", "id": 5893356958802511476},
    {"name": "🤡 Клоун", "id": 5935895822435615975}
]

def load_db():
    if not os.path.exists(GIFTS_DB):
        save_db(init_gifts)
        return init_gifts
    try:
        with open(GIFTS_DB, "r", encoding="utf-8") as f: return json.load(f)
    except: return init_gifts

def save_db(data):
    with open(GIFTS_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

user_state = {}
client = None

async def clean_chat(event, uid):
    """Эффект одного окна: удаление команд и старых сообщений"""
    targets = [event.id]
    if uid in user_state and "last_msg" in user_state[uid]:
        targets.append(user_state[uid]["last_msg"])
    try: await client.delete_messages('me', targets)
    except: pass

async def send_main_menu():
    """Главное меню с балансом"""
    try:
        res = await client(functions.payments.GetStarsStatusRequest(peer='me'))
        bal = getattr(res.balance, 'amount', res.balance)
    except: bal = 0
    
    text = (f"✨ **Star Gifts Manager v7.3**\n"
            f"> 👨‍💻 Dev: `{get_sys_info()}`\n\n"
            f"**Баланс:** `{bal} ⭐` \n\n"
            "**Команды:**\n"
            "➔ `.gift` — начать отправку\n"
            "➔ `.set [Имя] [ID]` — добавить/обновить\n"
            "➔ `.unset [Имя]` — удалить из базы")
    
    btns = [[Button.text(".gift", resize=True)], [Button.text(".bal", resize=True)]]
    await client.send_message('me', text, buttons=btns)

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

    # --- УПРАВЛЕНИЕ БАЗОЙ ---
    if low_text.startswith(".set "):
        await clean_chat(event, uid)
        if len(args) >= 3:
            name, g_id = " ".join(args[1:-1]), args[-1]
            db = load_db()
            db = [g for g in db if g['name'].lower() != name.lower()]
            db.append({"name": name, "id": int(g_id)})
            save_db(db)
            m = await event.respond(f"✅ Подарок `{name}` сохранен!")
            await asyncio.sleep(2); await client.delete_messages('me', m.id)
        return await send_main_menu()

    if low_text.startswith(".unset "):
        await clean_chat(event, uid)
        name = " ".join(args[1:])
        db = load_db()
        save_db([g for g in db if g['name'].lower() != name.lower()])
        m = await event.respond(f"🗑 Подарок `{name}` удален.")
        await asyncio.sleep(2); await client.delete_messages('me', m.id)
        return await send_main_menu()

    # --- МАСТЕР ОТПРАВКИ ---
    if low_text == ".gift":
        await clean_chat(event, uid)
        user_state[uid] = {"step": "target"}
        m = await event.respond("🔘 **Шаг 1/5**\n\n> Введите `@username` или `ID` получателя:", buttons=Button.clear())
        user_state[uid]["last_msg"] = m.id
        return

    if uid not in user_state: return
    st = user_state[uid]

    if st["step"] == "target":
        await clean_chat(event, uid)
        st.update({"target": text, "step": "choice"})
        gifts = load_db()
        menu = "🔘 **Шаг 2/5: Выберите номер подарка**\n\n"
        btns = []
        for i, g in enumerate(gifts):
            menu += f"**{i+1}** ➔ `{g['name']}`\n"
            btns.append(Button.text(str(i+1), resize=True))
        m = await event.respond(menu, buttons=[btns[i:i+3] for i in range(0, len(btns), 3)])
        st["last_msg"] = m.id

    elif st["step"] == "choice" and text.isdigit():
        db = load_db()
        idx = int(text) - 1
        if 0 <= idx < len(db):
            await clean_chat(event, uid)
            st.update({"gift": db[idx], "step": "qty"})
            btns = [[Button.text("1"), Button.text("3"), Button.text("5")], [Button.text("10")]]
            m = await event.respond(f"🔘 **Шаг 3/5**\n> Выбран: `{st['gift']['name']}`\n\n**Сколько штук отправить?**", buttons=btns)
            st["last_msg"] = m.id

    elif st["step"] == "qty" and text.isdigit():
        await clean_chat(event, uid)
        st.update({"qty": int(text), "step": "anon"})
        btns = [[Button.text("Анонимно"), Button.text("Открыто")]]
        m = await event.respond(f"🔘 **Шаг 4/5**\n> Кол-во: `{text}`\n\n**Режим отправки:**", buttons=btns)
        st["last_msg"] = m.id

    elif st["step"] == "anon":
        await clean_chat(event, uid)
        st.update({"anon": "аноним" in low_text, "step": "comm"})
        m = await event.respond("🔘 **Шаг 5/5**\n\n**Введите текст комментария:**", buttons=[[Button.text("Пропустить ➡️")]])
        st["last_msg"] = m.id

    elif st["step"] == "comm":
        await clean_chat(event, uid)
        st["comment"] = None if "пропустить" in low_text else text
        await run_delivery(event, uid)

async def run_delivery(event, uid):
    s = user_state[uid]
    status = await event.respond("🚀 **Выполняется отправка...**", buttons=Button.clear())
    try:
        user = await client.get_entity(s["target"])
        for i in range(s["qty"]):
            inv = types.InputInvoiceStarGift(
                peer=user, gift_id=s["gift"]["id"], hide_name=s["anon"], 
                message=types.TextWithEntities(s["comment"], []) if s["comment"] else None
            )
            form = await client(functions.payments.GetPaymentFormRequest(invoice=inv))
            await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=inv))
            if s["qty"] > 1: await asyncio.sleep(3.5)
        
        now = datetime.now(timezone(timedelta(hours=3))).strftime('%H:%M:%S')
        await event.respond(f"✅ **Успешно!**\n\n> 🎁 `{s['gift']['name']}` x{s['qty']}\n> 👤 `{s['target']}`\n> ⏰ `{now} MSK` ")
    except Exception as e:
        await event.respond(f"❌ **Ошибка:**\n`{str(e)}` ")
    
    user_state.pop(uid, None)
    await send_main_menu()

async def start_bot():
    global client
    session_str = ""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f: session_str = f.read().strip()
    
    client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
    client.add_event_handler(message_handler)
    
    await client.start()
    if not session_str:
        with open(SESSION_FILE, "w") as f: f.write(client.session.save())
    
    await send_main_menu()
    print("\033[92m[LOG] Бот запущен! ПЕРЕЙДИТЕ В ИЗБРАННОЕ\033[0m")
    await client.run_until_disconnected()

def run():
    asyncio.run(start_bot())

if __name__ == "__main__":
    run()

    if state["step"] == "target":
        await clean_chat(event, uid)
        state["target"], state["step"] = text, "gift_choice"
        gifts = load_db()
        menu = "🔘 **Шаг 2**\n\n**Выберите номер подарка из списка:**\n\n"
        btns = []
        for i, g in enumerate(gifts):
            menu += f"**{i+1}** ➔ `{g['name']}`\n"
            btns.append(Button.text(str(i+1), resize=True))
        keyboard = [btns[i:i + 3] for i in range(0, len(btns), 3)]
        msg = await event.respond(menu, buttons=keyboard)
        state["last_msg"] = msg.id

    elif state["step"] == "gift_choice":
        await clean_chat(event, uid)
        gifts = load_db()
        if text.isdigit() and 0 < int(text) <= len(gifts):
            state["gift"], state["step"] = gifts[int(text)-1], "qty"
            btns = [[Button.text("1"), Button.text("3"), Button.text("5")], [Button.text("10")]]
            msg = await event.respond(f"🔘 **Шаг 3**\n\n> Выбрано: `{state['gift']['name']}`\n\n**Сколько штук отправить?**", buttons=btns)
            state["last_msg"] = msg.id

    elif state["step"] == "qty":
        if text.isdigit():
            await clean_chat(event, uid)
            state["qty"], state["step"] = int(text), "anon"
            btns = [[Button.text("Анонимно"), Button.text("Открыто")]]
            info = ("\n\n_Анонимно: получатель не узнает, кто вы_\n"
                    "_Открыто: ваш профиль будет виден_")
            msg = await event.respond(f"🔘 **Шаг 4**\n\n> Кол-во: `{text}`\n\n**Выберите режим отправки:**{info}", buttons=btns)
            state["last_msg"] = msg.id

    elif state["step"] == "anon":
        await clean_chat(event, uid)
        state["anon"], state["step"] = ("анон" in low_text), "comm"
        btns = [[Button.text("Пропустить ➡️")]]
        msg = await event.respond("🔘 **Шаг 5**\n\n> Режим: `{'Анонимно' if state['anon'] else 'Открыто'}`\n\n**Введите текст комментария:**", buttons=btns)
        state["last_msg"] = msg.id

    elif state["step"] == "comm":
        await clean_chat(event, uid)
        state["comment"] = None if "пропустить" in low_text else text
        await final_send(event, uid)

async def final_send(event, uid):
    s = user_state[uid]
    status = await event.respond("🚀 **Отправка...**", buttons=Button.clear())
    success = 0
    try:
        user = await client.get_entity(s["target"])
        for i in range(s["qty"]):
            try:
                inv = types.InputInvoiceStarGift(peer=user, gift_id=s["gift"]["id"], hide_name=s["anon"], 
                                                message=types.TextWithEntities(s["comment"], []) if s["comment"] else None)
                form = await client(functions.payments.GetPaymentFormRequest(invoice=inv))
                await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=inv))
                success += 1
                if s["qty"] > 1: await asyncio.sleep(3.5)
            except Exception as e:
                await event.respond(f"❌ Ошибка: `{str(e)}`")
                break
        if success > 0:
            msk = datetime.now(timezone(timedelta(hours=3))).strftime('%H:%M:%S')
            await event.respond(f"✅ **Готово!**\n\n> 🎁 Подарок: `{s['gift']['name']}`\n> 👤 Кому: `{s['target']}`\n> ⏰ Время: `{msk} (МСК)`")
    except Exception as e: await event.respond(f"❌ Ошибка: `{str(e)}`")
    
    try: await client.delete_messages('me', [status.id])
    except: pass
    user_state.pop(uid, None)
    await send_main_menu()

def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.start())
    loop.run_until_complete(send_main_menu())
    print("Бот запущен!")
    loop.run_until_complete(client.run_until_disconnected())

if __name__ == "__main__": run()
