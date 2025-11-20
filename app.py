import os
import json
from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Firebase Admin
import firebase_admin
from firebase_admin import credentials, db

# ——————————————————————————————
# 0) الإعداد الأساسي للبوت + Firebase
# ——————————————————————————————

# توكن البوت من Secrets في Fly.io
TOKEN = os.environ["BOT_TOKEN"]
bot = telebot.TeleBot(TOKEN, parse_mode=None)

app = Flask(__name__)

# مفتاح Firebase من متغير البيئة FIREBASE_KEY (حطيناه في Secrets)
FIREBASE_KEY = os.environ.get("FIREBASE_KEY")

if not FIREBASE_KEY:
    raise RuntimeError("⚠️ متغير البيئة FIREBASE_KEY غير موجود. تأكد من إضافته في Fly.io Secrets.")

# تحويل النص JSON إلى dict ثم تهيئة Firebase
cred_info = json.loads(FIREBASE_KEY)
cred = credentials.Certificate(cred_info)

firebase_admin.initialize_app(cred, {
    "databaseURL": "https://content-summary-bot-default-rtdb.firebaseio.com/"
})


# ——————————————————————————————
# دوال مساعدة للتعامل مع المستخدمين في Firebase
# ——————————————————————————————

def default_user(chat_id: int, name: str = None) -> dict:
    """قالب البيانات الافتراضية للمستخدم."""
    return {
        "name": name or "",
        "accounts": [],   # قائمة الحسابات التي أضافها المستخدم
        "schedule": "",   # now / daily / weekly / monthly
        "mode": None      # مثلاً: "accounts" عندما يكون في وضع إدخال الحسابات
    }


def get_user_ref(chat_id: int):
    """إرجاع Reference لموقع المستخدم في قاعدة البيانات."""
    return db.reference(f"users/{chat_id}")


def get_user(chat_id: int) -> dict:
    """
    قراءة بيانات المستخدم من Firebase.
    لو ما كان له بيانات، نرجع له قالب افتراضي (بدون حفظ).
    """
    ref = get_user_ref(chat_id)
    data = ref.get()
    if data is None:
        data = default_user(chat_id)
    return data


def save_user(chat_id: int, data: dict):
    """حفظ بيانات المستخدم في Firebase."""
    ref = get_user_ref(chat_id)
    ref.set(data)


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
    chat_id = message.chat.id
    name = message.from_user.first_name or "صديقي"

    # قراءة بيانات المستخدم أو إنشاء قالب افتراضي ثم حفظ الاسم
    user = get_user(chat_id)
    user["name"] = name
    save_user(chat_id, user)

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
    name = message.from_user.first_name or ""

    # إعادة تعيين كل الإعدادات للمستخدم في Firebase
    user = default_user(chat_id, name)
    save_user(chat_id, user)

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

    # تصفير الحسابات السابقة ووضع المستخدم في وضع
