from telegram.ext import Application, ChatMemberHandler, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import logging
import os
from flask import Flask
from threading import Thread

# إعدادات البوت
BOT_TOKEN = os.environ.get("BOT_TOKEN",
                           "8458617128:AAFlOljng5_fWkaVHwGL36btoB88QaxgleA")
CHANNEL_1_ID = int(os.environ.get("CHANNEL_1_ID",
                                  "-1001720495165"))  # قناة المراقبة
CHANNEL_2_ID = int(os.environ.get("CHANNEL_2_ID",
                                  "-1003253463119"))  # قناة الاشتراك
ADMIN_ID = int(os.environ.get("ADMIN_ID", "6813062276"))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Flask لإبقاء البوت نشطاً
app = Flask(__name__)


@app.route('/')
def home():
    return "🤖 بوت المراقبة يعمل!"


def run_flask():
    app.run(host='0.0.0.0', port=5000)


def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()


async def track_chat_members(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):
    """تتبع الانضمام والمغادرة من قناة 1"""
    try:
        print("🎯 تم استقبال حدث ChatMember!")

        result = update.chat_member
        chat_id = result.chat.id

        print(f"📱 Chat ID: {chat_id}")
        print(f"🎯 Target Channel: {CHANNEL_1_ID}")

        # التأكد من أن الحدث من قناة 1
        if chat_id != CHANNEL_1_ID:
            print(f"⚠️ تجاهل حدث من chat_id: {chat_id}")
            return

        user = result.new_chat_member.user
        old_status = result.old_chat_member.status
        new_status = result.new_chat_member.status

        print(f"👤 User: {user.first_name}")
        print(f"🔄 Status: {old_status} -> {new_status}")

        user_name = f"@{user.username}" if user.username else user.first_name

        # تجاهل البوتات
        if user.is_bot:
            print("🤖 تجاهل بوت")
            return

        # ✅ الانضمام إلى قناة 1
        if old_status == 'left' and new_status in [
                'member', 'administrator', 'creator'
        ]:
            message = f"🟢 **انضم لقناة 1**\n\n👤 الاسم: {user_name}\n🆔 الأيدي: `{user.id}`"
            await context.bot.send_message(chat_id=ADMIN_ID,
                                           text=message,
                                           parse_mode='Markdown')
            print(f"✅ إشعار انضمام: {user_name}")

        # 🔴 المغادرة من قناة 1
        elif old_status in ['member', 'administrator', 'creator'
                            ] and new_status == 'left':
            print(f"🔴 عضو غادر: {user_name}")

            # حفظ بيانات العضو
            with open("left_members.txt", "a", encoding="utf-8") as f:
                f.write(f"{user.id},{user_name}\n")

            # إرسال إشعار مع زر طرد من قناة 2
            keyboard = [[
                InlineKeyboardButton("🚫 طرد من قناة 2",
                                     callback_data=f"kick_{user.id}")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            message = f"🔴 **غادر قناة 1**\n\n👤 الاسم: {user_name}\n🆔 الأيدي: `{user.id}`"
            await context.bot.send_message(chat_id=ADMIN_ID,
                                           text=message,
                                           reply_markup=reply_markup,
                                           parse_mode='Markdown')
            print(f"✅ إشعار مغادرة مع زر طرد: {user_name}")
        else:
            print(f"ℹ️ حالة أخرى: {old_status} -> {new_status}")

    except Exception as e:
        print(f"❌ خطأ في track_chat_members: {e}")


async def handle_kick_button(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):
    """معالجة زر الطرد من قناة 2"""
    try:
        query = update.callback_query
        await query.answer()

        print(f"🎯 نقر على زر: {query.data}")

        if query.data.startswith("kick_"):
            user_id = int(query.data.split("_")[1])

            print(f"🚫 محاولة طرد العضو: {user_id} من قناة 2")

            try:
                # الطرد من قناة 2 (الاشتراك الإجباري)
                await context.bot.ban_chat_member(CHANNEL_2_ID, user_id)
                await context.bot.unban_chat_member(CHANNEL_2_ID,
                                                    user_id)  # طرد فقط

                await query.edit_message_text(
                    f"✅ تم طرد العضو {user_id} من قناة 2")
                print(f"✅ تم طرد العضو {user_id} من قناة 2")

            except Exception as e:
                error_msg = f"❌ فشل في الطرد: {e}"
                await query.edit_message_text(error_msg)
                print(error_msg)

    except Exception as e:
        print(f"❌ خطأ في handle_kick_button: {e}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 بوت مراقبة قناة TGS CRYPTO يعمل!")
    print("✅ تم استقبال /start")


async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لاختبار إرسال رسالة"""
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="🧪 **اختبار البوت**\n\nالبوت يعمل بشكل صحيح!",
            parse_mode='Markdown')
        await update.message.reply_text("✅ تم إرسال رسالة الاختبار")
        print("✅ تم إرسال رسالة اختبار")
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """للتحقق من حالة البوت"""
    try:
        # التحقق من صلاحيات البوت في القنوات
        bot_member_1 = await context.bot.get_chat_member(
            CHANNEL_1_ID, context.bot.id)
        bot_member_2 = await context.bot.get_chat_member(
            CHANNEL_2_ID, context.bot.id)

        status_text = f"""
🤖 **حالة البوت:**

📊 قناة 1 (المراقبة):
- الحالة: {bot_member_1.status}
- {'✅ مشرف' if bot_member_1.status in ['administrator', 'creator'] else '❌ ليس مشرف'}

📺 قناة 2 (الاشتراك):
- الحالة: {bot_member_2.status}
- {'✅ مشرف' if bot_member_2.status in ['administrator', 'creator'] else '❌ ليس مشرف'}
        """
        await update.message.reply_text(status_text, parse_mode='Markdown')
        print("✅ تم إرسال حالة البوت")

    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في التحقق: {e}")
        print(f"❌ خطأ في status_command: {e}")


def main():
    # إبقاء البوت نشطاً
    keep_alive()

    # إنشاء التطبيق
    application = Application.builder().token(BOT_TOKEN).build()

    # إضافة المعالجات
    application.add_handler(
        ChatMemberHandler(track_chat_members, ChatMemberHandler.CHAT_MEMBER))
    application.add_handler(CallbackQueryHandler(handle_kick_button))
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("test", test_command))
    application.add_handler(CommandHandler("status", status_command))

    print("=" * 60)
    print("🚀 بدء بوت مراقبة قناة 1")
    print(f"📊 قناة المراقبة (1): {CHANNEL_1_ID}")
    print(f"📺 قناة الاشتراك (2): {CHANNEL_2_ID}")
    print(f"👤 أي دي المالك: {ADMIN_ID}")
    print("⚡ الأوامر: /start, /test, /status")
    print("=" * 60)

    # تشغيل البوت
    application.run_polling(allowed_updates=Update.ALL_TYPES,
                            drop_pending_updates=True)


if __name__ == '__main__':
    main()
