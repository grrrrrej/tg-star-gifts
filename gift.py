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
APP_VERSION = "7.9.6"

MAX_QTY = 100  # защита от случайной отправки огромного количества подарков за раз

YES_WORDS = {"да", "д", "yes", "y", "+", "ok", "ок"}
NO_WORDS = {"нет", "н", "no", "n", "-"}
CANCEL_WORDS = {".cancel", "отмена", "cancel"}


# --- КОНСОЛЬНЫЕ ЦВЕТА ---
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"


def enable_windows_ansi():
    # На Windows 10/11 ANSI-коды в cmd работают только после этого трюка
    if os.name == "nt":
        os.system("")


def log_error(prefix, e):
    # Ошибки теперь видно в консоли, а не только в чате Telegram
    print(f"{C.RED}[ERROR] {prefix}: {e}{C.RESET}")


def get_dev():
    try:
        return binascii.unhexlify(HEX_DEV).decode()
    except Exception:
        return "@unknown"


def wrap(text):
    return f"```\n{text}\n```"


def load_gifts():
    if not os.path.exists(GIFTS_DB_FILE):
        init = [{"name": "🎄 Елка", "id": 5922558454332916696, "price": 50}]
        save_gifts(init)
        return init
    with open(GIFTS_DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        # Проверка на наличие ключа price, чтобы не было ошибки KeyError
        for item in data:
            if "price" not in item:
                item["price"] = 50
        return data


def save_gifts(data):
    with open(GIFTS_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


user_state = {}
client = None
OWN_ID = None  # кэшируем свой ID один раз при старте, а не на каждое сообщение


async def get_menu_text():
    try:
        res = await client(functions.payments.GetStarsStatusRequest(peer='me'))
        bal = getattr(res.balance, 'amount', res.balance)
    except Exception as e:
        log_error("get_menu_text/balance", e)
        bal = "0"
    header = "✨✨✨ STAR GIFTS MANAGER v4.4.0 ✨✨✨\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    content = (
        f"💎 БАЛАНС: {bal} STARS 💎\n\n"
        "📋 КОМАНДЫ:\n"
        "  🎁 .gift   – Отправить подарок\n"
        "  💎 .bal    – Обновить баланс\n"
        "  📜 .set    – Добавить (Имя|ID|Цена)\n"
        "  📋 .list   – Список подарков\n"
        "  ❌ .unset  – Удалить (Номер)\n"
        "  🛑 .cancel – Отменить текущее действие"
    )
    footer = f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👨‍💻 DEV: {get_dev()}"
    return f"{header}{wrap(content)}{footer}"


async def final_cleanup(uid, delay=10):
    await asyncio.sleep(delay)
    if uid in user_state:
        st = user_state[uid]
        ids = st.get("to_delete", [])
        try:
            await client.delete_messages('me', ids)
        except Exception as e:
            log_error("final_cleanup/delete_messages", e)
        user_state.pop(uid, None)
        # Отправляем новую чистую таблицу после завершения
        await client.send_message('me', await get_menu_text())


@events.register(events.NewMessage(chats='me'))
async def handler(event):
    uid = OWN_ID
    text = (event.text or "").strip()
    low = text.lower()

    if low == ".bal":
        await event.delete()
        await client.send_message('me', await get_menu_text())
        return

    if low == ".list":
        await event.delete()
        db = load_gifts()
        if not db:
            await event.respond("📭 База подарков пуста", delete_after=5)
        else:
            list_txt = "\n".join(f"{i+1}. {g['name']} — {g.get('price', 50)}⭐ (id: {g['id']})" for i, g in enumerate(db))
            await event.respond(f"📜 **СПИСОК ПОДАРКОВ**\n{wrap(list_txt)}", delete_after=15)
        return

    if low.startswith(".set "):
        await event.delete()
        parts = [p.strip() for p in text[5:].split("|")]
        if len(parts) != 3:
            await event.respond("❗ Формат: `.set Имя|ID|Цена`", delete_after=6)
            return
        name, gid, price = parts
        if not name:
            await event.respond("❗ Укажите имя подарка", delete_after=6)
            return
        if not gid.isdigit() or not price.isdigit():
            await event.respond("❗ ID и Цена должны быть числами", delete_after=6)
            return
        db = load_gifts()
        db.append({"name": name, "id": int(gid), "price": int(price)})
        save_gifts(db)
        await event.respond(f"✅ Добавлено: `{name}`", delete_after=5)
        return

    if low.startswith(".unset"):
        await event.delete()
        arg = text[6:].strip()
        if not arg.isdigit():
            await event.respond("❗ Формат: `.unset НОМЕР` (см. `.list`)", delete_after=6)
            return
        idx = int(arg) - 1
        db = load_gifts()
        if 0 <= idx < len(db):
            removed = db.pop(idx)
            save_gifts(db)
            await event.respond(f"🗑️ Удалено: `{removed['name']}`", delete_after=5)
        else:
            await event.respond("❗ Нет такого номера. Проверьте `.list`", delete_after=5)
        return

    if low == ".gift":
        menu_id = None
        async for msg in client.iter_messages('me', limit=10):
            if msg.text and "STAR GIFTS MANAGER" in msg.text:
                menu_id = msg.id
                break

        await event.delete()
        m = await event.respond("🎯 **ШАГ 1/5**\n" + wrap("Введите @username или ID получателя:\n(или .cancel для отмены)"))
        user_state[uid] = {"step": "target", "main_msg": m, "to_delete": [m.id]}
        if menu_id:
            user_state[uid]["to_delete"].append(menu_id)
        return

    if uid not in user_state or "step" not in user_state[uid]:
        return

    st = user_state[uid]
    st["to_delete"].append(event.id)
    main_msg = st["main_msg"]
    asyncio.create_task(event.delete())

    if low in CANCEL_WORDS:
        await main_msg.edit("🛑 **Отменено пользователем.**")
        asyncio.create_task(final_cleanup(uid, 3))
        return

    try:
        if st["step"] == "target":
            try:
                entity = await client.get_entity(text)
            except Exception:
                return await main_msg.edit(
                    f"❗ **Получатель не найден!**\n{wrap('Проверьте @username или ID и введите снова.')}"
                )
            st["target"] = text
            st["target_entity"] = entity
            st["step"] = "choice"
            db = load_gifts()
            if not db:
                await main_msg.edit("❗ **База подарков пуста.** Добавьте подарок через `.set`")
                asyncio.create_task(final_cleanup(uid, 5))
                return
            list_txt = "\n".join([f"{i+1}. {g['name']} ({g.get('price', 50)}⭐)" for i, g in enumerate(db)])
            await main_msg.edit(f"🎨 **ШАГ 2/5 - ВЫБОР**\n{wrap(list_txt)}\n**Введите номер:**")

        elif st["step"] == "choice":
            if not text.isdigit():
                return await main_msg.edit(f"❗ **ОШИБКА: Введите число!**\n{wrap('Выберите номер из списка.')}")
            db = load_gifts()
            idx = int(text) - 1
            if 0 <= idx < len(db):
                st["gift"] = db[idx]
                st["step"] = "qty"
                await main_msg.edit(f"🔢 **ШАГ 3/5: КОЛИЧЕСТВО**\n{wrap('Введите число: сколько штук отправить?')}")
            else:
                await main_msg.edit("❗ **Нет такого номера!**")

        elif st["step"] == "qty":
            if not text.isdigit() or int(text) <= 0:
                return await main_msg.edit(f"❗ **ОШИБКА: Введите положительное число!**\n{wrap('Например: 1, 5, 10...')}")
            qty = int(text)
            if qty > MAX_QTY:
                return await main_msg.edit(f"❗ **Слишком много!**\n{wrap(f'Максимум {MAX_QTY} шт. за раз. Введите меньше.')}")
            st["qty"] = qty
            st["step"] = "anon"
            await main_msg.edit(f"🙈 **ШАГ 4/5**\n{wrap('Анонимно? (ДА / НЕТ)')}")

        elif st["step"] == "anon":
            ans = low.strip()
            if ans in YES_WORDS:
                st["anon"] = True
            elif ans in NO_WORDS:
                st["anon"] = False
            else:
                return await main_msg.edit(f"❗ **Ответьте ДА или НЕТ**\n{wrap('Анонимно отправить подарок?')}")
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
            ans = low.strip()
            if ans in YES_WORDS:
                await main_msg.edit("🚀 **Запуск...**")
                await execute_send(main_msg, uid)
            elif ans in NO_WORDS:
                await main_msg.edit("❌ **Отмена.**")
                asyncio.create_task(final_cleanup(uid, 3))
            else:
                await main_msg.edit("❗ **Ответьте ДА или НЕТ**")
    except Exception as e:
        log_error("handler", e)
        await main_msg.edit(f"❌ **Ошибка:** {e}")
        asyncio.create_task(final_cleanup(uid, 5))


async def finish_setup(msg, st):
    price = st["gift"].get("price", 50)
    total = price * st["qty"]
    header = "✨✨✨ STAR GIFTS MANAGER v4.4.0 ✨✨✨\n"
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
        peer = s.get("target_entity") or await client.get_entity(s["target"])
        for i in range(s["qty"]):
            try:
                inv = types.InputInvoiceStarGift(
                    peer=peer, gift_id=s["gift"]["id"], hide_name=s["anon"],
                    message=types.TextWithEntities(s["comment"], []) if s["comment"] else None
                )
                form = await client(functions.payments.GetPaymentFormRequest(invoice=inv))
                await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=inv))
                success += 1
                if i < s["qty"] - 1:
                    await asyncio.sleep(1)
            except RPCError as e:
                m = str(e)
                if "BALANCE_TOO_LOW" in m:
                    err_text = "❌ Не хватает звёзд!"
                elif "USER_PRIVACY_RESTRICTED" in m:
                    err_text = "❌ Приватность получателя закрыта!"
                elif "STARGIFT_USAGE_LIMITED" in m or "GIFT_ID_INVALID" in m:
                    err_text = "❌ Подарок больше недоступен!"
                else:
                    err_text = f"❌ Ошибка: {m}"
                log_error("execute_send/RPCError", e)
                break
    except Exception as e:
        log_error("execute_send/resolve_entity", e)
        err_text = "❌ Не удалось найти получателя"

    total = s["qty"]
    if success == total:
        await main_msg.edit(f"✅ **УСПЕХ!**\nДоставлено: `{success}` из `{total}`")
    elif success > 0:
        await main_msg.edit(f"⚠️ **ЧАСТИЧНО**\nДоставлено: `{success}` из `{total}`\n{err_text}")
    else:
        await main_msg.edit(err_text or "❌ Сбой отправки.")
    asyncio.create_task(final_cleanup(uid, 10))


