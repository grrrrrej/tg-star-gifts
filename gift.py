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
GIFTS_DB = "gifts_base.json"
ID_KEY = "40626c61636b7065616e"

def get_author():
    try: return bytes.fromhex(ID_KEY).decode()
    except: return ""

init_gifts = [
    {"name": "🎄 Елка", "id": 5922558454332916696},
    {"name": "🎄 Новогодний мишка", "id": 5956217000635139069},
    {"name": "❤️ Сердце валентинка", "id": 5801108895304779062},
    {"name": "🧸 Мишка 14 февраля", "id": 5800655655995968830},
    {"name": "🌸 Мишка 8 марта", "id": 5866352046986232958},
    {"name": "🍀 Мишка Патрик", "id": 5893356958802511476},
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

def save_db(data):
    with open(GIFTS_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

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
        console.print(Panel(f"👤 [bold white]Аккаунт:[/bold white] [cyan]{me.first_name}[/cyan]\n💎 [bold white]Баланс:[/bold white] [yellow]{balance} ⭐[/yellow]\n👨‍💻 [bold white]Dev:[/bold white] [green]{dev_name}[/green]", title="[bold magenta]Telegram Star Gifts[/bold magenta]", border_style="magenta", box=box.ROUNDED, width=60))

        # НОВАЯ ПОДСКАЗКА ДЛЯ МАССОВОЙ РАССЫЛКИ
        raw_recipients = console.input("\n[bold white]🎯 Кому (через запятую для рассылки): [/bold white]").strip()
        if not raw_recipients: break
        
        # Парсим список получателей
        recipients = [r.strip() for r in raw_recipients.split(",") if r.strip()]

        while True:
            clear()
            current_gifts = load_db()
            table = Table(box=box.ROUNDED, border_style="cyan", header_style="bold cyan", width=60, expand=True)
            table.add_column("№", justify="center", width=4)
            table.add_column("Название", justify="left")
            table.add_column("ID", justify="right", style="dim", width=22)
            
            for i, v in enumerate(current_gifts, 1):
                table.add_row(str(i), v['name'], str(v['id']))
            
            console.print(Panel(table, title="🎁 Выберите подарок", border_style="cyan", width=60))
            console.print(Panel("[bold magenta]➕ /set [ID] [Имя][/bold magenta]  [bold red]❌ /unset [№][/bold red]", box=box.ROUNDED, border_style="magenta", width=60))
            
            choice = console.input("\n[bold cyan]Команда или №: [/bold cyan]").strip()
            if not choice: break

            if choice.startswith("/set"):
                try:
                    p = choice.split(" ", 2)
                    current_gifts.append({"name": p[2], "id": int(p[1])})
                    save_db(current_gifts); continue
                except: continue
            
            if choice.startswith("/unset"):
                try:
                    idx = int(choice.split(" ")[1]) - 1
                    if 0 <= idx < len(current_gifts):
                        current_gifts.pop(idx)
                        save_db(current_gifts)
                    continue
                except: continue

            try: gift = current_gifts[int(choice)-1]
            except: continue
            
            # --- Настройка ---
            clear()
            is_mass = len(recipients) > 1
            rec_display = f"{recipients[0]} + {len(recipients)-1} чел." if is_mass else recipients[0]
            
            console.print(Panel(f"🎯 [cyan]{rec_display}[/cyan] | 🎁 [yellow]{gift['name']}[/yellow]\n💎 [bold white]Баланс:[/bold white] [yellow]{balance} ⭐[/yellow]", title="[bold yellow]Настройка[/bold yellow]", border_style="yellow", width=60))
            
            qty = 1
            if not is_mass:
                qty_str = Prompt.ask("[bold white]Кол-во для этого юзера[/bold white]", default="1")
                qty = int(qty_str) if qty_str.isdigit() else 1
            
            is_anon = Prompt.ask("[bold white]Анонимно?[/bold white]", choices=["да", "нет"], default="нет") == "да"
            gift_comment = console.input("[bold white]💬 Сообщение (Enter = пропустить): [/bold white]").strip() if not is_anon else None
            
            # --- Подтверждение ---
            clear()
            total_stars = (qty * 50) if not is_mass else (len(recipients) * 50)
            conf = Table(box=box.ROUNDED, border_style="red", width=60, show_header=False)
            conf.add_row("[bold white]Получателей:[/bold white]", f"[cyan]{len(recipients)}[/cyan]")
            conf.add_row("[bold white]Подарок:[/bold white]", f"[yellow]{gift['name']}[/yellow]")
            conf.add_row("[bold white]Итого звёзд:[/bold white]", f"[bold yellow]{total_stars} ⭐[/bold yellow]")
            console.print(Panel(conf, title="[bold red]ПОДТВЕРЖДЕНИЕ[/bold red]", border_style="red", box=box.DOUBLE, width=60))
            
            if Prompt.ask("\n🚀 Запустить?", choices=["да", "нет"], default="да") == "да":
                clear()
                results = []
                with console.status("[bold green]Работаю...") as status:
                    for target_name in recipients:
                        try:
                            status.update(f"[bold green]Отправка для {target_name}...")
                            target = int(target_name) if target_name.replace('-', '').isdigit() else target_name
                            user = await client.get_entity(target)
                            peer = await client.get_input_entity(user)
                            
                            final_msg = types.TextWithEntities(text=gift_comment, entities=[]) if gift_comment else None
                            
                            # Если один юзер - шлем qty, если рассылка - по 1 каждому
                            loops = qty if not is_mass else 1
                            for _ in range(loops):
                                inv = types.InputInvoiceStarGift(peer=peer, gift_id=gift['id'], hide_name=is_anon, message=final_msg)
                                form = await client(functions.payments.GetPaymentFormRequest(invoice=inv))
                                await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=inv))
                                if loops > 1 or is_mass: await asyncio.sleep(4.1)
                            
                            results.append((target_name, "[bold green]✅ Ок[/bold green]"))
                        except Exception as e:
                            results.append((target_name, f"[red]❌ {str(e)[:30]}[/red]"))

                # --- Итоговая таблица рассылки ---
                clear()
                res_table = Table(title="📊 Отчет по списку", box=box.ROUNDED, border_style="green", width=60)
                res_table.add_column("Получатель"); res_table.add_column("Результат")
                for r_name, r_status in results:
                    res_table.add_row(r_name, r_status)
                
                console.print(res_table)
                Prompt.ask("\n[bold yellow]Нажмите Enter[/bold yellow]")
            break
    await client.disconnect()

def run():
    try: asyncio.run(main_logic())
    except: pass

if __name__ == "__main__":
    run()
