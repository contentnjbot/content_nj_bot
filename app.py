import os
from flask import Flask, request
import telebot
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ——————————————————————————————
# 0) الإعداد الأساسي
# ——————————————————————————————
TOKEN = os.environ["BOT_TOKEN"]
bot = telebot.TeleBot(TOKEN, parse_mode=None)
app = Flask(__name__)

# تخزين البيانات المؤقتة
user_data = {}  # {chat_id: {"platforms": [], "accounts": [], "schedule": ""}}

# ——————————————————————————————
# 1) مسار الويب هوك
# ——————————————————————————————
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        json_str = request.get_data().decode("utf-8")
        data = json.loads(json_str)
        update = telebot.types.Update.de_json(data)
        bot.process_new_updates([update])
    except Exception as e:
        print("Webhook Error:", e)
    return "OK", 200

# ——————————————————————————————
# 2) أمر /start
# ——————————————————————————————
@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    bot.reply_to(
        message,
        f"🚀 أهلاً {name}!\n\n"
        "أنا بوت بهندسة عبدالله — مساعدك لتجميع ملخصات المحتوى من كل المنصات.\n"
        "ابدأ بالأمر /setup لبدء الإعدادات."
    )

# ——————————————————————————————
# 3) أمر /help
# ——————————————————————————————
@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.reply_to(
        message,
        "📝 قائمة الأوامر المتاحة:\n"
        "/start - بدء البوت\n"
        "/setup - إعداد النظام لأول مرة\n"
        "/platforms - اختيار المنصات\n"
        "/accounts - إضافة الحسابات\n"
        "/schedule - اختيار زمن الملخص\n"
        "/summary - استلام ملخص الآن\n"
        "/help - المساعدة"
    )

# ——————————————————————————————
# 4) أمر /setup
# ——————————————————————————————
@bot.message_handler(commands=['setup'])
def setup(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"platforms": [], "accounts": [], "schedule": ""}

    bot.reply_to(
        message,
        "🔧 لنبدأ إعداد النظام!\n"
        "1️⃣ أرسل /platforms لاختيار المنصات.\n"
        "2️⃣ ثم /accounts لإضافة الحسابات.\n"
        "3️⃣ ثم /schedule لتحديد وقت الملخص."
    )

