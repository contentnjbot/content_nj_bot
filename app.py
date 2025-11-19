# ——————————————————————————————
# 1) أمر /start
# ——————————————————————————————
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "🚀 أهلاً عبدالله!\n\n"
        "أنا كابتن سامي — مساعدك لتجميع ملخصات المحتوى من كل المنصات.\n"
        "ابدأ بالأمر /setup لبدء الإعدادات."
    )

# ——————————————————————————————
# 2) أمر /help
# ——————————————————————————————
@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.reply_to(
        message,
        "📝 قائمة الأوامر المتاحة:\n"
        "/start - بدء البوت\n"
        "/setup - إعداد النظام لأول مرة\n"
        "/platforms - اختيار المنصات\n"
        "/accounts - إضافة الحسابات المراد متابعتها\n"
        "/schedule - اختيار زمن الملخص\n"
        "/summary - استلام ملخص الآن\n"
        "/help - المساعدة"
    )

# ——————————————————————————————
# 3) أمر /setup
# ——————————————————————————————
@bot.message_handler(commands=['setup'])
def setup(message):
    bot.reply_to(
        message,
        "🔧 لنبدأ الإعدادات!\n"
        "1️⃣ أرسل /platforms لاختيار المنصات.\n"
        "2️⃣ ثم /accounts لإضافة الحسابات.\n"
        "3️⃣ وأخيراً /schedule لتحديد وقت الملخص."
    )

# ——————————————————————————————
# 4) أمر /platforms
# ——————————————————————————————
@bot.message_handler(commands=['platforms'])
def platforms(message):
    bot.reply_to(
        message,
        "📱 اختر المنصات التي تريد متابعتها:\n"
        "- Twitter\n"
        "- Instagram\n"
        "- TikTok\n"
        "- Snapchat\n"
        "- YouTube\n"
        "- Facebook\n"
        "- LinkedIn\n\n"
        "🔹 أرسل أسماء المنصات مفصولة بفواصل.\n"
        "مثال:\nTwitter, Instagram, TikTok"
    )

# ——————————————————————————————
# 5) أمر /accounts
# ——————————————————————————————
@bot.message_handler(commands=['accounts'])
def accounts(message):
    bot.reply_to(
        message,
        "👥 الآن أرسل معرفات الحسابات التي تريد متابعتها.\n"
        "🔹 مثال:\n@user1, @user2, https://twitter.com/user"
    )

# ——————————————————————————————
# 6) أمر /schedule
# ——————————————————————————————
@bot.message_handler(commands=['schedule'])
def schedule(message):
    bot.reply_to(
        message,
        "⏱ اختر طريقة استلام الملخص:\n"
        "- now\n"
        "- daily\n"
        "- weekly\n"
        "- monthly\n\n"
        "مثال:\ndaily"
    )

# ——————————————————————————————
# 7) أمر /summary (ملخص تجريبي)
# ——————————————————————————————
@bot.message_handler(commands=['summary'])
def summary(message):
    bot.reply_to(
        message,
        "📊 مثال لملخص يومي:\n\n"
        "Twitter – محمد:\n- نشر تغريدة جديدة.\n\n"
        "Instagram – محمد:\n- نشر صورة جديدة.\n\n"
        "YouTube – محمد:\n- فيديو جديد: 4 دقائق.\n\n"
        "✨ (هذا ملخص تجريبي — سيتم ربط النظام الحقيقي لاحقاً)"
    )
