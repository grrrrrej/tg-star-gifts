import asyncio
import os
import json
import sys
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient, events, functions, types, Button
from telethon.sessions import StringSession

# --- CONFIG ---
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
SESSION_FILE = "session.txt"
GIFTS_DB = "gifts_base.json"
ID_KEY = "40626c61636b7065616e"

init_gifts = [
    {"name": "🎄 Елка", "id": 5922558454332916696},
    {"name": "🎄 Медведь", "id": 5956217000635139069},
    {"name": "❤️ Сердце", "id": 5801108895304779062},
    {"name": "🧸 Подарок", "id": 5800655655995968830},
    {"name": "🌸 Цветы", "id": 5866352046986232958},
    {"name": "🍀 Клевер", "id": 5893356958802511476},
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
    text = (f"💎 **Баланс: {balance} ⭐**\n\n"
            "🔹 Напиши **.gift**, чтобы отправить подарок\n"
            "🔹 Напиши **.bal**, чтобы обновить баланс\n\n"
            "Если кнопки ниже не видны, используй команды текстом!")
    btns = [[Button.text(".gift", resize=True)], [Button.text(".bal", resize=True)]]
    await client.send_message('me', text, buttons=btns)

@client.on(events.NewMessage(chats='me'))
async def message_handler(event):
    uid = event.sender_id
    text = event.text.strip()

    if text.lower() == ".gift":
        user_state[uid] = {"step": "target"}
        await event.respond("🎯 **Шаг 1:** Введи ник получателя (@username или ID):", buttons=Button.clear())
        return
    elif text.lower() == ".bal":
        await send_main_menu()
        return

    if uid not in user_state: return
    state = user_state[uid]

    if state["step"] == "target":
        state["target"] = text
        state["step"] = "gift_choice"
        gifts = load_db()
        menu = "🎁 **Шаг 2: Выбери номер подарка:**\n\n"
        btns = []
        for i, g in enumerate(gifts):
            menu += f"**{i+1}** - {g['name']}\n"
            btns.append(Button.text(str(i+1), resize=True))
        keyboard = [btns[i:i + 3] for i in range(0, len(btns), 3)]
        await event.respond(menu, buttons=keyboard)

    elif state["step"] == "gift_choice":
        gifts = load_db()
        if text.isdigit() and 0 < int(text) <= len(gifts):
            state["gift"] = gifts[int(text)-1]
            state["step"] = "qty"
            btns = [[Button.text("1"), Button.text("3"), Button.text("5")], [Button.text("10")]]
            await event.respond(f"✅ Выбрано: **{state['gift']['name']}**\n**Шаг 3:** Сколько штук отправить?", buttons=btns)

    elif state["step"] == "qty":
        if text.isdigit():
            state["qty"] = int(text)
            state["step"] = "anon"
            btns = [[Button.text("Да"), Button.text("Нет")]]
            await event.respond(f"🔢 Количество: **{text}**\n**Шаг 4:** Анонимно? (Да/Нет)", buttons=btns)

    elif state["step"] == "anon":
        state["anon"] = (text.lower() == "да")
        if state["anon"]:
            state["comment"] = None
            await final_send(event, uid)
        else:
            state["step"] = "comm"
            await event.respond("💬 **Шаг 5:** Текст комментария (или 'нет'):", buttons=Button.clear())

    elif state["step"] == "comm":
        state["comment"] = text if text.lower() != "нет" else None
        await final_send(event, uid)

async def final_send(event, uid):
    s = user_state[uid]
    await event.respond("🚀 **Запускаю...**", buttons=Button.clear())
    try:
        user = await client.get_entity(s["target"])
        msg = types.TextWithEntities(text=s["comment"], entities=[]) if s["comment"] else None
        for _ in range(s["qty"]):
            inv = types.InputInvoiceStarGift(peer=user, gift_id=s["gift"]["id"], hide_name=s["anon"], message=msg)
            form = await client(functions.payments.GetPaymentFormRequest(invoice=inv))
            await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=inv))
            if s["qty"] > 1: await asyncio.sleep(4)
        
        msk = datetime.now(timezone(timedelta(hours=3))).strftime('%d.%m.%Y %H:%M:%S')
        await event.respond(f"✅ **Успешно!**\n🎁: `{s['gift']['name']}`\n👤: `{s['target']}`\n⏰: `{msk} (МСК)`")
    except Exception as e:
        await event.respond(f"❌ Ошибка: `{str(e)}` ")
    user_state.pop(uid, None)
    await send_main_menu()

async def start_bot():
    await client.start()
    with open(SESSION_FILE, "w") as f: f.write(client.session.save())
    await send_main_menu()
    print("\033[92mБот запущен!\033[0m")
    print("\033[94mПЕРЕЙДИТЕ В ИЗБРАННОЕ\033[0m")
    await client.run_until_disconnected()

# Функция run для pip/usr/bin/tg-gifts
def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())

if __name__ == "__main__":
    run()
