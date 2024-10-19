import requests
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
import config
import logging
import sqlite3

# Configurazione del logging
logging.basicConfig.level(logging.INFO)

Bot = Client(
    "group_guardian",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH
)

GROUP_ID = -1002202385937

# Connessione al database
conn = sqlite3.connect('user_ips.db')
c = conn.cursor()

# Funzione per ottenere gli IP raccolti da IPLogger
def get_iplogger_data():
    response = requests.get("https://iplogger.org/it/logger/n9MV452Fw0JF")
    response.raise_for_status()  # Controlla eventuali errori nella richiesta
    data = response.text
    return data

# Funzione per salvare l'IP nel database
def save_ip(user_id, ip_address):
    c.execute("INSERT OR REPLACE INTO ips (user_id, ip_address) VALUES (?, ?)", (user_id, ip_address))
    conn.commit()

# Funzione per confrontare gli IP
def is_duplicate_ip(ip_address):
    c.execute("SELECT * FROM ips WHERE ip_address=?", (ip_address,))
    return c.fetchone() is not None

# Funzione per mutare i nuovi utenti e inviare il link di verifica
@Bot.on_message(filters.new_chat_members)
def welcome_and_mute(client, message):
    for new_member in message.new_chat_members:
        client.restrict_chat_member(
            message.chat.id,
            new_member.id,
            ChatPermissions(can_send_messages=False)
        )
        iplogger_link = "https://iplogger.com/25uiV5"
        button = InlineKeyboardButton("Verifica", url=iplogger_link)
        keyboard = InlineKeyboardMarkup([[button]])
        message.reply_text(f"Benvenuto {new_member.first_name}! Per favore, completa la verifica cliccando il bottone qui sotto.", reply_markup=keyboard)

# Funzione per raccogliere e confrontare gli IP dagli IPLogger
@Bot.on_message(filters.text)
def check_ip(client, message):
    user_id = message.from_user.id

    # Raccogli gli IP dai dati di IPLogger
    iplogger_data = get_iplogger_data()

    for line in iplogger_data.splitlines():
        if "IP" in line:  # Supponiamo che ci sia "IP" per ogni voce di indirizzo IP
            ip_address = line.split(":")[1].strip()
            if is_duplicate_ip(ip_address):
                client.send_message(user_id, "Sei stato bannato per utilizzo di account multipli.")
                client.ban_chat_member(GROUP_ID, user_id)
            else:
                save_ip(user_id, ip_address)
                client.send_message(user_id, "Verifica completata con successo.")
                client.restrict_chat_member(
                    GROUP_ID,
                    user_id,
                    ChatPermissions(can_send_messages=True, can_send_media_messages=True, can send_other_messages=True, can add_web_page_previews=True)
                )
                break

# Avvia il bot
Bot.run()
