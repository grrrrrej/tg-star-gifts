import asyncio
import os
import json
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient, events, functions, types, Button
from telethon.sessions import StringSession

# --- CONFIG ---
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
    try:
        with open(GIFTS_DB, "r", encoding="utf-8") as f: return json.load(f)
    except: return init_gifts

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
    text = f"💎 **Баланс: {balance} ⭐**\nУправление подарками в меню ниже 👇"
    btns = [
        [Button.text("🎁 Отправить подарок", resize=True)],
        [Button.text("🔄 Обновить баланс", resize=True)]
    ]
    await client.send_message('me', text, buttons=btns)

async def process_sending(event, uid):
    s = user_state[uid]
    await event.respond("🚀 **Отправка запущена...**", buttons=Button.clear())
    try:
        user = await client.get_entity(s["target"])
        msg = types.TextWithEntities(text=s["comment"], entities=[]) if s["comment"] else None
        
        for _ in range(s["qty"]):
            inv = types.InputInvoiceStarGift(peer=user, gift_id=s["gift"]["id"], hide_name=s["anon"], message=msg)
            form = await client(functions.payments.GetPaymentFormRequest(invoice=inv))
            await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=inv))
            if s["qty"] > 1: await asyncio.sleep(4.1)
        
        # Время МСК
        msk = datetime.now(timezone(timedelta(hours=3))).strftime('%d.%m.%Y %H:%M:%S')
        await event.respond(
            f"✅ **Успешно!**\n"
            f"🎁 Подарок: `{s['gift']['name']}`\n"
            f"👤 Кому: `{s['target']}`\n"
            f"⏰ Дата/Время: `{msk} (МСК)`"
        )
    except Exception as e:
        await event.respond(f"❌ **Ошибка:** `{str(e)}` ")
    
    user_state.pop(uid, None)
    await send_main_menu()

@client.on(events.NewMessage(chats='me'))
async def message_handler(event):
    uid = event.sender_id
    text = event.text
    
    # Команды главного меню
    if text == "🎁 Отправить подарок":
        user_state[uid] = {"step": "target"}
        await event.respond("🎯 **Шаг 1:** Пришли ник или ID получателя:", buttons=Button.clear())
        return
    elif text == "🔄 Обновить баланс":
        await send_main_menu()
        return

    if uid not in user_state: return
    state = user_state[uid]

    # Шаг 1: Получили цель
    if state["step"] == "target":
        user_state[uid]["target"] = text
        user_state[uid]["step"] = "gift"
        btns = [[Button.text(g['name'], resize=True)] for g in load_db()]
        await event.respond(f"✅ Кому: `{text}`\n**Шаг 2:** Выбери подарок:", buttons=btns)
    
    # Шаг 2: Получили подарок
    elif state["step"] == "gift":
        gifts = load_db()
        gift = next((g for g in gifts if g['name'] == text), None)
        if gift:
            user_state[uid]["gift"] = gift
            user_state[uid]["step"] = "qty"
            btns = [[Button.text("1", resize=True), Button.text("2", resize=True), Button.text("3", resize=True)],
                    [Button.text("5", resize=True), Button.text("10", resize=True)]]
            await event.respond(f"🎁 Выбрано: **{text}**\n**Шаг 3:** Сколько штук отправить?", buttons=btns)
    
    # Шаг 3: Получили количество
    elif state["step"] == "qty":
        if text.isdigit():
            user_state[uid]["qty"] = int(text)
            user_state[uid]["step"] = "anon"
            btns = [[Button.text("👤 Открыто", resize=True), Button.text("👻 Анонимно", resize=True)]]
            await event.respond(f"🔢 Кол-во: **{text}**\n**Шаг 4:** Выбери тип отправки:", buttons=btns)
    
    # Шаг 4: Анонимность
    elif state["step"] == "anon":
        user_state[uid]["anon"] = (text == "👻 Анонимно")
        if user_state[uid]["anon"]:
            user_state[uid]["comment"] = None
            await process_sending(event, uid)
        else:
            user_state[uid]["step"] = "comm"
            await event.respond("💬 **Шаг 5:** Введи текст комментария (или напиши 'нет'):", buttons=Button.clear())
            
    # Шаг 5: Комментарий
    elif state["step"] == "comm":
        user_state[uid]["comment"] = text if text.lower() != "нет" else None
        await process_sending(event, uid)

async def start_bot():
    if get_author() != "@blackpean": return
    await client.start()
    with open(SESSION_FILE, "w") as f: f.write(client.session.save())
    await send_main_menu()
    print("\033[92mБот успешно запущен!\033[0m")
    print("\033[94mПЕРЕЙДИТЕ В ИЗБРАННОЕ\033[0m")
    await client.run_until_disconnected()

def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())

if __name__ == "__main__":
    run()
