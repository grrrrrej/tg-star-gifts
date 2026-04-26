import asyncio
import os
import json
from telethon import TelegramClient, events, functions, types, Button
from telethon.sessions import StringSession

# --- КОНФИГУРАЦИЯ ---
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
SESSION_FILE = "session.txt"
GIFTS_DB = "gifts_base.json"
ID_KEY = "40626c61636b7065616e"

def get_author():
    try: return bytes.fromhex(ID_KEY).decode()
    except: return ""

init_gifts = [
    {"name": "🎄 Елка", "id": 5922558454332916696},
    {"name": "🎄 Новогодний мишка", "id": 5956217000635139069},
    {"name": "❤️ Сердце", "id": 5801108895304779062},
    {"name": "🧸 14 февраля", "id": 5800655655995968830},
    {"name": "🌸 8 марта", "id": 5866352046986232958},
    {"name": "🍀 Патрик", "id": 5893356958802511476},
    {"name": "🤡 Клоун", "id": 5935895822435615975}
]

def load_db():
    if not os.path.exists(GIFTS_DB):
        with open(GIFTS_DB, "w", encoding="utf-8") as f:
            json.dump(init_gifts, f, ensure_ascii=False, indent=4)
        return init_gifts
    with open(GIFTS_DB, "r", encoding="utf-8") as f: return json.load(f)

# Глобальное состояние сессии
user_state = {}
session_str = ""
if os.path.exists(SESSION_FILE):
    with open(SESSION_FILE, "r") as f: session_str = f.read().strip()

client = TelegramClient(StringSession(session_str), API_ID, API_HASH)

async def get_balance():
    try:
        res = await client(functions.payments.GetStarsStatusRequest(peer='me'))
        return res.balance.amount if hasattr(res.balance, 'amount') else res.balance
    except: return 0

async def send_main_menu():
    balance = await get_balance()
    text = (f"👋 Привет! Это твой Star Gifts менеджер.\n"
            f"💎 Твой баланс: **{balance} ⭐**\n\n"
            "Нажми кнопку ниже, чтобы начать.")
    buttons = [[Button.inline("🎁 Отправить подарок", data="start_send")],
               [Button.inline("🔄 Обновить баланс", data="refresh")]]
    await client.send_message('me', text, buttons=buttons)

@client.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode()
    uid = event.sender_id

    if data == "refresh":
        await event.delete()
        await send_main_menu()

    elif data == "start_send":
        user_state[uid] = {"step": "target"}
        await event.edit("🎯 **Шаг 1: Кому?**\n\nПришли Username (с @) или ID получателя:")

    elif data.startswith("g_"): # Выбор подарка
        idx = int(data.split("_")[1])
        user_state[uid]["gift"] = load_db()[idx]
        user_state[uid]["step"] = "qty"
        btns = [[Button.inline("1", data="q_1"), Button.inline("2", data="q_2"), Button.inline("3", data="q_3")],
                [Button.inline("5", data="q_5"), Button.inline("10", data="q_10")]]
        await event.edit(f"📦 Подарок: **{user_state[uid]['gift']['name']}**\n\n**Шаг 3: Сколько штук?**", buttons=btns)

    elif data.startswith("q_"): # Выбор количества
        user_state[uid]["qty"] = int(data.split("_")[1])
        user_state[uid]["step"] = "anon"
        btns = [[Button.inline("👤 Открыто", data="a_no"), Button.inline("👻 Анонимно", data="a_yes")]]
        await event.edit(f"🔢 Количество: **{user_state[uid]['qty']}**\n\n**Шаг 4: Как отправить?**", buttons=btns)

    elif data.startswith("a_"): # Анонимность
        is_anon = data == "a_yes"
        user_state[uid]["anon"] = is_anon
        if is_anon:
            user_state[uid]["comment"] = None
            await process_sending(event, uid)
        else:
            user_state[uid]["step"] = "wait_comm"
            await event.edit("💬 **Шаг 5: Сообщение**\n\nВведи текст комментария (или напиши 'нет'):")

async def process_sending(event, uid):
    state = user_state[uid]
    gift = state["gift"]
    target = state["target"]
    qty = state["qty"]
    comment = state["comment"]
    anon = state["anon"]

    await event.respond(f"⏳ Начинаю отправку `{gift['name']}` для `{target}`...")
    
    success = 0
    try:
        user = await client.get_entity(target)
        msg = types.TextWithEntities(text=comment, entities=[]) if comment else None
        
        for i in range(qty):
            inv = types.InputInvoiceStarGift(peer=user, gift_id=gift['id'], hide_name=anon, message=msg)
            form = await client(functions.payments.GetPaymentFormRequest(invoice=inv))
            await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=inv))
            success += 1
            if qty > 1: await asyncio.sleep(4.1)
            
        await event.respond(f"✅ **Готово!**\nОтправлено: {success}/{qty}\nКому: {target}")
    except Exception as e:
        await event.respond(f"❌ **Ошибка:** `{str(e)}` ")
    
    user_state.pop(uid, None)
    await send_main_menu()

@client.on(events.NewMessage(chats='me'))
async def message_handler(event):
    uid = event.sender_id
    if uid not in user_state: return

    state = user_state[uid]
    
    if state["step"] == "target":
        user_state[uid]["target"] = event.text
        user_state[uid]["step"] = "select_gift"
        gifts = load_db()
        buttons = []
        row = []
        for i, g in enumerate(gifts):
            row.append(Button.inline(g['name'], data=f"g_{i}"))
            if len(row) == 2:
                buttons.append(row); row = []
        if row: buttons.append(row)
        await event.respond(f"✅ Получатель: `{event.text}`\n\n**Шаг 2: Выбери подарок:**", buttons=buttons)

    elif state["step"] == "wait_comm":
        user_state[uid]["comment"] = event.text if event.text.lower() != "нет" else None
        await process_sending(event, uid)

async def run():
    if get_author() != "@blackpean": return
    await client.start()
    with open(SESSION_FILE, "w") as f: f.write(client.session.save())
    await send_main_menu()
    await client.run_until_disconnected()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
        except Exception as e:
            await event.respond(f"❌ Ошибка: `{str(e)}` ")
        del user_state[event.sender_id]
        await send_main_menu()

async def run():
    if get_author() != "@blackpean": return
    await client.start()
    with open(SESSION_FILE, "w") as f: f.write(client.session.save())
    await send_main_menu()
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(run())
