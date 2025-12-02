from telegram.ext import Application, ChatMemberHandler, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import logging
import os
from flask import Flask
from threading import Thread
import time

# إعدادات البوت
BOT_TOKEN = os.environ.get("BOT_TOKEN",
                           "8458617128:AAFlOljng5_fWkaVHwGL36btoB88QaxgleA")
CHANNEL_1_ID = int(os.environ.get("CHANNEL_1_ID",
                                  "-1001720495165"))  # قناة TGS CRYPTO
CHANNEL_2_ID = int(os.environ.get("CHANNEL_2_ID",
                                  "-1003253463119"))  # قناة سلمى
ADMIN_ID = int(os.environ.get("ADMIN_ID", "6813062276"))

# أسماء القنوات
CHANNEL_1_NAME = "TGS CRYPTO"
CHANNEL_2_NAME = "سلمى"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Flask لإبقاء البوت نشطاً
app = Flask(__name__)


@app.route('/')
def home():
    return f"""
    <html>
        <head>
            <title>🤖 بوت مراقبة القنوات</title>
            <meta http-equiv="refresh" content="60">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .status {{ background: #f0f8ff; padding: 20px; margin: 20px; border-radius: 10px; }}
                .channel {{ background: #e8f5e8; padding: 15px; margin: 10px; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <h1>🤖 بوت مراقبة القنوات</h1>
            <div class="status">
                <h3>🟢 البوت يعمل بشكل طبيعي</h3>
                <p>⏰ آخر تحديث: {time.strftime("%Y-%m-%d %H:%M:%S")}</p>

                <div class="channel">
                    <h4>🔍 قناة المراقبة</h4>
                    <p><strong>{CHANNEL_1_NAME}</strong></p>
                    <p>يرسل إشعارات عند الانضمام والمغادرة</p>
                </div>

                <div class="channel">
                    <h4>🚫 قناة الطرد</h4>
                    <p><strong>{CHANNEL_2_NAME}</strong></p>
                    <p>يتم طرد الأعضاء منها عند المغادرة</p>
                </div>
            </div>
        </body>
    </html>
    """


def run_flask():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()


async def track_chat_members(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):
    """تتبع الانضمام والمغادرة من قناة TGS CRYPTO"""
    try:
        print("🎯 تم استقبال حدث ChatMember!")

        result = update.chat_member
        chat_id = result.chat.id

        # التأكد من أن الحدث من قناة TGS CRYPTO
        if chat_id != CHANNEL_1_ID:
            return

        user = result.new_chat_member.user
        old_status = result.old_chat_member.status
        new_status = result.new_chat_member.status

        user_name = f"@{user.username}" if user.username else user.first_name

        # تجاهل البوتات
        if user.is_bot:
            return

        # ✅ الانضمام إلى قناة TGS CRYPTO
        if old_status == 'left' and new_status in [
                'member', 'administrator', 'creator'
        ]:
            message = f"🟢 **انضم لقناة {CHANNEL_1_NAME}**\n\n👤 الاسم: {user_name}\n🆔 الأيدي: `{user.id}`"
            await context.bot.send_message(chat_id=ADMIN_ID,
                                           text=message,
                                           parse_mode='Markdown')
            print(f"✅ إشعار انضمام: {user_name}")

        # 🔴 المغادرة من قناة TGS CRYPTO
        elif old_status in ['member', 'administrator', 'creator'
                            ] and new_status == 'left':
            print(f"🔴 عضو غادر: {user_name}")

            # إرسال إشعار مع زر طرد من قناة سلمى
            keyboard = [[
                InlineKeyboardButton(f"🚫 طرد من {CHANNEL_2_NAME}",
                                     callback_data=f"kick_{user.id}")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            message = f"🔴 **غادر قناة {CHANNEL_1_NAME}**\n\n👤 الاسم: {user_name}\n🆔 الأيدي: `{user.id}`"
            await context.bot.send_message(chat_id=ADMIN_ID,
                                           text=message,
                                           reply_markup=reply_markup,
                                           parse_mode='Markdown')
            print(f"✅ إشعار مغادرة مع زر طرد: {user_name}")

    except Exception as e:
        print(f"❌ خطأ في track_chat_members: {e}")


async def handle_kick_button(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):
    """معالجة زر الطرد من قناة سلمى"""
    try:
        query = update.callback_query
        await query.answer()

        print(f"🎯 نقر على زر: {query.data}")

        if query.data.startswith("kick_"):
            user_id = int(query.data.split("_")[1])

            print(f"🚫 محاولة طرد العضو: {user_id} من {CHANNEL_2_NAME}")

            try:
                # الطرد من قناة سلمى
                await context.bot.ban_chat_member(CHANNEL_2_ID, user_id)
                await context.bot.unban_chat_member(CHANNEL_2_ID,
                                                    user_id)  # فك الحظر فوراً

                await query.edit_message_text(
                    f"✅ تم طرد العضو {user_id} من {CHANNEL_2_NAME}")
                print(f"✅ تم طرد العضو {user_id} من {CHANNEL_2_NAME}")

            except Exception as e:
                error_msg = f"❌ فشل في الطرد من {CHANNEL_2_NAME}: {e}"
                await query.edit_message_text(error_msg)
                print(error_msg)

                # إذا كان الخطأ لأن البوت ليس عضو
                if "not a member" in str(e):
                    bot_username = (await context.bot.get_me()).username
                    await query.edit_message_text(
                        f"❌ البوت ليس عضو في {CHANNEL_2_NAME}!\n\n"
                        f"📝 الحل:\n"
                        f"1. أضف البوت @{bot_username} لقناة {CHANNEL_2_NAME}\n"
                        f"2. امنحه صلاحية حظر المستخدمين\n"
                        f"3. جرب مرة أخرى")

    except Exception as e:
        print(f"❌ خطأ في handle_kick_button: {e}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_username = (await context.bot.get_me()).username
    await update.message.reply_text(
        f"🤖 **بوت مراقبة القنوات**\n\n"
        f"🔍 **قناة المراقبة:** {CHANNEL_1_NAME}\n"
        f"🚫 **قناة الطرد:** {CHANNEL_2_NAME}\n\n"
        f"📝 سأرسل إشعارات عند:\n"
        f"• انضمام أعضاء جدد لـ {CHANNEL_1_NAME}\n"
        f"• مغادرة أعضاء من {CHANNEL_1_NAME}\n\n"
        f"⚡ عند المغادرة، أرسل زر لطردهم من {CHANNEL_2_NAME}")


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

📊 {CHANNEL_1_NAME}:
- الحالة: {bot_member_1.status}
- {'✅ مشرف' if bot_member_1.status in ['administrator', 'creator'] else '❌ ليس مشرف'}

📺 {CHANNEL_2_NAME}:
- الحالة: {bot_member_2.status}
- {'✅ مشرف' if bot_member_2.status in ['administrator', 'creator'] else '❌ ليس مشرف'}
        """
        await update.message.reply_text(status_text, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في التحقق: {e}")


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
    application.add_handler(CommandHandler("status", status_command))

    print("=" * 60)
    print("🚀 بدء بوت مراقبة القنوات")
    print(f"🔍 قناة المراقبة: {CHANNEL_1_NAME} ({CHANNEL_1_ID})")
    print(f"🚫 قناة الطرد: {CHANNEL_2_NAME} ({CHANNEL_2_ID})")
    print(f"👤 أي دي المالك: {ADMIN_ID}")
    print("⚡ الأوامر: /start, /status")
    print("=" * 60)

    # تشغيل البوت
    application.run_polling()


if __name__ == '__main__':
    main()
