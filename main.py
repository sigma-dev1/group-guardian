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
    "group_guardian",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH
)

# ID del gruppo specifico
GROUP_ID = -1002202385937

# Memoria per gli IP e gli utenti sbloccati
ip_memory = {}
unbanned_users = set()
verifica_tasks = {}
bot_messages = []

# Funzione per ottenere l'hostname
def get_hostname(ip):
    """Retrieve hostname for the given IP."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return None

# Funzione per ottenere il proprio IP esterno
def get_my_ip():
    """Retrieve the external IP address."""
    try:
        return requests.get('https://icanhazip.com').text.strip()
    except Exception as e:
        logging.error(f"Errore nel recupero dell'IP esterno: {e}")
        return None

# Funzione per ottenere i dati whois
async def get_whois_info(ip):
    """Retrieve whois data for the given IP."""
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

# Funzione per ottenere l'IP e la geolocalizzazione
async def get_ip_and_location():
    ip = get_my_ip()
    if ip:
        data = await get_whois_info(ip)
        if data:
            return data["query"], data["countryCode"]
    return None, None

# Funzione per confrontare gli IP
def is_duplicate_ip(ip_address):
    return [user_id for user_id, ip in ip_memory.items() if ip == ip_address]

# Funzione per bannare l'utente
async def ban_user(client, chat_id, user_id, reason):
    await client.ban_chat_member(chat_id, user_id)
    ban_message = await client.send_message(chat_id, reason)
    bot_messages.append(ban_message.id)
    # Aggiungi pulsante di sblocco
    unban_button = InlineKeyboardButton(text="🔓 Unbanna", callback_data=f"unban_{user_id}")
    unban_keyboard = InlineKeyboardMarkup([[unban_button]])
    unban_message = await client.send_message(chat_id, "Se questo utente è stato bannato per errore, clicca qui per sbloccarlo.", reply_markup=unban_keyboard)
    bot_messages.append(unban_message.id)

# Funzione per sbloccare l'utente
async def unban_user(client, chat_id, user_id):
    await client.unban_chat_member(chat_id, user_id)
    if user_id not in unbanned_users:
        await client.send_message(chat_id, f"{user_id} è stato sbloccato e non dovrà ripetere la verifica.")
    unbanned_users.add(user_id)

@bot.on_message(filters.new_chat_members)
async def welcome_and_mute(client, message):
    for new_member in message.new_chat_members:
        if new_member.id in unbanned_users:
            continue
        logging.info("Nuovo membro: %s", new_member.id)
        await client.restrict_chat_member(
            message.chat.id,
            new_member.id,
            ChatPermissions(can_send_messages=False)
        )
        verification_link = f"https://t.me/{client.me.username}?start=verifica_{new_member.id}"
        button = InlineKeyboardButton(text="✅ Verifica", url=verification_link)
        keyboard = InlineKeyboardMarkup([[button]])
        welcome_message = await message.reply_text(f"Benvenuto {new_member.first_name or new_member.username}! Per favore, completa la verifica cliccando il bottone qui sotto.", reply_markup=keyboard)
        bot_messages.append(welcome_message.id)
        
        task = asyncio.create_task(timer(client, message.chat.id, new_member.id, welcome_message.id))
        verifica_tasks[new_member.id] = task

async def timer(client, chat_id, user_id, message_id):
    await asyncio.sleep(180)  # Aspetta 3 minuti
    if user_id not in ip_memory and user_id not in unbanned_users:
        await ban_user(client, chat_id, user_id, f"{user_id} non ha passato la verifica ed è stato bannato.")
        await client.delete_messages(chat_id, [message_id])
        bot_messages.remove(message_id)

@bot.on_message(filters.regex(r"^/start verifica_\d+$"))
async def verifica_callback(client, message):
    user_id = int(message.text.split("_")[1])
    logging.info("Pulsante di verifica cliccato dall'utente %s", user_id)
    
    if user_id in verifica_tasks:
        verifica_tasks[user_id].cancel()
        
    ip_address, country_code = await get_ip_and_location()
    if ip_address:
        logging.info("IP dell'utente: %s, Codice Paese: %s", ip_address, country_code)
        
        if country_code != "IT":
            await ban_user(client, GROUP_ID, user_id, f"{message.from_user.first_name or message.from_user.username} non ha passato la verifica ed è stato bannato per essere un account multiplo.")
        else:
            duplicate_users = is_duplicate_ip(ip_address)
            if duplicate_users:
                for duplicate_user_id in duplicate_users:
                    await ban_user(client, GROUP_ID, int(duplicate_user_id), "Account multiplo rilevato.")
                await ban_user(client, GROUP_ID, user_id, f"{message.from_user.first_name or message.from_user.username} non ha passato la verifica ed è stato bannato per essere un account multiplo.")
            else:
                ip_memory[user_id] = ip_address
                confirmation_message = await client.send_message(GROUP_ID, f"Verifica completata con successo per {message.from_user.first_name or message.from_user.username}.")
                bot_messages.append(confirmation_message.id)
                await client.send_message(user_id, "Verifica completata con successo.")
                await client.restrict_chat_member(
                    GROUP_ID,
                    user_id,
                    ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can send other messages,
                        can add web page previews
                    )
                )

@bot.on_callback_query(filters.regex(r"unban_"))
async def unban_callback(client, callback_query):
    user_id = int(callback_query.data.split("_")[1])
    chat_id = callback_query.message.chat.id
    await unban_user(client, chat_id, user_id)
    if user_id not in unbanned_users:
        await client.send_message(chat_id, f"{user_id} è stato sbloccato e non dovrà ripetere la verifica.")
    bot_messages.append(callback_query.message.id)

# Comando per cancellare i messaggi del bot
@bot.on_message(filters.command("cancella"))
async def delete_bot_messages(client, message):
    for msg_id in bot_messages:
        await client.delete_messages(message.chat.id, msg_id)
    bot_messages.clear()

# Funzione per cancellare i messaggi del bot ogni 2 ore
async def auto_delete_messages():
    while True:
        await asyncio.sleep(7200)  # 2 ore
        for msg_id in bot_messages:
            await bot.delete_messages(GROUP_ID, msg_id)
        bot_messages.clear()

# Avvia il task di auto-cancellazione
bot.add_handler(auto_delete_messages())

# Avvia il bot
bot.run()
