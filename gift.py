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
    gifts = load_db()
    text = (f"🎁 **Star Gifts Bot v4.0**\n💎 Баланс: **{balance} ⭐**\n\nВыберите подарок:")
    buttons = []
    row = []
    for i, g in enumerate(gifts):
        row.append(Button.inline(g['name'], data=f"gift_{i}"))
        if len(row) == 2:
            buttons.append(row); row = []
    if row: buttons.append(row)
    buttons.append([Button.inline("🔄 Обновить", data="refresh")])
    await client.send_message('me', text, buttons=buttons)

@client.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode()
    if data == "refresh":
        await event.delete()
        await send_main_menu()
    elif data.startswith("gift_"):
        idx = int(data.split("_")[1])
        gift = load_db()[idx]
        user_state[event.sender_id] = {"gift": gift, "step": "recipient"}
        await event.edit(f"🎯 Подарок: **{gift['name']}**\n\nПришли ник получателя:")

@client.on(events.NewMessage(chats='me'))
async def message_handler(event):
    state = user_state.get(event.sender_id)
    if not state: return
    if state['step'] == "recipient":
        state['recipient'] = event.text
        state['step'] = "comment"
        await event.respond(f"✅ Кому: `{event.text}`\n\nНапиши текст подарка (или 'нет'):")
    elif state['step'] == "comment":
        comment = event.text if event.text.lower() != 'нет' else None
        gift, recipient = state['gift'], state['recipient']
        await event.respond("🚀 Отправляю...")
        try:
            user = await client.get_entity(recipient)
            msg = types.TextWithEntities(text=comment, entities=[]) if comment else None
            inv = types.InputInvoiceStarGift(peer=user, gift_id=gift['id'], hide_name=False, message=msg)
            form = await client(functions.payments.GetPaymentFormRequest(invoice=inv))
            await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=inv))
            await event.respond(f"✅ Готово! {gift['name']} улетел к {recipient}")
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