async def startup_init():
    global OWN_ID
    me = await client.get_me()
    OWN_ID = me.id
    uname = f"@{me.username}" if me.username else "—"
    db = load_gifts()
    print(f"{C.CYAN}👤 Аккаунт:{C.RESET} {me.first_name or ''} ({uname})")
    print(f"{C.CYAN}🎁 Подарков в базе:{C.RESET} {len(db)}")
    await client.send_message('me', await get_menu_text())


def run():
    global client
    enable_windows_ansi()

    if not os.path.exists(SESSION_FILE):
        open(SESSION_FILE, 'w').close()
    with open(SESSION_FILE, 'r') as f:
        ss = f.read().strip()

    client = TelegramClient(StringSession(ss), API_ID, API_HASH,
                             device_model=DEVICE_MODEL, system_version=SYSTEM_VERSION, app_version=APP_VERSION)
    client.add_event_handler(handler)
    client.start()

    # Сохраняем сессию сразу после логина, иначе при первом запуске
    # авторизация не переживёт перезапуск скрипта
    with open(SESSION_FILE, 'w') as f:
        f.write(client.session.save())

    print(f"\n{C.CYAN}{'='*36}{C.RESET}")
    print(f"{C.GREEN}{C.BOLD}🚀 БОТ ЗАПУЩЕН!{C.RESET}")
    print(f"{C.CYAN}{'='*36}{C.RESET}")

    client.loop.run_until_complete(startup_init())

    print(f"{C.YELLOW}👉 Таблица отправлена в Избранное. Ожидание команд...{C.RESET}\n")
    client.run_until_disconnected()


if __name__ == "__main__":
    run()
