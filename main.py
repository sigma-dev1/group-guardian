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

AUTHORIZED_IDS = {7336875798, 343002941, 6849853752, 7082135434}
GROUP_IDS = [-1002202385937, -1001426643861, -1001509283453]  # Lista di gruppi
ip_memory = {}
unbanned_users = set()
verifica_tasks = {}
bot_messages = []

EUROPE_COUNTRY_CODES = ['AL', 'AD', 'AM', 'AT', 'AZ', 'BY', 'BE', 'BA', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'GE', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT', 'KZ', 'XK', 'LV', 'LI', 'LT', 'LU', 'MT', 'MD', 'MC', 'ME', 'NL', 'MK', 'NO', 'PL', 'PT', 'RO', 'SM', 'RS', 'SK', 'SI', 'ES', 'SE', 'CH', 'TR', 'UA', 'GB', 'VA']

def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return None

async def get_whois_info(ip):
    try:
        response = await asyncio.to_thread(requests.get, f"http://ip-api.com/json/{ip}")
        data = response.json()
        return data
    except Exception as e:
        logging.error(f"Errore nel recupero dei dati whois: {e}")
        return None

async def get_ip_and_location():
    ip = requests.get('https://icanhazip.com').text.strip()
    data = await get_whois_info(ip)
    return data["query"], data["countryCode"]

def is_duplicate_ip(ip_address):
    return [user_id for user_id, ip in ip_memory.items() if ip == ip_address]

async def ban_user(client, user_ids, reason):
    for group_id in GROUP_IDS:
        for user_id in user_ids:
            await client.ban_chat_member(group_id, user_id)
        unban_button = InlineKeyboardButton("🔓 Sblocca Utenti", callback_data=f"unban_{'_'.join(map(str, user_ids))}")
        unban_keyboard = InlineKeyboardMarkup([[unban_button]])
        ban_message = await client.send_message(group_id, reason, reply_markup=unban_keyboard)
        bot_messages.append(ban_message.id)

@bot.on_callback_query(filters.regex(r"unban_"))
async def unban_callback(client, callback_query):
    if callback_query.from_user.id not in AUTHORIZED_IDS:
        await callback_query.answer("Non sei autorizzato a sbloccare gli utenti.", show_alert=True)
        return

    user_ids = list(map(int, callback_query.data.split("_")[1:]))
    for group_id in GROUP_IDS:
        await unban_users(client, group_id, user_ids)

async def unban_users(client, chat_id, user_ids):
    for user_id in user_ids:
        await client.unban_chat_member(chat_id, user_id)
        if user_id not in unbanned_users:
            await client.send_message(chat_id, f"L'utente con ID {user_id} è stato sbloccato.")
        unbanned_users.add(user_id)

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
        welcome_message = await message.reply_text(f"Benvenuto {new_member.first_name}! Completa la verifica cliccando il bottone qui sotto.", reply_markup=keyboard)
        bot_messages.append(welcome_message.id)

        task = asyncio.create_task(timer(client, message.chat.id, new_member.id, welcome_message.id))
        verifica_tasks[new_member.id] = task

async def timer(client, chat_id, user_id, message_id):
    await asyncio.sleep(180)
    if user_id not in ip_memory and user_id not in unbanned_users:
        await ban_user(client, [user_id], f"L'utente {user_id} non ha passato la verifica ed è stato bannato.")
        await client.delete_messages(chat_id, [message_id])
        bot_messages.remove(message_id)

@bot.on_message(filters.regex(r"^/start verifica_\d+$"))
async def verifica_callback(client, message):
    user_id = int(message.text.split("_")[1])
    if user_id in verifica_tasks:
        verifica_tasks[user_id].cancel()

    ip_address, country_code = await get_ip_and_location()
    if ip_address:
        if country_code not in EUROPE_COUNTRY_CODES:
            await ban_user(client, [user_id], f"L'utente {user_id} non ha passato la verifica ed è stato bannato per provenienza estera.")
        else:
            duplicate_users = is_duplicate_ip(ip_address)
            if duplicate_users:
                reason = (
                    f"🛑 **Utenti VoIP rilevati** 🛑\n"
                    f"**Dati Primo VoIP**\n"
                    f"ID: {message.from_user.id}\n\n"
                    f"**Dati Secondo VoIP**\n"
                    f"ID: {duplicate_users[0]}\n"
                    f"⚠️ Questi utenti sono stati bannati per essere account multipli."
                )
                await ban_user(client, [user_id] + duplicate_users, reason)
            else:
                ip_memory[user_id] = ip_address
                confirmation_message = await client.send_message(message.chat.id, f"Verifica completata per {message.from_user.first_name}.")
                bot_messages.append(confirmation_message.id)
                await client.restrict_chat_member(
                    message.chat.id,
                    user_id,
                    ChatPermissions(can_send_messages=True, can_send_media_messages=True)
                )

@bot.on_message(filters.command("cancella"))
async def delete_bot_messages(client, message):
    if message.from_user.id not in AUTHORIZED_IDS:
        await message.reply_text("Non hai il permesso per usare questo comando.")
        return
    for msg_id in bot_messages:
        await client.delete_messages(message.chat.id, msg_id)
    bot_messages.clear()

async def auto_delete_messages():
    while True:
        await asyncio.sleep(7200)
        for group_id in GROUP_IDS:
            for msg_id in bot_messages:
                await bot.delete_messages(group_id, msg_id)
        bot_messages.clear()

bot.run()
