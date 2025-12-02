import os
from telegram import Bot
import asyncio

BOT_TOKEN = os.environ.get("BOT_TOKEN",
                           "8458617128:AAFlOljng5_fWkaVHwGL36btoB88QaxgleA")
CHANNEL_1_ID = int(os.environ.get("CHANNEL_1_ID", "-1001720495165"))
CHANNEL_2_ID = int(os.environ.get("CHANNEL_2_ID", "-1003253463119"))


async def check_bot_permissions():
    bot = Bot(BOT_TOKEN)

    print("🔍 التحقق من صلاحيات البوت...")

    try:
        # معلومات البوت
        me = await bot.get_me()
        print(f"🤖 البوت: @{me.username}")

        # التحقق من قناة 1
        try:
            chat_1 = await bot.get_chat(CHANNEL_1_ID)
            member_1 = await bot.get_chat_member(CHANNEL_1_ID, me.id)
            print(f"📊 قناة 1: {chat_1.title}")
            print(f"   - حالة البوت: {member_1.status}")
            print(
                f"   - {'✅ مشرف' if member_1.status in ['administrator', 'creator'] else '❌ ليس مشرف'}"
            )
        except Exception as e:
            print(f"❌ خطأ في قناة 1: {e}")

        # التحقق من قناة 2
        try:
            chat_2 = await bot.get_chat(CHANNEL_2_ID)
            member_2 = await bot.get_chat_member(CHANNEL_2_ID, me.id)
            print(f"📺 قناة 2: {chat_2.title}")
            print(f"   - حالة البوت: {member_2.status}")
            print(
                f"   - {'✅ مشرف' if member_2.status in ['administrator', 'creator'] else '❌ ليس مشرف'}"
            )
        except Exception as e:
            print(f"❌ خطأ في قناة 2: {e}")

    except Exception as e:
        print(f"❌ خطأ عام: {e}")


# تشغيل التحقق
asyncio.run(check_bot_permissions())
