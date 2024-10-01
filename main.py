from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
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

# Dizionario per memorizzare lo stato di helper e moderatori
helpers = {}
moderators = {}

# Il tuo ID utente e username
OWNER_ID = 6849853752
OWNER_USERNAME = "rifiutoatomico"

@Bot.on_message(filters.private & filters.command("start"))
async def start(bot, message):
    logging.info(f"Received /start command from {message.from_user.id}")
    if message.from_user.id == OWNER_ID:
        await message.reply("""Ciao! Sono il bot Telegram Group Guardian. Sono qui per aiutarti a mantenere il tuo gruppo pulito e sicuro per tutti. Ecco le principali funzionalità che offro:

• **Comandi per Helper:** Gli utenti possono eliminare messaggi e silenziare altri utilizzando i comandi del bot.

Per iniziare, aggiungimi semplicemente al tuo gruppo Telegram e promuovimi ad admin.

Grazie per aver utilizzato Telegram Group Guardian! Manteniamo il tuo gruppo sicuro e rispettoso. Powered by @NACBOTS""")
    else:
        await message.reply("Questo bot è privato e può essere utilizzato solo dal proprietario.")

@Bot.on_message(filters.group & filters.command("pex"))
async def promote_helper(bot, message):
    logging.info(f"Received /pex command from {message.from_user.id} in chat {message.chat.id}")
    if message.from_user.id == OWNER_ID or message.from_user.username == OWNER_USERNAME:
        if len(message.command) > 1:
            username = message.command[1].lstrip('@')
            user = await bot.get_users(username)
            if "mod" in message.command:
                moderators[user.id] = message.chat.id
                await message.reply(f"{user.first_name} è stato promosso a moderatore in questo gruppo!")
            else:
                helpers[user.id] = message.chat.id
                await message.reply(f"{user.first_name} è stato promosso a helper in questo gruppo!")
        else:
            await message.reply("Per favore fornisci un username da promuovere.")
    else:
        await message.reply("Solo il proprietario del bot può promuovere helper o moderatori.")

@Bot.on_message(filters.group & filters.command("cancella"))
async def delete_message(bot, message):
    logging.info(f"Received /cancella command from {message.from_user.id} in chat {message.chat.id}")
    if message.from_user.id in helpers and helpers[message.from_user.id] == message.chat.id:
        if message.reply_to_message:
            await message.reply_to_message.delete()
            await message.reply(f"Messaggio eliminato da {message.from_user.first_name}!")
        else:
            await message.reply("Per favore rispondi al messaggio che vuoi eliminare.")
    else:
        await message.reply("Non sei autorizzato a usare questo comando.")

@Bot.on_message(filters.group & filters.command("silenzia"))
async def mute_user(bot, message):
    logging.info(f"Received /silenzia command from {message.from_user.id} in chat {message.chat.id}")
    if message.from_user.id in helpers and helpers[message.from_user.id] == message.chat.id:
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
            await message.reply(f"L'utente con ID {user_id} è stato silenziato permanentemente da {message.from_user.first_name}!")
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
            await message.reply(f"{message.reply_to_message.from_user.first_name} è stato silenziato permanentemente da {message.from_user.first_name}!")
        else:
            await message.reply("Per favore fornisci un username, un ID o rispondi all'utente che vuoi silenziare.")
    else:
        await message.reply("Non sei autorizzato a usare questo comando.")

@Bot.on_message(filters.group & filters.command("espelli"))
async def kick_user(bot, message):
    logging.info(f"Received /espelli command from {message.from_user.id} in chat {message.chat.id}")
    if message.from_user.id in moderators and moderators[message.from_user.id] == message.chat.id:
        if len(message.command) > 1:
            identifier = message.command[1]
            if identifier.isdigit():
                user_id = int(identifier)
            else:
                user = await bot.get_users(identifier)
                user_id = user.id
            await bot.kick_chat_member(message.chat.id, user_id)
            await message.reply(f"L'utente con ID {user_id} è stato espulso permanentemente da {message.from_user.first_name}!")
        elif message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            await bot.kick_chat_member(message.chat.id, user_id)
            await message.reply(f"{message.reply_to_message.from_user.first_name} è stato espulso permanentemente da {message.from_user.first_name}!")
        else:
            await message.reply("Per favore fornisci un username, un ID o rispondi all'utente che vuoi espellere.")
    else:
        await message.reply("Non sei autorizzato a usare questo comando.")

if __name__ == "__main__":
    logging.info("Starting bot...")
    Bot.run()
