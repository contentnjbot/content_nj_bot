import os
from flask import Flask, request
import telebot

TOKEN = os.environ["BOT_TOKEN"]
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# Telegram webhook endpoint
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_data = request.get_json()
    if json_data:
        bot.process_new_updates([telebot.types.Update.de_json(json_data)])
    return "OK", 200

# test command
@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "🚀 Bot is running!")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
