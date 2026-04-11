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
CUSTOM_GIFTS_FILE = "custom_gifts.txt"
ID_KEY = "40626c61636b7065616e"

def get_author():
    try: return bytes.fromhex(ID_KEY).decode()
    except: return ""

# СПИСОК: ОТ ЕЛКИ ДО КЛОУНА
default_gifts = {
    "1": {"name": "🎄 Елка", "id": 5922558454332916696},
    "2": {"name": "🎄 Новогодний мишка", "id": 5956217000635139069},
    "3": {"name": "❤️ Сердце валентинка", "id": 5801108895304779062},
    "4": {"name": "🧸 Мишка 14 февраля", "id": 5800655655995968830},
    "5": {"name": "🌸 Мишка 8 марта", "id": 5866352046986232958},
    "6": {"name": "🍀 Мишка Патрик", "id": 5893356958802511476},
    "7": {"name": "🤡 Клоун", "id": 5935895822435615975}
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

def save_custom_gift(gift_id, name):
    custom_data = {}
    if os.path.exists(CUSTOM_GIFTS_FILE):
        try:
            with open(CUSTOM_GIFTS_FILE, "r", encoding="utf-8") as f: custom_data = json.load(f)
        except: pass
    new_idx = str(len(custom_data) + 1)
    custom_data[new_idx] = {"name": name, "id": int(gift_id)}
    with open(CUSTOM_GIFTS_FILE, "w", encoding="utf-8") as f:
        json.dump(custom_data, f, ensure_ascii=False, indent=4)

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
        # Увеличил ширину панели для баланса
        console.print(Panel(f"👤 [bold white]Аккаунт:[/bold white] [cyan]{me.first_name}[/cyan]\n💎 [bold white]Баланс:[/bold white] [yellow]{balance} ⭐[/yellow]\n👨‍💻 [bold white]Dev:[/bold white] [green]{dev_name}[/green]", title="[bold magenta]Telegram Star Gifts[/bold magenta]", border_style="magenta", box=box.ROUNDED, width=60))

        recipient = console.input("\n[bold white]🎯 Кому (Ник/ID): [/bold white]").strip()
        if not recipient: break

        while True:
            clear()
            all_gifts = load_all_gifts()
            # ТУТ ИСПРАВЛЕНА ТАБЛИЦА (width=60 и четкие колонки)
            table = Table(box=box.ROUNDED, border_style="cyan", header_style="bold cyan", width=60, expand=True)
            table.add_column("№", justify="center", width=4, no_wrap=True)
            table.add_column("Название", justify="left", no_wrap=True)
            table.add_column("ID", justify="right", style="dim", width=22, no_wrap=True)
            
            for k, v in all_gifts.items():
                table.add_row(k, v['name'], str(v['id']))
            
            console.print(Panel(table, title="🎁 Выберите подарок", border_style="cyan", width=60))
            console.print(Panel("[bold magenta]➕ /set [ID] [Имя][/bold magenta]", box=box.ROUNDED, border_style="magenta", width=60))
            
            choice = console.input("\n[bold cyan]Выберите №: [/bold cyan]").strip()
            if not choice: break

            if choice.startswith("/set"):
                try:
                    p = choice.split(" ", 2)
                    save_custom_gift(p[1], p[2]); continue
                except: continue

            gift = all_gifts.get(choice)
            if not gift: continue
            
            clear()
            console.print(Panel(f"👤 [cyan]{recipient}[/cyan] | 🎁 [yellow]{gift['name']}[/yellow]\n💎 [bold white]Баланс:[/bold white] [yellow]{balance} ⭐[/yellow]", title="[bold yellow]Настройка[/bold yellow]", border_style="yellow", width=60))
            
            qty_str = Prompt.ask("[bold white]Кол-во[/bold white]", default="1")
            qty = int(qty_str) if qty_str.isdigit() else 1
            is_anon = Prompt.ask("[bold white]Анонимно?[/bold white]", choices=["да", "нет"], default="нет") == "да"
            
            gift_comment = None
            if not is_anon:
                gift_comment = console.input("[bold white]💬 Сообщение: [/bold white]").strip()
                if not gift_comment: gift_comment = None

            clear()
            conf = Table(box=box.ROUNDED, border_style="red", width=60, show_header=False)
            conf.add_row("[bold white]Кому:[/bold white]", f"[cyan]{recipient}[/cyan]")
            conf.add_row("[bold white]Подарок:[/bold white]", f"[yellow]{gift['name']}[/yellow]")
            conf.add_row("[bold white]Количество:[/bold white]", f"[green]{qty} шт.[/green]")
            conf.add_row("[bold white]Анонимно:[/bold white]", "[green]Да[/green]" if is_anon else "[red]Нет[/red]")
            if not is_anon and gift_comment:
                conf.add_row("[bold white]Сообщение:[/bold white]", f"[dim]{gift_comment}[/dim]")
            conf.add_row("[bold white]Итого:[/bold white]", f"[bold yellow]{qty * 50} ⭐[/bold yellow]")
            
            console.print(Panel(conf, title="[bold red]ПОДТВЕРЖДЕНИЕ[/bold red]", border_style="red", box=box.DOUBLE, width=60))
            
            if Prompt.ask("\n🚀 Отправить?", choices=["да", "нет"], default="да") == "да":
                clear()
                sent = 0; errs = []
                with console.status("[bold green]Отправка...") as status:
                    try:
                        target = int(recipient) if recipient.replace('-', '').isdigit() else recipient
                        user = await client.get_entity(target)
                        peer = await client.get_input_entity(user)
                        
                        final_msg = None
                        if gift_comment and not is_anon:
                            final_msg = types.TextWithEntities(text=gift_comment, entities=[])

                        for i in range(qty):
                            try:
                                status.update(f"[bold green]Отправка {i+1}/{qty}...")
                                inv = types.InputInvoiceStarGift(peer=peer, gift_id=gift['id'], hide_name=is_anon, message=final_msg)
                                form = await client(functions.payments.GetPaymentFormRequest(invoice=inv))
                                await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=inv))
                                sent += 1
                                if qty > i+1: await asyncio.sleep(4.0)
                            except Exception as e:
                                errs.append(str(e)); break
                    except Exception as e: errs.append(str(e))

                clear()
                res = Table(title="📊 Итог", box=box.ROUNDED, border_style="green", width=60)
                res.add_column("Параметр"); res.add_column("Значение")
                res.add_row("Статус", f"[bold green]{sent} из {qty} успешно[/bold green]")
                if errs: res.add_row("Ошибка", f"[red]{errs[0][:60]}[/red]")
                
                console.print(res)
                Prompt.ask("\n[bold yellow]Нажмите Enter[/bold yellow]")
            break
    await client.disconnect()

def run():
    try: asyncio.run(main_logic())
    except: pass

if __name__ == "__main__":
    run()
