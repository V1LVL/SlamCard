from telegram import Bot
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN",
                           "8458617128:AAFlOljng5_fWkaVHwGL36btoB88QaxgleA")


async def get_channel_info():
    bot = Bot(BOT_TOKEN)

    # جرب الحصول على معلومات القناة
    try:
        chat = await bot.get_chat("@arabic_test_2023")  # ضع يوزر القناة هنا
        print(f"📢 معلومات القناة:")
        print(f"🏷️  العنوان: {chat.title}")
        print(f"🆔 الأيدي: {chat.id}")
        print(f"📝 النوع: {chat.type}")
    except Exception as e:
        print(f"❌ خطأ: {e}")


import asyncio

asyncio.run(get_channel_info())
