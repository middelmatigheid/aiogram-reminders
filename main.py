import os
from dotenv import load_dotenv
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from app.handlers import router
import app.database as db


load_dotenv()

# Connecting to telegram bot
TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()


# Main function to start the bot
async def main():
    await db.delete_tables()
    await db.create_tables()
    dp.include_router(router)
    await dp.start_polling(bot)


# Starting the bot
if __name__ == '__main__':
    asyncio.run(main())
