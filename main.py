import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from loguru import logger
from config import get_settings, Settings
from handlers import router
from database import get_session_maker, create_db


async def main() -> None:
    logger.add("logging.log", format="{time} {level} {message}", level="DEBUG",
               rotation="10 KB", compression="zip")

    logger.info("Startup bot")

    settings: Settings = get_settings()

    bot: Bot = Bot(token=settings.TELEGRAM_TOKEN)
    dp: Dispatcher = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await dp.start_polling(bot, sessionmaker=get_session_maker())


if __name__ == "__main__":
    try:
        create_db()
        asyncio.run(main())
    except Exception as error:
        logger.info("Shutdown bot")
        logger.error(error)
