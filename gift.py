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
            clear() # Удаляем предыдущий этап (ввод ника)
            all_gifts = load_all_gifts()
            
            table = Table(box=box.ROUNDED, border_style="cyan", header_style="bold cyan", width=48)
            table.add_column("№", justify="center")
            table.add_column("Название", justify="left")
            table.add_column("ID", justify="right", style="dim")

            for k, v in all_gifts.items():
                table.add_row(k, v['name'], str(v['id']))
            
            console.print(Panel(table, title="🎁 Подарки", border_style="cyan", width=50))
            console.print(Panel("[magenta]➕ /set [ID] [Имя][/magenta] | [red]❌ /unset [№][/red]\n[white]Пусто = Назад[/white]", box=box.ROUNDED, width=50))
            
            choice = console.input("\n[bold cyan]Выберите №: [/bold cyan]").strip()
            if not choice: break

            gift = all_gifts.get(choice)
            if not gift: continue
            
            clear() # Удаляем таблицу подарков перед настройкой отправки
            console.print(Panel(f"[bold yellow]Настройка:[/bold yellow] {gift['name']}", border_style="yellow", width=50))
            
            qty_str = Prompt.ask("[bold white]Кол-во[/bold white]", default="1")
            qty = int(qty_str) if qty_str.isdigit() else 1
            is_anon = Prompt.ask("[bold white]Анонимно?[/bold white]", choices=["да", "нет"], default="нет") == "да"
            
            if Prompt.ask(f"\n🚀 Отправить {qty} шт.?", choices=["да", "нет"], default="да") == "да":
                clear() # Очищаем перед процессом отправки
                sent_count = 0
                errors = []
                
                with console.status("[bold green]Отправка подарков...") as status:
                    try:
                        peer = await client.get_input_entity(recipient)
                        for i in range(qty):
                            try:
                                inv = types.InputInvoiceStarGift(peer=peer, gift_id=gift['id'], hide_name=is_anon)
                                form = await client(functions.payments.GetPaymentFormRequest(invoice=inv))
                                await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=inv))
                                sent_count += 1
                                if qty > 1: await asyncio.sleep(1.5)
                            except Exception as e:
                                errors.append(str(e))
                                break
                    except Exception as e:
                        errors.append(str(e))

                # ФИНАЛЬНАЯ ТАБЛИЦА
                clear()
                result_table = Table(title="📊 Итог операции", box=box.ROUNDED, border_style="green", width=50)
                result_table.add_column("Параметр", style="cyan")
                result_table.add_column("Значение", style="white")
                
                result_table.add_row("Получатель", recipient)
                result_table.add_row("Подарок", gift['name'])
                result_table.add_row("Отправлено", f"[bold green]{sent_count} / {qty}[/bold green]")
                result_table.add_row("Анонимно", "Да" if is_anon else "Нет")
                
                if errors:
                    result_table.add_row("Ошибки", f"[red]{errors[0]}[/red]")
                
                console.print(result_table)
                Prompt.ask("\n[bold yellow]Нажмите Enter, чтобы вернуться в меню[/bold yellow]")
            break

def run():
    try:
        asyncio.run(main_logic())
    except (KeyboardInterrupt, SystemExit): pass

if __name__ == "__main__":
    run()
