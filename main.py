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

# Dizionari per memorizzare lo stato di helper e moderatori
helpers = {}
moderators = {}

# Variabili per tenere traccia dello stato del gruppo
group_closed = False
new_members = []

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
            await message.reply("🔓 Il gruppo è stato riaperto. Ora tutti possono unirsi.")
        else:
            await message.reply("Non sei autorizzato a usare questo comando.")
    except Exception as e:
        logging.error(f"Errore nel comando open: {e}")

@Bot.on_message(filters.group)
async def handle_messages(bot, message):
    try:
        global group_closed
        if group_closed:
            if not message.text:
                await message.delete()
            else:
                await asyncio.sleep(5)
                await message.delete()
                await bot.restrict_chat_member(
                    message.chat.id, 
                    message.from_user.id, 
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
                    until_date=datetime.now() + timedelta(hours=1)
                )
                await message.reply(f"🔇 {message.from_user.first_name} è stato silenziato per un'ora per aver inviato messaggi non consentiti.")
    except Exception as e:
        logging.error(f"Errore nel gestire i messaggi: {e}")

@Bot.on_message(filters.new_chat_members)
async def handle_new_members(bot, message):
    try:
        global group_closed, new_members
        new_members.extend([member.id for member in message.new_chat_members])
        
        if len(new_members) > 5:
            for member_id in new_members:
                await bot.ban_chat_member(message.chat.id, member_id)
            await message.reply("🚫 Sono stati bannati tutti i nuovi membri per evitare uno storm.")
            new_members.clear()
        else:
            for new_member in message.new_chat_members:
                await bot.ban_chat_member(message.chat.id, new_member.id)
                await message.reply(f"                await message.reply(f"🚫 {new_member.first_name} è stato bannato.")
    except Exception as e:
        logging.error(f"Errore nel gestire i nuovi membri: {e}")

Bot.run()
