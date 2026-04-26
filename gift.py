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
    {"name": "🧸 Медведь", "id": 5956217000635139069},
    {"name": "❤️ Сердце", "id": 5801108895304779062},
    {"name": "🌸 Цветы", "id": 5866352046986232958},
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

async def clean_chat(event, uid):
    if uid in user_state and "last_msg" in user_state[uid]:
        try:
            await client.delete_messages('me', [user_state[uid]["last_msg"], event.id])
        except: pass

async def send_main_menu():
    balance = await get_balance()
    text = (f"✨ **Star Gifts Manager v5.6**\n\n"
            f"> 💎 Баланс: `{balance} ⭐` \n\n"
            "Напиши `.gift` для старта или используй кнопки:")
    btns = [[Button.text(".gift", resize=True)], [Button.text(".bal", resize=True)]]
    msg = await client.send_message('me', text, buttons=btns)
    return msg.id

@client.on(events.NewMessage(chats='me'))
async def message_handler(event):
    me = await client.get_me()
    uid = me.id
    text = event.text.strip()
    low_text = text.lower()

    if low_text == ".gift":
        await clean_chat(event, uid)
        user_state[uid] = {"step": "target"}
        msg = await event.respond("🎯 **Шаг 1: Кому?**\n\nВведите `@username` или `ID` получателя:", buttons=Button.clear())
        user_state[uid]["last_msg"] = msg.id
        return
    
    elif low_text == ".bal":
        await clean_chat(event, uid)
        mid = await send_main_menu()
        user_state[uid] = {"last_msg": mid}
        return

    if uid not in user_state or "step" not in user_state[uid]: return
    state = user_state[uid]

    if state["step"] == "target":
        await clean_chat(event, uid)
        state["target"] = text
        state["step"] = "gift_choice"
        gifts = load_db()
        menu = "🎁 **Шаг 2: Выберите подарок**\n\n"
        btns = []
        for i, g in enumerate(gifts):
            menu += f"**{i+1}** ➔ `{g['name']}`\n"
            btns.append(Button.text(str(i+1), resize=True))
        menu += "\n> Или просто введите **ID** подарка"
        keyboard = [btns[i:i + 3] for i in range(0, len(btns), 3)]
        msg = await event.respond(menu, buttons=keyboard)
        state["last_msg"] = msg.id

    elif state["step"] == "gift_choice":
        await clean_chat(event, uid)
        gifts = load_db()
        if text.isdigit() and 0 < int(text) <= len(gifts):
            state["gift"] = gifts[int(text)-1]
        elif text.isdigit() and len(text) > 10:
            state["gift"] = {"name": "Custom ID", "id": int(text)}
        else:
            msg = await event.respond("❌ Неверный ввод. Выбери номер или введи ID:")
            state["last_msg"] = msg.id
            return
            
        state["step"] = "qty"
        btns = [[Button.text("1"), Button.text("3"), Button.text("5")], [Button.text("10")]]
        msg = await event.respond(f"📦 Подарок: `{state['gift']['name']}`\n\n**Шаг 3: Сколько штук?**", buttons=btns)
        state["last_msg"] = msg.id

    elif state["step"] == "qty":
        if text.isdigit():
            await clean_chat(event, uid)
            state["qty"] = int(text)
            state["step"] = "anon"
            btns = [[Button.text("Анонимно"), Button.text("Открыто")]]
            msg = await event.respond(f"🔢 Кол-во: `{text}`\n\n**Шаг 4: Режим отправки?**", buttons=btns)
            state["last_msg"] = msg.id

    elif state["step"] == "anon":
        await clean_chat(event, uid)
        state["anon"] = ("анон" in low_text)
        state["step"] = "comm"
        btns = [[Button.text("Пропустить ➡️")]]
        msg = await event.respond("💬 **Шаг 5: Комментарий**\n\nНапиши текст или нажми кнопку:", buttons=btns)
        state["last_msg"] = msg.id

    elif state["step"] == "comm":
        await clean_chat(event, uid)
        state["comment"] = None if "пропустить" in low_text or low_text == "нет" else text
        await final_send(event, uid)

async def final_send(event, uid):
    s = user_state[uid]
    status_msg = await event.respond("🚀 **Процесс отправки запущен...**", buttons=Button.clear())
    success = 0
    try:
        user = await client.get_entity(s["target"])
        msg_obj = types.TextWithEntities(text=s["comment"], entities=[]) if s["comment"] else None
        
        for i in range(s["qty"]):
            try:
                inv = types.InputInvoiceStarGift(peer=user, gift_id=s["gift"]["id"], hide_name=s["anon"], message=msg_obj)
                form = await client(functions.payments.GetPaymentFormRequest(invoice=inv))
                await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=inv))
                success += 1
                if s["qty"] > 1: await asyncio.sleep(3.5)
            except Exception as e:
                err = str(e).upper()
                if "BALANCE" in err or "STARS_INSUFFICIENT" in err:
                    await event.respond("❌ **Ошибка:** Недостаточно звёзд на балансе!")
                else:
                    await event.respond(f"❌ **Ошибка:** `{str(e)}`")
                break
        
        if success > 0:
            msk = datetime.now(timezone(timedelta(hours=3))).strftime('%H:%M:%S')
            await event.respond(
                f"✅ **Успешно отправлено!**\n\n"
                f"> 🎁 Подарок: `{s['gift']['name']}`\n"
                f"> 👤 Кому: `{s['target']}` \n"
                f"> 🔢 Кол-во: `{success}`\n"
                f"> ⏰ Время: `{msk} (МСК)`"
            )
    except Exception as e:
        await event.respond(f"❌ **Ошибка получателя:** `{str(e)}`")
    
    try: await client.delete_messages('me', [status_msg.id])
    except: pass
    user_state.pop(uid, None)
    await send_main_menu()

