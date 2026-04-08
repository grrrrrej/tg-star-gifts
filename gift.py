import asyncio
import sys
import os
import json
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
        if not recipient: break

        while True:
            clear()
            table = Table(box=box.ROUNDED, border_style="cyan", header_style="bold cyan", width=48)
            table.add_column("№", justify="center")
            table.add_column("Название", justify="left")
            for k, v in default_gifts.items(): table.add_row(k, v['name'])
            
            console.print(Panel(table, title="🎁 Выберите подарок", border_style="cyan", width=50))
            choice = console.input("\n[bold cyan]Выберите № (Enter - Назад): [/bold cyan]").strip()
            if not choice: break

            gift = default_gifts.get(choice)
            if not gift: continue
            
            # --- ПАНЕЛЬ ПЕРЕД КОЛ-ВОМ ---
            clear()
            status_info = f"👤 [bold white]Цель:[/bold white] [cyan]{recipient}[/cyan]\n" \
                          f"🎁 [bold white]Подарок:[/bold white] [yellow]{gift['name']}[/yellow]\n" \
                          f"💎 [bold white]Ваш баланс:[/bold white] [yellow]{balance} ⭐[/yellow]"
            console.print(Panel(status_info, title="[bold yellow]Настройка[/bold yellow]", border_style="yellow", width=50))
            
            qty_str = Prompt.ask("[bold white]Кол-во[/bold white]", default="1")
            qty = int(qty_str) if qty_str.isdigit() else 1
            is_anon = Prompt.ask("[bold white]Анонимно?[/bold white]", choices=["да", "нет"], default="нет") == "да"
            
            gift_comment = None
            if not is_anon:
                gift_comment = console.input("[bold white]💬 Сообщение (пусто = без него): [/bold white]").strip()
                if not gift_comment: gift_comment = None

            # --- ТАБЛИЦА ПОДТВЕРЖДЕНИЯ ---
            clear()
            conf_table = Table(box=box.ROUNDED, border_style="red", width=50, show_header=False)
            conf_table.add_row("[bold white]Кому:[/bold white]", f"[cyan]{recipient}[/cyan]")
            conf_table.add_row("[bold white]Подарок:[/bold white]", f"[yellow]{gift['name']}[/yellow]")
            conf_table.add_row("[bold white]Количество:[/bold white]", f"[green]{qty} шт.[/green]")
            conf_table.add_row("[bold white]Анонимно:[/bold white]", "[green]Да[/green]" if is_anon else "[red]Нет[/red]")
            
            if not is_anon and gift_comment:
                conf_table.add_row("[bold white]Сообщение:[/bold white]", f"[dim]{gift_comment}[/dim]")
            
            conf_table.add_row("[bold white]Итого к оплате:[/bold white]", f"[bold yellow]{qty * 50} ⭐[/bold yellow]")
            
            console.print(Panel(conf_table, title="[bold red]ПОДТВЕРЖДЕНИЕ[/bold red]", border_style="red", box=box.DOUBLE, width=50))
            
            if Prompt.ask("\n🚀 Отправить?", choices=["да", "нет"], default="да") == "да":
                clear()
                sent_count = 0
                error_list = []
                
                with console.status("[bold green]Запуск процесса...") as status:
                    try:
                        target = recipient
                        if target.replace('-', '').isdigit(): target = int(target)
                        
                        user_obj = await client.get_entity(target)
                        peer = await client.get_input_entity(user_obj)
                        
                        for i in range(qty):
                            try:
                                status.update(f"[bold green]Отправка {i+1} из {qty}...")
                                # ФИКС: Явный None для API
                                final_msg = gift_comment if (gift_comment and not is_anon) else None

                                inv = types.InputInvoiceStarGift(
                                    peer=peer, gift_id=gift['id'], hide_name=is_anon, message=final_msg
                                )
                                form = await client(functions.payments.GetPaymentFormRequest(invoice=inv))
                                await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=inv))
                                sent_count += 1
                                if qty > i+1: await asyncio.sleep(3.5)
                            except Exception as e:
                                error_list.append(str(e))
                                break
                    except Exception as e:
                        error_list.append(str(e))

                # --- ИТОГОВЫЙ ОТЧЕТ ---
                clear()
                res = Table(title="📊 Итог операции", box=box.ROUNDED, border_style="green", width=50)
                res.add_column("Параметр", style="cyan")
                res.add_column("Значение", style="white")
                res.add_row("Получатель", f"{recipient}")
                res.add_row("Результат", f"[bold green]{sent_count} из {qty} успешно[/bold green]")
                res.add_row("Анонимно", "Да" if is_anon else "Нет")
                
                if not is_anon and gift_comment:
                    res.add_row("Сообщение", gift_comment)
                
                if error_list: res.add_row("Ошибка", f"[red]{error_list[0][:40]}[/red]")
                
                console.print(res)
                Prompt.ask("\n[bold yellow]Нажмите Enter для выхода в меню[/bold yellow]")
            break

    await client.disconnect()

def run():
    try: asyncio.run(main_logic())
    except (KeyboardInterrupt, SystemExit): pass

if __name__ == "__main__":
    run()