# ——————————————————————————————
# 5) اختيار المنصات — بأزرار
# ——————————————————————————————
@bot.message_handler(commands=['platforms'])
def platforms(message):
    chat_id = message.chat.id
    user_data.setdefault(chat_id, {"platforms": [], "accounts": [], "schedule": ""})
    user_data[chat_id]["platforms"] = []

    markup = InlineKeyboardMarkup(row_width=2)
    platforms_buttons = [
        ("Twitter", "platform_Twitter"),
        ("Instagram", "platform_Instagram"),
        ("TikTok", "platform_TikTok"),
        ("Snapchat", "platform_Snapchat"),
        ("YouTube", "platform_YouTube"),
        ("Facebook", "platform_Facebook"),
        ("LinkedIn", "platform_LinkedIn"),
    ]

    for name, callback in platforms_buttons:
        markup.add(InlineKeyboardButton(name, callback_data=callback))

    markup.add(InlineKeyboardButton("✅ تم", callback_data="platform_done"))

    bot.send_message(
        chat_id,
        "📱 اختر المنصات التي تريد متابعتها:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("platform_"))
def select_platform(call):
    chat_id = call.message.chat.id
    platform = call.data.replace("platform_", "")

    if platform not in user_data[chat_id]["platforms"]:
        user_data[chat_id]["platforms"].append(platform)

    bot.answer_callback_query(call.id, f"✔️ تم اختيار {platform}")

@bot.callback_query_handler(func=lambda call: call.data == "platform_done")
def done_platforms(call):
    chat_id = call.message.chat.id
    selected = user_data[chat_id]["platforms"]

    if not selected:
        bot.answer_callback_query(call.id, "❗ اختر منصة واحدة على الأقل", show_alert=True)
        return

    text = "✨ تم حفظ المنصات:\n" + "\n".join([f"- {p}" for p in selected])
    bot.send_message(chat_id, text + "\n\nالآن أرسل /accounts لإضافة الحسابات.")

# ——————————————————————————————
# 6) إضافة الحسابات — كل حساب في رسالة — مع زر تم
# ——————————————————————————————
@bot.message_handler(commands=['accounts'])
def accounts(message):
    chat_id = message.chat.id
    user_data[chat_id]["accounts"] = []

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ تم", callback_data="accounts_done"))

    bot.send_message(
        chat_id,
        "👥 أرسل المعرفات واحداً واحداً.\n"
        "كل رسالة = حساب واحد.\n"
        "مثال:\n@user1\nhttps://instagram.com/user",
        reply_markup=markup
    )

@bot.message_handler(func=lambda msg: True)
def collect_accounts(message):
    chat_id = message.chat.id

    if "accounts" in user_data.get(chat_id, {}):
        if message.text.startswith("/"):
            return  # تجاهل الأوامر
        user_data[chat_id]["accounts"].append(message.text)
        bot.reply_to(message, f"✔️ تم إضافة الحساب: {message.text}")

@bot.callback_query_handler(func=lambda call: call.data == "accounts_done")
def done_accounts(call):
    chat_id = call.message.chat.id
    accounts_list = user_data[chat_id]["accounts"]

    if not accounts_list:
        bot.answer_callback_query(call.id, "❗ أضف حساباً واحداً على الأقل", show_alert=True)
        return

    bot.send_message(chat_id, "✨ تم حفظ الحسابات.\nالآن أرسل /schedule لاختيار وقت الملخص.")

# ——————————————————————————————
# 7) اختيار نوع الملخص — بأزرار
# ——————————————————————————————
@bot.message_handler(commands=['schedule'])
def schedule(message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📩 الآن", callback_data="schedule_now"),
        InlineKeyboardButton("📅 يومي", callback_data="schedule_daily"),
        InlineKeyboardButton("🗓 أسبوعي", callback_data="schedule_weekly"),
        InlineKeyboardButton("📆 شهري", callback_data="schedule_monthly"),
    )
    markup.add(InlineKeyboardButton("✅ تم", callback_data="schedule_done"))

    bot.send_message(
        message.chat.id,
        "⏱ اختر طريقة استلام الملخص:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("schedule_"))
def select_schedule(call):
    chat_id = call.message.chat.id
    schedule = call.data.replace("schedule_", "")

    user_data[chat_id]["schedule"] = schedule
    bot.answer_callback_query(call.id, f"✔️ تم اختيار {schedule}")

@bot.callback_query_handler(func=lambda call: call.data == "schedule_done")
def done_schedule(call):
    chat_id = call.message.chat.id
    schedule = user_data[chat_id]["schedule"]

    if schedule == "":
        bot.answer_callback_query(call.id, "❗ اختر طريقة واحدة على الأقل", show_alert=True)
        return

    bot.send_message(
        chat_id,
        f"🎉 تم حفظ الإعدادات بالكامل!\n"
        f"📌 المنصات: {', '.join(user_data[chat_id]['platforms'])}\n"
        f"📌 الحسابات: {', '.join(user_data[chat_id]['accounts'])}\n"
        f"📌 نوع الملخص: {schedule}\n\n"
        "سيتم تشغيل النظام قريباً حسب إعداداتك."
    )

# ——————————————————————————————
# 8) ملخص تجريبي
# ——————————————————————————————
@bot.message_handler(commands=['summary'])
def summary(message):
    bot.reply_to(
        message,
        "📊 مثال لملخص يومي:\n\n"
        "Twitter – محمد:\n- نشر تغريدة جديدة.\n\n"
        "Instagram – محمد:\n- نشر صورة جديدة.\n\n"
        "YouTube – محمد:\n- فيديو جديد: 4 دقائق.\n\n"
        "✨ (تجريبي — سيتم ربط النظام الحقيقي لاحقاً)"
    )

# ——————————————————————————————
# 9) تشغيل السيرفر
# ——————————————————————————————
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
