from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
import config
import logging
from datetime import datetime

# Configurazione del logging
logging.basicConfig(level=logging.INFO)

Bot = Client(
    "group_guardian",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH
)

# Funzione per mutare i nuovi utenti
@Bot.on_message(filters.new_chat_members)
def welcome_and_mute(client, message):
    for new_member in message.new_chat_members:
        client.restrict_chat_member(
            message.chat.id, 
            new_member.id, 
            ChatPermissions(can_send_messages=False)
        )
        button = InlineKeyboardButton("Verifica", callback_data=f"verify_{new_member.id}")
        keyboard = InlineKeyboardMarkup([[button]])
        message.reply_text(f"Benvenuto {new_member.first_name}! Per favore, verifica il tuo IP cliccando il bottone qui sotto.", reply_markup=keyboard)

# Funzione per gestire la verifica IP
@Bot.on_callback_query(filters.regex(r"verify_(\d+)"))
def verify_ip(client, callback_query):
    user_id = int(callback_query.data.split('_')[1])
    if callback_query.from_user.id == user_id:
        # Chiedi di condividere l'IP (questo è un placeholder, dovresti integrare con la logica di raccolta IP)
        callback_query.message.edit_text("Per favore, condividi il tuo IP usando il bottone sotto.")
        button = InlineKeyboardButton("Condividi IP", callback_data=f"share_ip_{user_id}")
        keyboard = InlineKeyboardMarkup([[button]])
        callback_query.message.reply_text("Condividi IP", reply_markup=keyboard)

# Funzione per gestire la condivisione dell'IP
@Bot.on_callback_query(filters.regex(r"share_ip_(\d+)"))
def check_ip(client, callback_query):
    user_id = int(callback_query.data.split('_')[1])
    if callback_query.from_user.id == user_id:
        # Simula il processo di verifica IP (dovresti implementare la verifica reale)
        user_ip = "123.456.789.000"  # Sostituisci con il metodo di acquisizione IP reale
        previous_ip = "123.456.789.000"  # Sostituisci con la logica di controllo IP
        if user_ip == previous_ip:
            callback_query.message.edit_text("Verifica completata con successo.")
            client.restrict_chat_member(
                callback_query.message.chat.id, 
                user_id, 
                ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
            )
        else:
            callback_query.message.edit_text("IP non corrisponde. Utente bannato.")
            client.kick_chat_member(callback_query.message.chat.id, user_id)

# Avvia il bot
Bot.run()
