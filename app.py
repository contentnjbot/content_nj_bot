import os
import json
from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ——————————————————————————————
# 0) الإعداد الأساسي
# ——————————————————————————————
TOKEN = os.environ["BOT_TOKEN"]
bot = telebot.TeleBot(TOKEN, parse_mode=None)
app = Flask(__name__)

# تخزين بيانات المستخدمين مؤقتًا في الذاكرة
# مثال: {chat_id: {"accounts": [], "schedule": "", "mode": None}}
user_data = {}


def get_user(chat_id):
    """تأكد أن لكل مستخدم سجل جاهز."""
    if chat_id not in user_data:
        user_data[chat_id] = {
            "accounts": [],
            "schedule": "",
            "mode": None
        }
    return user_data[chat_id]


# ——————————————————————————————
# 1) مسار الويب هوك من تيليجرام
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
    name = message.from_user.first_name or "صديقي"
    chat_id = message.chat.id
    get_user(chat_id)  # تهيئة سجل المستخدم

    bot.reply_to(
        message,
        f"🚀 أهلاً {name}!\n\n"
        "أنا بوت بهندسة عبدالله — أساعدك تجمع ملخصات المحتوى من الحسابات اللي تهمّك.\n\n"
        "ابدأ بالأمر /setup لتهيئة الإعدادات."
    )


# ——————————————————————————————
# 3) أمر /help
# ——————————————————————————————
@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.reply_to(
        message,
        "📝 الأوامر المتاحة:\n"
        "/start - بدء البوت\n"
        "/setup - تهيئة الإعدادات من جديد\n"
        "/accounts - إضافة الحسابات التي تريد متابعتها\n"
        "/schedule - اختيار وقت استلام الملخص\n"
        "/summary - عرض ملخص تجريبي"
    )


# ——————————————————————————————
# 4) أمر /setup — إعادة ضبط إعدادات المستخدم
# ——————————————————————————————
@bot.message_handler(commands=['setup'])
def setup(message):
    chat_id = message.chat.id
    user_data[chat_id] = {
        "accounts": [],
        "schedule": "",
        "mode": None
    }

    bot.reply_to(
        message,
        "🔧 لنبدأ إعداد النظام من الصفر:\n"
        "1️⃣ أرسل /accounts لإضافة الحسابات.\n"
        "2️⃣ بعد الانتهاء أرسل /schedule لاختيار وقت الملخص.\n"
    )


# ——————————————————————————————
# 5) /accounts — إدخال روابط الحسابات واحدًا واحدًا
# ——————————————————————————————
@bot.message_handler(commands=['accounts'])
def accounts_cmd(message):
    chat_id = message.chat.id
    user = get_user(chat_id)
    user["accounts"] = []
    user["mode"] = "accounts"  # ندخل وضع إدخال الحسابات

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ تم", callback_data="accounts_done"))

    bot.send_message(
        chat_id,
        "👥 أرسل الآن روابط أو معرفات الحسابات واحداً واحداً.\n"
        "كل رسالة = حساب واحد.\n\n"
        "أمثلة:\n"
        "@user1\n"
        "https://instagram.com/user\n"
        "https://x.com/user\n\n"
        "بعد الانتهاء اضغط زر (تم ✅) أسفل الرسالة.",
        reply_markup=markup
    )


# استقبال أي رسالة نصية عندما يكون المستخدم في وضع إدخال الحسابات
@bot.message_handler(func=lambda msg: get_user(msg.chat.id).get("mode") == "accounts")
def collect_accounts(message):
    chat_id = message.chat.id
    user = get_user(chat_id)

    # تجاهل الأوامر (التي تبدأ بـ /)
    if message.text.startswith("/"):
        return

    account = message.text.strip()
    if account:
        user["accounts"].append(account)
        bot.reply_to(message, f"✔️ تم إضافة الحساب:\n{account}")


