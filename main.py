import requests
import logging
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
import config
import time
import asyncio

# Configurazione del logging
logging.basicConfig(level=logging.INFO)

bot = Client(
    "group_guardian",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH
)

# Memoria per gli IP
ip_memory = {}

# Funzione per ottenere l'IP e la geolocalizzazione
async def get_ip_and_location():
    try:
        response = await asyncio.to_thread(requests.get, "https://ipapi.co/json")
        response.raise_for_status()
        data = response.json()
        return data["ip"], data["country_code"]
    except requests.RequestException as e:
        logging.error("Errore nella richiesta dell'IP: %s", e)
        return None, None

# Funzione per confrontare gli IP
def is_duplicate_ip(ip_address):
    return [user_id for user_id, ip in ip_memory.items() if ip == ip_address]

@bot.on_message(filters.new_chat_members)
async def welcome_and_mute(client, message):
    for new_member in message.new_chat_members:
        logging.info("Nuovo membro: %s", new_member.id)
        await client.restrict_chat_member(
            message.chat.id,
            new_member.id,
            ChatPermissions(can_send_messages=False)
        )
        verification_link = f"https://t.me/{client.me.username}?start=verifica_{new_member.id}"
        button = InlineKeyboardButton(text="✅ Verifica", url=verification_link)
        keyboard = InlineKeyboardMarkup([[button]])
        await message.reply_text(f"Benvenuto {new_member.first_name}! Per favore, completa la verifica cliccando il bottone qui sotto.", reply_markup=keyboard)

@bot.on_message(filters.regex(r"^/start verifica_\d+$"))
async def verifica_callback(client, message):
    user_id = int(message.text.split("_")[1])
    logging.info("Pulsante di verifica cliccato dall'utente %s", user_id)
    
    ip_address, country_code = await get_ip_and_location()
    if ip_address:
        logging.info("IP dell'utente: %s, Codice Paese: %s", ip_address, country_code)
        
        if country_code != "IT":
            await client.ban_chat_member(message.chat.id, user_id, until_date=int(time.time() + 5))
            await client.send_message(message.chat.id, f"L'utente {user_id} ha utilizzato un IP non italiano e non ha passato la verifica.")
            await client.send_message(user_id, "Hai utilizzato un IP non italiano e non hai passato la verifica.")
        else:
            duplicate_users = is_duplicate_ip(ip_address)
            if duplicate_users:
                logging.info("IP %s duplicato per l'utente %s", ip_address, user_id)
                for duplicate_user_id in duplicate_users:
                    await client.ban_chat_member(message.chat.id, int(duplicate_user_id))
                await client.ban_chat_member(message.chat.id, user_id)
                await client.send_message(message.chat.id, f"Verifica fallita per gli utenti {', '.join(duplicate_users)} e {user_id}. Sono stati bannati per utilizzo di account multipli.")
                await client.send_message(user_id, "Hai utilizzato un IP duplicato e non hai passato la verifica.")
            else:
                ip_memory[user_id] = ip_address
                confirmation_message = await client.send_message(message.chat.id, f"Verifica completata con successo per l'utente {user_id}.")
                await client.send_message(user_id, "Verifica completata con successo.")
                await client.restrict_chat_member(
                    message.chat.id,
                    user_id,
                    ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True
                    )
                )
                await asyncio.sleep(30)  # Aspetta 30 secondi prima di eliminare il messaggio di conferma
                await client.delete_messages(message.chat.id, confirmation_message.message_id)
    else:
        error_message = await client.send_message(message.chat.id, f"Errore nella verifica dell'IP per l'utente {user_id}. Riprova più tardi.")
        await client.send_message(user_id, "Errore nella verifica dell'IP. Riprova più tardi.")
        await asyncio.sleep(30)  # Aspetta 30 secondi prima di eliminare il messaggio di errore
        await client.delete_messages(message.chat.id, error_message.message_id)

@bot.on_message(filters.command("start"))
async def start(client, message):
    welcome_text = (
        "Ciao! Sono un bot anti-account multipli. "
        "Aggiungimi al tuo gruppo per proteggere dai VoIP!\n\n"
        "✅ Aggiungimi ad un gruppo\n"
        "📜 [Privacy Policy](https://t.me/PrivacyAndPolicyCn)"
    )
    await message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Aggiungi ad un gruppo", url=f"https://t.me/{client.me.username}?startgroup=true")],
        [InlineKeyboardButton("📜 Privacy Policy", url="https://t.me/PrivacyAndPolicyCn")]
    ]))

# Avvia il bot
bot.run()
