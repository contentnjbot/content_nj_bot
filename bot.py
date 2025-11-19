import os
from flask import Flask
import telebot

TOKEN = os.environ.get("BOT_TOKEN")  # مهم: سنضيفه كـ secret لاحقًا
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# نقطة استقبال أوامر تيليجرام
@app.route("/" + TOKEN, methods=["POST"])
def webhook():
    json_updates = flask.request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_updates)
    bot.process_new_updates([update])
    return "OK", 200

# رسالة /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "تم تشغيل البوت بنجاح 🤖🔥")

# لتشغيل السيرفر
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
