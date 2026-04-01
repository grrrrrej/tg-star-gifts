import asyncio
import sys
import os
import json
from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box

console = Console()

# --- КОНФИГУРАЦИЯ ---
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
SESSION_FILE = "session.txt"
CUSTOM_GIFTS_FILE = "custom_gifts.txt"
GIFT_PRICE = 50
ID_KEY = "40626c61636b7065616e"

def get_author():
    try: return bytes.fromhex(ID_KEY).decode()
    except: return ""

default_gifts = {
    "1": {"name": "🎄 Новогодний Мишка", "id": 5956217000635139069},
    "2": {"name": "🎄 Новогодняя Елка", "id": 5922558454332916696},
    "3": {"name": "❤️ Валентинка", "id": 5801108895304779062},
    "4": {"name": "🧸 Мишка 14 февраля", "id": 5800655655995968830},
    "5": {"name": "🌸 Мишка 8 марта", "id": 5866352046986232958},
    "6": {"name": "🍀 Мишка Патрик", "id": 5893356958802511476}
}

def load_all_gifts():
    gifts = default_gifts.copy()
    if os.path.exists(CUSTOM_GIFTS_FILE):
        try:
            with open(CUSTOM_GIFTS_FILE, "r", encoding="utf-8") as f:
                custom = json.load(f)
                start_idx = len(default_gifts) + 1
                for v in custom.values():
                    gifts[str(start_idx)] = v
                    start_idx += 1
        except: pass
    return gifts

def save_custom_gift(gift_id, name):
    custom_data = {}
    if os.path.exists(CUSTOM_GIFTS_FILE):
        try:
            with open(CUSTOM_GIFTS_FILE, "r", encoding="utf-8") as f:
                custom_data = json.load(f)
        except: pass
    new_idx = str(len(custom_data) + 1)
    custom_data[new_idx] = {"name": name, "id": int(gift_id)}
    with open(CUSTOM_GIFTS_FILE, "w", encoding="utf-8") as f:
        json.dump(custom_data, f, ensure_ascii=False, indent=4)

def delete_custom_gift(choice_idx):
    if not os.path.exists(CUSTOM_GIFTS_FILE): return False, "Список пуст"
    try:
        idx = int(choice_idx)
        if idx <= len(default_gifts): return False, "Нельзя удалить стандартный"
        with open(CUSTOM_GIFTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        items = list(data.values())
        real_idx = idx - len(default_gifts) - 1
        if 0 <= real_idx < len(items):
            items.pop(real_idx)
            new_data = {str(i+1): v for i, v in enumerate(items)}
            with open(CUSTOM_GIFTS_FILE, "w", encoding="utf-8") as f:
                json.dump(new_data, f, ensure_ascii=False, indent=4)
            return True, "Удалено"
        return False, "Не найден"
    except: return False, "Ошибка"

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

async def get_balance(client):
    try:
        res = await client(functions.payments.GetStarsStatusRequest(peer=types.InputPeerSelf()))
        # Фикс бага с отображением объекта вместо числа
        balance = res.balance
        if hasattr(balance, 'amount'): return balance.amount
        return balance
    except: return 0

async def main_logic():
    dev_name = get_author()
    if dev_name != "@blackpean": return

    # Фикс сессии: читаем из файла если есть
    session_str = ""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            session_str = f.read().strip()

    client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
    
    await client.connect()
    if not await client.is_user_authorized():
        console.print("[yellow]Нужна авторизация...[/yellow]")
        await client.start()
        with open(SESSION_FILE, "w") as f:
            f.write(client.session.save())

    while True:
        clear()
        me = await client.get_me()
        balance = await get_balance(client)
        
        console.print(Panel(
            f"[bold white]👤 Аккаунт:[/bold white] [cyan]{me.first_name}[/cyan]\n"
            f"[bold white]💎 Баланс:[/bold white] [yellow]{balance} ⭐[/yellow]\n"
            f"[bold white]👨‍💻 Dev:[/bold white] [green]{dev_name}[/green]",
            title="[bold magenta]Telegram Star Gifts[/bold magenta]",
            border_style="magenta",
            box=box.ROUNDED
        ))

        recipient = console.input("[bold white]🎯 Кому (Ник/ID) или Enter для выхода: [/bold white]").strip()
        if not recipient: 
            console.print("[yellow]Выход...[/yellow]")
            break

        while True:
            clear()
            all_gifts = load_all_gifts()
            
            table = Table(title="🎁 Доступные подарки", box=box.ROUNDED, border_style="cyan", header_style="bold cyan")
            table.add_column("№", justify="center")
            table.add_column("Название", justify="left")
            table.add_column("ID Подарка", justify="right", style="dim")

            for k, v in all_gifts.items():
                table.add_row(k, v['name'], str(v['id']))
            
            console.print(table)
            console.print(Panel(
                "[magenta]➕ /set [ID] [Имя][/magenta] | [red]❌ /unset [№][/red]\n[white]Пусто = Назад к выбору цели[/white]",
                box=box.ROUNDED, border_style="dim"
            ))
            
            choice = console.input("\n[bold cyan]Выберите № или команду: [/bold cyan]").strip()
            if not choice: break

            if choice.startswith("/set"):
                try:
                    p = choice.split(" ", 2)
                    save_custom_gift(p[1], p[2])
                    continue
                except: continue

            if choice.startswith("/unset"):
                try:
                    ok, msg = delete_custom_gift(choice.split(" ")[1])
                    console.print(f"[{'green' if ok else 'red'}] {msg}[/]")
                    await asyncio.sleep(1); continue
                except: continue

            gift = all_gifts.get(choice)
            if not gift: continue
            
            qty = Prompt.ask("[bold white]Кол-во[/bold white]", default="1")
            is_anon = Prompt.ask("[bold white]Анонимно?[/bold white]", choices=["да", "нет"], default="нет") == "да"
            
            if Prompt.ask(f"\n🚀 Отправить {qty} шт {gift['name']}?", choices=["да", "нет"], default="да") == "да":
                try:
                    peer = await client.get_input_entity(recipient)
                    for i in range(int(qty)):
                        inv = types.InputInvoiceStarGift(peer=peer, gift_id=gift['id'], hide_name=is_anon)
                        form = await client(functions.payments.GetPaymentFormRequest(invoice=inv))
                        await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=inv))
                        console.print(f"[green]✅ {i+1} отправлен![/green]")
                        await asyncio.sleep(1)
                except Exception as e:
                    console.print(f"[red]Ошибка: {e}[/red]")
                Prompt.ask("\nНажмите Enter")
            break

    await client.disconnect()

def run():
    try:
        asyncio.run(main_logic())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    run()
