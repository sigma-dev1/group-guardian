from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
import config
import logging
from datetime import datetime, timedelta
import asyncio
import re

# Configurazione del logging
logging.basicConfig(level=logging.INFO)

Bot = Client(
    "group_guardian",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH
)

# Dizionari per memorizzare lo stato di helper e moderatori
helpers = {}
moderators = {}

# Variabili per tenere traccia dello stato del gruppo
group_closed = False

# Il tuo ID utente e username
OWNER_ID = 6849853752

@Bot.on_message(filters.private & filters.command("start"))
async def start(bot, message):
    try:
        if message.from_user.id == OWNER_ID:
            await message.reply("Ciao! Sono il bot Telegram Group Guardian, creato per SkyNetwork per la gestione dei gruppi. Questo bot è utilizzabile solo dallo staff di SkyNetwork.")
        else:
            await message.reply("Questo bot è privato e può essere utilizzato solo dal proprietario.")
    except Exception as e:
        logging.error(f"Errore nel comando start: {e}")

@Bot.on_message(filters.group & filters.command("mod"))
async def promote_mod(bot, message):
    try:
        if message.from_user.id == OWNER_ID:
            if len(message.command) > 1:
                identifier = message.command[1]
                if identifier.isdigit():
                    user_id = int(identifier)
                else:
                    user = await bot.get_users(identifier)
                    user_id = user.id
                moderators[user_id] = True
                await message.reply(f"⭐ {user.first_name} è stato promosso a moderatore!")
            else:
                await message.reply("Per favore fornisci un username o un ID dell'utente che vuoi promuovere.")
        else:
            await message.reply("Non sei autorizzato a usare questo comando.")
    except Exception as e:
        logging.error(f"Errore nel comando mod: {e}")

@Bot.on_message(filters.group & filters.command("pex"))
async def promote_helper(bot, message):
    try:
        if message.from_user.id == OWNER_ID:
            if len(message.command) > 1:
                identifier = message.command[1]
                if identifier.isdigit():
                    user_id = int(identifier)
                else:
                    user = await bot.get_users(identifier)
                    user_id = user.id
                helpers[user_id] = True
                await message.reply(f"⭐ {user.first_name} è stato promosso a helper!")
            else:
                await message.reply("Per favore fornisci un username o un ID dell'utente che vuoi promuovere.")
        else:
            await message.reply("Non sei autorizzato a usare questo comando.")
    except Exception as e:
        logging.error(f"Errore nel comando pex: {e}")

@Bot.on_message(filters.group & filters.command("cancella"))
async def delete_message(bot, message):
    try:
        if message.from_user.id == OWNER_ID or message.from_user.id in helpers or message.from_user.id in moderators:
            if message.reply_to_message:
                await message.reply_to_message.delete()
                await message.reply(f"Messaggio eliminato da {message.from_user.first_name}!")
            else:
                await message.reply("Per favore rispondi al messaggio che vuoi eliminare.")
        else:
            await message.reply("Non sei autorizzato a usare questo comando.")
    except Exception as e:
        logging.error(f"Errore nel comando cancella: {e}")

@Bot.on_message(filters.group & filters.command("silenzia"))
async def mute_user(bot, message):
    try:
        if message.from_user.id == OWNER_ID or message.from_user.id in helpers or message.from_user.id in moderators:
            if len(message.command) > 1:
                identifier = message.command[1]
                if identifier.isdigit():
                    user_id = int(identifier)
                else:
                    user = await bot.get_users(identifier)
                    user_id = user.id
                await bot.restrict_chat_member(
                    message.chat.id, 
                    user_id, 
                    permissions=ChatPermissions(
                        can_send_messages=False, 
                        can_send_media_messages=False, 
                        can_send_polls=False, 
                        can_send_other_messages=False, 
                        can_add_web_page_previews=False, 
                        can_change_info=False, 
                        can_invite_users=False, 
                        can_pin_messages=False
                    )
                )
                await message.reply(f"🔇 L'utente con ID {user_id} è stato silenziato permanentemente da {message.from_user.first_name}!")
            elif message.reply_to_message:
                user_id = message.reply_to_message.from_user.id
                await bot.restrict_chat_member(
                    message.chat.id, 
                    user_id, 
                    permissions=ChatPermissions(
                        can_send_messages=False, 
                        can_send_media_messages=False, 
                        can_send_polls=False, 
                        can_send_other_messages=False, 
                        can_add_web_page_previews=False, 
                        can_change_info=False, 
                        can_invite_users=False, 
                        can_pin_messages=False
                    )
                )
                await message.reply(f"🔇 {message.reply_to_message.from_user.first_name} è stato silenziato permanentemente da {message.from_user.first_name}!")
            else:
                await message.reply("Per favore fornisci un username, un ID o rispondi all'utente che vuoi silenziare.")
        else:
            await message.reply("Non sei autorizzato a usare questo comando.")
    except Exception as e:
        logging.error(f"Errore nel comando silenzia: {e}")

