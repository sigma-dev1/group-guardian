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

if name == "__main__":
    Bot.run()
