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
        button = InlineKeyboardButton("Verifica", callback_data=f"verify_{new_member.id}")
        keyboard = InlineKeyboardMarkup([[button]])
        message.reply_text(f"Benvenuto {new_member.first_name}! Per favore, completa la verifica cliccando il bottone qui sotto.", reply_markup=keyboard)

# Verifica del numero di telefono
@Bot.on_callback_query(filters.regex(r"verify_(\d+)"))
def verify_phone(client, callback_query):
    user_id = int(callback_query.data.split('_')[1])
    if callback_query.from_user.id == user_id:
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton("Condividi Numero di Telefono", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        client.send_message(user_id, "Per favore, condividi il tuo numero di telefono usando il bottone qui sotto.", reply_markup=keyboard)

@Bot.on_message(filters.contact)
def check_phone(client, message):
    user_id = message.from_user.id
    user_phone = message.contact.phone_number

    # Lista dei prefissi da bannare, eccetto +39
    banned_prefixes = [
        "+1", "+20", "+211", "+212", "+213", "+216", "+218", "+220", "+221", "+222", "+223", "+224", "+225",
        "+226", "+227", "+228", "+229", "+230", "+231", "+232", "+233", "+234", "+235", "+236", "+237", "+238",
        "+239", "+240", "+241", "+242", "+243", "+244", "+245", "+246", "+247", "+248", "+249", "+250", "+251",
        "+252", "+253", "+254", "+255", "+256", "+257", "+258", "+260", "+261", "+262", "+263", "+264", "+265",
        "+266", "+267", "+268", "+269", "+27", "+290", "+291", "+297", "+298", "+299", "+30", "+31", "+32", "+33",
        "+34", "+350", "+351", "+352", "+353", "+354", "+355", "+356", "+357", "+358", "+359", "+36", "+37", "+370",
        "+371", "+372", "+373", "+374", "+375", "+376", "+377", "+378", "+380", "+381", "+382", "+383", "+385", "+386",
        "+387", "+389", "+40", "+41", "+420", "+421", "+422", "+423", "+43", "+44", "+45", "+46", "+47", "+48",
        "+49", "+500", "+501", "+502", "+503", "+504", "+505", "+506", "+507", "+508", "+509", "+51", "+52", "+53", "+54",
        "+55", "+56", "+57", "+58", "+590", "+591", "+592", "+593", "+594", "+595", "+596", "+597", "+598", "+599", "+60",
        "+61", "+62", "+63", "+64", "+65", "+66", "+670", "+671", "+672", "+673", "+674", "+675", "+676", "+677", "+678",
        "+679", "+680", "+681", "+682", "+683", "+684", "+685", "+686", "+687", "+688", "+689", "+690", "+691", "+692",
        "+7", "+81", "+82", "+84", "+850", "+852", "+853", "+855", "+856", "+86", "+870", "+871", "+872", "+873", "+874",
        "+875", "+876", "+877", "+878", "+880", "+881", "+882", "+883", "+886", "+888", "+90", "+91", "+92", "+93", "+94",
        "+95", "+960", "+961", "+962", "+963", "+964", "+965", "+966", "+967", "+968", "+970", "+971", "+972", "+973",
        "+974", "+975", "+976", "+977", "+979", "+98", "+991", "+992", "+993", "+994", "+995", "+996", "+998", "+999"
    ]

    if user_phone.startswith("+39") and not user_phone.startswith("+39371"):
        client.send_message(user_id, "Verifica completata con successo.")
        client.restrict_chat_member(
            GROUP_ID, 
            user_id, 
            ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
        )
    elif any(user_phone.startswith(prefix) for prefix in banned_prefixes):
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
