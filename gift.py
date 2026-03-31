import asyncio
import sys
import os
import json
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession
from rich.console import Console

console = Console()

# --- КОНФИГУРАЦИЯ ---
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
SESSION_FILE = "session.txt"
CUSTOM_GIFTS_FILE = "custom_gifts.txt"
GIFT_PRICE = 50

# Имитация ПК
DEVICE = "HP Laptop 15-da0xxx"
SYS_VER = "Windows 11 x64"
APP_VER = "6.5.1 x64"

# Идентификатор автора
ID_KEY = "40626c61636b7065616e" 

def get_author():
    return bytes.fromhex(ID_KEY).decode()

default_gifts = {
    "1": {"name": "🎄 Новогодний Мишка", "id": 5956217000635139069},
    "2": {"name": "🎄 Новогодняя Елка", "id": 5922558454332916696},
    "3": {"name": "❤️ Валентинка (Сердце)", "id": 5801108895304779062},
    "4": {"name": "🧸 Мишка 14 февраля", "id": 5800655655995968830},
    "5": {"name": "🌸 Мишка 8 марта", "id": 5866352046986232958},
    "6": {"name": "🍀 Мишка Патрик", "id": 5893356958802511476}
}

def load_custom_gifts():
    gifts = default_gifts.copy()
    if os.path.exists(CUSTOM_GIFTS_FILE):
        try:
            with open(CUSTOM_GIFTS_FILE, "r", encoding="utf-8") as f:
                gifts.update(json.load(f))
        except: pass
    return gifts

def save_custom_gift(gift_id, name):
    current_custom = {}
    if os.path.exists(CUSTOM_GIFTS_FILE):
        try:
            with open(CUSTOM_GIFTS_FILE, "r", encoding="utf-8") as f:
                current_custom = json.load(f)
        except: pass
    idx = str(len(default_gifts) + len(current_custom) + 1)
    current_custom[idx] = {"name": name, "id": int(gift_id)}
    with open(CUSTOM_GIFTS_FILE, "w", encoding="utf-8") as f:
        json.dump(current_custom, f, ensure_ascii=False, indent=4)
    return idx

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

async def get_balance(client):
    try:
        res = await client(functions.payments.GetStarsStatusRequest(peer=types.InputPeerSelf()))
        return res.balance.amount if hasattr(res.balance, 'amount') else res.balance
    except: return 0

async def main():
    if get_author() != "@blackpean":
        clear()
        console.print("[bold red]❌ ОШИБКА ЛИЦЕНЗИИ[/bold red]")
        return

    clear()
    console.print("[bold magenta]Вход в систему...[/bold magenta]")
    
    session_str = ""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            session_str = f.read().strip()

    client = TelegramClient(
        StringSession(session_str), API_ID, API_HASH,
        device_model=DEVICE, system_version=SYS_VER, app_version=APP_VER
    )
    
    await client.connect()
    if not await client.is_user_authorized():
        await client.start()
        with open(SESSION_FILE, "w") as f: f.write(client.session.save())

    while True:
        clear()
        me = await client.get_me()
        balance = await get_balance(client)
        
        console.print(f"[bold cyan]╭──────────────── АККАУНТ ────────────────╮[/bold cyan]")
        console.print(f"[bold cyan]│[/bold cyan] 👤 Имя: [bold]{me.first_name}[/bold]")
        console.print(f"[bold cyan]│[/bold cyan] 💎 Баланс: [bold yellow]{balance} ⭐[/bold yellow]")
        console.print(f"[bold cyan]╰──────────────────────────────────────────╯[/bold cyan]")
        console.print("[dim]Нажми Enter (пустое поле) для выхода в терминал[/dim]\n")

        # ВЫХОД ТУТ: Если нажал Enter без текста
        recipient = console.input("[bold white]👤 Кому (Юзернейм/ID): [/bold white]").strip()
        if not recipient:
            console.print("[bold yellow]🚀 Выход в терминал...[/bold yellow]")
            break

        clear()
        all_gifts = load_custom_gifts()
        console.print(f"[bold yellow]╭──────────── СПИСОК ПОДАРКОВ ────────────╮[/bold yellow]")
        for k, v in all_gifts.items():
            console.print(f"[bold yellow]│[/bold yellow] {k}. {v['name']}")
        console.print(f"[bold yellow]╰──────────────────────────────────────────╯[/bold yellow]")
        console.print("[dim]Добавить: /set [ID] [Название] | Enter для отмены[/dim]\n")
        
        choice = console.input("[bold white]🔢 Номер: [/bold white]").strip()
        if not choice: continue

        if choice.startswith("/set"):
            try:
                p = choice.split(" ", 2)
                n = save_custom_gift(p[1], p[2])
                console.print(f"[green]✅ Добавлено под №{n}[/green]")
                await asyncio.sleep(1.5); continue
            except: continue

        gift = all_gifts.get(choice)
        if not gift: continue

        qty_in = console.input("[bold white]🔢 Кол-во (Enter=1): [/bold white]").strip()
        qty = int(qty_in) if qty_in.isdigit() else 1
        is_anon = console.input("[bold white]❓ Анонимно? (да/нет): [/bold white]").lower() in ['да', 'y', '1']
        comment = None
        if not is_anon:
            comment = console.input("[bold white]💬 Сообщение (Enter=нет): [/bold white]").strip() or None

        clear()
        total = qty * GIFT_PRICE
        console.print(f"[bold green]Сумма к оплате: {total} ⭐[/bold green]")

        if balance < total:
            console.input(f"\n[red]Недостаточно звезд! Нажми Enter...[/red]"); continue

        if console.input("\n🚀 Отправить? (да/нет): ").lower() in ['да', 'y']:
            for i in range(qty):
                console.print(f"📡 Отправка {i+1}/{qty}...", end="\r")
                try:
                    peer = await client.get_input_entity(recipient)
                    inv = types.InputInvoiceStarGift(
                        peer=peer, gift_id=gift['id'], 
                        hide_name=is_anon, 
                        message=types.TextWithEntities(text=comment, entities=[]) if comment else None
                    )
                    form = await client(functions.payments.GetPaymentFormRequest(invoice=inv))
                    await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=inv))
                    if qty > 1: await asyncio.sleep(2.5)
                except Exception as e:
                    console.print(f"\n[red]Ошибка: {e}[/red]"); break
            console.print("\n\n[bold green]✅ ГОТОВО![/bold green]"); await asyncio.sleep(2)

    await client.disconnect()

def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    run()
