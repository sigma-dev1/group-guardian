from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
import config
import logging
from datetime import datetime, timedelta
import asyncio

# Configurazione del logging
logging.basicConfig(level=logging.INFO)

Bot = Client(
    "group_guardian",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH
)

# Dizionari per memorizzare lo stato di helper e moderatori per ogni gruppo
helpers = {}
moderators = {}
user_message_count = {}
new_user_count = {}
ban_active = {}

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
                if message.chat.id not in moderators:
                    moderators[message.chat.id] = {}
                moderators[message.chat.id][user_id] = True
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
                if message.chat.id not in helpers:
                    helpers[message.chat.id] = {}
                helpers[message.chat.id][user_id] = True
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
        if message.from_user.id == OWNER_ID or message.from_user.id in helpers.get(message.chat.id, {}) or message.from_user.id in moderators.get(message.chat.id, {}):
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
        if message.from_user.id == OWNER_ID or message.from_user.id in helpers.get(message.chat.id, {}) or message.from_user.id in moderators.get(message.chat.id, {}):
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
        if message.from_user.id == OWNER_ID or message.from_user.id in moderators.get(message.chat.id, {}):
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
            await message.reply("🔒 Il gruppo è stato chiuso manualmente. I nuovi utenti non possono unirsi.")
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

@Bot.on_message(filters.group & filters.new_chat_members)
async def handle_new_members(bot, message):
    try:
        chat_id = message.chat.id
        if chat_id not in new_user_count:
            new_user_count[chat_id] = 0
        new_user_count[chat_id] += len(message.new_chat_members)

        logging.info(f"Nuovi membri aggiunti. Conteggio attuale: {new_user_count[chat_id]}")

        if new_user_count[chat_id] > 15:
            if chat_id not in ban_active or not ban_active[chat_id]:
                ban_active[chat_id] = True
                await message.reply("🚫 Troppi utenti si sono uniti di fila. I nuovi utenti verranno bannati per 5 minuti.")
                
                # Bannare i nuovi utenti che si uniscono
                for new_member in message.new_chat_members:
                    await bot.ban_chat_member(chat_id, new_member.id)
                    logging.info(f"Utente {new_member.id} bannato.")
                
                # Disattivare il ban automatico dopo 5 minuti
                await asyncio.sleep(300)
                ban_active[chat_id] = False
                new_user_count[chat_id] = 0
                await message.reply("🔓 Il ban automatico è stato disattivato.")
    except Exception as e:
        logging.error(f"Errore nel gestire i nuovi membri: {e}")

Bot.run()
