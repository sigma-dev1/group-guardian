import requests
import logging
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
import config

# Configurazione del logging
logging.basicConfig(level=logging.INFO)

bot = Client(
    "group_guardian",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH
)

GROUP_ID = -1002202385937
LOG_CHANNEL_ID = -1002315055843  # ID del canale dove inviare gli IP

# Funzione per ottenere l'IP
def get_ip():
    try:
        response = requests.get("https://api.ipify.org/?format=json")
        response.raise_for_status()
        data = response.json()
        return data["ip"]
    except requests.RequestException as e:
        logging.error("Errore nella richiesta dell'IP: %s", e)
        return None

# Funzione per confrontare gli IP
def is_duplicate_ip(ip_address, log_messages):
    for message in log_messages:
        if ip_address in message['text']:
            return True
    return False

# Funzione per inviare l'IP al canale
async def log_ip(client, user_id, ip_address):
    await client.send_message(LOG_CHANNEL_ID, f"User ID: {user_id}, IP: {ip_address}")

# Funzione per ottenere i messaggi dal canale di log
async def get_log_messages(client):
    messages = []
    async for message in client.iter_history(LOG_CHANNEL_ID):
        messages.append(message)
    return messages

@bot.on_message(filters.command("getip"))
async def get_user_ip(client, message):
    user_id = message.from_user.id
    ip_address = get_ip()
    if ip_address:
        logging.info("IP dell'utente: %s", ip_address)
        
        # Ottiene i messaggi di log
        log_messages = await get_log_messages(client)
        
        if is_duplicate_ip(ip_address, log_messages):
            logging.info("IP %s duplicato per l'utente %s", ip_address, user_id)
            await client.send_message(GROUP_ID, f"L'utente {user_id} è stato bannato per utilizzo di account multipli.")
            await client.ban_chat_member(GROUP_ID, user_id)
        else:
            await log_ip(client, user_id, ip_address)
            await client.send_message(GROUP_ID, f"Verifica completata con successo per l'utente {user_id}.")
    else:
        await client.send_message(GROUP_ID, f"Errore nella verifica dell'IP per l'utente {user_id}. Riprova più tardi.")

# Avvia il bot
bot.run()
