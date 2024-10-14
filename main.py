from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
import config
import logging

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
        button = InlineKeyboardButton("Prima Verifica", callback_data=f"verify_first_{new_member.id}")
        keyboard = InlineKeyboardMarkup([[button]])
        message.reply_text(f"Benvenuto {new_member.first_name}! Per favore, completa la prima verifica cliccando il bottone qui sotto.", reply_markup=keyboard)

# Prima verifica: controllo se il numero non è estero
@Bot.on_callback_query(filters.regex(r"verify_first_(\d+)"))
def first_verification(client, callback_query):
    user_id = int(callback_query.data.split('_')[2])
    if callback_query.from_user.id == user_id:
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton("Condividi Numero di Telefono", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        client.send_message(user_id, "Per favore, condividi il tuo numero di telefono usando il bottone qui sotto.", reply_markup=keyboard)

# Funzione per gestire la condivisione del numero di telefono per la prima verifica
@Bot.on_message(filters.contact)
def first_check_phone(client, message):
    user_id = message.from_user.id
    user_phone = message.contact.phone_number

    if user_phone.startswith("+39"):
        button = InlineKeyboardButton("Verifica Finale", callback_data=f"verify_final_{user_id}")
        keyboard = InlineKeyboardMarkup([[button]])
        client.send_message(user_id, "Prima verifica completata con successo. Ora clicca su 'Verifica Finale' per completare.", reply_markup=keyboard)
    else:
        client.send_message(user_id, "Numero internazionale non valido. Sei stato bannato.")
        ban_user_from_all_groups(client, user_id)

# Seconda verifica: controllo che il numero non sia +39371
@Bot.on_callback_query(filters.regex(r"verify_final_(\d+)"))
def final_verification(client, callback_query):
    user_id = int(callback_query.data.split('_')[2])
    if callback_query.from_user.id == user_id:
        user_phone = client.get_chat_member(callback_query.message.chat.id, user_id).user.phone_number

        if user_phone.startswith("+39371"):
            client.send_message(user_id, "Numero non valido. Sei stato bannato.")
            ban_user_from_all_groups(client, user_id)
        else:
            client.send_message(user_id, "Verifica completata con successo.")
            client.restrict_chat_member(
                GROUP_ID, 
                user_id, 
                ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
            )

def ban_user_from_all_groups(client, user_id):
    try:
        for dialog in client.iter_dialogs():
            if dialog.chat.type in ["group", "supergroup"]:
                client.ban_chat_member(dialog.chat.id, user_id)
    except Exception as e:
        logging.error(f"Errore nel gestire i ban: {e}")

# Avvia il bot
Bot.run()
