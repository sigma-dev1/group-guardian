from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup, Message
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
        message.reply_text(f"Benvenuto {new_member.first_name}! Per favore, verifica la tua posizione cliccando il bottone qui sotto.", reply_markup=keyboard)

# Funzione per gestire la verifica della posizione in privato
@Bot.on_callback_query(filters.regex(r"verify_(\d+)"))
def verify_position(client, callback_query):
    user_id = int(callback_query.data.split('_')[1])
    if callback_query.from_user.id == user_id:
        client.send_message(user_id, "Per favore, condividi la tua posizione cliccando il bottone qui sotto.")
        button = InlineKeyboardButton("Condividi Posizione", request_location=True)
        keyboard = InlineKeyboardMarkup([[button]])
        client.send_message(user_id, "Condividi Posizione", reply_markup=keyboard)

# Funzione per gestire la condivisione della posizione
@Bot.on_message(filters.location)
def check_position(client, message):
    user_id = message.from_user.id
    user_location = (message.location.latitude, message.location.longitude)
    previous_location = (52.5200, 13.4050)  # Sostituisci con la logica di controllo posizione reale

    if user_location == previous_location:
        client.send_message(user_id, "Verifica completata con successo.")
        client.restrict_chat_member(
            message.chat.id, 
            user_id, 
            ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
        )
    else:
        client.send_message(user_id, "Le coordinate non corrispondono. Sei stato bannato.")
        client.kick_chat_member(message.chat.id, user_id)

# Avvia il bot
Bot.run()