# زر "تم" بعد إدخال الحسابات
@bot.callback_query_handler(func=lambda call: call.data == "accounts_done")
def accounts_done(call):
    chat_id = call.message.chat.id
    user = get_user(chat_id)

    if not user["accounts"]:
        bot.answer_callback_query(
            call.id,
            "❗ أضف حساباً واحداً على الأقل قبل الضغط على (تم).",
            show_alert=True
        )
        return

    user["mode"] = None  # الخروج من وضع إدخال الحسابات

    text = "✨ تم حفظ الحسابات:\n"
    for acc in user["accounts"]:
        text += f"- {acc}\n"

    # إزالة الأزرار من الرسالة السابقة
    try:
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
    except Exception:
        pass

    bot.send_message(
        chat_id,
        text + "\nالآن أرسل /schedule لاختيار وقت استلام الملخّص."
    )


# ——————————————————————————————
# 6) /schedule — اختيار وقت استلام الملخّص بأزرار
# ——————————————————————————————
@bot.message_handler(commands=['schedule'])
def schedule_cmd(message):
    chat_id = message.chat.id
    user = get_user(chat_id)

    if not user["accounts"]:
        bot.reply_to(
            message,
            "❗ لم تُضِف أي حسابات بعد.\n"
            "أرسل /accounts أولاً لإضافة الحسابات."
        )
        return

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📩 الآن", callback_data="schedule_now"),
        InlineKeyboardButton("📅 يومي", callback_data="schedule_daily"),
        InlineKeyboardButton("🗓 أسبوعي", callback_data="schedule_weekly"),
        InlineKeyboardButton("📆 شهري", callback_data="schedule_monthly"),
    )

    bot.send_message(
        chat_id,
        "⏱ اختر طريقة استلام الملخص:",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("schedule_"))
def schedule_select(call):
    chat_id = call.message.chat.id
    user = get_user(chat_id)

    schedule_code = call.data.replace("schedule_", "")
    mapping = {
        "now": "الآن",
        "daily": "يومي",
        "weekly": "أسبوعي",
        "monthly": "شهري",
    }
    schedule_label = mapping.get(schedule_code, schedule_code)

    user["schedule"] = schedule_code

    # إزالة الأزرار من رسالة الجدولة
    try:
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
    except Exception:
        pass

    bot.send_message(
        chat_id,
        "🎉 تم حفظ إعداداتك!\n\n"
        "📌 الحسابات:\n" +
        "\n".join(f"- {a}" for a in user["accounts"]) +
        "\n\n"
        f"📌 طريقة استلام الملخص: {schedule_label}\n\n"
        "سيتم لاحقاً ربط النظام الذي يجلب المحتوى تلقائياً من هذه الحسابات "
        "وإرساله لك حسب الجدولة المختارة."
    )


# ——————————————————————————————
# 7) /summary — ملخص تجريبي
# ——————————————————————————————
@bot.message_handler(commands=['summary'])
def summary_cmd(message):
    chat_id = message.chat.id
    user = get_user(chat_id)

    accounts_text = (
        "\n".join(f"- {a}" for a in user["accounts"])
        if user["accounts"] else "لم تُضِف حسابات بعد."
    )
    schedule_text = user["schedule"] or "لم يتم اختيار جدولة بعد."

    bot.reply_to(
        message,
        "📊 هذا مثال تجريبي للملخّص (سيُستبدل لاحقاً بملخص حقيقي من الحسابات):\n\n"
        f"الحسابات المسجّلة:\n{accounts_text}\n\n"
        f"نوع الجدولة: {schedule_text}\n\n"
        "مثال محتوى:\n"
        "- X: تغريدة جديدة من أحد الحسابات.\n"
        "- Instagram: صورة جديدة.\n"
        "- YouTube: فيديو مدته 5 دقائق.\n\n"
        "✨ هذا مجرد نموذج — لاحقاً سنربطه بنظام يجمع المحتوى فعلياً."
    )


# ——————————————————————————————
# 8) تشغيل سيرفر Flask
# ——————————————————————————————
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
