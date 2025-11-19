import os
import telebot
from flask import Flask

TOKEN = os.environ["BOT_TOKEN"]
bot = telebot.TeleBot(TOKEN)

# Dummy web server for Fly.io health checks
server = Flask(__name__)

@server.route('/')
def home():
    return "Bot is running!", 200

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "Bot is running! 🚀")

if __name__ == "__main__":
    # Run telegram bot
    import threading
    threading.Thread(target=lambda: bot.infinity_polling()).start()

    # Run dummy web server so Fly.io doesn't kill the app
    port = int(os.environ.get("PORT", 8080))
    server.run(host="0.0.0.0", port=port)
