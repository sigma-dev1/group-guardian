from pyrogram import Client, filters
import re
import config
from datetime import datetime, timedelta

slangf = 'slang_words.txt'
with open(slangf, 'r') as f:
    slang_words = set(line.strip().lower() for line in f)

Bot = Client(
    "group_guardian",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH
)

# Dictionary to store the last message time for each user
last_message_time = {}

@Bot.on_message(filters.private & filters.command("start"))
async def start(bot, update):
    await update.reply("""Hi there! I'm the Telegram Group Guardian bot. I'm here to help you keep your group clean and safe for everyone. Here are the main features I offer:

• **Word Slagging:** I can detect and remove inappropriate language messages in your group. 

• **Spam Detection:** I can detect and warn users who send duplicate messages within 10 minutes.

To get started, simply add me to your Telegram group and promote me to admin.

Thanks for using Telegram Group Guardian! Let's keep your group safe and respectful. Powered by @NACBOTS""")

@Bot.on_message(filters.group & filters.text)
async def slang(bot, message):
    sender = await Bot.get_chat_member(message.chat.id, message.from_user.id)
    isadmin = sender.privileges
    if not isadmin:
        sentence = message.text
        sent = re.sub(r'\W+', ' ', sentence)
        isslang = False
        for word in sent.split():
            if word.lower() in slang_words:
                isslang = True
                await message.delete()
                sentence = sentence.replace(word, f'||{word}||')
        if isslang:
            name = message.from_user.first_name
            msgtxt = f"""{name}, your message has been deleted due to the presence of inappropriate language. Here is a censored version of your message:
            
{sentence}
            """
            await message.reply(msgtxt)

@Bot.on_message(filters.group & filters.text)
async def spam_detection(bot, message):
    user_id = message.from_user.id
    current_time = datetime.now()

    if user_id in last_message_time:
        last_time = last_message_time[user_id]
        if current_time - last_time < timedelta(minutes=10):
            await message.reply(f"{message.from_user.first_name}, you are sending duplicate messages. Please refrain from spamming.")
            return

    last_message_time[user_id] = current_time

Bot.run()
