#!/usr/bin/env python3

import telebot
import logging
import os
import sys
import base64
from openai import OpenAI

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Read the bot token from the environment
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

# Initialize the OpenAI client
client = OpenAI()

# Funktion zum Encodieren des Bildes
def encode_image(image_file):
    return base64.b64encode(image_file).decode('utf-8')

# Handler für das Empfangen von Fotos
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        messages=[
            {"role": "system", "content": "Du bist \"Be My AI\", ein natürliches Sprachmodell welches gegebene Bilder so detailliert und präzise wie nur möglich für blinde Menschen beschreibt."},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encode_image(downloaded_file)}"
                        },
                    }
                ]
            }
        ]

        # Call the OpenAI API with the base64-encoded image
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=4096,
        )

        # Antwort an den Benutzer senden
        bot.reply_to(message, response.choices[0].message.content)

    except Exception as e:
        bot.reply_to(message, f"Ein Fehler ist aufgetreten: {e}")

def main():
    # Starte den Bot
    logging.info("Starting bot polling...")
    bot.polling()

if __name__ == '__main__':
    main()

