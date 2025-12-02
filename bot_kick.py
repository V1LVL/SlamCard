from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import logging
import os
from flask import Flask
from threading import Thread

# إعدادات البوت
BOT_TOKEN = os.environ.get("BOT_TOKEN",
                           "8458617128:AAFlOljng5_fWkaVHwGL36btoB88QaxgleA")
CHANNEL_1_ID = int(os.environ.get(
    "CHANNEL_1_ID", "-100123456789"))  # غير هذا بأيدي قناة الاشتراك
ADMIN_ID = int(os.environ.get("ADMIN_ID", "6813062276"))

# إعداد Flask لإبقاء البوت نشطاً
app = Flask('')


@app.route('/')
def home():
    return "🤖 بوت الطرد يعمل!"


def run_flask():
    app.run(host='0.0.0.0', port=5001)


def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


async def show_left_members(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
    """عرض الأعضاء الذين غادروا القناة 2"""
    try:
        # قراءة الأعضاء الذين غادروا من الملف
        if not os.path.exists("left_members.txt"):
            await update.message.reply_text("📭 لا يوجد أعضاء غادروا القناة 2")
            return

        with open("left_members.txt", "r", encoding="utf-8") as f:
            members = f.readlines()

        if not members:
            await update.message.reply_text("📭 لا يوجد أعضاء غادروا القناة 2")
            return

        # عرض قائمة الأعضاء مع أزرار طرد
        keyboard = []
        for member in members[-10:]:  # آخر 10 أعضاء
            user_id, user_name = member.strip().split(",", 1)
            keyboard.append([
                InlineKeyboardButton(f"🚫 طرد {user_name}",
                                     callback_data=f"kick_{user_id}")
            ])

        keyboard.append(
            [InlineKeyboardButton("🔄 تحديث", callback_data="refresh")])
        keyboard.append(
            [InlineKeyboardButton("🗑️ مسح الكل", callback_data="clear_all")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"👥 الأعضاء الذين غادروا القناة 2: ({len(members)} عضو)\n\nاختر العضو الذي تريد طرده من قناة الاشتراك:",
            reply_markup=reply_markup)

    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}")


async def handle_button_click(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):
    """معالجة النقر على الأزرار"""
    query = update.callback_query
    await query.answer()

    if query.data == "refresh":
        await show_left_members(update, context)
        return

    elif query.data == "clear_all":
        # مسح جميع الأعضاء
        if os.path.exists("left_members.txt"):
            os.remove("left_members.txt")
        await query.edit_message_text("✅ تم مسح جميع الأعضاء من القائمة")
        return

    elif query.data.startswith("kick_"):
        user_id = int(query.data.split("_")[1])

        try:
            # طرد العضو من قناة الاشتراك الإجباري
            await context.bot.ban_chat_member(CHANNEL_1_ID, user_id)
            await context.bot.unban_chat_member(CHANNEL_1_ID, user_id
                                                )  # فك الحظر فوراً (طرد فقط)

            # إزالة العضو من القائمة
            if os.path.exists("left_members.txt"):
                with open("left_members.txt", "r", encoding="utf-8") as f:
                    members = f.readlines()

                with open("left_members.txt", "w", encoding="utf-8") as f:
                    for member in members:
                        if not member.startswith(str(user_id)):
                            f.write(member)

            await query.edit_message_text(
                f"✅ تم طرد العضو (ID: {user_id}) من قناة الاشتراك")
            print(f"✅ تم طرد العضو {user_id} من قناة سلمى")

        except Exception as e:
            await query.edit_message_text(f"❌ فشل في طرد العضو: {e}")


async def kick_specific_user(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):
    """طرد عضو محدد باستخدام الأيدي"""
    if not context.args:
        await update.message.reply_text("⚡ الاستخدام: /kick <user_id>")
        return

    try:
        user_id = int(context.args[0])
        await context.bot.ban_chat_member(CHANNEL_1_ID, user_id)
        await context.bot.unban_chat_member(CHANNEL_1_ID, user_id)

        await update.message.reply_text(f"✅ تم طرد العضو {user_id}")

    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 بوت الطرد يعمل!\n\n"
                                    "⚡ الأوامر المتاحة:\n"
                                    "/start - عرض هذه الرسالة\n"
                                    "/left - عرض الأعضاء الذين غادروا\n"
                                    "/kick <user_id> - طرد عضو محدد")


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """للتحقق من أن البوت يعمل"""
    await update.message.reply_text("🏓 بونغ! بوت الطرد يعمل بشكل طبيعي.")


def main():
    # إبقاء البوت نشطاً
    keep_alive()

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("left", show_left_members))
    application.add_handler(CommandHandler("kick", kick_specific_user))
    application.add_handler(CommandHandler("ping", ping_command))
    application.add_handler(CallbackQueryHandler(handle_button_click))

    print("=" * 50)
    print("🚀 بوت الطرد يعمل على Repl.it...")
    print(f"📺 أي دي قناة الاشتراك: {CHANNEL_1_ID}")
    print(f"👤 أي دي المالك: {ADMIN_ID}")
    print("⚡ الأوامر المتاحة: /left, /kick")
    print("=" * 50)

    application.run_polling()


if __name__ == '__main__':
    main()
