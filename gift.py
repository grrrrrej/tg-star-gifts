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

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

async def get_balance(client):
    try:
        res = await client(functions.payments.GetStarsStatusRequest(peer=types.InputPeerSelf()))
        return res.balance.amount if hasattr(res.balance, 'amount') else res.balance
    except: return 0

async def main_logic():
    dev_name = get_author()
    if dev_name != "@blackpean": return

    session_str = ""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            session_str = f.read().strip()

    client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
    await client.connect()
    
    if not await client.is_user_authorized():
        await client.start()
        with open(SESSION_FILE, "w") as f: f.write(client.session.save())

    while True:
        clear()
        me = await client.get_me()
        balance = await get_balance(client)
        
        console.print(Panel(
            f"👤 [bold white]Аккаунт:[/bold white] [cyan]{me.first_name}[/cyan]\n"
            f"💎 [bold white]Баланс:[/bold white] [yellow]{balance} ⭐[/yellow]\n"
            f"👨‍💻 [bold white]Dev:[/bold white] [green]{dev_name}[/green]",
            title="[bold magenta]Telegram Star Gifts[/bold magenta]", border_style="magenta", box=box.ROUNDED, width=50
        ))

        recipient = console.input("\n[bold white]🎯 Кому (Ник/ID): [/bold white]").strip()
        if not recipient: 
            await client.disconnect()
            sys.exit(0)

        while True:
            clear()
            all_gifts = load_all_gifts()
            
            table = Table(box=box.ROUNDED, border_style="cyan", header_style="bold cyan", width=48)
            table.add_column("№", justify="center")
            table.add_column("Название", justify="left")

            for k, v in all_gifts.items():
                table.add_row(k, v['name'])
            
            console.print(Panel(table, title="🎁 Подарки", border_style="cyan", width=50))
            
            choice = console.input("\n[bold cyan]Выберите №: [/bold cyan]").strip()
            if not choice: break

            gift = all_gifts.get(choice)
            if not gift: continue
            
            # Настройка
            qty = int(Prompt.ask("[bold white]Кол-во[/bold white]", default="1"))
            is_anon = Prompt.ask("[bold white]Анонимно?[/bold white]", choices=["да", "нет"], default="нет") == "да"
            
            if Prompt.ask("\n🚀 Отправить?", choices=["да", "нет"], default="да") == "да":
                sent_count = 0
                try:
                    peer = await client.get_input_entity(recipient)
                    for i in range(qty):
                        inv = types.InputInvoiceStarGift(peer=peer, gift_id=gift['id'], hide_name=is_anon)
                        form = await client(functions.payments.GetPaymentFormRequest(invoice=inv))
                        await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=inv))
                        sent_count += 1
                        await asyncio.sleep(1)
                except Exception as e:
                    console.print(f"[red]Ошибка: {e}[/red]")

                console.print(f"[green]Успешно отправлено: {sent_count}[/green]")
                Prompt.ask("\n[yellow]Нажмите Enter[/yellow]")
            break

def run():
    asyncio.run(main_logic())

if __name__ == "__main__":
    run()