@Bot.on_message(filters.group & filters.command("block"))
async def block_user(bot, message):
    try:
        if message.from_user.id == OWNER_ID or message.from_user.id in moderators:
            if len(message.command) > 1:
                identifier = message.command[1]
                if identifier.isdigit():
                    user_id = int(identifier)
                else:
                    user = await bot.get_users(identifier)
                    user_id = user.id
                await bot.ban_chat_member(message.chat.id, user_id)
                await message.reply(f"🚫 L'utente con ID {user_id} è stato bloccato permanentemente da {message.from_user.first_name}!")
            elif message.reply_to_message:
                user_id = message.reply_to_message.from_user.id
                await bot.ban_chat_member(message.chat.id, user_id)
                await message.reply(f"🚫 {message.reply_to_message.from_user.first_name} è stato bloccato permanentemente da {message.from_user.first_name}!")
            else:
                await message.reply("Per favore fornisci un username, un ID o rispondi all'utente che vuoi bloccare.")
        else:
            await message.reply("Non sei autorizzato a usare questo comando.")
    except Exception as e:
        logging.error(f"Errore nel comando block: {e}")

@Bot.on_message(filters.group & filters.command("closed"))
async def close_group(bot, message):
    try:
        global group_closed
        if message.from_user.id == OWNER_ID:
            group_closed = True
            await message.reply("🔒 Il gruppo è stato chiuso manualmente. Nessun nuovo utente può unirsi.")
        else:
            await message.reply("Non sei autorizzato a usare questo comando.")
    except Exception as e:
        logging.error(f"Errore nel comando closed: {e}")

@Bot.on_message(filters.group & filters.command("open"))
async def open_group(bot, message):
    try:
        global group_closed
        if message.from_user.id == OWNER_ID:
            group_closed = False
            await message.reply("🔓 Il gruppo è stato aperto manualmente. I nuovi utenti possono unirsi.")
        else:
            await message.reply("Non sei autorizzato a usare questo comando.")
    except Exception as e:
        logging.error(f"Errore nel comando open: {e}")

@Bot.on_message(filters.new_chat_members)
async def handle_new_members(bot, message):
    try:
        global group_closed
        if group_closed:
            for new_member in message.new_chat_members:
                await bot.ban_chat_member(message.chat.id, new_member.id)
    except Exception as e:
        logging.error(f"Errore nel gestire i nuovi membri: {e}")

# Dizionario per tenere traccia del numero di messaggi inviati dagli utenti
user_message_count = {}

# Inizializza il bot
Bot = Client("my_bot")

# Dizionario per contare i messaggi degli utenti
user_message_count = {}

@Bot.on_message(filters.group)
async def check_message_count(bot, message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Inizializza il conteggio dei messaggi per l'utente se non esiste
    if user_id not in user_message_count:
        user_message_count[user_id] = 0

    # Incrementa il conteggio dei messaggi
    user_message_count[user_id] += 1

@Bot.on_message(filters.group & filters.entity(MessageEntity.URL))
async def mute_for_link(bot, message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Controlla se l'utente ha inviato meno di 150 messaggi
    if user_message_count.get(user_id, 0) < 150:
        # Muta l'utente per un minuto
        await bot.restrict_chat_member(
            chat_id,
            user_id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False
            ),
            until_date=datetime.now() + timedelta(minutes=1)
        )
        await message.reply(f"🔇 {message.from_user.first_name} è stato silenziato per un minuto per aver inviato un link senza aver inviato almeno 150 messaggi.")

        # Attendi un minuto e poi smuta l'utente
        await asyncio.sleep(60)
        await bot.restrict_chat_member(
            chat_id,
            user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=False,
                can_invite_users=True,
                can_pin_messages=True
            )
        )
        await bot.send_message(chat_id, f"🔊 {message.from_user.first_name} è stato smutato e può inviare messaggi di nuovo.")

# Avvia il bot
Bot.run()
