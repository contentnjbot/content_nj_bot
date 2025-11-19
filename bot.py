import os
import telebot

TOKEN = os.environ["BOT_TOKEN"]
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "Bot is running! 🚀")

if __name__ == "__main__":
    bot.infinity_polling(timeout=30, long_polling_timeout=30)
