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

# Идентификатор автора
ID_KEY = "40626c61636b7065616e" 

def get_author():
    try:
        return bytes.fromhex(ID_KEY).decode()
    except: return ""

default_gifts = {
    "1": {"name": "🎄 Новогодний Мишка", "id": 5956217000635139069},
    "2": {"name": "🎄 Новогодняя Елка", "id": 5922558454332916696},
    "3": {"name": "❤️ Валентинка (Сердце)", "id": 5801108895304779062},
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
                # Пересчитываем индексы для кастомных подарков, чтобы они шли после дефолтных
                start_idx = len(default_gifts) + 1
                for i, (old_k, v) in enumerate(custom.items()):
                    gifts[str(start_idx + i)] = v
        except: pass
    return gifts

def save_custom_gift(gift_id, name):
    custom_list = []
    if os.path.exists(CUSTOM_GIFTS_FILE):
        try:
            with open(CUSTOM_GIFTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                custom_list = list(data.values())
        except: pass
    
    custom_list.append({"name": name, "id": int(gift_id)})
    
    # Сохраняем просто как список объектов
    new_data = {str(i+1): v for i, v in enumerate(custom_list)}
    with open(CUSTOM_GIFTS_FILE, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)

def delete_custom_gift(choice_idx):
    all_gifts = load_all_gifts()
    if choice_idx not in all_gifts:
        return False, "Номер не найден"
    if int(choice_idx) <= len(default_gifts):
        return False, "Нельзя удалить стандартный подарок"

    # Читаем только кастомные
    if os.path.exists(CUSTOM_GIFTS_FILE):
        with open(CUSTOM_GIFTS_FILE, "r", encoding="utf-8") as f:
            custom_data = json.load(f)
        
        # Вычисляем какой это был по счету в кастомном файле
        internal_idx = str(int(choice_idx) - len(default_gifts))
        if internal_idx in custom_data:
            del custom_data[internal_idx]
            # Переиндексация оставшихся
            new_custom = {str(i+1): v for i, v in enumerate(custom_data.values())}
            with open(CUSTOM_GIFTS_FILE, "w", encoding="utf-8") as f:
                json.dump(new_custom, f, ensure_ascii=False, indent=4)
            return True, "Удалено"
    return False, "Ошибка удаления"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

async def get_balance(client):
    try:
        res = await client(functions.payments.GetStarsStatusRequest(peer=types.InputPeerSelf()))
        return res.balance.amount if hasattr(res.balance, 'amount') else res.balance
    except: return 0

async def main():
    if get_author() != "@blackpean":
        print("Ошибка лицензии"); return

    client = TelegramClient(StringSession(""), API_ID, API_HASH)
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            client.session = StringSession(f.read().strip())

    await client.connect()
    if not await client.is_user_authorized():
        await client.start()
        with open(SESSION_FILE, "w") as f: f.write(client.session.save())

    while True:
        clear()
        me = await client.get_me()
        balance = await get_balance(client)
        
        console.print(f"[bold cyan]👤 {me.first_name} | 💎 {balance} ⭐[/bold cyan]")
        console.print("[dim]Enter для выхода[/dim]\n")

        recipient = console.input("[bold white]Кому (Ник/ID): [/bold white]").strip()
        if not recipient: break

        while True:
            clear()
            all_gifts = load_all_gifts()
            console.print("[bold yellow]📜 Список подарков:[/bold yellow]")
            for k, v in all_gifts.items():
                console.print(f" {k}. {v['name']} [dim]({v['id']})[/dim]")
            
            console.print("\n[magenta]➕ Добавить: /set [ID] [Имя][/magenta]")
            console.print("[red]❌ Удалить: /unset [Номер][/red]")
            
            choice = console.input("\n[bold white]Номер подарка: [/bold white]").strip()
            if not choice: break

            # ЛОГИКА /SET
            if choice.startswith("/set"):
                try:
                    _, g_id, g_name = choice.split(" ", 2)
                    save_custom_gift(g_id, g_name)
                    console.print("[green]✅ Сохранено![/green]")
                    await asyncio.sleep(1); continue
                except: continue

            # ЛОГИКА /UNSET
            if choice.startswith("/unset"):
                try:
                    _, u_idx = choice.split(" ", 1)
                    ok, msg = delete_custom_gift(u_idx)
                    color = "green" if ok else "red"
                    console.print(f"[{color}] {msg}[/{color}]")
                    await asyncio.sleep(1.5); continue
                except: continue

            gift = all_gifts.get(choice)
            if not gift: continue

            qty_in = console.input("Кол-во (Enter=1): ").strip()
            qty = int(qty_in) if qty_in.isdigit() else 1
            is_anon = console.input("Анонимно? (да/нет): ").lower() in ['да', 'y', '1']
            
            total = qty * GIFT_PRICE
            if balance < total:
                check = console.input(f"\n[red]Недостаточно звезд ({balance}/{total})[/red]\n[yellow]Enter для выхода[/yellow]")
                if not check: return
                else: break

            if console.input(f"\n🚀 Отправить {qty} шт за {total} ⭐? (да/нет): ").lower() in ['да', 'y', '1']:
                for i in range(qty):
                    try:
                        peer = await client.get_input_entity(recipient)
                        inv = types.InputInvoiceStarGift(peer=peer, gift_id=gift['id'], hide_name=is_anon)
                        form = await client(functions.payments.GetPaymentFormRequest(invoice=inv))
                        await client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=inv))
                        console.print(f"✅ {i+1} отправлен")
                        if qty > 1: await asyncio.sleep(2)
                    except Exception as e:
                        console.print(f"[red]Ошибка: {e}[/red]"); break
                
                if not console.input("\n[yellow]Enter для выхода или любой символ для меню[/yellow]"): return
                break

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
