from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
import config

Bot = Client(
    "group_guardian",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH
)

# Dictionary to store helper and moderator status
helpers = {}
moderators = {}

# Your user ID and username
OWNER_ID = 6849853752
OWNER_USERNAME = "rifiutoatomico"
CO_OWNER_ID = 5318754238
CO_OWNER_USERNAME = "Aanubi"

@Bot.on_message(filters.private & filters.command("start"))
async def start(bot, update):
    await update.reply("""Hi there! I'm the Telegram Group Guardian bot. I'm here to help you keep your group clean and safe for everyone. Here are the main features I offer:

• **Helper Commands:** Users can delete messages and mute others using the bot commands.

To get started, simply add me to your Telegram group and promote me to admin.

Thanks for using Telegram Group Guardian! Let's keep your group safe and respectful. Powered by @NACBOTS""")

@Bot.on_message(filters.group & filters.command("pex"))
async def promote_helper(bot, message):
    if message.from_user.id in [OWNER_ID, CO_OWNER_ID] or message.from_user.username in [OWNER_USERNAME, CO_OWNER_USERNAME]:
        if len(message.command) > 1:
            username = message.command[1].lstrip('@')
            user = await bot.get_users(username)
            helpers[user.id] = True
            await message.reply(f"{user.first_name} has been promoted to helper!")
        else:
            await message.reply("Please provide a username to promote.")
    else:
        await message.reply("Only the bot owner and co-owner can promote helpers.")

@Bot.on_message(filters.group & filters.command("cancella"))
async def delete_message(bot, message):
    if message.from_user.id in helpers or message.from_user.id in moderators:
        if message.reply_to_message:
            await message.reply_to_message.delete()
            await message.reply(f"Message deleted by {message.from_user.first_name}!")
        else:
            await message.reply("Please reply to the message you want to delete.")
    else:
        await message.reply("You are not authorized to use this command.")

@Bot.on_message(filters.group & filters.command("silenzia"))
async def mute_user(bot, message):
    if message.from_user.id in helpers or message.from_user.id in moderators:
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
    if message.from_user.id in moderators:
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

@Bot.on_message(filters.group & filters.command("riavvia"))
async def restart_bot(bot, message):
    if message.from_user.id in [OWNER_ID, CO_OWNER_ID] or message.from_user.username in [OWNER_USERNAME, CO_OWNER_USERNAME]:
        await message.reply("Il bot si sta riavviando...")
        await bot.stop()
        await bot.start()
        await message.reply("Il bot è stato riavviato con successo!")
    else:
        await message.reply("Non sei autorizzato a usare questo comando.")

Bot.run()
