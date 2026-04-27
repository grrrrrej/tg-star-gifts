import asyncio, os, json, binascii
from telethon import TelegramClient, events, functions, types
from telethon.sessions import StringSession
from telethon.errors import RPCError

# --- CONFIG ---
HEX_DEV = "40626c61636b7065616e"
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
SESSION_FILE = "session.txt"
GIFTS_DB_FILE = "gifts_base.json"

DEVICE_MODEL = "HP Laptop 15-da0xxx"
SYSTEM_VERSION = "Windows 11 Pro x64"
APP_VERSION = "7.9.5"

def get_dev():
    try: return binascii.unhexlify(HEX_DEV).decode()
    except: return "@unknown"

def wrap(text): return f"```\n{text}\n```"

def load_gifts():
    if not os.path.exists(GIFTS_DB_FILE):
        init = [{"name": "🎄 Елка", "id": 5922558454332916696, "price": 50}]
        save_gifts(init)
        return init
    with open(GIFTS_DB_FILE, "r", encoding="utf-8") as f: return json.load(f)

def save_gifts(data):
    with open(GIFTS_DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

user_state = {}
client = None

async def get_menu_text():
    try:
        res = await client(functions.payments.GetStarsStatusRequest(peer='me'))
        bal = getattr(res.balance, 'amount', res.balance)
    except: bal = "0"
    header = "✨✨✨ STAR GIFTS MANAGER v4.3.0 ✨✨✨\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    content = f"💎 БАЛАНС: {bal} STARS 💎\n\n📋 КОМАНДЫ:\n  🎁 .gift  – Отправить подарок\n  💎 .bal   – Обновить баланс\n  📜 .set   – Добавить (Имя|ID|Цена)\n  ❌ .unset – Удалить (Номер)"
    footer = f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👨‍💻 DEV: {get_dev()}"
    return f"{header}{wrap(content)}{footer}"

async def final_cleanup(uid, delay=10):
    await asyncio.sleep(delay)
    if uid in user_state:
        st = user_state[uid]
        ids = st.get("to_delete", [])
        # Удаляем и сообщение с процессом, и саму таблицу меню, и ответы юзера
        try: await client.delete_messages('me', ids)
        except: pass
        user_state.pop(uid, None)

@events.register(events.NewMessage(chats='me'))
async def handler(event):
    me = await client.get_me()
    uid, text = me.id, event.text.strip()
    low = text.lower()

    if low == ".bal":
        await event.delete()
        m = await event.respond(await get_menu_text())
        # Запоминаем ID новой таблицы, чтобы удалить её позже если нужно
        if uid not in user_state: user_state[uid] = {"to_delete": []}
        user_state[uid]["to_delete"].append(m.id)
        return

    if low.startswith(".set "):
        await event.delete()
        try:
            p = text[5:].split("|")
            db = load_gifts()
            db.append({"name": p[0].strip(), "id": int(p[1].strip()), "price": int(p[2].strip())})
            save_gifts(db)
            await event.respond(f"✅ Добавлено: `{p[0].strip()}`")
        except: await event.respond("❗ Ошибка формата")
        return

    if low == ".gift":
        # Находим последнее сообщение с таблицей (меню) перед запуском
        msgs = await client.get_messages('me', limit=5)
        menu_id = None
        for msg in msgs:
            if "STAR GIFTS MANAGER" in (msg.text or ""):
                menu_id = msg.id
                break
        
        await event.delete()
        m = await event.respond("🎯 **ШАГ 1/5**\n" + wrap("Введите @username или ID получателя:"))
        
        user_state[uid] = {
            "step": "target", 
            "main_msg": m, 
            "to_delete": [m.id]
        }
        if menu_id: user_state[uid]["to_delete"].append(menu_id)
        return

    if uid not in user_state or "step" not in user_state[uid]: return
    st = user_state[uid]
    st["to_delete"].append(event.id)
    main_msg = st["main_msg"]
    asyncio.create_task(event.delete())

    try:
        if st["step"] == "target":
            st["target"] = text
            st["step"] = "choice"
            db = load_gifts()
            list_txt = "\n".join([f"{i+1}. {g['name']} ({g['price']}⭐)" for i, g in enumerate(db)])
            await main_msg.edit(f"🎨 **ШАГ 2/5 - ВЫБОР**\n{wrap(list_txt)}\n**Введите номер:**")

        elif st["step"] == "choice":
            if not text.isdigit():
                return await main_msg.edit(f"❗ **ОШИБКА: Введите число!**\n{wrap('Выберите номер из списка.')}")
            db = load_gifts()
            idx = int(text) - 1
            if 0 <= idx < len(db):
                st["gift"] = db[idx]
                st["step"] = "qty"
                await main_msg.edit(f"🔢 **ШАГ 3/5**\n{wrap('Введите число: сколько штук отправить?')}")
            else: await main_msg.edit(f"❗ **Нет такого номера!**")

        elif st["step"] == "qty":
            if not text.isdigit():
                return await main_msg.edit(f"❗ **ОШИБКА: Введите ЧИСЛО!**\n{wrap('Введите количество цифрами.')}")
            st["qty"] = int(text)
            st["step"] = "anon"
            await main_msg.edit(f"🙈 **ШАГ 4/5**\n{wrap('Анонимно? (ДА / НЕТ)')}")

        elif st["step"] == "anon":
            st["anon"] = "да" in low
            if st["anon"]:
                st["comment"] = None
                await finish_setup(main_msg, st)
            else:
                st["step"] = "comment"
                await main_msg.edit(f"💬 **ШАГ 5/5**\n{wrap('Введите комментарий или точку (.)')}")

        elif st["step"] == "comment":
            st["comment"] = None if text == "." else text
            await finish_setup(main_msg, st)

        elif st["step"] == "confirm":
            if "да" in low:
                await main_msg.edit("🚀 **Запуск...**")
                await execute_send(main_msg, uid)
            else:
                await main_msg.edit("❌ **Отмена.**")
                asyncio.create_task(final_cleanup(uid, 3))

    except Exception as e:
        await main_msg.edit(f"❌ **Ошибка:** {e}")
        asyncio.create_task(final_cleanup(uid, 5))

async def finish_setup(msg, st):
    total = st["gift"]["price"] * st["qty"]
    header = "✨✨✨ STAR GIFTS MANAGER v4.3.0 ✨✨✨\n"
    res = (f"📋 ИТОГ:\n🎁 {st['gift']['name']}\n👤 {st['target']}\n"
           f"🔢 {st['qty']} шт.\n🙈 Анон: {'ДА' if st['anon'] else 'НЕТ'}\n"
           f"💬 Текст: {st['comment'] or '-'}\n💰 СУММА: {total} ⭐")
    await msg.edit(f"{header}{wrap(res)}\n**ОТПРАВИТЬ? (ДА / НЕТ)**")
    st["step"] = "confirm"

async def execute_send(main_msg, uid):
    s = user_state[uid]
    success = 0
    err_text = ""
    try:
        peer = await client.get_entity(s["target"])
        for _ in range(s["qty"]):
            try:
                inv = types.InputInvoiceStarGift(peer=peer, gift_id=s["gift"]["id"], hide_name=s["anon"], 
                                                message=types.TextWithEntities(s["comment"], []) if s["comment"] else None)
                form = await client(functions.payments.GetPaymentFormRequest(invoice=inv))
                await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=inv))
                success += 1
                await asyncio.sleep(1)
            except RPCError as e:
                m = str(e)
                if "BALANCE_TOO_LOW" in m: err_text = "❌ Не хватает звёзд!"
                elif "USER_PRIVACY_RESTRICTED" in m: err_text = "❌ Приватность закрыта!"
                else: err_text = f"❌ Ошибка: {m}"
                raise Exception()
        await main_msg.edit(f"✅ **УСПЕХ!**\nДоставлено: `{success}`")
    except Exception:
        await main_msg.edit(err_text or "❌ Сбой.")
    asyncio.create_task(final_cleanup(uid, 10))

def run():
    global client
    if not os.path.exists(SESSION_FILE): open(SESSION_FILE, 'w').close()
    with open(SESSION_FILE, 'r') as f: ss = f.read().strip()
    client = TelegramClient(StringSession(ss), API_ID, API_HASH, device_model=DEVICE_MODEL, system_version=SYSTEM_VERSION, app_version=APP_VERSION)
    client.add_event_handler(handler)
    client.start()
    print("🚀 Бот запущен!")
    client.loop.run_until_complete(client.send_message('me', "✨ Скрипт готов. Введите `.bal` для меню."))
    client.run_until_disconnected()

if __name__ == "__main__":
    run()
