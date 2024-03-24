from config import get_settings, Settings
from database import get_session_maker, create_db
from handlers import hello_router, profile_router, create_journey, my_journeys, notes, places

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger


async def main() -> None:
    logger.add("logging.log", format="{time} {level} {message}", level="DEBUG",
               rotation="10 MB", compression="zip")

    logger.info("Startup bot")

    settings: Settings = get_settings()

    bot: Bot = Bot(token=settings.TELEGRAM_TOKEN.get_secret_value())
    dp: Dispatcher = Dispatcher(storage=MemoryStorage())

    dp.include_routers(
        hello_router,
        profile_router,
        create_journey,
        my_journeys,
        notes,
        places,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, sessionmaker=get_session_maker())


if __name__ == "__main__":
    try:
        create_db()
        asyncio.run(main())
    except Exception as error:
        logger.info("Shutdown bot")
        logger.error(error)
