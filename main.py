import requests
import logging
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
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

# Memoria per gli IP
ip_memory = {}

# Funzione per ottenere l'IP e la geolocalizzazione
def get_ip_and_location():
    try:
        response = requests.get("https://ipapi.co/json")
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
        button = InlineKeyboardButton(text="Verifica", callback_data="verifica")
        keyboard = InlineKeyboardMarkup([[button]])
        await message.reply_text(f"Benvenuto {new_member.first_name}! Per favore, completa la verifica cliccando il bottone qui sotto.", reply_markup=keyboard)

@bot.on_callback_query(filters.regex(r"verifica"))
async def verifica_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    logging.info("Pulsante di verifica cliccato dall'utente %s", user_id)
    
    ip_address, country_code = get_ip_and_location()
    if ip_address:
        logging.info("IP dell'utente: %s, Codice Paese: %s", ip_address, country_code)
        
        if country_code != "IT":
            await client.kick_chat_member(GROUP_ID, user_id, until_date=int(time.time() + 5))
            await client.send_message(GROUP_ID, f"L'utente {user_id} ha utilizzato un IP non italiano e non ha passato la verifica.")
        else:
            duplicate_users = is_duplicate_ip(ip_address)
            if duplicate_users:
                logging.info("IP %s duplicato per l'utente %s", ip_address, user_id)
                for duplicate_user_id in duplicate_users:
                    await client.ban_chat_member(GROUP_ID, int(duplicate_user_id))
                await client.ban_chat_member(GROUP_ID, user_id)
                await client.send_message(GROUP_ID, f"Verifica fallita per gli utenti {', '.join(duplicate_users)} e {user_id}. Sono stati bannati per utilizzo di account multipli.")
            else:
                ip_memory[user_id] = ip_address
                await client.send_message(GROUP_ID, f"Verifica completata con successo per l'utente {user_id}.")
                await client.restrict_chat_member(
                    GROUP_ID,
                    user_id,
                    ChatPermissions(
                        can_send_messages=True,
                        can send media messages=True,
                        can send other messages=True,
                        can add web page previews=True
                    )
                )
    else:
        await client.send_message(GROUP_ID, f"Errore nella verifica dell'IP per l'utente {user_id}. Riprova più tardi.")

# Avvia il bot
bot.run()
