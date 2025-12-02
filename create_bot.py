"""Модуль по созданию бота"""

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from decouple import config

# pg_db = DatabaseManager(config("PG_LINK")) # type: ignore
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
admins = [int(config("ADMINS"))]
TOKEN = config("TOKEN")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

bot = Bot(
    token=TOKEN,  # type: ignore
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher(storage=MemoryStorage())
