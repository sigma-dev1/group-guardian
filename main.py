import requests
import logging
from pyrogram import Client

# Configurazione del logging
logging.basicConfig(level=logging.INFO)

# Configurazione del bot
bot = Client(
    "group_guardian",
    bot_token="YOUR_TELEGRAM_BOT_TOKEN",
    api_id="YOUR_API_ID",
    api_hash="YOUR_API_HASH"
)

def get_ip():
    try:
        response = requests.get("https://api.ipify.org/?format=json")
        response.raise_for_status()
        data = response.json()
        return data["ip"]
    except requests.RequestException as e:
        logging.error("Errore nella richiesta dell'IP: %s", e)
        return None

@bot.on_message()
def main(client, message):
    ip_address = get_ip()
    if ip_address:
        logging.info("Il tuo IP è: %s", ip_address)
    else:
        logging.info("Impossibile ottenere l'IP.")

# Avvia il bot
bot.run()
