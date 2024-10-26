import requests
import logging
import socket
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
import config
import asyncio

# Configurazione del logging
logging.basicConfig(level=logging.INFO)

bot = Client(
    "VoIP_blocker",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH
)

ip_memory = {}
unbanned_users = set()
verifica_tasks = {}
bot_messages = []

EUROPE_COUNTRY_CODES = [
    'AL', 'AD', 'AM', 'AT', 'AZ', 'BY', 'BE', 'BA', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 
    'FR', 'GE', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT', 'KZ', 'XK', 'LV', 'LI', 'LT', 'LU', 'MT', 
    'MD', 'MC', 'ME', 'NL', 'MK', 'NO', 'PL', 'PT', 'RO', 'SM', 'RS', 'SK', 'SI', 'ES', 'SE', 
    'CH', 'TR', 'UA', 'GB', 'VA'
]

def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return None

async def get_whois_info(ip):
    try:
        response = await asyncio.to_thread(requests.get, f"http://ip-api.com/json/{ip}")
        data = response.json()
        hostname = get_hostname(ip)
        if hostname:
            logging.info(f"Hostname: {hostname}")
        return data
    except Exception as e:
        logging.error(f"Errore nel recupero dei dati whois: {e}")
        return None

async def get_ip_and_location():
    ip = requests.get('https://icanhazip.com').text.strip()
    data = await get_whois_info(ip)
    return (data["query"], data["countryCode"]) if data else (None, None)

async def ban_user(client, chat_id, user_ids, reason):
    for user_id in user_ids:
        await client.ban_chat_member(chat_id, user_id)
    unban_button = InlineKeyboardButton(text="🔓 Sblocca Utenti", callback_data=f"unban_{'_'.join(map(str, user_ids))}")
    unban_keyboard = InlineKeyboardMarkup([[unban_button]])
    ban_message = await client.send_message(chat_id, reason, reply_markup=unban_keyboard)
    bot_messages.append((chat_id, ban_message.id))

@bot.on_callback_query(filters.regex(r"unban_"))
async def unban_callback(client, callback_query):
    user_ids = list(map(int, callback_query.data.split("_")[1:]))
    chat_id = callback_query.message.chat.id
    for user_id in user_ids:
        await client.unban_chat_member(chat_id, user_id)
        if user_id not in unbanned_users:
            await client.send_message(chat_id, f"L'utente con ID {user_id} è stato sbloccato e non dovrà ripetere la verifica.")
        unbanned_users.add(user_id)
    bot_messages.append((chat_id, callback_query.message.id))

@bot.on_message(filters.new_chat_members)
async def welcome_and_mute(client, message):
    for new_member in message.new_chat_members:
        if new_member.id in unbanned_users:
            continue
        await client.restrict_chat_member(
            message.chat.id,
            new_member.id,
            ChatPermissions(can_send_messages=False)
        )
        verification_link = f"https://t.me/{client.me.username}?start=verifica_{new_member.id}"
        button = InlineKeyboardButton(text="✅ Verifica", url=verification_link)
        keyboard = InlineKeyboardMarkup([[button]])
        welcome_message = await message.reply_text(
            f"Benvenuto {new_member.first_name or new_member.username}! Completa la verifica cliccando il bottone qui sotto.",
            reply_markup=keyboard
        )
        bot_messages.append((message.chat.id, welcome_message.id))
        
        task = asyncio.create_task(timer(client, message.chat.id, new_member.id, welcome_message.id))
        verifica_tasks[new_member.id] = task

async def timer(client, chat_id, user_id, message_id):
    await asyncio.sleep(180)
    if user_id not in ip_memory and user_id not in unbanned_users:
        await ban_user(client, chat_id, [user_id], f"L'utente {user_id} non ha passato la verifica ed è stato bannato.")
        await client.delete_messages(chat_id, [message_id])

@bot.on_message(filters.command("start"))
async def start_message(client, message):
    if len(message.command) > 1 and message.command[1].startswith("verifica_"):
        user_id = int(message.command[1].split("_")[1])
        if user_id in verifica_tasks:
            verifica_tasks[user_id].cancel()
        ip_address, country_code = await get_ip_and_location()
        if ip_address:
            if country_code not in EUROPE_COUNTRY_CODES:
                await ban_user(
                    client, message.chat.id, [user_id],
                    f"⚠️ **Verifica non superata** ⚠️\n\n"
                    f"L'utente {message.from_user.first_name or message.from_user.username} non ha passato la verifica.\n"
                    f"Per sbloccare, clicca il pulsante qui sotto."
                )
            else:
                ip_memory[user_id] = ip_address
                await client.restrict_chat_member(
                    message.chat.id, user_id,
                    ChatPermissions(can_send_messages=True, can_send_media_messages=True)
                )
    else:
        button1 = InlineKeyboardButton("🔒 Privacy and Policy", url="https://t.me/PrivacyAndPolicyCn")
        button2 = InlineKeyboardButton("➕ Aggiungimi ad un gruppo", url=f"https://t.me/{client.me.username}?startgroup=true")
        keyboard = InlineKeyboardMarkup([[button1], [button2]])
        await message.reply_text(
            f"👋 Ciao {message.from_user.first_name}. Benvenuto in VoIP Blocker!\n\n"
            f"❓ **Cos'è un VOIP?**\n"
            f"Si tratta di un numero virtuale. Su Telegram, spesso viene usato per evitare ban o creare account temporanei.\n\n"
            f"⚙️ **COME FUNZIONA?**\n"
            f"Mi basta essere aggiunto come amministratore in un gruppo per iniziare a bloccare automaticamente i VOIP.\n\n"
            f"Usa i pulsanti qui sotto per saperne di più:",
            reply_markup=keyboard
        )

@bot.on_message(filters.command("cancella"))
async def delete_bot_messages(client, message):
    chat_id = message.chat.id
    for msg_id in [msg[1] for msg in bot_messages if msg[0] == chat_id]:
        await client.delete_messages(chat_id, msg_id)
    bot_messages[:] = [msg for msg in bot_messages if msg[0] != chat_id]

async def auto_delete_messages():
    while True:
        await asyncio.sleep(7200)  # ogni 2 ore
        for chat_id, msg_id in bot_messages:
            await bot.delete_messages(chat_id, msg_id)
        bot_messages.clear()

bot.run()
