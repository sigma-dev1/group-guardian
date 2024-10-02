from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
import time
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

# Dizionario per tenere traccia dei messaggi inviati dagli utenti
user_messages = {}

# Il tuo ID utente e username
OWNER_ID = 6849853752
OWNER_USERNAME = "rifiutoatomico"

@Bot.on_message(filters.private & filters.command("start"))
async def start(bot, message):
    if message.from_user.id == OWNER_ID:
        await message.reply("Ciao! Sono il bot Telegram Group Guardian, creato per SkyNetwork per la gestione dei gruppi. Questo bot è utilizzabile solo dallo staff di SkyNetwork.")
    else:
        await message.reply("Questo bot è privato e può essere utilizzato solo dal proprietario.")

@Bot.on_message(filters.group & filters.command("mod"))
async def promote_mod(bot, message):
    if message.from_user.id == OWNER_ID:
        if len(message.command) > 1:
            identifier = message.command[1]
            if identifier.isdigit():
                user_id = int(identifier)
            else:
                user = await bot.get_users(identifier)
                user_id = user.id
            await bot.promote_chat_member(
                message.chat.id, 
                user_id, 
                can_change_info=True,
                can_delete_messages=True,
                can_restrict_members=True,
                can_pin_messages=True,
                can_promote_members=True
            )
            await message.reply(f"⭐ {user.first_name} è stato promosso a moderatore!")
        else:
            await message.reply("Per favore fornisci un username o un ID dell'utente che vuoi promuovere.")
    else:
        await message.reply("Non sei autorizzato a usare questo comando.")

@Bot.on_message(filters.group & filters.command("cancella"))
async def delete_message(bot, message):
    if message.from_user.id == OWNER_ID or message.from_user.id in helpers or message.from_user.id in moderators:
        if message.reply_to_message:
            await message.reply_to_message.delete()
            await message.reply(f"Messaggio eliminato da {message.from_user.first_name}!")
        else:
            await message.reply("Per favore rispondi al messaggio che vuoi eliminare.")
    else:
        await message.reply("Non sei autorizzato a usare questo comando.")

@Bot.on_message(filters.group & filters.command("silenzia"))
async def mute_user(bot, message):
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
                    can add_web_page_previews=False, 
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
                    can add_web_page_previews=False, 
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

@Bot.on_message(filters.group & filters.command("espelli"))
async def kick_user(bot, message):
    if message.from_user.id == OWNER_ID or message.from_user.id in moderators:
        if len(message.command) > 1:
            identifier = message.command[1]
            if identifier.isdigit():
                user_id = int(identifier)
            else:
                user = await bot.get_users(identifier)
                user_id = user.id
            await bot.kick_chat_member(message.chat.id, user_id)
            await message.reply(f"🚫 L'utente con ID {user_id} è stato espulso permanentemente da {message.from_user.first_name}!")
        elif message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            await bot.kick_chat_member(message.chat.id, user_id)
            await message.reply(f"🚫 {message.reply_to_message.from_user.first_name} è stato espulso permanentemente da {message.from_user.first_name}!")
        else:
            await message.reply("Per favore fornisci un username, un ID o rispondi all'utente che vuoi espellere.")
    else:
        await message.reply("Non sei autorizzato a usare questo comando.")

@Bot.on_message(filters.text & filters.group)
async def antispam(bot, message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text

    # Inizializza il dizionario per l'utente se non esiste
    if user_id not in user_messages:
        user_messages[user_id] = []

    # Aggiungi il messaggio corrente con il timestamp
    user_messages[user_id].append((text, time.time()))

    # Filtra i messaggi vecchi più di 10 minuti
    user_messages[user_id] = [(msg, timestamp) for msg, timestamp in user_messages[user_id] if time.time() - timestamp < 600]

    # Conta i messaggi identici inviati negli ultimi 10 minuti
    identical_messages = [msg for msg, timestamp in user_messages[user_id] if msg == text]

    if len(identical_messages) > 3 or len(text) > 400:
        await bot.restrict_chat_member(
            chat_id, 
            user_id, 
            ChatPermissions(can_send_messages=False), 
            until_date=int(time.time() + 43200)  # 12 ore
        )
        await message.reply(f"🔇 {message.from_user.first_name} è stato silenziato per 12 ore per spam.")
        await bot.send_message(chat_id, f"🔇 {message.from_user.first_name} è stato silenziato per 12 ore per spam.")
        
        # Elimina i messaggi di spam
        for msg, timestamp in user_messages[user_id]:
            if msg == text:
                await bot.delete_messages(chat_id, message.message_id)

if __name__ == "__main__":
    logging.info("Starting bot...")
    Bot.run()
