from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
import config
import logging
from blocked_numbers import is_blocked_number  # Importa la funzione di controllo

# Configurazione del logging
logging.basicConfig(level=logging.INFO)

Bot = Client(
    "group_guardian",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH
)

GROUP_ID = -1002202385937

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
        message.reply_text(f"Benvenuto {new_member.first_name}! Per favore, completa la verifica cliccando il bottone qui sotto.", reply_markup=keyboard)

# Verifica del numero di telefono
@Bot.on_callback_query(filters.regex(r"verify_(\d+)"))
def verify_phone(client, callback_query):
    user_id = int(callback_query.data.split('_')[1])
    if callback_query.from_user.id == user_id:
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton("Condividi Numero di Telefono", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        client.send_message(user_id, "Per favore, condividi il tuo numero di telefono usando il bottone qui sotto.", reply_markup=keyboard)

@Bot.on_message(filters.contact)
def check_phone(client, message):
    user_id = message.from_user.id
    user_phone = message.contact.phone_number

    # Verifica se il numero è bloccato
    if is_blocked_number(user_phone):
        client.send_message(user_id, "Numero non valido. Sei stato bannato.")
        ban_user_from_group(client, GROUP_ID, user_id)
    else:
        client.send_message(user_id, "Verifica completata con successo.")
        client.restrict_chat_member(
            GROUP_ID, 
            user_id, 
            ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
        )

def ban_user_from_group(client, group_id, user_id):
    try:
        client.ban_chat_member(group_id, user_id)
    except Exception as e:
        logging.error(f"Errore nel bannare l'utente {user_id} nel gruppo {group_id}: {e}")

# Avvia il bot
Bot.run()