async def start_bot():
    await client.start()
    me = await client.get_me()
    with open(SESSION_FILE, "w") as f: f.write(client.session.save())
    mid = await send_main_menu()
    user_state[me.id] = {"last_msg": mid}
    print("\033[94mБот запущен! Иди в Избранное.\033[0m")
    await client.run_until_disconnected()

def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())

if __name__ == "__main__":
    run()
        gifts = load_db()
        if text.isdigit() and 0 < int(text) <= len(gifts):
            state["gift"] = gifts[int(text)-1]
        elif text.isdigit() and len(text) > 10: # Похоже на кастомный ID
            state["gift"] = {"name": "Кастомный ID", "id": int(text)}
        else:
            msg = await event.respond("❌ Ошибка. Выберите номер из списка или введите длинный ID:")
            state["last_msg"] = msg.id
            return
            
        state["step"] = "qty"
        btns = [[Button.text("1"), Button.text("3"), Button.text("5")], [Button.text("10")]]
        msg = await event.respond(f"📦 Выбрано: `{state['gift']['name']}`\n\n**Шаг 3: Сколько штук?**", buttons=btns)
        state["last_msg"] = msg.id

    # --- ШАГ 3: КОЛИЧЕСТВО ---
    elif state["step"] == "qty":
        if text.isdigit():
            await clean_chat(event, uid)
            state["qty"] = int(text)
            state["step"] = "anon"
            btns = [[Button.text("Анонимно"), Button.text("Открыто")]]
            msg = await event.respond(f"🔢 Количество: `{text}`\n\n**Шаг 4: Режим отправки?**", buttons=btns)
            state["last_msg"] = msg.id

    # --- ШАГ 4: АНОНИМНОСТЬ ---
    elif state["step"] == "anon":
        await clean_chat(event, uid)
        state["anon"] = ("анон" in low_text)
        state["step"] = "comm"
        btns = [[Button.text("Пропустить ➡️")]]
        msg = await event.respond("💬 **Шаг 5: Комментарий**\n\nВведите текст или нажмите кнопку:", buttons=btns)
        state["last_msg"] = msg.id

    # --- ШАГ 5: КОММЕНТАРИЙ ---
    elif state["step"] == "comm":
        await clean_chat(event, uid)
        state["comment"] = None if "пропустить" in low_text or low_text == "нет" else text
        await final_send(event, uid)

async def final_send(event, uid):
    s = user_state[uid]
    status_msg = await event.respond("🚀 **Процесс отправки запущен...**", buttons=Button.clear())
    success_count = 0
    try:
        user = await client.get_entity(s["target"])
        msg_obj = types.TextWithEntities(text=s["comment"], entities=[]) if s["comment"] else None
        
        for i in range(s["qty"]):
            try:
                inv = types.InputInvoiceStarGift(peer=user, gift_id=s["gift"]["id"], hide_name=s["anon"], message=msg_obj)
                form = await client(functions.payments.GetPaymentFormRequest(invoice=inv))
                await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=inv))
                success_count += 1
                if s["qty"] > 1: await asyncio.sleep(3.5)
            except Exception as e:
                if "BALANCE_TOO_LOW" in str(e) or "BALANCE_NOT_ENOUGH" in str(e):
                    await event.respond("❌ **Ошибка:** Недостаточно звёзд на балансе!")
                else:
                    await event.respond(f"❌ **Ошибка на {i+1}-м подарке:** `{str(e)}`")
                break
        
        if success_count > 0:
            msk = datetime.now(timezone(timedelta(hours=3))).strftime('%H:%M:%S')
            await event.respond(
                f"✅ **Успешно отправлено!**\n\n"
                f"> 🎁 Подарок: `{s['gift']['name']}`\n"
                f"> 👤 Кому: `{s['target']}` \n"
                f"> 🔢 Кол-во: `{success_count}`\n"
                f"> ⏰ Время: `{msk} (МСК)`"
            )
    except Exception as e:
        await event.respond(f"❌ **Глобальная ошибка:** `{str(e)}` \n(Проверьте ник/ID получателя)")
    
    await client.delete_messages('me', [status_msg.id])
    user_state.pop(uid, None)
    await send_main_menu()

async def start_bot():
    await client.start()
    with open(SESSION_FILE, "w") as f: f.write(client.session.save())
    mid = await send_main_menu()
    user_state[client.uid] = {"last_msg": mid}
    print("\033[94mБот v5.5 запущен! ПЕРЕЙДИТЕ В ИЗБРАННОЕ\033[0m")
    await client.run_until_disconnected()

def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())

if __name__ == "__main__":
    run()
