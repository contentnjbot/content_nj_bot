import os
from flask import Flask, request
import telebot
import json

TOKEN = os.environ["BOT_TOKEN"]
bot = telebot.TeleBot(TOKEN, parse_mode=None)

app = Flask(__name__)

# Webhook endpoint
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        json_str = request.get_data().decode("utf-8")
        data = json.loads(json_str)
        update = telebot.types.Update.de_json(data)
        bot.process_new_updates([update])
    except Exception as e:
        # فقط لتتبع الأخطاء في اللوقز
        print("Error in webhook:", e)
    return "OK", 200

# أمر /start للتجربة
@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "🚀 Bot is running!")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
