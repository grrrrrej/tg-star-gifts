import asyncio
import sys
import os
import json
import re
from telethon import TelegramClient, functions, types, errors
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
    "6": {"name": "🍀 Мишка Патрик", "id": 5893356958802511476},
    "7": {"name": "🤡 Мишка Клоун", "id": 5935895822435615926}
}

def load_all_gifts():
    gifts = default_gifts.copy()
    if os.path.exists(CUSTOM_GIFTS_FILE):
        try:
            with open(CUSTOM_GIFTS_FILE, "r", encoding="utf-8") as f:
                custom = json.load(f)
                for i, v in enumerate(custom.values(), start=len(default_gifts)+1):
                    gifts[str(i)] = v
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
        with open(SESSION_FILE, "r") as f: session_str = f.read().strip()

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
            table.add_column("ID", justify="right", style="dim")
            for k, v in all_gifts.items(): table.add_row(k, v['name'], str(v['id']))
            
            console.print(Panel(table, title="🎁 Подарки", border_style="cyan", width=50))
            console.print(Panel("[white]Выберите № подарка (Enter - Назад)[/white]", box=box.ROUNDED, width=50, border_style="dim"))
            
            choice = console.input("\n[bold cyan]Выберите №: [/bold cyan]").strip()
            if not choice: break

            gift = all_gifts.get(choice)
            if not gift: continue
            
            clear()
            console.print(Panel(f"[bold yellow]Настройка:[/bold yellow] {gift['name']}", border_style="yellow", width=50, box=box.ROUNDED))
            qty_str = Prompt.ask("[bold white]Кол-во[/bold white]", default="1")
            qty = int(qty_str) if qty_str.isdigit() else 1
            is_anon = Prompt.ask("[bold white]Анонимно?[/bold white]", choices=["да", "нет"], default="нет") == "да"
            
            gift_comment = None
            if not is_anon:
                gift_comment = console.input("[bold white]💬 Сообщение (Enter = нет): [/bold white]").strip()
            
            clear()
            confirm_info = (
                f"👤 [bold white]Кому:[/bold white] [cyan]{recipient}[/cyan]\n"
                f"🎁 [bold white]Подарок:[/bold white] [yellow]{gift['name']}[/yellow]\n"
                f"📦 [bold white]Количество:[/bold white] [green]{qty} шт.[/green]\n"
                f"🕶️ [bold white]Анонимно:[/bold white] {'[green]Да[/green]' if is_anon else '[red]Нет[/red]'}"
            )
            if gift_comment: confirm_info += f"\n💬 [bold white]Текст:[/bold white] [dim]{gift_comment}[/dim]"
            confirm_info += f"\n💰 [bold white]Итого:[/bold white] [yellow]{qty * 50} ⭐[/yellow]"
            
            console.print(Panel(confirm_info, title="[bold red]ПОДТВЕРЖДЕНИЕ[/bold red]", border_style="red", box=box.DOUBLE, width=50))
            
            if Prompt.ask("\n🚀 Отправить?", choices=["да", "нет"], default="да") == "да":
                clear()
                sent_count = 0
                errors_list = []
                
                with console.status("[bold green]Работаю...") as status:
                    try:
                        peer = await client.get_input_entity(recipient)
                        i = 0
                        while i < qty:
                            try:
                                status.update(f"[bold green]Отправка {i+1} из {qty}...")
                                inv = types.InputInvoiceStarGift(
                                    peer=peer, 
                                    gift_id=gift['id'], 
                                    hide_name=is_anon, 
                                    message=gift_comment if gift_comment else None
                                )
                                form = await client(functions.payments.GetPaymentFormRequest(invoice=inv))
                                await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=inv))
                                
                                sent_count += 1
                                i += 1
                                if i < qty:
                                    await asyncio.sleep(2.5) # Пауза для мобильной стабильности
                                    
                            except errors.FloodWaitError as e:
                                status.update(f"[bold yellow]FloodWait: ждем {e.seconds} сек...")
                                await asyncio.sleep(e.seconds + 1)
                                # Не увеличиваем i, пробуем этот же подарок снова
                            except Exception as e:
                                errors_list.append(str(e))
                                i += 1 # Пропускаем проблемный подарок и идем дальше
                                
                    except Exception as e:
                        errors_list.append(f"Ошибка доступа: {str(e)}")

                clear()
                res = Table(title="📊 Итог операции", box=box.ROUNDED, border_style="green", width=50)
                res.add_column("Параметр"); res.add_column("Значение")
                res.add_row("Получатель", recipient)
                res.add_row("Подарок", gift['name'])
                res.add_row("Результат", f"[bold green]{sent_count} из {qty} успешно[/bold green]")
                if errors_list:
                    res.add_row("Заметки", f"[red]{errors_list[-1][:40]}...[/red]")
                
                console.print(res)
                Prompt.ask("\n[bold yellow]Нажмите Enter[/bold yellow]")
            break

def run():
    try: asyncio.run(main_logic())
    except (KeyboardInterrupt, SystemExit): pass

if __name__ == "__main__":
    run()
